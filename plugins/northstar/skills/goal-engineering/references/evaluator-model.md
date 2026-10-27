# The Evaluator Model

How the `/goal` evaluator works, what it can and cannot do, and how to write
conditions it judges correctly. Read this when a condition needs to hold up
across many turns or when a goal has misbehaved.

## Architecture

`/goal` is a wrapper around a **session-scoped prompt-based Stop hook**. The
mechanics:

1. Claude finishes a turn.
2. The Stop hook fires. It sends the **condition text** plus the **conversation
   so far** to the session's configured small fast model (Haiku by default).
3. That model returns a **yes/no decision and a short reason**.
4. "No" → Claude starts another turn; the reason is injected as guidance for
   that turn. "Yes" → the goal clears and an achieved entry is recorded.

The evaluator is a *separate* model from the one doing the work. This separation
is the point: the worker is not allowed to declare itself finished. A fresh
reader decides.

## What the evaluator can and cannot do

**Cannot:** run commands, read files, call tools, browse, or inspect the
repository. It has no access to anything outside the conversation text.

**Can:** read every message in the transcript and reason about whether the
condition is satisfied by what is written there.

This single fact governs every condition you write: **if the proof is not in the
transcript as text, the evaluator cannot see it.** A test can be passing on disk
and the evaluator will still say "no" if Claude never pasted the result.

## The "surface the evidence" principle

A condition implicitly places two demands on Claude:

1. Do the work.
2. **Surface the evidence** — echo the proof into the conversation.

Demand 2 is the one writers forget. A good condition states the check *and*
requires the output. Compare:

- Weak: "`npm test` passes." Claude may run it and say "tests pass" — the
  evaluator only has Claude's word.
- Strong: "`npm test` exits 0 and Claude has pasted the final summary line of
  the run." Now the evidence is forced into the transcript.

Phrases that force evidence: "Claude has pasted…", "the output shows…", "the
transcript contains the line…", "Claude has quoted…".

## Evaluator failure modes and fixes

### 1. Premature yes — the goal clears too early

Cause: the condition is loose enough that a partial or superficial result reads
as satisfied. Example: "the feature is implemented" — a stub satisfies the
words.

Fix: replace adjectives with counts and commands. Demand the *strongest* cheap
proof. Add an explicit completeness clause: "all N items", "every call site",
"no remaining occurrences of X".

### 2. Never yes — the goal loops forever

Two sub-causes:

- **Unreachable bar.** The condition asks for something Claude's tools cannot
  produce (an external deploy, a human approval, a network resource that does
  not exist). Fix: scope the condition to what Claude can do in the workspace,
  or hand the unreachable part back to the user.
- **Proof never surfaces.** The work is done but the condition demands wording
  Claude is not producing. Fix: align the condition's phrasing with the exact
  output Claude naturally generates, or add the bound clause so the loop ends.

### 3. Oscillation — yes one turn, no the next

Cause: the condition is ambiguous and the evaluator interprets it differently as
the transcript grows. Fix: make the condition a single unambiguous sentence with
one end state. Remove "and/or", soft words ("mostly", "should"), and competing
finish lines.

### 4. Evidence decay — proof scrolls out of view

On very long goals, context compaction or sheer length can push early evidence
far back. The evaluator reads what it is given. Fix: for long-running goals,
require Claude to **re-surface a status block each turn** — "at the end of every
turn, print a STATUS block listing each criterion and its current pass/fail with
the proving command output". This keeps fresh evidence near the end of the
transcript every turn.

## Writing checks the evaluator reads cleanly

Prefer checks whose output is short, deterministic, and unambiguous:

- **Exit codes** — "`<cmd>` exits 0". Pair with the summary line.
- **Empty / non-empty** — "`git status --porcelain` prints nothing",
  "`grep -rn TODO src/` returns no matches".
- **Counts** — "`<cmd> | wc -l` shows 0", "the file is 400 lines or fewer".
- **Diffs** — "`git diff --stat` shows only files under `src/auth/`".

Avoid checks that produce long or noisy output the evaluator must wade through;
ask Claude to reduce them to a single proving line.

## The bound clause

A bound is part of the condition, not separate machinery. Write it as an
alternative finish line: "…**or** stop after 25 turns and report the blocker".
The evaluator judges the bound from the transcript like any other clause — so
require Claude to report turn count or elapsed time each turn ("each turn, state
the current turn number against the 25-turn budget"). When the budget is
reached, Claude states it, the evaluator sees it, and the goal clears with a
clear reason instead of running unbounded.

## Quick reference

| Symptom                          | Likely cause            | Fix                                        |
|----------------------------------|-------------------------|--------------------------------------------|
| Cleared but work not done        | Premature yes           | Counts + commands + completeness clause    |
| Runs forever, work looks done    | Proof never surfaces    | Force evidence wording; align phrasing     |
| Runs forever, work cannot finish | Unreachable bar         | Rescope to workspace-doable; hand off rest |
| Yes/no flip-flop                 | Ambiguous condition     | One sentence, one end state, no soft words |
| Long goal stalls near the end    | Evidence decay          | Require a per-turn STATUS block            |
