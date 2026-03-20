---
name: orchestrate
description: Break complex tasks into discrete subtasks and coordinate specialized agents with parallel dispatch and progress tracking.
triggers:
  - "orchestrate"
  - "execute this"
  - "implement"
  - "build this"
---

# Orchestrate

Coordinate specialized agents to complete complex multi-step tasks efficiently.

## Steps

### 1. Analyze and Decompose

Restate the task in your own words. Break it into discrete subtasks with clear boundaries and explicit dependencies. Classify each subtask by type so you can route to the right agent.

### 2. Build Execution Plan

Map each subtask to an agent and identify which can run in parallel vs. sequentially.

**Agent Routing**

| Agent | Use For |
|-------|---------|
| `oh-my-claudecode:executor` | Code implementation, file edits |
| `oh-my-claudecode:planner` | Feature design, phase breakdown |
| `oh-my-claudecode:architect` | System design, interfaces |
| `oh-my-claudecode:debugger` | Root cause analysis, bug fixes |
| `oh-my-claudecode:build-fixer` | Build errors, type failures |
| `oh-my-claudecode:explore` | Codebase discovery, symbol mapping |
| `oh-my-claudecode:verifier` | Completion evidence, claim validation |
| `oh-my-claudecode:quality-reviewer` | Logic defects, maintainability |

**Execution Patterns**

Sequential (later tasks depend on earlier):
```
agent-A → agent-B → agent-C
```

Parallel (independent tasks):
```
         ┌→ agent-A ─┐
trigger →├→ agent-B ─┼→ synthesize
         └→ agent-C ─┘
```

### 3. Execute with Progress Tracking

For each phase, announce it before dispatching:

```
[Phase 1/N] <Name> — dispatching <agent>
[Phase 2/N] <Name> — parallel dispatch: <agent-A>, <agent-B>
[Phase N/N] Synthesizing results
```

Dispatch independent tasks in the same message using parallel Task calls. Wait for results before starting dependent phases.

Pass full context to every agent: relevant file paths, function names, code snippets, and the specific subtask scope. Never spawn an agent without context.

### 4. Synthesize Results

After all phases complete, combine agent outputs into a unified result. Resolve any conflicts between agent outputs. Report what was completed, what changed, and any unresolved issues.

### 5. Validate

Confirm the work meets the original requirements. If anything is incomplete, dispatch a targeted follow-up agent rather than re-running the full orchestration.

## Coordination Rules

1. Each agent owns distinct files — no overlap between parallel agents
2. Pass file paths and function names explicitly in every agent prompt
3. If an agent fails, diagnose before retrying — do not repeat blindly
4. After 3 failures on the same subtask, escalate to `oh-my-claudecode:architect`
5. Report progress after each phase; do not go silent during long orchestrations

## Output Format

```
## Execution Plan
Phase 1: <Name> [agent]
Phase 2: <Name> [agent-A, agent-B — parallel]
Phase 3: Validation [verifier]

## Progress
[Phase 1/3] <Name> — complete
[Phase 2/3] <Name> — complete
[Phase 3/3] Validation — complete

## Results
<Unified summary of what was built/changed>

## Unresolved
<Any issues that need follow-up, or "None">
```
