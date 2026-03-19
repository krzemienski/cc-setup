# Coding Style

## Read Before You Write (MANDATORY)

**NEVER edit a file you haven't fully read.** Before modifying ANY source file:
1. Read the FULL file — no offset, no limit, no skimming
2. Understand how it connects to other modules
3. If the file is large, read it in sections but read ALL of it
4. Understand the existing patterns before introducing changes

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones:

```
// Pseudocode
WRONG:  modify(original, field, value) → changes original in-place
CORRECT: update(original, field, value) → returns new copy with change
```

Rationale: Immutable data prevents hidden side effects, makes debugging easier, and enables safe concurrency.

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Extract utilities from large modules
- Organize by feature/domain, not by type

## Error Handling

ALWAYS handle errors comprehensively:
- Handle errors explicitly at every level
- Provide user-friendly error messages in UI-facing code
- Log detailed error context on the server side
- Never silently swallow errors

## Input Validation

ALWAYS validate at system boundaries:
- Validate all user input before processing
- Use schema-based validation where available
- Fail fast with clear error messages
- Never trust external data (API responses, user input, file content)

## Reference Data Protection

NEVER modify without explicit user approval:
- Ground truth files, test fixtures, reference datasets
- Configuration files that define expected behavior (YAML, JSON configs)
- Seed data, migration baselines, snapshot files
- Any file the user has marked as authoritative

If you believe reference data is wrong, ASK the user — don't change it yourself.

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No hardcoded values (use constants or config)
- [ ] No mutation (immutable patterns used)
- [ ] Feature validated through real UI (not just compiled)
