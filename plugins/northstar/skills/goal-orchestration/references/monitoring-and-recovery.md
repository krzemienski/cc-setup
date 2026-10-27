# Monitoring and Recovery

How to read a running goal, detect a stall, and recover one. Use while a goal is
in flight or when a run has gone wrong.

## The one signal that matters: the evaluator's reason

After every turn the evaluator returns yes/no **and a short reason**. The reason
is the steering output of the whole system — it tells you what Claude is working
toward next. Everything in monitoring comes back to reading it.

Where to find it:

- **Hand-off / headless:** `/goal` with no argument shows the latest reason
  alongside condition, elapsed time, turns evaluated, and token spend.
- **Self-orchestrate:** the subagent judge's one-line reason, printed in each
  iteration's STATUS block.

## Reading the reason

| Reason pattern across turns        | Interpretation        | Action                         |
|------------------------------------|-----------------------|--------------------------------|
| Changes, names new sub-progress    | Healthy progress      | Let it run                     |
| Changes, but circles the same area | Slow / thrashing      | Watch one or two more turns    |
| Identical for 3+ turns             | Stalled               | Start the recovery playbook    |
| Names a concrete external blocker  | Hard-blocked          | Stop; surface to the user      |
| "Condition met" but work looks thin| Premature yes         | Condition flaw; re-craft       |

Healthy: "criteria 1–3 pass; criterion 4 (rate-limit test) still failing".
Next turn: "criterion 4 now passes; running full suite". The reason advances.

Stalled: "the build still fails" three turns running, with no detail changing —
Claude is not converging.

## Stall detection

A goal is stalled when **any** of these holds:

- The evaluator's reason is byte-for-byte the same for 3 or more turns.
- Turn count climbs but no criterion flips from FAIL to PASS.
- The same error text reappears in the transcript every turn.
- Token spend grows steeply with no STATUS-block movement.

Do not let a stalled goal burn its full bound. Intervene as soon as the pattern
is clear.

## The recovery playbook

Work these in order. Stop at the first that applies.

### Step 1 — Read the latest reason literally

The reason almost always names the blocker. Take it at face value before
theorizing. "cannot find module `@auth/tokens`" means exactly that.

### Step 2 — Classify the stall

Decide which of three kinds it is:

- **Condition flaw** — the wording itself is the problem.
- **Real blocker** — Claude genuinely cannot proceed.
- **Evidence decay** — the work is fine but proof is not reaching the evaluator.

### Step 3a — Recover a condition flaw

Symptoms: premature-yes (cleared with work undone), never-yes (looping with work
apparently done), or oscillation (yes/no flip-flop).

Action: **stop the goal** and return the condition to goal-engineering. Re-running
a flawed condition only burns turns. Typical fixes — tighten loose adjectives
into counts and commands; align the proof wording with the output Claude
actually produces; collapse competing end states into one. Then re-launch with
the corrected condition.

### Step 3b — Recover a real blocker

Symptoms: a missing dependency, an unreachable resource, a permission wall, or a
decision only the user can make.

Action: **stop the goal** and surface the blocker to the user with the exact
reason text and what is needed to clear it. Do not let the goal grind against an
immovable obstacle. Once the blocker is cleared, re-launch.

### Step 3c — Recover evidence decay

Symptoms: long-running goal; STATUS shows criteria passing, but the evaluator
still says no because old proof has scrolled away or been compacted.

Action: amend the condition to require a **per-turn STATUS block** that
re-surfaces each criterion with its proving command output. This keeps fresh
evidence near the end of the transcript every turn. Re-launch.

### Step 4 — Re-launch

Re-launch with the corrected condition, or after the blocker clears. Carry over
nothing from the stalled state except lessons — a fresh, correct condition runs
cleaner than a patched one.

## When to abort entirely

Abort — do not re-launch — when:

- The condition cannot be made transcript-provable with the tools available.
- The work genuinely requires a human decision the user has not delegated.
- Two recovery cycles have failed for the same reason; the task likely needs
  to be decomposed into smaller, separately-goaled pieces.

Aborting cleanly and reporting why is a good outcome. A goal that runs to its
bound with nothing to show is not.

## Orchestration anti-patterns

- **Running an unbounded goal.** Every run carries a turn or time bound. No
  exceptions.
- **Re-running a flawed condition unchanged.** If the stall is a condition flaw,
  fix the condition first — the loop cannot fix bad wording.
- **Skipping the separate judge in self-orchestrate.** Letting the worker grade
  itself defeats the entire mechanism.
- **Ignoring the reason.** The evaluator hands you the next move every turn;
  monitoring that ignores the reason is just watching a number climb.
- **Forcing `/goal` onto the wrong shape of work.** Interval re-runs want
  `/loop`; schedule-bound work wants a scheduled task. Match the tool.
- **No auto mode on a tool-heavy hand-off goal.** The loop stalls on the first
  confirmation prompt. Pair `/goal` with auto mode.
