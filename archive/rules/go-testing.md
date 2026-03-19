---
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
---
# Go Validation

> This file extends [testing.md](./testing.md) with Go specific content.

## Validation Approach

1. Build the real binary: `go build ./...`
2. Run it and exercise through actual interfaces
3. Use `-race` flag during development builds for race detection
4. Capture output and logs as evidence
5. Verify behavior matches expectations

## Static Analysis

```bash
go vet ./...
staticcheck ./...
```
