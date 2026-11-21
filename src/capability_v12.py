"""Frozen output-protocol intervention with paired training-only pilot."""
import argparse
import hashlib
import importlib.metadata
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .capability_v11 import ROOT, DATASET, v1, contract_preflight, schemas
from .qwen_agent import GenerationParameters, QwenAgent, MLXBackend

BASE = ROOT/'research-log/evidence/capability-v1.1'
INSTRUCTIONS = (
    'Return one action per response as one valid JSON object. No Markdown fences, '
    'explanatory prose, tags, comments, or text outside the object. '
    'There are exactly two mutually exclusive action forms. '
    'For a tool call, the object must have exactly tool and arguments, both required. '
    'tool is a JSON string naming one available tool. arguments is a JSON object '
    'with exactly platform, start_date, and end_date, all required JSON strings. '
    'platform is a lowercase supported platform name. Dates are YYYY-MM-DD strings '
    'copied from the requested scope. There are no optional fields or campaign arguments. '
    'Use tool, not tool-action or name. Do not add final_answer, result, id, or other '
    'fields to a tool call. Send only one call and wait for the tool observation. '
    'For a final answer, the object must have exactly one required key, final_answer. '
    'Its value is only the requested answer. Amounts and counts must be JSON integers, '
    'without quotation marks, decimal points, units, explanations, lists, or nested objects. '
    'A platform comparison answer must be the lowercase platform-name string. '
    'Never put tool or arguments into a final-answer object. '
    'If the requested data is already supplied in the question, use it. If needed data '
    'is missing, call the matching lookup. When the task explicitly requires lookups, '
    'complete those lookups before submitting the final answer. A request for only the '
    'next tool action should receive a tool call, not a final answer. '
    'After each tool observation, read its result and retain which lookup was completed. '
    'If another required lookup is missing, call that next. If all required information '
    'and lookups are complete, submit final_answer. Do not repeat a completed lookup '
    'or invent a tool result. Tool observations have id and result; these are observation '
    'fields, not fields to copy into an action. Date ranges include both endpoints. '
    'Preserve the requested scope. Perform all checks requested by the task before '
    'submitting the answer. ')


def configuration():
    old=json.loads((ROOT/'benchmark-configs/capability-v1.1.json').read_text())
    tail=old['system_prompt'].split('Available tool schemas: ',1)[1]
    return {**old,'version':'capability-v1.2','system_prompt':INSTRUCTIONS+'Available tool schemas: '+tail,
            'pilot':'first train instance/category, first four frozen seeds each; paired live v1.1/v1.2'}


def messages(system,task,history):
    result=[{'role':'system','content':system},{'role':'user','content':task['prompt']}]
    for turn in history:
        result.extend([{'role':'assistant','content':turn.raw_output},
                       {'role':'user','content':'Tool observation: '+json.dumps(turn.observation)}])
    return result


def rollout(agent,system,task,index,sample):
    import mlx.core as mx
    seed=500000+index*100+sample;mx.random.seed(seed)
    env=v1.CapabilityEnvironment(task);inputs=[]
    while not env.done:
        m=messages(system,task,env.trajectory);inputs.append(m)
        env.step(agent.backend.generate(m,agent.parameters))
    h=env.trajectory;first=h[0].observation
    return {'task_id':task['id'],'category':task['category'],'split':task['split'],
        'sample_id':sample+1,'seed':seed,'reward':int(env.status=='success'),'status':env.status,
        'next_action_correct':first['status']=='success' or ('result' in first and not first['done']),
        'final_answer_correct':env.final_answer_correct,'trajectory':[asdict(t) for t in h],
        'input_messages_per_turn':inputs}


def run(output):
    config=json.loads((ROOT/'benchmark-configs/capability-v1.2.json').read_text())
    assert config==configuration(),'Frozen prompt/configuration changed'
    data=json.loads(DATASET.read_text());baseline=json.loads((BASE/'summary.json').read_text())
    versions={n:importlib.metadata.version(n) for n in baseline['versions']}
    assert versions==baseline['versions']
    assert hashlib.sha256(DATASET.read_bytes()).hexdigest()==config['dataset_sha256']
    assert schemas(config['system_prompt'])==schemas(baseline['configuration']['system_prompt'])
    output.mkdir(parents=True,exist_ok=False)
    contract_preflight()
    revisions=baseline['cached_revisions'];assert len(revisions)==1
    checkpoint=Path.home()/'.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots'/revisions[0]
    assert checkpoint.is_dir()
    parameters=GenerationParameters(**config['decoding'])
    agent=QwenAgent(baseline['model'],parameters,backend=MLXBackend(str(checkpoint),parameters))
    prior={(r['task_id'],r['sample_id']):r for r in
           (json.loads(s) for s in (BASE/'samples.jsonl').read_text().splitlines())}
    pilot=[]
    for category in v1.CATEGORIES:
        index,task=next((i,t) for i,t in enumerate(data['tasks']) if t['category']==category and t['split']=='train')
        for sample in range(4):
            old=rollout(agent,baseline['configuration']['system_prompt'],task,index,sample)
            assert old['trajectory']==prior[task['id'],sample+1]['trajectory'],'v1.1 pilot mismatch; stop'
            new=rollout(agent,config['system_prompt'],task,index,sample)
            pilot.append({'v1.1':old,'v1.2':new})
    (output/'pilot.json').write_text(json.dumps(pilot,indent=2)+'\n')
    print('PAIRED TRAIN PILOT',json.dumps({arm:v1.summarize([r[arm] for r in pilot])['groups'] for arm in ('v1.1','v1.2')}),flush=True)
    # No performance-based revision: only protocol-test failures may block the run.
    results=[];start=datetime.now(timezone.utc).isoformat()
    with (output/'samples.jsonl').open('w') as stream:
        for index,task in enumerate(data['tasks']):
            for sample in range(16):
                r=rollout(agent,config['system_prompt'],task,index,sample)
                for pair in pilot:
                    p=pair['v1.2']
                    if (p['task_id'],p['sample_id'])==(r['task_id'],r['sample_id']):assert p['trajectory']==r['trajectory']
                results.append(r);stream.write(json.dumps(r)+'\n');stream.flush()
            print(task['id'],sum(r['reward'] for r in results if r['task_id']==task['id']),'/16',flush=True)
    summary=v1.summarize(results)
    summary.update(configuration=config,model=agent.model_id,versions=versions,checkpoint_revision=revisions[0],
        started_utc=start,finished_utc=datetime.now(timezone.utc).isoformat(),pilot_revision_count=0,
        note='Pilot frozen before inference. No test-set tuning. No reward/parser changes.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output)


if __name__=='__main__':main()
