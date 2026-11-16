"""Fixed tasks and a command-line benchmark runner."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .mock_agent import respond
from .verifier import verify


@dataclass(frozen=True)
class Task:
    prompt: str
    tool: str
    arguments: dict
    expected_result: int | float


def build_tasks():
    ranges = ((1, 1), (2, 2), (3, 3), (1, 3))
    # Expected values are independent of the tool implementation.
    scenarios = (
        ("google", "spend", "get_ad_spend", (100, 120, 80, 300)),
        ("meta", "spend", "get_ad_spend", (70, 90, 110, 270)),
        ("google", "conversions", "get_conversions", (4, 7, 3, 14)),
        ("meta", "conversions", "get_conversions", (2, 5, 6, 13)),
    )
    tasks = []
    for platform, metric, tool, results in scenarios:
        for (first, last), result in zip(ranges, results):
            start, end = f"2025-01-{first:02}", f"2025-01-{last:02}"
            tasks.append(Task(
                f"Get {metric} for {platform} from {start} through {end}.",
                tool, dict(platform=platform, start_date=start, end_date=end),
                result,
            ))
    for revenue, spend, result in ((0, 50, 0), (90, 60, 1.5),
                                   (125, 100, 1.25), (300, 75, 4)):
        tasks.append(Task(
            f"Compute ROAS for revenue ${revenue} and spend ${spend}.",
            "calculate_roas", dict(revenue=revenue, spend=spend), result,
        ))
    return tasks


def main():
    tasks = build_tasks()
    counts = Counter(verify(respond(task.prompt), task) for task in tasks)
    successes = counts.pop("success", 0)
    print(f"Success rate: {successes}/{len(tasks)} ({successes / len(tasks):.1%})")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
