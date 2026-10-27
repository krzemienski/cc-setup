# XC-MCP Tool Reference

All 29 tools organized by category with signatures.

## Build & Test (6 tools)

### xcodebuild-build
```typescript
xcodebuild-build({
  projectPath: string,      // Required
  scheme: string,           // Required
  configuration?: string,   // Default: "Debug"
  destination?: string,     // Auto-detected
  sdk?: string,
  derivedDataPath?: string
})
// Returns: { buildId, success, summary }
```

### xcodebuild-test
```typescript
xcodebuild-test({
  projectPath: string,
  scheme: string,
  destination?: string,
  testPlan?: string,
  onlyTesting?: string[],
  skipTesting?: string[]
})
// Returns: { testId, success, summary }
```

### xcodebuild-clean
```typescript
xcodebuild-clean({ projectPath: string, scheme: string, configuration?: string })
```

### xcodebuild-list
```typescript
xcodebuild-list({ projectPath: string, outputFormat?: "json"|"text" })
// Returns: { targets, schemes, configurations }
```

### xcodebuild-version
```typescript
xcodebuild-version({ outputFormat?: "json"|"text", sdk?: string })
```

### xcodebuild-get-details
```typescript
xcodebuild-get-details({
  buildId: string,
  detailType: "full-log"|"errors-only"|"warnings-only"|"summary"|"command"|"metadata",
  maxLines?: number  // Default: 100
})
```

## Simulator (4 tools)

### simctl-device (7 operations)
```typescript
simctl-device({
  operation: "boot"|"shutdown"|"create"|"delete"|"erase"|"clone"|"rename",
  deviceId?: string,        // UDID, "booted", or omit
  name?: string,            // For create
  deviceType?: string,      // For create: "iPhone 15 Pro"
  runtime?: string,         // For create: "iOS 17.0"
  newName?: string          // For clone/rename
})
```

### simctl-list
```typescript
simctl-list({
  concise?: boolean,        // Default: true
  deviceType?: string,      // Filter: "iPhone", "iPad"
  runtime?: string,
  availability?: "available"|"unavailable"|"all",
  outputFormat?: "json"|"text"
})
// Returns: { cacheId, summary, quickAccess }
```

### simctl-get-details
```typescript
simctl-get-details({
  cacheId: string,
  detailType: "full-list"|"devices-only"|"runtimes-only"|"available-only",
  maxDevices?: number  // Default: 20
})
```

### simctl-health-check
```typescript
simctl-health-check({})
```

## App Management

### simctl-app (4 operations)
```typescript
simctl-app({
  operation: "install"|"uninstall"|"launch"|"terminate",
  deviceId?: string,
  appPath?: string,
  bundleId?: string,
  launchArguments?: string[],
  environmentVariables?: Record<string, string>
})
```

### idb-app (4 operations)
Same as simctl-app but supports physical devices.

## UI Automation (6 tools)

### accessibility-quality-check
```typescript
accessibility-quality-check({ screenContext?: string })
// Returns: { quality: "rich"|"moderate"|"minimal", recommendation, elementCounts }
```

### idb-ui-find-element
```typescript
idb-ui-find-element({ query: string, udid?: string })
// Returns: { centerX, centerY, label, type, frame }
```

### idb-ui-tap
```typescript
idb-ui-tap({ x: number, y: number, udid?: string, duration?: number })
```

### idb-ui-input
```typescript
idb-ui-input({
  operation: "text"|"keycode",
  text?: string,
  keycode?: number,
  udid?: string
})
```

### idb-ui-gesture
```typescript
idb-ui-gesture({
  gesture: "swipe"|"pinch"|"rotate",
  startX?: number, startY?: number,
  endX?: number, endY?: number,
  duration?: number,
  scale?: number,   // For pinch
  angle?: number,   // For rotate
  udid?: string
})
```

### idb-ui-describe
```typescript
idb-ui-describe({
  operation: "all"|"point",
  x?: number, y?: number,
  udid?: string
})
// Returns: { uiTreeId, summary } for "all"
```

## I/O (2 tools)

### screenshot
```typescript
screenshot({
  screenName?: string,
  state?: string,
  udid?: string,
  size?: "full"|"half"
})
// Returns: { base64, semanticFilename, dimensions }
```

### simctl-io
```typescript
simctl-io({
  operation: "screenshot"|"recordVideo"|"stopRecording",
  deviceId?: string,
  outputPath?: string,
  type?: "png"|"jpeg"
})
```

## Workflow (2 tools)

### workflow-tap-element
```typescript
workflow-tap-element({
  elementQuery: string,
  screenContext?: string,
  inputText?: string,
  verifyResult?: boolean,
  udid?: string
})
// Cost: ~90 tokens, ~300ms
```

### workflow-fresh-install
```typescript
workflow-fresh-install({
  projectPath: string,
  scheme: string,
  simulatorUdid?: string,
  eraseSimulator?: boolean,
  configuration?: "Debug"|"Release",
  launchArguments?: string[],
  environmentVariables?: Record<string, string>
})
// Cost: ~200 tokens, ~20s
```

## Cache (2 routers)

### cache (4 operations)
```typescript
cache({
  operation: "get-stats"|"get-config"|"set-config"|"clear",
  cacheType?: "simulator"|"project"|"response"|"all"
})
```

### persistence (3 operations)
```typescript
persistence({
  operation: "enable"|"disable"|"status",
  cacheDir?: string,
  clearData?: boolean
})
```

## System (4 tools)

### rtfm
```typescript
rtfm({ categoryName: "build"|"simulator"|"app"|"idb"|"io"|"cache"|"workflow"|"system" })
rtfm({ toolName: "xcodebuild-build" })
```

### simctl-openurl
```typescript
simctl-openurl({ deviceId?: string, url: string })
```

### simctl-get-app-container
```typescript
simctl-get-app-container({
  deviceId?: string,
  bundleId: string,
  container?: "app"|"data"|"groups"
})
```

### simctl-push
```typescript
simctl-push({
  deviceId?: string,
  bundleId: string,
  payload: object,
  testName?: string,
  expectedBehavior?: string
})
```

### idb-targets (4 operations)
```typescript
idb-targets({
  operation: "list"|"describe"|"connect"|"disconnect",
  udid?: string
})
```
