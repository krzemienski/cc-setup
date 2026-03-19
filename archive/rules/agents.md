# Agent Orchestration

## Available Agents

Located in `~/.claude/agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring |
| architect | System design | Architectural decisions |
| code-reviewer | Code review | After writing code |
| security-reviewer | Security analysis | Before commits |
| build-error-resolver | Fix build errors | When build fails |
| refactor-cleaner | Dead code cleanup | Code maintenance |
| doc-updater | Documentation | Updating docs |

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Architectural decision - Use **architect** agent
4. Build failure - Use **build-error-resolver** agent

## Context Before Delegation (MANDATORY)

**NEVER spawn a subagent without first gathering context.** Subagents without context produce generic, wrong, or conflicting output.

Before delegating to ANY agent:
1. **Explore** the relevant codebase area (Glob/Grep/Read or Explore agent)
2. **Read full files** that the agent will need to understand
3. **Provide** specific file paths, function names, and code context in the prompt
4. **Describe** what exists, what needs to change, and why

A vague prompt like "fix the bug" is NEVER acceptable. Always include the full context.

## Validation Approach

Do NOT use test-driven agents. Instead:
1. Build the real system
2. Run in simulator or on device
3. Capture evidence (screenshots, logs)
4. Verify against expected behavior using `gate-validation-discipline`

Use skills: `functional-validation`, `gate-validation-discipline`

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of auth module
2. Agent 2: Performance review of cache system
3. Agent 3: Build verification across targets

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
