"""Paired protocol versus task-outcome diagnostics for the frozen v1.2 run."""
import csv
import json
from collections import Counter
from datetime import date
from .capability_v12 import BASE
from .capability_v11 import ROOT,DATASET,v1
from .report_capability_v11 import diagnostics,parsed
from .verifier import _object,_invalid_constant


def json_valid(raw):
    try:
        json.loads(raw,object_pairs_hook=_object,parse_constant=_invalid_constant)
        return True
    except (ValueError,TypeError):return False


def protocol_valid(raw):
    a=parsed(raw)
    if not isinstance(a,dict):return False
    if set(a)=={'final_answer'}:
        return type(a['final_answer']) is int or (isinstance(a['final_answer'],str) and a['final_answer'] in v1.PLATFORMS)
    if set(a)!={'tool','arguments'} or a['tool'] not in v1.METRICS:return False
    args=a['arguments']
    if not isinstance(args,dict) or set(args)!={'platform','start_date','end_date'}:return False
    if any(type(x) is not str for x in args.values()) or args['platform'] not in v1.PLATFORMS:return False
    try:
        for key in ('start_date','end_date'):
            if date.fromisoformat(args[key]).isoformat()!=args[key]:return False
    except ValueError:return False
    return True


def claims(records,tasks):
    result={}
    for split in ('train','test'):
        for cat in (*v1.CATEGORIES,'overall'):
            rs=[r for r in records if r['split']==split and (cat=='overall' or r['category']==cat)]
            correct=0
            for r in rs:
                t=tasks[r['task_id']];a=parsed(r['trajectory'][0]['raw_output'])
                if t['category']!='selection' and isinstance(a,dict) and 'final_answer' in a:
                    value=a['final_answer']
                    correct+=type(value) is type(t['expected']) and value==t['expected']
            result[split+'/'+cat]={'attempts':len(rs),
                'strict_json_first_outputs':sum(json_valid(r['trajectory'][0]['raw_output']) for r in rs),
                'protocol_valid_first_outputs':sum(protocol_valid(r['trajectory'][0]['raw_output']) for r in rs),
                'correct_typed_final_value_claims_including_invalid_envelopes':correct}
    return result


def main():
    output=ROOT/'capability-runs/v1.2-protocol'
    load=lambda path:[json.loads(s) for s in path.read_text().splitlines()]
    before=load(BASE/'samples.jsonl');after=load(output/'samples.jsonl')
    assert len(before)==len(after)==640
    tasks={t['id']:t for t in json.loads(DATASET.read_text())['tasks']}
    a,b=v1.summarize(before),v1.summarize(after)
    da,db=diagnostics(before,tasks),diagnostics(after,tasks)
    ca,cb=claims(before,tasks),claims(after,tasks)
    old={(r['task_id'],r['sample_id'],r['seed']):r for r in before}
    new={(r['task_id'],r['sample_id'],r['seed']):r for r in after}
    assert old.keys()==new.keys()
    paired=[]
    for key,r in new.items():
        env=v1.CapabilityEnvironment(tasks[r['task_id']])
        for t in r['trajectory']:assert env.step(t['raw_output'])==t['observation']
        assert env.status==r['status'] and int(env.status=='success')==r['reward']
        p=old[key];paired.append({'task_id':key[0],'sample_id':key[1],'seed':key[2],
            'before_reward':p['reward'],'after_reward':r['reward'],'before_status':p['status'],'after_status':r['status']})
    pilot=json.loads((output/'pilot.json').read_text())
    pilot_report={arm:{'outcomes':v1.summarize([r[arm] for r in pilot]),
                       'progression':diagnostics([r[arm] for r in pilot],tasks)} for arm in ('v1.1','v1.2')}
    report={'v1.1':a,'v1.2':b,'progression_v1.1':da,'progression_v1.2':db,
        'compliance_v1.1':ca,'compliance_v1.2':cb,'pilot':pilot_report,
        'fixed':sum(not r['before_reward'] and bool(r['after_reward']) for r in paired),
        'regressed':sum(bool(r['before_reward']) and not r['after_reward'] for r in paired),
        'status_transitions':[{'before':x,'after':y,'count':n} for (x,y),n in Counter((r['before_status'],r['after_status']) for r in paired).most_common()]}
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'paired.json').write_text(json.dumps(paired,indent=2)+'\n')
    with (output/'per-instance.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(['id','split','category','v1.1_successes','v1.2_successes','v1.1_mixed','v1.2_mixed'])
        for task in tasks.values():
            x,y=a['instances'][task['id']],b['instances'][task['id']]
            w.writerow([task['id'],task['split'],task['category'],x['successes'],y['successes'],x['mixed_rewards'],y['mixed_rewards']])
    lines=['# Benchmark v1.2: output-protocol intervention','',
        '| Capability | v1.1 Train | v1.2 Train | v1.1 Test | v1.2 Test | Train change (pp) | Test change (pp) |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for cat in (*v1.CATEGORIES,'overall'):
        tr,te=a['groups']['train/'+cat],a['groups']['test/'+cat];nr,ne=b['groups']['train/'+cat],b['groups']['test/'+cat]
        fmt=lambda x:f"{x['successes']}/{x['attempts']} ({x['success_rate']:.2%})"
        lines.append('| '+' | '.join([cat,fmt(tr),fmt(nr),fmt(te),fmt(ne),f"{100*(nr['success_rate']-tr['success_rate']):+.2f}",f"{100*(ne['success_rate']-te['success_rate']):+.2f}"])+' |')
    lines.extend(['','## Detailed diagnostics','',
        '| Split/category | JSON/schema failures v1.1 → v1.2 | Unknown tools | Invalid arguments | IGF | First correct action | Lookups executed | Later turns |',
        '|---|---:|---:|---:|---:|---:|---:|---:|'])
    for key,x in a['groups'].items():
        y=b['groups'][key];dx,dy=da[key],db[key]
        lines.append('| '+key+' | '+' | '.join([f"{x['format_failures']} → {y['format_failures']}",
            f"{x['failures'].get('unknown_tool',0)} → {y['failures'].get('unknown_tool',0)}",
            f"{x['failures'].get('invalid_arguments',0)} → {y['failures'].get('invalid_arguments',0)}",
            f"{x['mixed_instance_fraction']:.2%} → {y['mixed_instance_fraction']:.2%}",
            f"{x['next_action_correct_rate']:.2%} → {y['next_action_correct_rate']:.2%}",
            f"{dx['successful_lookup_observations']} → {dy['successful_lookup_observations']}",
            f"{dx['later_model_turns']} → {dy['later_model_turns']}"])+' |')
    lines.extend(['',f"Paired fixes: {report['fixed']}; regressions: {report['regressed']}.",
        'The typed-final-value diagnostic counts explicit correct values even in invalid envelopes; it is not a repaired reward or evidence of genuine reasoning. In particular, the metric/winner shortcut remains. Strict JSON, protocol-valid actions, exact task correctness and terminal completion are separate quantities in comparison.json.',
        'No test-set tuning, numerical hints, new examples, weight updates, parser repair or reward changes. The synthetic v1.1 example suffix and tool schemas are byte-identical. Pilot used first training instance/category and first four existing seeds; all 16 live v1.1 controls matched recorded trajectories. Pilot v1.2 trajectories also reproduced exactly when sampled again in the full run. No prompt revisions occurred.',
        'Checkpoint was pinned to the single cache revision recorded by v1.1; package versions were checked before running. Original v1 checkpoint provenance remains historically incomplete.'])
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')
    examples=[]
    for cat in v1.CATEGORIES:
        for success in (True,False):
            r=next((r for r in after if r['category']==cat and bool(r['reward'])==success),None)
            if r:examples.append({'task':tasks[r['task_id']],'v1.1':old[r['task_id'],r['sample_id'],r['seed']],'v1.2':r})
    (output/'representatives.json').write_text(json.dumps(examples,indent=2)+'\n')
    print(json.dumps({'fixed':report['fixed'],'regressed':report['regressed'],'groups':b['groups'],'progression':db,'compliance':cb},indent=2))


if __name__=='__main__':main()
