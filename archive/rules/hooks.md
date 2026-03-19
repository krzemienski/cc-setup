# Hooks System

## Active Enforcement Hooks

These hooks enforce project discipline automatically:

### UserPromptSubmit (fires on every request)
| Hook | Purpose |
|------|---------|
| `documentation-context-check.js` | Requires: sequential thinking, docs lookup, code exploration, skill scan |
| `skill-activation-forced-eval.js` | Forces skill evaluation → activation → then implement |

### PreToolUse (fires before tool execution)
| Hook | Matcher | Purpose |
|------|---------|---------|
| `block-test-files.js` | Write\|Edit\|MultiEdit | **BLOCKS** creation of test/mock/stub files |
| `block-api-key-references.js` | Write\|Edit\|MultiEdit | **BLOCKS** code referencing ANTHROPIC_API_KEY or non-SDK AI imports (SessionForge only) |
| `plan-before-execute.js` | Write\|Edit\|MultiEdit | Warns if writing source code without any planning phase detected |
| `read-before-edit.js` | Edit\|MultiEdit | Reminds to read FULL file before editing |
| `subagent-context-enforcer.js` | Agent | Warns if subagent prompt lacks context |
| `sdk-auth-subagent-enforcer.js` | Agent | Injects Agent SDK auth rules into every subagent (SessionForge only) |
| `evidence-gate-reminder.js` | TaskUpdate | Injects evidence checklist on task completion |

### PostToolUse (fires after tool execution)
| Hook | Matcher | Purpose |
|------|---------|---------|
| `validation-not-compilation.js` | Bash | Reminds: compilation ≠ validation |
| `completion-claim-validator.js` | Bash | Catches build success without functional validation evidence |
| `dev-server-restart-reminder.js` | Edit\|Write\|MultiEdit | Reminds to restart dev server after route/schema/config changes |
| `skill-invocation-tracker.js` | Edit\|Write\|MultiEdit | Warns if 5+ code changes made without any skill invocation |

### SessionStart (fires on session init)
| Hook | Matcher | Purpose |
|------|---------|---------|
| `session-sdk-context.js` | startup\|resume\|clear\|compact | Injects Agent SDK auth context from turn 1 (SessionForge only) |

## The Principles These Enforce

1. **Skill-First**: Always scan and invoke relevant skills before any work
2. **Think First**: Use sequential thinking MCP to reason through requests
3. **Docs First**: Check Context7/deepwiki for library documentation
4. **Explore First**: Read full files and explore codebase before editing
5. **No Skimming**: Read complete files, not snippets
6. **No Test Files**: Never create mocks, stubs, or test files
7. **Validate Through UI**: Compilation is not validation — exercise real features
8. **Evidence Before Completion**: Personally examine all evidence, cite specific proof
9. **Context for Subagents**: Never delegate without providing full codebase context
10. **Agent SDK Auth (SessionForge)**: NEVER reference ANTHROPIC_API_KEY, NEVER import @anthropic-ai/sdk directly — enforced by block hook + subagent injection + session start injection
11. **Plan Before Execute**: Don't jump to writing code without a planning phase
12. **Dev Server Awareness**: Restart dev server after route/schema changes to avoid stale cache false errors
13. **Never Modify Reference Data**: Never modify ground truth, fixtures, or reference configuration without explicit user approval

## Hook Types

- **PreToolUse**: Before tool execution — can block or inject context
- **PostToolUse**: After tool execution — inject reminders
- **UserPromptSubmit**: On every user message — inject workflow requirements
- **SessionStart**: On session init — load context
