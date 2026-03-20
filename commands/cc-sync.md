---
name: cc-sync
description: Sync Claude Code config between ~/.claude/ and ~/cc-setup repo — backup, restore, diff, install
---

# CC Config Sync

Manage your Claude Code configuration via the ~/cc-setup git repo.

## Usage

Ask the user which direction they want:

### Backup (live → repo)
Snapshot current ~/.claude/ config into ~/cc-setup:
```bash
cd ~/cc-setup && ./backup.sh
```
Then review changes with `git diff` and offer to commit.

### Restore (repo → live)
Deploy ~/cc-setup config to ~/.claude/:
```bash
cd ~/cc-setup && ./restore.sh
```
Creates a safety backup before overwriting.

### Diff (compare)
Show what changed since last sync:
```bash
cd ~/cc-setup && ./diff.sh
```

### Install (fresh machine)
Full deploy from repo to ~/.claude/:
```bash
cd ~/cc-setup && ./install.sh
```

## Workflow
1. Ask which direction: backup (→ repo) or restore (→ live)
2. Run the appropriate script
3. If backup: show git diff and offer to commit
4. If restore: run health.sh to verify
