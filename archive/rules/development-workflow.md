# Development Workflow

> This file extends [git-workflow.md](./git-workflow.md) with the full feature development process that happens before git operations.

## Skill-First Mandate

**BEFORE starting any task**, scan available skills and invoke relevant ones. Skills carry project-specific context, patterns, and validation requirements that you do not have by default. This is non-negotiable.

- Check the full skill list at the start of every task
- Select and invoke the most relevant skills for the current work
- If multiple skills apply, invoke all of them
- Never rationalize skipping a skill — even a 1% chance of relevance means invoke it

## Feature Implementation Workflow

0. **Research & Reuse** _(mandatory before any new implementation)_
   - **GitHub code search first:** Run `gh search repos` and `gh search code` to find existing implementations, templates, and patterns before writing anything new.
   - **Check package registries:** Search npm, PyPI, crates.io, and other registries before writing utility code. Prefer battle-tested libraries over hand-rolled solutions.
   - **Search for adaptable implementations:** Look for open-source projects that solve 80%+ of the problem and can be forked, ported, or wrapped.
   - Prefer adopting or porting a proven approach over writing net-new code when it meets the requirement.

1. **Plan First**
   - Use **planner** agent to create implementation plan
   - Identify dependencies and risks
   - Break down into phases
   - Every plan MUST include a functional validation phase with evidence checkpoints
   - Plans must NOT include steps like "write unit tests" or "add test coverage"

2. **Build & Validate (Functional Validation)**
   - Build the real system — no mocks, no stubs, no test files
   - Run the app in the simulator or on device
   - Exercise the feature through the actual UI
   - Capture screenshots/logs as evidence
   - Apply `gate-validation-discipline`: personally examine all evidence, cite specific proof, match to criteria

3. **Code Review**
   - Use **code-reviewer** agent immediately after writing code
   - Address CRITICAL and HIGH issues
   - Fix MEDIUM issues when possible

4. **Commit & Push**
   - Detailed commit messages
   - Follow conventional commits format
   - Include validation evidence (screenshots, build output, logs)
   - See [git-workflow.md](./git-workflow.md) for commit message format and PR process
