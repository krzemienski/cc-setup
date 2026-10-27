---
name: "northstar-2"
description: Turns any input — a vague idea, a voice ramble, a PLAN.md, a pasted spec, or the current conversation — into a hardened, transcript-provable `/goal` completion condition plus the execution orchestration to run it unattended. Use whenever the user wants Claude to "keep working until X is done", mentions `/goal`, autonomous/long-running/multi-turn work, "set a goal", "loop until it passes", "run this to completion", or describes a substantial task with a verifiable end state. Use even when the user just describes the end state without saying "goal".
allowed-tools: Read, Grep, Glob, Bash
---

<objective>
Convert arbitrary input into a single `/goal` command whose completion condition the `/goal` evaluator can actually verify, then hand back the orchestration recipe to run it unattended.

The `/goal` evaluator is a small fast model that runs after every turn. It does NOT run commands or read files — **it only judges what Claude has surfaced in the transcript**. Every condition northstar writes must therefore be provable from Claude's own output. This is the whole job: most raw input describes an *intent* ("make the refactor clean"); northstar's value is rewriting it as a *transcript-verifiable end state* ("`npm test` and `npm run lint` both exit 0, with output shown each run").

This is the Iron Rule applied to autonomous loops: the proof is real-system command output in the transcript, never an assertion that the work "looks done", and never a mock.
</objective>

<when_not_to_use>
- The task finishes in one turn with no verifiable end state → no goal needed; just do it.
- The trigger is a time interval, not a condition ("check the deploy every 5 min") → that is `/loop`, not `/goal`. Say so.
- The user wants a permanent, every-session rule → that is a Stop hook in settings, not a session goal. Say so.
</when_not_to_use>

<inputs>
Input arrives via `$ARGUMENTS`, or — when invoked with no argument or the word "context" — from the current conversation. Accept any shape: a one-line intent, a rambling dictation, a file path (read it), a backlog, an acceptance-criteria list. Never ask the user to pre-structure it; that is the skill's job.
</inputs>

<process>
Work through these phases in order. Do not skip grounding — an ungrounded condition is the most common failure.

**Phase 1 — Extract the true end state.**
Read the input (read the file if a path was given). Strip the framing and find the ONE measurable thing that means "done". If the input implies several, pick the single outermost one and fold the rest into the checks or constraints. If you genuinely cannot find a verifiable end state, stop and tell the user the task isn't goal-shaped, with the reason.

**Phase 2 — Ground the checks in the real system.**
Before writing any check, find out how this project actually proves things. Inspect rather than assume:
- Detect the test/build/lint commands (`package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, CI config). Read `references/goal-mechanics.md` if you need the rules on what the evaluator can and cannot see.
- Resolve vague nouns to real paths/commands ("the auth tests" → `npm test -- test/auth`, "the queue" → the actual file or command that prints its length).
- If no real check exists for part of the end state, invent the smallest real one (a command that prints a count, a `git status`, a grep that must return empty) rather than leaving it unprovable.

**Phase 3 — Synthesize the condition.**
Assemble the four parts (see `references/condition-patterns.md` for the pattern library and anti-patterns):
1. **One measurable end state** — a single outermost signal.
2. **Stated checks** — exactly how Claude proves it, as real commands whose output lands in the transcript (e.g. "`pytest -q` exits 0", "`git status --porcelain` prints nothing").
3. **Constraints that must not change** — guardrails the loop could otherwise violate ("no file outside `src/auth/` is modified", "no test is deleted or skipped to make it pass", "no mock/stub/fixture is introduced").
4. **A bound** — always include one, e.g. "or stop after N turns" / "or stop after T minutes", so a stuck loop surfaces instead of burning tokens. Pick N from task size; default 15–25.
Keep the whole condition ≤ 4000 characters. Write it as one directive Claude can act on immediately, since setting the goal starts a turn with the condition as the prompt.

**Phase 4 — Harden against a false "yes".**
The evaluator can be fooled by ambiguous transcript text. Re-read the condition adversarially: could a turn that *didn't* actually finish produce output the evaluator would rubber-stamp? Tighten until "done" requires unambiguous proof — require the exit code or the empty output to be visible, forbid "should pass"/"appears complete" language, and require the proving command to be re-run on the final turn (not cited from an earlier turn). Apply the checklist in `references/condition-patterns.md`.

**Phase 5 — Emit using the template.**
Produce the output exactly as `templates/goal-output.md` lays out: the ready-to-run `/goal …` line in its own copyable block, the orchestration recipe (auto mode + turn budget + headless form + the Stop-hook equivalent for repeatable use), and one line on how to watch and stop it. Then run the self-check below before presenting.
</process>

<orchestration>
`/goal` removes per-turn prompts; **auto mode** removes per-tool prompts. They are complementary and an unattended loop usually wants both — always recommend auto mode alongside the goal, and flag that auto mode approves tool calls without asking.

Give the user the right runtime for their case:
- **Interactive**: paste the `/goal …` line into the session. Status: `/goal` with no args shows the condition, turns, tokens, and the evaluator's last reason. Stop early: `/goal clear`.
- **Headless / one-shot**: `claude -p "/goal <condition>"` runs the loop to completion in a single invocation; Ctrl+C interrupts.
- **Repeatable across sessions**: since `/goal` is a session-scoped prompt-based Stop hook, the same condition can live as a Stop hook in settings instead — offer this only when the user wants it every session, and note it changes settings.

Surface the cost honestly: this keeps spending main-turn tokens every turn until the condition holds or the bound trips; the bound is what protects them.
</orchestration>

<self_check>
Before presenting, verify every item. If any fails, fix it — do not ship a goal that can't be judged.
- Every check is a real command whose output appears in the transcript; nothing relies on the evaluator reading files or running anything.
- No mock, stub, fixture, or "test mode" is introduced to satisfy a check.
- A bound clause is present.
- Constraints forbid the obvious cheats (deleting/skipping tests, editing out of scope, faking output).
- The condition is ≤ 4000 chars and reads as a single actionable directive.
- The output includes the `/goal` line, the orchestration recipe, and how to watch/stop it.
</self_check>

<success_criteria>
The user can copy one `/goal` line, optionally flip on auto mode, and walk away — and the loop will either reach a genuinely-proven end state or stop at the bound with a readable reason, never declare a false victory off ambiguous text.
</success_criteria>

<references>
- `references/goal-mechanics.md` — exactly how `/goal` and its evaluator behave, and the hard limits that constrain a condition. Read when unsure what the evaluator can see or how the loop is bounded/restored.
- `references/condition-patterns.md` — provable-condition pattern library by project type, the four-part anatomy, and the anti-pattern / false-yes checklist. Read during Phases 3–4.
- `templates/goal-output.md` — the exact output structure to emit in Phase 5.
</references>
