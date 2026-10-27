---
name: condition-library
description: >
  This skill should be used when a /goal condition matches a common, recurring
  shape and a proven template would be faster than writing one from scratch. Use
  when the user mentions a "goal template", "condition pattern", "reusable goal",
  or describes standard work like making tests pass, getting a green build,
  refactoring to a size budget, draining a backlog, hitting a coverage or
  performance number, upgrading dependencies, or clearing lint warnings. Supplies
  the templates that goal-engineering fills in and goal-orchestration runs.
version: 0.1.0
---

# Condition Library

A library of proven, parameterized `/goal` condition templates for recurring
kinds of work. Each template is pre-engineered to the goal-engineering recipe —
end state, evidence-forcing check, constraints, and a bound — so the only work
left is filling the placeholders.

## How to use this skill

1. **Match the request to a template** using the index below.
2. **Load `references/templates.md`** and copy the matching template.
3. **Fill every `{{placeholder}}`** with project-specific values. Leave none
   unfilled — an unfilled placeholder is a broken condition.
4. **Run the goal-engineering self-review rubric** on the filled result. The
   template removes the structural work, not the judgment; verify it is
   transcript-provable, single-end-state, and correctly bounded for this task.
5. **Hand to goal-orchestration** to choose an execution mode and run it.

If no template matches cleanly, do not force one — write the condition from
scratch with the goal-engineering skill. Templates are accelerators, not a
required path.

## Template index

`references/templates.md` contains the full text of each. The index:

| # | Template            | Use it for                                              |
|---|---------------------|---------------------------------------------------------|
| 1 | `tests-pass`        | Making a test suite or a subset of tests pass           |
| 2 | `build-green`       | Getting a build or compile step to exit clean           |
| 3 | `refactor-budget`   | Restructuring to a size/count budget, behavior locked   |
| 4 | `migration`         | Moving every call site from an old API to a new one     |
| 5 | `backlog-drain`     | Working a queue of issues/tasks until it is empty       |
| 6 | `spec-implement`    | Implementing every acceptance criterion in a doc        |
| 7 | `coverage-target`   | Raising test coverage to a threshold                    |
| 8 | `performance-target`| Hitting a latency, throughput, or size number           |
| 9 | `dependency-upgrade`| Upgrading a dependency with build and tests still green |
| 10| `lint-clean`        | Driving lint/type warnings to zero, honestly            |

## Placeholder conventions

Every template uses `{{double-brace}}` placeholders. Common ones:

- `{{test_command}}` — the exact command, e.g. `npm test`, `pytest tests/`.
- `{{scope_path}}` — the directory or file the work is confined to.
- `{{turn_budget}}` — the bound; size it to the task (small 10–15, medium 20–40,
  large 50+).
- `{{constraint}}` — what must not break; templates ship with sensible defaults,
  but tighten them per task.

## What every template guarantees

Each template is built so the filled condition will:

- Force evidence — it requires Claude to **paste** the proving output, not just
  claim success.
- Carry exactly one end state.
- Include at least one default constraint (commonly "no test is weakened,
  skipped, or deleted").
- End with a turn-budget bound and a report-on-bound clause.

These guarantees only survive if every placeholder is filled correctly. After
filling, re-read the condition once as if you were the evaluator — Haiku, no
tools, transcript only — and confirm you could answer "yes" from the text alone.

## Reference

- `references/templates.md` — the complete, copy-ready text of all ten
  templates, each with a filled example.
