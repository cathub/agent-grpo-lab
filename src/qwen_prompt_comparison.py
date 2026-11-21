"""Controlled system-prompt-only comparison; original baselines are untouched."""
import json
from pathlib import Path

from .qwen_agent import QwenAgent
from .qwen_episodes import episode_instructions, run

RULE = ("If you don't have the required data, you must call the appropriate tool before "
        "giving final_answer. Do not fabricate numbers, observation IDs, or claims. "
        "If you already have sufficient data, you may give final_answer without an "
        "additional tool call, subject to the task's explicit tool requirements.")


class SystemPromptBackend:
    def __init__(self, backend, system_prompt):
        self.backend = backend
        self.system_prompt = system_prompt

    def generate(self, messages, parameters):
        messages = [dict(message) for message in messages]
        messages[0]['content'] = self.system_prompt
        return self.backend.generate(messages, parameters)


def first_tool_executed(result):
    """Count successful execution of the first action, not merely an attempted call."""
    return bool(result.trajectory and 'result' in result.trajectory[0].observation)


def main():
    root = Path('qwen-prompt-comparison')
    if root.exists():
        raise FileExistsError('Preserve existing comparisons; choose a new directory in code')
    root.mkdir()
    prompts = {'original': episode_instructions(),
               'conditional_tool': RULE + ' ' + episode_instructions()}
    report = {}
    for name, prompt in prompts.items():
        # Fresh model initialization resets the same seed for each arm.
        agent = QwenAgent()
        backend = agent.backend
        agent.backend = SystemPromptBackend(backend, prompt)
        report[name] = {}
        for level in (2, 3):
            results, summary = run(agent, level, root / name / f'level{level}')
            metrics = summary['by_level'][str(level)]
            report[name][str(level)] = {
                'task_count': len(results),
                'first_tool_execution_count': sum(first_tool_executed(r) for r in results),
                'first_tool_execution_rate': sum(first_tool_executed(r) for r in results) / len(results),
                'success_rate': metrics['task_success_rate'],
                'failure_categories': metrics['failure_category_counts'],
            }
        del agent, backend
    (root / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'system-prompts.json').write_text(json.dumps(prompts, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
