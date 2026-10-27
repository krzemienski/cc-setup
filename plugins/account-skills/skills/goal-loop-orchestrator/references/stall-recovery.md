# Stall detection and recovery

A `/goal` loop should converge: the evaluator's most recent reason (visible in `/goal` status and the transcript) should change turn over turn and point at shrinking remaining work. When it stops doing that, the loop is stalled. Catch it early — don't let it grind to the bound.

## Signs of a stall

- The evaluator's **reason repeats verbatim** across turns.
- The **same error or test failure recurs** with no new approach.
- **Turn count climbs** toward the bound with no movement in the reason.
- Token spend rises but the surfaced evidence doesn't change.
- Claude starts attempting **cheats** toward the end state (skipping a test, mocking a dependency, committing to clean the tree) — a sign the real path is blocked.

## Diagnose: which kind of stall?

Read the latest evaluator reason and the last turn's output, then classify:

**A. Work blocker** — the task is genuinely hard or has a real bug Claude keeps hitting.
- Symptom: reason names a specific failing check that won't go green; approaches vary but all fail.
- Action: `/goal clear`, then work the blocker directly (or in a normal turn) until the real obstacle is resolved. Re-set the goal once the path is clear. Don't ask the loop to brute-force a problem it can't currently solve.

**B. Bad condition** — the condition is unprovable, ambiguous, a moving target, or missing a surfacing step.
- Symptom: the work looks done in the transcript but the evaluator still says "no", or the reason shows it can't tell what "done" means.
- Action: `/goal clear` and rewrite the condition (use goal-condition-architect). The usual fixes: add the "show the output" proof step, fix a moving-target threshold to a fixed line, or split a multi-goal condition into one end state.

**C. Environment / preconditions** — tools fail, the dev server is down, auth expired, or `/goal` itself is unavailable.
- Symptom: errors are about the environment, not the task; or `/goal` reports it can't run (trust not accepted, `disableAllHooks` set).
- Action: fix the environment (start the server, restore auth, accept trust, adjust managed hook policy), then re-set the goal. A preflight pass before long runs prevents most of these.

**D. Cheating-toward-success** — the loop is about to satisfy the letter of the condition by faking the proof.
- Symptom: a mock appears, a test gets skipped/deleted, sample data replaces real data, or a stash/revert is used to clean the tree.
- Action: this is a failure, not progress. `/goal clear`, undo the cheat, and re-set with tightened constraints that forbid that specific shortcut. The condition's constraints exist precisely to block this; strengthen them.

## Recovery commands

- **Stop the loop:** `/goal clear` (aliases: `stop`, `off`, `reset`, `none`, `cancel`). `/clear` also removes the active goal.
- **Inspect before deciding:** `/goal` (no argument) for condition, elapsed time, turns evaluated, token spend, and the latest reason.
- **Replace, don't stack:** setting a new goal replaces the active one — so the fix for a bad condition is simply to clear and set the corrected version.

## After recovery

Re-run with the corrected condition or cleared blocker. If the same class of stall recurs, the problem is upstream: either the work needs to be broken into smaller goals (sequence them), or the condition needs a tighter end state. Raising the bound is almost never the right fix — a goal that needs more turns to *maybe* converge is usually underspecified, not under-budgeted.

## Completion

When the condition holds, the goal clears itself and records an "achieved" entry; `/goal` status then shows the achieved condition with its duration, turn count, and token spend. Capture that summary as the proof-of-completion for the run.
