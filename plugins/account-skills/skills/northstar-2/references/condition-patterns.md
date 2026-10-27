# Condition patterns

The four-part anatomy, a pattern library of transcript-provable conditions by project type, the anti-patterns that produce false "yes" verdicts, and the hardening checklist. Used in Phases 3–4.

## The four-part anatomy

A condition that survives many turns has:

1. **One measurable end state** — a single outermost signal: a test result, a build exit code, a file/row count, an empty queue.
2. **Stated checks** — how Claude proves it, as real commands whose output lands in the transcript.
3. **Constraints** — what must not change on the way there.
4. **A bound** — a turn or time clause so a stuck loop surfaces.

Write the whole thing as one directive Claude can act on immediately. Prefer exit codes and explicit counts over prose.

## Good vs bad — the core move

The job is turning intent into a transcript-verifiable end state. The bad versions below are unprovable by a model that can't run anything.

| Intent (raw input) | ❌ Unprovable condition | ✅ Provable condition |
|---|---|---|
| "make the refactor clean" | "the refactor is clean and done" | "`npm run lint` and `npm test` both exit 0 (show output each run); no file outside `src/` changed per `git status --porcelain`; or stop after 20 turns" |
| "migrate auth to the new API" | "auth is migrated" | "every call site uses `authV2`: `rg 'authV1\\(' src` prints nothing, and `npm test -- test/auth` exits 0 with output shown; no test deleted or skipped; or stop after 25 turns" |
| "fix the failing CI" | "CI passes" | "`npm test` exits 0 and `npm run build` exits 0, both re-run on the final turn with output shown; no test is skipped or its assertion weakened; or stop after 15 turns" |
| "clear the issue backlog" | "all issues handled" | "`gh issue list --label ready --json number` prints `[]`; each closed issue has a linked commit; or stop after 30 turns" |
| "split the big file" | "the file is split up" | "no file in `src/parsers/` exceeds 300 lines: `find src/parsers -name '*.ts' -exec wc -l {} + | awk '$1>300'` prints no rows; `npm test` exits 0 with output shown; or stop after 12 turns" |

## Provable check vocabulary by project type

Reach for checks that print an unambiguous result into the transcript.

- **Tests**: `pytest -q` / `npm test` / `cargo test` / `go test ./...` exits 0 — and the run is shown on the final turn.
- **Build**: `npm run build` / `cargo build --release` / `make` exits 0.
- **Lint/format/types**: `ruff check .` / `npm run lint` / `tsc --noEmit` / `cargo clippy -- -D warnings` exits 0.
- **Clean tree / scope**: `git status --porcelain` empty, or its output shows only allowed paths.
- **Absence (a thing is gone)**: `rg '<pattern>' <dir>` prints nothing.
- **Count / threshold**: a command that prints a number, with the target stated ("the count printed is 0").
- **Empty queue / backlog**: a list command that prints `[]` or zero rows.
- **iOS/native** (per the user's stack): a real simulator/build signal surfaced as text — e.g. `xcodebuild ... build` exits 0, or a validation-runner step prints a PASS line with the evidence path — never "the screenshot looks right".
- **HTTP/API**: a real `curl` whose status line / body is echoed into the transcript and matches a stated expectation.

## Constraints worth defaulting in

The loop will take shortcuts if you let it. Common guardrails:
- "no test is deleted, skipped, or its assertions weakened to make the suite pass"
- "no mock, stub, fixture, or test-mode fallback is introduced"
- "no file outside `<scope>` is modified"
- "no new dependency is added" (when relevant)
- "the proving command is re-run on the final turn, not cited from an earlier one"

## Bounds

Always include one. Size it to the task: small fix 10–15 turns, feature/migration 20–30, large sweep 30+. Time bounds ("or stop after 30 minutes") suit watch-style goals. The bound is the only thing standing between a stuck loop and unbounded token spend.

## Anti-patterns (these produce false "yes" verdicts)

- **Subjective end states**: "clean", "done", "production-ready", "looks correct" — nothing in the transcript proves them.
- **File-state claims with no command**: "all imports updated" without a grep that proves it.
- **Proof by assertion**: letting Claude *say* it passed instead of *showing* the passing run.
- **Stale proof**: relying on a passing run from turn 3 when later turns changed code — require a final-turn re-run.
- **Cheatable checks**: "the test file passes" (can be satisfied by deleting the test) — pair every test check with a no-deletion/no-skip constraint.
- **Mock-satisfied checks**: a check that a stub can make green — forbid mocks explicitly.
- **No bound**: a condition that can never be met loops until the user notices.
- **Multiple competing end states**: pick one outermost signal; fold the rest into checks/constraints.

## Hardening checklist (Phase 4)

Read the drafted condition adversarially and confirm:
- [ ] Could a turn that did NOT actually finish produce text the evaluator would accept? If yes, tighten.
- [ ] Is every "done" signal an exit code, an empty output, or an explicit count — not prose?
- [ ] Is the proving command required to run on the final turn?
- [ ] Are the obvious cheats (delete/skip tests, edit out of scope, mock, fake output) forbidden by a constraint?
- [ ] Is there exactly one outermost end state?
- [ ] Is a bound present?
- [ ] Is the whole condition ≤ 4000 characters and a single actionable directive?
