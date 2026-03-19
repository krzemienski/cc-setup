# cc-setup

Git-tracked source of truth for Claude Code configuration.

## Quick Start

```bash
# First time: copy .env.template, fill in secrets
cp .env.template .env
vi .env

# Deploy config to ~/.claude/
./install.sh

# Check everything works
./health.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Deploy repo config → ~/.claude/ (merge semantics) |
| `backup.sh` | Snapshot ~/.claude/ → repo (strips secrets) |
| `restore.sh` | Repo → ~/.claude/ (preserves local secrets) |
| `diff.sh` | Show what changed since last sync |
| `health.sh` | Verify hooks, plugins, MCP, agents all working |

## Structure

- `global/` — deploys to `~/.claude/` (rules, hooks, agents, CLAUDE.md)
- `mcp/` — deploys MCP configs (`~/.mcp.json`, `~/.claude.json`)
- `skills/` — custom skills (`cc-sync`, `cc-health`, `cc-index`)
- `projects/` — project-type templates (ios, web, python)
- `archive/` — archived artifacts (GSD agents, old rules, dead hooks)

## Secret Handling

Secrets live in `.env` (gitignored). Templates use `__PLACEHOLDER__` syntax.
`install.sh` replaces placeholders with `.env` values at deploy time.

## Workflow

```bash
# After making changes to CC config:
./backup.sh          # snapshot current state
git add -A && git commit -m "feat: description"

# On a new machine:
git clone <repo> ~/cc-setup
cp .env.template .env && vi .env
./install.sh

# Check what drifted:
./diff.sh
```
