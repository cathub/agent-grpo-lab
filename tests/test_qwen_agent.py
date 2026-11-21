import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from src.qwen_agent import GenerationParameters, MLXBackend, QwenAgent
from src.qwen_evaluation import run


class FakeBackend:
    def __init__(self, output):
        self.output, self.calls = output, []

    def generate(self, messages, parameters):
        self.calls.append((messages, parameters))
        return self.output


class QwenTests(unittest.TestCase):
    def test_prompt_and_raw_output(self):
        backend = FakeBackend('bad JSON')
        self.assertEqual(QwenAgent(backend=backend).sample('user task'), ['bad JSON'])
        messages, parameters = backend.calls[0]
        self.assertEqual(messages[1], {'role': 'user', 'content': 'user task'})
        schemas = json.loads(messages[0]['content'].split('Available tool schemas: ')[1])
        self.assertEqual({s['name'] for s in schemas},
                         {'get_ad_spend', 'get_conversions', 'calculate_roas'})
        self.assertNotIn('expected_result', messages[0]['content'])
        self.assertEqual(parameters.max_tokens, 128)

    def test_train_split_and_logs(self):
        backend = FakeBackend('{')
        with tempfile.TemporaryDirectory() as directory:
            rollouts, summary = run(QwenAgent(model_id='fake', backend=backend), Path(directory))
            self.assertEqual(len(rollouts), 10)
            self.assertEqual(len(backend.calls), 10)
            self.assertEqual(summary['failure_category_counts'], {'invalid_json': 10})
            self.assertEqual(summary['task_success_rate'], 0)
            saved = json.loads((Path(directory) / 'summary.json').read_text())
            self.assertEqual(saved['metadata']['model'], 'fake')
            self.assertEqual(saved['metadata']['sampling_parameters']['seed'], 0)
            records = [json.loads(s) for s in
                       (Path(directory) / 'rollouts.jsonl').read_text().splitlines()]
            self.assertTrue(all(r['raw_output'] == '{' for r in records))

    def test_existing_verifier_success(self):
        from src.benchmark import build_tasks
        from src.evaluation import evaluate, EvaluationMetadata
        backend = FakeBackend('{"tool":"get_ad_spend","arguments":{"platform":"google",'
                              '"start_date":"2025-01-01","end_date":"2025-01-01"}}')
        _, summary = evaluate(build_tasks()[:1], QwenAgent(backend=backend).sample,
                              EvaluationMetadata('fake', {}, 'day1-v1', 'day1-v1'))
        self.assertEqual(summary['task_success_rate'], 1)

    def test_chat_template_and_generation(self):
        tokenizer = Mock()
        tokenizer.apply_chat_template.return_value = 'formatted chat'
        generate, sampler = Mock(return_value='raw'), Mock(return_value='sampler')
        backend = MLXBackend.__new__(MLXBackend)
        backend.model, backend.tokenizer = object(), tokenizer
        messages = [{'role': 'user', 'content': 'hi'}]
        with patch.dict('sys.modules', {
            'mlx_lm': SimpleNamespace(generate=generate),
            'mlx_lm.sample_utils': SimpleNamespace(make_sampler=sampler),
        }):
            self.assertEqual(backend.generate(messages, GenerationParameters()), 'raw')
        tokenizer.apply_chat_template.assert_called_once_with(
            messages, tokenize=False, add_generation_prompt=True)
        self.assertEqual(generate.call_args.kwargs['prompt'], 'formatted chat')
        self.assertEqual(generate.call_args.kwargs['max_tokens'], 128)
        sampler.assert_called_once_with(temp=0.0, top_p=1.0)

    def test_invalid_parameters(self):
        for kwargs in ({'max_tokens': 0}, {'temperature': -1}, {'top_p': 0}):
            with self.assertRaises(ValueError):
                GenerationParameters(**kwargs)
