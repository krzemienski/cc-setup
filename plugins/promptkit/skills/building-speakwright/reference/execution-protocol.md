# Execution protocol

## Evidence naming

`.planning/phases/<phase>/evidence/<gate-id-lowercase>-<what>.<ext>`, for example `vg1-bg.json`, `vg2-s5.png`, `vg-phase-02-summary.json`. Scripts that produce evidence live in `evidence/scripts/` and are committed; they are the gate, so re-running them reproduces the verdict.

## Gate record (append to the plan's SUMMARY.md for each gate)

```markdown
### VG-2 — S9 Providers & keys
- Prerequisites: VG-1 PASS; keys present (names only)
- Executed: `node evidence/scripts/vg1-s9.mjs` at 2026-10-02T14:03Z
- Evidence: evidence/vg1-cards.json, evidence/vg1-s9.png, …
- Criteria:
  - Anthropic and OpenAI cards test-passed with latency > 0 — PASS (412, 388 ms)
  - custom endpoint "Local Anthropic proxy" test-passed; proxy log shows /v1/messages — PASS
  - no plaintext key — PASS
- mock_scan: clean
- Verdict: PASS
```

## SUMMARY.md (per plan)

```markdown
# Phase NN Plan MM: <title> — SUMMARY
Date: YYYY-MM-DD
## What was built
<files and behavior, one paragraph per task>
## Gates
<one gate record per gate>
## Deviations
<anything done differently from the plan, and why; "none" if none>
## Follow-ups
<issues found but out of scope>
```

## NN-VALIDATION.md (per phase)

```markdown
# Phase NN — VALIDATION
## VG-PHASE-NN
Delivers: "<objective copied from ROADMAP>"
| # | Criterion (copied from ROADMAP) | Evidence | Result |
|---|---|---|---|
| 1 | … | evidence/… | PASS |
Regression: VG-PHASE-<NN-1> criteria re-run — PASS
mock_scan: clean
Verdict: PASS
```

`phase_status.py` looks for `VG-PHASE-NN` followed by `Verdict: PASS` in this file.

## STATE.md (whenever the run stops)

```markdown
# Build state
Phase: 03-providers-keys  Plan: 03-02  Last gate: VG-1
Verdict: BLOCKED
Blocker: SPEAKWRIGHT_OPENAI_KEY is not set; the OpenAI card cannot pass Test.
Done so far: <list>
Next action once unblocked: re-run evidence/scripts/vg1-s9.mjs
```

## When a gate fails

1. Read the evidence to find the actual cause; do not guess from the symptom.
2. Fix the real code or configuration.
3. Re-run the entire gate, not only the failing criterion.
4. Record each failed attempt briefly in the SUMMARY (criterion, cause, fix). Three failures on the same criterion with different fixes means the plan or PRD may be wrong: write the finding to STATE.md, propose the correction, and stop for the user.

## Commit convention

`phase NN plan MM: <plan title> — gates PASS`, one commit per passed plan, plus `phase NN: VG-PHASE-NN PASS` after the phase gate. Never commit keys, `.env`, or evidence containing secrets; evidence JSON stores header names, never values.
