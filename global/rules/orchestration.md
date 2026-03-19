# Orchestration

## Model Selection
- Haiku: lightweight agents, frequent invocation, quick lookups
- Sonnet: standard implementation, orchestration, coding tasks
- Opus: architecture, deep analysis, maximum reasoning

## Sequential Thinking
Before implementing ANY non-trivial request, use sequential thinking to:
1. Break down the request into discrete steps
2. Identify ambiguities and assumptions
3. Plan the approach before writing code
4. Consider edge cases and failure modes

## Delegation Rules
- NEVER spawn subagent without context (file paths, function names, code)
- Include work context path, reports path, plans path in every prompt
- Use parallel agents for 2+ independent tasks
- Use sequential chains for dependent tasks

## Batch Operations (>20 files)
1. Count files with Glob (not find), show 3 samples, confirm
2. Process max 20 per chunk
3. Checkpoint to .claude/checkpoints/<timestamp>-<slug>.json after each chunk
4. If context heavy: /compact, resume from checkpoint
5. Headless resume: `claude -p "Read checkpoint, process next 20, checkpoint"`

## Agent Teams
- Each teammate owns distinct files — no overlap
- Prefer git worktrees for parallel work
- Never force-push from teammate session
- Use SendMessage for peer DMs, broadcast only for critical blocks
- File ownership conflicts: STOP and escalate to lead
- Shutdown: approve unless mid-critical-operation
- Idle is normal — sending a message to idle teammate wakes them

## Context Budget
- Per-message hooks inject ~15 lines (optimized from ~50)
- Use /compact when context feels heavy
- NEVER run parallel observer/memory agents — use claude-mem instead
- For large batch ops, checkpoint and start fresh sessions
