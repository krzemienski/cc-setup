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
