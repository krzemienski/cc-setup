#!/usr/bin/env node
// PreToolUse hook: When editing files, remind to read the FULL file first.
// Prevents skimming — you must understand the complete file before modifying it.
//
// Matches: Edit, MultiEdit
// Injects context reminder about reading files thoroughly.

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const filePath = toolInput.file_path || '';

    if (!filePath) {
      process.exit(0);
    }

    // Skip config files, lock files, and auto-generated files
    const skipPatterns = [
      /package\.json$/,
      /\.lock$/,
      /\.json$/,
      /\.claude\//,
      /\.omc\//,
      /node_modules/,
    ];

    for (const pattern of skipPatterns) {
      if (pattern.test(filePath)) {
        process.exit(0);
      }
    }

    const message =
      `Editing ${filePath}. Ensure you have:\n` +
      '- Read the FULL file (not just a snippet) — use Read without offset/limit\n' +
      '- Understood the surrounding context and how this code connects to other modules\n' +
      '- Never skim — if the file is large, read it in sections but read ALL of it';

    const output = {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));
  } catch (e) {
    process.exit(0);
  }
});
