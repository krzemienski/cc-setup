---
name: gate-validation
description: >
  Enforces evidence-based validation before marking any task, gate, or milestone
  complete. Triggers on "gate", "validate completion", "evidence check", "mark
  complete". Rejects vague claims. Requires specific file paths, command output,
  or line numbers as proof.
triggers:
  - gate
  - validate completion
  - evidence check
  - mark complete
---

# Gate Validation Protocol

## The Iron Rule

```
NEVER accept vague completion claims.
NEVER mark a gate PASSED without cited evidence.
ALWAYS require specific file paths, line numbers, or command output.
ALWAYS verify build passes and no regressions exist before passing any gate.
```

## Instant Rejection Triggers

Any completion claim containing the following phrases is **automatically rejected**:

| Phrase | Why It Fails |
|--------|--------------|
| "should work" | Speculation — not observation |
| "looks good" | Visual impression — not verified behavior |
| "seems fine" | Hedged — not confirmed |
| "I believe it works" | Belief — not evidence |
| "probably working" | Probability — not proof |
| "tested locally" | Unverified — no artifact cited |

## Required Evidence Checklist

Before any gate can be marked PASSED, all of the following must be satisfied:

- [ ] **Build passes** — cite exact command and output (e.g. `npm run build` exit 0)
- [ ] **No regressions** — cite before/after comparison or confirm unchanged behavior
- [ ] **Evidence files exist** — name the file path(s) where artifacts are saved
- [ ] **Evidence is described** — quote specific content from those files, not just their existence
- [ ] **Specific citations** — include file path + line number or command + output snippet

## Gate Verdict Format

```markdown
### Gate: [Gate name or milestone]
**PASSED** / **FAILED** / **BLOCKED**

Build: `<command>` → exit <code> (cite output line)
Regressions: None detected — <what was checked and how>
Evidence:
- `<path/to/file>` line <N>: "<quoted content>"
- `<command output excerpt>`
```

A gate is **BLOCKED** when any checklist item is unresolved. A **BLOCKED** gate
cannot be promoted to PASSED without completing the missing items.

## Escalation

If a completion claim is made without evidence:

1. **Reject** — state which checklist items are missing
2. **Request** — name the exact artifacts or commands needed
3. **Re-evaluate** — only after the requester provides cited evidence

Never soft-approve to unblock velocity. A false PASSED is worse than a delay.
