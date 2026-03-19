#!/bin/bash
set -euo pipefail

# restore.sh — Deploy cc-setup config to ~/.claude/ (preserves local secrets)

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

echo "=== CC Config Restore ==="

# Check for local changes first
"$REPO_DIR/diff.sh" 2>/dev/null && echo ""

# Backup current config
BACKUP="$TARGET.restore-backup.$(date +%Y%m%d-%H%M%S)"
echo "Creating safety backup at $BACKUP..."
cp -r "$TARGET" "$BACKUP"

# Merge settings.json: preserve secrets from current, take structure from repo
if [ -f "$REPO_DIR/global/settings.json.template" ] && [ -f "$TARGET/settings.json" ]; then
    # Extract current secrets
    CURRENT_ENV=$(jq '.env' "$TARGET/settings.json")
    # Take repo template, inject current secrets
    jq --argjson env "$CURRENT_ENV" '.env = $env' "$REPO_DIR/global/settings.json.template" > "$TARGET/settings.json.new"
    mv "$TARGET/settings.json.new" "$TARGET/settings.json"
    echo "  settings.json merged (secrets preserved)"
fi

# CLAUDE.md
[ -f "$REPO_DIR/global/CLAUDE.md" ] && cp "$REPO_DIR/global/CLAUDE.md" "$TARGET/" && echo "  CLAUDE.md"

# Rules, hooks, agents: sync from repo
rsync -a --delete "$REPO_DIR/global/rules/" "$TARGET/rules/" && echo "  rules/"
rsync -a --delete --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' "$REPO_DIR/global/hooks/" "$TARGET/hooks/" && echo "  hooks/"
rsync -a --delete "$REPO_DIR/global/agents/" "$TARGET/agents/" && echo "  agents/"

# Output styles
[ -d "$REPO_DIR/global/output-styles" ] && rsync -a --delete "$REPO_DIR/global/output-styles/" "$TARGET/output-styles/" && echo "  output-styles/"

echo ""
echo "Restore complete. Safety backup at: $BACKUP"
echo "Run health.sh to verify."
