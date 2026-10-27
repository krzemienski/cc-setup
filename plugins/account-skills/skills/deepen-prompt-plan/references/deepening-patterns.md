# Deepening Patterns Reference

Platform-specific validation gate templates, XML formatting patterns, prompt strengthening techniques, and before/after examples.

## Validation Gate Templates by Platform

### iOS / macOS

```xml
<validation_gate id="VG-{N}" blocking="true" platform="ios">
  <prerequisites>
    Boot simulator: xcrun simctl boot "iPhone 16 Pro"
    Start backend: cd backend && npm start &amp;
    Poll health: until curl -sf http://localhost:3000/health; do sleep 1; done
    Build and install: xcodebuild -project App.xcodeproj -scheme App -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 16 Pro' build 2>&amp;1 | tail -5
    Install: xcrun simctl install booted Build/Products/Debug-iphonesimulator/App.app
    Launch: xcrun simctl launch booted com.example.App
    Wait for render: sleep 3
  </prerequisites>
  <execute>
    xcrun simctl io booted screenshot evidence/vg{N}-{description}.png
  </execute>
  <pass_criteria>
    [SPECIFIC: "Screenshot shows login form with email field, password field, and Submit button"]
    [NOT: "App launches successfully"]
  </pass_criteria>
  <review>
    Use Read tool to visually inspect evidence/vg{N}-{description}.png
    Check against pass criteria point by point
  </review>
  <verdict>PASS → proceed | FAIL → fix → re-run from prerequisites</verdict>
  <mock_guard>IF tempted to write XCTest or mock URLProtocol → STOP → fix real system</mock_guard>
</validation_gate>
```

### CLI / Binary

```xml
<validation_gate id="VG-{N}" blocking="true" platform="cli">
  <prerequisites>
    Build: cargo build --release 2>&amp;1 | tail -3
    Verify binary: ls -la target/release/mytool
  </prerequisites>
  <execute>
    ./target/release/mytool --input test-data.csv --output result.json 2>&amp;1 | tee evidence/vg{N}-output.txt
    echo "Exit code: $?" >> evidence/vg{N}-output.txt
  </execute>
  <pass_criteria>
    Exit code 0
    Output file exists and contains valid JSON
    JSON has "processed" field with value > 0
    stderr contains no ERROR lines
  </pass_criteria>
  <review>
    cat evidence/vg{N}-output.txt
    cat result.json | jq '.processed'
  </review>
  <verdict>PASS → proceed | FAIL → fix → re-run</verdict>
  <mock_guard>IF tempted to write test_*.rs or mock filesystem → STOP → fix real binary</mock_guard>
</validation_gate>
```

### Backend API

```xml
<validation_gate id="VG-{N}" blocking="true" platform="api">
  <prerequisites>
    Start server: npm start &amp;
    Poll health: until curl -sf http://localhost:3000/health; do sleep 1; done
    Verify database: curl -sf http://localhost:3000/health/db || echo "DB NOT READY"
  </prerequisites>
  <execute>
    curl -s -X POST http://localhost:3000/api/resource \
      -H "Content-Type: application/json" \
      -d '{"field": "value"}' \
      | tee evidence/vg{N}-response.json | jq .
  </execute>
  <pass_criteria>
    HTTP 201 (check with -w "%{http_code}")
    Response contains "id" field (non-empty string)
    Response contains "field" matching input
    Response does NOT contain sensitive fields (password, token)
    Duplicate request returns 409
  </pass_criteria>
  <review>
    cat evidence/vg{N}-response.json | jq -e '.id and .field'
  </review>
  <verdict>PASS → proceed | FAIL → fix endpoint → re-run</verdict>
  <mock_guard>IF tempted to use nock, supertest with mocks, or :memory: DB → STOP</mock_guard>
</validation_gate>
```

### Web Frontend

```xml
<validation_gate id="VG-{N}" blocking="true" platform="web">
  <prerequisites>
    Start backend: cd api && npm start &amp;
    Start frontend: cd web && npm run dev &amp;
    Poll ready: until curl -sf http://localhost:3000; do sleep 1; done
    Launch browser: npx playwright install chromium (if needed)
  </prerequisites>
  <execute>
    node -e "
      const { chromium } = require('playwright');
      (async () => {
        const browser = await chromium.launch();
        const page = await browser.newPage();
        await page.goto('http://localhost:3000/dashboard');
        await page.waitForSelector('[data-testid=widget-card]', {timeout: 10000});
        await page.screenshot({path: 'evidence/vg{N}-dashboard.png', fullPage: true});
        await browser.close();
      })();
    "
  </execute>
  <pass_criteria>
    Screenshot shows dashboard with 3 widget cards
    Each card displays numeric data (not "Loading..." or "Error")
    Navigation bar shows user name
  </pass_criteria>
  <review>
    Use Read tool to visually inspect evidence/vg{N}-dashboard.png
  </review>
  <verdict>PASS → proceed | FAIL → fix → re-run</verdict>
  <mock_guard>IF tempted to use Testing Library render() or Storybook → STOP</mock_guard>
</validation_gate>
```

### Phase-Level Regression Gate

Use between phases to ensure earlier work still passes:

```xml
<phase_regression_gate id="PRG-{phase}" blocking="true">
  <description>
    Before starting Phase {N}, verify Phase {N-1} still passes.
    Evidence compounds: Phase 3 prerequisites include Phase 2 AND Phase 1 proof.
  </description>
  <re_validate>
    Re-run VG-1 through VG-{last_phase_gate} from Phase {N-1}
    Compare evidence against original PASS criteria
  </re_validate>
  <pass_criteria>All previous phase gates still PASS with current system state</pass_criteria>
  <on_regression>
    STOP. Fix the regression before starting new phase.
    Do NOT proceed with Phase {N} if Phase {N-1} is broken.
  </on_regression>
</phase_regression_gate>
```

---

## XML Formatting Patterns

### Semantic Tag Naming
Tags should describe their content, not their position.

**Good:**
```xml
<task id="1" priority="high" depends_on="setup">
<validation_gate id="VG-1" blocking="true" platform="api">
<research_finding source_type="official_docs" confidence="high">
<open_question owner="product" severity="blocking">
```

**Bad:**
```xml
<section1>
<item>
<data>
<block type="important">
```

### Nesting for Hierarchy

```xml
<phase id="1" name="foundation">
  <task id="1.1">
    <description>Set up database schema</description>
    <files>migrations/001_initial.sql, src/db/schema.ts</files>
    <approach>Follow existing migration pattern in migrations/</approach>
    <validation_gate id="VG-1.1" blocking="true">
      <pass_criteria>psql -c "\dt" shows users, sessions, tokens tables</pass_criteria>
    </validation_gate>
  </task>
  <task id="1.2" depends_on="1.1">
    <description>Create database client with connection pooling</description>
    <validation_gate id="VG-1.2" blocking="true">
      <pass_criteria>SELECT 1 returns successfully through the client</pass_criteria>
    </validation_gate>
  </task>
</phase>
```

### Metadata Tags for Downstream Consumption

When the document will be consumed by another Claude instance (meta-prompts, agent pipelines):

```xml
<document_metadata>
  <type>implementation_plan</type>
  <platform>ios</platform>
  <risk_level>high</risk_level>
  <deepened>2026-03-26</deepened>
  <confidence level="high">
    All key decisions have evidence-backed rationale.
    Validation gates cover all tasks.
  </confidence>
  <assumptions>
    <assumption id="A1" validated="false">Backend API is already deployed and healthy</assumption>
    <assumption id="A2" validated="true">User auth follows OAuth 2.0 PKCE flow (confirmed in auth-spec.md)</assumption>
  </assumptions>
  <open_questions>
    <question owner="product" blocking="true">Should expired sessions show an error or silently redirect to login?</question>
    <question owner="engineering" blocking="false">Redis vs in-process cache for session tokens — benchmark needed</question>
  </open_questions>
</document_metadata>
```

---

## Prompt Strengthening Patterns

For documents that are prompts or agent instructions, these patterns strengthen specific weaknesses.

### Pattern 1: Add Decision Routing Where Missing

**Before (weak):**
```markdown
Process the user's request and provide an appropriate response.
```

**After (strong):**
```xml
<routing>
  <route match="user asks to create" action="creation_workflow" />
  <route match="user asks to fix/debug" action="diagnosis_workflow" />
  <route match="user asks to explain" action="explanation_workflow" />
  <route match="no match" action="ask_clarifying_question" />
</routing>
```

### Pattern 2: Add Few-Shot Examples Where Output Is Ambiguous

**Before:**
```markdown
Generate a commit message for the changes.
```

**After:**
```xml
<output_specification>
  <format>Conventional Commits: type(scope): description</format>
  <examples>
    <example>
      <input>Added JWT authentication with refresh token rotation</input>
      <output>feat(auth): implement JWT authentication with refresh token rotation</output>
    </example>
    <example>
      <input>Fixed crash when user has no profile picture</input>
      <output>fix(profile): handle null avatar URL in user profile component</output>
    </example>
  </examples>
</output_specification>
```

### Pattern 3: Add Error Recovery Where Only Happy Path Exists

**Before:**
```markdown
1. Read the file
2. Parse the JSON
3. Extract the data
4. Write the output
```

**After:**
```xml
<workflow>
  <step id="1">
    <action>Read the file</action>
    <on_error>
      <if condition="file not found">Ask user for correct path</if>
      <if condition="permission denied">Report and suggest chmod or different location</if>
    </on_error>
  </step>
  <step id="2">
    <action>Parse the JSON</action>
    <on_error>
      <if condition="invalid JSON">Report line/column of syntax error, suggest fix</if>
      <if condition="empty file">Report empty file, ask user to verify</if>
    </on_error>
  </step>
</workflow>
```

### Pattern 4: Add Scope Boundaries Where Missing

**Before:**
```markdown
Optimize the database queries for better performance.
```

**After:**
```xml
<scope>
  <in_scope>
    Query optimization (indexes, joins, pagination)
    Connection pooling configuration
    Caching strategy for read-heavy queries
  </in_scope>
  <out_of_scope>
    Schema redesign (requires separate plan)
    Database engine migration
    Application-level caching (Redis, Memcached)
  </out_of_scope>
  <escalation>If optimization requires schema changes, surface as open question — do not proceed</escalation>
</scope>
```

---

## Before / After: Full Section Deepening Example

### Before (weak Risks section):

```markdown
## Risks
- API might be slow
- Database could have issues
- Security concerns
```

### After (deepened Risks section):

```xml
<risks>
  <risk id="R1" severity="high" likelihood="medium">
    <description>API response latency exceeds 500ms under load</description>
    <evidence>Current p95 latency is 380ms (from /metrics endpoint). Adding auth middleware adds ~50-80ms per request based on bcrypt cost factor 12.</evidence>
    <mitigation>
      Pre-compute auth tokens with 15-min TTL. Cache validated sessions in-process.
      Monitor p95 after deployment — rollback trigger at 600ms.
    </mitigation>
    <validation>
      <gate>After deployment, run: curl -w "%{time_total}" -o /dev/null -s localhost:3000/api/protected × 100 | confirm p95 &lt; 500ms</gate>
    </validation>
  </risk>
  <risk id="R2" severity="high" likelihood="low">
    <description>Migration fails on production data with 2.3M user rows</description>
    <evidence>Test migration on staging (50k rows) completed in 45s. Linear extrapolation: ~35 min for production. Acceptable within maintenance window (2hr).</evidence>
    <mitigation>
      Run in batches of 10k rows with progress logging.
      Prepare rollback script (tested on staging).
      Schedule during low-traffic window (2-4am UTC).
    </mitigation>
  </risk>
  <risk id="R3" severity="critical" likelihood="low">
    <description>Token signing key exposure via environment variable leak</description>
    <evidence>Current .env.example lists JWT_SECRET. Production uses AWS Secrets Manager (confirmed in infra/terraform/secrets.tf).</evidence>
    <mitigation>
      Verify Secrets Manager rotation policy is active.
      Add .env to .gitignore audit check in CI.
      Never log token values — confirmed in logging middleware (src/middleware/logger.ts line 23: redacted fields include 'token', 'secret').
    </mitigation>
  </risk>
</risks>
```

**What changed:**
- Generic risks → specific, measurable risks with evidence
- No mitigation → concrete mitigation strategies
- No severity → severity and likelihood assessed
- No validation → R1 has a validation gate for performance
- No evidence → each risk grounded in actual system data
