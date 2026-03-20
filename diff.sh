#!/bin/bash
# diff.sh — Compare deployed ~/.claude/ config against cc-setup repo

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== CC Config Diff ==="

HAS_DIFF=false

# Rules
RDIFF=$(diff -rq "$REPO_DIR/global/rules" "$HOME/.claude/rules" --exclude='.DS_Store' 2>/dev/null || true)
if [ -n "$RDIFF" ]; then
    echo "RULES:"
    echo "$RDIFF" | head -10
    HAS_DIFF=true
fi

# Hooks
HDIFF=$(diff -rq "$REPO_DIR/global/hooks" "$HOME/.claude/hooks" --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' --exclude='.DS_Store' 2>/dev/null || true)
if [ -n "$HDIFF" ]; then
    echo "HOOKS:"
    echo "$HDIFF" | head -10
    HAS_DIFF=true
fi

# Agents
ADIFF=$(diff -rq "$REPO_DIR/global/agents" "$HOME/.claude/agents" --exclude='.DS_Store' 2>/dev/null || true)
if [ -n "$ADIFF" ]; then
    echo "AGENTS:"
    echo "$ADIFF" | head -10
    HAS_DIFF=true
fi

# CLAUDE.md
CDIFF=$(diff "$REPO_DIR/global/CLAUDE.md" "$HOME/.claude/CLAUDE.md" 2>/dev/null || true)
if [ -n "$CDIFF" ]; then
    echo "CLAUDE.md: differs"
    HAS_DIFF=true
fi

# Settings (compare without env/secrets)
SDIFF=$(diff <(jq 'del(.env)' "$REPO_DIR/global/settings.json.template" 2>/dev/null) <(jq 'del(.env)' "$HOME/.claude/settings.json" 2>/dev/null) 2>/dev/null || true)
if [ -n "$SDIFF" ]; then
    echo "SETTINGS.JSON: differs (excluding secrets)"
    HAS_DIFF=true
fi

if ! $HAS_DIFF; then
    echo "  No differences found. Config is in sync."
fi

# Skills
SKDIFF=$(diff -rq "$REPO_DIR/skills" "$HOME/.claude/skills" --exclude='.DS_Store' 2>/dev/null | grep -v "^Only in $HOME" || true)
if [ -n "$SKDIFF" ]; then
    echo "SKILLS:"
    echo "$SKDIFF" | head -10
    HAS_DIFF=true
fi

# MCP configs (compare after stripping secrets from live copy)
if [ -f "$REPO_DIR/lib/secrets.sh" ]; then
    source "$REPO_DIR/lib/secrets.sh"

    if [ -f "$HOME/.mcp.json" ]; then
        MCDIFF=$(diff <(jq -S . "$REPO_DIR/mcp/mcp.json.template" 2>/dev/null) <(strip_mcp_secrets "$HOME/.mcp.json" | jq -S . 2>/dev/null) 2>/dev/null || true)
        if [ -n "$MCDIFF" ]; then
            echo "MCP.JSON: differs (secrets excluded)"
            HAS_DIFF=true
        fi
    fi

    if [ -f "$HOME/.claude.json" ]; then
        CJDIFF=$(diff <(jq -S . "$REPO_DIR/mcp/claude.json.template" 2>/dev/null) <(jq '{mcpServers: .mcpServers}' "$HOME/.claude.json" | strip_claude_secrets /dev/stdin | jq -S . 2>/dev/null) 2>/dev/null || true)
        if [ -n "$CJDIFF" ]; then
            echo "CLAUDE.JSON (mcpServers): differs (secrets excluded)"
            HAS_DIFF=true
        fi
    fi
fi
