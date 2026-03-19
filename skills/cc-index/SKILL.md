---
name: cc-index
description: "[FUTURE] Build/refresh semantic code index with Zoekt via code-index-mcp"
triggers:
  - "index codebase"
  - "build index"
  - "refresh index"
  - "cc index"
---

# CC Code Index [FUTURE]

Build and refresh a persistent semantic code index using Zoekt via code-index-mcp.

## Prerequisites
- Go installed: `go version`
- code-index-mcp installed: `go install github.com/trondhindenes/code-index-mcp@latest`
- Server added to ~/.mcp.json

## Usage
```bash
# Index current project
code-index-mcp index .

# Search the index
# (available via MCP tools once server is configured)
```

## Status
This skill is FUTURE — code-index-mcp is not yet installed. Install it after the core CC setup is validated.
