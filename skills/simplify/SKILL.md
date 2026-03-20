---
name: simplify
description: >
  Reviews recently changed code for simplification opportunities and applies fixes directly.
  Triggers on "simplify", "clean up code", "reduce complexity", "refactor".
argument-hint: Optional scope, e.g. "focus on naming" or "staged only"
---

# Code Simplification Protocol

Operate only on files changed since the last commit. Apply fixes directly — do not report without fixing.

## Step 1: Identify Changed Files

```bash
git diff --name-only HEAD
git diff --name-only --cached
```

Combine both lists, deduplicate. If the list is empty, check `git diff --name-only HEAD~1`.

## Step 2: Scan Each File

For each changed file, check for these issues in order:

### Dead Code
- Exported symbols with zero references (`lsp_find_references` → 0 results)
- Commented-out code blocks older than this change
- Unreachable branches (`if (false)`, code after `return`)

### Unused Imports
- Run `lsp_diagnostics` — flag any "unused import" or "declared but not used" warnings
- Remove them directly with Edit

### Redundant Logic
- Duplicate conditional branches with identical bodies
- Boolean expressions that simplify (`x === true` → `x`, `!x === false` → `x`)
- Wrapper functions that only call one other function with no transformation

### Deep Nesting
- Flag any block nested more than 4 levels deep
- Apply early-return / guard-clause pattern to flatten

### Unclear Naming
- Single-letter variables outside loop counters (`i`, `j`, `k` are acceptable)
- Generic names: `data`, `result`, `temp`, `obj`, `val`, `stuff`, `thing`
- Rename using `lsp_rename` to preserve all references

## Step 3: Apply Fixes

- Use `Edit` for targeted line changes
- Use `lsp_rename` for symbol renames (propagates across all files)
- Use `ast_grep_replace` for structural patterns (always `dryRun=true` first)
- One fix at a time — run `lsp_diagnostics` on the file after each change

## Step 4: Verify Build

After all fixes are applied, verify the build still passes:

```bash
# Detect build system and run appropriate check
[ -f package.json ] && npm run build 2>&1 | tail -20
[ -f Cargo.toml ] && cargo check 2>&1 | tail -20
[ -f go.mod ] && go build ./... 2>&1 | tail -20
```

If the build fails, revert the last change and skip that simplification.

## Step 5: Report

```
## Simplification Summary

Files reviewed: N
Changes applied: N

| File | Change | Lines affected |
|------|--------|----------------|
| path/to/file.ts | Removed unused import `X` | 3 |
| path/to/file.ts | Renamed `data` → `userProfile` | 12, 34, 67 |
| path/to/file.go | Flattened 5-level nesting with guard clause | 45–62 |

Build: PASS
```

## Constraints

- Never modify files not in the changed set
- Never reformat unrelated code (whitespace-only changes outside touched lines)
- Never extract new abstractions — simplify what exists, do not restructure
- If a rename would touch more than 20 files, ask before proceeding
