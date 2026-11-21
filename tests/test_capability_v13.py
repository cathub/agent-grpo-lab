import itertools
import json
import re
import unittest
from src.capability_v13 import configuration,RULE
from src.capability_v11 import ROOT,DATASET,v1,schemas


class DecisionRuleTests(unittest.TestCase):
    def test_exact_single_insertion_and_no_hints(self):
        old=json.loads((ROOT/'benchmark-configs/capability-v1.2.json').read_text());new=configuration()
        self.assertEqual(new['system_prompt'],RULE+' '+old['system_prompt'])
        self.assertEqual(new['system_prompt'].count(RULE),1)
        self.assertEqual(schemas(new['system_prompt']),schemas(old['system_prompt']))
        self.assertEqual(new['system_prompt'][len(RULE)+1:],old['system_prompt'])
        self.assertFalse(re.search(r'\d|google|meta|tiktok',RULE,re.I))
        for k in ('dataset_sha256','scorer_snapshot_sha256','decoding','samples_per_instance','sampling_seed_base'):
            self.assertEqual(new[k],old[k])

    def test_boundary_consistency_on_reachable_frozen_states(self):
        # This checks concrete fixture semantics, not a formal proof of English.
        # Selection explicitly says requested metric missing; unrelated data
        # does not satisfy it. Multi-step has no supplied totals initially.
        data=json.loads(DATASET.read_text())
        for t in data['tasks']:
            if t['category'] in ('extraction','comparison'):
                self.assertEqual(t['required'],[])
                self.assertEqual(v1.CapabilityEnvironment(t).step(json.dumps({'final_answer':t['expected']}))['status'],'success')
            elif t['category']=='selection':
                self.assertIn('No value for this metric has been retrieved.',t['prompt'])
                self.assertIn('Return only the next tool action.',t['prompt'])
                self.assertEqual(len(t['required']),1)
            else:
                self.assertEqual(len(t['required']),3)
                for n in range(4):
                    for subset in itertools.combinations(t['required'],n):
                        env=v1.CapabilityEnvironment(t)
                        for tool,args in subset:env.step(json.dumps({'tool':tool,'arguments':args}))
                        obs=env.step(json.dumps({'final_answer':t['expected']}))
                        self.assertEqual(obs['status'],'success' if n==3 else 'missing_requirements')
