#!/bin/bash
set -euo pipefail

# install.sh — Deploy cc-setup config to ~/.claude/
# Deploys: rules, hooks, CLAUDE.md (merge), settings.json, output-styles, MCP configs
# Plugin handles: agents, skills, commands (auto-discovered via marketplace)
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
    rsync -a --ignore-errors "$TARGET/" "$BACKUP/" 2>/dev/null || cp -r "$TARGET" "$BACKUP" 2>/dev/null || true
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

# Deploy directories (rules, hooks, output-styles — NOT agents or skills)
mkdir -p "$TARGET"/{rules,hooks/lib,output-styles}
rsync -a "$REPO_DIR/global/rules/" "$TARGET/rules/" && echo "  rules/"
rsync -a --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' "$REPO_DIR/global/hooks/" "$TARGET/hooks/" && echo "  hooks/"
[ -d "$REPO_DIR/global/output-styles" ] && rsync -a "$REPO_DIR/global/output-styles/" "$TARGET/output-styles/" && echo "  output-styles/"

# Deploy CLAUDE.md with OMC-aware merge logic
if [ -f "$REPO_DIR/global/CLAUDE.md" ]; then
    CC_CONTENT=$(cat "$REPO_DIR/global/CLAUDE.md")
    if [ -f "$TARGET/CLAUDE.md" ]; then
        # Check if live CLAUDE.md has an OMC block
        if grep -q '<!-- OMC:START -->' "$TARGET/CLAUDE.md" 2>/dev/null; then
            # Extract OMC block (everything between OMC:START and OMC:END inclusive)
            OMC_BLOCK=$(sed -n '/<!-- OMC:START -->/,/<!-- OMC:END -->/p' "$TARGET/CLAUDE.md")
            # Write: OMC block + blank line + cc-setup content
            printf '%s\n\n%s\n' "$OMC_BLOCK" "$CC_CONTENT" > "$TARGET/CLAUDE.md"
            echo "  CLAUDE.md merged (OMC block preserved)"
        else
            # No OMC block — append cc-setup content below existing
            printf '%s\n\n%s\n' "$(cat "$TARGET/CLAUDE.md")" "$CC_CONTENT" > "$TARGET/CLAUDE.md"
            echo "  CLAUDE.md merged (no OMC block found)"
        fi
    else
        echo "$CC_CONTENT" > "$TARGET/CLAUDE.md"
        echo "  CLAUDE.md installed"
    fi
fi

# Clean up stale agents that are now covered by OMC/ECC plugins
# These were previously deployed by install.sh but are now redundant
STALE_AGENTS=(architect build-error-resolver code-reviewer code-simplifier database-reviewer debugger doc-updater e2e-runner go-build-resolver go-reviewer planner python-reviewer refactor-cleaner security-reviewer tdd-guide)
CLEANED=0
for agent in "${STALE_AGENTS[@]}"; do
    if [ -f "$TARGET/agents/${agent}.md" ]; then
        rm -f "$TARGET/agents/${agent}.md"
        CLEANED=$((CLEANED + 1))
    fi
done
[ $CLEANED -gt 0 ] && echo "  Cleaned $CLEANED stale agents (now covered by OMC/ECC plugins)"

# Deploy MCP configs (with secret injection)
source "$REPO_DIR/lib/secrets.sh"

if [ -f "$REPO_DIR/mcp/mcp.json.template" ]; then
    inject_secrets "$REPO_DIR/mcp/mcp.json.template" > "$HOME/.mcp.json"
    validate_json "$HOME/.mcp.json" || echo "  WARNING: .mcp.json may have unresolved placeholders"
    echo "  .mcp.json (secrets injected)"
fi

if [ -f "$REPO_DIR/mcp/claude.json.template" ]; then
    if [ -f "$HOME/.claude.json" ]; then
        TEMPLATE_MCPSERVERS=$(inject_secrets "$REPO_DIR/mcp/claude.json.template" | jq '.mcpServers')
        jq --argjson servers "$TEMPLATE_MCPSERVERS" '.mcpServers = (.mcpServers // {}) * $servers' "$HOME/.claude.json" > "$HOME/.claude.json.tmp"
        mv "$HOME/.claude.json.tmp" "$HOME/.claude.json"
        validate_json "$HOME/.claude.json" || echo "  WARNING: .claude.json may have issues"
        echo "  .claude.json merged (secrets injected, app state preserved)"
    else
        inject_secrets "$REPO_DIR/mcp/claude.json.template" > "$HOME/.claude.json"
        validate_json "$HOME/.claude.json" || echo "  WARNING: .claude.json may have unresolved placeholders"
        echo "  .claude.json installed (secrets injected)"
    fi
fi

echo ""
echo "=== Config deployed. Now register the plugin: ==="
echo "  /plugin marketplace add ~/cc-setup"
echo "  /plugin install cc-setup@cc-setup-marketplace"
echo ""
echo "Running health check..."
"$REPO_DIR/health.sh"
