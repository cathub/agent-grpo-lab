"""Matched-seed terminal-reward probe from fully observed fixed states."""
import hashlib
import importlib.metadata
import json
import platform
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .environment import Environment
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_diagnostic_probe import DiagnosticBackend
from .qwen_episodes import QwenEpisodeSampler, episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .qwen_prompt_comparison import SystemPromptBackend
from .scenarios import build_suite

RULE = ("When all information required by the user's question has been retrieved, "
        "submit a final_answer JSON object containing the answer. Do not call another "
        "tool if no additional information is needed. Never repeat an already completed lookup.")


def restore(task, history):
    env = Environment(task)
    for turn in history:
        assert not env.done
        assert env.step(turn['raw_output']) == turn['observation']
    assert not env.done
    return env


def main():
    import mlx.core as mx
    root = Path('qwen-finalization-experiment')
    root.mkdir(exist_ok=False)
    source = Path('qwen-partial-state-probe/branches.jsonl')
    branches = [json.loads(s) for s in source.read_text().splitlines()]
    unique = {json.dumps(r['trajectory'], sort_keys=True): r['trajectory']
              for r in branches if r['task_id'] == 'l2-train-platform'
              and r['next_action_correct']}
    assert len(unique) == 1
    platform_history = next(iter(unique.values()))
    campaign_history = next(r['trajectory'][:1] for r in branches
                            if r['task_id'] == 'l2-train-campaign')
    states = {'platform': platform_history, 'campaign': campaign_history}
    tasks = {t.task_id: t for t in build_suite('train')}
    specifications = [('platform', tasks['l2-train-platform'], 16, 'meta'),
                      ('campaign', tasks['l2-train-campaign'], 64, 129)]
    # Reference validation is outside all model messages.
    for name, task, _, expected in specifications:
        assert task.expected_answer == expected
        check = restore(task, states[name])
        assert check.step(json.dumps({'final_answer': expected}))['status'] == 'success'
    base = episode_instructions() + EXAMPLE
    prompts = {'original': base, 'finalization': base + ' ' + RULE}
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    summaries = []
    with (root / 'turn-diagnostics.jsonl').open('w') as diagnostics, (root / 'rollouts.jsonl').open('w') as log:
        backend = DiagnosticBackend(agent.backend, diagnostics)
        for prompt_name, prompt in prompts.items():
            agent.backend = SystemPromptBackend(backend, prompt)
            for state_name, task, count, _ in specifications:
                outcomes = Counter()
                records = []
                for sample in range(count):
                    seed = (10000 if state_name == 'platform' else 20000) + sample
                    mx.random.seed(seed)
                    env = restore(task, states[state_name])
                    session = QwenEpisodeSampler(agent)(task.prompt, 2, sample + 1)
                    immediate = None
                    while not env.done:
                        backend.context = {'state': state_name, 'prompt': prompt_name,
                                           'sample': sample + 1, 'seed': seed,
                                           'turn': len(env.trajectory) + 1}
                        env.step(session(env.trajectory))
                        if immediate is None:
                            immediate = env.status == 'success'
                    record = {'state': state_name, 'prompt': prompt_name, 'sample': sample + 1,
                        'seed': seed, 'immediate_final_correct': immediate,
                        'reward': float(env.status == 'success'), 'status': env.status,
                        'trajectory': [asdict(t) for t in env.trajectory]}
                    records.append(record)
                    outcomes[env.status] += 1
                    log.write(json.dumps(record) + '\n')
                    log.flush()
                p = sum(r['reward'] for r in records) / count
                variance = p * (1-p)
                summary = {'state': state_name, 'prompt': prompt_name, 'samples': count,
                    'immediate_correct': sum(r['immediate_final_correct'] for r in records),
                    'successes': sum(r['reward'] for r in records), 'success_rate': p,
                    'reward_variance_population': variance, 'mixed_rewards': 0 < p < 1,
                    'outcomes': dict(outcomes),
                    'advantage_convention': '(reward - group_mean) / (population_std + 1e-8)',
                    'advantages': [(r['reward']-p)/(variance**0.5+1e-8) for r in records]}
                summaries.append(summary)
                print(json.dumps(summary), flush=True)
    metadata = {'model': agent.model_id, 'parameters': agent.sampling_parameters(),
        'seed_policy': 'platform 10000..10015; campaign 20000..20063; matched across prompts',
        'platform': platform.platform(), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'versions': {name: importlib.metadata.version(name) for name in ('mlx', 'mlx-lm', 'transformers')},
        'prompts': prompts, 'states': states, 'groups': summaries}
    (root / 'summary.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    main()
