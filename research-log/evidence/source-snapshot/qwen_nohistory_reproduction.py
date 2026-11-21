"""Reproduce saved campaign no-history messages with old and new seeds."""
import importlib.metadata
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_diagnostic_probe import DiagnosticBackend
from .qwen_finalization_experiment import restore
from .scenarios import build_suite


def main():
    import mlx.core as mx
    root = Path('qwen-nohistory-reproduction')
    root.mkdir(exist_ok=False)
    source = Path('qwen-transition-experiment')
    prior = [json.loads(s) for s in (source/'rollouts.jsonl').read_text().splitlines()]
    prior = [r for r in prior if r['condition']=='B_plain_data' and r['state']=='campaign']
    saved = [json.loads(s) for s in (source/'turn-diagnostics.jsonl').read_text().splitlines()]
    saved = [r for r in saved if r['condition']=='B_plain_data' and r['state']=='campaign']
    assert len(prior)==len(saved)==64
    messages = saved[0]['messages']
    assert all(r['messages']==messages for r in saved)
    history = json.loads((source/'summary.json').read_text())['states']['campaign']
    task = next(t for t in build_suite('train') if t.task_id=='l2-train-campaign')
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    reports = []
    with (root/'turn-diagnostics.jsonl').open('w') as diagnostics, (root/'rollouts.jsonl').open('w') as log:
        backend = DiagnosticBackend(agent.backend, diagnostics)
        for arm, start in [('same_seeds',20000),('new_seeds',30000)]:
            results = []
            for i in range(64):
                seed = start+i
                mx.random.seed(seed)
                env = restore(task,history)
                backend.context = {'arm':arm,'sample':i+1,'seed':seed}
                raw = backend.generate(messages,agent.parameters)
                env.step(raw)
                assert env.done
                record = {'arm':arm,'sample':i+1,'seed':seed,'raw_output':raw,
                    'status':env.status,'reward':float(env.status=='success'),
                    'trajectory':[asdict(t) for t in env.trajectory]}
                if arm=='same_seeds':
                    old = prior[i]
                    assert old['seed']==seed
                    record.update(outcome_matches=env.status==old['status'],
                                  reward_matches=record['reward']==old['reward'],
                                  raw_matches=raw==old['trajectory'][-1]['raw_output'])
                log.write(json.dumps(record)+'\n'); log.flush()
                results.append(record)
            report = {'arm':arm,'seed_range':[start,start+63],'samples':64,
                'successes':sum(r['reward'] for r in results),
                'success_rate':sum(r['reward'] for r in results)/64,
                'outcomes':dict(Counter(r['status'] for r in results))}
            if arm=='same_seeds':
                report.update({key:sum(r[key] for r in results)
                               for key in ('outcome_matches','reward_matches','raw_matches')})
            reports.append(report); print(json.dumps(report),flush=True)
    (root/'summary.json').write_text(json.dumps({'reports':reports,'messages':messages,
        'model':agent.model_id,'parameters':agent.sampling_parameters(),
        'versions':{n:importlib.metadata.version(n) for n in ('mlx','mlx-lm','transformers')}},indent=2)+'\n')


if __name__ == '__main__':
    main()
