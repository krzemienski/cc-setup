---
name: skill-stocktake
description: Audit all skills and commands across installed plugins for quality. Supports Quick Scan (changed skills only) and Full Stocktake modes with per-skill pass/fail verdicts.
triggers:
  - "stocktake"
  - "audit skills"
  - "skill quality"
  - "check skills"
---

# skill-stocktake

Audits all Claude skills across global and plugin paths. Two modes: Quick Scan (changed skills only) and Full Stocktake (complete review). Outputs a summary report with verdicts per skill.

## Scope

| Path | Description |
|------|-------------|
| `~/.claude/skills/` | Global skills |
| `~/.claude/plugins/*/skills/` | Plugin skills |
| `{cwd}/.claude/skills/` | Project skills (if present) |
| `{cwd}/skills/` | Plugin source skills (if present) |

List found paths at the start of Phase 1.

## Modes

| Mode | Trigger | Duration |
|------|---------|---------|
| Quick Scan | `results.json` exists | 5–10 min |
| Full Stocktake | No `results.json`, or `full` arg | 20–30 min |

Results cache: `~/.claude/skills/skill-stocktake/results.json`

## Quick Scan Flow

1. Read `results.json`; collect mtimes of all skill files
2. Compare to cached mtimes — identify changed files
3. If none changed: report "No changes since last run." and stop
4. Re-evaluate only changed skills using Full Stocktake criteria
5. Merge with cached results; output diff only
6. Save updated `results.json`

## Full Stocktake Flow

### Phase 1 — Inventory

Enumerate all `SKILL.md` files under the scoped paths. For each, extract:
- Frontmatter: `name`, `description`, `triggers`
- File mtime (via `date -r <file> -u +%Y-%m-%dT%H:%M:%SZ`)

Print inventory table:

| Skill | Path | Last Modified |
|-------|------|---------------|

### Phase 2 — Quality Evaluation

Read each skill file and apply this checklist:

```
- [ ] YAML frontmatter present and valid (name, description, triggers)
- [ ] Description is specific and actionable (not generic)
- [ ] Triggers cover realistic invocation patterns
- [ ] Content is structured (headers, examples, or steps)
- [ ] No substantial overlap with another skill or CLAUDE.md rule
- [ ] Technical references are current (WebSearch if CLI flags / APIs present)
```

Verdict per skill:

| Verdict | Meaning |
|---------|---------|
| Pass | Well-formed, unique, actionable |
| Improve | Worth keeping; specific change needed |
| Update | Technical content outdated |
| Retire | Low value, stale, or fully covered elsewhere |
| Merge | Substantial overlap; name the target |

Evaluation is holistic AI judgment, not a numeric score. Reason must be specific:
- **Retire**: state the defect and what already covers it
- **Merge**: name the target and what to integrate
- **Improve**: name the section and the change needed

Process up to 20 skills per subagent (Task tool, explore agent, model: opus). Save `status: "in_progress"` after each chunk; resume from first unevaluated skill if interrupted.

### Phase 3 — Summary Report

Print counts (Pass / Improve / Update / Retire / Merge) then a table:

| Skill | Verdict | Reason |
|-------|---------|--------|

### Phase 4 — Actions

- **Retire / Merge**: show justification; confirm with user before any deletion
- **Improve / Update**: present specific change with rationale; user decides
- No file is modified or deleted without explicit confirmation

## Results Cache

`~/.claude/skills/skill-stocktake/results.json` — fields: `evaluated_at` (UTC via `date -u +%Y-%m-%dT%H:%M:%SZ`), `mode`, `batch_progress` (`total`, `evaluated`, `status`), `skills` (keyed by name: `path`, `verdict`, `reason`, `mtime`).
