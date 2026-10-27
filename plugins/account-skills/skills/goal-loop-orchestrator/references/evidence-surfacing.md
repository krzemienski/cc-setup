# Evidence surfacing — what to print so the evaluator can confirm

The `/goal` evaluator runs no tools. It confirms your condition by reading the transcript. So the loop terminates correctly only if each criterion's **real proof** appears as text in Claude's turns. This file is the per-platform cheat sheet for *what to surface*.

Rule of thumb: for every success criterion, there must be a command Claude runs and an **output Claude shows**. "It works" is invisible. The command's output is the evidence.

## Tests
- Run the suite scoped to the condition: `npm test -- <scope>`, `pytest <path> -q`, `go test ./... `, `cargo test`.
- **Surface:** the summary line — `X passed, 0 failed` / `OK (123 tests)` / `test result: ok. N passed; 0 failed`.
- Do not paraphrase. Paste the line. The evaluator matches "0 failed" against "tests pass."
- Iron Rule: if a test was failing, the proof of "fixed" is the implementation change plus the now-green summary — never a skipped/xfail/deleted test.

## Builds / compiles
- Run the build and capture status: `npm run build; echo "exit=$?"`, `tsc --noEmit; echo "exit=$?"`, `cargo build 2>&1 | tail`, `xcodebuild ... | tail`.
- **Surface:** the explicit `exit=0` (or the tool's success line). Showing only the absence of errors is weaker; show the status.

## Static checks / lint / types
- `eslint . ; echo "exit=$?"`, `ruff check .`, `mypy <pkg>`.
- **Surface:** the "clean" output or zero-error count. "Lint is clean" without the output is not confirmable.

## File-count / size budgets
- `wc -l <dir>/* ` or `find <dir> -name '*.ts' -exec wc -l {} +` then sort.
- **Surface:** the listing (or the max line). The evaluator reads the numbers; let it.

## Queue / backlog drain
- `gh issue list --label bug --state open`, `git log --oneline <range>`, a TODO grep.
- **Surface:** the command output showing the list is empty (or each remaining item). "Backlog cleared" alone won't confirm.

## Working tree / git state
- `git status --porcelain`, `git log --oneline -n 5`.
- **Surface:** the porcelain output (empty = clean) AND, when the condition requires real work, the recent commits proving the change exists — so a clean tree from a stash/revert can't satisfy it.

## CLI binaries
- Execute the real binary with real args: `./mytool run --input real.dat`.
- **Surface:** stdout/stderr and exit code. Run the actual built binary, not a description of what it would do.

## Backend / API
- Hit the running service: `curl -i localhost:8080/health`, `curl -s -X POST .../export -d @real.json | jq .`.
- **Surface:** the HTTP status line and the response body. Use real endpoints and real payloads, not example fixtures.

## Web frontend
- Drive the live page (agent-browser or equivalent) and capture state: screenshot path, the asserted DOM text, the network 200s.
- **Surface:** the captured evidence described in text the evaluator can read (e.g. "screenshot saved to X; the page shows 'Export complete'; POST /export returned 200"). A screenshot file the evaluator can't open must be accompanied by the textual claim of what it shows.

## iOS / macOS (simulator)
- Boot a real simulator, run the app, exercise the flow (`xcrun simctl`, XC-MCP, ios-validation-runner patterns).
- **Surface:** the build success line, the simulator log excerpt proving the action, and the screenshot path with a text description of what it depicts. The evaluator reads text — pair every artifact with its textual assertion.

## Data / ML pipelines
- Run the pipeline on **real input data** and validate the output: row counts, schema check, checksum, sample rows.
- **Surface:** the validation output (e.g. "wrote 1,240,332 rows; schema check OK; sha256 = ..."). Forbidden: sample/synthetic/truncated data standing in for the real run.

## The anti-cheat principle

The condition's constraints ("no mocks", "don't delete tests", "real data only") exist because the fastest path to a green check is sometimes to fake it. Your job orchestrating the loop is to ensure the **surfaced evidence is genuine**. If a turn produces a passing check via a mock, a stub, a skipped test, or fabricated output, the goal has not been met no matter what the evaluator says — treat it as a stall and fix the root cause. Surfaced proof must come from the real system, every time.
