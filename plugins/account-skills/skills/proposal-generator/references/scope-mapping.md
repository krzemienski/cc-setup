# Scope → proposal mapping

How a raw scope (PDFs, a brief, or a description) becomes the structured proposal.
This is the extraction contract to follow when reading source documents.

## The chain

```
source doc item            scope.json field           proposal section
─────────────────────────  ─────────────────────────  ──────────────────────────────
product / who it serves →  product_name / summary   → Overview hero + summary
desired outcomes        →  goals[]                  → Overview · goal cards
work packages           →  deliverables[]           → Scope · expandable deliverables
   sub-tasks            →     tasks[] (name)        →    task rows
   effort               →     tasks[].hours         → Estimations + cost line items
   sequencing           →     tasks[].phase         → Timeline weeks (via phase_order)
stated givens           →  assumptions[]            → Scope · assumptions
limits / boundaries     →  constraints[]            → Scope · constraints
explicit exclusions     →  out_of_scope[]           → Scope · out of scope
```

## Extraction rules (when reading source PDFs/docs — read completely, do not skim)

1. **Deliverables are the work packages.** Group the source's features/modules into
   5–6 coherent deliverables with stable ids (`D1…Dn`). Each gets a one–two sentence
   description.
2. **Tasks carry the hours.** Break each deliverable into 3–6 concrete tasks with an
   honest integer `hours` estimate. The sum across all tasks is the whole engagement —
   it directly sets the recommended price (`total_hours × hourly_rate`), so estimate
   realistically. For a clean weekly cadence, aim the total near
   `weekly_hours × intended_core_weeks` (e.g. 100h for a 5-week, 20h/week core).
3. **Phases drive the timeline.** Tag every task with a `phase`. Use a small, ordered
   set of phases (e.g. Foundation → Core Features → Integration → Polish → Launch) and
   declare them in `phase_order`. One phase becomes one timeline week; a deliverable
   may legitimately span phases (and therefore weeks).
4. **Assumptions / constraints / out-of-scope are the guardrails.** Capture stated
   givens, boundaries, and explicit exclusions verbatim in intent. If the source is
   silent, infer the obvious ones (single platform, no SSO, English-only, etc.) and
   mark them as assumptions — they protect the estimate.
5. **No fabrication of commercial terms.** Hours and scope come from the source; the
   commercial parameters (rate, budget, down payment, change budget) come from the
   user/params, never invented from the scope doc.

## If there is no source doc

Synthesize a realistic scope the same way (the Get Path example was produced this
way). Commit to one concrete product vision so deliverables, goals, and tasks cohere,
then keep the total hours honest against the intended core weeks.

See `examples/get-path/scope.json` for a complete, well-formed example.
