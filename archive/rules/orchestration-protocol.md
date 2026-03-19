# Orchestration Protocol

## Large Batch Operations

When sessions involve large batch operations (100+ files):
- Break work into numbered batches of 20-30 and checkpoint progress after each batch
- Always report batch N/M status
- Write checkpoint to `.session-state/checkpoint.json` after each batch
- If approaching context limits, stop and report remaining batches for continuation

## Observer/Memory Agent Efficiency

When running observer/memory agents alongside primary sessions:
- Keep observer prompts minimal to avoid 'Prompt is too long' errors
- Observer agents should record brief structured observations, not full transcripts
- Consolidate observer duties into periodic checkpoints rather than continuous monitoring

## Delegation Context (MANDATORY)

When spawning subagents via Task tool, **ALWAYS** include in prompt:

1. **Work Context Path**: The git root of the PRIMARY files being worked on
2. **Reports Path**: `{work_context}/plans/reports/` for that project
3. **Plans Path**: `{work_context}/plans/` for that project

**Example:**
```
Task prompt: "Fix parser bug.
Work context: /path/to/project-b
Reports: /path/to/project-b/plans/reports/
Plans: /path/to/project-b/plans/"
```

**Rule:** If CWD differs from work context (editing files in different project), use the **work context paths**, not CWD paths.

---

#### Sequential Chaining
Chain subagents when tasks have dependencies or require outputs from previous steps:
- **Planning → Implementation → Simplification → Testing → Review**: Use for feature development (tests verify simplified code)
- **Research → Design → Code → Documentation**: Use for new system components
- Each agent completes fully before the next begins
- Pass context and outputs between agents in the chain

#### Parallel Execution
Spawn multiple subagents simultaneously for independent tasks:
- **Code + Tests + Docs**: When implementing separate, non-conflicting components
- **Multiple Feature Branches**: Different agents working on isolated features
- **Cross-platform Development**: iOS and Android specific implementations
- **Careful Coordination**: Ensure no file conflicts or shared resource contention
- **Merge Strategy**: Plan integration points before parallel execution begins

---

## Agent Teams (Optional)

For multi-session parallel collaboration, activate the `/team` skill.
Not part of the default orchestration workflow. See `$HOME/.claude/skills/team/SKILL.md` for templates, decision criteria, and spawn instructions.
