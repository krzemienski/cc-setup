---
name: proposal-generator
description: >-
  Generate a complete, WithAgents-branded client project proposal — goals, scope,
  task-level estimates, an interactive timeline, a full cost model, and
  pay-as-you-go terms — as an interactive webpage (primary), a print-ready PDF,
  and a slide deck, all from ONE data model so the numbers always match across
  deliverables. Use this whenever the user wants to create a project proposal,
  client proposal, statement of work (SOW), project quote, cost or timeline
  estimate, engagement proposal, or pitch for a build engagement — especially
  WithAgents proposals or anything that should carry the WithAgents "Operator
  Console" branding. Trigger on phrases like "write a proposal", "proposal for a
  client", "quote this project", "draft an SOW", "scope and cost this build",
  "estimate this project", or when the user points at scope docs / PDFs and wants
  them turned into a proposal. Reads source scope documents when provided;
  otherwise works from a scope JSON or a described scope.
---

# Proposal Generator

Turns a project scope + a few commercial parameters into a polished,
WithAgents-branded proposal in three formats that always agree on the numbers:

1. **Interactive webpage** (`proposal.html`) — the primary deliverable. Expandable
   deliverables, an interactive timeline, a headline↔recommended cost toggle, and
   an effort-breakdown toggle. Self-contained single file.
2. **Print-ready PDF** (`proposal.pdf`) — ink-on-paper, generated with weasyprint.
3. **Slide deck** (`proposal-slides.html`) — a self-contained scroll-snap deck
   (no reveal.js/CDN dependency) covering goals, scope, estimates, timeline, and cost.

Everything is rendered from a single `proposal_data.json`, so the webpage, PDF, and
slides can never drift apart. The cost and timeline are computed by deterministic
engines, not written by hand.

## When to use

Use for any "turn this engagement into a client-ready proposal" request: project
proposals, SOWs, quotes, cost/timeline estimates, build pitches — particularly
WithAgents engagements. Use even when the user only describes the work verbally or
hands over scope PDFs; the first step is just to capture that scope as a JSON.

Not for: internal planning docs with no commercial terms (use a planning skill),
or generic slide decks unrelated to a proposal (use visual-explainer).

## Workflow

```
source scope (PDFs / description)  ──►  scope.json
scope.json + commercial params     ──►  build_proposal.py
                                          ├─ compute_estimations()   (cost_engine)
                                          ├─ build_timeline()        (timeline_engine)
                                          └─ compute_costs()         (cost_engine)
                                        ──►  proposal_data.json   ← single source of truth
                                          ├─ render_webpage.py  → proposal.html
                                          ├─ render_pdf.py      → proposal.pdf
                                          └─ render_slides.py   → proposal-slides.html
```

1. **Capture the scope.** If the user provides PDFs or scope docs, read them
   completely and extract deliverables → tasks (with hour estimates) → phases,
   plus assumptions, constraints, and out-of-scope items, into a `scope.json`
   (shape below; full schema in `references/data-contract.md`). If they only
   describe the work, synthesize a realistic scope JSON the same way. Keep task
   hours honest — the recommended price is `total_hours × hourly_rate`.
2. **Run the build.** Pass commercial parameters as flags (or a `--params` JSON).
3. **Deliver** the three outputs (or whichever the user asked for via `--outputs`).

### Quick start

```bash
# One command → proposal_data.json + all three deliverables
python3 scripts/build_proposal.py \
  --scope examples/get-path/scope.json \
  --out-dir examples/get-path/outputs

# Different client / budget — nothing is hardcoded
python3 scripts/build_proposal.py --scope my/scope.json --out-dir out \
  --client-name "Acme Robotics" --headline-amount 24000 --hourly-rate 125 \
  --down-payment 5000 --change-budget 8000 --outputs webpage,pdf
```

Dependencies: Python 3.10+, and `weasyprint` for the PDF
(`pip install weasyprint --break-system-packages`; its pango/cairo system libs are
usually already present). The webpage and slides need no third-party packages.

## Parameters

Defaults are the WithAgents "Get Path" reference instance; every one is overridable.

| Parameter | Flag | Default | Meaning |
|---|---|---|---|
| Client name | `--client-name` | `Get Path` | Who the proposal is for. |
| Source scope | `--scope` (required) | — | Path to the scope JSON. |
| Hourly rate | `--hourly-rate` | `100` | $/hr; drives the recommended price. |
| Weekly hours | `--weekly-hours` | `20` | Nominal hrs/week → weekly rate. |
| Headline amount | `--headline-amount` | `15000` | The flat anchor ("full build"). |
| Headline weeks | `--headline-weeks` | `8` | Framing duration for the headline. |
| Duration range | `--duration-weeks` | `5-10` | Flexible week range for the core. |
| Start date | `--start-date` | `next-monday` | ISO date, or `next-monday` (resolved from run date). |
| Down payment | `--down-payment` | `4000` | Kickoff payment; covers the first weeks. |
| Remediation rate | `--remediation-rate` | `100` | $/hr for post-build changes. |
| Change budget | `--change-budget` | `5000` | Reserve for post-build evolution. |
| Outputs | `--outputs` | `webpage,pdf,slides` | Which deliverables to render. |
| Run date | `--run-date` | today | Treat-as-today (for deterministic runs/tests). |

### scope.json shape (input)

```jsonc
{
  "product_name": "Get Path",
  "product_summary": "1–2 sentences on what it is and who it serves.",
  "phase_order": ["Foundation","Core Features","AI Integration","Polish & UX","Launch & Handoff"],
  "goals": [ { "title": "...", "detail": "..." } ],
  "deliverables": [
    { "id": "D1", "name": "...", "description": "...",
      "tasks": [ { "name": "...", "hours": 8, "phase": "Foundation" } ] }
  ],
  "assumptions": ["..."], "constraints": ["..."], "out_of_scope": ["..."]
}
```

`phase_order` is optional but recommended — it fixes the narrative order of phases
(and therefore the weekly timeline) regardless of which deliverable a phase first
appears in. One phase becomes one timeline week.

## How it fits together

- **`references/data-contract.md`** — the full `proposal_data.json` schema every
  renderer consumes. Read this before changing any engine or renderer.
- **`references/cost-timeline-model.md`** — how the headline/recommended framing,
  down payment, weekly cadence, remediation, and change budget are computed and
  why they reconcile exactly.
- **`references/scope-mapping.md`** — how scope items become proposal sections
  (deliverables → tasks → estimates → cost line items → timeline weeks).
- **`references/branding.md`** + **`assets/tokens.css` / `print.css` / `slides.css`**
  — the WithAgents Operator Console design system (warm-black, crimson `#FF3D52`,
  Inter / Fraunces / JetBrains Mono). Dark-only on screen; ink-on-paper for print.
- **`references/visual-explainer-patterns.md`** — the front-end patterns the
  interactive webpage and deck are built on.

## Validation (Iron Rule — real execution, no mocks)

The engines self-assert that line items and the weekly schedule reconcile exactly to
the recommended amount. After generating, verify on the real artifacts:

- re-read `proposal.pdf` with `pdfplumber` and assert the client name, headline,
  recommended, down payment, remediation, and change-budget figures all appear;
- grep `proposal.html` for the same figures and for the interactivity hooks
  (`setMode`, `setView`, `<details>`);
- re-run with a different `--client-name` + budget and confirm no values from the
  previous run leak through.

See `examples/get-path/` for a complete worked instance.
