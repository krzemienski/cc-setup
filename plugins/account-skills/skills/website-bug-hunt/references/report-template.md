# REPORT.md template

Use this exact structure. The report has two audiences at once: a human
skimming for "how bad is it", and a coding agent that will be handed one fix
prompt at a time. Write every section so it survives being read out of
context.

````markdown
# Bug hunt report — <site name or URL>

- **Target**: <URL>
- **Date**: <ISO date>
- **Stated purpose**: <user's answer, or "inferred: …">
- **Stop condition**: full-coverage | bug-quota N | time-box M
- **Mode**: solo | parallel (<N> subagents)
- **Driver**: playwright (default) | agent-browser

## Summary

| Metric | Value |
|--------|-------|
| Pages discovered | N |
| Pages audited | N (X%) |
| Interactive elements exercised | N of N |
| Viewports | desktop 1440×900, tablet 768×1024, mobile 375×812 |
| Findings confirmed | N (C critical / H high / M medium / L low) |
| — of which UX findings | N |
| Console/network errors observed | N |
| Not covered | N pages / N gated areas |
| Escalation rungs used (relentless quota only) | 1–K of 6 |

### Bug index

| ID | Severity | Title | Where |
|----|----------|-------|-------|
| BUG-001 | CRITICAL | … | /checkout (all viewports) |

## Bugs

### BUG-001 — <one-line title> `CRITICAL`

- **URL**: <exact URL>
- **Boundary matrix**: desktop:FAIL tablet:FAIL mobile:PASS · logged-out:FAIL logged-in:PASS <extend as probed>
- **Also affects** (blast radius, tested): <sibling pages/elements confirmed to share the root symptom>
- **Reproduced**: 2/2 (or INTERMITTENT 1/2 — both attempts described below)
- **Root symptom**: <smallest black-box-defensible cause, e.g., "`POST /api/cart` → 401 `{"error":"no session"}`, swallowed by the UI">
- **Type**: functional / visual / UX / console-network

**Steps to reproduce**

1. Open <URL> at <viewport size>
2. …numbered, minimal, from a fresh page load…
3. Observe: <the defect>

**Expected**: <what the label/context promised>
**Actual**: <what happened, described from the evidence>

**Evidence**
- `bugs/BUG-001/before.png` — <one line on what it shows>
- `bugs/BUG-001/defect.png` — <one line on what it shows>
- Console: `<error line>` (if relevant)

**Fix prompt**

```text
You are working in the codebase that serves <URL>. Fix this bug:

<one-line title>

Repro (verified twice on the live site):
1. …
2. …

Expected: …
Actual: …
Boundary matrix: <where it fails / where it doesn't>
Root symptom (black-box evidence): …
Console/network evidence: …

Likely area: <your black-box inference — e.g., "the mobile nav toggle
handler" — phrased as a hint, not a certainty>.

Acceptance criteria (evidence-gated — no mocks, no stubs, no test files):
- Following the repro steps above against the RUNNING site no longer
  produces the defect at <viewports/states from the boundary matrix>
- <any secondary check, e.g., "no console errors on load">
GATE: Do not consider this fixed until you have re-run the repro steps
against the running site and captured a screenshot proving the new
behavior. A fix without live-repro proof is not a fix.
```

*(…repeat per finding, ordered CRITICAL → LOW. UX findings are findings —
they appear here with everything above, never only in Observations…)*

## Observations (strictly non-findings)

Only for things that are genuinely not defects: absent features the site
never advertised, deliberate-looking design choices you verified work, and
slow-but-functioning pages below any reasonable threshold. Anything you
flagged as a problem belongs in Findings, whatever its severity.

## Coverage gaps

- **Gated**: <login/paywall areas not audited, and why>
- **Uncrawled**: <pages beyond the crawl cap>
- **Skipped by stop condition**: <if bug-quota or time-box ended the run early>

## Appendix — inventory

<the final inventory table, each row marked PASS / BUG-NNN / NOT-COVERED>
````

## Writing rules

- Reproduction steps always start from a URL and a viewport — never from
  "on the page from the previous bug".
- One screenshot minimum per finding; reference paths relative to the report.
- The fix prompt must stand alone: someone pasting only that block into a
  coding agent gets everything needed. No "see above".
- Order findings by severity, then by page. Keep titles under ~12 words and
  symptom-first ("Checkout button dead on mobile", not "Issue with button").
- Every finding gets the full treatment regardless of severity — LOW is an
  ordering position, not an exemption.
- If the user asked for the report as a single file, inline the inventory;
  otherwise link it.

---

# MASTER-FIX-PROMPT.md template

Always emit this file alongside REPORT.md. It is the one artifact the user
pastes into a coding agent (or wraps in a `/goal`) to remediate everything.
Compose it with `create-meta-prompts` and `transform-validation-prompt`
when installed; either way it must match this shape and stand completely
alone — every finding embedded verbatim, zero references to the report.

````markdown
<remediation_mission>
You are working in the codebase that serves <URL> (<stated purpose>).
A black-box audit on <ISO date> confirmed <N> findings
(<C> CRITICAL / <H> HIGH / <M> MEDIUM / <L> LOW), each verified twice on
the live site with evidence. Your mission: fix every finding, in order,
proving each fix against the running site before moving to the next.
</remediation_mission>

<iron_rule>
Real-system proof only. No mocks, no stubs, no test files as evidence.
A finding is fixed ONLY when its reproduction steps, re-run against the
running site, no longer produce the defect — captured in a screenshot or
response log. Claiming a fix without live proof is a gate failure.
</iron_rule>

<execution_order>
Work the findings CRITICAL → HIGH → MEDIUM → LOW, in index order below.
Complete the validation gate for each before starting the next.
</execution_order>

<findings_index>
| # | ID | Severity | Title |
|---|----|----------|-------|
| 1 | BUG-003 | CRITICAL | … |
…all findings, no omissions — LOW included…
</findings_index>

<finding id="BUG-003" severity="CRITICAL">
  <title>…</title>
  <repro>
  1. Open <URL> at <viewport>
  2. …verbatim from the report…
  </repro>
  <boundary_matrix>desktop:FAIL tablet:FAIL mobile:PASS …</boundary_matrix>
  <root_symptom>…verbatim…</root_symptom>
  <expected>…</expected>
  <actual>…</actual>
  <likely_area>…hint, not certainty…</likely_area>
  <acceptance_criteria>
  - Repro steps above no longer produce the defect at <all FAIL cells of
    the boundary matrix>
  - <secondary checks>
  </acceptance_criteria>
  <validation_gate>
  Re-run the repro against the running site. Capture proof (screenshot /
  response log). GATE-BLOCK: do not proceed to the next finding until this
  evidence exists and you have personally read it.
  </validation_gate>
</finding>

…one <finding> block per finding, all severities…

<final_gate>
After the last fix:
1. Re-run the reproduction steps for ALL findings above against the
   running site — every one must no longer produce its defect.
2. Smoke-test the P0 journeys (<list from the audit inventory>) at
   desktop and mobile viewports to catch regressions.
3. Produce a completion summary: per finding, the evidence path proving
   the fix. The mission is complete only when this table has no gaps.
</final_gate>
````

## Master-prompt rules

- Every finding from the report appears as a `<finding>` block — the Flag
  Rule extends to remediation; nothing is "too low" to include.
- Repro, boundary matrix, root symptom, and acceptance criteria are copied
  verbatim, not summarized.
- Gates are per-finding AND final; both are gate-blocking.
- If the user wants unattended execution, offer to wrap this file into a
  `/goal` condition via `northstar` / `goal-condition-architect`.
