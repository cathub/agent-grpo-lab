"""Single inserted decision rule; frozen tasks, parser and rollout machinery."""
import argparse
import hashlib
import importlib.metadata
import json
from datetime import datetime,timezone
from pathlib import Path
from .capability_v11 import ROOT,DATASET,v1,schemas,contract_preflight
from .capability_v12 import rollout
from .qwen_agent import QwenAgent,MLXBackend,GenerationParameters

RULE = ("Before calling a tool, determine whether the information already provided is "
        "sufficient to answer the user's question. If the information is sufficient, "
        "return the final answer directly using the required JSON schema. Otherwise, "
        "call the appropriate available tool to obtain the missing information. "
        "Do not call tools merely because tools are available.")
BASE=ROOT/'research-log/evidence/capability-v1.2'


def configuration():
    old=json.loads((ROOT/'benchmark-configs/capability-v1.2.json').read_text())
    return {**old,'version':'capability-v1.3','system_prompt':RULE+' '+old['system_prompt'],
        'pilot':'first train task/category; first four frozen seeds; exactly 16 new v1.3 samples; saved v1.1/v1.2 controls'}


def run(output):
    config=json.loads((ROOT/'benchmark-configs/capability-v1.3.json').read_text())
    assert config==configuration()
    original=json.loads((ROOT/'benchmark-configs/capability-v1.2.json').read_text())
    assert config['system_prompt']==RULE+' '+original['system_prompt']
    assert schemas(config['system_prompt'])==schemas(original['system_prompt'])
    data=json.loads(DATASET.read_text());base=json.loads((BASE/'summary.json').read_text())
    assert hashlib.sha256(DATASET.read_bytes()).hexdigest()==config['dataset_sha256']
    versions={n:importlib.metadata.version(n) for n in base['versions']};assert versions==base['versions']
    contract_preflight();output.mkdir(parents=True,exist_ok=False)
    checkpoint=Path.home()/'.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots'/base['checkpoint_revision']
    assert checkpoint.is_dir()
    parameters=GenerationParameters(**config['decoding'])
    agent=QwenAgent(base['model'],parameters,backend=MLXBackend(str(checkpoint),parameters))
    previous={}
    for version in ('v1.1','v1.2'):
        previous[version]={(r['task_id'],r['sample_id'],r['seed']):r for r in
            (json.loads(s) for s in (ROOT/f'research-log/evidence/capability-{version}/samples.jsonl').read_text().splitlines())}
    pilot=[]
    for category in v1.CATEGORIES:
        index,task=next((i,t) for i,t in enumerate(data['tasks']) if t['category']==category and t['split']=='train')
        for sample in range(4):
            r=rollout(agent,config['system_prompt'],task,index,sample)
            key=r['task_id'],r['sample_id'],r['seed']
            pilot.append({'v1.1':previous['v1.1'][key],'v1.2':previous['v1.2'][key],'v1.3':r})
    (output/'pilot.json').write_text(json.dumps(pilot,indent=2)+'\n')
    print('TRAIN PILOT',json.dumps({arm:v1.summarize([r[arm] for r in pilot])['groups'] for arm in previous.keys()|{'v1.3'}}),flush=True)
    start=datetime.now(timezone.utc).isoformat();results=[]
    with (output/'samples.jsonl').open('w') as stream:
        for index,task in enumerate(data['tasks']):
            for sample in range(16):
                r=rollout(agent,config['system_prompt'],task,index,sample)
                for pair in pilot:
                    p=pair['v1.3']
                    if (p['task_id'],p['sample_id'])==(r['task_id'],r['sample_id']):assert p['trajectory']==r['trajectory']
                results.append(r);stream.write(json.dumps(r)+'\n');stream.flush()
            print(task['id'],sum(r['reward'] for r in results if r['task_id']==task['id']),'/16',flush=True)
    summary=v1.summarize(results)
    summary.update(configuration=config,model=agent.model_id,versions=versions,
        checkpoint_revision=base['checkpoint_revision'],started_utc=start,
        finished_utc=datetime.now(timezone.utc).isoformat(),pilot_new_samples=16,prompt_revisions=0,
        note='Exact single prepend; no test tuning, repairs, task changes or training.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output)


if __name__=='__main__':main()
