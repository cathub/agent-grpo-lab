import unittest
from types import SimpleNamespace
from src.environment import Turn
from src.qwen_prompt_comparison import SystemPromptBackend, first_tool_executed


class ComparisonTests(unittest.TestCase):
    def test_only_system_content_changes(self):
        captured = []
        backend = SimpleNamespace(generate=lambda m, p: captured.append((m, p)) or 'raw')
        messages = [{'role': 'system', 'content': 'old'},
                    {'role': 'user', 'content': 'task'},
                    {'role': 'assistant', 'content': '{'},
                    {'role': 'user', 'content': 'observation'}]
        parameters = object()
        self.assertEqual(SystemPromptBackend(backend, 'new').generate(messages, parameters), 'raw')
        self.assertEqual(messages[0]['content'], 'old')
        self.assertEqual(captured[0][0][1:], messages[1:])
        self.assertIs(captured[0][1], parameters)

    def test_execution_metric_excludes_attempts_and_final_answers(self):
        for observation, expected in [({'result': 0, 'id': 1}, True),
                                      ({'status': 'invalid_json'}, False),
                                      ({'status': 'success'}, False)]:
            result = SimpleNamespace(trajectory=(Turn('raw', observation),))
            self.assertEqual(first_tool_executed(result), expected)
