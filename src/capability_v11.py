"""Prompt-only contract correction against the committed v1 evidence snapshot."""
import argparse
import difflib
import hashlib
import importlib.util
import importlib.metadata
import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .qwen_agent import QwenAgent, GenerationParameters

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'research-log/evidence'
SOURCE = EVIDENCE / 'source-snapshot/capability_benchmark.py'
spec = importlib.util.spec_from_file_location('src._frozen_capability_v1', SOURCE)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
DATASET = EVIDENCE / 'benchmarks/capability-v1/dataset.json'
BEFORE = EVIDENCE / 'capability-runs/base-before'


def corrected_prompt(original):
    prefix, tail = original.split('Available tool schemas: ', 1)
    schemas, end = json.JSONDecoder().raw_decode(tail)
    suffix = tail[end:]
    obsolete = ('calculate_roas requires revenue and spend objects with observation_id referencing '
                'earlier get_revenue and get_ad_spend observations for the same scope, not raw numbers. ')
    assert prefix.count(obsolete) == 1
    prefix = prefix.replace(obsolete, '')
    schemas = [s for s in schemas if s['name'] != 'calculate_roas']
    for s in schemas:
        del s['parameters']['properties']['campaign']
    return prefix + 'Available tool schemas: ' + json.dumps(schemas) + suffix


def configuration():
    data = json.loads(DATASET.read_text())
    return {'version': 'capability-v1.1', 'dataset': str(DATASET.relative_to(ROOT)),
        'dataset_sha256': hashlib.sha256(DATASET.read_bytes()).hexdigest(),
        'scorer_snapshot_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'system_prompt': corrected_prompt(data['system_prompt']),
        'decoding': data['decoding'], 'samples_per_instance': data['samples_per_instance'],
        'sampling_seed_base': data['sampling_seed_base']}


def schemas(prompt):
    return json.JSONDecoder().raw_decode(prompt.split('Available tool schemas: ',1)[1])[0]


def contract_preflight():
    data=json.loads(DATASET.read_text());config=configuration()
    advertised=schemas(config['system_prompt'])
    assert {s['name'] for s in advertised}==set(v1.METRICS)
    exercised=[]
    for schema in advertised:
        p=schema['parameters']
        assert set(p['properties'])==set(p['required'])=={'platform','start_date','end_date'}
        assert p['additionalProperties'] is False
        for platform in p['properties']['platform']['enum']:
            task=next(t for t in data['tasks'] if t['category']=='multistep' and t['required'][0][0]==schema['name'])
            args={'platform':platform,'start_date':task['start'],'end_date':task['end']}
            env=v1.CapabilityEnvironment(task)
            obs=env.step(json.dumps({'tool':schema['name'],'arguments':args}))
            assert obs['result']==task['values'][platform][schema['name']] and not obs['done']
            exercised.append((schema['name'],platform))
    # Scripted end-to-end smoke, one task from each category.
    for category in v1.CATEGORIES:
        task=next(t for t in data['tasks'] if t['category']==category)
        env=v1.CapabilityEnvironment(task)
        for tool,args in task['required']:
            env.step(json.dumps({'tool':tool,'arguments':args}))
        if category!='selection':env.step(json.dumps({'final_answer':task['expected']}))
        assert env.status=='success' and env.trajectory[-1].observation['done']
    return {'contract_cases':len(exercised),'scripted_category_smokes':4,'status':'passed'}


def run(output):
    import mlx.core as mx
    config=configuration();data=json.loads(DATASET.read_text());before=json.loads((BEFORE/'summary.json').read_text())
    versions={n:importlib.metadata.version(n) for n in before['versions']}
    assert versions==before['versions'], 'Runtime versions differ from v1; stop'
    assert config['dataset_sha256']==before['dataset_sha256']
    output.mkdir(parents=True,exist_ok=False)
    preflight=contract_preflight()
    agent=QwenAgent(before['model'],GenerationParameters(**data['decoding']))
    old={(r['task_id'],r['sample_id']):r for r in
         (json.loads(s) for s in (BEFORE/'samples.jsonl').read_text().splitlines())}
    # Actual model smoke: verify original raw outputs before the full arm.
    smoke=[]
    for category in v1.CATEGORIES:
        index,task=next((i,t) for i,t in enumerate(data['tasks']) if t['category']==category)
        mx.random.seed(data['sampling_seed_base']+index*100)
        messages=[{'role':'system','content':data['system_prompt']},{'role':'user','content':task['prompt']}]
        raw=agent.backend.generate(messages,agent.parameters)
        assert raw==old[task['id'],1]['trajectory'][0]['raw_output'], 'Original raw smoke mismatch; stop'
        smoke.append({'category':category,'seed':data['sampling_seed_base']+index*100,'raw_output':raw,'exact_match':True})
    preflight['original_model_reproduction']=smoke
    (output/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    print('PREFLIGHT PASSED: contract, scripted loop, four original raw outputs',flush=True)
    results=[];started=datetime.now(timezone.utc).isoformat()
    with (output/'samples.jsonl').open('w') as stream:
        for index,task in enumerate(data['tasks']):
            for sample in range(16):
                seed=data['sampling_seed_base']+index*100+sample;mx.random.seed(seed)
                env=v1.CapabilityEnvironment(task);inputs=[]
                while not env.done:
                    messages=[{'role':'system','content':config['system_prompt']},{'role':'user','content':task['prompt']}]
                    for turn in env.trajectory:
                        messages.extend([{'role':'assistant','content':turn.raw_output},
                            {'role':'user','content':'Tool observation: '+json.dumps(turn.observation)}])
                    inputs.append(messages)
                    env.step(agent.backend.generate(messages,agent.parameters))
                history=env.trajectory;first=history[0].observation
                r={'task_id':task['id'],'category':task['category'],'split':task['split'],
                    'sample_id':sample+1,'seed':seed,'reward':int(env.status=='success'),'status':env.status,
                    'next_action_correct':first['status']=='success' or ('result' in first and not first['done']),
                    'final_answer_correct':env.final_answer_correct,'trajectory':[asdict(t) for t in history],
                    'input_messages_per_turn':inputs}
                results.append(r);stream.write(json.dumps(r)+'\n');stream.flush()
            print(task['id'],sum(r['reward'] for r in results if r['task_id']==task['id']),'/16',flush=True)
    summary=v1.summarize(results)
    snapshots=list((Path.home()/'.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots').glob('*'))
    summary.update(configuration=config,model=agent.model_id,versions=versions,started_utc=started,
        finished_utc=datetime.now(timezone.utc).isoformat(),cached_revisions=[p.name for p in snapshots],
        original_checkpoint_revision='UNVERIFIED: v1 did not record a resolved revision')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    paired=[]
    for r in results:
        b=old[r['task_id'],r['sample_id']];assert r['seed']==b['seed']
        paired.append({'task_id':r['task_id'],'sample_id':r['sample_id'],'seed':r['seed'],
            'before_reward':b['reward'],'after_reward':r['reward'],'before_status':b['status'],'after_status':r['status']})
    (output/'paired.json').write_text(json.dumps(paired,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    run(args.output)


if __name__=='__main__':main()
