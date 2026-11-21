import json
import tempfile
import unittest
from pathlib import Path
from src.environment import Turn
from src.qwen_agent import QwenAgent
from src.qwen_episodes import QwenEpisodeSampler, run


class Backend:
    def __init__(self):
        self.calls = []

    def generate(self, messages, parameters):
        self.calls.append(messages)
        return '{'


class EpisodeAdapterTests(unittest.TestCase):
    def test_history_is_raw_and_sessions_are_isolated(self):
        backend = Backend()
        factory = QwenEpisodeSampler(QwenAgent(backend=backend))
        session = factory('task prompt', 3, 1)
        raw = '{"tool":"get_revenue","arguments":{}}'
        self.assertEqual(session((Turn(raw, {'id': 1, 'result': 42}),)), '{')
        messages = backend.calls[-1]
        self.assertEqual(messages[1]['content'], 'task prompt')
        self.assertEqual(messages[2]['content'], raw)
        self.assertIn('42', messages[3]['content'])
        self.assertIn('observation_id', messages[0]['content'])
        factory('other task', 2, 1)(())
        self.assertEqual(len(backend.calls[-1]), 2)

    def test_both_training_levels_preserve_invalid_output(self):
        for level in (2, 3):
            backend = Backend()
            with tempfile.TemporaryDirectory() as directory:
                results, summary = run(QwenAgent(backend=backend), level, Path(directory))
                self.assertEqual(len(results), 3)
                self.assertTrue(all(r.failure_category == 'invalid_json' for r in results))
                self.assertTrue(all(r.trajectory[0].raw_output == '{' for r in results))
                self.assertEqual(len(backend.calls), 3)
                self.assertEqual(summary['by_level'][str(level)]['rollout_count'], 3)
