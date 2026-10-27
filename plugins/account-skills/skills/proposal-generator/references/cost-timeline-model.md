# Cost & timeline model

How `cost_engine.py` and `timeline_engine.py` turn a scope + params into the
numbers shown in the proposal. The design goal is that every figure reconciles
exactly and derives from inputs — so a reviewer can trust the math and a different
client/budget just works.

## Two framings, always shown together

The proposal presents two prices side by side so the client sees the full value,
then the leaner ask:

- **Headline** — a flat anchor (`--headline-amount`, default `$15,000`) described as
  the "full build" (e.g. 20 hrs/week @ $100/hr over 8 weeks, AI costs included). It
  is a marketing anchor, intentionally *not* a strict `rate × hours` product, so it
  is stored as given and never asserted against an hours calculation.
- **Recommended** — the initial build we actually advise:
  `recommended_amount = total_scope_hours × hourly_rate`. For the Get Path reference
  that is `100 h × $100 = $10,000`.

## Estimations

`compute_estimations(scope)` sums task hours into `total_hours`, a per-deliverable
breakdown (with %), and a per-phase breakdown (ordered by `phase_order`). These feed
both the estimation visuals and the cost line items.

## Cost line items

One `build` line per deliverable: `deliverable_hours × hourly_rate`. Their sum is
asserted to equal `recommended_amount` (a mismatch is a hard error, never a rounding
nudge). A single zero-cost `included` line surfaces the "AI / agent runtime + tooling
included" positioning without affecting the sum.

## Pay-as-you-go schedule

The weekly cadence is the billing mechanism the proposal sells: predictable, pausable,
pay-as-you-go.

```
weekly_rate = hourly_rate × weekly_hours                  # 100 × 20 = $2,000
dp_weeks    = round(down_payment / weekly_rate)           # 4000 / 2000 = 2 weeks
```

- **Down payment** (`--down-payment`, default `$4,000`) is the first schedule row and
  covers the first `dp_weeks` weeks.
- Each remaining core week bills a flat `weekly_rate`, and the **final week trues up**
  so the running total lands *exactly* on `recommended_amount`. The engine asserts
  `schedule[-1].running_total == recommended_amount`.

Get Path schedule:

| When | Milestone | Invoice | Cumulative |
|---|---|---|---|
| Wk 1–2 | Kickoff · Foundation + Core Features | $4,000 | $4,000 |
| Wk 3 | AI Integration | $2,000 | $6,000 |
| Wk 4 | Polish & UX | $2,000 | $8,000 |
| Wk 5 | Launch & Handoff | $2,000 | $10,000 |

- **Remediation** (`--remediation-rate`, default `$100/hr`) — post-build changes,
  billed hourly, only as used. Shown as a term, kept out of the core schedule.
- **Change budget** (`--change-budget`, default `$5,000`) — a reserve for product
  evolution *after* the initial build. Also kept out of the core running total; it is
  a separate, drawn-down-as-agreed line so the recommended price stays clean.

## Timeline

`build_timeline()` maps **one phase → one week**, in `phase_order`. For a well-formed
scope the phase count equals `ceil(total_hours / weekly_hours)`, so the timeline and
the billing cadence agree. Each week carries its focus (phase), the deliverables that
have a task in that phase, the phase's hours, and Monday→Friday dates.

- **Start date** resolves `next-monday` relative to the run date (if today is Monday,
  it means the following Monday — the colloquial "next Monday"). An explicit ISO date
  is used as-is.
- **Range** comes from `--duration-weeks` (e.g. `5-10`): the lean core is the floor,
  flexible up to the ceiling as scope evolves.

## Why it generalizes

Change the client, rate, budget, down payment, or scope and everything recomputes:
recommended follows scope hours × rate, the schedule re-derives and re-trues-up, the
timeline re-maps phases to weeks. The Get Path figures are defaults in
`build_proposal.py`, not constants in the engines.
