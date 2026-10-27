# How `/goal` works (ground truth)

Source: Claude Code docs, `code.claude.com/docs/en/goal.md`. This file is the authoritative behavior reference for every goal-* skill. If anything elsewhere conflicts with this, this wins; if in doubt, re-fetch the doc.

## Table of contents
1. What `/goal` does
2. The evaluator (the part everything depends on)
3. Setting a goal
4. Checking status, clearing, resuming
5. Non-interactive / headless
6. Requirements and failure modes
7. Comparison: `/goal` vs `/loop` vs Stop hook vs auto mode

## 1. What `/goal` does

`/goal <condition>` sets a **session-scoped** completion condition. Claude keeps working toward it without you prompting each step. After each turn, the condition is checked; if not met, Claude starts another turn instead of returning control to you. The goal clears automatically once met. Only **one goal can be active per session** — setting a new one replaces the old.

Good fit: substantial work with a verifiable end state — migrating call sites until everything compiles and tests pass, implementing a design doc until all acceptance criteria hold, splitting a large file until each piece is under a size budget, draining a labeled issue backlog.

## 2. The evaluator (the part everything depends on)

`/goal` is a wrapper around a session-scoped **prompt-based Stop hook**. Each time Claude finishes a turn, the condition plus the conversation so far are sent to the configured **small fast model** (defaults to Haiku). It returns a yes/no decision and a short reason.

- **No** → Claude keeps working; the reason is passed in as guidance for the next turn.
- **Yes** → the goal clears and an "achieved" entry is recorded in the transcript.

Critical properties:
- The evaluator **does not call tools.** It cannot run commands or read files. It judges **only what Claude has already surfaced in the conversation.**
- It runs on whichever provider the session is configured for.
- Evaluation tokens bill on the small fast model and are typically negligible next to main-turn spend.

Design consequence: a condition is only as good as the evidence Claude prints. "Tests pass" is judgeable when Claude runs the tests and the result lands in the transcript. "The code is correct" is not judgeable and will loop forever (until a bound).

## 3. Setting a goal

Run `/goal` followed by the condition. Setting a goal **starts a turn immediately**, with the condition itself as the directive — no separate prompt needed. While active, a `◎ /goal active` indicator shows how long it has been running. After each turn the evaluator's most recent reason appears in the status view and transcript, so you can see what Claude is working toward next.

**Writing an effective condition** (from the docs):
- One measurable end state: a test result, a build exit code, a file count, an empty queue.
- A stated check: how Claude should prove it — e.g. "`npm test` exits 0" or "`git status` is clean".
- Constraints that matter: anything that must not change on the way there — e.g. "no other test file is modified".
- To bound runtime, include a turn or time clause such as `or stop after 20 turns`. Claude reports progress against that clause each turn and the evaluator judges it from the conversation.

The condition can be up to **4,000 characters**.

## 4. Checking status, clearing, resuming

- **Status:** run `/goal` with no argument. If a goal is active it shows the condition, how long it has run, how many turns were evaluated, current token spend, and the evaluator's most recent reason. If none is active but one was achieved earlier in the session, it shows the achieved condition with its duration, turns, and spend.
- **Clear early:** `/goal clear`. Aliases accepted: `stop`, `off`, `reset`, `none`, `cancel`. Running `/clear` (new conversation) also removes an active goal.
- **Resume:** a goal still active when a session ended is restored on `--resume` / `--continue`. The condition carries over, but turn count, timer, and token-spend baseline all reset. A goal already achieved or cleared is not restored.

## 5. Non-interactive / headless

`/goal` works in non-interactive (headless) mode and through Remote Control. Setting a goal with `-p` runs the loop to completion in a single invocation:

```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

Interrupt with Ctrl+C to stop a non-interactive goal before the condition is met.

## 6. Requirements and failure modes

- `/goal` runs only in workspaces where the **trust dialog has been accepted**, because the evaluator is part of the hooks system.
- If `disableAllHooks` is set in managed policy settings, `/goal` is **unavailable**.
- In both cases the command tells you why instead of silently doing nothing — so if `/goal` reports unavailable, check trust and managed hook policy first.

## 7. Comparison: pick the right autonomous tool

All three below keep the current session running between prompts; pick by what should start the next turn.

| Approach | Next turn starts when | Stops when |
| --- | --- | --- |
| `/goal` | the previous turn finishes | a model confirms the condition is met |
| `/loop` | a time interval elapses | you stop it, or Claude decides the work is done |
| Stop hook | the previous turn finishes | your own script or prompt decides |

- `/goal` and a Stop hook both fire after every turn. `/goal` is the session-scoped shortcut (type a condition, active for this session only). A Stop hook lives in settings, applies to every session in its scope, and can run a **script** (deterministic check) or a **prompt** (model-evaluated).
- **Auto mode** approves tool calls *within* a turn but does not start a new one; Claude stops when it judges the work done. `/goal` adds a separate evaluator that checks the condition after every turn, so completion is decided by a fresh model rather than the one doing the work. They are complementary: auto mode removes per-tool prompts, `/goal` removes per-turn prompts. Running a goal under auto mode is what makes each turn unattended.
- For work that should run independent of any open session (nightly tests, morning triage), use scheduled tasks / cloud routines instead.
