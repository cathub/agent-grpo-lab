import json
import unittest
from src.episode_evaluation import evaluate_episodes
from src.evaluation import EvaluationMetadata
from src.qwen_agent import QwenAgent
from src.qwen_episodes import QwenEpisodeSampler
from src.scenarios import build_suite


class LoopTests(unittest.TestCase):
    def test_scripted_lookup_observation_final_and_termination(self):
        calls = []

        class Backend:
            def generate(self, messages, parameters):
                calls.append(messages)
                if len(calls) == 1:
                    self.action = json.dumps({'tool': 'get_ad_spend', 'arguments': {
                        'platform': 'google', 'campaign': 'brand',
                        'start_date': '2025-02-01', 'end_date': '2025-02-03'}})
                    return self.action
                if len(calls) == 2:
                    self_check.assertEqual(messages[2], {'role': 'assistant', 'content': self.action})
                    observation = json.loads(messages[3]['content'].removeprefix('Tool observation: '))
                    self_check.assertEqual(observation, {'id': 1, 'result': 129,
                                                         'done': False, 'status': None})
                    return '{"final_answer":129}'
                raise AssertionError('Generation continued after terminal final answer')

        self_check = self
        task = next(t for t in build_suite('train') if t.task_id == 'l2-train-campaign')
        results, _ = evaluate_episodes([task], QwenEpisodeSampler(QwenAgent(backend=Backend())),
                                      1, EvaluationMetadata('scripted', {}, 'test', 'unchanged'))
        self.assertEqual(len(calls), 2)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].reward, 1)
        self.assertEqual(results[0].tool_calls, 1)
        self.assertEqual(results[0].trajectory[-1].observation,
                         {'done': True, 'status': 'success'})
