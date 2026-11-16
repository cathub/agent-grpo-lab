import json
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.benchmark import build_tasks
from src.environment import Environment
from src.episode_evaluation import evaluate_episodes
from src.evaluation import EvaluationMetadata, write_evaluation
from src.scenarios import SPLITS, build_suite
from src.verifier import verify


def call(tool, **arguments):
    return json.dumps({"tool": tool, "arguments": arguments})


def final(answer):
    return json.dumps({"final_answer": answer})


class EpisodeTests(unittest.TestCase):
    def setUp(self):
        self.tasks = {task.task_id: task for task in build_suite("train")}
        self.roas = self.tasks["l3-train-roas"]
        self.scope = {
            "platform": "google", "campaign": "brand",
            "start_date": "2025-02-01", "end_date": "2025-02-03",
        }

    def test_roas_uses_matching_prior_observations_in_either_order(self):
        for first in ("get_revenue", "get_ad_spend"):
            with self.subTest(first=first):
                env = Environment(self.roas)
                second = "get_revenue" if first == "get_ad_spend" else "get_ad_spend"
                ids = {}
                values = {}
                for tool in (first, second):
                    observation = env.step(call(tool, **self.scope))
                    ids[tool] = {"observation_id": observation["id"]}
                    values[tool] = observation["result"]
                    observation["result"] = -1  # Caller edits cannot alter stored observations.
                self.assertEqual(values, {"get_revenue": 216, "get_ad_spend": 129})
                roas = env.step(call("calculate_roas", revenue=ids["get_revenue"],
                                     spend=ids["get_ad_spend"]))
                self.assertAlmostEqual(roas["result"], 216 / 129)
                self.assertEqual(env.step(final(roas["result"]))["status"], "success")
                self.assertEqual((env.tool_calls, len(env.trajectory)), (3, 4))

    def test_invalid_and_unnecessary_calls(self):
        for raw, status in (
            (call("unknown"), "unknown_tool"),
            (call("get_revenue", **dict(self.scope, platform="bad")), "invalid_arguments"),
            (call("get_revenue", **dict(self.scope, campaign="prospecting")), "unnecessary_call"),
            (call("calculate_roas", revenue=216, spend=129), "invalid_arguments"),
            (call("calculate_roas", revenue={"observation_id": 1},
                  spend={"observation_id": 2}), "invalid_observation_reference"),
        ):
            with self.subTest(status=status):
                self.assertEqual(Environment(self.roas).step(raw)["status"], status)
        env = Environment(self.roas)
        raw = call("get_revenue", **self.scope)
        env.step(raw)
        self.assertEqual(env.step(raw)["status"], "unnecessary_call")

    def test_execution_failure_wrong_answer_and_missing_requirements(self):
        campaign = self.tasks["l2-train-campaign"]
        raw = call("get_ad_spend", **self.scope)
        with patch("src.environment.lookup", side_effect=ValueError):
            self.assertEqual(Environment(campaign).step(raw)["status"], "execution_error")
        env = Environment(campaign)
        env.step(raw)
        self.assertEqual(env.step(final(999))["status"], "wrong_final_answer")
        self.assertFalse(env.final_answer_correct)
        env = Environment(campaign)
        self.assertEqual(env.step(final(129))["status"], "missing_requirements")
        self.assertTrue(env.final_answer_correct)

    def test_step_budget(self):
        env = Environment(replace(self.roas, max_steps=1))
        self.assertEqual(env.step(call("get_revenue", **self.scope))["status"], "step_limit_exceeded")
        self.assertEqual(len(env.trajectory), 1)
        with self.assertRaises(RuntimeError):
            env.step(final(216 / 129))

    def test_all_splits_preserve_legacy_and_have_separate_prompts_and_scopes(self):
        suites = [build_suite(split) for split in SPLITS]
        tasks = [task for suite in suites for task in suite]
        self.assertEqual(len(tasks), 38)
        self.assertEqual(len({task.task_id for task in tasks}), len(tasks))
        self.assertEqual(len({task.prompt for task in tasks}), len(tasks))
        self.assertCountEqual([task.legacy.prompt for task in tasks if task.legacy],
                              [task.prompt for task in build_tasks()])
        windows = [{(scope.start_date, scope.end_date) for task in suite
                    for _, scope in task.required_lookups} for suite in suites]
        self.assertEqual(sum(map(len, windows)), len(set.union(*windows)))

        for task in tasks:
            if task.legacy:
                raw = call(task.legacy.tool, **task.legacy.arguments)
                self.assertEqual(Environment(task).step(raw)["status"], verify(raw, task.legacy))

    def test_constrained_task_requires_all_platform_checks(self):
        task = self.tasks["l3-train-constrained"]
        env = Environment(task)
        by_platform = {}
        for platform in ("tiktok", "google", "meta"):
            scope = dict(platform=platform, start_date="2025-02-01", end_date="2025-02-03")
            conversions = env.step(call("get_conversions", **scope))["result"]
            spend = env.step(call("get_ad_spend", **scope))["id"]
            revenue = env.step(call("get_revenue", **scope))["id"]
            ratio = env.step(call("calculate_roas", revenue={"observation_id": revenue},
                                  spend={"observation_id": spend}))["result"]
            by_platform[platform] = conversions, ratio
        eligible = [p for p, (conversions, _) in by_platform.items() if conversions >= 25]
        self.assertCountEqual(eligible, ["meta", "tiktok"])
        self.assertEqual(env.step(final(max(eligible, key=lambda p: by_platform[p][1])))["status"],
                         "success")

    def test_level_metrics_and_logging(self):
        campaign = self.tasks["l2-train-campaign"]
        legacy = self.tasks["l1-01"]

        def sampler(prompt, level, sample_id):
            if level == 1:
                return lambda history: "{" if sample_id == 2 else call(
                    "get_ad_spend", platform="google", start_date="2025-01-01", end_date="2025-01-01")

            def session(history):
                if not history:
                    return call("get_ad_spend", **self.scope)
                return final(history[-1].observation["result"] if sample_id == 1 else 999)
            return session

        metadata = EvaluationMetadata("test-fixture", {}, "levels-v1", "levels-v1")
        rollouts, summary = evaluate_episodes([legacy, campaign], sampler, 2, metadata)
        level1, level2 = (summary["by_level"][level] for level in ("1", "2"))
        self.assertIsNone(level1["final_answer_correctness"])
        self.assertEqual(level2["task_success_rate"], 0.5)
        self.assertEqual(level2["informative_group_ratio"], 1.0)
        self.assertEqual(level2["average_tool_calls_per_task"], 1.0)
        self.assertEqual(level2["trajectory_length_counts"], {"2": 2})
        self.assertEqual(level2["final_answer_correctness"], 0.5)
        self.assertEqual(level2["failure_category_counts"], {"wrong_final_answer": 1})
        with TemporaryDirectory() as temp:
            path = Path(temp)
            write_evaluation(path, rollouts, summary)
            rows = [json.loads(line) for line in (path / "rollouts.jsonl").read_text().splitlines()]
            self.assertEqual(rows[2]["trajectory"][0], asdict(rollouts[2].trajectory[0]))
