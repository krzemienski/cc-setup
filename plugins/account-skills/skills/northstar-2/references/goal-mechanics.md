# /goal mechanics

What `/goal` is, exactly, and the facts that constrain any condition northstar writes. Source: Claude Code docs (`/goal`, skills). Keep this accurate — the whole skill depends on these constraints being true.

## The loop

- `/goal <condition>` sets a session-scoped completion condition. Setting it **starts a turn immediately** with the condition itself as the directive — no separate prompt needed.
- After **every** turn, an evaluator decides yes/no. "No" → Claude runs another turn instead of returning control, and the evaluator's short reason is passed in as guidance for the next turn. "Yes" → the goal clears and an "achieved" entry is recorded.
- One goal per session. Setting a new one replaces the active one.
- `/goal` with no argument shows status: the condition, how long it has run, turns evaluated, token spend, and the evaluator's most recent reason.
- Clear early with `/goal clear` (aliases: `stop`, `off`, `reset`, `none`, `cancel`). Starting a new conversation with `/clear` also clears it.
- A still-active goal is **restored on `--resume` / `--continue`**, but the turn count, timer, and token baseline reset. An already-achieved or cleared goal is not restored.

## The evaluator — the single most important constraint

- It is the session's configured **small fast model** (defaults to Haiku), running on whatever provider the session uses.
- It returns a yes/no decision plus a short reason.
- **It does NOT call tools. It does not run commands and does not read files.** It judges only what Claude has already surfaced in the conversation transcript.

Consequences northstar must design around:
- A condition is only verifiable if Claude's own output demonstrates it. "All tests in `test/auth` pass" works **because Claude runs them and the result lands in the transcript** — not because the evaluator runs anything.
- Anything the evaluator would have to independently check (file contents, live system state, "is the code clean") is unprovable unless a command surfaces it as text.
- The proof must be visible on the turn being judged. Require the proving command to be re-run on the final turn rather than cited from earlier, since the evaluator reasons over the conversation, not over a remembered fact.
- Ambiguous transcript text invites a false "yes". Exit codes, empty outputs, and explicit counts are unambiguous; prose like "the migration looks complete" is not.

## Hard limits

- The condition can be up to **4000 characters**.
- To bound runtime, include a turn or time clause **inside the condition** (e.g. `or stop after 20 turns`). Claude reports progress against that clause each turn and the evaluator judges it from the conversation. There is no separate timeout flag — the bound is part of the text.

## How it relates to the rest of the system

- `/goal` is implemented as a **session-scoped, prompt-based Stop hook**. The same evaluation can instead be written as a Stop hook in settings when you want it to apply to every session in scope rather than just the current one.
- **Auto mode** is orthogonal and complementary: auto mode approves tool calls within a turn (removes per-tool prompts); `/goal` decides whether to start another turn (removes per-turn prompts). Unattended runs usually want both.
- `/loop` is the sibling for *interval*-triggered repetition (next turn starts after a time interval), whereas `/goal`'s next turn starts when the previous finishes and stops when the condition is met.
- `/goal` works in non-interactive mode: `claude -p "/goal <condition>"` runs the loop to completion in one invocation; Ctrl+C interrupts. It also works through Remote Control.

## Requirements / availability

- Runs only in workspaces where the trust dialog has been accepted (the evaluator is part of the hooks system).
- Unavailable if `disableAllHooks` is set in managed policy settings. In both cases the command explains why rather than failing silently.
- Evaluator tokens bill on the small fast model and are typically negligible next to main-turn spend.
