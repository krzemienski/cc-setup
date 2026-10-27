---
description: Execute a /goal condition via hand-off, headless, or self-orchestrated mode
argument-hint: "[handoff|headless|self] [condition or input]"
---

# Goal Run

Execute a Claude Code `/goal` to completion. `$ARGUMENTS` may contain an optional
leading mode keyword followed by an optional condition or input.

## What this command does

1. **Resolves the condition** — uses a condition already in the conversation, or
   crafts one from the input given.
2. **Selects an execution mode** — hand-off, headless, or self-orchestrate.
3. **Runs the goal** in that mode and reports the outcome.

## Usage

```
/goal-run                          # run the condition already crafted above
/goal-run handoff                  # run that condition in hand-off mode
/goal-run self make the build green # craft from input, then self-orchestrate
/goal-run headless docs/spec.md    # craft from a file, then run headless
```

## Implementation steps

When this command is invoked:

### 1. Parse `$ARGUMENTS`

- If `$ARGUMENTS` begins with `handoff`, `headless`, or `self` (case-insensitive),
  treat that word as the **mode** and the remainder as the **input**.
- Otherwise there is no explicit mode; the whole of `$ARGUMENTS` is the input.
- The input may be empty, a loose prompt, or a file path.

### 2. Resolve the condition

- If the input is non-empty, run the crafting workflow from the `goal-craft`
  command (engage the **goal-engineering** skill, and **condition-library** if a
  template fits) to produce a self-reviewed `/goal` condition.
- If the input is empty, look for a `/goal` condition already crafted earlier in
  this conversation and use that one.
- If the input is empty and no prior condition exists, stop and tell the user to
  run `/goal-craft <work>` first, or to pass the work as input here.

Confirm the resolved condition carries one end state, an evidence-forcing check,
constraints, and a turn or time bound. If it does not, re-craft it before
running — never run an unbounded or unprovable condition.

### 3. Select the execution mode

If a mode was parsed in step 1, use it. Otherwise engage the
**goal-orchestration** skill and apply its mode-selection guide:

- **handoff** (default) — native `/goal` available and the user is interactive.
- **headless** — should run unattended or scripted, and the `claude` CLI is
  available.
- **self** — native `/goal` is unavailable (hooks disabled, untrusted
  workspace), or the user wants the loop visible in this conversation.

State which mode was chosen and why before executing.

### 4. Execute the chosen mode

Follow the full procedure in the goal-orchestration skill's
`references/execution-modes.md`.

**Hand-off:** present the `/goal` line on its own line, ready to paste, plus the
run plan — enable auto mode for tool-heavy goals; check progress with `/goal`
(no argument); stop early with `/goal clear`. The user pastes the line to start
the native loop.

**Headless:** verify the `claude` CLI exists with `command -v claude`. If
missing, fall back to self mode and say so. Otherwise run, from the project
directory, a bounded subprocess and capture its log:

```bash
cd <project-dir>
timeout 2h claude -p "/goal <condition>" 2>&1 | tee goal-run.log
```

On completion, read the tail of `goal-run.log` and report the outcome.

**Self-orchestrate:** run the loop algorithm from `references/execution-modes.md`
inside this conversation. Each iteration: do one focused unit of work, surface
the proving output, print a STATUS block, then run the **separate-judge** check
— launch a subagent with the Task tool, give it only the condition and that
iteration's evidence, and have it return met/not-met with a reason. Continue
until the judge says met or the hard iteration maximum is reached. Never let the
worker grade its own completion.

### 5. Report the outcome

State whether the goal was met or the bound was reached. Include the final
evidence (passing output, counts, the achieved condition) or, if bounded out,
the specific blocker. If the run stalled, point the user to `/goal-status` and
the recovery guidance.

## Important notes

- **Every run is bounded.** If the condition has no turn or time clause, re-craft
  it before running.
- **Hand-off needs auto mode** for tool-heavy goals, or the native loop stalls
  on the first tool confirmation.
- **Headless runs in a separate process** — its transcript is not this
  conversation; always `tee` to a log.
- **Self-orchestrate must use the subagent judge.** Skipping it removes the
  guarantee that makes a goal a goal.

## Error handling

If any step fails:

- Report the specific failure (no condition found, `claude` CLI missing, a
  blocker Claude cannot clear).
- For a missing CLI in headless mode, fall back to self mode automatically and
  note the fallback.
- For a genuine blocker, stop and surface it to the user — do not loop against
  an immovable obstacle.
