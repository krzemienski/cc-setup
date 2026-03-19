#!/usr/bin/env node
// PreToolUse hook: Inject Agent SDK auth context into every subagent prompt
// when working in the SessionForge project.
//
// This is the #1 most violated rule in the project — subagents repeatedly
// suggest ANTHROPIC_API_KEY or direct SDK imports because they lack context.
//
// Matches: Agent
// Injects additional context about SDK auth into every agent spawn.

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const cwd = data.cwd || process.cwd();

    // Only enforce in SessionForge project
    if (!/sessionforge/i.test(cwd)) {
      process.exit(0);
    }

    const message =
      'CRITICAL CONTEXT — AGENT SDK AUTH (SessionForge):\n' +
      'This project uses @anthropic-ai/claude-agent-sdk EXCLUSIVELY for all AI features.\n' +
      'The SDK query() function inherits auth from the Claude CLI — there are ZERO API keys.\n\n' +
      'NEVER:\n' +
      '- Suggest setting up ANTHROPIC_API_KEY or any AI env vars\n' +
      '- Import from @anthropic-ai/sdk (the direct SDK) — only use @anthropic-ai/claude-agent-sdk\n' +
      '- Instantiate new Anthropic() — use query() from the agent SDK\n' +
      '- Assume AI features need local API key configuration\n\n' +
      'ALWAYS:\n' +
      '- Use: import { query } from "@anthropic-ai/claude-agent-sdk"\n' +
      '- Add: delete process.env.CLAUDECODE before any query() call in dev\n' +
      '- MCP tools query the SessionForge DB only — no external API keys needed';

    const output = {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
