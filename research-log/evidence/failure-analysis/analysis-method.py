import sys,json,re,hashlib,collections,html,csv
from pathlib import Path
from decimal import Decimal,InvalidOperation
repo=Path('/Users/boli/development/agent-grpo-lab');sys.path.insert(0,str(repo))
from src.capability_benchmark import CapabilityEnvironment
from src.verifier import _object,_invalid_constant
out=Path('outputs/capability-failure-analysis');out.mkdir(parents=True,exist_ok=True)
paths=[repo/'benchmarks/capability-v1/dataset.json',repo/'capability-runs/base-before/samples.jsonl',repo/'capability-runs/base-before/summary.json']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
data=json.loads(paths[0].read_text());rows=[json.loads(s) for s in paths[1].read_text().splitlines()];tasks={t['id']:t for t in data['tasks']}

def strict(s):
 try:return json.loads(s,object_pairs_hook=_object,parse_constant=_invalid_constant)
 except (ValueError,TypeError,RecursionError):return None

def check_scalar(v,t):
 e=t['expected']
 if type(e) is int:
  if type(v) in (int,float):return v==e
  if isinstance(v,str) and re.fullmatch(r'\s*\$?\d+(?:\.\d+)?(?:\s*USD)?\s*',v):
   return Decimal(re.sub(r'[^0-9.]','',v))==e
 else:
  return isinstance(v,str) and v.strip().lower()==e
 return False

def answer_evidence(raw,t):
 # Conservative task-success oracle, not a parser repair or replacement score.
 if t['category']=='multistep':return False,'No required tools executed; no output-only fix can satisfy full-task requirements'
 a=strict(raw);candidate=raw.strip()
 fence=re.fullmatch(r'```(?:json)?\s*\n?(.*?)\n?```',candidate,re.S|re.I)
 if a is None and fence:a=strict(fence.group(1));candidate=fence.group(1)
 if t['category']=='selection':
  good=isinstance(a,dict) and set(a)=={'tool','arguments'} and any(a['tool']==tool and a['arguments']==args for tool,args in t['required'])
  return good,'Single complete schema-correct required tool action with only external formatting' if good else 'No unambiguous complete correct next action'
 if isinstance(a,dict) and set(a)=={'final_answer'}:
  v=a['final_answer']
  if check_scalar(v,t):return True,'Explicit correct scalar answer; only representation differs'
  if isinstance(v,dict) and len(v)==1:
   k,val=next(iter(v.items()))
   metric=('spend','conversions','revenue')[t['condition']]
   if k.lower() in (metric,'observed_'+metric,'advertising_spend','result','value') and check_scalar(val,t):
    if k!='advertising_spend' or metric=='spend':return True,'Single labeled correct metric value in extra object wrapper'
  # A clear short prose assertion can be evaluated below.
  candidate=v if isinstance(v,str) else ''
 # Do not credit plans, embedded calls, multiple claims, wrong dates, or mere answer occurrence.
 if any(x in candidate.lower() for x in ('"tool"','observation_id','calculate_roas','we need','to determine','we will','ratio','per month','per day','average')):return False,'Ambiguous/mixed output; correct value occurrence alone is insufficient'
 dates=re.findall(r'\d{4}-\d{2}-\d{2}',candidate)
 if any(d not in (t['start'],t['end']) for d in dates):return False,'Changes the requested date scope'
 if t['category']=='extraction':
  metric=('spend','conversions','revenue')[t['condition']]
  target=re.search(r'for (google|meta|tiktok)',t['prompt']).group(1)
  cleaned=re.sub(r'\d{4}-\d{2}-\d{2}','',candidate)
  numbers=re.findall(r'(?<![\w])\d+(?:\.\d+)?',cleaned)
  if len(candidate)<300 and target in candidate.lower() and metric.rstrip('s') in candidate.lower() and numbers and all(Decimal(n)==t['expected'] for n in numbers):
   if re.search(r'\b(is|are|has|spent|spend|revenue|conversions)\b',candidate,re.I):return True,'Short explicit observed-metric assertion, correct platform/value, no competing numeric claim'
 if t['category']=='comparison':
  winners=[]
  patterns=[r'(google|meta|tiktok)\s+(?:has|had)\s+the\s+highest',r'(?:highest[^.!?\n]{0,130}?\bis\s+(?:from\s+)?)(google|meta|tiktok)']
  for p in patterns:winners+=re.findall(p,candidate,re.I)
  winners=[x.lower() for x in winners]
  if winners and set(winners)=={t['expected']} and len(candidate)<350:
   metric=('get_ad_spend','get_conversions','get_revenue')[t['condition']]
   cleaned=re.sub(r'\d{4}-\d{2}-\d{2}','',candidate)
   nums=re.findall(r'(?<![\w])\d+(?:\.\d+)?',cleaned)
   if all(Decimal(n)==t['values'][t['expected']][metric] for n in nums):return True,'Explicit unique correct winner assertion with no contradictory numerical claim'
 return False,'Semantic correctness not established conservatively'

analysis=[];mismatches=[]
for r in rows:
 t=tasks[r['task_id']];raw=r['trajectory'][-1]['raw_output'];a=strict(raw);flags=[]
 env=CapabilityEnvironment(t)
 for turn in r['trajectory']:
  if env.step(turn['raw_output'])!=turn['observation']:mismatches.append((r['task_id'],r['sample_id'],'observation'))
 if env.status!=r['status'] or int(env.status=='success')!=r['reward']:mismatches.append((r['task_id'],r['sample_id'],'reward'))
 oracle,evidence=answer_evidence(raw,t)
 if r['reward']:primary='success'
 elif oracle:primary='formatting/schema only (confirmed lower bound)'
 elif r['status']=='missing_requirements':primary='tool/action'
 elif isinstance(a,dict) and 'tool' in a:primary='tool/action'
 elif t['category']=='multistep' and isinstance(a,dict) and 'final_answer' in a:primary='tool/action'
 elif isinstance(a,dict) and set(a)=={'final_answer'} and ((t['category']=='comparison' and a['final_answer'] in ('google','meta','tiktok')) or (t['category']=='extraction' and type(a['final_answer']) is int)):primary='reasoning'
 elif re.search(r'(?:not provided|not available|do not have|please provide|only have|need you to provide)',raw,re.I) and t['category'] in ('extraction','comparison'):primary='context'
 else:primary='unclear/mixed'
 if 'calculate_roas' in raw:flags.append('ROAS material in irrelevant task')
 if isinstance(a,dict) and a.get('tool')=='calculate_roas' and r['status']=='unknown_tool':flags.append('advertised tool rejected as unknown by fixture environment')
 if isinstance(a,dict) and isinstance(a.get('arguments'),dict):
  args=a['arguments']
  if 'campaign' in args:flags.append('optional campaign advertised but rejected by fixture schema')
  if any(args.get(k) not in (None,t['start'] if k=='start_date' else t['end']) for k in ('start_date','end_date')):flags.append('incorrect date scope')
  if t['category']=='selection' and a.get('tool')!=t['required'][0][0]:flags.append('wrong requested metric/tool')
 if isinstance(a,dict) and 'final_answer' in a and t['category']=='multistep':flags.append('premature final answer with no observations')
 if r['status'] in ('invalid_json','invalid_format') and not oracle:flags.append('format verifier failure NOT proven formatting-only')
 analysis.append({**r,'primary_cause':primary,'conservative_oracle_success':bool(oracle or r['reward']),
   'oracle_evidence':evidence,'diagnostic_flags':flags})
assert len(rows)==640 and not mismatches
summary={}
for cat in ('extraction','comparison','selection','multistep','overall'):
 rs=[r for r in analysis if cat=='overall' or r['category']==cat]
 failures=[r for r in rs if not r['reward']];fmt=[r for r in rs if r['status'] in ('invalid_json','invalid_format')]
 summary[cat]={'attempts':len(rs),'successes':sum(r['reward'] for r in rs),'failures':len(failures),
 'verifier_failures':dict(collections.Counter(r['status'] for r in failures)),
 'primary_causes':dict(collections.Counter(r['primary_cause'] for r in failures)),
 'primary_percent_of_failures':{k:100*v/len(failures) for k,v in collections.Counter(r['primary_cause'] for r in failures).items()},
 'json_format_failures':len(fmt),'json_format_proven_only':sum(r['primary_cause'].startswith('formatting/') for r in fmt),
 'oracle_success_lower_bound':sum(r['conservative_oracle_success'] for r in rs),
 'flags':dict(collections.Counter(f for r in failures for f in r['diagnostic_flags']))}
(out/'audit.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in analysis))
(out/'metrics.json').write_text(json.dumps({'summary':summary,'source_sha256':hashes,'replay_mismatches':mismatches},indent=2)+'\n')
with (out/'audit.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['category','split','task_id','sample_id','seed','reward','verifier_status','primary_cause','oracle_success_lower_bound','evidence','flags'])
 for r in analysis:w.writerow([r['category'],r['split'],r['task_id'],r['sample_id'],r['seed'],r['reward'],r['status'],r['primary_cause'],r['conservative_oracle_success'],r['oracle_evidence'],'; '.join(r['diagnostic_flags'])])
# Representative selection covers distinct observed modes, without truncating traces.
selected=[]
for cat in ('extraction','comparison','selection','multistep'):
 rs=[r for r in analysis if r['category']==cat]
 predicates=[lambda r:r['reward'],lambda r:r['primary_cause'].startswith('formatting/'),lambda r:r['primary_cause']=='reasoning',lambda r:r['primary_cause']=='context',lambda r:r['status']=='unknown_tool',lambda r:r['status']=='wrong_final_answer' and r['category']=='multistep',lambda r:r['status']=='missing_requirements',lambda r:r['status']=='invalid_arguments',lambda r:r['status']=='invalid_json' and not r['conservative_oracle_success']]
 failures=0
 for pred in predicates:
  candidates=[r for r in rs if pred(r) and r not in selected]
  if candidates and (candidates[0]['reward'] or failures<5):
   selected.append(candidates[0]);failures+=not candidates[0]['reward']
 payload=[]
 for r in selected:
  if r['category']!=cat:continue
  t=tasks[r['task_id']];messages=[{'role':'system','content':data['system_prompt']},{'role':'user','content':t['prompt']}]
  payload.append({'task':t,'messages_reconstructed_from_frozen_inputs':messages,'expected_behavior':{'required_tools':t['required'],'final_action':None if t['category']=='selection' else {'final_answer':t['expected']},'selection_success_rule':'exact next required lookup' if t['category']=='selection' else None},'result':r})
 # all saved episodes are one action: no omitted prior steps
 assert all(len(x['result']['trajectory'])==1 for x in payload)
 (out/f'{cat}-representatives.json').write_text(json.dumps(payload,indent=2)+'\n')
parts=['<!doctype html><meta charset="utf-8"><title>Capability benchmark failure audit</title><style>body{max-width:1150px;margin:35px auto;padding:0 20px;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f4f4;padding:14px}section{border-top:1px solid #aaa;margin:25px 0}summary{cursor:pointer;padding:10px}</style><h1>Complete representative traces</h1><p>Inputs are reconstructed from the immutable dataset and the saved evaluation loop, not newly generated. All 640 episodes have exactly one saved action; no hidden tool observations are omitted. Original strings are preserved. Primary causes are conservative diagnostic labels, not replacement verifier scores.</p>']
for cat in ('extraction','comparison','selection','multistep'):
 parts.append('<h1>'+cat+'</h1>')
 for p in json.loads((out/f'{cat}-representatives.json').read_text()):
  r=p['result'];parts.append('<section><h2>'+html.escape(f"{r['task_id']} / sample {r['sample_id']} / seed {r['seed']} / {r['status']}")+'</h2>')
  for label,value in [('Task and fixture (labels evaluator-only)',p['task']),('Exact system/user input messages (reconstructed)',p['messages_reconstructed_from_frozen_inputs']),('Expected behavior',p['expected_behavior']),('Complete saved trajectory',r['trajectory']),('Diagnostic explanation',{'primary':r['primary_cause'],'evidence':r['oracle_evidence'],'flags':r['diagnostic_flags'],'reward':r['reward']})]:
   parts.append('<details open><summary>'+html.escape(label)+'</summary><pre>'+html.escape(json.dumps(value,indent=2,ensure_ascii=False))+'</pre></details>')
  parts.append('</section>')
(out/'representative-traces.html').write_text('\n'.join(parts))
print(json.dumps(summary,indent=2));print('Representatives',len(selected))
