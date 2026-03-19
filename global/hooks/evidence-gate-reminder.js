#!/usr/bin/env node
// PreToolUse hook: When marking tasks complete or claiming completion,
// inject a mandatory evidence checklist reminder.
//
// Matches: TaskUpdate
// Triggers when status is being set to "completed".

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const status = toolInput.status || '';

    if (status !== 'completed') {
      process.exit(0);
    }

    const message =
      'GATE VALIDATION CHECKPOINT — Before marking this task complete, verify:\n' +
      '[ ] Did you PERSONALLY examine the evidence (not just receive a report)?\n' +
      '[ ] Did you VIEW screenshots and confirm their CONTENT (not just existence)?\n' +
      '[ ] Did you EXAMINE command output (not just exit codes)?\n' +
      '[ ] Can you CITE specific evidence for each validation criterion?\n' +
      '[ ] Would a skeptical reviewer agree this is complete?\n\n' +
      'If ANY checkbox is unchecked, do NOT mark complete. ' +
      'Run the functional-validation skill and capture real evidence first.';

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
