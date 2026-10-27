# Auto-Claude Spec System Reference

The auto-claude spec system is a structured task management system embedded in
the repository. When it exists, it's the richest source of intent for each
worktree branch.

## Directory Structure

```
.auto-claude/
├── .env                    # Configuration (API tokens, model overrides, MCP servers)
├── project_index.json      # Project metadata (language, framework, services)
├── file_evolution.json     # File change history tracking
├── specs/                  # One directory per task/feature
│   ├── 001-feature-slug/
│   ├── 069-another-feature/
│   └── ...
├── roadmap/                # Feature roadmap and competitive analysis
│   ├── roadmap.json        # Master roadmap with phases and milestones
│   └── competitor_analysis.json
├── ideation/               # Ideas organized by category
│   ├── ideation.json       # Master ideation catalog
│   ├── ui_ux_improvements_ideas.json
│   ├── code_improvements_ideas.json
│   └── ...
├── worktrees/              # Active worktree task directories
│   └── tasks/
│       ├── 235-feature-name/
│       └── ...
└── file-timelines/         # Per-file change history
```

## Per-Spec Directory Contents

Each spec directory (`specs/{ID}-{slug}/`) contains:

### spec.md — Feature Specification
The source of truth for what the feature should do.

- Title and overview
- Rationale (why this exists)
- User stories and acceptance criteria
- Technical details and constraints

**How to use**: This defines your PASS criteria for validation. Every acceptance
criterion listed here must be verified against the real running system.

### requirements.json — Dependencies and Preconditions
```json
{
  "description": "Task description",
  "workflow_type": "simple | complex | multi-phase",
  "dependencies": ["other-spec-ids"],
  "preconditions": ["what must exist first"]
}
```

**How to use**: Drives merge ordering. If Branch B depends on Branch A's
changes, merge A first.

### context.json — Codebase Integration Points
```json
{
  "files_to_modify": ["path/to/file.swift"],
  "patterns": ["design patterns used"],
  "implementation_status": "pending | in_progress | done",
  "related_modules": ["ModuleName"]
}
```

**How to use**: Predicts conflict risk. Branches touching the same files
will conflict. Branches touching the same modules may have subtle integration
issues even without textual conflicts.

### implementation_plan.json — Execution Blueprint
```json
{
  "status": "pending | in_progress | done",
  "workflow_type": "simple | complex",
  "phases": [{"name": "...", "subtasks": [...]}],
  "verification_strategy": {
    "risk_level": "low | medium | high",
    "acceptance_criteria": ["..."],
    "verification_commands": ["xcodebuild ...", "curl ..."]
  },
  "qa_signoff": {"status": "pending | passed", "timestamp": "..."}
}
```

**How to use**: Assess completeness. Compare actual code changes against
planned subtasks. Identify which subtasks are done vs pending. Use
`verification_commands` as starting points for validation.

### task_metadata.json — Status and Classification
```json
{
  "sourceType": "ideation | roadmap | manual",
  "category": "ui_ux | feature | bug_fix | performance | security",
  "affectedFiles": ["path/to/file.swift"]
}
```

**How to use**: Quick triage. Category tells you what kind of validation
is needed (UI changes need screenshots, API changes need curl, etc.).

### task_logs.json — Execution History
Array of events: task started, subtask completed, errors encountered,
decisions made during implementation.

**How to use**: Understand what happened during development. Known errors
in the log may still be present. Decisions recorded here explain why code
looks the way it does.

### build-progress.txt — Build Output
Raw build output from the last attempt.

**How to use**: Quick check — does this branch compile? If the last build
failed, read the errors to understand what needs fixing.

### memory/ — Session Knowledge
```
memory/
├── build_commits.json        # Git commits for this task
├── codebase_map.json         # Files involved
├── attempt_history.json      # Per-subtask attempt tracking
└── session_insights/
    ├── session_001.json      # Per-session learnings
    └── session_002.json
```

**How to use**: The richest context. Session insights contain:
- `what_worked` — approaches that succeeded
- `what_failed` — approaches that didn't (don't repeat these)
- `recommendations_for_next_session` — the previous agent's advice to you
- `discoveries` — things learned about the codebase during implementation

Read ALL session insight files before attempting to complete or fix a branch.

### Other Files
- `init.sh` — Environment setup script (run to verify prerequisites)
- `MANUAL_TEST_PLAN.md` — QA test instructions (use as validation checklist)
- `qa_report.md` — Previous QA findings (known issues may persist)
- `.graphiti_state.json` — Memory graph state (if using Graphiti)

## When No Spec System Exists

Fall back to these sources, in priority order:

1. **PR descriptions** — `gh pr list --head <branch>` may show intent
2. **Branch name** — `feature/add-search` tells you what to expect
3. **Commit messages** — `git log main..<branch> --oneline` shows the story
4. **README/doc changes** — diffs to documentation often explain intent
5. **Code comments** — TODO/FIXME markers indicate incomplete work
6. **The diff itself** — last resort, but you can infer intent from changes

## Correlating Specs to Worktrees

The spec directory number/slug typically matches the branch name:
- Spec: `specs/235-cross-session-search/`
- Branch: `235-cross-session-search` or `auto-claude/235-cross-session-search`

Use `git worktree list` and `ls .auto-claude/specs/` to build the correlation
table. Flag any mismatches (specs without branches, branches without specs).
