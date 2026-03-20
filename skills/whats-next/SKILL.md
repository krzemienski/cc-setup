---
name: whats-next
description: Analyze the current session and produce a handoff document so a fresh Claude context can resume exactly where this left off.
triggers:
  - "whats next"
  - "what's next"
  - "handoff"
  - "session summary"
  - "continue later"
---

# What's Next — Session Handoff

Generate a handoff document from this session so work can resume in a fresh context without lost state.

## Steps

### 1. Audit the Session

Review the full conversation and identify:

- **Completed work**: what was built, changed, or decided — with file paths
- **In-progress work**: tasks started but not finished — with file paths and line numbers
- **Blocked work**: items waiting on user input, external dependency, or unresolved decision
- **Deferred work**: items mentioned but intentionally skipped

### 2. Determine the Save Path

Use today's date and current time:

```
./plans/handoff-YYMMDD-HHMM.md
```

### 3. Write the Handoff Document

Save to the path above with this structure:

```markdown
# Session Handoff — YYMMDD-HHMM

## Accomplished

- <what was done> (`path/to/file.ts:42`)
- ...

## Unfinished Work

- [ ] <task> — `path/to/file.ts:88` — <why it stopped>
- ...

## Blockers / Decisions Needed

- <question or blocker> — context: <brief explanation>

## Resume Prompt

Paste this into a fresh Claude session to continue:

---
<self-contained prompt that includes: goal, relevant file paths with line numbers,
current state, next concrete action, and any open decisions>
---
```

### 4. Output to User

Print the full handoff document to the conversation, then output:

```
Handoff saved to: ./plans/handoff-YYMMDD-HHMM.md

Start a new session and paste the Resume Prompt above to continue.
```

## Rules

- Resume Prompt must be self-contained — assume zero shared context with the next session.
- Include absolute file paths and line numbers wherever work is file-specific.
- If nothing was accomplished, say so. Never fabricate blockers or tasks not in the conversation.
