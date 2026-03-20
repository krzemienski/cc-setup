# Claude Code — Operating Manual

## Philosophy
- Functional validation only. NEVER mock, stub, or write test files.
- Skill-first. ALWAYS check skills before any work.
- Plan before execute. Think before coding.
- Evidence before completion. Prove it works.
- YAGNI / KISS / DRY.

## NEVER
- find/fd in Bash for code search. Use lsp_workspace_symbols > ast_grep > Glob > Grep.
- Mock, stub, or write test files. Build and run the real system.
- Spawn subagent without context (file paths, function names, code).

## Workflow
1. DISCOVER: lsp_workspace_symbols > ast_grep_search > Glob > Grep
2. PLAN: /everything-claude-code:plan or /oh-my-claudecode:ralplan
3. EXECUTE: /oh-my-claudecode:ralph or /oh-my-claudecode:team
4. REVIEW: code-reviewer agent
5. VALIDATE: /functional-validation → build + run + screenshot
6. REFLECT: /reflexion:reflect
7. COMMIT: Conventional format, no AI attribution

## Batch Operations
>20 files: chunk 20, checkpoint .claude/checkpoints/ after each batch.

## Context Budget
Per-message hooks inject ~15 lines (optimized from ~50). Use /compact when heavy.
NEVER run parallel observer/memory agents.

## Config
Repo: ~/cc-setup | Backup: backup.sh | Restore: restore.sh | Health: health.sh
