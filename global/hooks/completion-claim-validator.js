#!/usr/bin/env node
// PostToolUse hook: Detect completion claims in Bash output without functional
// validation evidence. Catches patterns like "all done", "task complete",
// "build succeeded" and reminds that compilation != validation.
//
// Matches: Bash

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const stdout = (data.tool_result || data.stdout || data.output || '').toString();

    // Only trigger on build/compile success output
    const hasBuildSuccess =
      /compiled successfully|build succeeded|exit code 0|✓ Ready|Compiled.*in/i.test(stdout) ||
      /Successfully compiled|Build complete|no errors/i.test(stdout);

    if (!hasBuildSuccess) {
      process.exit(0);
    }

    // Check if there's evidence of actual validation (Playwright, screenshots, browser)
    const conversationText = JSON.stringify(data.conversation || data.messages || '');
    const hasValidation =
      /playwright|screenshot|browser_navigate|browser_snapshot|browser_click|e2e-evidence|functional.validation/i.test(conversationText);

    if (hasValidation) {
      process.exit(0);
    }

    const message =
      'BUILD SUCCESS ≠ VALIDATION. The code compiles, but has it been ' +
      'exercised through the real UI? Run /functional-validation or use ' +
      'Playwright MCP before claiming completion.';

    const output = {
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));
  } catch (e) {
    process.exit(0);
  }
});
