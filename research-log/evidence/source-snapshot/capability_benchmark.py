"""Frozen, stratified in-distribution capability benchmark (no training)."""
import argparse
import hashlib
import json
import random
from collections import Counter
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from .environment import Environment
from .qwen_agent import DEFAULT_MODEL, GenerationParameters, QwenAgent
from .qwen_episodes import episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .scenarios import Scope
from .verifier import _object, _invalid_constant

VERSION = 'capability-v1'
CATEGORIES = ('extraction', 'comparison', 'selection', 'multistep')
METRICS = ('get_ad_spend', 'get_conversions', 'get_revenue')
LABELS = ('advertising spend in USD', 'conversions', 'revenue in USD')
PLATFORMS = ('google', 'meta', 'tiktok')


def generate(seed=42, instances=10, test_only=False):
    if not 0 <= seed <= 2000:
        raise ValueError('Choose a generation seed between 0 and 2000 for valid fixture dates')
    if instances < 10 or instances % 10:
        raise ValueError('instances per category must be a positive multiple of 10')
    rng = random.Random(seed)
    tasks = []
    for category_index, category in enumerate(CATEGORIES):
        for i in range(instances):
            # Each ten-instance block has 7/3 strata with all three conditions.
            split = 'test' if test_only or i % 10 in (1, 5, 9) else 'train'
            condition = i % 3
            start = (date(2028, 1, 1) + timedelta(days=seed*1000 + (category_index*instances+i)*4)).isoformat()
            end = (date.fromisoformat(start)+timedelta(days=2)).isoformat()
            order = list(PLATFORMS); rng.shuffle(order)
            values = {p: {m: rng.randint(10, 900) for m in METRICS} for p in PLATFORMS}
            metric = METRICS[condition]
            winner = PLATFORMS[condition]
            # Condition determines the winner, not a fixed numeric answer.
            values[winner][metric] = max(v[metric] for v in values.values()) + rng.randint(1, 50)
            target = order[0]
            scope = {'platform': target, 'start_date': start, 'end_date': end}
            required = []
            if category == 'extraction':
                observation = {'id': 1, 'result': values[target][metric]}
                wording = ('Extract the {label} for {target}.', 'What is the observed {label} for {target}?')[i%2]
                prompt = wording.format(label=LABELS[condition], target=target)
                prompt += f' Date range: {start} through {end}. Observation: '+json.dumps(observation)
                expected = values[target][metric]
            elif category == 'comparison':
                prompt = f'Which platform has the highest {LABELS[condition]} from {start} through {end}? '
                prompt += 'Retrieved totals: '+ '; '.join(f'{p}={values[p][metric]}' for p in order)+'.'
                expected = winner
            elif category == 'selection':
                prompt = f'Retrieve {LABELS[condition]} for {target} from {start} through {end}. '
                prompt += 'No value for this metric has been retrieved. Return only the next tool action.'
                prompt += ' Available unrelated information: '+json.dumps({'platform':target,'metric':METRICS[(condition+1)%3],
                    'result':values[target][METRICS[(condition+1)%3]]})
                required = [(metric, scope)]
                expected = None
            else:
                prompt = f'Use the tools to compare {LABELS[condition]} for '+', '.join(order)
                prompt += f' from {start} through {end}. Retrieve all three totals and return the highest platform name.'
                required = [(metric, {'platform':p,'start_date':start,'end_date':end}) for p in order]
                expected = winner
            tasks.append({'id':f'{VERSION}-{seed}-{category}-{i:04}', 'scenario_id':f'{seed}-{category_index}-{i}',
                'category':category,'condition':condition,'split':split,'prompt':prompt,
                'expected':expected,'required':required,'values':values,'start':start,'end':end})
    system = episode_instructions()+EXAMPLE
    return {'version':VERSION,'generation_seed':seed,'instances_per_category':instances,
        'system_prompt':system,'decoding':asdict(GenerationParameters(temperature=0.7)),
        'samples_per_instance':16,'sampling_seed_base':500000,
        'tasks':tasks}


class CapabilityEnvironment(Environment):
    """Reuse strict action parsing, history, termination and final-answer checks.

    Only fixture dispatch and the explicit next-action task success rule are new.
    """
    def __init__(self, record):
        self.record = record
        requirements = frozenset((tool, Scope(**scope)) for tool,scope in record['required'])
        task = SimpleNamespace(legacy=None, expected_answer=record['expected'],
            required_lookups=requirements,required_roas=frozenset(),
            max_steps=1 if record['category']!='multistep' else 4)
        super().__init__(task)

    def _call(self, tool, args):
        if tool not in METRICS:
            return 'unknown_tool', None
        if args.keys() != {'platform','start_date','end_date'} or any(type(v) is not str for v in args.values()):
            return 'invalid_arguments', None
        key = tool, Scope(**args)
        if key not in self.task.required_lookups or key in self._lookups:
            return 'unnecessary_call', None
        self._lookups[key] = len(self._history)+1
        return None, self.record['values'][args['platform']][tool]

    def _record(self, raw_output, observation, status=None):
        if self.record['category']=='selection' and status is None and 'result' in observation:
            status = 'success'
        return super()._record(raw_output, observation, status)


def freeze(path, seed, instances, test_only):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(generate(seed,instances,test_only),stream,indent=2); stream.write('\n')


def evaluate(dataset, output, model, adapter=None):
    import mlx.core as mx
    from mlx_lm import load
    output.mkdir(parents=True,exist_ok=False)
    blob = dataset.read_bytes(); data=json.loads(blob)
    if data['version']!=VERSION:
        raise ValueError('Unsupported frozen scoring version')
    agent=QwenAgent(model,GenerationParameters(**data['decoding']))
    if adapter:
        agent.backend.model,agent.backend.tokenizer=load(model,adapter_path=adapter)
    results=[]
    with (output/'samples.jsonl').open('w') as stream:
        for index,task in enumerate(data['tasks']):
            for sample in range(data['samples_per_instance']):
                seed=data['sampling_seed_base']+index*100+sample
                mx.random.seed(seed)
                env=CapabilityEnvironment(task)
                first_correct=False
                while not env.done:
                    messages=[{'role':'system','content':data['system_prompt']},
                              {'role':'user','content':task['prompt']}]
                    for turn in env.trajectory:
                        messages.extend([{'role':'assistant','content':turn.raw_output},
                            {'role':'user','content':'Tool observation: '+json.dumps(turn.observation)}])
                    observation=env.step(agent.backend.generate(messages,agent.parameters))
                    if len(env.trajectory)==1:
                        first_correct=env.status=='success' or ('result' in observation and not env.done)
                record={'task_id':task['id'],'category':task['category'],'split':task['split'],
                    'sample_id':sample+1,'seed':seed,'reward':int(env.status=='success'),
                    'status':env.status,'next_action_correct':first_correct,
                    'final_answer_correct':env.final_answer_correct,
                    'trajectory':[asdict(t) for t in env.trajectory]}
                results.append(record);stream.write(json.dumps(record)+'\n');stream.flush()
            print(task['id'],sum(r['reward'] for r in results if r['task_id']==task['id']),'/16',flush=True)
    report=summarize(results)
    import importlib.metadata
    report.update(dataset_sha256=hashlib.sha256(blob).hexdigest(),version=VERSION,
        model=model,adapter=adapter,decoding=data['decoding'],samples_per_instance=data['samples_per_instance'],
        system_prompt=data['system_prompt'],versions={n:importlib.metadata.version(n) for n in ('mlx','mlx-lm','transformers')})
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


def summarize(results):
    instances={}
    for r in results:instances.setdefault(r['task_id'],[]).append(r)
    per_instance={key:{'successes':sum(x['reward'] for x in group),'attempts':len(group),
        'success_rate':sum(x['reward'] for x in group)/len(group),
        'mixed_rewards':0<sum(x['reward'] for x in group)<len(group)} for key,group in instances.items()}
    groups={}
    for split in ('train','test'):
        for category in (*CATEGORIES,'overall'):
            rs=[r for r in results if r['split']==split and (category=='overall' or r['category']==category)]
            if not rs:continue
            ids={r['task_id'] for r in rs}
            groups[f'{split}/{category}']={'successes':sum(r['reward'] for r in rs),'attempts':len(rs),
                'success_rate':sum(r['reward'] for r in rs)/len(rs),
                'mixed_instance_fraction':sum(per_instance[i]['mixed_rewards'] for i in ids)/len(ids),
                'next_action_correct_rate':sum(r['next_action_correct'] for r in rs)/len(rs),
                'failures':dict(Counter(r['status'] for r in rs if not r['reward'])),
                'format_failures':sum(r['status'] in ('invalid_json','invalid_format') for r in rs)}
    return {'groups':groups,'instances':per_instance}


def compare(before,after,output):
    a=json.loads(before.read_text()); b=json.loads(after.read_text()) if after else None
    if b:
        for key in ('dataset_sha256','version','decoding','samples_per_instance','system_prompt'):
            if a[key]!=b[key]:raise ValueError('Incompatible evaluations: '+key)
    lines=['| Capability | Train Before | Train After | Test Before | Test After | Train change (pp) | Test change (pp) |',
           '|---|---:|---:|---:|---:|---:|---:|']
    notes=[]
    for cat in (*CATEGORIES,'overall'):
        tr=a['groups'].get('train/'+cat);te=a['groups'].get('test/'+cat)
        br=b['groups'].get('train/'+cat) if b else None;be=b['groups'].get('test/'+cat) if b else None
        fmt=lambda x:f"{x['success_rate']:.2%} ({x['successes']}/{x['attempts']})" if x else 'Not run'
        change=lambda x,y:f"{100*(y['success_rate']-x['success_rate']):+.2f}" if x and y else '—'
        lines.append('| '+' | '.join([cat,fmt(tr),fmt(br),fmt(te),fmt(be),change(tr,br),change(te,be)])+' |')
        if tr and te:notes.append(f"{cat}: before train−test gap {100*(tr['success_rate']-te['success_rate']):+.2f} pp.")
        if br and be:notes.append(f"{cat}: after train−test gap {100*(br['success_rate']-be['success_rate']):+.2f} pp.")
    if after:
        load=lambda path:{(r['task_id'],r['sample_id'],r['seed']):r for r in
            (json.loads(s) for s in (path.parent/'samples.jsonl').read_text().splitlines())}
        old,new=load(before),load(after)
        if old.keys()!=new.keys():raise ValueError('Per-instance sampling seeds differ')
        paired={'fixed':[],'regressed':[]}
        for key,r in old.items():
            if r['reward']!=new[key]['reward']:
                paired['fixed' if new[key]['reward'] else 'regressed'].append(list(key))
        output.with_suffix('.paired.json').write_text(json.dumps(paired,indent=2)+'\n')
        notes.append(f"Paired samples: {len(paired['fixed'])} fixed, {len(paired['regressed'])} regressed.")
    output.write_text('\n'.join(lines)+ '\n\n'+'\n\n'.join(notes)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    g=sub.add_parser('generate');g.add_argument('--dataset',type=Path,required=True);g.add_argument('--seed',type=int,default=42)
    g.add_argument('--instances',type=int,default=10);g.add_argument('--test-only',action='store_true')
    e=sub.add_parser('evaluate');e.add_argument('--dataset',type=Path,required=True);e.add_argument('--output',type=Path,required=True)
    e.add_argument('--model',default=DEFAULT_MODEL);e.add_argument('--adapter')
    c=sub.add_parser('compare');c.add_argument('--before',type=Path,required=True);c.add_argument('--after',type=Path);c.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='generate':freeze(a.dataset,a.seed,a.instances,a.test_only)
    elif a.command=='evaluate':evaluate(a.dataset,a.output,a.model,a.adapter)
    else:compare(a.before,a.after,a.output)


if __name__=='__main__':main()
