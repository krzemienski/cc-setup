---
name: xc-mcp-ios-automation
description: >
  Production-grade iOS development automation using the XC-MCP server for Xcode, iOS Simulator, and UI testing workflows. Use when working with iOS apps, Xcode projects, iOS simulators, Swift/SwiftUI development, building/testing iOS applications, UI automation, or interacting with any .xcodeproj/.xcworkspace files. Triggers on: iOS development, Xcode builds, simulator management, UI testing, accessibility automation, app installation, push notification testing, or any task involving Apple development tools.
---

# XC-MCP iOS Automation Skill

Production-grade MCP server for Xcode workflows optimized for AI agents with accessibility-first iOS automation.

## MCP Server Requirement

**XC-MCP must be configured in the MCP client.** Add to MCP configuration:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp"]
    }
  }
}
```

For Claude Code (use `--mini` flag for reduced context):
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

## Core Workflow Patterns

### 1. Tool Discovery (ALWAYS START HERE)

```javascript
// Browse tool categories
rtfm({ categoryName: "build" })

// Get comprehensive docs for specific tool
rtfm({ toolName: "xcodebuild-build" })

// Execute with discovered parameters
xcodebuild-build({ scheme: "MyApp", configuration: "Debug" })
```

### 2. Accessibility-First Automation (MANDATORY)

**ALWAYS assess accessibility before taking screenshots:**

```javascript
// Step 1: Quality check (30 tokens, 80ms)
accessibility-quality-check({ screenContext: "LoginScreen" })
// Returns: { quality: "rich" | "moderate" | "minimal" }

// Step 2: Decision branch
if (quality === "rich" || quality === "moderate") {
  // Use accessibility tree (50 tokens, 120ms) - PREFERRED
  idb-ui-find-element({ query: "email" })
  idb-ui-tap({ x: 200, y: 150 })
} else {
  // Fall back to screenshot (170 tokens, 2000ms) - LAST RESORT
  screenshot({ screenName: "LoginScreen" })
}
```

**Performance comparison:**
- Accessibility: 50 tokens, 120ms — 3-4x cheaper, 16x faster
- Screenshot: 170 tokens, 2000ms — only when accessibility insufficient

### 3. Progressive Disclosure Pattern

**Never request full logs upfront.** Use cache IDs:

```javascript
// Build returns summary + buildId
xcodebuild-build({ projectPath: "./MyApp.xcworkspace", scheme: "MyApp" })
// Returns: { buildId: "build-abc123", success: true, summary: {...} }

// Access full logs ONLY when debugging
xcodebuild-get-details({ buildId: "build-abc123", detailType: "full-log" })
```

## Workflow Tools (High-Level Abstractions)

### workflow-tap-element — Semantic UI Interaction

Combines quality check + element search + tap in one call:

```javascript
workflow-tap-element({
  elementQuery: "Login",
  screenContext: "LoginScreen",
  inputText: "user@example.com",  // optional: type after tap
  verifyResult: true              // optional: screenshot after
})
```

### workflow-fresh-install — Clean State Testing

Complete app refresh workflow:

```javascript
workflow-fresh-install({
  projectPath: "./MyApp.xcworkspace",
  scheme: "MyApp",
  eraseSimulator: true,           // wipe simulator data
  launchArguments: ["--resetData"]
})
```

## Tool Reference Summary

### Router Tools (6 consolidated operations)

| Tool | Operations | Use Case |
|------|------------|----------|
| `simctl-device` | boot, shutdown, create, delete, erase, clone, rename | Simulator lifecycle |
| `simctl-app` | install, uninstall, launch, terminate | App management |
| `idb-app` | install, uninstall, launch, terminate | IDB app operations |
| `cache` | get-stats, get-config, set-config, clear | Cache management |
| `persistence` | enable, disable, status | Persistence control |
| `idb-targets` | list, describe, connect, disconnect | Target discovery |

### Build & Test Tools

- `xcodebuild-build`: Build with smart defaults, returns buildId
- `xcodebuild-test`: Test with filtering and test plans
- `xcodebuild-clean`: Clean build artifacts
- `xcodebuild-list`: List targets/schemes (cached)
- `xcodebuild-version`: Xcode and SDK versions
- `xcodebuild-get-details`: Access cached build/test logs

### UI Automation Tools

- `idb-ui-find-element`: Semantic element search by label (PREFERRED)
- `idb-ui-tap`: Coordinate-based tapping
- `idb-ui-input`: Text input with keyboard control
- `idb-ui-gesture`: Swipes, pinches, rotations
- `idb-ui-describe`: Full accessibility tree
- `accessibility-quality-check`: Rapid UI assessment

### I/O & Discovery Tools

- `screenshot`: Vision-optimized base64 screenshots
- `simctl-io`: Screenshots and video recording
- `simctl-list`: Progressive disclosure simulator listing
- `simctl-get-details`: On-demand full simulator data
- `simctl-openurl`: Open URLs and deep links
- `simctl-push`: Simulate push notifications

## Best Practices

### DO

- **Let UDID auto-detect** — Don't prompt users for simulator UDIDs
- **Use semantic context** — Include `screenContext`, `appName`, `screenName` parameters
- **Prefer accessibility over screenshots** — Better for efficiency AND app quality
- **Use operation enums** — `simctl-device({ operation: "boot" })` instead of separate tools
- **Use workflow tools** — `workflow-tap-element` for common patterns
- **Get summaries first** — Use buildId/cacheId for progressive disclosure

### DON'T

- **Request full logs upfront** — Always get summaries first
- **Use screenshots as primary** — Check accessibility quality first
- **Skip the quality check** — `accessibility-quality-check` is fast (80ms)
- **Hardcode simulator UDIDs** — Let the system auto-detect

## Example: Complete Login Automation

```javascript
// 1. Quality check (30 tokens, 80ms)
accessibility-quality-check({ screenContext: "LoginScreen" })

// 2. Semantic element interaction (40 tokens each, 120ms)
idb-ui-find-element({ query: "email" })
idb-ui-tap({ x: 200, y: 150 })
idb-ui-input({ operation: "text", text: "user@example.com" })

idb-ui-find-element({ query: "password" })
idb-ui-tap({ x: 200, y: 250 })
idb-ui-input({ operation: "text", text: "password123" })

idb-ui-find-element({ query: "login" })
idb-ui-tap({ x: 200, y: 400 })

// 3. Verify with screenshot ONLY at end (170 tokens, 2000ms)
screenshot({ screenName: "HomeScreen", state: "LoggedIn" })

// Total: ~280 tokens, ~2400ms
// vs Screenshot-first: ~510 tokens, ~6000ms
```

## Reference Documentation

For detailed tool signatures and parameters, see:
- [references/tool-reference.md](references/tool-reference.md) — Complete tool signatures
- [references/workflows.md](references/workflows.md) — Common workflow patterns
- [references/best-practices.md](references/best-practices.md) — Accessibility-first philosophy
