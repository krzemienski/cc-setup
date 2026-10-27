"""Shared helpers for the proposal-generator skill.

Pure utility functions used by the engines and renderers. No external deps.
"""
from __future__ import annotations

import datetime as _dt
import re


def fmt_money(n: float, *, cents: bool = False) -> str:
    """Format a number as USD. Whole dollars by default ($10,000); cents on request."""
    if cents:
        return "${:,.2f}".format(n)
    return "${:,.0f}".format(round(n))


def fmt_hours(n: float) -> str:
    """Format hours without a trailing .0 for whole numbers."""
    return ("{:g}".format(n)) + "h"


def parse_date(s: str) -> _dt.date:
    """Parse an ISO date (YYYY-MM-DD)."""
    return _dt.datetime.strptime(s, "%Y-%m-%d").date()


def next_monday(from_date: _dt.date) -> _dt.date:
    """Resolve 'next Monday' relative to a date.

    Always returns a Monday strictly in the future relative to the calendar week:
    if from_date is itself a Monday, this returns the *following* Monday (7 days out),
    matching the colloquial meaning of "we'll start next Monday".
    """
    days_ahead = (7 - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return from_date + _dt.timedelta(days=days_ahead)


def resolve_start_date(value: str | None, run_date: _dt.date) -> _dt.date:
    """Resolve a start_date param. Empty / 'next-monday' / 'next monday' -> next Monday."""
    if not value or value.strip().lower().replace("_", "-") in ("next-monday", "next monday"):
        return next_monday(run_date)
    return parse_date(value)


def add_days(d: _dt.date, n: int) -> _dt.date:
    return d + _dt.timedelta(days=n)


def fmt_date_long(d: _dt.date) -> str:
    """'Monday, June 22, 2026' (zero-padded day stripped)."""
    return d.strftime("%A, %B ") + str(d.day) + d.strftime(", %Y")


def fmt_date_short(d: _dt.date) -> str:
    """'Jun 22'."""
    return d.strftime("%b ") + str(d.day)


def parse_week_range(value, fallback_min: int):
    """Parse a duration_weeks param into (min, max).

    Accepts '5-10', '5–10', '5 to 10', 5, '5', (5, 10), [5, 10], or None.
    Falls back to (fallback_min, fallback_min * 2) when unparseable.
    """
    if value is None:
        return fallback_min, fallback_min * 2
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    if isinstance(value, (int, float)):
        return int(value), int(value)
    s = str(value)
    nums = [int(x) for x in re.findall(r"\d+", s)]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], max(nums[0], fallback_min * 2)
    return fallback_min, fallback_min * 2


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ordered_phases(scope: dict) -> list[str]:
    """Phases in delivery order.

    Honors an explicit ``scope["phase_order"]`` when present (the reliable way to
    control narrative order, since a phase can legitimately appear in several
    deliverables). Any phase used by a task but missing from that list is appended
    in first-appearance order, so an incomplete phase_order can never drop a phase.
    Falls back to pure first-appearance order when no phase_order is given.
    """
    present: list[str] = []
    for d in scope["deliverables"]:
        for t in d["tasks"]:
            if t["phase"] not in present:
                present.append(t["phase"])
    explicit = scope.get("phase_order")
    if explicit:
        ordered = [p for p in explicit if p in present]
        ordered += [p for p in present if p not in ordered]
        return ordered
    return present
