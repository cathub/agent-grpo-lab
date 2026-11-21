"""Paired numeric-output instruction experiment; unchanged binary scoring."""
import json
from collections import Counter
from pathlib import Path
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_diagnostic_probe import DiagnosticBackend
from .qwen_finalization_experiment import restore
from .scenarios import build_suite
from .verifier import _object, _invalid_constant

RULE = ('When the answer is numeric, output it as a JSON number, not a string. '
        'The final_answer must contain only the requested value, without units, '
        'explanations, or nested objects.')


def category(record):
    if record['reward']:
        return 'success'
    try:
        parsed = json.loads(record['raw_output'], object_pairs_hook=_object,
                            parse_constant=_invalid_constant)
    except ValueError:
        return 'invalid_json'
    if not isinstance(parsed, dict) or parsed.keys() != {'final_answer'}:
        return 'other_action'
    value = parsed['final_answer']
    if isinstance(value, str):
        try:
            float(value)
            return 'numeric_string'
        except ValueError:
            return 'other_string'
    if isinstance(value, dict):
        return 'object'
    if type(value) in (int, float):
        return 'numeric_type_mismatch' if value == 129 else 'incorrect_numeric_value'
    return 'other_type'


def main():
    import mlx.core as mx
    root = Path('qwen-numeric-prompt-experiment')
    root.mkdir(exist_ok=False)
    source = Path('qwen-nohistory-reproduction')
    old = [json.loads(s) for s in (source/'rollouts.jsonl').read_text().splitlines()]
    baseline = {r['seed']: r for r in old}
    saved = json.loads((source/'summary.json').read_text())
    messages = [dict(m) for m in saved['messages']]
    messages[0]['content'] += ' ' + RULE
    history = json.loads(Path('qwen-transition-experiment/summary.json').read_text())['states']['campaign']
    task = next(t for t in build_suite('train') if t.task_id=='l2-train-campaign')
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    reports = []
    with (root/'turn-diagnostics.jsonl').open('w') as diagnostics, (root/'rollouts.jsonl').open('w') as log:
        backend = DiagnosticBackend(agent.backend, diagnostics)
        for start in (20000,30000):
            results = []
            for sample in range(64):
                seed = start + sample
                mx.random.seed(seed)
                env = restore(task,history)
                backend.context = {'sample':sample+1,'seed':seed,'seed_set':start}
                raw = backend.generate(messages,agent.parameters)
                env.step(raw)
                assert env.done
                prior = baseline[seed]
                record = {'seed':seed,'sample':sample+1,'raw_output':raw,
                    'status':env.status,'reward':float(env.status=='success'),
                    'baseline_reward':prior['reward'],'baseline_output':prior['raw_output']}
                record['category'] = category(record)
                log.write(json.dumps(record)+'\n'); log.flush()
                results.append(record)
            report = {'seed_range':[start,start+63], 'samples':64,
                'baseline_successes':sum(baseline[start+i]['reward'] for i in range(64)),
                'modified_successes':sum(r['reward'] for r in results),
                'baseline_categories':dict(Counter(category(baseline[start+i]) for i in range(64))),
                'modified_categories':dict(Counter(r['category'] for r in results)),
                'fixed_seeds':[r['seed'] for r in results if r['reward'] and not r['baseline_reward']],
                'regressed_seeds':[r['seed'] for r in results if not r['reward'] and r['baseline_reward']]}
            reports.append(report); print(json.dumps(report),flush=True)
    (root/'summary.json').write_text(json.dumps({'reports':reports,
        'original_messages':saved['messages'],'modified_messages':messages,'added_instruction':RULE,
        'model':agent.model_id,'parameters':agent.sampling_parameters(),'versions':saved['versions']},indent=2)+'\n')


if __name__ == '__main__':
    main()
