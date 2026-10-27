# XC-MCP Common Workflows

## Build and Run

```typescript
// 1. Discover project
xcodebuild-list({ projectPath: "./App.xcworkspace" })

// 2. List and boot simulator
simctl-list({ deviceType: "iPhone", availability: "available" })
simctl-device({ operation: "boot", deviceId: "UDID" })

// 3. Build
xcodebuild-build({
  projectPath: "./App.xcworkspace",
  scheme: "App",
  configuration: "Debug"
})

// 4. Install and launch
simctl-app({ operation: "install", deviceId: "booted", appPath: "./build/App.app" })
simctl-app({ operation: "launch", deviceId: "booted", bundleId: "com.example.App" })
```

---

## UI Test Automation (Accessibility-First)

```typescript
// 1. Always check accessibility first
accessibility-quality-check({ screenContext: "LoginScreen" })

// 2. Rich quality → semantic search
idb-ui-find-element({ query: "email" })
idb-ui-tap({ x: 187, y: 150 })
idb-ui-input({ operation: "text", text: "user@example.com" })

idb-ui-find-element({ query: "password" })
idb-ui-tap({ x: 187, y: 220 })
idb-ui-input({ operation: "text", text: "secretPassword123" })

idb-ui-find-element({ query: "login" })
idb-ui-tap({ x: 187, y: 350 })

// 3. Verify with screenshot at end
screenshot({ screenName: "HomeScreen", state: "LoggedIn" })
```

### Simplified with Workflow Tool

```typescript
workflow-tap-element({ elementQuery: "email", inputText: "user@example.com" })
workflow-tap-element({ elementQuery: "password", inputText: "secretPassword123" })
workflow-tap-element({ elementQuery: "login", verifyResult: true })
```

---

## Clean Build Testing

```typescript
// Using workflow tool
workflow-fresh-install({
  projectPath: "./App.xcworkspace",
  scheme: "App",
  eraseSimulator: true,
  launchArguments: ["--resetData"]
})

// Manual approach
simctl-device({ operation: "shutdown", deviceId: "all" })
simctl-device({ operation: "erase", deviceId: "UDID" })
simctl-device({ operation: "boot", deviceId: "UDID" })
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })
simctl-app({ operation: "install", appPath: "./path/to/App.app" })
simctl-app({ operation: "launch", bundleId: "com.example.App" })
```

---

## CI/CD Integration

```typescript
// 1. Health check
simctl-health-check({})

// 2. Create test simulator
simctl-device({
  operation: "create",
  name: "CI-Test-iPhone",
  deviceType: "iPhone 15 Pro",
  runtime: "iOS 17.0"
})

// 3. Boot
simctl-device({ operation: "boot", deviceId: "NEW_UDID" })

// 4. Build
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App", configuration: "Release" })

// 5. Run tests
xcodebuild-test({ projectPath: "./App.xcworkspace", scheme: "AppTests" })

// 6. Get failures
xcodebuild-get-details({ buildId: testResult.testId, detailType: "errors-only" })

// 7. Cleanup
simctl-device({ operation: "delete", deviceId: "NEW_UDID" })
```

---

## Debug Build Failures

```typescript
// 1. Build
const result = xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })

// 2. On failure, get errors
xcodebuild-get-details({ buildId: result.buildId, detailType: "errors-only" })

// 3. Get full context
xcodebuild-get-details({ buildId: result.buildId, detailType: "full-log", maxLines: 200 })

// 4. Clean and rebuild
xcodebuild-clean({ projectPath: "./App.xcworkspace", scheme: "App" })
cache({ operation: "clear", cacheType: "all" })
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })
```

---

## Form Filling

```typescript
// Check accessibility
accessibility-quality-check({ screenContext: "RegistrationForm" })

// Fill fields
const fields = [
  { query: "first name", value: "John" },
  { query: "last name", value: "Doe" },
  { query: "email", value: "john@example.com" }
];

for (const field of fields) {
  const element = idb-ui-find-element({ query: field.query })
  idb-ui-tap({ x: element.centerX, y: element.centerY })
  idb-ui-input({ operation: "text", text: field.value })
}

// Scroll if needed
idb-ui-gesture({ gesture: "swipe", startX: 187, startY: 600, endX: 187, endY: 200 })

// Submit
workflow-tap-element({ elementQuery: "submit", verifyResult: true })
```

---

## Performance Patterns

| Pattern | Tokens | Time | Use When |
|---------|--------|------|----------|
| `accessibility-quality-check` | ~30 | 80ms | Always first |
| `idb-ui-find-element` | ~40 | 120ms | Element search |
| `idb-ui-tap` | ~20 | 50ms | Tapping |
| `workflow-tap-element` | ~90 | 300ms | Combined ops |
| `screenshot` | ~170 | 2000ms | Verification only |

**Rule: Screenshots are 3-4x more expensive. Use only for verification.**
