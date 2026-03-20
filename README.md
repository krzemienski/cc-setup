# cc-setup

Git-tracked Claude Code environment — delivered as a **plugin** (agents, skills, commands) + **install script** (rules, hooks, CLAUDE.md, settings, MCP).

## Quick Start

```bash
# 1. Clone and configure secrets
git clone <repo> ~/cc-setup
cp .env.template .env && vi .env

# 2. Deploy config components (rules, hooks, settings, MCP)
./install.sh

# 3. Register the plugin (in a Claude Code session)
/plugin marketplace add ~/cc-setup
/plugin install cc-setup@cc-setup-marketplace
```

## Dual Delivery Model

### Plugin (auto-discovered by Claude Code)
| Component | Count | Contents |
|-----------|-------|---------|
| Agents | 10 | brainstormer, docs-manager, fullstack-developer, git-manager, journal-writer, mcp-manager, project-manager, researcher, tester, ui-ux-designer |
| Skills | 3 | cc-health, cc-sync, cc-index |
| Commands | 3 | /cc-health, /cc-sync, /cc-install |

### install.sh (path-dependent config)
| Component | Why not plugin? |
|-----------|----------------|
| Rules (10 files) | Always-loaded context; not a plugin component type |
| Hooks (26 scripts) | `__dirname` traversals to `~/.claude/`; path-dependent |
| CLAUDE.md | OMC ownership; needs merge logic with OMC block |
| settings.json | Secret injection + hook registrations |
| Output styles (6) | Not a plugin component type |
| MCP configs (2) | Secret injection required |

## Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Deploy config → `~/.claude/` + clean stale agents + prompt for plugin registration |
| `backup.sh` | Snapshot `~/.claude/` → repo (strips secrets + OMC block from CLAUDE.md) |
| `restore.sh` | Repo → `~/.claude/` (preserves secrets, merges CLAUDE.md, cleans stale agents) |
| `diff.sh` | Show config drift since last sync |
| `health.sh` | Verify hooks, plugins, MCP, agents, CLAUDE.md, plugin manifests |

## Structure

```
cc-setup/
├── .claude-plugin/          # Plugin manifests
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Self-hosted marketplace
├── agents/                  # Plugin: 10 unique agents (auto-discovered)
├── commands/                # Plugin: /cc-health, /cc-sync, /cc-install
├── skills/                  # Plugin: cc-health, cc-sync, cc-index
├── global/                  # install.sh: deployed to ~/.claude/
│   ├── CLAUDE.md            # Operating Manual (~33 lines, no OMC block)
│   ├── settings.json.template
│   ├── rules/               # 10 rule files
│   ├── hooks/               # 26 hook scripts + lib/
│   └── output-styles/       # 6 coding level presets
├── mcp/                     # MCP config templates
├── lib/secrets.sh           # Shared secret management
├── projects/                # Project-type starter templates
├── docs/                    # System architecture diagrams
└── plans/                   # Planning artifacts
```

## Agent Dedup

15 agents removed from cc-setup — covered by OMC/ECC plugins:

| Removed | Covered By |
|---------|-----------|
| architect, planner | OMC (opus) |
| code-reviewer, security-reviewer, debugger, code-simplifier | OMC (sonnet/opus) |
| build-error-resolver, go-build-resolver, go-reviewer, python-reviewer | ECC |
| database-reviewer, doc-updater, e2e-runner, refactor-cleaner, tdd-guide | ECC |

## Secret Handling

Secrets live in `.env` (gitignored). Four API keys:

| Key | Used by |
|-----|---------|
| `FIRECRAWL_API_KEY` | firecrawl-mcp (web scraping) |
| `CONTEXT7_API_KEY` | context7 (library docs) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | github MCP server |
| `GOOGLE_API_KEY` | stitch (UI generation) |

## CLAUDE.md Merge Logic

`install.sh` and `restore.sh` preserve OMC's block (`<!-- OMC:START -->` to `<!-- OMC:END -->`). cc-setup only manages its own "Operating Manual" section (~33 lines). `backup.sh` strips the OMC block when backing up.

## Workflow

```bash
# After making changes to CC config:
./backup.sh          # snapshot current state (strips secrets + OMC block)
git add -A && git commit -m "feat: description"

# On a new machine:
git clone <repo> ~/cc-setup
cp .env.template .env && vi .env
./install.sh
# Then in Claude Code: /plugin marketplace add ~/cc-setup

# Check what drifted:
./diff.sh
```

## System Architecture

See [docs/system-architecture.md](docs/system-architecture.md) for:
- Context hierarchy flow (CLAUDE.md → rules → hooks → skills → agents)
- Delivery boundary map (plugin vs install.sh)
- Enforcement chain (6 hooks enforcing 6 principles)
- Component inventory with source attribution
