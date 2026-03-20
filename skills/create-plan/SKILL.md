---
name: create-plan
description: Create a hierarchical multi-phase project plan optimized for solo agentic development. Supports brief, roadmap, and phase-plan types. Each task is scoped for a single agent session. Saves to ./plans/YYMMDD-HHMM-slug/.
triggers:
  - "create plan"
  - "project plan"
  - "roadmap"
  - "phase plan"
  - "create a roadmap"
  - "project roadmap"
---

# Create Plan

Build a hierarchical project plan saved to disk before any implementation begins.

## Step 1: Detect Plan Type

Classify as one of:

- **brief** — 1–3 phases, under 1 week of work
- **roadmap** — 4–8 phases, multi-week, milestones and dependencies
- **phase-plan** — single phase broken into agent-session-sized tasks

If ambiguous, ask: "Brief, roadmap, or phase-plan?"

## Step 2: Gather Scope

Restate the goal in one sentence. Identify what is in scope, out of scope, and key constraints.

## Step 3: Structure Each Phase

```
Phase N: <Name>
Goal: <What this phase achieves>
Tasks:
  N.1 <Task> → output: <artifact>
  N.2 <Task> → output: <artifact>
Dependencies: Phase X must complete first
Effort: S / M / L
Validation gate: <What must be true before next phase>
```

Rules for tasks:
- Each task is completable by a single agent in one session
- Each task has a named output (file, endpoint, config, etc.)
- Each task lists its inputs (what must exist before it runs)

Always end with a Functional Validation phase:
```
Phase N: Functional Validation
Tasks:
  N.1 Build / start the real system
  N.2 Exercise through actual interface (CLI, UI, API)
  N.3 Capture evidence (screenshot, log, response)
  N.4 Confirm evidence matches success criteria
Validation gate: Evidence captured and all success criteria met
```

No unit tests. No mocks. Real system only.

## Step 4: Save the Plan

Save overview to `./plans/YYMMDD-HHMM-<slug>/plan.md`.

For roadmap and phase-plan, also save `./plans/YYMMDD-HHMM-<slug>/phase-NN-<name>.md` per phase.

## Step 5: Present and Confirm

Output the full plan, then end with:

```
Plan saved to: ./plans/YYMMDD-HHMM-<slug>/

CONFIRM to proceed, or tell me what to change.
```

Do not write code or take any implementation action until the user confirms.

## Output Format

```markdown
## Project: <Name>
**Type:** brief | roadmap | phase-plan
**Goal:** <one sentence>
**In scope:** ... | **Out of scope:** ... | **Constraints:** ...
## Success Criteria
- [ ] ...
## Phases
### Phase 1: <Name>
**Goal:** ... | **Effort:** S/M/L | **Dependencies:** none
1.1 ... → output: ...
**Validation gate:** ...
### Phase N: Functional Validation
...
## Dependency Map
Phase 2 → requires Phase 1
## Effort Summary
Total: ~X days
```
