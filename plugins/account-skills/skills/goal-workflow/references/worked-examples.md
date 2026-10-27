# Worked examples — input to running goal

Each example shows the full pipeline: the raw input, the end state extracted from it, the crafted `/goal` command, and the orchestration choices. These are illustrative — adapt the commands and the proof clauses to the real repo.

## Example 1 — vague one-liner

**Input:** "the auth tests are flaky, get them solid"

**Stage 1 (understand):** ambiguous between "make them pass" and "make them non-flaky." One clarifying question resolves it. Say the answer is: pass reliably across 3 consecutive runs.

**Stage 2 (craft):**
```
/goal The auth test suite passes 3 consecutive times: run `npm test -- test/auth` three times in a row and show all three summary lines, each proving 0 failures. Fix the root cause of flakiness in the implementation or test setup — do not skip, retry-wrap, xfail, or delete tests, and do not add mocks to mask timing. Stop after 15 turns and report the flakiest test if it isn't solid by then.
```
Bound rationale: small, single-suite scope → 15 turns.

**Stage 3-4 (run):** interactive first run with auto mode off so you can watch the reasons; the proof is three printed summaries; stall signal would be the same test failing on run 2 every time → diagnose the actual race.

## Example 2 — design doc

**Input:** "implement the export feature from DESIGN.md"

**Stage 1:** the doc lists acceptance criteria; distill to three checkable outcomes (build, functions + integration test, docs).

**Stage 2:**
```
/goal The export feature in DESIGN.md is complete, proven by ALL of: (1) `npm run build` exits 0 — show `exit=$?`; (2) `exportToCsv` and `exportToJson` exist and `npm test -- export` passes — show the summary; (3) README documents both commands — show the diff of the added section. Constraints: no existing public export is renamed; no mocked or stubbed implementations. Stop after 30 turns and summarize unmet criteria if not all three hold.
```
Bound rationale: multi-criterion feature → 30 turns.

**Stage 3-4:** interactive or headless under auto mode once trusted; evidence is the three artifacts surfaced; watch that criterion (2) isn't satisfied by a stub returning a fixed string.

## Example 3 — backlog drain

**Input:** "clear the bug-labeled issues"

**Stage 1:** end state is an empty filtered queue.

**Stage 2:**
```
/goal The queue of open issues labeled `bug` is empty: after each fix, run `gh issue list --label bug --state open` and show its output; the goal holds only when that prints no issues. Each closed issue must reference the commit that fixed it. Do not close an issue without a real code change. Stop after 25 turns and list issues still open if any remain.
```
Bound rationale: queue length unknown → 25 turns as a safe default; scale up if the queue is large.

**Stage 3-4:** headless `-p` is reasonable here since the shape is well understood; the empty `gh issue list` output is the terminating proof; stall signal is an issue that keeps reopening or a fix that won't land.

## Example 4 — migration

**Input:** "we're moving off the old http client, finish the migration"

**Stage 1:** end state is no remaining references to the old client, with build + tests green.

**Stage 2:**
```
/goal The migration off `OldHttpClient` is complete: `grep -rn "OldHttpClient" src` returns nothing (show the output), `npm run build` exits 0 (show `exit=$?`), and `npm test` passes (show the summary). Constraints: public signatures in `src/api/index.ts` are unchanged; no call site is deleted just to clear the grep. Stop after 35 turns and list remaining references if any.
```
Bound rationale: cross-file migration → 35 turns.

**Stage 3-4:** interactive at first so you can confirm the grep target is right; the empty grep + green build + green tests are the combined proof; stall signal is the grep count plateauing above zero (a reference Claude can't safely rewrite — diagnose it).

## What every example has in common

- Exactly one end state (or one explicit ALL-of checklist).
- A printed proof for every criterion — because the evaluator reads only the transcript.
- Constraints that block the cheap cheat (delete the test, stub the function, fake the data).
- A bound sized to the work.
- An orchestration choice (interactive vs headless, auto mode on/off) matched to how trusted the condition is.
