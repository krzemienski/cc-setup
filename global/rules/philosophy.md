# Philosophy

## Core Principles
- YAGNI / KISS / DRY
- Immutability: create new objects, never mutate
- Functional validation ONLY: never mock, stub, or write test files
- Evidence before completion: prove it works with screenshots/logs
- Skill-first: always check and invoke relevant skills before work
- Read before write: ALWAYS read full file before editing

## Code Quality
- Many small files > few large files (200-400 lines, 800 max)
- Functions under 50 lines, nesting under 4 levels
- File naming: kebab-case (JS/TS/Python/shell), PascalCase (Swift/C#/Java)
- Handle errors explicitly at every level
- Validate input at system boundaries
- No hardcoded values — use constants or config
- No deep nesting (>4 levels)
- Self-documenting code with meaningful names

## Reference Data Protection
- NEVER modify ground truth, fixtures, or reference config without user approval
- If you believe reference data is wrong, ASK — don't change it yourself
