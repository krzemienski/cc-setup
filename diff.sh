#!/bin/bash
# diff.sh — Compare deployed ~/.claude/ config against cc-setup repo
# Only compares what install.sh actually deploys: rules, hooks, CLAUDE.md, settings hooks, MCP

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== CC Config Diff ==="

HAS_DIFF=false

# Rules (install.sh syncs with --delete, so exact match expected)
RDIFF=$(diff -rq "$REPO_DIR/global/rules" "$HOME/.claude/rules" --exclude='.DS_Store' 2>/dev/null || true)
if [ -n "$RDIFF" ]; then
    echo "RULES:"
    echo "$RDIFF" | head -10
    HAS_DIFF=true
fi

# Hooks (install.sh adds but doesn't delete, so only check repo→deployed direction)
HDIFF=$(diff -rq "$REPO_DIR/global/hooks" "$HOME/.claude/hooks" --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' --exclude='.DS_Store' 2>/dev/null | grep "^Only in $REPO_DIR" || true)
if [ -n "$HDIFF" ]; then
    echo "HOOKS (missing from deployed):"
    echo "$HDIFF" | head -10
    HAS_DIFF=true
fi

# CLAUDE.md (expected to differ due to OMC block merge — report but don't flag as error)
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
    if ! grep -q 'Operating Manual' "$HOME/.claude/CLAUDE.md" 2>/dev/null; then
        echo "CLAUDE.md: missing Operating Manual section"
        HAS_DIFF=true
    fi
fi

# Settings.json — check template hooks are all present in deployed (subset check)
if [ -f "$HOME/.claude/settings.json" ]; then
    TEMPLATE_HOOKS=$(jq -r '[.hooks | to_entries[] | .value[] | .hooks[] | .command] | sort[]' "$REPO_DIR/global/settings.json.template" 2>/dev/null)
    DEPLOYED_HOOKS=$(jq -r '[.hooks | to_entries[] | .value[] | .hooks[] | .command] | sort[]' "$HOME/.claude/settings.json" 2>/dev/null)
    MISSING_HOOKS=$(comm -23 <(echo "$TEMPLATE_HOOKS") <(echo "$DEPLOYED_HOOKS"))
    if [ -n "$MISSING_HOOKS" ]; then
        echo "SETTINGS.JSON: missing template hooks:"
        echo "$MISSING_HOOKS" | head -5
        HAS_DIFF=true
    fi
fi

if ! $HAS_DIFF; then
    echo "  No differences found. Config is in sync."
fi

# MCP configs (compare after stripping secrets from live copy)
if [ -f "$REPO_DIR/lib/secrets.sh" ]; then
    source "$REPO_DIR/lib/secrets.sh"

    if [ -f "$HOME/.mcp.json" ]; then
        # Check template servers exist in deployed (subset check, ignores platform removals)
        TEMPLATE_SERVERS=$(jq -r '.mcpServers | keys[]' "$REPO_DIR/mcp/mcp.json.template" 2>/dev/null | sort)
        DEPLOYED_SERVERS=$(jq -r '.mcpServers | keys[]' "$HOME/.mcp.json" 2>/dev/null | sort)
        MISSING_SERVERS=$(comm -23 <(echo "$TEMPLATE_SERVERS") <(echo "$DEPLOYED_SERVERS"))
        # Filter out known platform-specific servers
        MISSING_SERVERS=$(echo "$MISSING_SERVERS" | grep -v -E "^(tuist|serena|fetch)$" || true)
        if [ -n "$MISSING_SERVERS" ]; then
            echo "MCP.JSON: missing servers: $MISSING_SERVERS"
            HAS_DIFF=true
        fi
    fi

    if [ -f "$HOME/.claude.json" ]; then
        TEMPLATE_CJ=$(jq -r '.mcpServers | keys[]' "$REPO_DIR/mcp/claude.json.template" 2>/dev/null | sort)
        DEPLOYED_CJ=$(jq -r '.mcpServers | keys[]' "$HOME/.claude.json" 2>/dev/null | sort)
        MISSING_CJ=$(comm -23 <(echo "$TEMPLATE_CJ") <(echo "$DEPLOYED_CJ"))
        MISSING_CJ=$(echo "$MISSING_CJ" | grep -v -E "^(xcode|pencil)$" || true)
        if [ -n "$MISSING_CJ" ]; then
            echo "CLAUDE.JSON: missing servers: $MISSING_CJ"
            HAS_DIFF=true
        fi
    fi
fi
