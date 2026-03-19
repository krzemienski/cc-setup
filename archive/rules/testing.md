# Validation Requirements

## Functional Validation Mandate

**NEVER:** write mocks, stubs, test doubles, unit tests, or test files. No test frameworks. No mock fallbacks.

**ALWAYS:** build and run the real system. Validate through actual user interfaces. Capture and verify evidence before claiming completion.

## Mandatory Skill Invocation

**BEFORE any task**, check available skills. If a skill might apply (even 1% chance), invoke it first.

Key validation skills to always consider:
- `functional-validation` — Full functional validation protocol
- `gate-validation-discipline` — Evidence-based completion verification
- `no-mocking-validation-gates` — Enforces real system validation
- `e2e-validate` — End-to-end validation flows
- `create-validation-plan` — Structured validation planning

**NEVER rationalize skipping a skill.** Skills have project-specific context you lack. Scan the full skill list and select the most relevant ones for the current task.

## Gate Validation Discipline

**NEVER mark any gate, task, or checkpoint as complete until you have:**

1. **Personally examined the evidence** — Not just received a report about it
2. **Cited specific proof** — File paths, line numbers, exact output, screenshot content
3. **Matched evidence to criteria** — Each validation criterion has corresponding proof

### Verification Checklist (MANDATORY before any completion claim)

```
[ ] Did I READ the actual evidence file (not just the report about it)?
[ ] Did I VIEW the actual screenshot (not just confirm it exists)?
[ ] Did I EXAMINE the actual command output (not just the exit code)?
[ ] Can I CITE specific evidence for each validation criterion?
[ ] Would a skeptical reviewer agree this is complete?
```

### Evidence Standards

- **Screenshots**: Describe what you SEE, not that it exists. "Viewed screenshot — shows 3 sessions listed with green status indicators"
- **API responses**: Quote the actual response body, not just the status code
- **Builds**: Quote the actual output line showing success, not just "build succeeded"

## Validation Approach

1. **Build the real system** — No placeholders, no stubs
2. **Run it** — Start the app, simulator, or service
3. **Exercise through UI** — Use Playwright MCP or actual device interaction
4. **Capture evidence** — Screenshots, logs, network responses
5. **Verify behavior** — Confirm outputs match expectations using gate validation discipline

## Troubleshooting Failures

1. Read actual error messages and stack traces
2. Trace through the real code path
3. Fix the implementation (not a test harness)
4. Re-validate through the UI

## Agent Support

- Use `functional-validation` skill for the full protocol
- Use `gate-validation-discipline` skill for completion verification
- Use Playwright MCP for browser-based validation
