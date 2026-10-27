# XC-MCP Best Practices

## Accessibility-First Philosophy

XC-MCP promotes accessibility-first automation because it:

1. **Encourages better apps** — Developers building accessible UIs benefit all users (screen readers, voice control, assistive technologies)
2. **Enables precise AI interaction** — Semantic element discovery via accessibility tree vs visual guesswork from screenshots
3. **Improves efficiency** — 3-4x faster execution, 3-4x cheaper token cost
4. **Reduces energy usage** — Skip computationally expensive image processing

## Decision Framework

### ALWAYS Check Accessibility First

```javascript
accessibility-quality-check({ screenContext: "ScreenName" })
```

Returns one of:
- `rich` (>3 tappable elements) → Use accessibility tools
- `moderate` (2-3 elements) → Use accessibility tools
- `minimal` (≤1 element) → Fall back to screenshot

### Decision Branch Pattern

```javascript
const { quality } = await accessibility-quality-check({ screenContext: "LoginScreen" })

if (quality === "rich" || quality === "moderate") {
  // PREFERRED: Use semantic search
  const element = await idb-ui-find-element({ query: "email" })
  await idb-ui-tap({ x: element.centerX, y: element.centerY })
} else {
  // LAST RESORT: Fall back to screenshot
  const screenshot = await screenshot({ screenName: "LoginScreen" })
  // Analyze visually...
}
```

## Performance Comparison

| Approach | Tokens | Latency | When to Use |
|----------|--------|---------|-------------|
| Accessibility Tree | ~50 | ~120ms | Rich/Moderate UIs (>1 tappable element) |
| Screenshot Analysis | ~170 | ~2000ms | Minimal UIs only (≤1 tappable element) |
| **Efficiency Gain** | **3.4x cheaper** | **16x faster** | When accessibility sufficient |

## Progressive Disclosure

### Never Request Full Data Upfront

❌ **Wrong:** Request full build logs immediately
✅ **Right:** Get summary, then drill down if needed

### Cache ID Pattern

```javascript
// Step 1: Get summary
const buildResult = await xcodebuild-build({ scheme: "App" })
// Returns: { buildId: "build-abc", success: true, summary: {...} }

// Step 2: Only get details when debugging
if (!buildResult.success) {
  await xcodebuild-get-details({
    buildId: buildResult.buildId,
    detailType: "errors-only"
  })
}
```

### Simulator List Pattern

```javascript
// Step 1: Get summary (2k tokens vs 57k raw)
const { cacheId, quickAccess } = await simctl-list({ deviceType: "iPhone" })

// Step 2: Use quickAccess for booted/recent devices
// Only drill down if needed
if (needMoreDevices) {
  await simctl-get-details({ cacheId, detailType: "available-only" })
}
```

## Auto-Detection Patterns

### Let UDID Auto-Detect

❌ **Wrong:**
```javascript
// Prompting user for UDID
"What simulator UDID do you want to use?"
```

✅ **Right:**
```javascript
// Auto-detect booted simulator
simctl-app({ operation: "install", appPath: "./App.app" })
// deviceId defaults to "booted"
```

### Smart Defaults

XC-MCP provides intelligent defaults:
- `deviceId`: defaults to "booted"
- `configuration`: defaults to "Debug"
- `availability`: defaults to "available"
- `concise`: defaults to true

## Semantic Context

Include context parameters for better tracking:

```javascript
// Screenshots with semantic naming
screenshot({
  appName: "MyApp",
  screenName: "LoginScreen",
  state: "Empty"
})
// Generates: MyApp_LoginScreen_Empty_2025-01-24.png

// Push notifications with test context
simctl-push({
  bundleId: "com.example.app",
  payload: { aps: { alert: "Test" } },
  testName: "notification-test",
  expectedBehavior: "show banner"
})
```

## Error Handling

### Check Health First

```javascript
// Validate environment before operations
const health = await simctl-health-check({})
if (!health.xcodeInstalled) {
  throw new Error("Xcode not installed")
}
```

### Structured Error Responses

XC-MCP returns McpError with:
- Error code (validation, execution, timeout)
- Human-readable message
- Troubleshooting suggestions

## Operation Enums

### Use Routers Instead of Individual Tools

❌ **Wrong (old pattern):**
```javascript
simctl-boot({ deviceId: "..." })
simctl-shutdown({ deviceId: "..." })
```

✅ **Right (V2.0+ pattern):**
```javascript
simctl-device({ operation: "boot", deviceId: "..." })
simctl-device({ operation: "shutdown", deviceId: "..." })
```

### Available Routers

| Router | Operations |
|--------|------------|
| `simctl-device` | boot, shutdown, create, delete, erase, clone, rename |
| `simctl-app` | install, uninstall, launch, terminate |
| `idb-app` | install, uninstall, launch, terminate |
| `cache` | get-stats, get-config, set-config, clear |
| `persistence` | enable, disable, status |
| `idb-targets` | list, describe, connect, disconnect |

## Workflow Tools

### Use High-Level Abstractions

For common patterns, use workflow tools instead of chaining:

```javascript
// Instead of 3-4 separate calls:
workflow-tap-element({
  elementQuery: "Login",
  inputText: "user@example.com",
  verifyResult: true
})

// Instead of 5+ separate calls:
workflow-fresh-install({
  projectPath: "./App.xcworkspace",
  scheme: "App",
  eraseSimulator: true
})
```

## Token Budget

### Monitor Context Usage

V3.0 with deferred loading: ~0 tokens at startup
V3.0 with all tools loaded: ~18.7k tokens
Context window: 200k tokens

### Optimization Tips

1. Use `--mini` flag for Claude Code
2. Use `--build-only` for build-focused workflows
3. Use workflow tools for combined operations
4. Get summaries first, details on demand
5. Prefer accessibility over screenshots
