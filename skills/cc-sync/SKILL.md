---
name: cc-sync
description: Sync Claude Code config between ~/.claude/ and ~/cc-setup repo
triggers:
  - "sync config"
  - "backup config"
  - "cc sync"
  - "cc setup"
  - "cc-sync"
---

# CC Config Sync

Manage your Claude Code configuration via the ~/cc-setup git repo.

## Commands

### Backup (default)
Snapshot current ~/.claude/ config into ~/cc-setup repo:
```bash
cd ~/cc-setup && ./backup.sh
```
Then review changes with `git diff` and commit.

### Restore
Deploy ~/cc-setup config to ~/.claude/:
```bash
cd ~/cc-setup && ./restore.sh
```
Creates a safety backup before overwriting.

### Diff
Show what changed since last sync:
```bash
cd ~/cc-setup && ./diff.sh
```

### Install (fresh machine)
Full deploy from repo to ~/.claude/:
```bash
cd ~/cc-setup && ./install.sh
```

## Usage
When the user says "sync config", "backup config", or "cc sync":
1. Ask which direction: backup (→ repo) or restore (→ live)
2. Run the appropriate script
3. If backup: show git diff and offer to commit
4. If restore: run health.sh to verify
