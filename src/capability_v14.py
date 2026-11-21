"""Small post-observation diagnostic; no tool planning or new scoring protocol."""
import argparse
import hashlib
import importlib.metadata
import json
import random
from dataclasses import asdict
from datetime import date,timedelta,datetime,timezone
from pathlib import Path
from .capability_v11 import ROOT,DATASET,v1
from .capability_v12 import messages,rollout
from .qwen_agent import QwenAgent,MLXBackend,GenerationParameters
from .report_capability_v11 import parsed

FAMILIES=('integer','float','comparison','native_fields','distractors','sum')
DEMO=(' Unrelated synthetic finalization demonstration. '
      'Tool observation: {"id":1,"result":83,"done":false,"status":null} '
      'Assistant final action: {"final_answer":83}')


def generate():
    rng=random.Random(1414);instances=[]
    for family in FAMILIES:
        for variant in range(2):
            i=len(instances);platforms=list(v1.PLATFORMS);rng.shuffle(platforms)
            start=(date(2026,3,1)+timedelta(days=i*5)).isoformat()
            end=(date.fromisoformat(start)+timedelta(days=2)).isoformat()
            values={p:{m:rng.choice([x for x in range(110,950) if x!=83]) for m in v1.METRICS} for p in platforms}
            target=platforms[0];metric=v1.METRICS[i%3]
            scope=lambda p:{'platform':p,'start_date':start,'end_date':end}
            required=[(metric,scope(target))]
            if family=='float':values[target][metric]=rng.randint(110,900)+.375
            expected=values[target][metric]
            question=f'What was the total {dict(zip(v1.METRICS,("advertising spend in USD","conversions","revenue in USD")))[metric]} for {target} from {start} through {end}?'
            if family=='comparison':
                metric='get_conversions';pair=platforms[:2]
                # Independently varying order/winner; no metric-to-winner rule.
                winner=pair[variant];loser=pair[1-variant]
                values[winner][metric]=values[loser][metric]+rng.randint(1,130)
                required=[(metric,scope(p)) for p in pair];expected=winner
                question=f'Which had more total conversions, {pair[0]} or {pair[1]}, from {start} through {end}?'
            elif family=='sum':
                metric='get_revenue';pair=platforms[:2]
                required=[(metric,scope(p)) for p in pair]
                expected=sum(values[p][metric] for p in pair)
                question=f'What is the combined revenue in USD for {pair[0]} and {pair[1]} from {start} through {end}?'
            elif family=='distractors':
                question+=' Unrelated planning metadata: '+json.dumps({'budget_cap':1701+i,'record_batch':310+i})
            record={'id':f'v14-{family}-{variant}','split':'train' if variant==0 else 'validation',
                'family':family,'category':'multistep','prompt':question,'expected':expected,
                'required':required,'values':values,'start':start,'end':end,
                'expected_output_schema':{'type':'object','required':['final_answer'],'additionalProperties':False,
                    'properties':{'final_answer':{'type':'number' if type(expected) is float else 'integer' if type(expected) is int else 'string'}}},
                'prompt_type_mismatch':family=='float'}
            env=v1.CapabilityEnvironment(record)
            for tool,args in required:env.step(json.dumps({'tool':tool,'arguments':args}))
            assert not env.done
            record['executed_history']=[asdict(t) for t in env.trajectory]
            instances.append(record)
    baseline=json.loads((ROOT/'benchmark-configs/capability-v1.3.json').read_text())
    data={'version':'capability-v1.4-diagnostic','generation_seed':1414,'samples_per_instance':8,
        'seed_base':610000,'guard_samples_per_task':4,'guard_categories':['extraction','comparison','selection'],
        'conditions':{'A':baseline['system_prompt'],'B':baseline['system_prompt']+DEMO},
        'demonstration':DEMO,'decoding':baseline['decoding'],'instances':instances}
    return json.loads(json.dumps(data))


def restore(record):
    env=v1.CapabilityEnvironment(record)
    for turn in record['executed_history']:
        assert env.step(turn['raw_output'])==turn['observation']
    assert not env.done
    return env


def semantic_value(action,expected):
    # Deterministic structural diagnostic, never used as reward or parser repair.
    # Accept only one scalar: raw JSON scalar, exact final wrapper, or native
    # observation-shaped id/result object. No prose/fence removal or nested search.
    value=action
    if isinstance(action,dict):
        if set(action)=={'final_answer'}:value=action['final_answer']
        elif 'result' in action and set(action)<={'id','result','done','status'}:value=action['result']
        else:return False
    if isinstance(expected,str):return isinstance(value,str) and value.strip().lower()==expected
    if type(value) in (int,float):return abs(value-expected)<=max(1e-9,1e-6*abs(expected))
    if isinstance(value,str):
        import re
        if re.fullmatch(r'-?\d+(?:\.\d+)?',value.strip()):
            return abs(float(value)-expected)<=max(1e-9,1e-6*abs(expected))
    return False


def run(output):
    import mlx.core as mx
    data=json.loads((ROOT/'benchmark-configs/capability-v1.4-diagnostic.json').read_text())
    assert data==generate(),'Frozen diagnostic changed'
    base=json.loads((ROOT/'research-log/evidence/capability-v1.3/summary.json').read_text())
    versions={n:importlib.metadata.version(n) for n in base['versions']};assert versions==base['versions']
    parameters=GenerationParameters(**data['decoding'])
    checkpoint=Path.home()/'.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots'/base['checkpoint_revision']
    assert checkpoint.is_dir();output.mkdir(parents=True,exist_ok=False)
    agent=QwenAgent(base['model'],parameters,backend=MLXBackend(str(checkpoint),parameters))
    started=datetime.now(timezone.utc).isoformat()
    with (output/'samples.jsonl').open('w') as stream:
        for condition,system in data['conditions'].items():
            for index,record in enumerate(data['instances']):
                for sample in range(8):
                    seed=610000+index*100+sample;mx.random.seed(seed)
                    env=restore(record);m=messages(system,record,env.trajectory)
                    raw=agent.backend.generate(m,parameters)
                    action=parsed(raw);env.step(raw);assert env.done
                    wrapper=isinstance(action,dict) and set(action)=={'final_answer'}
                    value=action.get('final_answer') if wrapper else None
                    typed=wrapper and (type(value) in (int,float) if type(record['expected']) is float else type(value) is type(record['expected']))
                    result={'condition':condition,'instance_id':record['id'],'family':record['family'],
                        'split':record['split'],'sample_id':sample+1,'seed':seed,'messages':m,
                        'raw_output':raw,'parsed_action':action,'status':env.status,'reward':int(env.status=='success'),
                        'semantic_correct':semantic_value(action,record['expected']),
                        'final_wrapper':wrapper,'correct_value_type':typed,
                        'observation_shaped':isinstance(action,dict) and 'result' in action and set(action)<={'id','result','done','status'},
                        'tool_field':isinstance(action,dict) and 'tool' in action,
                        'scoring_trajectory':[asdict(t) for t in env.trajectory]}
                    stream.write(json.dumps(result)+'\n');stream.flush()
                print(condition,record['id'],'complete',flush=True)
    # Separate small training guard, never pooled with diagnostic outcomes.
    original=json.loads(DATASET.read_text());old={(r['task_id'],r['sample_id'],r['seed']):r for r in
        (json.loads(s) for s in (ROOT/'research-log/evidence/capability-v1.3/samples.jsonl').read_text().splitlines())}
    guard=[]
    for condition,system in data['conditions'].items():
        for cat in data['guard_categories']:
            index,task=next((i,t) for i,t in enumerate(original['tasks']) if t['category']==cat and t['split']=='train')
            for sample in range(4):
                r=rollout(agent,system,task,index,sample)
                if condition=='A':assert r['trajectory']==old[r['task_id'],r['sample_id'],r['seed']]['trajectory']
                guard.append({'condition':condition,**r})
    (output/'guard.json').write_text(json.dumps(guard,indent=2)+'\n')
    (output/'metadata.json').write_text(json.dumps({'configuration':data,'model':agent.model_id,
        'checkpoint_revision':base['checkpoint_revision'],'versions':versions,'started_utc':started,
        'finished_utc':datetime.now(timezone.utc).isoformat(),'new_diagnostic_generations':192,
        'new_guard_rollouts':24,'full_benchmark_run':False},indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output)


if __name__=='__main__':main()
