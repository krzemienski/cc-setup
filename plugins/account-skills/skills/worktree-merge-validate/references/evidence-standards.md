# Evidence Standards Reference

Evidence is the foundation of every gate check in this workflow. This reference
defines what counts as evidence, how to collect it, and how to cite it.

## Full Evidence Directory Structure

```
worktree-merge-evidence/
├── manifest.json                    # Master evidence index (schema below)
├── phase-1-analysis/
│   ├── branch-reports/              # Per-worktree structured reports
│   │   ├── feature-auth.md
│   │   └── feature-dashboard.md
│   └── baseline/                    # Main branch baseline evidence
│       ├── build-output.txt         # Clean build log
│       ├── health-check.txt         # Backend health response
│       └── screenshots/             # Baseline UI state (if applicable)
│           └── 01-home-baseline.png
├── phase-4-merges/
│   ├── merge-001-feature-auth/
│   │   ├── build-output.txt         # Post-merge build log
│   │   ├── git-diff-stat.txt        # What changed
│   │   ├── conflict-resolution.md   # If conflicts, how resolved
│   │   └── validation/              # Post-merge validation evidence
│   │       ├── screenshots/         # iOS/web: numbered screenshots
│   │       ├── curl-responses/      # API: JSON response captures
│   │       ├── cli-outputs/         # CLI: stdout/stderr/exit code captures
│   │       ├── logs/                # App logs during validation
│   │       └── video/               # iOS: screen recordings (.mov)
│   └── merge-002-feature-dashboard/
│       └── ...
├── phase-5-audit/
│   ├── surface-inventory.md         # Complete surface list with status
│   ├── screenshots/                 # Full audit screenshot set
│   ├── curl-responses/              # Full API audit responses
│   ├── cli-outputs/                 # Full CLI audit outputs
│   ├── logs/                        # Session logs during audit
│   ├── video/                       # Screen recordings
│   ├── console-errors.txt           # Web: browser console errors
│   ├── network-failures.txt         # Web: failed network requests
│   └── VERDICT.md                   # Final audit verdict
├── phase-6-final/
│   ├── build-output.txt             # Final clean build
│   ├── health-check.txt             # Final health check
│   ├── git-log.txt                  # Merge history
│   ├── worktree-list.txt            # Should show main only
│   └── e2e-report.md               # Final e2e-validate report
└── remediation/
    ├── fix-001-broken-nav/
    │   ├── before.png               # Screenshot before fix
    │   ├── after.png                # Screenshot after fix
    │   ├── commit-hash.txt          # Git commit of the fix
    │   └── description.md           # What broke, why, how fixed
    └── fix-002-api-500/
        ├── before-response.json     # API response before fix
        ├── after-response.json      # API response after fix
        ├── commit-hash.txt
        └── description.md
```

## Evidence Manifest Schema

Maintain `worktree-merge-evidence/manifest.json` — the master index.

```json
{
  "project": "project-name",
  "started_at": "2026-03-21T10:00:00Z",
  "completed_at": "2026-03-21T14:30:00Z",
  "project_type": "ios | web | cli | api | fullstack",
  "worktrees_processed": 4,
  "merges_completed": 3,
  "merges_abandoned": 1,
  "issues_found": 7,
  "issues_fixed": 7,
  "evidence": [
    {
      "phase": 1,
      "type": "build_log",
      "path": "phase-1-analysis/baseline/build-output.txt",
      "description": "Main branch baseline build — zero errors",
      "timestamp": "2026-03-21T10:05:00Z"
    },
    {
      "phase": 4,
      "type": "screenshot",
      "path": "phase-4-merges/merge-001/validation/screenshots/01-login-screen.png",
      "description": "Login screen renders correctly after auth merge",
      "timestamp": "2026-03-21T11:15:00Z",
      "surface": "LoginView",
      "verdict": "pass"
    },
    {
      "phase": 4,
      "type": "curl_response",
      "path": "phase-4-merges/merge-001/validation/curl-responses/01-auth-endpoint.json",
      "description": "POST /api/v1/auth returns 200 with valid token",
      "timestamp": "2026-03-21T11:16:00Z",
      "surface": "POST /api/v1/auth",
      "verdict": "pass"
    },
    {
      "phase": 5,
      "type": "remediation",
      "path": "remediation/fix-001-broken-nav/",
      "description": "Navigation broken after dashboard merge",
      "commit": "abc1234",
      "verdict": "fixed"
    }
  ]
}
```

### Evidence Types

Valid `type` values: `build_log`, `screenshot`, `video`, `curl_response`,
`cli_output`, `log_capture`, `health_check`, `git_log`, `remediation`,
`report`, `surface_inventory`.

## Core Principle

**File existence is not evidence. You must READ the content.**

A screenshot file on disk proves you ran `xcrun simctl io ... screenshot`.
It does NOT prove the screen shows what you claim. You must open/read the
image and describe what it shows. Same for JSON responses, build logs, and
every other artifact.

## Evidence Hierarchy

From strongest to weakest:

| Strength | Type | Example |
|----------|------|---------|
| **Strongest** | Screenshot/recording you visually inspected | "Screenshot shows login form with email and password fields, submit button enabled" |
| **Strong** | Captured output you parsed | "curl response: `{"status": 200, "sessions": [{"id": "abc"}]}`" |
| **Moderate** | Build log with success line | "Build output ends with `BUILD SUCCEEDED`" |
| **Weak** | Command exit code | "Exit code 0" (doesn't tell you WHAT succeeded) |
| **Not evidence** | "It should work" | Speculation, no artifact |

## Naming Conventions

### Screenshots and Images
```
{NN}-{surface}-{state}.png
```
Examples:
- `01-home-screen-loaded.png`
- `02-settings-tap-open.png`
- `03-login-form-filled.png`
- `04-login-error-invalid-password.png`

### curl / API Responses
```
{NN}-{method}-{endpoint-slug}.json
```
Examples:
- `01-get-sessions-list.json`
- `02-post-sessions-create.json`
- `03-get-sessions-by-id.json`
- `04-delete-sessions-remove.json`

### CLI Outputs
```
{NN}-{command}-{scenario}.txt
```
Examples:
- `01-help-output.txt`
- `02-process-valid-input.txt`
- `03-process-invalid-input.txt`
- `04-list-empty-state.txt`

### Build Logs
```
build-output-{context}.txt
```
Examples:
- `build-output-baseline.txt`
- `build-output-post-merge-auth.txt`
- `build-output-after-fix-001.txt`

### Video Recordings
```
{NN}-{flow-description}.mov
```
Examples:
- `01-full-login-flow.mov`
- `02-settings-navigation.mov`

### Log Captures
```
{context}-logs.txt
```
Examples:
- `app-launch-logs.txt`
- `auth-flow-logs.txt`
- `crash-logs.txt`

## Per-Platform Collection Patterns

### iOS/macOS

```bash
EVIDENCE_DIR="worktree-merge-evidence/phase-4-merges/merge-001-feature-auth/validation"
mkdir -p "$EVIDENCE_DIR"/{screenshots,video,logs}

# Start log streaming BEFORE launching
xcrun simctl spawn <UDID> log stream \
  --predicate "subsystem == \"<BUNDLE_ID>\"" \
  --info --debug --style compact \
  > "$EVIDENCE_DIR/logs/app-logs.txt" 2>/dev/null &
LOG_PID=$!

# Start video recording
xcrun simctl io <UDID> recordVideo --codec=h264 --force \
  "$EVIDENCE_DIR/video/01-feature-validation.mov" &
VIDEO_PID=$!

# Launch app
xcrun simctl launch <UDID> <BUNDLE_ID>
sleep 3

# Capture screenshots at each validation point
xcrun simctl io <UDID> screenshot "$EVIDENCE_DIR/screenshots/01-app-launched.png"

# ... perform validation actions ...

xcrun simctl io <UDID> screenshot "$EVIDENCE_DIR/screenshots/02-feature-active.png"

# Stop recording (SIGINT, not SIGKILL)
kill -SIGINT $VIDEO_PID
wait $VIDEO_PID

# Stop log streaming
kill $LOG_PID

# Capture historical logs as backup
xcrun simctl spawn <UDID> log show --last 300s \
  --predicate "subsystem == \"<BUNDLE_ID>\"" \
  --info --debug --style compact \
  > "$EVIDENCE_DIR/logs/historical-logs.txt"
```

### Web Frontend

```bash
EVIDENCE_DIR="worktree-merge-evidence/phase-4-merges/merge-001/validation"
mkdir -p "$EVIDENCE_DIR"/{screenshots,logs}
```

```javascript
// validate.mjs
import { chromium } from 'playwright';

const evidence = './worktree-merge-evidence/phase-4-merges/merge-001/validation';
const errors = [];
const networkFailures = [];

const browser = await chromium.launch();
const page = await browser.newPage();

// Monitor console and network
page.on('console', msg => {
  if (msg.type() === 'error') errors.push(msg.text());
});
page.on('response', resp => {
  if (resp.status() >= 400) networkFailures.push(`${resp.status()} ${resp.url()}`);
});

// Validate
await page.goto('http://localhost:3000');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${evidence}/screenshots/01-home-loaded.png`, fullPage: true });

// ... more validation steps ...

// Write error logs
import { writeFileSync } from 'fs';
writeFileSync(`${evidence}/logs/console-errors.txt`, errors.join('\n') || 'No console errors');
writeFileSync(`${evidence}/logs/network-failures.txt`, networkFailures.join('\n') || 'No network failures');

await browser.close();
```

If `agent-browser` skill is available, use it instead of raw Playwright for
browser automation. It provides the same capabilities with additional
AI-guided interaction patterns.

### CLI

```bash
EVIDENCE_DIR="worktree-merge-evidence/phase-4-merges/merge-001/validation/cli-outputs"
mkdir -p "$EVIDENCE_DIR"

# Help output
./binary --help > "$EVIDENCE_DIR/01-help-output.txt" 2>&1
echo "EXIT_CODE=$?" >> "$EVIDENCE_DIR/01-help-output.txt"

# Valid operation
./binary process input.txt > "$EVIDENCE_DIR/02-process-valid.txt" 2>&1
echo "EXIT_CODE=$?" >> "$EVIDENCE_DIR/02-process-valid.txt"

# Error case
./binary process nonexistent.txt > "$EVIDENCE_DIR/03-process-error.txt" 2>&1
echo "EXIT_CODE=$?" >> "$EVIDENCE_DIR/03-process-error.txt"

# If CLI produces output files, capture those too
cp output.csv "$EVIDENCE_DIR/04-produced-output.csv"
wc -l "$EVIDENCE_DIR/04-produced-output.csv" >> "$EVIDENCE_DIR/04-produced-output-stats.txt"
```

### Backend API

```bash
EVIDENCE_DIR="worktree-merge-evidence/phase-4-merges/merge-001/validation/curl-responses"
BASE="http://localhost:9999"
mkdir -p "$EVIDENCE_DIR"

# Health check
curl -s -w "\nHTTP_STATUS=%{http_code}\nTIME=%{time_total}s\n" \
  "$BASE/health" | tee "$EVIDENCE_DIR/00-health-check.json"

# CRUD lifecycle
curl -s -w "\nHTTP_STATUS=%{http_code}\n" \
  "$BASE/api/v1/sessions" | tee "$EVIDENCE_DIR/01-list-sessions.json" | jq .

curl -s -w "\nHTTP_STATUS=%{http_code}\n" \
  -X POST "$BASE/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}' | tee "$EVIDENCE_DIR/02-create-session.json" | jq .

# Extract ID from create response for subsequent calls
ID=$(jq -r '.id' "$EVIDENCE_DIR/02-create-session.json")

curl -s -w "\nHTTP_STATUS=%{http_code}\n" \
  "$BASE/api/v1/sessions/$ID" | tee "$EVIDENCE_DIR/03-get-session.json" | jq .

curl -s -w "\nHTTP_STATUS=%{http_code}\n" \
  -X DELETE "$BASE/api/v1/sessions/$ID" | tee "$EVIDENCE_DIR/04-delete-session.json"

# Verify deletion
curl -s -w "\nHTTP_STATUS=%{http_code}\n" \
  "$BASE/api/v1/sessions/$ID" | tee "$EVIDENCE_DIR/05-verify-deleted.json"
```

## Remediation Evidence

Every fix requires before/after proof:

```
remediation/fix-{NNN}-{slug}/
├── description.md       # What broke, root cause, how fixed
├── before.png           # or before-response.json, before-output.txt
├── after.png            # or after-response.json, after-output.txt
├── commit-hash.txt      # The git commit that contains the fix
└── related-logs.txt     # Relevant log entries (optional)
```

### description.md Template
```markdown
## Fix #{NNN}: {Short Description}

**Phase:** {4 or 5}
**Surface:** {screen name, endpoint, command}
**Element:** {specific button, field, response field}

### Issue
{What was observed — cite the before evidence}

### Root Cause
{Why it happened — usually merge conflict resolution or missing integration}

### Fix
{What was changed — cite specific files and lines}

### Verification
- Before: `before.png` shows {description of broken state}
- After: `after.png` shows {description of fixed state}
- Commit: `{hash}` — `{commit message}`
```

## Updating the Manifest

After capturing any evidence, append to `manifest.json`:

```bash
# Helper function (add to your shell session)
add_evidence() {
  local phase=$1 type=$2 path=$3 description=$4 surface=$5 verdict=$6
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  # Use jq to append to the evidence array
  jq --arg p "$phase" --arg t "$type" --arg pa "$path" \
     --arg d "$description" --arg s "$surface" --arg v "$verdict" \
     --arg ts "$timestamp" \
     '.evidence += [{"phase":($p|tonumber),"type":$t,"path":$pa,"description":$d,"surface":$s,"verdict":$v,"timestamp":$ts}]' \
     manifest.json > manifest.tmp && mv manifest.tmp manifest.json
}

# Usage:
add_evidence 4 "screenshot" \
  "phase-4-merges/merge-001/validation/screenshots/01-login.png" \
  "Login screen renders with email and password fields" \
  "LoginView" "pass"
```
