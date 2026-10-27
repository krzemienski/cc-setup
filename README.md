# claude-account — every plugin and skill on Nick's claude.ai account

Exported 2026-10-27 from claude.ai: 85 enabled plugins plus `account-skills` (232 personal skills).
Totals: 883 skills, 148 commands, 130 agents; 17 plugins ship hooks, 19 ship MCP servers.
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
