#!/bin/bash
# lib/secrets.sh — Shared secret management for cc-setup scripts
# Usage: source "$(dirname "$0")/lib/secrets.sh"

# Known MCP API key locations (4 keys across 2 files):
# mcp.json: .mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN
# mcp.json: .mcpServers["firecrawl-mcp"].env.FIRECRAWL_API_KEY
# mcp.json: .mcpServers.context7.headers.CONTEXT7_API_KEY
# claude.json: .mcpServers.stitch.headers["X-Goog-Api-Key"]

strip_mcp_secrets() {
    local file="$1"
    jq '
        .mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PERSONAL_ACCESS_TOKEN}" |
        .mcpServers["firecrawl-mcp"].env.FIRECRAWL_API_KEY = "${FIRECRAWL_API_KEY}" |
        .mcpServers.context7.headers.CONTEXT7_API_KEY = "${CONTEXT7_API_KEY}"
    ' "$file"
}

strip_claude_secrets() {
    local file="$1"
    jq '
        .mcpServers.stitch.headers["X-Goog-Api-Key"] = "${GOOGLE_API_KEY}"
    ' "$file"
}

inject_secrets() {
    local file="$1"
    sed -e "s|\${GITHUB_PERSONAL_ACCESS_TOKEN}|${GITHUB_PERSONAL_ACCESS_TOKEN:-}|g" \
        -e "s|\${FIRECRAWL_API_KEY}|${FIRECRAWL_API_KEY:-}|g" \
        -e "s|\${CONTEXT7_API_KEY}|${CONTEXT7_API_KEY:-}|g" \
        -e "s|\${GOOGLE_API_KEY}|${GOOGLE_API_KEY:-}|g" \
        "$file"
}

validate_json() {
    local file="$1"
    if ! jq . "$file" > /dev/null 2>&1; then
        echo "  ERR: $file is not valid JSON after processing"
        return 1
    fi
    return 0
}
