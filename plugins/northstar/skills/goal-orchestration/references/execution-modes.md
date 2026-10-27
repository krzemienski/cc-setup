# Execution Modes

Full step-by-step procedure for each of the three execution modes. Use after
goal-engineering has produced a self-reviewed condition.

---

## Mode 1 — Hand-off

The plugin prepares everything; the user pastes one line to start the real
native `/goal` loop.

### Steps

1. **Confirm the condition is final.** It must carry an end state, a check that
   forces evidence, constraints, and a turn/time bound.

2. **Emit the paste line.** Present the `/goal` line alone, on its own line, with
   no surrounding backticks or prose inside it, so it is selectable in one
   action:

   ```
   /goal <full condition text>
   ```

3. **Emit the run plan.** Directly below it, give the user:
   - **Enable auto mode** for the session if the goal makes many tool calls,
     otherwise the loop stalls on the first tool confirmation.
   - **What to expect:** a `◎ /goal active` indicator; one turn starts
     immediately with the condition as the directive — no separate prompt
     needed.
   - **How to check in:** run `/goal` with no argument for condition, elapsed
     time, turns evaluated, token spend, and the evaluator's latest reason.
   - **How to stop early:** `/goal clear` (aliases: `stop`, `off`, `reset`,
     `none`, `cancel`). Starting a new conversation with `/clear` also clears it.
   - **Resume:** if the session ends mid-goal, `--resume` or `--continue`
     restores the active goal; the timer and turn count reset on resume.

4. **Offer a status follow-up.** Tell the user they can paste the evaluator's
   latest reason back here and ask for help if the goal stalls.

### Requirements

`/goal` runs only in a workspace whose trust dialog has been accepted, and is
unavailable if `disableAllHooks` is set in managed policy. If either blocks it,
the command itself reports why — fall back to Mode 3.

---

## Mode 2 — Headless

Run the goal as a non-interactive subprocess. Real `/goal` semantics, no live
session.

### Steps

1. **Confirm prerequisites.** The `claude` CLI is on PATH; the target workspace
   is trusted; hooks are not disabled by policy. If any fails, fall back to
   Mode 3.

2. **Bound at the OS level.** Never launch unbounded. Wrap with a timeout and
   keep the turn clause in the condition. Run from the project directory:

   ```bash
   cd /path/to/project
   timeout 2h claude -p "/goal <full condition text>" 2>&1 | tee goal-run.log
   ```

   On macOS without GNU `timeout`, use `gtimeout` (from coreutils) or rely on
   the condition's turn bound alone.

3. **Capture output.** `tee` to a log so the run is inspectable after the fact —
   the subprocess transcript is not the current conversation.

4. **Report on completion.** When the process exits, read the tail of the log:
   the achieved entry (goal met) or the bound report (turns/time exhausted).
   Summarize the outcome and the evaluator's final reason for the user.

5. **Interrupting.** A headless goal is stopped with Ctrl+C on the process, or
   by the wrapping `timeout`.

### Caveats

- The subprocess has its own context; it cannot see this conversation.
- Token spend accrues on the subprocess; there is no live indicator.
- In sandboxed environments the `claude` CLI may be absent — verify first with
  `command -v claude` and fall back to Mode 3 if missing.

---

## Mode 3 — Self-orchestrate

Run the goal loop inside the current session. A faithful simulation of `/goal`
that works anywhere. Fidelity depends on the separate-judge rule.

### The loop algorithm

```
INPUT: condition C (with criteria, checks, constraints, bound B)
iteration = 0
hard_max = B's turn count, or 30 if B is time-based

LOOP:
  iteration += 1

  1. WORK
     Do one focused unit of work toward the unmet criteria of C.
     Run the checks named in C. Surface their output verbatim into the
     conversation — paste exit codes, counts, diffs, summary lines.

  2. STATUS
     Print a STATUS block:
       - iteration N of hard_max
       - each criterion: PASS / FAIL, with the proving command output
       - constraints: each still holding? yes/no
       - elapsed time if B is time-based

  3. JUDGE  (separate-judge rule — do NOT self-assess)
     Launch a subagent (Task tool, general-purpose) with ONLY:
       - the condition C
       - this iteration's STATUS block and surfaced evidence
     Ask it to return: VERDICT = met | not-met, plus a one-line reason.
     The subagent must not see the work reasoning — only the evidence.

  4. DECIDE
     - VERDICT met            → exit LOOP, report success + evidence.
     - iteration >= hard_max  → exit LOOP, report bound reached + blocker.
     - otherwise              → carry the subagent's reason forward as the
                                directive for the next iteration; continue.
```

### Steps

1. **Parse the condition** into its criteria, checks, constraints, and bound.

2. **Set the hard maximum.** Use the condition's turn count; if the bound is
   time-based, set a backstop count (default 30) so the loop cannot run away.

3. **Run the loop** above. One unit of work per iteration — resist doing
   everything at once; the per-iteration judge is what keeps the run honest.

4. **Honor the judge.** If the subagent says not-met, do not argue — its reason
   is the next directive. If it says met, stop even if more polish seems
   possible; the condition defined "done".

5. **Report.** On exit, give the user: outcome (met / bound reached), the final
   STATUS block, and — if bound reached — the specific blocker.

### Why the subagent judge matters

The native feature's value is that the worker cannot grade its own homework.
Self-assessment quietly drifts toward "good enough". A worker-blind subagent,
handed only the condition and the evidence, reproduces the native separation and
catches premature-done. Skipping it turns self-orchestrate from a simulation of
`/goal` into just "Claude doing a task", losing the guarantee.

---

## Mode comparison

| Aspect              | Hand-off        | Headless           | Self-orchestrate      |
|---------------------|-----------------|--------------------|-----------------------|
| Real native `/goal` | yes             | yes                | simulated             |
| User action needed  | paste one line  | none after launch  | none after launch     |
| Runs in this chat   | no (their loop) | no (subprocess)    | yes, visible          |
| Works if hooks off  | no              | no                 | yes                   |
| Needs `claude` CLI  | no              | yes                | no                    |
| Evaluator           | native Haiku    | native Haiku       | subagent (Task tool)  |
| Best default for    | interactive use | unattended/scripts | restricted envs       |
