"""Three-arm saved-result audit and task-aware paired uncertainty; no inference."""
import csv
import json
import math
from collections import Counter
from .capability_v11 import ROOT,DATASET,v1
from .capability_uncertainty import clopper_pearson,paired_task_bootstrap
from .report_capability_v11 import diagnostics,parsed
from .report_capability_v12 import json_valid,protocol_valid


def load(path):return [json.loads(s) for s in path.read_text().splitlines()]


def group_metrics(rows,tasks):
    ids=sorted({r['task_id'] for r in rows});rates={key:sum(r['reward'] for r in rows if r['task_id']==key)/16 for key in ids}
    n=len(rows);k=sum(r['reward'] for r in rows);required_calls=gratuitous=repeats=names=0
    for r in rows:
        task=tasks[r['task_id']];action=parsed(r['trajectory'][0]['raw_output'])
        if isinstance(action,dict) and action.get('tool') in {x[0] for x in task['required']}:names+=1
        completed=[]
        for turn in r['trajectory']:
            a=parsed(turn['raw_output']);obs=turn['observation']
            if obs['status']=='unnecessary_call':
                if not task['required']:gratuitous+=1
                elif a in completed:repeats+=1
                else:required_calls+=1
            if 'result' in obs:completed.append(a)
    mean=k/n
    return {'attempts':n,'successes':k,'success_rate':mean,'binomial_cp95_nominal':clopper_pearson(k,n),
        'tasks':len(ids),'task_success_rates':rates,'task_rate_min':min(rates.values()),'task_rate_max':max(rates.values()),
        'between_task_sd':math.sqrt(sum((p-mean)**2 for p in rates.values())/(len(ids)-1)) if len(ids)>1 else 0,
        'mixed_tasks':sum(0<p<1 for p in rates.values()),'IGF':sum(0<p<1 for p in rates.values())/len(ids),
        'failures':dict(Counter(r['status'] for r in rows if not r['reward'])),
        'json_schema_failures':sum(r['status'] in ('invalid_json','invalid_format') for r in rows),
        'strict_json_first_outputs':sum(json_valid(r['trajectory'][0]['raw_output']) for r in rows),
        'protocol_valid_first_outputs':sum(protocol_valid(r['trajectory'][0]['raw_output']) for r in rows),
        'parsed_first_tool_fields':sum(isinstance(parsed(r['trajectory'][0]['raw_output']),dict) and 'tool' in parsed(r['trajectory'][0]['raw_output']) for r in rows),
        'correct_first_action_count':sum(r['next_action_correct'] for r in rows),
        'required_tool_name_matches':names,'gratuitous_calls':gratuitous,
        'incorrect_required_calls':required_calls,'repeated_required_calls':repeats,
        'first_lookup_executions':sum('result' in r['trajectory'][0]['observation'] for r in rows),
        'lookup_observations':sum('result' in t['observation'] for r in rows for t in r['trajectory']),
        'later_model_turns':sum(len(r['trajectory'])-1 for r in rows)}


def main():
    output=ROOT/'capability-runs/v1.3-decision'
    tasks={t['id']:t for t in json.loads(DATASET.read_text())['tasks']}
    arms={version:load(ROOT/f'research-log/evidence/capability-{version}/samples.jsonl') for version in ('v1.1','v1.2')}
    arms['v1.3']=load(output/'samples.jsonl')
    for rows in arms.values():
        assert len(rows)==640 and Counter(r['task_id'] for r in rows)=={key:16 for key in tasks}
    for r in arms['v1.3']:
        env=v1.CapabilityEnvironment(tasks[r['task_id']])
        for turn in r['trajectory']:assert env.step(turn['raw_output'])==turn['observation']
        assert env.done and int(env.status=='success')==r['reward'] and env.status==r['status']
    summaries={};uncertainty={};paired=[]
    for version,rows in arms.items():
        summaries[version]={}
        for split in ('all','train','test'):
            for category in (*v1.CATEGORIES,'overall'):
                rs=[r for r in rows if (split=='all' or r['split']==split) and (category=='overall' or r['category']==category)]
                summaries[version][split+'/'+category]=group_metrics(rs,tasks)
    for old_version in ('v1.1','v1.2'):
        old={(r['task_id'],r['sample_id'],r['seed']):r for r in arms[old_version]}
        new={(r['task_id'],r['sample_id'],r['seed']):r for r in arms['v1.3']};assert old.keys()==new.keys()
        pairs=[{'comparison':old_version+'->v1.3','task_id':key[0],'sample_id':key[1],'seed':key[2],
            'before_reward':old[key]['reward'],'after_reward':new[key]['reward'],
            'before_status':old[key]['status'],'after_status':new[key]['status']} for key in old]
        paired+=pairs;groups={}
        for key,b in summaries[old_version].items():
            a=summaries['v1.3'][key];subset={i:tasks[i] for i in b['task_success_rates']}
            boot=paired_task_bootstrap(b['task_success_rates'],a['task_success_rates'],subset)
            selected=[p for p in pairs if p['task_id'] in subset]
            groups[key]={'fixed':sum(not p['before_reward'] and bool(p['after_reward']) for p in selected),
                'regressed':sum(bool(p['before_reward']) and not p['after_reward'] for p in selected),
                'paired_task_bootstrap':boot}
        uncertainty[old_version+'->v1.3']=groups
    progress={version:diagnostics(rows,tasks) for version,rows in arms.items()}
    pilot=json.loads((output/'pilot.json').read_text())
    pilot_metrics={v:{cat:group_metrics([p[v] for p in pilot if p[v]['category']==cat],tasks) for cat in v1.CATEGORIES} for v in arms}
    # Pilot has four, not sixteen samples per task: recompute its small-group rates.
    for version in pilot_metrics:
        for cat,g in pilot_metrics[version].items():
            g['task_success_rates']={k:sum(p[version]['reward'] for p in pilot if p[version]['task_id']==k)/4 for k in g['task_success_rates']}
            g['task_rate_min']=g['task_rate_max']=g['success_rate'];g['between_task_sd']=0
            g['mixed_tasks']=int(0<g['success_rate']<1);g['IGF']=g['mixed_tasks']
    report={'arms':summaries,'paired_uncertainty':uncertainty,'progression':progress,'pilot':pilot_metrics,
        'uncertainty_notes':[
            '95% Clopper-Pearson is exact under IID/common-probability binomial sampling. Pooled heterogeneous-task intervals are nominal descriptive intervals, not task-population generalization claims.',
            'Paired bootstrap resamples whole paired task means within category/split strata, retains all 16 seed outcomes per task, 5000 iterations, statistics seed 20261121.',
            'Small strata (3 held-out tasks/category) make intervals coarse. A degenerate bootstrap interval from all-zero observed tasks does not prove zero uncertainty for unseen tasks.',
            'Per-task 16-trial CP intervals and task-level SD/min/max are reported separately. No treatment of 640 outcomes as 640 independent tasks.']}
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'paired.json').write_text(json.dumps(paired,indent=2)+'\n')
    with (output/'per-instance.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['task_id','split','category','version','successes','attempts','rate','CP95_lower','CP95_upper','mixed'])
        for task_id,t in tasks.items():
            for version,rows in arms.items():
                rs=[r for r in rows if r['task_id']==task_id];k=sum(r['reward'] for r in rs)
                w.writerow([task_id,t['split'],t['category'],version,k,16,k/16,*clopper_pearson(k,16),0<k<16])
    lines=['# Benchmark v1.3: single decision-rule intervention','',
        '| Capability | v1.1 | v1.2 | v1.3 | v1.3 nominal exact binomial 95% CI | Δ vs v1.2 (pp) | Paired task-bootstrap 95% interval (pp) |',
        '|---|---:|---:|---:|---:|---:|---:|']
    fmt=lambda g:f"{g['successes']}/{g['attempts']} ({g['success_rate']:.2%})"
    for cat in (*v1.CATEGORIES,'overall'):
        key='all/'+cat;g=summaries['v1.3'][key];boot=uncertainty['v1.2->v1.3'][key]['paired_task_bootstrap']
        lines.append('| '+cat+' | '+' | '.join(fmt(summaries[v][key]) for v in arms)+f" | [{g['binomial_cp95_nominal'][0]:.2%}, {g['binomial_cp95_nominal'][1]:.2%}] | {100*boot['delta']:+.2f} | [{100*boot['ci95'][0]:+.2f}, {100*boot['ci95'][1]:+.2f}] |")
    for split in ('train','test'):
        lines+=['','## '+split,'','| Capability | v1.1 | v1.2 | v1.3 | IGF v1.3 | Gratuitous / incorrect required / repeated calls v1.3 | JSON/schema failures v1.3 |','|---|---:|---:|---:|---:|---:|---:|']
        for cat in (*v1.CATEGORIES,'overall'):
            key=split+'/'+cat;g=summaries['v1.3'][key]
            lines.append('| '+cat+' | '+' | '.join(fmt(summaries[v][key]) for v in arms)+f" | {g['mixed_tasks']}/{g['tasks']} ({g['IGF']:.2%}) | {g['gratuitous_calls']} / {g['incorrect_required_calls']} / {g['repeated_required_calls']} | {g['json_schema_failures']} |")
    lines+=['','## Uncertainty and inference limits','',*report['uncertainty_notes'],
        '', 'Per-seed fixes/regressions, task-level variability, first-lookup/continuation counts, pilot results and failure categories are in comparison.json. All scores are actual unchanged-verifier outcomes, not semantic oracle estimates. Metric/winner correlation and other v1 task defects remain. No general reasoning improvement can be claimed from comparison labels.',
        'No training, new examples, prompt revision, output repair, task regeneration or test-set tuning. Only the requested rule was prepended, and the remaining v1.2 string is byte-identical.']
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')
    examples=[]
    for cat in v1.CATEGORIES:
        for success in (True,False):
            r=next((r for r in arms['v1.3'] if r['category']==cat and bool(r['reward'])==success),None)
            if r:examples.append({'task':tasks[r['task_id']],'result':r})
    # Also preserve an actual observation continuation when available.
    r=next((r for r in arms['v1.3'] if len(r['trajectory'])>1),None)
    if r:examples.append({'task':tasks[r['task_id']],'result':r})
    (output/'representatives.json').write_text(json.dumps(examples,indent=2)+'\n')
    print(json.dumps({'v1.3':summaries['v1.3'],'paired':uncertainty,'progression':progress['v1.3']},indent=2))


if __name__=='__main__':main()
