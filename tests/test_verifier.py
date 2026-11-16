import json
import unittest
from dataclasses import replace

from src.benchmark import build_tasks
from src.verifier import verify


class VerifierTests(unittest.TestCase):
    def test_rejections(self):
        task = build_tasks()[0]
        for response, expected in (
            ('{"tool":', "invalid_json"),
            ('{"tool":"a","tool":"b"}', "invalid_json"),
            ('{"tool":NaN}', "invalid_json"),
            ('[]', "invalid_format"),
            ('{"tool":"get_ad_spend","arguments":[]}', "invalid_format"),
            ('{"tool":"no_such_tool","arguments":{}}', "wrong_tool"),
            ('{"tool":"get_ad_spend","arguments":{}}', "wrong_arguments"),
        ):
            with self.subTest(response=response):
                self.assertEqual(verify(response, task), expected)

    def test_result_mismatch(self):
        task = replace(build_tasks()[0], expected_result=-1)
        response = json.dumps(dict(tool=task.tool, arguments=task.arguments))
        self.assertEqual(verify(response, task), "wrong_result")

    def test_execution_error(self):
        task = replace(build_tasks()[-1], arguments=dict(revenue=300, spend=0))
        response = json.dumps(dict(tool=task.tool, arguments=task.arguments))
        self.assertEqual(verify(response, task), "execution_error")

    def test_boolean_is_not_a_number(self):
        task = build_tasks()[-4]  # Expected revenue is zero.
        response = json.dumps(dict(tool=task.tool, arguments=dict(revenue=False, spend=50)))
        self.assertEqual(verify(response, task), "wrong_arguments")
