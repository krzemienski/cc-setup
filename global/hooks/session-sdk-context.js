#!/usr/bin/env node
// SessionStart hook: Inject Agent SDK auth context at the start of every session
// when working in the SessionForge project. This ensures the main agent (not just
// subagents) has the SDK auth rules from turn 1.
//
// Matches: startup|resume|clear|compact

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const cwd = data.cwd || process.cwd();

    // Only inject in SessionForge project
    if (!/sessionforge/i.test(cwd)) {
      process.exit(0);
    }

    const message =
      'SESSION CONTEXT — AGENT SDK AUTH:\n' +
      'This project uses @anthropic-ai/claude-agent-sdk. Auth inherits from Claude CLI.\n' +
      'ZERO API keys. NEVER suggest ANTHROPIC_API_KEY. NEVER import @anthropic-ai/sdk.\n' +
      'CLAUDECODE env fix already applied to all 12 SDK files — do NOT re-apply.';

    const output = {
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));
  } catch (e) {
    process.exit(0);
  }
});
