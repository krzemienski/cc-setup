# Workflow

## Canonical Flow
1. DISCOVER — Semantic search (see search-protocol.md)
2. PLAN — /everything-claude-code:plan or /oh-my-claudecode:ralplan
3. EXECUTE — /oh-my-claudecode:ralph or /oh-my-claudecode:team
4. REVIEW — code-reviewer agent immediately post-implementation
5. VALIDATE — /functional-validation, build + run + screenshot + evidence
6. REFLECT — /reflexion:reflect
7. COMMIT — Conventional commits (see git.md)

## Skill-First Mandate
BEFORE any task: scan skills, invoke all that match (even 1% chance).
Never rationalize skipping a skill — skills have project-specific context you lack.

## Research Before Code
- GitHub code search first: `gh search repos` and `gh search code`
- Check package registries before writing utility code
- Search for adaptable implementations in open source
- Prefer adapting proven approaches over net-new code

## Implementation Rules
- Compile after every change
- DO NOT create new files when existing ones can be updated
- Every plan MUST include a validation phase with evidence checkpoints
- Plans must NOT include "write unit tests" or "add test coverage"
- Build the real system — no placeholders, no stubs
- Run it — start the app, simulator, or service
- Exercise through UI — capture screenshots/logs as evidence
