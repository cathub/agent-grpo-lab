"""Read-only paired v1/v1.1 reporting; no inferred or repaired rewards."""
import csv
import json
from collections import Counter
from pathlib import Path
from .capability_v11 import BEFORE, DATASET, ROOT, v1
from .verifier import _object, _invalid_constant


def parsed(raw):
    try:return json.loads(raw,object_pairs_hook=_object,parse_constant=_invalid_constant)
    except (ValueError,TypeError):return None


def diagnostics(records,tasks):
    result={}
    for split in ('train','test'):
        for category in (*v1.CATEGORIES,'overall'):
            rows=[r for r in records if r['split']==split and (category=='overall' or r['category']==category)]
            names=0;lookups=0;first_lookup=0;later=0;context_checks=0
            following_correct=0;following_success=0;following_failures=Counter()
            for r in rows:
                required={name for name,args in tasks[r['task_id']]['required']}
                call=parsed(r['trajectory'][0]['raw_output'])
                if isinstance(call,dict) and call.get('tool') in required:names+=1
                first_lookup+='result' in r['trajectory'][0]['observation']
                lookups+=sum('result' in t['observation'] for t in r['trajectory'])
                later+=max(0,len(r['trajectory'])-1)
                for prior,turn in zip(r['trajectory'],r['trajectory'][1:]):
                    if 'result' in prior['observation']:
                        obs=turn['observation']
                        following_correct+=('result' in obs or obs['status']=='success')
                        following_success+=obs['status']=='success'
                        if obs['done'] and obs['status']!='success':following_failures[obs['status']]+=1
                if 'input_messages_per_turn' in r:
                    for i,messages in enumerate(r['input_messages_per_turn']):
                        for k,turn in enumerate(r['trajectory'][:i]):
                            assert messages[2+2*k]=={'role':'assistant','content':turn['raw_output']}
                            assert messages[3+2*k]=={'role':'user','content':'Tool observation: '+json.dumps(turn['observation'])}
                            context_checks+=1
            result[split+'/'+category]={'first_tool_name_matches_required':names,
                'attempts':len(rows),'first_lookup_executions':first_lookup,
                'successful_lookup_observations':lookups,'later_model_turns':later,
                'prior_history_pairs_verified':context_checks,
                'correct_actions_after_observation':following_correct,
                'terminal_successes_after_observation':following_success,
                'terminal_failures_after_observation':dict(following_failures),
                'first_valid_action_envelopes':sum(isinstance(parsed(r['trajectory'][0]['raw_output']),dict)
                    and (set(parsed(r['trajectory'][0]['raw_output']))=={'final_answer'} or
                         set(parsed(r['trajectory'][0]['raw_output']))=={'tool','arguments'}) for r in rows)}
    return result


def main():
    output=ROOT/'capability-runs/v1.1-contract'
    load=lambda path:[json.loads(s) for s in path.read_text().splitlines()]
    before=load(BEFORE/'samples.jsonl');after=load(output/'samples.jsonl')
    assert len(before)==len(after)==640
    tasks={t['id']:t for t in json.loads(DATASET.read_text())['tasks']}
    old={(r['task_id'],r['sample_id'],r['seed']):r for r in before}
    new={(r['task_id'],r['sample_id'],r['seed']):r for r in after}
    assert old.keys()==new.keys()
    # All observations and binary outcomes must reproduce with unchanged scorer.
    for r in after:
        env=v1.CapabilityEnvironment(tasks[r['task_id']])
        for turn in r['trajectory']:assert env.step(turn['raw_output'])==turn['observation']
        assert env.status==r['status'] and int(env.status=='success')==r['reward']
    a,b=v1.summarize(before),v1.summarize(after)
    da,db=diagnostics(before,tasks),diagnostics(after,tasks)
    transitions=Counter((old[key]['status'],new[key]['status']) for key in old)
    result={'v1':a,'v1.1':b,'diagnostics_v1':da,'diagnostics_v1.1':db,
        'paired_fixes':sum(not old[k]['reward'] and bool(new[k]['reward']) for k in old),
        'paired_regressions':sum(bool(old[k]['reward']) and not new[k]['reward'] for k in old),
        'status_transitions':[{'before':x,'after':y,'count':n} for (x,y),n in transitions.most_common()]}
    (output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'per-instance.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['task_id','split','category','before_successes','after_successes','before_IGF','after_IGF'])
        for task_id,task in tasks.items():
            x,y=a['instances'][task_id],b['instances'][task_id]
            w.writerow([task_id,task['split'],task['category'],x['successes'],y['successes'],x['mixed_rewards'],y['mixed_rewards']])
    lines=['# Benchmark v1 versus v1.1: contract-only prompt intervention','',
        'No training. Same 40 tasks, scorer, seed schedule, model ID, decoding and package versions. Original checkpoint revision was unrecorded; current cached revision and four exact original-prompt model reproduction cases are recorded.','',
        '| Split / capability | v1 successes | v1.1 successes | Change (pp) | IGF v1 → v1.1 | unknown_tool v1 → v1.1 | JSON/format v1 → v1.1 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for key,x in a['groups'].items():
        y=b['groups'][key]
        lines.append(f"| {key} | {x['successes']}/{x['attempts']} ({x['success_rate']:.2%}) | {y['successes']}/{y['attempts']} ({y['success_rate']:.2%}) | {100*(y['success_rate']-x['success_rate']):+.2f} | {x['mixed_instance_fraction']:.2%} → {y['mixed_instance_fraction']:.2%} | {x['failures'].get('unknown_tool',0)} → {y['failures'].get('unknown_tool',0)} | {x['format_failures']} → {y['format_failures']} |")
    lines.extend(['','## Action/progression diagnostics','',
        'Tool-name correctness is diagnostic: a parsed first action names a required tool, independent of arguments. Full next-action correctness and binary success remain unchanged scorer metrics. Selection ends after its correct lookup; multi-step requires three lookups plus final answer.',
        '| Split / capability | First correct tool name v1 → v1.1 | First successful lookup v1 → v1.1 | All successful lookups v1 → v1.1 | Later model turns v1 → v1.1 |',
        '|---|---:|---:|---:|---:|'])
    for key,x in da.items():
        y=db[key];lines.append('| '+key+' | '+' | '.join(f"{x[field]} → {y[field]}" for field in ('first_tool_name_matches_required','first_lookup_executions','successful_lookup_observations','later_model_turns'))+' |')
    lines.extend(['',f"Paired fixes: {result['paired_fixes']}; paired regressions: {result['paired_regressions']}.",
        'All v1.1 histories were replayed with the unchanged scorer. Every prior tool-call/observation pair in every later v1.1 input was checked for exact inclusion. This verifies passing context, not that the model uses it correctly.',
        '', '## Limits on attribution',
        'Only unusable advertised material was removed. This also shortens/reorders the model input token sequence, so changed outputs do not prove each prior failure was caused by a tool mismatch. Correct required-tool names with wrong scopes still fail. Unknown tools can still be hallucinated. No output repair, numeric-output rule, extra demonstration, retry policy, dataset shortcut fix or budget change was introduced.',
        'The v1 metric-to-winner shortcut and unusual 2142/2143 dates remain. Held-out metrics are descriptive, not used for tuning. This is not a v2 benchmark or evidence of trained improvements. Detailed status transitions, all per-seed changes and per-instance IGF are separate JSON/CSV files.'])
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'fixes':result['paired_fixes'],'regressions':result['paired_regressions'],'groups':b['groups'],'progression':db},indent=2))


if __name__=='__main__':main()
