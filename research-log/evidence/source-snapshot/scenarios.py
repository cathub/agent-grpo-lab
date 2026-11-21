"""Deterministic datasets and task specifications for the three levels."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from .benchmark import Task, build_tasks

PLATFORMS = ("google", "meta", "tiktok")
CAMPAIGNS = ("brand", "prospecting")
SPLITS = ("train", "validation", "test")
METRICS = {"get_ad_spend": "spend", "get_conversions": "conversions",
           "get_revenue": "revenue"}


@dataclass(frozen=True)
class Scope:
    platform: str
    start_date: str
    end_date: str
    campaign: Optional[str] = None


@dataclass(frozen=True)
class Row:
    platform: str
    campaign: str
    day: str
    spend: int
    conversions: int
    revenue: int


def build_rows():
    rows = []
    for week in range(3):
        for p, platform in enumerate(PLATFORMS):
            for c, campaign in enumerate(CAMPAIGNS):
                for day in range(4):
                    day_key = (date(2025, 2, 1) + timedelta(days=week * 7 + day)).isoformat()
                    spend = 40 + 17 * p + 13 * c + 3 * day + 7 * week
                    conversions = 2 + (3 * p + 2 * c + day + week) % 7
                    revenue = conversions * (24 + 5 * c + 3 * week)
                    rows.append(Row(platform, campaign, day_key, spend, conversions, revenue))
    return tuple(rows)


ROWS = build_rows()
DAYS = {row.day for row in ROWS}


def lookup(tool, scope):
    """Aggregate one metric within a validated, inclusive scope."""
    return sum(getattr(row, METRICS[tool]) for row in ROWS
               if row.platform == scope.platform
               and (scope.campaign is None or row.campaign == scope.campaign)
               and scope.start_date <= row.day <= scope.end_date)


@dataclass(frozen=True)
class EpisodeTask:
    task_id: str
    level: int
    split: str
    prompt: str
    expected_answer: object
    required_lookups: frozenset[tuple[str, Scope]] = frozenset()
    required_roas: frozenset[Scope] = frozenset()
    max_steps: int = 1
    legacy: Optional[Task] = None


def build_suite(split):
    """Return one split; the existing Level 1 fixture remains intact."""
    if split not in SPLITS:
        raise ValueError(f"Unknown split: {split}")
    week = SPLITS.index(split)
    tasks = [
        EpisodeTask(f"l1-{i + 1:02}", 1, split, task.prompt, None, legacy=task)
        for i, task in enumerate(build_tasks())
        if (0, 0, 1, 2)[i % 4] == week
    ]
    start = (date(2025, 2, 1) + timedelta(days=7 * week)).isoformat()
    end = (date.fromisoformat(start) + timedelta(days=2 + week % 2)).isoformat()
    window = f"{start} through {end} inclusive"
    first, second = PLATFORMS[week], PLATFORMS[(week + 1) % 3]
    one, two = Scope(first, start, end), Scope(second, start, end)
    brand = Scope(first, start, end, "brand")
    prospecting = Scope(first, start, end, "prospecting")
    conversion_tool, spend_tool, revenue_tool = "get_conversions", "get_ad_spend", "get_revenue"

    def add(level, name, prompt, answer, lookups, roas=()):
        tasks.append(EpisodeTask(
            f"l{level}-{split}-{name}", level, split, prompt, answer,
            frozenset(lookups), frozenset(roas), len(lookups) + len(roas) + 1,
        ))

    indexed_rows = {(r.platform, r.campaign, r.day): r for r in ROWS}

    def reference(tool, scope):
        # Compute labels directly from fixture rows, independently of tool dispatch.
        campaigns = (scope.campaign,) if scope.campaign else CAMPAIGNS
        return sum(getattr(indexed_rows[scope.platform, campaign, day], METRICS[tool])
                   for campaign in campaigns for day in sorted(DAYS)
                   if scope.start_date <= day <= scope.end_date)

    def ratio(scope):
        return reference(revenue_tool, scope) / reference(spend_tool, scope)

    comparison = (
        f"Which had more conversions, {first} or {second}, for {window}?",
        f"From {window}, name the higher-converting platform of {first} and {second}.",
        f"Compare total conversions over {window}: does {first} or {second} lead?",
    )[week]
    add(2, "platform", comparison + " Break ties by choosing the alphabetically later name.",
        max((one, two), key=lambda scope: (reference(conversion_tool, scope), scope.platform)).platform,
        [(conversion_tool, one), (conversion_tool, two)])
    add(2, "campaign", f"How much did {first}'s brand campaign spend in USD over {window}?",
        reference(spend_tool, brand), [(spend_tool, brand)])
    add(2, "combined", f"Give the combined revenue in USD for {first}'s brand and "
        f"{second}'s prospecting campaigns during {window}.",
        reference(revenue_tool, brand) + reference(revenue_tool, Scope(second, start, end, "prospecting")),
        [(revenue_tool, brand), (revenue_tool, Scope(second, start, end, "prospecting"))])

    add(3, "roas", f"Use the ROAS tool to calculate {first}'s brand campaign ROAS for {window}.",
        ratio(brand), [(revenue_tool, brand), (spend_tool, brand)], [brand])
    add(3, "campaign", f"Which {first} campaign, brand or prospecting, had higher ROAS during {window}? "
        "Calculate both with the ROAS tool. Break ties alphabetically.",
        max((brand, prospecting), key=lambda scope: (ratio(scope), scope.campaign == "brand")).campaign,
        [(tool, scope) for scope in (brand, prospecting) for tool in (revenue_tool, spend_tool)],
        [brand, prospecting])

    platform_scopes = tuple(Scope(p, start, end) for p in PLATFORMS)
    threshold = (25, 37, 28)[week]
    eligible = [scope for scope in platform_scopes if reference(conversion_tool, scope) >= threshold]
    winner = min(eligible, key=lambda scope: (-ratio(scope), scope.platform)).platform
    add(3, "constrained", f"For {window}, which platform had the highest ROAS among google, meta, "
        f"and tiktok with at least {threshold} conversions? Check conversions and calculate ROAS "
        "with the tool for all three. Break ties alphabetically.",
        winner, [(tool, scope) for scope in platform_scopes
                 for tool in (conversion_tool, revenue_tool, spend_tool)], platform_scopes)
    return tasks
