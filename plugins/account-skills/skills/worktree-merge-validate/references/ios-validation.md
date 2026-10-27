# iOS/macOS Validation Strategy

## When This Applies
Project contains `.xcodeproj`, `.xcworkspace`, or `Package.swift` with iOS/macOS targets.

## Build Verification

```bash
# iOS — use the project's dedicated simulator
xcodebuild -project <path>.xcodeproj -scheme <scheme> \
  -destination 'id=<SIMULATOR_UDID>' -quiet 2>&1 | tail -20

# macOS
xcodebuild -project <path>.xcodeproj -scheme <scheme> \
  -destination 'platform=macOS' -quiet 2>&1 | tail -20
```

**Read the CLAUDE.md or project docs** for the correct scheme name, simulator
UDID, and any build flags. Many projects have a dedicated simulator — using
the wrong one can interfere with other sessions.

## Simulator Management

### Booting
```bash
xcrun simctl boot <UDID>
sleep 5  # Wait for boot to complete
xcrun simctl list devices | grep <UDID>  # Verify booted
```

### Status Bar Override (for clean screenshots)
```bash
xcrun simctl status_bar <UDID> override \
  --time "9:41" --batteryState charged --batteryLevel 100 \
  --cellularMode active --cellularBars 4
```

### App Installation and Launch
```bash
# Terminate any existing instance first
xcrun simctl terminate <UDID> <BUNDLE_ID> 2>/dev/null

# Find the built app
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/ \
  -name "*.app" -path "*/Debug-iphonesimulator/*" | head -1)

# Install and launch
xcrun simctl install <UDID> "$APP_PATH"
xcrun simctl launch <UDID> <BUNDLE_ID>
sleep 3  # Wait for UI to settle
```

## Evidence Collection

### Screenshots
```bash
xcrun simctl io <UDID> screenshot /path/to/evidence/01-home-screen.png
```
- Number sequentially: `01-`, `02-`, `03-`
- Name descriptively: `01-home-screen.png`, `02-settings-tap.png`
- **ALWAYS read screenshots with the Read tool** — file existence is not verification

### Video Recording
```bash
xcrun simctl io <UDID> recordVideo --codec=h264 --force recording.mov &
RECORD_PID=$!

# ... perform actions ...

kill -SIGINT $RECORD_PID  # NEVER kill -9 — corrupts the file
wait $RECORD_PID          # Wait for finalization (1-3 seconds)
```

### Log Streaming
```bash
# Start BEFORE launching app
xcrun simctl spawn <UDID> log stream \
  --predicate "subsystem == \"<BUNDLE_ID>\"" \
  --info --debug --style compact \
  > live-logs.txt 2>/dev/null &

# After testing, also capture historical logs
xcrun simctl spawn <UDID> log show --last 120s \
  --predicate "subsystem == \"<BUNDLE_ID>\"" \
  --info --debug --style compact \
  > historical-logs.txt
```

**`--info --debug` is mandatory** — without them, most app logging is invisible.

## Navigation and Interaction

### Deep Links
```bash
xcrun simctl openurl <UDID> "yourscheme://path/to/screen"
sleep 3  # Wait for navigation
```
- UUIDs in URLs must be **lowercase**
- App must be foregrounded or OS shows a confirmation dialog

### Tap Coordinates
Use `idb_describe operation:all` for accessibility tree coordinates, then
`idb_tap`. Never guess pixel coordinates.

### Timing
- **3 seconds** minimum after any navigation or state change
- **5-10 seconds** for heavy data loads (1000+ items)
- If screenshot shows loading spinner → increase wait time

## Backend Integration

If the app connects to a backend:
```bash
# Verify backend is healthy BEFORE testing the app
curl -sf http://localhost:<PORT>/health
```

Start the backend if needed. Apps that can't reach their backend show
onboarding/error states, not the features you're validating.

## Multi-Simulator Usage (for parallel audits)

When running parallel surface audits, provision dedicated simulators:
```bash
xcrun simctl create "Audit-Agent-1" "iPhone 16 Pro" <runtime>
xcrun simctl create "Audit-Agent-2" "iPhone SE (3rd generation)" <runtime>
```

**Never use `booted` as UDID** in multi-session environments — it picks
a random booted simulator.

Clean up after:
```bash
xcrun simctl delete <UDID>
```

## iOS-Specific Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| Wrong DerivedData path | Can't find .app bundle | Use `find` in DerivedData, not `build/` |
| Uppercase UUIDs in deep links | Silent navigation failure | Always lowercase |
| Missing `--info --debug` on log stream | Zero useful log entries | Always include both flags |
| `kill -9` on video recording | Corrupt MOV file | Use `kill -SIGINT` + `wait` |
| Screenshot during loading | Evidence of loading, not feature | Increase sleep time |
| Multiple simulators booted | `booted` keyword picks wrong one | Always use explicit UDID |

## If `ios-validation-runner` Skill Is Available

Invoke it. It automates the SETUP→RECORD→ACT→COLLECT→VERIFY protocol
with proper evidence collection. You still must do Phase 5 (VERIFY) —
visually inspect every screenshot and write a verdict.
