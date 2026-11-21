"""Sample completions, score them with the benchmark verifier, and log results."""

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

from .benchmark import Task, build_tasks
from .mock_agent import respond
from .verifier import verify


@dataclass(frozen=True)
class RolloutResult:
    task_id: str
    sample_id: int
    raw_output: str
    reward: float
    success: bool
    failure_category: Optional[str]
    verifier_details: dict


@dataclass(frozen=True)
class PromptGroupMetrics:
    sample_count: int
    success_count: int
    success_rate: float
    mean_reward: float
    reward_variance: float
    informative: bool


@dataclass(frozen=True)
class EvaluationMetadata:
    model: str
    sampling_parameters: dict
    dataset_version: str
    verifier_version: str


def group_metrics(rollouts: list[RolloutResult]) -> PromptGroupMetrics:
    count = len(rollouts)
    successes = sum(rollout.success for rollout in rollouts)
    rate = successes / count if count else 0.0
    # For binary rewards the mean is the success rate and variance is p(1-p).
    return PromptGroupMetrics(count, successes, rate, rate, rate * (1 - rate),
                              0 < successes < count)


def evaluate(
    tasks: Iterable[Task],
    sampler: Callable[[str], Iterable[str]],
    metadata: EvaluationMetadata,
) -> tuple[list[RolloutResult], dict]:
    rollouts = []
    groups = {}
    for task_index, task in enumerate(tasks, 1):
        task_id = f"task-{task_index:02}"
        group = []
        for sample_id, output in enumerate(sampler(task.prompt), 1):
            status = verify(output, task)
            success = status == "success"
            group.append(RolloutResult(
                task_id, sample_id, output, float(success), success,
                None if success else status, {"status": status},
            ))
        groups[task_id] = {"prompt": task.prompt, **asdict(group_metrics(group))}
        rollouts.extend(group)

    successes = sum(rollout.success for rollout in rollouts)
    informative = sum(group["informative"] for group in groups.values())
    summary = {
        "metadata": asdict(metadata),
        "rollout_count": len(rollouts),
        "success_count": successes,
        "task_success_rate": successes / len(rollouts) if rollouts else 0.0,
        "prompt_group_count": len(groups),
        "informative_group_count": informative,
        "informative_group_ratio": informative / len(groups) if groups else 0.0,
        "prompt_groups": groups,
        "reward_distribution": {"0": len(rollouts) - successes, "1": successes},
        "failure_category_counts": dict(Counter(
            rollout.failure_category for rollout in rollouts if not rollout.success
        )),
    }
    return rollouts, summary


def write_evaluation(output_dir: Path, rollouts: Iterable[RolloutResult],
                     summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "rollouts.jsonl").open("w", encoding="utf-8") as stream:
        for rollout in rollouts:
            stream.write(json.dumps(asdict(rollout)) + "\n")
    with (output_dir / "summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")


def mock_sample(prompt: str) -> Iterable[str]:
    """Alternate the original mock and its error-free parsing mode."""
    for inject_errors in (True, False, True, False):
        yield respond(prompt, inject_errors=inject_errors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation-output"))
    args = parser.parse_args()
    metadata = EvaluationMetadata(
        model="mock",
        sampling_parameters={"samples_per_prompt": 4, "strategy": "alternate_error_mode"},
        dataset_version="day1-v1",
        verifier_version="day1-v1",
    )
    rollouts, summary = evaluate(build_tasks(), mock_sample, metadata)
    write_evaluation(args.output_dir, rollouts, summary)
    print(f"Task Success Rate: {summary['success_count']}/{len(rollouts)} "
          f"({summary['task_success_rate']:.1%})")
    print(f"Informative Group Ratio: {summary['informative_group_count']}/"
          f"{summary['prompt_group_count']} ({summary['informative_group_ratio']:.1%})")
    print(f"Reward distribution: {summary['reward_distribution']}")
    print(f"Failures: {summary['failure_category_counts']}")
    print(f"Logs: {args.output_dir / 'rollouts.jsonl'}, {args.output_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
