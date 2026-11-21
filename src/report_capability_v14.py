"""Read-only scoring replay and paired reporting for the v1.4 diagnostic."""
import argparse
import json
from collections import Counter
from pathlib import Path
from .capability_v14 import restore,semantic_value
from .capability_v11 import ROOT,DATASET,v1
from .report_capability_v11 import parsed
from .report_capability_v12 import json_valid
from .capability_uncertainty import clopper_pearson,paired_task_bootstrap


def candidate_type(action,expected):
    value=action
    if isinstance(action,dict):
        if set(action)=={'final_answer'}:value=action['final_answer']
        elif 'result' in action and set(action)<={'id','result','done','status'}:value=action['result']
        else:return False
    return type(value) in (int,float) if type(expected) is float else type(value) is type(expected)


def metrics(rows,tasks):
    n=len(rows);strict=sum(r['reward'] for r in rows)
    tool_rows=[r for r in rows if r['tool_field']]
    repeats=sum(any(r['parsed_action']==parsed(t['raw_output']) for t in tasks[r['instance_id']]['executed_history']) for r in tool_rows)
    semantic=sum(r['semantic_correct'] for r in rows)
    return {'n':n,'strict_successes':strict,'strict_rate':strict/n,
        'strict_cp95':clopper_pearson(strict,n),'semantic_correct':semantic,'semantic_rate':semantic/n,
        'semantic_cp95':clopper_pearson(semantic,n),
        'strict_json':sum(json_valid(r['raw_output']) for r in rows),
        'exact_final_wrapper':sum(r['final_wrapper'] for r in rows),
        'correct_type_inside_final_wrapper':sum(r['correct_value_type'] for r in rows),
        'correct_candidate_type_including_observation_echo':sum(candidate_type(r['parsed_action'],tasks[r['instance_id']]['expected']) for r in rows),
        'observation_shaped':sum(r['observation_shaped'] for r in rows),
        'tool_field':len(tool_rows),'exact_completed_call_repeats':repeats,
        'other_tool_field_outputs':len(tool_rows)-repeats,
        'statuses':dict(Counter(r['status'] for r in rows)),
        'semantic_correct_but_strict_failure':sum(r['semantic_correct'] and not r['reward'] for r in rows)}


def report(output):
    metadata=json.loads((output/'metadata.json').read_text());data=metadata['configuration']
    rows=[json.loads(s) for s in (output/'samples.jsonl').read_text().splitlines()]
    tasks={t['id']:t for t in data['instances']};assert len(rows)==192
    for r in rows:
        task=tasks[r['instance_id']];env=restore(task);env.step(r['raw_output'])
        assert env.done and env.status==r['status'] and int(env.status=='success')==r['reward']
        assert [t.observation for t in env.trajectory]==[t['observation'] for t in r['scoring_trajectory']]
        assert semantic_value(parsed(r['raw_output']),task['expected'])==r['semantic_correct']
        assert r['parsed_action']==parsed(r['raw_output'])
        assert r['messages'][0]['content']==data['conditions'][r['condition']]
        assert r['messages'][1]['content']==task['prompt']
    arms={c:{(r['instance_id'],r['sample_id']):r for r in rows if r['condition']==c} for c in ('A','B')}
    assert arms['A'].keys()==arms['B'].keys() and len(arms['A'])==96
    assert set(arms['A'])=={(key,s) for key in tasks for s in range(1,9)}
    paired=[]
    for key,a in arms['A'].items():
        b=arms['B'][key];assert a['seed']==b['seed']==610000+list(tasks).index(key[0])*100+key[1]-1 and a['messages'][1:]==b['messages'][1:]
        assert a['messages'][2:]==[m for t in tasks[key[0]]['executed_history'] for m in
            ({'role':'assistant','content':t['raw_output']},{'role':'user','content':'Tool observation: '+json.dumps(t['observation'])})]
        paired.append({'instance_id':key[0],'sample_id':key[1],'seed':a['seed'],
            'A_reward':a['reward'],'B_reward':b['reward'],'A_semantic':a['semantic_correct'],
            'B_semantic':b['semantic_correct'],'A_status':a['status'],'B_status':b['status']})
    groups={'all':list(tasks),'compatible':[k for k,t in tasks.items() if not t['prompt_type_mismatch']],
        **{f:[k for k,t in tasks.items() if t['family']==f] for f in sorted({t['family'] for t in tasks.values()})}}
    results={}
    for group,ids in groups.items():
        results[group]={c:metrics([r for r in rows if r['condition']==c and r['instance_id'] in ids],tasks) for c in arms}
        stat_tasks={k:{'category':tasks[k]['family'],'split':'development'} for k in ids}
        for field in ('reward','semantic_correct'):
            means={c:{k:sum(r[field] for r in arms[c].values() if r['instance_id']==k)/8 for k in ids} for c in arms}
            results[group][field+'_paired_task_bootstrap']=paired_task_bootstrap(means['A'],means['B'],stat_tasks)
        ps=[p for p in paired if p['instance_id'] in ids]
        results[group]['strict_fixes']=sum(p['A_reward']==0 and p['B_reward']==1 for p in ps)
        results[group]['strict_regressions']=sum(p['A_reward']==1 and p['B_reward']==0 for p in ps)
    per_task={k:{'split':t['split'],'family':t['family'],'expected':t['expected'],
        **{c:metrics([r for r in rows if r['condition']==c and r['instance_id']==k],tasks) for c in arms}}
        for k,t in tasks.items()}
    guard=json.loads((output/'guard.json').read_text());assert len(guard)==24
    originals={t['id']:t for t in json.loads(DATASET.read_text())['tasks']}
    old={(r['task_id'],r['sample_id'],r['seed']):r for r in map(json.loads,(ROOT/'research-log/evidence/capability-v1.3/samples.jsonl').read_text().splitlines())}
    for r in guard:
        env=v1.CapabilityEnvironment(originals[r['task_id']])
        for t in r['trajectory']:assert env.step(t['raw_output'])==t['observation']
        assert env.status==r['status'] and int(env.status=='success')==r['reward']
        if r['condition']=='A':assert r['trajectory']==old[r['task_id'],r['sample_id'],r['seed']]['trajectory']
    guard_summary={c:{cat:{'n':4,'successes':sum(r['reward'] for r in guard if r['condition']==c and r['category']==cat),
        'statuses':dict(Counter(r['status'] for r in guard if r['condition']==c and r['category']==cat))}
        for cat in data['guard_categories']} for c in arms}
    summary={'groups':results,'per_task':per_task,'guard':guard_summary,
        'missing_observations':0,'paired_samples':96,'rescoring_matches':192,
        'by_split':{split:{c:metrics([r for r in rows if r['condition']==c and r['split']==split],tasks) for c in arms} for split in ('train','validation')},
        'mixed_reward_states':{c:[key for key,t in per_task.items() if 0<t[c]['strict_successes']<8] for c in arms},
        'guard_pairs':[{'task_id':a['task_id'],'sample_id':a['sample_id'],'seed':a['seed'],'A_reward':a['reward'],'B_reward':b['reward']} for a,b in zip(guard[:12],guard[12:])],
        'uncertainty_note':'CP intervals are nominal conditional binomial summaries, not unseen-task guarantees. Paired bootstrap resamples the two tasks per family, pooling train/validation as development only; tiny strata give limited uncertainty estimates.',
        'semantic_rule':'Only strict parsed JSON scalar, exact final_answer wrapper, or native observation-shaped result; numeric strings allowed for semantic diagnostic only. No fences/prose stripped, nested searches or scoring repairs.',
        'scope':'12 synthetic train/validation states, one continuation each. Float stratum conflicts with unchanged integer-only instruction. Separate 3-task training guard. No end-to-end planning claims.'}
    (output/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'paired.json').write_text(json.dumps(paired,indent=2)+'\n')
    lines=['# Benchmark v1.4: Observation-to-Final-Answer diagnostic','',
        'VERIFIED: 192 one-action continuations (12 states × 8 paired seeds × 2 prompts); 24 separate training guard rollouts. No training or full benchmark rerun.',
        '',summary['scope'],'',summary['semantic_rule'],'',summary['uncertainty_note'],'']
    for name,g in results.items():
        lines+=['## '+name,'']
        for c in arms:
            m=g[c];lines += [f"- {c}: strict {m['strict_successes']}/{m['n']} ({m['strict_rate']:.2%}); semantic {m['semantic_correct']}/{m['n']} ({m['semantic_rate']:.2%}); JSON {m['strict_json']}; exact wrapper {m['exact_final_wrapper']}; observation echo {m['observation_shaped']}; tool field {m['tool_field']}; statuses {json.dumps(m['statuses'])}."]
        lines+= [f"- Paired strict fixes/regressions: {g['strict_fixes']}/{g['strict_regressions']}; task-bootstrap delta/95% interval {g['reward_paired_task_bootstrap']['delta']:.3f} / {g['reward_paired_task_bootstrap']['ci95']}.",'']
    lines+=['## Per state','']
    for k,t in per_task.items():
        lines += [f"- {k} ({t['split']}): "+'; '.join(f"{c} strict {t[c]['strict_successes']}/8, semantic {t[c]['semantic_correct']}/8" for c in arms)]
    lines+=['','Mixed strict-reward states: '+json.dumps(summary['mixed_reward_states']), '', '## Separate training regression guard','', 'A controls exactly reproduced all 12 corresponding saved v1.3 trajectories. These are not pooled with diagnostic results.','', '```json',json.dumps(guard_summary,indent=2),'```','','## Complete representative inputs, outputs and scoring histories','']
    # Deterministic coverage of both outcomes in each arm/family; no invented history.
    chosen=[]
    for c in arms:
        for family in sorted({t['family'] for t in tasks.values()}):
            rs=[r for r in rows if r['condition']==c and r['family']==family]
            for reward in (1,0):
                r=next((r for r in rs if r['reward']==reward),None)
                if r is not None:chosen.append(r)
    for r in rows:
        if (r['semantic_correct'] and not r['reward']) or (r['condition']=='B' and r['status']=='invalid_json'):
            if r not in chosen:chosen.append(r)
    (output/'representatives.json').write_text(json.dumps(chosen,indent=2)+'\n')
    for r in chosen:
        t=tasks[r['instance_id']]
        lines += [f"### {r['condition']} / {r['instance_id']} / sample {r['sample_id']} / seed {r['seed']}",'',
            'Expected: '+json.dumps(t['expected'])+'; strict status: '+r['status']+'; reward: '+str(r['reward'])+'; semantic diagnostic: '+str(r['semantic_correct']),
            '', '```json',json.dumps({'messages':r['messages'],'raw_output':r['raw_output'],'parsed_action':r['parsed_action'],'scoring_trajectory':r['scoring_trajectory']},indent=2),'```','']
    (output/'report.md').write_text('\n'.join(lines).rstrip()+'\n')
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(report(a.output)['groups']['all'],indent=2))


if __name__=='__main__':main()
