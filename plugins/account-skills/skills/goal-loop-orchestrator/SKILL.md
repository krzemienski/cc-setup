---
name: goal-loop-orchestrator
description: Run a Claude Code /goal to completion with proper execution orchestration. Use whenever the user wants to "run a goal", "execute this /goal", "kick off the goal loop", "let it run until it's done", or has a goal condition (from goal-condition-architect or written by hand) that now needs to actually execute autonomously. Covers preconditions (trust dialog, hooks policy), pairing with auto mode for unattended turns, the evidence-surfacing discipline the Haiku evaluator depends on, turn and token budgeting, live status monitoring via /goal, stall detection and recovery, and headless execution with claude -p. Enforces the Iron Rule of real-system proof in the transcript, never mocks, stubs, or skipped checks.
---

# Goal Loop Orchestrator

You have a `/goal` condition. This skill runs it well: set it up so each turn is unattended, every turn lands real proof in the transcript, the loop is bounded and monitored, and a stall gets diagnosed instead of silently burning turns.

If there is no condition yet, get one from **goal-condition-architect** first — orchestrating an unprovable condition just loops to the bound.

## Why orchestration matters

`/goal` re-checks your condition after every turn using a small fast model (Haiku) that **reads only the transcript and runs no tools.** So the loop's reliability is decided by two things this skill controls:

1. **Whether each turn can run unattended** (auto mode) — otherwise the loop stalls on tool-approval prompts.
2. **Whether each turn surfaces the evidence the evaluator needs** — otherwise a finished-in-reality task never gets confirmed and the loop wastes turns.

Get those right and the goal terminates correctly. Get them wrong and you get either a runaway loop or a premature stop.

## Preconditions — check before setting the goal

1. **Trust accepted.** `/goal` runs only in workspaces where the trust dialog has been accepted, because the evaluator is part of the hooks system. If `/goal` reports unavailable, this or item 2 is why.
2. **Hooks not disabled.** If `disableAllHooks` is set in managed policy settings, `/goal` is unavailable. The command tells you the reason rather than failing silently — read it.
3. **Auto mode decision.** A goal turn runs unattended only if tool calls are auto-approved. Confirm with the user that running under auto mode is acceptable for this workspace before a long unattended run, since the loop will execute commands without per-tool prompts. Auto mode removes per-tool prompts; `/goal` removes per-turn prompts — together they make the run hands-off.
4. **Clean starting state.** One goal per session; setting a new one replaces any active goal. If a goal is already active (`◎ /goal active` shown, or `/goal` status reports one), decide explicitly whether to replace or `/goal clear` first.

## Setup workflow

1. **Confirm the condition is transcript-provable.** Scan it for "show / print / display" clauses. If a success criterion has no surfacing step, fix the condition before running — see references/evidence-surfacing.md. This is the single highest-leverage check.

2. **Confirm a bound exists.** The condition should end with `or stop after N turns` (or a time clause). If not, add one matched to the work size. An unbounded goal under auto mode can run away.

3. **Choose the execution mode** — interactive, headless `-p`, or remote. See references/execution-modes.md. Default to interactive for first runs of a new condition (you can watch the evaluator's reasons), headless for trusted, well-shaped conditions.

4. **Set the goal.** Setting it starts a turn immediately with the condition as the directive — no separate prompt. From then on the `◎ /goal active` indicator shows elapsed time.

5. **Monitor.** Use `/goal` (no argument) to see the condition, elapsed time, turns evaluated, token spend, and the evaluator's most recent reason. The reason is the signal — it tells you what Claude is working toward next and whether the loop is converging.

## The evidence-surfacing discipline (the core of the Iron Rule here)

The evaluator confirms only what it can read. So every turn that claims progress must **print the real proof**, not describe it:

- Ran tests? Show the summary line, not "tests are passing."
- Built? Show the exit status, not "the build works."
- Met a size budget? Show the `wc -l` output, not "files are small enough."
- Drained a queue? Show the empty `list` output, not "the backlog is clear."

This is the same standard as functional-validation, gate-validation-discipline, and no-mocking-validation-gates: real-system execution, surfaced. Never let a turn satisfy the goal with mocked data, a stubbed return, a skipped test, or a deleted check — that is the evaluator being fooled, and it is exactly what the condition's constraints exist to prevent. If you notice the loop trying to cheat toward the end state, that is a stall to diagnose, not progress. Details and per-platform examples: references/evidence-surfacing.md.

## Monitoring, stalls, and recovery

A goal is converging when the evaluator's reason changes turn over turn and points at shrinking remaining work. It is **stalled** when the reason repeats unchanged, the same error recurs, or turns climb toward the bound with no movement. On a stall, don't wait for the bound — read references/stall-recovery.md and act: inspect the latest reason, decide whether the blocker is the work, the condition, or the environment, and either `/goal clear` and fix the root cause or replace the condition with a corrected one.

When the goal is achieved, it clears automatically and records an "achieved" entry; `/goal` status then shows the achieved condition with duration, turns, and spend. Capture that as the run's evidence of completion.

## Reference files

- **references/evidence-surfacing.md** — Exactly what to print so the evaluator can confirm each criterion, by platform (tests, builds, CLI, iOS simulator, web, API, data). Read when setting up any goal that claims a checkable result.
- **references/execution-modes.md** — Interactive vs headless `-p` vs Remote Control, auto mode pairing, resume behavior (`--resume` / `--continue`), and when to use each. Read when choosing how to launch the loop.
- **references/stall-recovery.md** — Detecting a stalled loop and the decision tree for fixing it (work blocker vs bad condition vs environment), plus clearing and resuming. Read the moment a loop stops converging.
