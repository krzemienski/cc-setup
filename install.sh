#!/bin/bash
set -euo pipefail

# install.sh — Deploy cc-setup config to ~/.claude/
# Deploys: rules, hooks, CLAUDE.md (merge), settings.json (smart merge), output-styles, MCP configs
# Plugin handles: agents, skills, commands (auto-discovered via marketplace)
# Uses SMART MERGE by default (preserves user prefs, plugins, hooks). Use --clean for full overwrite.
#
# Settings.json merge strategy:
#   Template-wins: env, includeCoAuthoredBy, permissions (config intent from cc-setup)
#   User-wins:     model, effortLevel, alwaysThinkingEnabled, autoUpdatesChannel,
#                  skipDangerousModePermissionPrompt, teammateMode, semantic_search
#   Union-merge:   enabledPlugins, extraKnownMarketplaces, hooks, autoAllowedTools

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"
CLEAN_MODE=false
OS_TYPE="$(uname -s)"

[ "${1:-}" = "--clean" ] && CLEAN_MODE=true

echo "=== CC Config Install (${OS_TYPE}) ==="

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
BACKUP=""
if [ -d "$TARGET" ]; then
    BACKUP="/tmp/claude-install-backup-$(date +%Y%m%d-%H%M%S)"
    echo "  Backing up existing config to $BACKUP"
    rsync -a --ignore-errors "$TARGET/" "$BACKUP/" 2>/dev/null || cp -r "$TARGET" "$BACKUP" 2>/dev/null || true
fi

# Check for drift (merge mode only)
if [ -d "$TARGET" ] && ! $CLEAN_MODE; then
    echo ""
    echo "  Checking for local drift..."
    "$REPO_DIR/diff.sh" 2>/dev/null || true
    echo ""
fi

# --- Smart merge function for settings.json ---
# Merges template into existing settings preserving user preferences and doing
# union-merge on hooks, plugins, marketplaces, and autoAllowedTools.
smart_merge_settings() {
    local existing="$1"
    local template="$2"
    local output="$3"

    # Count pre-merge values for safety validation
    local pre_plugins pre_hooks pre_tools
    pre_plugins=$(jq '[.enabledPlugins // {} | keys[]] | length' "$existing")
    pre_hooks=$(jq '[.hooks // {} | to_entries[] | .value[] | .hooks[] | .command] | length' "$existing")
    pre_tools=$(jq '[.autoAllowedTools // [] | .[]] | length' "$existing")

    # Smart merge:
    # 1. Start with existing (preserves all user keys)
    # 2. Overwrite template-wins keys
    # 3. Union-merge object keys (enabledPlugins, extraKnownMarketplaces)
    # 4. Union-merge autoAllowedTools array
    # 5. Merge hooks by event type, then by matcher, dedup by command
    jq -s '
      # existing = .[0], template = .[1]
      .[0] as $existing | .[1] as $template |

      # Start with existing, overwrite template-wins scalars
      $existing
      | .env = $template.env
      | .includeCoAuthoredBy = $template.includeCoAuthoredBy
      | .permissions = $template.permissions

      # User-wins: keep existing value if set, otherwise use template default
      | .model = ($existing.model // $template.model)
      | .effortLevel = ($existing.effortLevel // $template.effortLevel)
      | .alwaysThinkingEnabled = ($existing.alwaysThinkingEnabled // $template.alwaysThinkingEnabled)
      | .autoUpdatesChannel = ($existing.autoUpdatesChannel // $template.autoUpdatesChannel)
      | .skipDangerousModePermissionPrompt = ($existing.skipDangerousModePermissionPrompt // $template.skipDangerousModePermissionPrompt)
      | .statusLine = ($existing.statusLine // $template.statusLine)

      # Union-merge enabledPlugins (additive)
      | .enabledPlugins = (($existing.enabledPlugins // {}) * ($template.enabledPlugins // {}))

      # Union-merge extraKnownMarketplaces (additive)
      | .extraKnownMarketplaces = (($existing.extraKnownMarketplaces // {}) * ($template.extraKnownMarketplaces // {}))

      # Union-merge autoAllowedTools (deduplicated)
      | .autoAllowedTools = ([$existing.autoAllowedTools // [], $template.autoAllowedTools // []] | add | unique)

      # Merge hooks: for each event type, combine matcher groups and deduplicate commands
      | .hooks = (
          ($existing.hooks // {} | keys) + ($template.hooks // {} | keys) | unique |
          map(. as $event |
            {
              ($event): (
                # Collect all matcher groups from both sources
                (($existing.hooks[$event] // []) + ($template.hooks[$event] // [])) |
                # Group by matcher string, merge hooks within same matcher
                group_by(.matcher) |
                map({
                  matcher: .[0].matcher,
                  hooks: ([.[] | .hooks[]] | unique_by(.command))
                })
              )
            }
          ) | add // {}
        )
    ' "$existing" "$template" > "$output"

    # Post-merge safety validation
    local post_plugins post_hooks post_tools
    post_plugins=$(jq '[.enabledPlugins // {} | keys[]] | length' "$output")
    post_hooks=$(jq '[.hooks // {} | to_entries[] | .value[] | .hooks[] | .command] | length' "$output")
    post_tools=$(jq '[.autoAllowedTools // [] | .[]] | length' "$output")

    if [ "$post_plugins" -lt "$pre_plugins" ] || [ "$post_hooks" -lt "$pre_hooks" ] || [ "$post_tools" -lt "$pre_tools" ]; then
        echo "  ERROR: Merge would lose data (plugins: ${pre_plugins}->${post_plugins}, hooks: ${pre_hooks}->${post_hooks}, tools: ${pre_tools}->${post_tools})"
        echo "  Aborting merge. Backup at: $BACKUP"
        cp "$BACKUP/settings.json" "$existing" 2>/dev/null || true
        return 1
    fi

    echo "  settings.json smart-merged (plugins: ${pre_plugins}->${post_plugins}, hooks: ${pre_hooks}->${post_hooks})"
}

# --- Process settings.json template ---
if [ -f "$REPO_DIR/global/settings.json.template" ]; then
    SETTINGS_CONTENT=$(cat "$REPO_DIR/global/settings.json.template")
    # Replace env placeholders
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_AUTH_TOKEN__|${ANTHROPIC_AUTH_TOKEN:-__ANTHROPIC_AUTH_TOKEN__}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_BASE_URL__|${ANTHROPIC_BASE_URL:-__ANTHROPIC_BASE_URL__}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_HAIKU_MODEL__|${ANTHROPIC_DEFAULT_HAIKU_MODEL:-claude-haiku-4-5-20251001}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_OPUS_MODEL__|${ANTHROPIC_DEFAULT_OPUS_MODEL:-claude-opus-4-6}|g")
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__ANTHROPIC_DEFAULT_SONNET_MODEL__|${ANTHROPIC_DEFAULT_SONNET_MODEL:-claude-sonnet-4-6}|g")
    # Replace __HOME__ placeholder with actual home directory
    SETTINGS_CONTENT=$(echo "$SETTINGS_CONTENT" | sed "s|__HOME__|$HOME|g")

    echo "$SETTINGS_CONTENT" > /tmp/cc-settings-template.json

    if [ -f "$TARGET/settings.json" ] && ! $CLEAN_MODE; then
        smart_merge_settings "$TARGET/settings.json" /tmp/cc-settings-template.json "$TARGET/settings.json.tmp"
        mv "$TARGET/settings.json.tmp" "$TARGET/settings.json"
    else
        if $CLEAN_MODE && [ -f "$TARGET/settings.json" ]; then
            echo "  WARNING: --clean replaces settings.json entirely."
            echo "  Your enabledPlugins, hooks, and preferences will be reset."
            echo "  Backup saved to: $BACKUP"
        fi
        mkdir -p "$TARGET"
        mv /tmp/cc-settings-template.json "$TARGET/settings.json"
        echo "  settings.json installed (clean)"
    fi
    rm -f /tmp/cc-settings-template.json
fi

# Deploy directories (rules, hooks, output-styles — NOT agents or skills)
mkdir -p "$TARGET"/{rules,hooks/lib,output-styles}
rsync -a --delete "$REPO_DIR/global/rules/" "$TARGET/rules/" && echo "  rules/ (synced, stale removed)"
rsync -a --exclude='.logs' --exclude='__tests__' --exclude='tests' --exclude='docs' "$REPO_DIR/global/hooks/" "$TARGET/hooks/" && echo "  hooks/"
[ -d "$REPO_DIR/global/output-styles" ] && rsync -a "$REPO_DIR/global/output-styles/" "$TARGET/output-styles/" && echo "  output-styles/"

# Deploy CLAUDE.md with OMC-aware merge logic
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

# Clean up stale agents that are now covered by OMC/ECC plugins
STALE_AGENTS=(architect build-error-resolver code-reviewer code-simplifier database-reviewer debugger doc-updater e2e-runner go-build-resolver go-reviewer planner python-reviewer refactor-cleaner security-reviewer tdd-guide)
CLEANED=0
for agent in "${STALE_AGENTS[@]}"; do
    if [ -f "$TARGET/agents/${agent}.md" ]; then
        rm -f "$TARGET/agents/${agent}.md"
        CLEANED=$((CLEANED + 1))
    fi
done
[ $CLEANED -gt 0 ] && echo "  Cleaned $CLEANED stale agents (now covered by OMC/ECC plugins)"

# Deploy MCP configs (with secret injection and platform gating)
source "$REPO_DIR/lib/secrets.sh"

if [ -f "$REPO_DIR/mcp/mcp.json.template" ]; then
    inject_secrets "$REPO_DIR/mcp/mcp.json.template" > "$HOME/.mcp.json"
    # Remove macOS-only servers on Linux
    if [ "$OS_TYPE" = "Linux" ]; then
        jq 'del(.mcpServers.tuist, .mcpServers.serena)' "$HOME/.mcp.json" > /tmp/mcp-platform.json && mv /tmp/mcp-platform.json "$HOME/.mcp.json"
        command -v uvx >/dev/null 2>&1 || jq 'del(.mcpServers.fetch)' "$HOME/.mcp.json" > /tmp/mcp-platform.json && mv /tmp/mcp-platform.json "$HOME/.mcp.json"
        echo "  .mcp.json (secrets injected, macOS servers removed)"
    else
        echo "  .mcp.json (secrets injected)"
    fi
    validate_json "$HOME/.mcp.json" || echo "  WARNING: .mcp.json may have unresolved placeholders"
fi

if [ -f "$REPO_DIR/mcp/claude.json.template" ]; then
    if [ -f "$HOME/.claude.json" ]; then
        TEMPLATE_MCPSERVERS=$(inject_secrets "$REPO_DIR/mcp/claude.json.template" | jq '.mcpServers')
        jq --argjson servers "$TEMPLATE_MCPSERVERS" '.mcpServers = (.mcpServers // {}) * $servers' "$HOME/.claude.json" > "$HOME/.claude.json.tmp"
        mv "$HOME/.claude.json.tmp" "$HOME/.claude.json"
        # Remove macOS-only servers on Linux
        if [ "$OS_TYPE" = "Linux" ]; then
            jq '.mcpServers |= del(.xcode, .pencil)' "$HOME/.claude.json" > /tmp/claude-platform.json && mv /tmp/claude-platform.json "$HOME/.claude.json"
        fi
        validate_json "$HOME/.claude.json" || echo "  WARNING: .claude.json may have issues"
        echo "  .claude.json merged (secrets injected, app state preserved)"
    else
        inject_secrets "$REPO_DIR/mcp/claude.json.template" > "$HOME/.claude.json"
        if [ "$OS_TYPE" = "Linux" ]; then
            jq '.mcpServers |= del(.xcode, .pencil)' "$HOME/.claude.json" > /tmp/claude-platform.json && mv /tmp/claude-platform.json "$HOME/.claude.json"
        fi
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
