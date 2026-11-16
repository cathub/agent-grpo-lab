import json
import unittest
from collections import Counter

from src.benchmark import build_tasks
from src.mock_agent import respond
from src.verifier import verify


class BenchmarkTests(unittest.TestCase):
    def test_fixture_is_stable_and_unique(self):
        tasks = build_tasks()
        self.assertEqual(tasks, build_tasks())
        self.assertEqual(len({task.prompt for task in tasks}), 20)
        self.assertEqual(Counter(task.tool for task in tasks), {
            "get_ad_spend": 8, "get_conversions": 8, "calculate_roas": 4,
        })

    def test_all_reference_calls_pass(self):
        for task in build_tasks():
            with self.subTest(prompt=task.prompt):
                call = json.dumps(dict(tool=task.tool, arguments=task.arguments))
                self.assertEqual(verify(call, task), "success")

    def test_mock_failure_breakdown(self):
        self.assertEqual(Counter(
            verify(respond(task.prompt), task) for task in build_tasks()
        ), {"success": 12, "wrong_arguments": 4,
            "invalid_json": 2, "wrong_tool": 2})
