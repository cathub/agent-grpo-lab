import json
import tempfile
import unittest
from pathlib import Path

from src.benchmark import build_tasks
from src.evaluation import EvaluationMetadata, evaluate, mock_sample, write_evaluation


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tasks = build_tasks()
        self.metadata = EvaluationMetadata("test", {}, "test-data", "test-verifier")

    def test_group_outcomes(self):
        good = list(mock_sample(self.tasks[0].prompt))[1]
        bad = '{"tool":'
        for outputs, successes, rate, variance, informative in (
            ([good, good], 2, 1.0, 0.0, False),
            ([bad, bad], 0, 0.0, 0.0, False),
            ([good, bad], 1, 0.5, 0.25, True),
            ([], 0, 0.0, 0.0, False),
        ):
            with self.subTest(outputs=outputs):
                rollouts, summary = evaluate(self.tasks[:1], lambda _: outputs, self.metadata)
                group = summary["prompt_groups"]["task-01"]
                self.assertEqual(group["sample_count"], len(outputs))
                self.assertEqual(group["success_count"], successes)
                self.assertEqual(group["success_rate"], rate)
                self.assertEqual(group["mean_reward"], rate)
                self.assertEqual(group["reward_variance"], variance)
                self.assertEqual(group["informative"], informative)
                self.assertEqual(summary["task_success_rate"], rate)
                self.assertEqual(summary["informative_group_ratio"], float(informative))
                self.assertEqual([r.raw_output for r in rollouts], outputs)

    def test_aggregation_and_logs(self):
        first, second, third = self.tasks[:3]
        good = list(mock_sample(first.prompt))[1]
        samples = {first.prompt: [good, good, "{"], second.prompt: ["{"], third.prompt: []}
        rollouts, summary = evaluate(self.tasks[:3], samples.__getitem__, self.metadata)
        self.assertEqual(summary["task_success_rate"], 0.5)
        self.assertEqual(summary["informative_group_ratio"], 1 / 3)
        self.assertEqual(summary["reward_distribution"], {"0": 2, "1": 2})
        self.assertEqual(summary["failure_category_counts"], {"invalid_json": 2})

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            write_evaluation(path, rollouts, summary)
            self.assertEqual(json.loads((path / "summary.json").read_text()), summary)
            rows = [json.loads(line) for line in (path / "rollouts.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertIsNone(rows[0]["failure_category"])
        self.assertEqual(rows[2]["verifier_details"], {"status": "invalid_json"})
        self.assertEqual((rows[-1]["task_id"], rows[-1]["sample_id"]), ("task-02", 1))

    def test_empty_dataset(self):
        rollouts, summary = evaluate([], mock_sample, self.metadata)
        self.assertEqual(rollouts, [])
        self.assertEqual(summary["task_success_rate"], 0.0)
        self.assertEqual(summary["informative_group_ratio"], 0.0)

    def test_mock_is_reproducible(self):
        first = evaluate(self.tasks, mock_sample, self.metadata)
        self.assertEqual(first, evaluate(self.tasks, mock_sample, self.metadata))
        self.assertEqual(first[1]["rollout_count"], 80)
        self.assertEqual(first[1]["success_count"], 64)
        self.assertEqual(first[1]["informative_group_count"], 8)
