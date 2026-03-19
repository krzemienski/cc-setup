#!/usr/bin/env node
// PreToolUse hook: Warn if writing/editing source code without any planning phase
// detected in the current session.
//
// Matches: Write|Edit|MultiEdit
// Checks if the file being modified is a source file and whether any planning
// skill or agent has been invoked. Injects advisory if no planning detected.

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};

    // Get file path being written/edited
    const filePath = toolInput.file_path || toolInput.path || '';

    // Only care about source code files
    if (!/\.(tsx?|jsx?|py|rs|go|swift|vue|svelte)$/.test(filePath)) {
      process.exit(0);
    }

    // Skip config/generated files
    if (/node_modules|\.next|dist|build|\.lock|package\.json|tsconfig/.test(filePath)) {
      process.exit(0);
    }

    // Skip small files like CLAUDE.md edits, memory files, hook files
    if (/CLAUDE\.md|memory\/|\.claude\/|\.omc\//.test(filePath)) {
      process.exit(0);
    }

    // Check conversation context for planning signals
    const conversationText = JSON.stringify(data.conversation || data.messages || '');
    const hasPlanning =
      /\/ralplan|\/plan|\/omc-plan|planner.*agent|implementation plan|phase \d|step \d.*of/i.test(conversationText) ||
      /EnterPlanMode|ExitPlanMode|plan mode/i.test(conversationText);

    if (hasPlanning) {
      process.exit(0);
    }

    const message =
      'PLANNING CHECK: No planning phase detected in this session. ' +
      'Consider /ralplan or /plan before writing source code. ' +
      'Jumping to execution without planning is a recurring violation.';

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
