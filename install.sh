#!/bin/bash
set -euo pipefail

# install.sh — Deploy cc-setup to ~/.claude/ on a fresh machine
# Uses MERGE semantics by default. Use --clean for full overwrite.

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"
CLEAN_MODE=false

[ "${1:-}" = "--clean" ] && CLEAN_MODE=true

echo "=== CC Config Install ==="

# Load secrets from .env
if [ -f "$REPO_DIR/.env" ]; then
    set -a
    source "$REPO_DIR/.env"
    set +a
    echo "  Loaded secrets from .env"
else
    echo "  WARNING: No .env file found. Copy .env.template to .env and fill in values."
    echo "  Continuing without secrets (placeholders will remain)."
fi

# Backup existing config if present
if [ -d "$TARGET" ]; then
    BACKUP="/tmp/claude-install-backup-$(date +%Y%m%d-%H%M%S)"
    echo "  Backing up existing config to $BACKUP"
    cp -r "$TARGET" "$BACKUP"
fi

# Check for drift
if [ -d "$TARGET" ] && ! $CLEAN_MODE; then
    echo ""
    echo "  Checking for local drift..."
    "$REPO_DIR/diff.sh" 2>/dev/null || true
    echo ""
fi

# Process settings.json template
if [ -f "$REPO_DIR/global/settings.json.template" ]; then
    SETTINGS_CONTENT=$(cat "$REPO_DIR/global/settings.json.template")
    # Replace placeholders with env values
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_AUTH_TOKEN__|${ANTHROPIC_AUTH_TOKEN:-__ANTHROPIC_AUTH_TOKEN__}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_BASE_URL__|${ANTHROPIC_BASE_URL:-__ANTHROPIC_BASE_URL__}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_HAIKU_MODEL__|${ANTHROPIC_DEFAULT_HAIKU_MODEL:-claude-haiku-4-5-20251001}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_OPUS_MODEL__|${ANTHROPIC_DEFAULT_OPUS_MODEL:-claude-opus-4-6}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_SONNET_MODEL__|${ANTHROPIC_DEFAULT_SONNET_MODEL:-claude-sonnet-4-6}|g")

    if [ -f "$TARGET/settings.json" ] && ! $CLEAN_MODE; then
        # Merge: preserve keys not in template
        echo "$SETTINGS_CONTENT" > /tmp/cc-settings-new.json
        jq -s '.[0] * .[1]' "$TARGET/settings.json" /tmp/cc-settings-new.json > "$TARGET/settings.json.tmp"
        mv "$TARGET/settings.json.tmp" "$TARGET/settings.json"
        rm /tmp/cc-settings-new.json
        echo "  settings.json merged"
    else
        mkdir -p "$TARGET"
        echo "$SETTINGS_CONTENT" > "$TARGET/settings.json"
        echo "  settings.json installed"
    fi
fi

# Deploy directories
mkdir -p "$TARGET"/{rules,hooks/lib,agents,output-styles}
rsync -a "$REPO_DIR/global/rules/" "$TARGET/rules/" && echo "  rules/"
rsync -a --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' "$REPO_DIR/global/hooks/" "$TARGET/hooks/" && echo "  hooks/"
rsync -a "$REPO_DIR/global/agents/" "$TARGET/agents/" && echo "  agents/"
[ -f "$REPO_DIR/global/CLAUDE.md" ] && cp "$REPO_DIR/global/CLAUDE.md" "$TARGET/" && echo "  CLAUDE.md"
[ -d "$REPO_DIR/global/output-styles" ] && rsync -a "$REPO_DIR/global/output-styles/" "$TARGET/output-styles/" && echo "  output-styles/"

# Deploy MCP configs
if [ -f "$REPO_DIR/mcp/mcp.json.template" ]; then
    cp "$REPO_DIR/mcp/mcp.json.template" "$HOME/.mcp.json"
    echo "  .mcp.json"
fi

echo ""
echo "Install complete. Running health check..."
"$REPO_DIR/health.sh"
