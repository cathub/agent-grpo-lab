import json
import unittest
from src.capability_v14 import generate,restore,semantic_value,DEMO
from src.capability_v11 import ROOT


class FinalizationTests(unittest.TestCase):
    def test_determinism_controls_and_no_demo_value_collision(self):
        data=generate();self.assertEqual(data,generate());self.assertEqual(len(data['instances']),12)
        self.assertEqual(data,json.loads(json.dumps(data)))
        baseline=json.loads((ROOT/'benchmark-configs/capability-v1.3.json').read_text())
        self.assertEqual(data['conditions']['A'],baseline['system_prompt'])
        self.assertEqual(data['conditions']['B'],baseline['system_prompt']+DEMO)
        for r in data['instances']:
            self.assertNotEqual(r['expected'],83)
            self.assertNotIn(83,[v for fields in r['values'].values() for v in fields.values()])
            self.assertIn(r['split'],('train','validation'))

    def test_all_reference_finals_pass_original_scorer(self):
        for r in generate()['instances']:
            env=restore(r)
            self.assertTrue(all(t.observation['result'] is not None for t in env.trajectory))
            self.assertEqual(env.step(json.dumps({'final_answer':r['expected']}))['status'],'success')
            env=restore(r)
            self.assertEqual(env.step(r['executed_history'][0]['raw_output'])['status'],'unnecessary_call')

    def test_semantic_diagnostic_is_not_strict_success(self):
        self.assertTrue(semantic_value({'id':1,'result':137},137))
        self.assertTrue(semantic_value({'final_answer':'137'},137))
        self.assertFalse(semantic_value({'final_answer':{'result':137}},137))
        self.assertFalse(semantic_value('The answer is 137',137))
        r=generate()['instances'][0];env=restore(r)
        self.assertEqual(env.step(json.dumps({'id':1,'result':r['expected']}))['status'],'invalid_format')

    def test_native_observations_and_known_float_prompt_conflict(self):
        data=generate()
        for r in data['instances']:
            for t in r['executed_history']:self.assertEqual(set(t['observation']),{'id','result','done','status'})
            self.assertEqual(r['prompt_type_mismatch'],r['family']=='float')
        self.assertIn('must be JSON integers',data['conditions']['A'])


class DiagnosticReportingTests(unittest.TestCase):
    def test_semantics_and_types_are_distinct(self):
        from src.report_capability_v14 import candidate_type
        self.assertTrue(semantic_value({'final_answer':'137'},137))
        self.assertFalse(candidate_type({'final_answer':'137'},137))
        self.assertTrue(candidate_type({'id':1,'result':137},137))
        self.assertFalse(candidate_type({'final_answer':True},1))
        self.assertFalse(candidate_type({'final_answer':137.0},137))
        self.assertTrue(candidate_type({'final_answer':137},137.375))

    def test_no_json_repair_in_diagnostics(self):
        from src.report_capability_v11 import parsed
        from src.report_capability_v12 import json_valid
        for raw in ('Assistant final action: {"final_answer":137}',
                    '```json\n{"final_answer":137}\n```',
                    '{"final_answer":137,"final_answer":138}'):
            self.assertFalse(json_valid(raw))
            self.assertIsNone(parsed(raw))
