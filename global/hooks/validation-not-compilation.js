#!/usr/bin/env node
// PostToolUse hook: When build/compile commands succeed, remind that
// compilation alone is NOT functional validation.
//
// Matches: Bash
// Detects build/compile commands and injects a reminder.

const BUILD_PATTERNS = [
  /\bnpm run build\b/,
  /\bbun run build\b/,
  /\byarn build\b/,
  /\bnext build\b/,
  /\btsc\b/,
  /\bgo build\b/,
  /\bcargo build\b/,
  /\bswift build\b/,
  /\bxcodebuild\b/,
  /\bmake\b/,
  /\bgcc\b/,
  /\bg\+\+\b/,
  /\bpython.*setup\.py\b/,
  /\bpip install\b/,
  /\bnpx tsc/,
  /\bbunx tsc/,
];

// Commands that ARE validation (don't warn on these)
const VALIDATION_PATTERNS = [
  /\bcurl\b/,
  /\bplaywright\b/,
  /\bxcrun simctl/,
  /\bnext dev\b/,
  /\bnpm run dev\b/,
  /\bbun run dev\b/,
  /localhost/,
  /screenshot/,
];

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const command = toolInput.command || '';

    if (!command) {
      process.exit(0);
    }

    // Skip if this is already a validation command
    for (const vp of VALIDATION_PATTERNS) {
      if (vp.test(command)) {
        process.exit(0);
      }
    }

    // Check if this is a build/compile command
    let isBuild = false;
    for (const bp of BUILD_PATTERNS) {
      if (bp.test(command)) {
        isBuild = true;
        break;
      }
    }

    if (!isBuild) {
      process.exit(0);
    }

    const message =
      'REMINDER: Compilation/build success is NOT functional validation. ' +
      'A successful build only proves the code compiles — it does NOT prove the feature works. ' +
      'You MUST exercise the feature through the actual UI (Playwright MCP, curl, simulator) ' +
      'and capture evidence before claiming any task is complete. ' +
      'See skill: functional-validation and gate-validation-discipline.';

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
