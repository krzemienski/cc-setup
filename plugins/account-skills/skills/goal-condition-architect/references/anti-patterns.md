# Goal condition anti-patterns

Run a draft condition past this list before emitting it. Each anti-pattern maps to a concrete failure mode of the evaluator-driven loop.

## 1. The unprovable claim
**Bad:** `/goal the authentication code is correct and secure`
**Why it fails:** "correct" and "secure" are not observable in the transcript. The evaluator has nothing to read, so it answers "no" every turn and the goal loops to its bound.
**Fix:** name the observable proof — tests pass and their summary is shown; a specific security check runs and its output is shown.

## 2. Multi-goal soup
**Bad:** `/goal refactor the parser, also improve the docs, and look into the slow query`
**Why it fails:** three unrelated end states with no single completion signal. The evaluator can't tell when "done" is done; partial progress on one reads as failure overall.
**Fix:** one goal per run. If criteria are genuinely related, make them an explicit checklist under a single end state ("complete when ALL of (1)(2)(3) hold"). Otherwise sequence separate goals.

## 3. No bound
**Bad:** `/goal make every test in the suite pass`
**Why it fails:** if the suite has a genuinely unfixable test or a flaky one, the goal never confirms and burns turns/tokens unattended.
**Fix:** append `or stop after N turns` (or a time clause). The bound makes the run inspectable instead of runaway.

## 4. Cheatable success
**Bad:** `/goal npm test exits 0`
**Why it's risky:** the fastest way to make tests pass is to delete or skip the failing ones. Under auto mode this can actually happen.
**Fix:** add the constraints that close the loophole — "fix the implementation, not the tests; do not skip, xfail, or delete any test; no mocks or stubbed returns." Forbid the cheat explicitly.

## 5. Proof that never surfaces
**Bad:** `/goal all files in src/parsers are under 200 lines`
**Why it fails:** true or not, the evaluator can't see file lengths — it runs no tools. It will answer "no" indefinitely.
**Fix:** require the artifact be printed — "run `wc -l` over the directory and show the output proving no file exceeds 200 lines." Make the check produce transcript text.

## 6. Pasting the whole document
**Bad:** `/goal <entire 3,000-line design doc pasted in>`
**Why it fails:** blows past the 4,000-char budget, buries the actual end state, and gives the evaluator a haystack instead of a target.
**Fix:** distill to the acceptance criteria as a short checklist. Reference the doc by name ("the export feature in DESIGN.md") and list only the checkable outcomes.

## 7. Moving-target conditions
**Bad:** `/goal keep improving performance until it's fast enough`
**Why it fails:** "fast enough" has no fixed line; every turn can plausibly read as "not yet."
**Fix:** fix the line — "p95 latency for `GET /search` is under 200ms, proven by showing the benchmark output." A goal needs a stationary target.

## 8. Constraint-free destructive work
**Bad:** `/goal the working tree is clean (git status shows nothing to commit)`
**Why it's risky:** committing or stashing everything trivially satisfies it without doing the intended work.
**Fix:** pair the end state with what the change must contain — "...after the feature is implemented and `npm test` passes (show the summary); the clean tree must follow real commits that add the feature, not a stash or revert."

## Final sanity checklist

Before emitting, confirm the draft has:
- [ ] exactly one end state (or one explicit ALL-of checklist)
- [ ] every clause backed by a "show / print / display the output" proof step
- [ ] constraints that block the obvious cheats (especially: no deleting tests, no mocks/stubs)
- [ ] a turn or time bound
- [ ] under 4,000 characters, ideally far under
- [ ] phrased as a directive Claude can act on, not a wish
