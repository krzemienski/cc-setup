#!/usr/bin/env node
// PreToolUse hook: Block code that references ANTHROPIC_API_KEY or non-SDK AI imports.
// Enforces the Agent SDK auth mandate — SessionForge uses @anthropic-ai/claude-agent-sdk
// exclusively, which inherits auth from the CLI. Zero API keys.
//
// Matches: Write, Edit, MultiEdit
// Blocks if content contains forbidden API key references or non-SDK AI imports.

const FORBIDDEN_PATTERNS = [
  // API key references
  { pattern: /ANTHROPIC_API_KEY/i, reason: "ANTHROPIC_API_KEY reference" },
  { pattern: /OPENAI_API_KEY/i, reason: "OPENAI_API_KEY reference" },
  { pattern: /process\.env\.(ANTHROPIC|OPENAI|AI)_/i, reason: "AI API key env var reference" },

  // Non-SDK AI imports (direct API clients)
  { pattern: /from\s+['"]@anthropic-ai\/sdk['"]/, reason: "Direct Anthropic SDK import (use @anthropic-ai/claude-agent-sdk instead)" },
  { pattern: /from\s+['"]anthropic['"]/, reason: "Direct Anthropic SDK import (use @anthropic-ai/claude-agent-sdk instead)" },
  { pattern: /require\(['"]@anthropic-ai\/sdk['"]\)/, reason: "Direct Anthropic SDK require (use @anthropic-ai/claude-agent-sdk instead)" },
  { pattern: /require\(['"]anthropic['"]\)/, reason: "Direct Anthropic SDK require (use @anthropic-ai/claude-agent-sdk instead)" },
  { pattern: /new\s+Anthropic\s*\(/, reason: "Direct Anthropic client instantiation (use query() from agent SDK instead)" },

  // API key configuration patterns
  { pattern: /apiKey:\s*process\.env/, reason: "API key from env var (SessionForge uses SDK auth inheritance, not API keys)" },
  { pattern: /api_key\s*[=:]\s*["']sk-/, reason: "Hardcoded API key" },
];

// Only enforce in SessionForge project
const SESSIONFORGE_PATHS = [
  /sessionforge/i,
];

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const filePath = toolInput.file_path || toolInput.filePath || '';
    const content = toolInput.content || toolInput.new_string || '';

    // Only enforce in SessionForge paths
    const isSessionForge = SESSIONFORGE_PATHS.some(p => p.test(filePath));
    if (!isSessionForge || !content) {
      process.exit(0);
    }

    // Skip non-source files
    if (/\.(md|txt|json|yaml|yml|css|scss|html)$/.test(filePath)) {
      process.exit(0);
    }

    // Check for forbidden patterns
    for (const { pattern, reason } of FORBIDDEN_PATTERNS) {
      if (pattern.test(content)) {
        const output = {
          decision: "block",
          reason: `BLOCKED: ${reason} detected in "${filePath}".\n\n` +
            `AGENT SDK AUTH MANDATE (SessionForge):\n` +
            `This project uses @anthropic-ai/claude-agent-sdk exclusively.\n` +
            `The SDK's query() function inherits auth from the Claude CLI session.\n` +
            `There are ZERO API keys. NEVER reference ANTHROPIC_API_KEY.\n` +
            `NEVER import @anthropic-ai/sdk directly. NEVER instantiate new Anthropic().\n\n` +
            `Correct pattern:\n` +
            `  import { query } from "@anthropic-ai/claude-agent-sdk";\n` +
            `  delete process.env.CLAUDECODE; // required in dev\n` +
            `  for await (const msg of query({ prompt, options })) { ... }`
        };
        process.stdout.write(JSON.stringify(output));
        process.exit(0);
      }
    }

    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
