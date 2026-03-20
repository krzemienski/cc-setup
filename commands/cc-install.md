---
name: cc-install
description: Deploy cc-setup configuration to this machine — rules, hooks, CLAUDE.md, settings, MCP configs, and register plugin
---

# CC Install

Full deploy of cc-setup to this machine.

## Usage

Run the install script:
```bash
cd ~/cc-setup && ./install.sh
```

Then register the plugin marketplace in Claude Code:
```
/plugin marketplace add ~/cc-setup
/plugin install cc-setup@cc-setup-marketplace
```

## What install.sh Deploys
- `~/.claude/rules/` — rule files (always-loaded context)
- `~/.claude/hooks/` — hook scripts (event handlers)
- `~/.claude/CLAUDE.md` — global instructions (merged with OMC block)
- `~/.claude/settings.json` — settings with hook registrations and secret injection
- `~/.claude/output-styles/` — output style presets
- MCP configs with API key injection from .env

## What the Plugin Delivers (auto-discovered)
- `agents/` — unique agent definitions
- `skills/` — cc-health, cc-sync, cc-index
- `commands/` — /cc-health, /cc-sync, /cc-install

## Prerequisites
- Copy `.env.template` to `.env` and fill in API keys
- Run `./install.sh` before registering the plugin
