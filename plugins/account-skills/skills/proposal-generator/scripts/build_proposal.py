#!/usr/bin/env python3
"""Orchestrator for the proposal-generator skill.

Reads params + a scope JSON, runs the estimation / timeline / cost engines, and
emits a single proposal_data.json (the contract every renderer consumes). Then,
based on the `outputs` param, renders the webpage / PDF / slides so all three
deliverables share identical numbers.

Usage:
  python build_proposal.py --scope examples/get-path/scope.json --out-dir examples/get-path/outputs
  python build_proposal.py --scope my/scope.json --client-name "Acme" --headline-amount 24000 \
         --hourly-rate 120 --outputs webpage,pdf

All financial / schedule values default to the WithAgents "Get Path" reference
instance, but every one is a parameter -- pass flags (or --params file.json) to
change them. Nothing is hardcoded downstream.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import fmt_money, parse_date, slugify  # noqa: E402
from cost_engine import compute_costs, compute_estimations  # noqa: E402
from timeline_engine import build_timeline  # noqa: E402

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(SKILL_ROOT, "assets")

DEFAULTS = {
    "client_name": "Get Path",
    "title": "Project Proposal",
    "hourly_rate": 100,
    "weekly_hours": 20,
    "headline_amount": 15000,
    "headline_weeks": 8,
    "headline_label": "Full build",
    "down_payment": 4000,
    "remediation_rate": 100,
    "change_budget": 5000,
    "duration_weeks": "5-10",
    "start_date": "next-monday",
    "outputs": ["webpage", "pdf", "slides"],
}


def build_data(scope: dict, params: dict, run_date: _dt.date) -> dict:
    estimations = compute_estimations(scope)
    timeline = build_timeline(scope, params, run_date)
    costs = compute_costs(scope, params, estimations, timeline)

    client = params["client_name"]
    valid_until = run_date + _dt.timedelta(days=30)
    proposal_id = "WA-{}-{}".format(
        slugify(client).replace("-", "").upper(), run_date.strftime("%Y%m%d")
    )

    product_name = scope.get("product_name", client)
    thing = product_name if product_name and product_name != client else "their product"
    overview_summary = (
        f"{client} partners with WithAgents to design and build {thing}, delivered with agents — "
        "a working product shipped fast on transparent, pay-as-you-go weekly terms."
    )

    terms = [
        {
            "title": "Down payment",
            "body": (
                f"A {fmt_money(costs['down_payment']['amount'])} down payment kicks off the engagement and "
                f"covers the {costs['down_payment']['covers'].lower()}."
            ),
        },
        {
            "title": "Weekly billing",
            "body": (
                f"After the down payment, work is billed at {fmt_money(costs['weekly_rate'])}/week "
                f"({costs['weekly_hours']} hrs @ {fmt_money(costs['hourly_rate'])}/hr) as it progresses — "
                "pay-as-you-go, pause or adjust between weeks."
            ),
        },
        {
            "title": "Remediation",
            "body": (
                f"Post-build changes and fixes are billed at {fmt_money(costs['remediation_rate']['amount'])}/hour, "
                "only as used — no retainer."
            ),
        },
        {
            "title": "Change budget",
            "body": (
                f"A {fmt_money(costs['change_budget']['amount'])} reserve is set aside for product evolution "
                "after the initial build ships, drawn down only against agreed work."
            ),
        },
    ]

    return {
        "client": {"name": client, "initial": (client.strip()[:1] or "•").upper()},
        "provider": {
            "name": "WithAgents",
            "wordmark": "withagents",
            "positioning": "build with agents",
            "tagline": "Timely delivery, pay-as-you-go weekly rates.",
        },
        "meta": {
            "title": params["title"],
            "subtitle": f"{scope.get('product_name', client)} — initial build",
            "generated_date": run_date.isoformat(),
            "generated_label": run_date.strftime("%B ") + str(run_date.day) + run_date.strftime(", %Y"),
            "proposal_id": proposal_id,
            "valid_until": valid_until.isoformat(),
            "valid_until_label": valid_until.strftime("%B ") + str(valid_until.day) + valid_until.strftime(", %Y"),
        },
        "overview": {
            "summary": overview_summary,
            "product_summary": scope.get("product_summary", ""),
            "goals": scope.get("goals", []),
        },
        "scope": {
            "deliverables": scope["deliverables"],
            "assumptions": scope.get("assumptions", []),
            "constraints": scope.get("constraints", []),
            "out_of_scope": scope.get("out_of_scope", []),
        },
        "estimations": estimations,
        "timeline": timeline,
        "costs": costs,
        "terms": terms,
    }


def _apply_renderers(data: dict, out_dir: str, which: list[str]) -> dict:
    results = {}
    if "webpage" in which:
        import render_webpage
        results["webpage"] = render_webpage.render(data, out_dir, ASSETS_DIR)
    if "slides" in which:
        import render_slides
        results["slides"] = render_slides.render(data, out_dir, ASSETS_DIR)
    if "pdf" in which:
        import render_pdf
        results["pdf"] = render_pdf.render(data, out_dir, ASSETS_DIR)
    return results


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a WithAgents-branded proposal.")
    p.add_argument("--scope", required=True, help="Path to scope JSON.")
    p.add_argument("--out-dir", required=True, help="Directory for proposal_data.json + deliverables.")
    p.add_argument("--params", help="Optional JSON file of param overrides.")
    p.add_argument("--client-name")
    p.add_argument("--title")
    p.add_argument("--hourly-rate", type=int)
    p.add_argument("--weekly-hours", type=int)
    p.add_argument("--headline-amount", type=int)
    p.add_argument("--headline-weeks", type=int)
    p.add_argument("--down-payment", type=int)
    p.add_argument("--remediation-rate", type=int)
    p.add_argument("--change-budget", type=int)
    p.add_argument("--duration-weeks")
    p.add_argument("--start-date", help="ISO date, or 'next-monday' (default).")
    p.add_argument("--outputs", help="Comma list of: webpage,pdf,slides")
    p.add_argument("--run-date", help="ISO date to treat as 'today' (default: actual today).")
    p.add_argument("--data-only", action="store_true", help="Only emit proposal_data.json.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    params = dict(DEFAULTS)
    if args.params:
        with open(args.params) as fh:
            params.update(json.load(fh))
    # CLI flags override file + defaults.
    flag_map = {
        "client_name": args.client_name, "title": args.title, "hourly_rate": args.hourly_rate,
        "weekly_hours": args.weekly_hours, "headline_amount": args.headline_amount,
        "headline_weeks": args.headline_weeks, "down_payment": args.down_payment,
        "remediation_rate": args.remediation_rate, "change_budget": args.change_budget,
        "duration_weeks": args.duration_weeks, "start_date": args.start_date,
    }
    for k, v in flag_map.items():
        if v is not None:
            params[k] = v
    if args.outputs:
        params["outputs"] = [o.strip() for o in args.outputs.split(",") if o.strip()]

    run_date = parse_date(args.run_date) if args.run_date else _dt.date.today()

    with open(args.scope) as fh:
        scope = json.load(fh)

    data = build_data(scope, params, run_date)

    os.makedirs(args.out_dir, exist_ok=True)
    data_path = os.path.join(args.out_dir, "proposal_data.json")
    with open(data_path, "w") as fh:
        json.dump(data, fh, indent=2)

    print(f"proposal_data.json -> {data_path}")
    print(f"  client={data['client']['name']!r}  id={data['meta']['proposal_id']}")
    print(f"  total_hours={data['estimations']['total_hours']}  "
          f"recommended={fmt_money(data['costs']['recommended']['amount'])}  "
          f"headline={fmt_money(data['costs']['headline']['amount'])}")
    print(f"  start={data['timeline']['start_label']}  weeks={data['timeline']['recommended_weeks']} "
          f"(range {data['timeline']['range_label']})")

    if not args.data_only:
        results = _apply_renderers(data, args.out_dir, params["outputs"])
        for kind, path in results.items():
            print(f"  {kind} -> {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
