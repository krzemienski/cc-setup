---
name: memorize
description: Curates insights from reflections into CLAUDE.md as durable, actionable guidance. Triggers on "memorize", "save learning", "remember this pattern".
argument-hint: Optional --dry-run to preview without writing, or a specific insight to memorize
---

# Memorize: Curate Insights into CLAUDE.md

Extract high-value learnings from recent work or reflections and append them to `CLAUDE.md` as actionable guidance.

## What to Memorize

Only capture insights that are:

- **Specific** — names a file, tool, API, flow, or concrete condition
- **Actionable** — written as an imperative rule a future agent can apply immediately
- **Evidence-backed** — observed in code, docs, or repeated failures (not speculation)
- **Generalizable** — applicable to future tasks in this repo, not a one-off workaround
- **Non-redundant** — not already covered by an existing bullet in CLAUDE.md

Skip anything ephemeral: task-specific context, one-time decisions, personal preferences, or vague guidelines like "write clean code."

## Selection Criteria by Type

| Type | Memorize if... |
|------|----------------|
| Error / bug | Root cause is structural and could recur |
| API / tool usage | Auth, pagination, rate limits, or gotchas discovered |
| Pattern | Approach worked and is reusable across tasks |
| Anti-pattern | Approach failed with a clear reason — evidence exists |
| Domain fact | Business rule or constraint not obvious from code |
| Verification item | Concrete check that would have caught a real regression |

## Process

### 1. Identify the source

Look at:
- Recent reflection output (`/reflect` results)
- Critique findings (`/critique` results)
- Decisions made during the current task
- Failures or corrections that occurred

If unclear what to memorize, ask: "What output should I memorize — last message, a specific insight, or reflection results?"

### 2. Extract insights

For each candidate insight, form one bullet using this shape:

```
[Imperative verb] [specific subject] [condition or context if needed].
```

Examples:
- "Always call `git remote get-url origin` before pushing to confirm HTTPS vs SSH."
- "For dataset lookups under 100 items, prefer plain Object over Map — Map overhead dominates at small scale."
- "When adding a new route, restart the dev server; hot reload does not pick up route registration."

### 3. Read current CLAUDE.md

Read the existing file to:
- Confirm the insight is not already present
- Identify the best section to append under
- Detect any contradiction with existing guidance (prefer the more specific, evidence-backed rule)

### 4. Append

Place each bullet under the most relevant existing section. If no section fits, create one with a clear heading.

Rules:
- One idea per bullet — no compound sentences disguised as one rule
- No secrets, tokens, internal URLs, or PII
- Mark version-specific facts inline: e.g., "(as of Node 20)"
- Do not delete or rewrite existing bullets — only add

### 5. Confirm

Report what was added:
- Count of new bullets by section
- Confirm CLAUDE.md was updated (or preview only if `--dry-run`)

## Output Format

```
## Memorize Summary

Added N insight(s) to CLAUDE.md:

- [Section name]: "[bullet text]"
- [Section name]: "[bullet text]"

CLAUDE.md updated. ✓
```

If `--dry-run`, show the proposed bullets without writing and end with `(dry run — no changes made)`.
