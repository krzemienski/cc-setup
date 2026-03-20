#!/bin/bash
set -euo pipefail

# restore.sh — Deploy cc-setup config to ~/.claude/ (preserves local secrets)
# Restores: rules, hooks, CLAUDE.md (merge), settings, output-styles, MCP
# Does NOT restore: agents or skills (managed by plugin at repo root)

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

echo "=== CC Config Restore ==="

# Check for local changes first
"$REPO_DIR/diff.sh" 2>/dev/null && echo ""

# Backup current config
BACKUP="$TARGET.restore-backup.$(date +%Y%m%d-%H%M%S)"
echo "Creating safety backup at $BACKUP..."
rsync -a --ignore-errors "$TARGET/" "$BACKUP/" 2>/dev/null || cp -r "$TARGET" "$BACKUP" 2>/dev/null || true

# Merge settings.json: preserve secrets from current, take structure from repo
if [ -f "$REPO_DIR/global/settings.json.template" ] && [ -f "$TARGET/settings.json" ]; then
    CURRENT_ENV=$(jq '.env' "$TARGET/settings.json")
    jq --argjson env "$CURRENT_ENV" '.env = $env' "$REPO_DIR/global/settings.json.template" > "$TARGET/settings.json.new"
    mv "$TARGET/settings.json.new" "$TARGET/settings.json"
    echo "  settings.json merged (secrets preserved)"
fi

# CLAUDE.md: merge with OMC-awareness
if [ -f "$REPO_DIR/global/CLAUDE.md" ]; then
    CC_CONTENT=$(cat "$REPO_DIR/global/CLAUDE.md")
    if [ -f "$TARGET/CLAUDE.md" ]; then
        if grep -q '<!-- OMC:START -->' "$TARGET/CLAUDE.md" 2>/dev/null; then
            OMC_BLOCK=$(sed -n '/<!-- OMC:START -->/,/<!-- OMC:END -->/p' "$TARGET/CLAUDE.md")
            printf '%s\n\n%s\n' "$OMC_BLOCK" "$CC_CONTENT" > "$TARGET/CLAUDE.md"
            echo "  CLAUDE.md merged (OMC block preserved)"
        else
            printf '%s\n\n%s\n' "$(cat "$TARGET/CLAUDE.md")" "$CC_CONTENT" > "$TARGET/CLAUDE.md"
            echo "  CLAUDE.md merged (no OMC block found)"
        fi
    else
        echo "$CC_CONTENT" > "$TARGET/CLAUDE.md"
        echo "  CLAUDE.md installed"
    fi
fi

# Rules, hooks: sync from repo (NOT agents — plugin handles those)
rsync -a --delete "$REPO_DIR/global/rules/" "$TARGET/rules/" && echo "  rules/"
rsync -a --delete --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' "$REPO_DIR/global/hooks/" "$TARGET/hooks/" && echo "  hooks/"

# Output styles
[ -d "$REPO_DIR/global/output-styles" ] && rsync -a --delete "$REPO_DIR/global/output-styles/" "$TARGET/output-styles/" && echo "  output-styles/"

# Clean stale agents (previously deployed by install.sh, now covered by OMC/ECC)
STALE_AGENTS=(architect build-error-resolver code-reviewer code-simplifier database-reviewer debugger doc-updater e2e-runner go-build-resolver go-reviewer planner python-reviewer refactor-cleaner security-reviewer tdd-guide)
CLEANED=0
for agent in "${STALE_AGENTS[@]}"; do
    if [ -f "$TARGET/agents/${agent}.md" ]; then
        rm -f "$TARGET/agents/${agent}.md"
        CLEANED=$((CLEANED + 1))
    fi
done
[ $CLEANED -gt 0 ] && echo "  Cleaned $CLEANED stale agents (now covered by OMC/ECC plugins)"

# MCP configs (with secret injection)
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
echo "Restore complete. Safety backup at: $BACKUP"
echo "Note: agents and skills are managed by the cc-setup plugin."
echo "  /plugin marketplace add ~/cc-setup"
echo "  /plugin install cc-setup@cc-setup-marketplace"
echo ""
echo "Run health.sh to verify."
