#!/bin/bash
# health.sh — Verify Claude Code setup health (dual-delivery model)

echo "=== CC Health Check ==="

ERRORS=0
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

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

# cc-setup plugin check
echo ""
echo "CC-SETUP PLUGIN:"
if [ -f "$REPO_DIR/.claude-plugin/plugin.json" ]; then
    PLUGIN_NAME=$(jq -r '.name' "$REPO_DIR/.claude-plugin/plugin.json" 2>/dev/null)
    echo "  OK  plugin.json (name: $PLUGIN_NAME)"
else
    echo "  ERR plugin.json not found"
    ERRORS=$((ERRORS + 1))
fi
if [ -f "$REPO_DIR/.claude-plugin/marketplace.json" ]; then
    echo "  OK  marketplace.json"
else
    echo "  ERR marketplace.json not found"
    ERRORS=$((ERRORS + 1))
fi
# Plugin components
PLUGIN_AGENTS=$(ls "$REPO_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
PLUGIN_COMMANDS=$(ls "$REPO_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
PLUGIN_SKILLS=$(ls -d "$REPO_DIR/skills/"*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
echo "  Agents: $PLUGIN_AGENTS | Commands: $PLUGIN_COMMANDS | Skills: $PLUGIN_SKILLS"

# MCP servers
echo ""
echo "MCP SERVERS:"
echo "  .mcp.json: $(jq -r '.mcpServers | keys | length' ~/.mcp.json 2>/dev/null) servers"
echo "  .claude.json: $(jq -r '.mcpServers | keys | length' ~/.claude.json 2>/dev/null) servers"

# Rules
echo ""
echo "RULES: $(ls ~/.claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ') files"

# Agents (user-level — should only have cc-setup's 10 unique agents, not 25)
echo ""
USER_AGENTS=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "USER AGENTS: $USER_AGENTS files (plugin agents are separate)"
# Warn if stale agents are still present
STALE_CHECK=0
for agent in architect code-reviewer debugger planner security-reviewer; do
    [ -f "$HOME/.claude/agents/${agent}.md" ] && STALE_CHECK=$((STALE_CHECK + 1))
done
if [ $STALE_CHECK -gt 0 ]; then
    echo "  WARN: $STALE_CHECK stale agents found (covered by OMC/ECC). Run install.sh to clean."
fi

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

# CLAUDE.md ownership check
echo ""
echo "CLAUDE.MD:"
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
    TOTAL_LINES=$(wc -l < "$HOME/.claude/CLAUDE.md" | tr -d ' ')
    HAS_OMC="no"
    grep -q '<!-- OMC:START -->' "$HOME/.claude/CLAUDE.md" 2>/dev/null && HAS_OMC="yes"
    HAS_MANUAL="no"
    grep -q 'Operating Manual' "$HOME/.claude/CLAUDE.md" 2>/dev/null && HAS_MANUAL="yes"
    echo "  Lines: $TOTAL_LINES | OMC block: $HAS_OMC | CC-setup manual: $HAS_MANUAL"
else
    echo "  MISSING ~/.claude/CLAUDE.md"
    ERRORS=$((ERRORS + 1))
fi

# MCP JSON validation
echo ""
echo "MCP CONFIGS:"
for mcpfile in "$HOME/.mcp.json" "$HOME/.claude.json"; do
    fname=$(basename "$mcpfile")
    if [ -f "$mcpfile" ]; then
        if jq . "$mcpfile" > /dev/null 2>&1; then
            echo "  OK  $fname (valid JSON)"
        else
            echo "  ERR $fname (invalid JSON)"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  SKIP $fname (not found)"
    fi
done

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "=== HEALTHY ==="
else
    echo "=== $ERRORS ISSUES FOUND ==="
fi
