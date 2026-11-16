"""Simulated tools backed by three days of synthetic data."""

from datetime import date
from math import isfinite

# Each row stores (spend in USD, conversions).
DATA = {
    "google": ((100, 4), (120, 7), (80, 3)),
    "meta": ((70, 2), (90, 5), (110, 6)),
}
FIRST_DAY = date(2025, 1, 1)


def _total(platform, start_date, end_date, column):
    rows = DATA[platform]
    start = (date.fromisoformat(start_date) - FIRST_DAY).days
    end = (date.fromisoformat(end_date) - FIRST_DAY).days
    if not 0 <= start <= end < len(rows):
        raise ValueError("Date range must be within January 1–3, 2025")
    return sum(row[column] for row in rows[start:end + 1])


def get_ad_spend(platform, start_date, end_date):
    return _total(platform, start_date, end_date, 0)


def get_conversions(platform, start_date, end_date):
    return _total(platform, start_date, end_date, 1)


def calculate_roas(revenue, spend):
    if not all(isfinite(value) for value in (revenue, spend)):
        raise ValueError("Revenue and spend must be finite")
    if revenue < 0 or spend <= 0:
        raise ValueError("Revenue must be nonnegative and spend must be positive")
    return revenue / spend


TOOLS = {tool.__name__: tool for tool in (
    get_ad_spend, get_conversions, calculate_roas
)}
