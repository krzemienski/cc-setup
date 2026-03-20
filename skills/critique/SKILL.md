---
name: critique
description: Multi-perspective review using specialized judges with debate and consensus building. Triggers on "critique", "review", "multi-perspective review", "challenge this".
argument-hint: Optional file paths, commits, or context to review (defaults to recent changes)
---

# Work Critique

Report-only review using three parallel judges. No automatic fixes — findings are for user consideration.

## Phase 1: Scope

Identify what to review:
- Arguments provided: use them as scope
- No arguments: use recent conversation history and file changes
- Unclear: ask "What work should I review?"

Announce scope before proceeding:

```
Review Scope:
- Request: [summary]
- Files: [list]
- Approach: [brief description]

Starting multi-agent review...
```

## Phase 2: Parallel Judge Reviews

Spawn three agents in parallel via Task tool. Each works independently.

### Judge 1 — Requirements Validator

Review alignment with original requirements. For each requirement: met / partial / missed.

Output:
```
### Requirements Score: X/10

Coverage:
- [met]
- [partial] — [why]
- [missed] — [why]

Gaps: [item] — Severity: Critical/High/Medium/Low
Scope creep: [item] — [good or problematic?]
```

### Judge 2 — Solution Architect

Evaluate the technical approach and design decisions against alternatives.

Output:
```
### Architecture Score: X/10

Approach: [description]
Strengths: [list]
Weaknesses: [list]

Alternatives considered:
1. [name] — Pros/Cons — Better/Worse/Equivalent
2. [name] — Pros/Cons — Better/Worse/Equivalent

Anti-patterns: [item] — Severity
Scalability/Maintainability: [assessment]
```

### Judge 3 — Code Quality Reviewer

Assess implementation quality and refactoring opportunities.

Output:
```
### Code Quality Score: X/10

Strengths: [list with examples]

Issues:
- [issue] — Severity: Critical/High/Medium/Low — [file:line]

Refactorings (prioritized):
1. [name] — Priority: High/Medium/Low — Effort: S/M/L
   Before: [snippet]
   After: [snippet]

Code smells: [item at location — impact]
```

## Phase 3: Debate

After all three reports:

1. Identify agreements and contradictions.
2. If significant disagreements exist, spawn follow-up agents with both conflicting views and ask each to defend or revise their position.
3. Synthesize: note resolved vs. unresolved disagreements ("reasonable people may disagree").

## Phase 4: Consensus Report

```markdown
# Critique Report

## Summary
[2-3 sentences]

**Overall Score**: X/10

| Judge | Score | Key Finding |
|-------|-------|-------------|
| Requirements Validator | X/10 | [one-line] |
| Solution Architect | X/10 | [one-line] |
| Code Quality Reviewer | X/10 | [one-line] |

## Strengths
1. **[Strength]** — [evidence] — Source: [judge(s)]

## Issues (Critical / High / Medium / Low)
- **[Issue]** — [file:line] — [impact] — Recommendation: [action]

## Requirements
Met: X/Y | Coverage: Z% | [table with status per requirement]

## Architecture
Chosen: [description] | Alternatives: [why chosen wins/loses vs each]
Recommendation: [keep / switch because...]

## Refactorings
1. **[Name]** — Priority: High/Med/Low — Effort: S/M/L — Benefit: [x]

## Consensus / Debate
Agreed: [item]
Disputed: **[Topic]** — [Judge A] vs [Judge B] — Resolution: [outcome or "reasonable disagreement"]

## Action Items
Must Do: - [ ] [Critical action]
Should Do: - [ ] [High priority action]
Could Do: - [ ] [Medium priority action]

## Verdict
[Ready to ship | Needs improvements | Requires rework]
```

## Guidelines

- Cite file:line and code examples — no vague assertions
- Frame criticism as improvement opportunities
- Account for project constraints (size, timeline, existing conventions)
- Scores are relative to professional development standards
- Disagreements between judges are valuable signal, not failure
