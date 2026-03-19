# Git Workflow

## Commit Message Format
```
<type>: <description>

<optional body>
```

Types: feat, fix, refactor, docs, chore, perf, ci

Note: Attribution disabled globally via ~/.claude/settings.json.

## Git Remote Protocol

- Always use HTTPS (not SSH) for git push operations
- Check git remote URL before pushing: `git remote get-url origin`
- If remote is SSH, switch to HTTPS: `git remote set-url origin https://github.com/...`

## Pull Request Workflow

When creating PRs:
1. Analyze full commit history (not just latest commit)
2. Use `git diff [base-branch]...HEAD` to see all changes
3. Draft comprehensive PR summary
4. Include validation evidence (screenshots, build output, logs)
5. Push with `-u` flag if new branch

> For the full development process (planning, functional validation, code review) before git operations,
> see [development-workflow.md](./development-workflow.md).
