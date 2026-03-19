#!/bin/bash
# health.sh — Verify Claude Code setup health

echo "=== CC Health Check ==="

ERRORS=0

# Hooks syntax check
echo ""
echo "HOOKS:"
for hook in ~/.claude/hooks/*.js ~/.claude/hooks/*.cjs; do
    [ -f "$hook" ] || continue
    fname=$(basename "$hook")
    if node --check "$hook" 2>/dev/null; then
        echo "  OK  $fname"
    else
        echo "  ERR $fname"
        ERRORS=$((ERRORS + 1))
    fi
done

# Plugins
echo ""
echo "PLUGINS (enabled):"
ENABLED=$(jq -r '.enabledPlugins | to_entries[] | select(.value == true) | .key' ~/.claude/settings.json 2>/dev/null | wc -l | tr -d ' ')
DISABLED=$(jq -r '.enabledPlugins | to_entries[] | select(.value == false) | .key' ~/.claude/settings.json 2>/dev/null | wc -l | tr -d ' ')
echo "  $ENABLED enabled, $DISABLED disabled"

# MCP servers
echo ""
echo "MCP SERVERS:"
echo "  .mcp.json: $(jq -r '.mcpServers | keys | length' ~/.mcp.json 2>/dev/null) servers"
echo "  .claude.json: $(jq -r '.mcpServers | keys | length' ~/.claude.json 2>/dev/null) servers"

# Rules
echo ""
echo "RULES: $(ls ~/.claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ') files"

# Agents
echo ""
echo "AGENTS: $(ls ~/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ') files"

# Empty hook matchers
echo ""
EMPTY=$(jq '[.hooks | to_entries[] | .value[] | select(.hooks | length == 0)] | length' ~/.claude/settings.json 2>/dev/null)
if [ "$EMPTY" -gt 0 ] 2>/dev/null; then
    echo "WARNING: $EMPTY empty hook matcher groups in settings.json"
    ERRORS=$((ERRORS + 1))
else
    echo "No empty hook matchers."
fi

# Settings valid JSON
echo ""
if node -e "JSON.parse(require('fs').readFileSync('$HOME/.claude/settings.json'))" 2>/dev/null; then
    echo "settings.json: valid JSON"
else
    echo "settings.json: INVALID JSON"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "=== HEALTHY ==="
else
    echo "=== $ERRORS ISSUES FOUND ==="
fi
