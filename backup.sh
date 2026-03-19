#!/bin/bash
set -euo pipefail

# backup.sh — Snapshot ~/.claude/ config into cc-setup repo (strips secrets)

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$HOME/.claude"

echo "=== CC Config Backup ==="

# Settings: strip env secrets
if [ -f "$SOURCE/settings.json" ]; then
    jq 'del(.env.ANTHROPIC_AUTH_TOKEN, .env.ANTHROPIC_BASE_URL)' "$SOURCE/settings.json" > "$REPO_DIR/global/settings.json.template"
    echo "  settings.json → template (secrets stripped)"
fi

# CLAUDE.md
[ -f "$SOURCE/CLAUDE.md" ] && cp "$SOURCE/CLAUDE.md" "$REPO_DIR/global/" && echo "  CLAUDE.md"

# Rules
rsync -a --delete --exclude='.DS_Store' "$SOURCE/rules/" "$REPO_DIR/global/rules/" 2>/dev/null && echo "  rules/ ($(ls "$SOURCE/rules/"*.md 2>/dev/null | wc -l | tr -d ' ') files)"

# Hooks (exclude logs, tests, DS_Store)
rsync -a --delete --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' --exclude='.DS_Store' "$SOURCE/hooks/" "$REPO_DIR/global/hooks/" 2>/dev/null && echo "  hooks/ ($(ls "$SOURCE/hooks/"*.{js,cjs} 2>/dev/null | wc -l | tr -d ' ') files)"

# Agents
rsync -a --delete --exclude='.DS_Store' "$SOURCE/agents/" "$REPO_DIR/global/agents/" 2>/dev/null && echo "  agents/ ($(ls "$SOURCE/agents/"*.md 2>/dev/null | wc -l | tr -d ' ') files)"

# Output styles
[ -d "$SOURCE/output-styles" ] && rsync -a --delete "$SOURCE/output-styles/" "$REPO_DIR/global/output-styles/" 2>/dev/null && echo "  output-styles/"

# MCP configs (strip API keys)
if [ -f "$HOME/.mcp.json" ]; then
    cp "$HOME/.mcp.json" "$REPO_DIR/mcp/mcp.json.template"
    echo "  .mcp.json → template"
fi

if [ -f "$HOME/.claude.json" ]; then
    # Only extract mcpServers section
    jq '{mcpServers: .mcpServers}' "$HOME/.claude.json" > "$REPO_DIR/mcp/claude.json.template" 2>/dev/null
    echo "  .claude.json → template (mcpServers only)"
fi

echo ""
echo "Backup complete. Run 'cd $REPO_DIR && git status' to see changes."
