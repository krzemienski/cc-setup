# Parallel team protocol

Read this only when the user chose parallel mode and subagent dispatch is
available. Parallelism buys wall-clock speed at the cost of coordination —
these rules keep the cost from exceeding the benefit.

## Roles

- **Lead (you)** — runs Phases 0–2 solo, partitions the inventory, dispatches
  auditors, verifies their evidence, runs Phase 4 confirmation for
  cross-partition duplicates, writes the report. The lead never delegates
  report writing or evidence verification.
- **Auditor subagents** — each owns a partition of pages and runs Phase 3
  (all three viewports) against it, returning candidate findings.

Phases 0–2 stay solo because they're cheap, sequential by nature, and
everything downstream depends on a single coherent inventory.

## Partitioning

Split by page, not by viewport — an auditor who has seen a page at desktop
spots mobile regressions on the same page much faster. Group related pages
(e.g., all `/docs/*`) into the same partition so shared components get
consistent judgment. Target 3–8 pages per auditor; more auditors than that
rarely helps because evidence verification serializes on the lead anyway.

## Session isolation (the one hard rule)

Every auditor uses its own named browser session:

```bash
agent-browser --session hunt-<partition> open <url>
```

Two agents in one session corrupt each other's refs and navigation state and
produce false findings. If the site required login, the lead saves state once
(`agent-browser state save hunt-auth.json`) and each auditor loads it into its
own session (`state load hunt-auth.json`) — never share a live session.

Auditors must `agent-browser --session hunt-<partition> close` when done.

## Auditor prompt template

```text
You are a QA auditor on a black-box website bug hunt. Read the skill at
<skill-path>/SKILL.md, then execute Phase 3 (audit sweep) ONLY, for these
pages: <list>.

Context:
- Site purpose: <from run-config.md>
- Inventory rows you own: <paste rows>
- Browser session name: hunt-<partition>  (use --session on every command)
- Auth: load hunt-auth.json into your session first  (omit if no auth)
- Evidence dir: <workspace>/screenshots/  (append-only; use your page slugs)

For each page × viewport (1440×900, 768×1024, 375×812): capture the initial
full-page screenshot, run the visual checklist, exercise every inventory
element you own, capture after-interaction screenshots, and collect console
and network errors.

Return: a findings list where each candidate has draft repro steps, the
screenshot paths, and your severity guess. Do NOT write to REPORT.md and do
NOT mark anything as a confirmed bug — the lead confirms. Close your browser
session when finished.
```

## Merge protocol (lead)

1. Collect findings from all auditors.
2. **Read every cited screenshot yourself.** An auditor's summary is a claim;
   the pixels are the evidence. Discard findings whose evidence doesn't show
   what the summary says.
3. De-duplicate across partitions (shared header/footer bugs will be
   reported by every auditor).
4. Run Phase 4 confirmation (second reproduction) yourself, in your own
   session, for every surviving candidate.
5. Write the report.

## Failure handling

- Auditor times out or errors → re-run its partition solo; don't guess at
  what it would have found.
- Two auditors disagree about the same shared component → the lead's own
  reproduction is the tiebreaker.
- Site starts erroring under parallel load → drop to solo and note the
  (possible rate-limiting) observation in the report.
