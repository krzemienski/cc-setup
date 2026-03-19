# Git

## Commit Format
```
<type>: <description>

<optional body>
```
Types: feat, fix, refactor, docs, chore, perf, ci
No AI attribution (includeCoAuthoredBy: false).

## Protocol
- Use HTTPS (not SSH) for git push
- Check remote URL before pushing: `git remote get-url origin`
- Create NEW commits (never amend unless explicitly asked)
- Never skip hooks (--no-verify)
- Never force-push to main/master
- Stage specific files (not `git add -A`) to avoid committing secrets

## Pull Requests
- Analyze FULL commit history (not just latest commit)
- Use `git diff [base-branch]...HEAD` to see all changes
- Draft comprehensive PR summary with validation evidence
- Include screenshots, build output, logs
- Push with `-u` flag if new branch
