"""A prompt-only mock with predictable parsing mistakes."""

import json
import re


def respond(prompt, *, inject_errors=True):
    lookup = re.fullmatch(
        r"Get (spend|conversions) for (\w+) from ([\d-]+) through ([\d-]+)\.",
        prompt,
    )
    if lookup:
        metric, platform, start, end = lookup.groups()
        if inject_errors and platform == "meta" and start == end == "2025-01-02":
            return '{"tool":'
        tool = "get_ad_spend" if metric == "spend" else "get_conversions"
        if inject_errors and metric == "conversions" and start == end == "2025-01-03":
            tool = "get_ad_spend"
        if inject_errors and start != end:
            end = start  # This mock drops the end of multi-day ranges.
        arguments = dict(platform=platform, start_date=start, end_date=end)
    else:
        roas = re.fullmatch(r"Compute ROAS for revenue \$(\d+) and spend \$(\d+)\.", prompt)
        if not roas:
            return "{}"
        revenue, spend = map(int, roas.groups())
        tool = "calculate_roas"
        arguments = dict(revenue=revenue, spend=spend)
    return json.dumps(dict(tool=tool, arguments=arguments))
