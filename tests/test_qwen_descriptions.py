import json
import unittest
from src.qwen_description_experiment import enhanced_prompt
from src.qwen_episodes import episode_instructions


class DescriptionTests(unittest.TestCase):
    def test_only_tool_descriptions_change(self):
        a_prefix, a = episode_instructions().split('Available tool schemas: ', 1)
        b_prefix, b = enhanced_prompt().split('Available tool schemas: ', 1)
        self.assertEqual(a_prefix, b_prefix)
        a, b = json.loads(a), json.loads(b)
        self.assertEqual(len(a), len(b))
        for old, new in zip(a, b):
            self.assertNotEqual(old['description'], new['description'])
            old.pop('description')
            new.pop('description')
        self.assertEqual(a, b)
