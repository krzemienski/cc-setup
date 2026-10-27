# Data contract — `proposal_data.json`

Every renderer (webpage, PDF, slides) consumes **this single object** so the three deliverables
are guaranteed to agree on tasks, estimates, timeline, and costs. The engines write it; the
renderers only read it. Never compute a number inside a renderer — if it isn't in `proposal_data.json`, it doesn't render.

```jsonc
{
  "client":   { "name": "Get Path", "initial": "G" },
  "provider": { "name": "WithAgents", "wordmark": "withagents",
                "positioning": "build with agents",
                "tagline": "Timely delivery, pay-as-you-go weekly rates." },
  "meta": {
    "title": "Project Proposal",
    "subtitle": "AI product build",
    "generated_date": "2026-06-17",   // run date
    "proposal_id": "WA-GETPATH-20260617",
    "valid_until": "2026-07-17"        // generated_date + 30d
  },

  "overview": {
    "summary": "1–2 sentence framing of the engagement.",
    "goals": [ { "title": "Ship a working v1", "detail": "..." } ]   // 3–5
  },

  "scope": {
    "deliverables": [
      { "id": "D1", "name": "...", "description": "...",
        "tasks": [ { "name": "...", "hours": 12, "phase": "Foundation" } ] }
    ],
    "assumptions":  [ "..." ],
    "constraints":  [ "..." ],
    "out_of_scope": [ "..." ]
  },

  // ---- computed by cost_engine ----
  "estimations": {
    "total_hours": 100,
    "by_deliverable": [ { "id": "D1", "name": "...", "hours": 28, "pct": 28.0 } ],
    "by_phase":       [ { "phase": "Foundation", "hours": 24, "pct": 24.0 } ]
  },

  // ---- computed by timeline_engine ----
  "timeline": {
    "start_date": "2026-06-22",          // resolved "next Monday"
    "start_label": "Monday, June 22, 2026",
    "recommended_weeks": 5,
    "range": { "min_weeks": 5, "max_weeks": 10 },
    "weeks": [
      { "n": 1, "label": "Week 1", "focus": "Foundation",
        "deliverable_ids": ["D1"], "start": "2026-06-22", "end": "2026-06-26",
        "hours": 20 }
    ]
  },

  // ---- computed by cost_engine ----
  "costs": {
    "currency": "USD",
    "hourly_rate": 100,
    "weekly_hours": 20,
    "weekly_rate": 2000,                  // hourly_rate * weekly_hours
    "headline": {                         // the framing anchor
      "label": "Full build",
      "amount": 15000, "weeks": 8, "weekly_hours": 20, "hourly_rate": 100,
      "note": "20 hrs/week @ $100/hr over 8 weeks. AI/agent costs included." },
    "recommended": {                      // what we actually advise
      "label": "Recommended initial build",
      "amount": 10000, "core_weeks": 5, "range_weeks": "5–10",
      "note": "Lean 5-week core, flexible to 10 weeks as scope evolves." },
    "line_items": [                       // sums to recommended.amount
      { "label": "...", "detail": "...", "amount": 4000, "kind": "build" }
    ],
    "down_payment":     { "amount": 4000, "covers": "First two weeks of work" },
    "remediation_rate": { "amount": 100, "unit": "hour",
                          "note": "Post-build changes billed hourly." },
    "change_budget":    { "amount": 5000, "note": "Reserve for product evolution after the initial build." },
    "schedule": [                         // pay-as-you-go cadence; running_total reconciles to recommended
      { "week": "Wk 1–2", "milestone": "Kickoff + foundation", "amount": 4000,
        "kind": "down_payment", "running_total": 4000 },
      { "week": "Wk 3", "milestone": "...", "amount": 2000, "kind": "weekly", "running_total": 6000 }
    ]
  },

  "terms": [ { "title": "Down payment", "body": "..." } ]   // down payment, weekly billing, remediation, change budget
}
```

## Field rules
- **`kind` enums** — line_items: `build` | `included`; schedule: `down_payment` | `weekly` | `reserve`.
  Renderers color by kind (build→crimson, included→green, reserve→amber).
- **Reconciliation** — `sum(line_items.amount) == costs.recommended.amount`; the weekly `schedule` running_total reaches `recommended.amount` by the last core week. The engine asserts both; a mismatch is a hard error, not a rounding nudge.
- **Headline vs recommended** — both are always shown. Headline ($15k/8wk) is the anchor; recommended ($10k/5-wk core) is the advised path. The cost section presents them side by side so the client sees the value, then the leaner ask.
- **Parameterization** — every value above derives from params + scope. No client name, dollar figure, or date is hardcoded in any engine or renderer. The Get Path numbers are the *defaults*, not constants.
