"""Independent one-action branches from verified saved partial histories."""
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .environment import Environment
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_episodes import QwenEpisodeSampler, episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .qwen_prompt_comparison import SystemPromptBackend
from .scenarios import Scope, build_suite


def main():
    output = Path('qwen-partial-state-probe')
    output.mkdir(exist_ok=False)
    source = Path('qwen-level2-group16-diagnostics/rollouts.jsonl')
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    states = [r for r in rows if 'result' in r['trajectory'][0]['observation']]
    assert len(states) == 5
    tasks = {t.task_id: t for t in build_suite('train') if t.level == 2}
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    prompt = episode_instructions() + EXAMPLE
    agent.backend = SystemPromptBackend(agent.backend, prompt)
    factory = QwenEpisodeSampler(agent)
    summaries = []
    with (output / 'branches.jsonl').open('w') as stream:
        for state in states:
            task = tasks[state['task_id']]
            first = state['trajectory'][0]
            action = json.loads(first['raw_output'])
            assert (action['tool'], Scope(**action['arguments'])) in task.required_lookups
            counts = Counter()
            correct = successes = 0
            for sample in range(1, 17):
                env = Environment(task)
                assert env.step(first['raw_output']) == first['observation']
                assert not env.done
                session = factory(task.prompt, 2, sample)
                raw = session(env.trajectory)
                observation = env.step(raw)
                # Correct next action either completes successfully or executes
                # another required tool successfully. No reward changes.
                next_correct = env.status == 'success' or ('result' in observation and not env.done)
                success = env.status == 'success'
                correct += next_correct
                successes += success
                counts[env.status or 'valid_nonterminal'] += 1
                stream.write(json.dumps({
                    'task_id': task.task_id, 'source_sample_id': state['sample_id'],
                    'branch_sample_id': sample, 'next_action_correct': next_correct,
                    'terminal_success': success, 'terminal': env.done,
                    'trajectory': [asdict(turn) for turn in env.trajectory],
                }) + '\n')
                stream.flush()
            summaries.append({'task_id': task.task_id, 'source_sample_id': state['sample_id'],
                'samples': 16, 'next_action_correct_count': correct,
                'next_action_correct_rate': correct / 16,
                'terminal_success_count': successes, 'terminal_success_rate': successes / 16,
                'mixed_terminal_success_failure': 0 < successes < 16,
                'outcomes': dict(counts)})
    (output / 'states.json').write_text(json.dumps(states, indent=2) + '\n')
    (output / 'summary.json').write_text(json.dumps({
        'model': agent.model_id, 'parameters': agent.sampling_parameters(),
        'samples_per_state': 16, 'seed_policy': 'seed 0 once; advancing RNG across branches',
        'system_prompt': prompt, 'states': summaries,
    }, indent=2) + '\n')
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
