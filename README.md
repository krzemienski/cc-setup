# claude-account — every plugin and skill on Nick's claude.ai account

Exported 2026-10-27 from claude.ai: all 129 account plugins (enabled and disabled; 5 broken uploads excluded), `account-skills` (233 personal skills) and `nick-core`.
Totals: 131 plugins, 1004 skills, 209 commands, 137 agents; 24 plugins ship hooks, 33 ship MCP servers.
`inventory.json` lists every plugin with its skills, commands, agents, hooks and MCP flags.

## Install on a Mac

```bash
git clone -b account-sync https://github.com/krzemienski/cc-setup.git ~/claude-account-plugins
cd ~/claude-account-plugins
./install.sh --dry-run   # see the plan
./install.sh             # Claude Code + OMP + ~/.agents/skills
```

Plugins you already have from their original marketplace are skipped so hooks never run twice
(`--force-dupes` overrides). Configs are backed up to `.backups/<time>/`; nothing is deleted.

## Keep it synced

`./sync.sh` pulls this branch, lists plugins that changed (re-upload those to claude.ai), and re-runs the installer.
