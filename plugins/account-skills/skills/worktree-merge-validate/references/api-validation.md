# Backend API Validation Strategy

## When This Applies
Project has REST/GraphQL routes, OpenAPI spec, Express/Fastify/Vapor/FastAPI/
Rails/Django server, or any HTTP-serving backend.

## Build and Start

```bash
# Build
swift build          # Vapor
npm run build        # Node/TypeScript
go build ./...       # Go
cargo build          # Rust

# Start
PORT=<port> swift run <ServerBinary> &
npm run start &
go run ./cmd/server &

# Wait for startup
sleep 3
curl -sf http://localhost:<PORT>/health && echo "Server ready"
```

## Health Check

Always verify the server is healthy before testing endpoints:
```bash
curl -sf http://localhost:<PORT>/health
# Expected: 200 OK with body like {"status": "ok"}
```

If health check fails, read server logs. Don't proceed with broken infrastructure.

## Evidence Collection

### Per-Endpoint Testing Pattern
```bash
EVIDENCE_DIR="./evidence"
BASE="http://localhost:<PORT>"
mkdir -p "$EVIDENCE_DIR"

# GET endpoint
curl -s "$BASE/api/v1/sessions" | tee "$EVIDENCE_DIR/01-list-sessions.json" | jq .

# POST endpoint (create)
curl -s -X POST "$BASE/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-session"}' \
  | tee "$EVIDENCE_DIR/02-create-session.json" | jq .

# GET single resource
curl -s "$BASE/api/v1/sessions/<id>" \
  | tee "$EVIDENCE_DIR/03-get-session.json" | jq .

# PUT/PATCH (update)
curl -s -X PATCH "$BASE/api/v1/sessions/<id>" \
  -H "Content-Type: application/json" \
  -d '{"name": "updated-name"}' \
  | tee "$EVIDENCE_DIR/04-update-session.json" | jq .

# DELETE
curl -s -X DELETE "$BASE/api/v1/sessions/<id>" \
  | tee "$EVIDENCE_DIR/05-delete-session.json" | jq .
```

### Capture Response Details
```bash
# Full response with headers and status code
curl -s -w "\n---\nHTTP Status: %{http_code}\nTime: %{time_total}s\n" \
  -D - "$BASE/api/v1/endpoint" \
  | tee "$EVIDENCE_DIR/full-response.txt"
```

## Validation Criteria

### Per-Endpoint Checklist

| Aspect | Check | Evidence |
|--------|-------|---------|
| Status code | Correct for operation (200, 201, 204, 404, etc.) | `curl -o /dev/null -w "%{http_code}"` |
| Response body | Contains expected fields and data | `jq '.field'` on response |
| Content-Type | Correct header (`application/json`, etc.) | `-D -` to capture headers |
| CRUD lifecycle | Create→Read→Update→Delete→Verify-Gone | Sequential curl calls |
| Error handling | Invalid input returns 400/422 with message | Send malformed request |
| Auth | Protected endpoints reject unauthenticated requests | Request without token |
| Pagination | Large collections paginate correctly | Request with `?page=1&limit=10` |
| Performance | Response time acceptable | `curl -w "%{time_total}"` |

### Error Case Testing
```bash
# Missing required field
curl -s -X POST "$BASE/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | tee "$EVIDENCE_DIR/error-missing-field.json" | jq .

# Invalid ID
curl -s "$BASE/api/v1/sessions/nonexistent-id" \
  | tee "$EVIDENCE_DIR/error-not-found.json" | jq .

# Wrong content type
curl -s -X POST "$BASE/api/v1/sessions" \
  -d "not json" \
  | tee "$EVIDENCE_DIR/error-wrong-content-type.json" | jq .
```

## Database Verification

If the API uses a database:
```bash
# Check database file exists and has data (SQLite)
ls -la *.sqlite
sqlite3 app.db "SELECT count(*) FROM sessions;"

# Or via API — create, then list, verify count increased
BEFORE=$(curl -s "$BASE/api/v1/sessions" | jq '.total')
curl -s -X POST "$BASE/api/v1/sessions" -H "Content-Type: application/json" -d '{"name":"test"}'
AFTER=$(curl -s "$BASE/api/v1/sessions" | jq '.total')
echo "Before: $BEFORE, After: $AFTER"
```

## GraphQL APIs

```bash
# Introspection
curl -s -X POST "$BASE/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}' \
  | tee "$EVIDENCE_DIR/schema.json" | jq .

# Query
curl -s -X POST "$BASE/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ sessions { id name } }"}' \
  | tee "$EVIDENCE_DIR/query-sessions.json" | jq .

# Mutation
curl -s -X POST "$BASE/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createSession(name: \"test\") { id } }"}' \
  | tee "$EVIDENCE_DIR/mutation-create.json" | jq .
```

## WebSocket Endpoints

```bash
# Using websocat (install: cargo install websocat)
echo '{"type": "ping"}' | websocat ws://localhost:<PORT>/ws \
  | tee "$EVIDENCE_DIR/ws-response.json"

# Or using wscat (install: npm install -g wscat)
wscat -c ws://localhost:<PORT>/ws -x '{"type": "ping"}' \
  | tee "$EVIDENCE_DIR/ws-response.json"
```

## API-Specific Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| API prefix auto-added | Double prefix: `/api/v1/api/v1/...` | Check if client adds prefix |
| Port conflict | Server won't start | Check `lsof -i :<PORT>`, kill stale processes |
| Database migrations | Schema mismatch errors | Run migrations before testing |
| Auth tokens expire | Requests fail mid-test | Refresh token between test sequences |
| Rate limiting | 429 errors during testing | Add small delays between requests |
| CORS headers | Browser clients can't reach API | Check CORS config if testing with frontend |
