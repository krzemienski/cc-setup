"""Timeline engine.

Turns a scope + params into a week-by-week timeline. One phase maps to one week,
in the scope's natural phase order, so the timeline always reads as a clean
narrative arc (Foundation -> ... -> Launch). The number of core weeks therefore
follows the scope's phase count; for a well-formed scope this equals
ceil(total_hours / weekly_hours), keeping the timeline and the billing cadence
in agreement. Everything derives from inputs -- nothing is hardcoded.
"""
from __future__ import annotations

import datetime as _dt

from common import (
    add_days,
    fmt_date_long,
    fmt_date_short,
    ordered_phases,
    parse_week_range,
    resolve_start_date,
)


def build_timeline(scope: dict, params: dict, run_date: _dt.date) -> dict:
    start = resolve_start_date(params.get("start_date"), run_date)
    phases = ordered_phases(scope)

    # Hours and deliverables touched per phase.
    phase_hours: dict[str, int] = {p: 0 for p in phases}
    phase_delivs: dict[str, list[str]] = {p: [] for p in phases}
    for d in scope["deliverables"]:
        for t in d["tasks"]:
            phase_hours[t["phase"]] += t["hours"]
            if d["id"] not in phase_delivs[t["phase"]]:
                phase_delivs[t["phase"]].append(d["id"])

    core_weeks = len(phases)
    min_w, max_w = parse_week_range(params.get("duration_weeks"), core_weeks)
    # The recommended core is the phase-driven week count, clamped into the stated range.
    recommended_weeks = max(min_w, min(core_weeks, max_w)) if min_w <= max_w else core_weeks

    weeks = []
    for i, phase in enumerate(phases):
        wk_start = add_days(start, i * 7)
        wk_end = add_days(wk_start, 4)  # Mon -> Fri
        weeks.append({
            "n": i + 1,
            "label": f"Week {i + 1}",
            "focus": phase,
            "deliverable_ids": phase_delivs[phase],
            "hours": phase_hours[phase],
            "start": wk_start.isoformat(),
            "end": wk_end.isoformat(),
            "dates_label": f"{fmt_date_short(wk_start)} – {fmt_date_short(wk_end)}",
        })

    return {
        "start_date": start.isoformat(),
        "start_label": fmt_date_long(start),
        "recommended_weeks": recommended_weeks,
        "core_weeks": core_weeks,
        "range": {"min_weeks": min_w, "max_weeks": max_w},
        "range_label": f"{min_w}–{max_w} weeks",
        "weeks": weeks,
    }
