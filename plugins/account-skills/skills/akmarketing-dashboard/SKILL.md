---
name: ak:marketing-dashboard
description: Local-first marketing command center for solopreneurs. Manage campaigns, content, and assets with Claude Code AI automation.
metadata:
  author: agentkit
  version: "1.0.0"
---

# Marketing Dashboard

**Status:** Foundation Phase (Phase 1 Complete)

Local-first marketing command center for solopreneurs. Manage campaigns, content, and assets with Claude Code AI automation.

## Quick Start

### Development Mode

```bash
# Terminal 1: Start API server
cd server
npm install
npm run dev

# Terminal 2: Start Vue frontend
cd app
npm install
npm run dev
```

Access:
- **Frontend:** http://localhost:5173
- **API:** http://localhost:3457

### Production Mode

```bash
# Build frontend
cd app
npm install
npm run build

# Start server (serves API + built frontend)
cd ../server
npm install
npm start
```

If the server reports `better-sqlite3 is not available`, use Node 20 LTS for
the dashboard server. On Windows, install Visual Studio Build Tools with the C++
desktop workload, then run `npm rebuild better-sqlite3 --build-from-source` from
`server`.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + Tailwind CSS |
| Backend | Hono (Node.js) |
| Database | SQLite (optional better-sqlite3 native driver) |
| AI | Claude Code CLI |

## Phase 1 Complete ✓

- [x] Vue 3 + Vite app initialized
- [x] Tailwind CSS configured with design tokens
- [x] Hono API server created
- [x] SQLite database schema defined
- [x] Basic API endpoints (GET)

## Next Phases

- **Phase 2:** Full CRUD API routes
- **Phase 3:** Vue components & stores
- **Phase 4:** Dashboard features
- **Phase 5:** Integration & deployment

## Database Tables

- `campaigns` - Marketing campaigns
- `content` - Blog posts, social media, emails
- `assets` - Images, videos, documents
- `automations` - AI automation recipes

## Commands

```bash
# Start dashboard
/marketing:dashboard

# Or manually:
node server/index.js
```
