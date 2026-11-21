"""Transition demonstration versus plain-text data; unchanged terminal scoring."""
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_diagnostic_probe import DiagnosticBackend
from .qwen_episodes import QwenEpisodeSampler, episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .qwen_finalization_experiment import restore
from .qwen_prompt_comparison import SystemPromptBackend
from .scenarios import build_suite
from .verifier import _object, _invalid_constant

DEMONSTRATION = (
    ' Synthetic example of the action protocol: '
    'User: How much did tiktok brand advertising cost from 2024-06-10 through 2024-06-12? '
    'Assistant tool action: {"tool":"get_ad_spend","arguments":{"platform":"tiktok",'
    '"campaign":"brand","start_date":"2024-06-10","end_date":"2024-06-12"}} '
    'Tool observation: {"id":1,"result":87,"done":false,"status":null} '
    'Assistant final action: {"final_answer":87}')


def final_properties(raw, expected):
    try:
        value = json.loads(raw, object_pairs_hook=_object, parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError):
        return False, False, False
    envelope = isinstance(value, dict) and value.keys() == {'final_answer'}
    typed = envelope and type(value['final_answer']) is type(expected)
    semantic = typed and value['final_answer'] == expected
    return envelope, typed, semantic


def main():
    import mlx.core as mx
    root = Path('qwen-transition-experiment')
    root.mkdir(exist_ok=False)
    previous = json.loads(Path('qwen-finalization-experiment/summary.json').read_text())
    states = previous['states']
    tasks = {t.task_id: t for t in build_suite('train')}
    conditions = {'A_transition_example': episode_instructions() + DEMONSTRATION,
                  'B_plain_data': episode_instructions() + EXAMPLE}
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    groups = []
    with (root / 'turn-diagnostics.jsonl').open('w') as diagnostics, (root / 'rollouts.jsonl').open('w') as log:
        backend = DiagnosticBackend(agent.backend, diagnostics)
        for condition, system in conditions.items():
            agent.backend = SystemPromptBackend(backend, system)
            for state, count in [('platform', 16), ('campaign', 64)]:
                task = tasks['l2-train-platform' if state == 'platform' else 'l2-train-campaign']
                records = []
                for sample in range(count):
                    seed = (10000 if state == 'platform' else 20000) + sample
                    mx.random.seed(seed)
                    env = restore(task, states[state])
                    saved_count = len(env.trajectory)
                    session = QwenEpisodeSampler(agent)(task.prompt, 2, sample + 1)
                    immediate = None
                    while not env.done:
                        backend.context = {'condition': condition, 'state': state,
                                           'sample': sample+1, 'seed': seed,
                                           'turn': len(env.trajectory)+1}
                        if condition == 'A_transition_example':
                            raw = session(env.trajectory)
                        else:
                            # Values and scopes only, not the expected answer.
                            facts = ('Retrieved data for February 1–3, 2025: Google total conversions = 24; '
                                     'Meta total conversions = 35.' if state == 'platform' else
                                     'Retrieved data for February 1–3, 2025: Google brand campaign total '
                                     'advertising spend = 129 USD.')
                            messages = [{'role': 'system', 'content': system},
                                        {'role': 'user', 'content': task.prompt + '\n' + facts}]
                            for turn in env.trajectory[saved_count:]:
                                messages.extend([{'role':'assistant','content':turn.raw_output},
                                    {'role':'user','content':'Tool observation: '+json.dumps(turn.observation)}])
                            raw = agent.backend.generate(messages, agent.parameters)
                        if immediate is None:
                            immediate = final_properties(raw, task.expected_answer)
                        env.step(raw)
                    record = {'condition':condition,'state':state,'sample':sample+1,'seed':seed,
                        'final_envelope':immediate[0], 'typed_final_format':immediate[1],
                        'semantic_correct':immediate[2], 'reward':float(env.status=='success'),
                        'status':env.status,'trajectory':[asdict(t) for t in env.trajectory]}
                    records.append(record)
                    log.write(json.dumps(record)+'\n'); log.flush()
                p = sum(r['reward'] for r in records)/count
                group = {'condition':condition,'state':state,'samples':count,
                    'final_envelope_count':sum(r['final_envelope'] for r in records),
                    'typed_final_format_count':sum(r['typed_final_format'] for r in records),
                    'correct_final_count':sum(r['semantic_correct'] for r in records),
                    'terminal_successes':sum(r['reward'] for r in records),
                    'success_rate':p,'mixed_rewards':0<p<1,'reward_variance':p*(1-p),
                    'outcomes':dict(Counter(r['status'] for r in records))}
                groups.append(group); print(json.dumps(group),flush=True)
    (root/'summary.json').write_text(json.dumps({'groups':groups,'prompts':conditions,
        'model':agent.model_id,'parameters':agent.sampling_parameters(),
        'seed_policy':previous['seed_policy'],'versions':previous['versions'],
        'states':states,'A_design':'Replace single tool-call example with one complete transition example',
        'B_design':'No saved tool history in model input; history replayed only in scoring environment'},indent=2)+'\n')


if __name__ == '__main__':
    main()
