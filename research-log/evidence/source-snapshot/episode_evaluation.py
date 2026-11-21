"""Roll out sampler sessions and aggregate binary rewards by difficulty."""

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Optional

from .environment import Environment, Turn
from .evaluation import EvaluationMetadata, group_metrics
from .scenarios import EpisodeTask

# A factory creates an independent session for each prompt and sample.
Session = Callable[[tuple[Turn, ...]], str]
Sampler = Callable[[str, int, int], Session]


@dataclass(frozen=True)
class EpisodeResult:
    task_id: str
    level: int
    split: str
    sample_id: int
    reward: float
    success: bool
    failure_category: Optional[str]
    tool_calls: int
    trajectory_length: int
    final_answer_correct: Optional[bool]
    trajectory: tuple[Turn, ...]


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def _summarize(rollouts, groups, level):
    count = len(rollouts)
    success = sum(result.success for result in rollouts)
    informative = sum(group["informative"] for group in groups)
    submitted = [r.final_answer_correct for r in rollouts if r.final_answer_correct is not None]
    correct = sum(submitted)
    return {
        "rollout_count": count,
        "task_success_rate": _ratio(success, count),
        "prompt_group_count": len(groups),
        "informative_group_ratio": _ratio(informative, len(groups)),
        "average_tool_calls_per_task": _ratio(sum(r.tool_calls for r in rollouts), count),
        "average_trajectory_length": _ratio(sum(r.trajectory_length for r in rollouts), count),
        "trajectory_length_counts": dict(Counter(str(r.trajectory_length) for r in rollouts)),
        "final_answers_submitted": len(submitted),
        "final_answers_correct": correct,
        "final_answer_correctness": None if level == 1 else _ratio(correct, len(submitted)),
        "failure_category_counts": dict(Counter(r.failure_category for r in rollouts if not r.success)),
        "reward_distribution": {"0": count - success, "1": success},
    }


def evaluate_episodes(tasks: Iterable[EpisodeTask], sampler: Sampler,
                      samples_per_prompt: int, metadata: EvaluationMetadata):
    """Run isolated episodes. The sampler sees prompts and its own history only."""
    if samples_per_prompt < 0:
        raise ValueError("samples_per_prompt must be nonnegative")
    rollouts = []
    groups = {}
    for task in tasks:
        if task.task_id in groups:
            raise ValueError(f"Duplicate task ID: {task.task_id}")
        results = []
        for sample_id in range(1, samples_per_prompt + 1):
            session = sampler(task.prompt, task.level, sample_id)
            environment = Environment(task)
            while not environment.done:
                environment.step(session(environment.trajectory))
            success = environment.status == "success"
            history = environment.trajectory
            results.append(EpisodeResult(
                task.task_id, task.level, task.split, sample_id, float(success), success,
                None if success else environment.status, environment.tool_calls,
                len(history), environment.final_answer_correct, history,
            ))
        groups[task.task_id] = {"level": task.level, "split": task.split,
                                "prompt": task.prompt, **asdict(group_metrics(results))}
        rollouts.extend(results)

    summary = {
        "metadata": asdict(metadata),
        "samples_per_prompt": samples_per_prompt,
        "splits": sorted({group["split"] for group in groups.values()}),
        "by_level": {
            str(level): _summarize(
                [r for r in rollouts if r.level == level],
                [g for g in groups.values() if g["level"] == level], level,
            )
            for level in sorted({group["level"] for group in groups.values()})
        },
        "prompt_groups": groups,
    }
    return rollouts, summary
