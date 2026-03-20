---
name: e2e-validate
description: >
  End-to-end functional validation through real user interfaces. Triggers on
  "e2e", "end to end", "validate end to end", "browser test". Never write test
  files or mocks. Validate via browser (Playwright), CLI terminal, or API (curl).
triggers:
  - e2e
  - end to end
  - validate end to end
  - browser test
---

# E2E Functional Validation

## The Iron Rule

```
NEVER create test files, spec files, or test suites.
NEVER import jest, vitest, pytest, or any test framework.
ALWAYS drive the real running system through real user interfaces.
ALWAYS capture evidence to e2e-evidence/ and quote it in verdicts.
```

## Target Detection

Identify the target FIRST — wrong approach wastes the entire session.

| Target | Indicators | Validation Approach |
|--------|------------|---------------------|
| Web app | `package.json` + React/Vue/Next/Svelte | Playwright browser automation |
| CLI tool | `main.go`, `Cargo.toml`, `cli.py`, binary | Execute binary, capture stdout/stderr |
| API | `server.ts`, `app.py`, route handlers | `curl` with real request/response bodies |
| Full-stack | Frontend + backend both present | Bottom-up: API first, then browser UI |

## Protocol

### 1. Start the Real System

Launch with real dependencies — no in-memory fakes, no mocked services.

```bash
# Web / full-stack
npm run dev   # or pnpm dev, yarn dev

# API only
node dist/server.js   # or python app.py, go run main.go

# CLI — build first
go build -o ./bin/mytool ./cmd/mytool
cargo build --release
```

If the build or start fails, that IS the first finding. Report it before proceeding.

### 2. Exercise Through the Real Interface

**Browser (Playwright MCP or npx playwright):**

```typescript
// Navigate and interact as a real user would
await page.goto('http://localhost:3000')
await page.waitForLoadState('networkidle')
await page.locator('[data-testid="submit"]').click()
await page.waitForResponse(r => r.url().includes('/api/') && r.status() === 200)
await page.screenshot({ path: 'e2e-evidence/after-submit.png', fullPage: true })
```

**CLI:**

```bash
./bin/mytool --flag value > e2e-evidence/cli-output.txt 2>&1
echo "exit code: $?"
```

**API (curl):**

```bash
curl -s -w "\nHTTP %{http_code}" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  http://localhost:3000/api/endpoint \
  > e2e-evidence/api-response.json
```

### 3. Capture Evidence

Save all artifacts to `e2e-evidence/`. Evidence must be READ and quoted — existence alone is not proof.

- Screenshots: `e2e-evidence/*.png`
- API responses: `e2e-evidence/*.json`
- CLI output: `e2e-evidence/*.txt`
- Console logs: `e2e-evidence/console.log`

### 4. Write Verdict

```markdown
### Criterion: [What was required]
**PASS** / **FAIL**
Evidence: `e2e-evidence/[file]` — "[Specific quoted content from the file]"
```

Every criterion must be evaluated. One **FAIL** blocks completion until fixed and re-validated.

## Playwright Reliability Patterns

```typescript
// Wait for real network activity, not arbitrary timeouts
await page.waitForResponse(r => r.url().includes('/api/data'))

// Use locators (auto-retry built in) — never page.click(selector)
await page.locator('[data-testid="button"]').click()

// Wait for visual stability before asserting
await page.locator('[data-testid="result"]').waitFor({ state: 'visible' })
```

## Security Boundary

Never bypass authentication or disable security checks during validation. Exercise the system through the same trust boundaries real users encounter.
