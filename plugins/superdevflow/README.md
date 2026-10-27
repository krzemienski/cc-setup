# superdevflow

A Claude Code plugin that bundles developer workflow tools.

## Skills

| Skill | Description |
|-------|-------------|
| `/superdevflow:gha <url>` | Analyze GitHub Actions failures, check flakiness, identify breaking commits |
| `/superdevflow:handoff` | Create handoff documents so the next agent can continue your work |
| `/superdevflow:clone` | Clone the current conversation to branch off and try a different approach |
| `/superdevflow:half-clone` | Clone the later half of a conversation, reducing token usage |
| `/superdevflow:review-claudemd` | Review recent conversations to suggest CLAUDE.md improvements |

## Install

```bash
claude plugin marketplace add ykdojo/superdevflow
claude plugin install superdevflow@ykdojo
```

## Requirements

- Claude Code
- `gh` CLI (for gha skill)

## Origin

Originally part of [45 Claude Code Tips](https://github.com/ykdojo/claude-code-tips).
