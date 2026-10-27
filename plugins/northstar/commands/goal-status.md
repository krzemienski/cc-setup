---
description: Check, interpret, and recover a running or stalled /goal
argument-hint: (no arguments)
---

# Goal Status

Inspect the current `/goal`, interpret its progress, and recommend a recovery
move if it has stalled.

## What this command does

1. **Determines what is running** — a native `/goal` or a self-orchestrated loop.
2. **Reads the progress signal** — the evaluator's most recent reason.
3. **Interprets it** — healthy progress, slow, stalled, or hard-blocked.
4. **Recommends the next move** — keep running, recover, or abort.

## Usage

```
/goal-status
```

## Implementation steps

When this command is invoked:

### 1. Identify the active orchestration

Determine which kind of goal, if any, is running:

- **Native `/goal`** — a goal set with the `/goal` command in this session.
- **Self-orchestrated** — a loop started by `/goal-run self` in this
  conversation.
- **None** — no goal is active.

If none is active, say so and tell the user to start one with `/goal-craft` then
`/goal-run`.

### 2. Collect the status signal

**Native `/goal`:** instruct the user to run `/goal` with no argument, which
reports the condition, how long it has run, turns evaluated, token spend, and the
evaluator's most recent reason. Ask the user to paste that output here so it can
be interpreted.

**Self-orchestrated:** read the most recent STATUS block and subagent judge
reason from the conversation directly.

### 3. Interpret the signal

Engage the **goal-orchestration** skill and apply the reading guide from
`references/monitoring-and-recovery.md`:

- **Healthy** — the evaluator's reason changes turn to turn and names new
  sub-progress. Report that the goal is converging; recommend letting it run.
- **Slow / thrashing** — the reason changes but circles the same area. Report
  this and recommend watching one or two more turns.
- **Stalled** — the reason is unchanged for 3+ turns, or turns climb with no
  criterion flipping to pass. Move to step 4.
- **Hard-blocked** — the reason names a concrete external blocker. Move to
  step 4.
- **Premature done** — the goal cleared but the work looks thin. Report this as
  a condition flaw; recommend re-crafting with `/goal-craft` and re-running.

### 4. Recommend recovery if needed

For a stalled or hard-blocked goal, apply the recovery playbook from
`references/monitoring-and-recovery.md`. Classify the stall and recommend
accordingly:

- **Condition flaw** (premature-yes hole, never-yes trap, ambiguity) — recommend
  stopping the goal and re-crafting the condition with `/goal-craft`, then
  re-running. Name the specific flaw.
- **Real blocker** (missing dependency, unreachable resource, a decision only
  the user can make) — surface the exact blocker and what is needed to clear it.
- **Evidence decay** (long goal, work fine, proof scrolled away) — recommend
  amending the condition to require a per-turn STATUS block, then re-running.

State plainly when the right move is to abort rather than re-launch: the
condition cannot be made transcript-provable, the work needs a human decision,
or two recovery cycles have already failed for the same reason.

### 5. Report

Present a short status summary:

```
## Goal status

**State**:    <healthy | slow | stalled | hard-blocked | premature-done | none>
**Condition**: <the active condition, abbreviated>
**Latest reason**: <the evaluator's or judge's most recent reason>
**Progress**: <turns/iterations evaluated, criteria passed if known>

**Recommendation**: <keep running | recover via ... | abort because ...>
```

## Important notes

- **The evaluator's reason is the signal.** Everything in interpretation comes
  back to whether that reason is advancing.
- **Do not re-run a flawed condition unchanged.** If the stall is a condition
  flaw, the condition must be re-crafted first.
- **A clean abort is a valid outcome.** A goal that runs to its bound with
  nothing to show is not.

## Error handling

If the native `/goal` status output cannot be obtained, ask the user to paste it
rather than guessing. If no goal is active, report that plainly and stop.
