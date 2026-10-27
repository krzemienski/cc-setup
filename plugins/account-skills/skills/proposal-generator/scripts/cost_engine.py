"""Cost engine.

Derives estimations and the full cost model from scope + params. Two framings are
always produced side by side: the *headline* (a flat anchor price, e.g. the full
build) and the *recommended* initial build (scope hours x hourly rate). The weekly
payment schedule encodes the pay-as-you-go cadence: a down payment covering the
first weeks, then flat weekly billing, with the final week truing up so the schedule
reconciles exactly to the recommended amount. Nothing is hardcoded -- the Get Path
figures are defaults supplied by build_proposal, not constants here.
"""
from __future__ import annotations

from common import fmt_money, ordered_phases


def compute_estimations(scope: dict) -> dict:
    by_deliverable = []
    phase_hours: dict[str, int] = {}
    total = 0
    for d in scope["deliverables"]:
        dh = sum(t["hours"] for t in d["tasks"])
        total += dh
        by_deliverable.append({"id": d["id"], "name": d["name"], "hours": dh})
        for t in d["tasks"]:
            phase_hours[t["phase"]] = phase_hours.get(t["phase"], 0) + int(t["hours"])

    for row in by_deliverable:
        row["pct"] = round(row["hours"] / total * 100, 1) if total else 0.0

    # Use the scope's declared delivery order (phase_order) when present.
    by_phase = []
    for ph in ordered_phases(scope):
        hrs = phase_hours.get(ph, 0)
        by_phase.append({
            "phase": ph,
            "hours": hrs,
            "pct": round(hrs / total * 100, 1) if total else 0.0,
        })

    return {"total_hours": total, "by_deliverable": by_deliverable, "by_phase": by_phase}


def compute_costs(scope: dict, params: dict, estimations: dict, timeline: dict) -> dict:
    hourly_rate = params["hourly_rate"]
    weekly_hours = params["weekly_hours"]
    weekly_rate = hourly_rate * weekly_hours
    total_hours = estimations["total_hours"]

    recommended_amount = total_hours * hourly_rate
    headline_amount = params["headline_amount"]
    headline_weeks = params["headline_weeks"]

    # Line items: one per deliverable (build), summing to the recommended amount,
    # plus a zero-cost "included" line that surfaces the AI/agent-costs-included framing.
    line_items = []
    for row in estimations["by_deliverable"]:
        line_items.append({
            "label": row["name"],
            "detail": f"{row['hours']} hrs @ {fmt_money(hourly_rate)}/hr",
            "amount": row["hours"] * hourly_rate,
            "kind": "build",
        })
    line_items.append({
        "label": "AI / agent runtime + tooling",
        "detail": "Model usage, agent orchestration, and dev tooling",
        "amount": 0,
        "kind": "included",
    })

    build_sum = sum(li["amount"] for li in line_items if li["kind"] == "build")
    assert build_sum == recommended_amount, (
        f"line items ({build_sum}) must reconcile to recommended ({recommended_amount})"
    )

    down_payment = params["down_payment"]
    change_budget = params["change_budget"]
    remediation_rate = params["remediation_rate"]
    core_weeks = timeline["recommended_weeks"]
    weeks = timeline["weeks"]

    schedule = _build_schedule(
        recommended_amount=recommended_amount,
        weekly_rate=weekly_rate,
        down_payment=down_payment,
        core_weeks=core_weeks,
        weeks=weeks,
    )
    assert schedule[-1]["running_total"] == recommended_amount, (
        f"schedule running total ({schedule[-1]['running_total']}) must reach "
        f"recommended ({recommended_amount})"
    )

    return {
        "currency": "USD",
        "hourly_rate": hourly_rate,
        "weekly_hours": weekly_hours,
        "weekly_rate": weekly_rate,
        "headline": {
            "label": params.get("headline_label", "Full build"),
            "amount": headline_amount,
            "weeks": headline_weeks,
            "weekly_hours": weekly_hours,
            "hourly_rate": hourly_rate,
            "note": (
                f"{weekly_hours} hrs/week @ {fmt_money(hourly_rate)}/hr over "
                f"{headline_weeks} weeks. AI/agent costs included."
            ),
        },
        "recommended": {
            "label": "Recommended initial build",
            "amount": recommended_amount,
            "core_weeks": core_weeks,
            "range_weeks": timeline["range_label"],
            "total_hours": total_hours,
            "note": (
                f"Lean {core_weeks}-week core ({total_hours} hrs), flexible across a "
                f"{timeline['range_label']} range as scope evolves."
            ),
        },
        "line_items": line_items,
        "down_payment": {
            "amount": down_payment,
            "covers": f"First {max(1, round(down_payment / weekly_rate))} weeks of work",
        },
        "remediation_rate": {
            "amount": remediation_rate,
            "unit": "hour",
            "note": "Post-build changes and fixes billed hourly, only as used.",
        },
        "change_budget": {
            "amount": change_budget,
            "note": "Reserve for product evolution after the initial build ships.",
        },
        "schedule": schedule,
    }


def _build_schedule(*, recommended_amount, weekly_rate, down_payment, core_weeks, weeks):
    """Down payment covering the first weeks, then flat weekly billing with a final
    true-up so the running total lands exactly on the recommended amount."""
    dp_weeks = max(1, round(down_payment / weekly_rate))
    dp_weeks = min(dp_weeks, core_weeks)
    rem_weeks = core_weeks - dp_weeks

    def focus_of(week_idx_zero_based):
        if 0 <= week_idx_zero_based < len(weeks):
            return weeks[week_idx_zero_based]["focus"]
        return "Delivery"

    schedule = []
    running = 0

    # Down payment row.
    covered = " + ".join(focus_of(i) for i in range(dp_weeks))
    dp_amount = down_payment if rem_weeks > 0 else recommended_amount
    running += dp_amount
    schedule.append({
        "week": f"Wk 1–{dp_weeks}" if dp_weeks > 1 else "Wk 1",
        "milestone": f"Kickoff · {covered}",
        "amount": dp_amount,
        "kind": "down_payment",
        "running_total": running,
    })

    # Weekly rows.
    for j in range(rem_weeks):
        idx = dp_weeks + j
        is_last = j == rem_weeks - 1
        amount = (recommended_amount - running) if is_last else weekly_rate
        running += amount
        schedule.append({
            "week": f"Wk {idx + 1}",
            "milestone": focus_of(idx),
            "amount": amount,
            "kind": "weekly",
            "running_total": running,
        })

    return schedule
