---
name: do-in-steps
description: Execute complex tasks through sequential sub-agent orchestration, passing results forward at each step with model-routed agents and per-step verification.
triggers:
  - "do in steps"
  - "step by step"
  - "sequential execution"
  - "chain agents"
---

# Do In Steps

Execute a complex task as a chain of focused sub-agents, each building on the previous step's output.

## Steps

### 1. Decompose the Task

Break the request into discrete, ordered steps. Each step must have:
- A single clear objective
- Explicit inputs (what it receives from the prior step)
- Explicit outputs (what it passes to the next step)
- A model assignment based on complexity

**Model Routing**

| Complexity | Model | Use For |
|------------|-------|---------|
| Simple | `haiku` | Lookups, reads, searches, summarization |
| Standard | `sonnet` | Implementation, file edits, refactoring |
| Complex | `opus` | Architecture, deep analysis, ambiguous design |

### 2. Execute Each Step Sequentially

For each step N:

1. Announce: `[Step N/Total] <Objective> — dispatching <agent> (<model>)`
2. Dispatch a Task agent with:
   - The step objective
   - A concise summary of all prior step outputs (not raw dumps)
   - Relevant file paths, symbol names, and code context
   - Explicit scope: what this agent should and should not do
3. Wait for the result before proceeding
4. Verify the result meets the step's output criteria
5. If verification fails: diagnose, re-dispatch once with a corrected prompt, then escalate on second failure

**Never dispatch step N+1 until step N is verified.**

### 3. Pass Context Forward

Summarize each completed step into a compact handoff:

```
Step N result: <2-3 sentence summary of what was done and key outputs>
Artifacts: <file paths or symbols changed/created>
```

Include this handoff block in every subsequent agent prompt. Keep it under 10 lines total regardless of how many steps have completed.

### 4. Synthesize

After all steps complete, deliver a unified summary:
- What each step accomplished
- All files or symbols changed
- Any deferred issues or open questions

## Rules

1. Each agent owns a distinct scope — no two parallel agents touch the same file
2. Always include file paths and symbol names in agent prompts — never spawn without context
3. After 2 failed verifications on the same step, escalate to `oh-my-claudecode:architect`
4. Do not compress the handoff so aggressively that the next agent lacks needed context

## Output Format

```
## Step Plan
Step 1: <Objective> [haiku/sonnet/opus]
Step 2: <Objective> [haiku/sonnet/opus]
...

## Execution
[Step 1/N] <Objective> — complete
  Result: <summary>
[Step 2/N] <Objective> — complete
  Result: <summary>
...

## Summary
<What was accomplished end-to-end>

## Open Issues
<Unresolved items, or "None">
```
