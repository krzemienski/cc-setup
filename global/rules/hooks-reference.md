# Active Hooks Reference

## SessionStart (startup|resume|clear|compact)
- session-init.cjs — env setup, project detection, static context (one-time)
- session-sdk-context.js — Agent SDK auth context (SessionForge-specific)

## UserPromptSubmit (every message)
- dev-rules-reminder.cjs — dynamic context: datetime, CWD, paths, plan, naming (~15 lines)
- skill-activation-forced-eval.js — skill gate (~3 lines)

## PreToolUse
- descriptive-name.cjs (Write) — enforce descriptive filenames
- block-test-files.js (Write|Edit|MultiEdit) — block test/mock/stub file creation
- plan-before-execute.js (Write|Edit|MultiEdit) — warn if no planning detected
- read-before-edit.js (Edit|MultiEdit) — remind to read full file first
- subagent-context-enforcer.js (Agent) — warn if subagent lacks context
- sdk-auth-subagent-enforcer.js (Agent) — inject SDK auth rules
- evidence-gate-reminder.js (TaskUpdate) — evidence checklist on completion

## PostToolUse
- validation-not-compilation.js (Bash) — compilation is not validation
- completion-claim-validator.js (Bash) — catch build success without evidence
- dev-server-restart-reminder.js (Edit|Write|MultiEdit) — restart after route/schema changes
- skill-invocation-tracker.js (Edit|Write|MultiEdit) — warn if 5+ edits without skill

## SubagentStart (*)
- subagent-init.cjs — context injection
- team-context-inject.cjs — team context

## SubagentStop (Plan)
- cook-after-plan-reminder.cjs — post-plan reminder

## TaskCompleted / TeammateIdle / Stop
- task-completed-handler.cjs, teammate-idle-handler.cjs
- Sound effect (Submarine.aiff when PROJEKT_TERMINAL=1)
