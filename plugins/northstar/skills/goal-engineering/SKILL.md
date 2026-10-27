---
name: goal-engineering
description: >
  This skill should be used when transforming any prompt, request, design doc, bug
  report, task description, or backlog into a rigorous Claude Code /goal completion
  condition. Use when the user says "craft a goal", "make a /goal", "turn this into
  a goal", "write a goal condition", "goalify this", "set up autonomous execution",
  or wants multi-turn autonomous work with a verifiable end state. This skill writes
  the condition; goal-orchestration runs it; condition-library supplies reusable patterns.
version: 0.1.0
---

# Goal Engineering

Transform any input into a Claude Code `/goal` completion condition that an
evaluator can reliably judge and that Claude can actually finish.

## Why condition quality is everything

`/goal` sets a completion condition. After every turn a small fast model (Haiku
by default) reads the condition plus the conversation so far and returns yes/no
with a short reason. "No" sends Claude back to work with that reason as guidance;
"yes" clears the goal. Claude can loop unattended for hours.

The condition is the entire steering mechanism. A vague condition causes two
failure modes: a **premature yes** (the goal clears before the work is truly
done) or a **never-yes** (Claude loops forever because nothing it produces can
satisfy the wording). Both waste time and tokens. Engineering the condition well
is the highest-leverage step in the whole workflow.

## The one constraint that drives every decision

**The evaluator only sees the transcript. It never runs commands or reads files.**

It judges the condition against what Claude has *surfaced in the conversation*.
Therefore every condition must be **demonstrable from Claude's own output**.

- "All tests in `test/auth` pass" works — Claude runs the tests and the result
  text lands in the transcript for the evaluator to read.
- "The code is high quality" fails — nothing concrete proves it; the evaluator
  guesses.
- "The bug is fixed" fails — "fixed" is not visible; "the failing test
  `test_login_expiry` now passes and Claude has pasted the passing output" is.

When writing a condition, always ask: *what exact text must appear in the
transcript for a careful reader to answer "yes"?* Then make the condition demand
exactly that text.

## The condition recipe

Every durable condition has four parts. Write all four, in this order.

### 1. End state — one measurable outcome

Exactly one primary finish line, expressed as something countable or
binary: a test result, a build exit code, a file count, an empty queue, a
benchmark number. If the request implies several outcomes, pick the one that, if
true, means the work is genuinely done, and fold the rest into checks or
constraints. One end state keeps the evaluator decisive.

### 2. Check — how Claude proves it

State the exact command or observation that produces the proof, and require
Claude to surface its output. Examples: "`npm test` exits 0 and Claude has
pasted the summary line", "`git status --porcelain` prints nothing", "the
output of `wc -l src/parser.ts` shows 400 or fewer". The check turns an abstract
end state into transcript-visible evidence.

### 3. Constraints — what must not break on the way

Anything that must stay true while Claude works: "no file outside `src/auth/`
is modified", "the public API in `index.ts` is unchanged", "no dependency is
added to `package.json`". Constraints stop Claude from satisfying the letter of
the goal by damaging something else.

### 4. Bound — when to stop trying

Always add a turn or time clause so a stuck goal cannot run forever:
"or stop after 25 turns", "or stop after 90 minutes". Claude reports progress
against this clause each turn and the evaluator honors it. A bound converts an
open-ended loop into a contained one.

## The transformation procedure

Apply these six steps to any input — a one-line request, a design doc, a bug
report, a screenshot of errors, a backlog.

1. **Find the true end state.** Read the input and ask what "done" actually
   means. Strip restatements of the task and keep the outcome. "Improve the
   parser" → the outcome is a passing test suite or a size budget, not the verb
   "improve".

2. **Make it measurable.** Convert the end state into something countable or
   binary. If it is not yet measurable, propose the closest measurable proxy and
   say so explicitly (for example, "all 14 acceptance criteria in `spec.md` are
   individually confirmed" instead of "the spec is implemented").

3. **Specify the check.** Name the command or observation and require Claude to
   echo its output. Prefer checks with deterministic output: exit codes, counts,
   diffs, empty/non-empty.

4. **Capture constraints.** Scan the input for anything fragile — public
   interfaces, unrelated files, performance, behavior that must not regress —
   and list each as a "must not" clause. When in doubt, add "no test file is
   modified unless the task is to modify it".

5. **Add a bound.** Estimate effort and set a turn or time limit with headroom.
   Small task: 10–15 turns. Medium: 20–40. Large/backlog: 50+ or a time clause.

6. **Self-review, then emit.** Run the rubric below. Fix every "no" before
   presenting the condition.

## Input-type quick map

Different inputs hide the end state in different places. Load
`references/input-recipes.md` for full worked recipes; this is the index.

| Input type            | Where the end state hides                                  |
|-----------------------|------------------------------------------------------------|
| Vague one-liner       | Infer a measurable proxy; state the assumption out loud    |
| Design / spec doc     | Each acceptance criterion becomes a checkable clause       |
| Bug report            | The failing reproduction becomes the passing check         |
| Refactor request      | A size, count, or structure budget plus "behavior unchanged" |
| Migration             | "Every call site updated" + "build and tests pass"         |
| Issue / task backlog  | "The queue is empty" + per-item done definition            |
| Performance target    | A benchmark number with the measuring command              |
| Cleanup / tech debt   | A count going to zero (lint warnings, TODOs, dead files)   |

## Self-review rubric

Before presenting any condition, verify each item. Any "no" means revise.

- **Transcript-provable?** Can a reader confirm it using only conversation text?
- **Exactly one end state?** Not two competing finish lines.
- **Check named?** A concrete command or observation, with output required.
- **No premature-yes hole?** Could a lazy or partial result still read as "yes"?
  Tighten the wording until it cannot.
- **No never-yes trap?** Is the bar actually reachable by Claude's tools?
- **Constraints listed?** At least the obvious "must not break" items.
- **Bounded?** A turn or time clause is present.
- **Under 4,000 characters?** That is the hard limit for a condition.

## Output format

Present the result in this shape every time:

```
## Crafted /goal condition

/goal <the full condition, ready to paste>

## Anatomy
- End state:   <one line>
- Check:       <one line>
- Constraints: <one line each>
- Bound:       <one line>

## Assumptions
<any proxy or interpretation made when the input was vague — or "none">

## Self-review
<rubric result: all clear, or what was tightened>

## Recommended orchestration
<one-line pointer: which execution mode fits — see goal-orchestration>
```

Keep the `/goal` line copy-paste ready: a single line, no surrounding prose, no
backticks inside it.

## Worked example

Input: *"make the auth module not flaky"*

This is a vague one-liner. The true end state is a reliably passing auth test
suite. Measurable proxy: the suite passes on repeated runs. Check: run it
several times and surface the results. Constraint: do not delete or skip tests
to make them "pass". Bound: 20 turns.

```
/goal the test suite in test/auth passes on 5 consecutive runs of `npm test -- test/auth`, with Claude pasting the summary line of each run; no test is deleted, skipped, or marked .only/.skip, and no file outside src/auth/ or test/auth/ is modified; or stop after 20 turns and report which run failed and why
```

## References

- `references/evaluator-model.md` — how the evaluator works in depth, and how to
  write conditions it can verify; evaluator failure modes and fixes.
- `references/input-recipes.md` — full worked recipes for every input type, each
  with an example input and the condition it produces.

For execution after the condition is written, defer to the **goal-orchestration**
skill. For ready-made parameterized patterns, defer to **condition-library**.
