---
name: functional-validation
description: >
  Enforces end-user perspective validation through real system execution. Triggers
  on "validate", "functional test", "prove it works", "evidence". Never write mocks
  or test files. Validate via simulator, browser, CLI, or cURL with PASS/FAIL verdict.
---

# Functional Validation Protocol

## The Iron Rule

```
NEVER create mocks, stubs, test doubles, or test files.
NEVER import jest, vitest, pytest, XCTest, or any test framework.
ALWAYS validate through the same interfaces real users experience.
ALWAYS capture evidence that proves the feature works end-to-end.
```

## Before You Validate

1. Is the real system running? (not a dev server with mocks)
2. Can I access it as a user would? (browser, simulator, CLI — not a test harness)
3. Are all dependencies real? (real DB, real API keys, real network)
4. Do I have PASS criteria written down? (specific, observable, measurable)
5. Am I capturing evidence to files? (not just observing in terminal)

## Platform Detection

Detect the platform FIRST. Wrong platform = wrong validation approach.

| Priority | Platform | Indicators | Approach |
|----------|----------|------------|----------|
| 1 | iOS/macOS | `*.xcodeproj`, `Package.swift` | Xcode build, simulator, simctl/idb |
| 2 | Web | `package.json` + React/Vue/Next | Dev server, browser, Playwright MCP |
| 3 | CLI | `main.go`, `Cargo.toml`, `cli.py` | Build binary, execute, capture stdout |
| 4 | API | `server.ts`, `app.py` + routes | Start server, curl endpoints |
| 5 | Full-Stack | Frontend + Backend present | Bottom-up: DB -> API -> Frontend |

## The 4-Step Protocol

### Step 1: Build & Launch

Build the real system with all real dependencies. If the build fails, that IS your first finding — stop and report it before proceeding.

### Step 2: Exercise Through UI

Interact as a real user would — browser, simulator, CLI binary, or curl. No REPL imports, no direct function calls, no internal API invocations that bypass the real entry point.

### Step 3: Capture Evidence

Save artifacts to `e2e-evidence/` — screenshots, response bodies, CLI output, logs. Evidence must be READ and DESCRIBED with specific quoted content, not just confirmed to exist.

### Step 4: Write Verdict

For each criterion, cite specific evidence with file paths and quoted content. See verdict format below.

## Multi-Platform Validation Order

For full-stack apps, validate bottom-up. Each layer must PASS before testing the layer above it.

```
Database/Infra  ->  Business Logic  ->  API Endpoints  ->  Frontend UI
  (first)                                                     (last)
```

If the DB is broken, every API test fails with misleading errors. Fix lower layers first.

## Verdict Format

```markdown
### Criterion: [What was required]
**PASS** / **FAIL**
Evidence: `e2e-evidence/[file]` — [What I actually saw, quoted specifically]
```

All criteria must be evaluated before claiming completion. A single **FAIL** blocks the completion claim until fixed and re-validated.

## Security Policy

This skill executes real systems for validation. It never introduces new functionality, never disables security checks, and never bypasses auth — it validates through the same security boundaries real users encounter.
