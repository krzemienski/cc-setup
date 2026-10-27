---
name: goal-orchestration
description: >
  This skill should be used when running, executing, or supervising a Claude Code
  /goal after the condition has been written. Use when the user says "run this goal",
  "execute the goal", "which execution mode", "orchestrate this", "monitor the goal",
  "the goal is stuck", "goal vs loop", or wants the goal carried out across hand-off,
  headless, or self-orchestrated modes. Pair with goal-engineering, which writes the
  condition this skill runs.
version: 0.1.0
---

# Goal Orchestration

Run a crafted `/goal` condition to completion. This skill covers the three
execution modes, how to choose between them, how to bound and monitor a run, and
how to recover a goal that stalls.

## Prerequisite

Orchestration runs a condition that goal-engineering has already produced and
self-reviewed. If no condition exists yet, craft one first — a sloppy condition
is the most common cause of a failed run, and no execution mode can rescue it.

## The three execution modes

A plugin cannot type the native `/goal` command into a live interactive session
— `/goal` is user-initiated. So "execute" takes three real shapes. All three are
supported; pick per task.

### Mode 1 — Hand-off (default)

Produce the exact, copy-paste-ready `/goal <condition>` line plus a short
run plan, and hand it to the user to paste. This starts the **real native goal
loop** with its genuine separate-model evaluator.

- **Use when:** the user is in an interactive Claude Code or Cowork session and
  wants the authentic `/goal` behavior. This is the default — recommend it
  unless a reason points elsewhere.
- **Strengths:** real evaluator, real `◎ /goal active` indicator, native status
  and resume. Nothing to simulate.
- **Cost:** one paste of one line by the user.

### Mode 2 — Headless

Run the goal as a non-interactive subprocess: `claude -p "/goal <condition>"`.
The loop runs to completion in a single invocation.

- **Use when:** the goal should run unattended with no live session, or as part
  of a script or scheduled job.
- **Strengths:** fully hands-off; real `/goal` semantics; integrates with
  automation.
- **Cost / caveats:** requires the `claude` CLI on PATH and a workspace whose
  trust dialog has been accepted (`/goal` needs the hooks system). Runs in a
  separate process, so its transcript is not the current conversation. Always
  bound it and capture output to a log.

### Mode 3 — Self-orchestrate

Run the goal loop *inside the current session* without invoking native `/goal`:
work toward the condition, then evaluate it with a fresh checker each turn,
repeating until met or bounded.

- **Use when:** native `/goal` is unavailable (hooks disabled, untrusted
  workspace, an environment without the command) or the user wants the loop
  visible and steerable in the current conversation.
- **Strengths:** works anywhere; fully transparent; the user can interrupt.
- **Cost:** it is a faithful simulation, not the native feature — fidelity
  depends on honoring the separate-judge rule below.

**The separate-judge rule.** Native `/goal`'s core property is that the worker
never declares itself done — a different model does. Self-orchestrate must
preserve this: after each work iteration, run the evaluation as a **fresh,
worker-blind check** — ideally a subagent (Task tool) given *only* the condition
and the iteration's surfaced evidence, asked to return yes/no + reason. Never let
the same reasoning that did the work also rule it complete.

## Choosing a mode

```
Native /goal available and user is interactive?
  └─ yes → Mode 1 (Hand-off)          ← default
  └─ no  → continue
Should it run unattended / scripted, claude CLI available?
  └─ yes → Mode 2 (Headless)
  └─ no  → Mode 3 (Self-orchestrate)
```

When unsure, present Mode 1 and name Mode 3 as the fallback. Detailed
step-by-step procedures for all three modes are in
`references/execution-modes.md`.

## Bound every run

Every run has a bound — it is already in the condition as a turn or time clause.
At orchestration time, reinforce it:

- **Hand-off:** remind the user the condition self-bounds, and that `/goal clear`
  stops it early, `/goal` with no argument shows turns and tokens spent.
- **Headless:** wrap the invocation with an OS-level timeout and a turn budget
  in the condition; never launch an unbounded headless goal.
- **Self-orchestrate:** enforce a hard maximum iteration count in the loop
  itself, independent of the condition's clause, as a backstop.

A goal with no bound is a defect. Refuse to run one — send it back to
goal-engineering.

## Pair with auto mode

`/goal` removes per-turn prompts; **auto mode** removes per-tool prompts. They
are complementary and a goal usually wants both — without auto mode, an
unattended goal stalls on the first tool confirmation. When recommending a
hand-off run, tell the user to enable auto mode for the session if the goal
involves many tool calls.

## Monitor the run

While a goal runs, the signal to watch is the **evaluator's most recent reason**
— it shows in the native status view and transcript, and it is what Claude is
steering toward next.

- **Hand-off / headless:** the user checks `/goal` (no argument) for the
  condition, elapsed time, turns evaluated, token spend, and latest reason.
- **Self-orchestrate:** print a STATUS block every iteration — iteration number
  against the budget, each criterion's pass/fail with proving output, and the
  judge's latest reason.

Healthy progress: the reason changes turn to turn and moves toward the criteria.
See `references/monitoring-and-recovery.md` for reading these signals.

## Recover a stalled goal

A goal is stalled when the evaluator's reason stops changing, or repeats the same
blocker, for several turns. Do not just wait it out. Recovery steps, in order:

1. **Read the latest reason literally.** It usually names the exact blocker.
2. **Stall from a condition flaw?** If the reason shows a premature-yes hole, a
   never-yes trap, or ambiguity, stop the goal and send the condition back to
   goal-engineering to re-craft. Re-running a flawed condition wastes turns.
3. **Stall from a real blocker?** If Claude genuinely cannot proceed (missing
   dependency, unreachable resource, a decision only the user can make), stop
   and surface it to the user.
4. **Stall from evidence decay?** On long goals, add a per-turn STATUS block
   requirement so fresh proof stays near the end of the transcript.
5. **Re-launch** with the corrected condition or after the blocker clears.

Full recovery playbook: `references/monitoring-and-recovery.md`.

## `/goal` vs other autonomous workflows

`/goal` is one of several ways to keep work running. Choose by what should start
the next unit of work:

| Tool             | Next unit starts when        | Stops when                          |
|------------------|------------------------------|-------------------------------------|
| `/goal`          | the previous turn finishes   | a model confirms the condition met  |
| `/loop`          | a time interval elapses      | the user stops it, or work is done  |
| Stop hook        | the previous turn finishes   | a custom script or prompt decides   |
| Scheduled task   | a clock/cron time arrives    | the schedule is removed             |

Use `/goal` for substantial work with a single verifiable end state. Use `/loop`
for repeated re-runs on an interval. Use a Stop hook when evaluation logic must
be deterministic, custom, or shared across every session. Use a scheduled task
for work that should run independent of any open session. If the user's request
fits `/loop` or a scheduled task better than `/goal`, say so rather than forcing
a goal.

## References

- `references/execution-modes.md` — full step-by-step procedure for each of the
  three modes, including the self-orchestrate loop algorithm.
- `references/monitoring-and-recovery.md` — reading evaluator reasons, stall
  detection, the recovery playbook, and orchestration anti-patterns.
