---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Validation

> This file extends [testing.md](./testing.md) with Python specific content.

## Validation Approach

1. Build and run the real application
2. Exercise features through actual interfaces (CLI, API, UI)
3. Capture output and logs as evidence
4. Verify behavior matches expectations

## Debugging

Use Python's built-in tools for investigation:
- `python -m pdb` for interactive debugging
- `logging` module for runtime tracing
- Direct script execution to verify behavior
