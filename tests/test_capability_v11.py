import json
import unittest
from src.capability_v11 import configuration, contract_preflight, DATASET, schemas


class ContractTests(unittest.TestCase):
    def test_executable_contract_and_four_category_smoke(self):
        report=contract_preflight()
        self.assertEqual(report['contract_cases'],9)
        self.assertEqual(report['scripted_category_smokes'],4)

    def test_only_contract_material_changes(self):
        original=json.loads(DATASET.read_text())['system_prompt']
        config=configuration();updated=config['system_prompt']
        self.assertNotIn('calculate_roas',updated)
        self.assertNotIn('campaign',updated)
        self.assertEqual(original.split('] Example tool action')[-1],updated.split('] Example tool action')[-1])
        old={s['name']:s for s in schemas(original)}
        for s in schemas(updated):
            prior=old[s['name']]
            del prior['parameters']['properties']['campaign']
            self.assertEqual(s,prior)
        self.assertEqual(config['decoding'],json.loads(DATASET.read_text())['decoding'])
