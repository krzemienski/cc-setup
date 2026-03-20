---
name: plan
description: Create a structured implementation plan with risk assessment, phased steps, and validation gates. Saves plan to ./plans/ directory. Waits for user confirmation before any implementation begins.
triggers:
  - "plan"
  - "plan this"
  - "create a plan"
  - "implementation plan"
  - "plan the"
  - "let's plan"
---

# Plan

Create a detailed, file-backed implementation plan before any code is written.

## Steps

### 1. Restate Requirements

Restate what will be built in your own words. Be specific about scope and what is explicitly out of scope.

### 2. Assess Risks

Rate each risk HIGH / MEDIUM / LOW:

- **HIGH**: Could block implementation or require architectural rethink
- **MEDIUM**: Needs attention but has a clear mitigation path
- **LOW**: Minor concerns, acceptable to defer

### 3. Build the Plan

Break work into phases. Each phase must have:
- A clear goal statement
- Concrete, numbered steps
- A validation gate before the next phase starts

Phase structure:
```
Phase 1: <Name>
Goal: <What this phase achieves>
Steps:
  1.1 ...
  1.2 ...
Validation gate: <What must be true before Phase 2 begins>
```

Every plan must end with a **Functional Validation Phase**:
```
Phase N: Functional Validation
Goal: Prove the system works end-to-end through real execution
Steps:
  N.1 Build / start the real system (no mocks, no stubs)
  N.2 Exercise the feature through its actual interface (CLI, UI, API)
  N.3 Capture evidence (screenshot, log output, response body)
  N.4 Confirm evidence matches requirements from Phase 1
Validation gate: Evidence captured and requirements met
```

No unit tests. No test files. No mocks. Validate through the real system only.

### 4. Save the Plan

Determine the plan slug from the requirements (kebab-case, descriptive).

Save the plan to:
```
./plans/YYMMDD-HHMM-<slug>/plan.md
```

Use today's date and current time for the timestamp (format: YYMMDD-HHMM).

The plan file should contain:
- Requirements restatement
- Risk table
- All phases with steps and validation gates
- Dependencies (external services, APIs, tools)
- Complexity estimate (HIGH / MEDIUM / LOW) with rough time estimate

### 5. Wait for Confirmation

After saving the plan, output the full plan to the user and end with:

```
Plan saved to: ./plans/YYMMDD-HHMM-<slug>/plan.md

CONFIRM to proceed, or tell me what to change.
```

**Do NOT write any code, create any files (other than the plan), or take any implementation action until the user replies with "confirm", "yes", "proceed", or equivalent.**

If the user requests changes, update the plan file and re-present it. Wait again.

## Output Format

```markdown
## Requirements

<Clear restatement of what will be built and what is out of scope>

## Risks

| Severity | Risk | Mitigation |
|----------|------|------------|
| HIGH     | ...  | ...        |
| MEDIUM   | ...  | ...        |
| LOW      | ...  | ...        |

## Dependencies

- <Dependency 1>: <why needed>

## Complexity: HIGH / MEDIUM / LOW (~X hours / days)

## Phases

### Phase 1: <Name>
**Goal:** ...
1.1 ...
1.2 ...
**Validation gate:** ...

### Phase 2: ...

### Phase N: Functional Validation
**Goal:** Prove the system works through real execution
N.1 Build / start the real system
N.2 Exercise through actual interface
N.3 Capture evidence
N.4 Confirm requirements met
**Validation gate:** Evidence captured and requirements met
```
