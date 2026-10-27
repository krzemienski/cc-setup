# Full-Stack Validation Strategy

## When This Applies

Project has BOTH a frontend (web, iOS, macOS) AND a backend (API server,
database). Examples: Next.js with API routes, React + Express, SwiftUI + Vapor,
Vue + FastAPI.

## Key Principle: Bottom-Up Validation Order

Always validate from the foundation up. A broken database makes API tests
meaningless. A broken API makes frontend tests misleading.

```
Layer 1: Database / Data Store
  ↓
Layer 2: Backend API
  ↓
Layer 3: Frontend Application
  ↓
Layer 4: Cross-Layer Integration
```

## Layer 1: Database / Data Store

```bash
# SQLite
sqlite3 app.db ".tables"
sqlite3 app.db "SELECT count(*) FROM main_table;"

# PostgreSQL
psql -c "\dt" -d dbname
psql -c "SELECT count(*) FROM main_table;" -d dbname

# Migrations current?
# Check framework-specific migration status
```

**PASS criteria:** Database is reachable, schema matches expectations,
seed/existing data is intact.

## Layer 2: Backend API

Start the backend and validate independently of the frontend.

```bash
# Start backend
PORT=<port> <start command> &
sleep 3

# Health check
curl -sf http://localhost:<PORT>/health

# Exercise every endpoint touched by merged worktrees
# See references/api-validation.md for full patterns
```

**PASS criteria:** Health check returns 200. Every endpoint returns
expected status codes and response shapes. CRUD lifecycle works end-to-end.

## Layer 3: Frontend Application

Only AFTER Layer 2 passes. Start the frontend and validate with its backend
running.

```bash
# Start frontend (backend already running)
npm run dev &
sleep 5

# Use agent-browser or Playwright — see references/web-validation.md
# Or use simulator — see references/ios-validation.md
```

**PASS criteria:** App loads without errors. Navigation works. Data from
backend renders correctly. Forms submit and persist through the API.

## Layer 4: Cross-Layer Integration

The most important and most commonly broken layer. Validate that the
frontend and backend actually work together.

### What to Check

| Check | How | Evidence |
|-------|-----|---------|
| Frontend shows real data from API | Load a list screen, verify items match API response | Screenshot + curl response side-by-side |
| Frontend create/update persists to API | Submit a form, then curl the API to verify | Form screenshot + curl GET response |
| Frontend handles API errors | Trigger a 404/500, verify error UI shows | Error screenshot + curl showing error |
| Auth flows end-to-end | Login via frontend, verify session in API | Login screenshot + auth endpoint response |
| Real-time updates (if applicable) | Trigger event via API, verify frontend updates | Before/after screenshots + API call |

### Evidence Pattern for Cross-Layer

```bash
EVIDENCE="worktree-merge-evidence/phase-5-audit"

# 1. Capture API state
curl -s http://localhost:9999/api/v1/sessions \
  | tee "$EVIDENCE/curl-responses/01-sessions-before-create.json" | jq .

# 2. Create via frontend (screenshot of form + submit)
# ... agent-browser or Playwright ...

# 3. Verify API reflects the new data
curl -s http://localhost:9999/api/v1/sessions \
  | tee "$EVIDENCE/curl-responses/02-sessions-after-create.json" | jq .

# 4. Compare — new item should appear
diff "$EVIDENCE/curl-responses/01-sessions-before-create.json" \
     "$EVIDENCE/curl-responses/02-sessions-after-create.json"
```

## Merge Order for Full-Stack Projects

When merging worktrees that span the stack:

1. **Database migrations / schema changes** — merge first, run migrations
2. **Shared models / DTOs** — merge next (both layers depend on these)
3. **Backend features** — merge and validate API independently
4. **Frontend features** — merge last, validate with backend running

If a single worktree spans multiple layers, validate bottom-up within
that merge: build backend → run backend → validate API → build frontend →
validate frontend → validate integration.

## Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| Frontend points to wrong API URL | All API calls fail | Check `.env`, `next.config.js`, API base URL config |
| CORS not configured | Browser blocks API calls | Backend must allow frontend origin |
| Database migration not run | Schema mismatch errors | Always run migrations after merging schema changes |
| Port conflicts | Server won't start | Kill stale processes: `lsof -i :<PORT>` |
| Frontend dev server proxies API | Direct curl works but frontend fails (or vice versa) | Check proxy config in framework |
| SSR vs CSR mismatch | Hydration errors in browser | Check for `window`/`document` access in SSR paths |
