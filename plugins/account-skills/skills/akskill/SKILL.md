---
name: ak:skill
description: Marketing skill lifecycle manager — create, add references, optimize, fix, update, and plan new skills in the marketing kit. Use when building or improving marketing automation skills.
argument-hint: "[add|create|fix-logs|optimize|plan|update] [skill-name] [prompt]"
metadata:
  author: agentkit
  version: "1.0.0"
---

# Skill — Marketing Skill Manager

Create and manage marketing kit skills. Expert skill authoring at AI speed.

<args>$ARGUMENTS</args>

## When to Use

- Create a new marketing skill from scratch (URL, GitHub, or description)
- Add reference files or scripts to an existing skill
- Optimize an existing skill for token efficiency
- Fix a skill based on error logs
- Update a skill's content or references
- Plan (with user review) before creating or optimizing a skill

## Actions

| Action | Description | Reference |
|--------|-------------|-----------|
| `add <skill-name> <ref-prompt>` | Add reference files or scripts to skill | `references/add.md` |
| `create <prompt-or-url>` | Create a new skill from scratch | `references/create.md` |
| `fix-logs [skill-name]` | Fix skill based on `logs.txt` error output | `references/fix-logs.md` |
| `optimize <skill-name> [prompt]` | Plan + optimize an existing skill (with user approval) | `references/optimize.md` |
| `plan <skill-name> [prompt]` | Plan a new skill with user review before implementing | `references/plan.md` |
| `update <skill-name> [prompt]` | Update skill content or references directly | `references/update.md` |

## Workflow

1. Parse `--action` (first word of `$ARGUMENTS`) and remaining args
2. Route to corresponding `references/{action}.md`
3. Activate `skill-creator` + `claude-code` skills
4. Use `docs-seeker` for documentation lookup when building from URLs
5. Use `sequential-thinking` for complex multi-step skill designs

## Rules

- Operate in **project-scope** unless explicitly authorized for user-scope skill changes
- `SKILL.md` must be concise — progressive disclosure via `references/` files
- Skills are practical instructions, not documentation — teach Claude how to use tools
- Use the `ask_user` capability if arguments are missing or ambiguous

## Agents Used

- `researcher` — background research for new skills
- `skill-creator` — skill scaffolding and best practices

## Routing

1. Parse action from `$ARGUMENTS` (first word)
2. Load corresponding `references/{action}.md`
3. Execute with remaining arguments
