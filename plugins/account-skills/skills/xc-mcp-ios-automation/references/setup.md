# XC-MCP Setup Guide

## Prerequisites

- **macOS** with Xcode 15+ and command-line tools
- **Node.js 18+** for npm/npx
- **IDB** (optional) for UI automation on physical devices

### Install Prerequisites

```bash
# Xcode command line tools
xcode-select --install

# IDB (optional)
brew install idb-companion
pip3 install fb-idb
```

## MCP Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp"],
      "cwd": "/path/to/your/ios/project"
    }
  }
}
```

### Claude Code (Minimal Mode)

Use `--mini` for 97% token reduction:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--mini"]
    }
  }
}
```

### Build-Only Mode

For workflows without UI automation:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--build-only"]
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `XCODE_CLI_MCP_TIMEOUT` | 300 | Operation timeout (seconds) |
| `XCODE_CLI_MCP_LOG_LEVEL` | info | debug, info, warn, error |
| `XC_MCP_DEFER_LOADING` | true | Set false to load all tools upfront |

## Verification

```typescript
simctl-health-check({})
simctl-list({ deviceType: "iPhone", availability: "available" })
rtfm({ categoryName: "build" })
```

## Troubleshooting

**Xcode not found**: `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`

**Simulator unavailable**: Download runtimes in Xcode → Settings → Platforms

**Token overflow**: Use `--mini` flag and progressive disclosure

**IDB errors**: `killall idb_companion && idb_companion --udid <udid>`
