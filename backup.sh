#!/bin/bash
set -euo pipefail

# backup.sh — Snapshot ~/.claude/ config into cc-setup repo (strips secrets)
# Backs up: rules, hooks, CLAUDE.md (non-OMC only), settings, output-styles, MCP
# Does NOT back up: agents or skills (managed by plugin at repo root)

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$HOME/.claude"

echo "=== CC Config Backup ==="

# Settings: strip env secrets
if [ -f "$SOURCE/settings.json" ]; then
    jq 'del(.env.ANTHROPIC_AUTH_TOKEN, .env.ANTHROPIC_BASE_URL)' "$SOURCE/settings.json" > "$REPO_DIR/global/settings.json.template"
    echo "  settings.json → template (secrets stripped)"
fi

# CLAUDE.md: extract only non-OMC content
if [ -f "$SOURCE/CLAUDE.md" ]; then
    if grep -q '<!-- OMC:START -->' "$SOURCE/CLAUDE.md" 2>/dev/null; then
        # Strip OMC block, keep only cc-setup's content
        sed '/<!-- OMC:START -->/,/<!-- OMC:END -->/d' "$SOURCE/CLAUDE.md" | sed '/^$/N;/^\n$/d' > "$REPO_DIR/global/CLAUDE.md"
        echo "  CLAUDE.md (OMC block stripped, cc-setup content only)"
    else
        cp "$SOURCE/CLAUDE.md" "$REPO_DIR/global/"
        echo "  CLAUDE.md (no OMC block found)"
    fi
fi

# Rules
rsync -a --delete --exclude='.DS_Store' "$SOURCE/rules/" "$REPO_DIR/global/rules/" 2>/dev/null && echo "  rules/ ($(ls "$SOURCE/rules/"*.md 2>/dev/null | wc -l | tr -d ' ') files)"

# Hooks (exclude logs, tests, DS_Store)
rsync -a --delete --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' --exclude='.DS_Store' "$SOURCE/hooks/" "$REPO_DIR/global/hooks/" 2>/dev/null && echo "  hooks/ ($(ls "$SOURCE/hooks/"*.{js,cjs} 2>/dev/null | wc -l | tr -d ' ') files)"

# Output styles
[ -d "$SOURCE/output-styles" ] && rsync -a --delete "$SOURCE/output-styles/" "$REPO_DIR/global/output-styles/" 2>/dev/null && echo "  output-styles/"

# MCP configs (strip API keys via shared lib)
source "$REPO_DIR/lib/secrets.sh"

if [ -f "$HOME/.mcp.json" ]; then
    strip_mcp_secrets "$HOME/.mcp.json" > "$REPO_DIR/mcp/mcp.json.template"
    echo "  .mcp.json → template (secrets stripped)"
fi

if [ -f "$HOME/.claude.json" ]; then
    jq '{mcpServers: .mcpServers}' "$HOME/.claude.json" | strip_claude_secrets /dev/stdin > "$REPO_DIR/mcp/claude.json.template"
    echo "  .claude.json → template (mcpServers only, secrets stripped)"
fi

echo ""
echo "Backup complete. Run 'cd $REPO_DIR && git status' to see changes."
echo "Note: agents/ and skills/ are managed directly at repo root (plugin components)."
