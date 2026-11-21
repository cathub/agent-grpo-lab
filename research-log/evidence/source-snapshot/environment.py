"""Execute one JSON action at a time against a deterministic task."""

import json
from copy import deepcopy
from dataclasses import dataclass
from math import isclose

from .scenarios import CAMPAIGNS, DAYS, METRICS, PLATFORMS, Scope, lookup
from .tools import calculate_roas
from .verifier import _invalid_constant, _object, verify


@dataclass(frozen=True)
class Turn:
    raw_output: str
    observation: dict


class Environment:
    def __init__(self, task):
        self.task = task
        self._history = []
        self._lookups = {}
        self._roas = set()
        self.status = None
        self.tool_calls = 0
        self.final_answer_correct = None

    @property
    def trajectory(self):
        return tuple(deepcopy(self._history))

    @property
    def done(self):
        return self.status is not None

    def _record(self, raw_output, observation, status=None):
        if status is None and len(self._history) + 1 >= self.task.max_steps:
            status = "step_limit_exceeded"
        self.status = status
        observation = {**observation, "done": self.done, "status": status}
        self._history.append(Turn(raw_output, observation))
        return deepcopy(observation)

    def step(self, raw_output):
        if self.done:
            raise RuntimeError("Episode has already ended")
        if self.task.legacy is not None:
            self.tool_calls = 1
            status = verify(raw_output, self.task.legacy)
            return self._record(raw_output, {}, status)

        try:
            action = json.loads(raw_output, object_pairs_hook=_object,
                                parse_constant=_invalid_constant)
        except (ValueError, TypeError, RecursionError):
            return self._record(raw_output, {}, "invalid_json")
        if not isinstance(action, dict):
            return self._record(raw_output, {}, "invalid_format")
        if action.keys() == {"final_answer"}:
            return self._record(raw_output, {}, self._finish(action["final_answer"]))
        if "tool" in action:
            self.tool_calls += 1
        if (action.keys() != {"tool", "arguments"} or not isinstance(action["tool"], str)
                or not isinstance(action["arguments"], dict)):
            return self._record(raw_output, {}, "invalid_format")

        tool, args = action["tool"], action["arguments"]
        status, result = self._call(tool, args)
        if status:
            return self._record(raw_output, {}, status)
        return self._record(raw_output, {"id": len(self._history) + 1, "result": result})

    def _finish(self, answer):
        expected = self.task.expected_answer
        if type(expected) is float and type(answer) in (int, float):
            try:
                self.final_answer_correct = isclose(answer, expected, rel_tol=1e-6, abs_tol=1e-9)
            except OverflowError:
                self.final_answer_correct = False
        else:
            self.final_answer_correct = type(answer) is type(expected) and answer == expected
        if not self.final_answer_correct:
            return "wrong_final_answer"
        if self._lookups.keys() != self.task.required_lookups or self._roas != self.task.required_roas:
            return "missing_requirements"
        return "success"

    def _call(self, tool, args):
        if tool == "calculate_roas":
            return self._calculate_roas(args)
        if tool not in METRICS:
            return "unknown_tool", None

        required = {"platform", "start_date", "end_date"}
        if not required <= args.keys() <= required | {"campaign"}:
            return "invalid_arguments", None
        if any(not isinstance(value, str) for value in args.values()):
            return "invalid_arguments", None
        scope = Scope(**args)
        if (scope.platform not in PLATFORMS or scope.start_date not in DAYS
                or scope.end_date not in DAYS or scope.start_date > scope.end_date
                or (scope.campaign is not None and scope.campaign not in CAMPAIGNS)):
            return "invalid_arguments", None

        key = tool, scope
        if key not in self.task.required_lookups or key in self._lookups:
            return "unnecessary_call", None
        try:
            result = lookup(tool, scope)
        except (ValueError, TypeError, KeyError, ArithmeticError):
            return "execution_error", None
        self._lookups[key] = len(self._history) + 1
        return None, result

    def _calculate_roas(self, args):
        if args.keys() != {"revenue", "spend"}:
            return "invalid_arguments", None
        refs = [args[key] for key in ("revenue", "spend")]
        if any(not isinstance(ref, dict) or ref.keys() != {"observation_id"}
               or type(ref["observation_id"]) is not int for ref in refs):
            return "invalid_arguments", None
        revenue_id, spend_id = (ref["observation_id"] for ref in refs)
        observed = {number: key for key, number in self._lookups.items()}
        revenue = observed.get(revenue_id)
        if (revenue is None or revenue[0] != "get_revenue"
                or observed.get(spend_id) != ("get_ad_spend", revenue[1])):
            return "invalid_observation_reference", None
        scope = revenue[1]
        if scope not in self.task.required_roas or scope in self._roas:
            return "unnecessary_call", None
        try:
            result = calculate_roas(self._history[revenue_id - 1].observation["result"],
                                    self._history[spend_id - 1].observation["result"])
        except (ValueError, TypeError, KeyError, ArithmeticError):
            return "execution_error", None
        self._roas.add(scope)
        return None, result


def main():
    """List a split or play one task by supplying JSON actions on stdin."""
    import argparse

    from .scenarios import SPLITS, build_suite

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("split", choices=SPLITS)
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    tasks = {task.task_id: task for task in build_suite(args.split)}
    if args.task_id is None:
        for task in tasks.values():
            print(f"{task.task_id}  {task.prompt}")
        return
    if args.task_id not in tasks:
        parser.error(f"Unknown task ID for {args.split}: {args.task_id}")

    task = tasks[args.task_id]
    env = Environment(task)
    print(task.prompt)
    print(f"Step limit: {task.max_steps}. Enter one JSON action per line.")
    while not env.done:
        try:
            raw_output = input()
        except EOFError:
            parser.exit(1, "Input ended before the episode finished.\n")
        print(json.dumps(env.step(raw_output)))
    print(f"Reward: {float(env.status == 'success'):.1f}")


if __name__ == "__main__":
    main()
