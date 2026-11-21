import json
import unittest
from src.capability_v12 import configuration,messages
from src.capability_v11 import DATASET,ROOT,v1,schemas,contract_preflight


class ProtocolTests(unittest.TestCase):
    def test_protocol_diagnostics_do_not_replace_rewards(self):
        from src.report_capability_v12 import json_valid,protocol_valid
        self.assertTrue(json_valid('null'))
        self.assertFalse(protocol_valid('null'))
        self.assertFalse(json_valid('{"x":1,"x":2}'))
        self.assertFalse(protocol_valid('{"final_answer":"129"}'))
        self.assertFalse(protocol_valid('{"final_answer":129.0}'))
        self.assertTrue(protocol_valid('{"final_answer":129}'))
        self.assertTrue(protocol_valid('{"final_answer":"meta"}'))
        self.assertFalse(protocol_valid('{"tool":"get_revenue","arguments":{},"final_answer":1}'))

    def test_schemas_and_example_unchanged(self):
        a=json.loads((ROOT/'benchmark-configs/capability-v1.1.json').read_text())
        b=configuration()
        self.assertEqual(a['system_prompt'].split('Available tool schemas: ')[1],b['system_prompt'].split('Available tool schemas: ')[1])
        self.assertEqual(schemas(a['system_prompt']),schemas(b['system_prompt']))
        self.assertEqual(contract_preflight()['contract_cases'],9)
        # Existing generic example is executable in a matching synthetic scope;
        # its dates are NOT claimed to match any frozen benchmark task.
        raw=b['system_prompt'].split('Example tool action (raw JSON, without Markdown fences): ')[1]
        action=json.loads(raw);args=action['arguments']
        task={'category':'selection','expected':None,'required':[(action['tool'],args)],
              'values':{args['platform']:{action['tool']:7}}}
        env=v1.CapabilityEnvironment(task)
        self.assertEqual(env.step(raw)['status'],'success')

    def test_negative_actions_and_integer_contract(self):
        data=json.loads(DATASET.read_text());task=next(t for t in data['tasks'] if t['category']=='extraction')
        for raw,expected in [('{','invalid_json'),('{"final_answer":1,"final_answer":2}','invalid_json'),
            (json.dumps({'final_answer':str(task['expected'])}),'wrong_final_answer'),
            (json.dumps({'final_answer':float(task['expected'])}),'wrong_final_answer'),
            (json.dumps({'final_answer':task['expected']}),'success'),
            ('{"tool":"unsupported","arguments":{}}','unknown_tool'),
            ('{"tool":"get_ad_spend","arguments":{"platform":3,"start_date":"x","end_date":"y"}}','invalid_arguments'),
            ('{"tool-action":"get_ad_spend","arguments":{}}','invalid_format')]:
            self.assertEqual(v1.CapabilityEnvironment(task).step(raw)['status'],expected)

    def test_lookup_observation_continuation_final(self):
        task=next(t for t in json.loads(DATASET.read_text())['tasks'] if t['category']=='multistep')
        env=v1.CapabilityEnvironment(task)
        for tool,args in task['required']:
            raw=json.dumps({'tool':tool,'arguments':args});observation=env.step(raw)
            m=messages(configuration()['system_prompt'],task,env.trajectory)
            self.assertEqual(m[-2],{'role':'assistant','content':raw})
            self.assertEqual(m[-1],{'role':'user','content':'Tool observation: '+json.dumps(observation)})
            self.assertFalse(observation['done'])
        self.assertEqual(env.step(json.dumps({'final_answer':task['expected']}))['status'],'success')
