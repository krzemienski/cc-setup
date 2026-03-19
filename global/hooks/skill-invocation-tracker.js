#!/usr/bin/env node
// PostToolUse hook: Track skill invocations. After enough tool calls without
// any skill being invoked, inject a stronger reminder. This catches sessions
// where the UserPromptSubmit reminder fires but gets ignored.
//
// Matches: Bash|Edit|Write|MultiEdit
// (fires on common implementation tools — if many calls happen without
// a Skill call, the session likely skipped skill evaluation)

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);

    // Check conversation for any skill invocation
    const conversationText = JSON.stringify(data.conversation || data.messages || '');

    const hasSkillInvocation =
      /Skill tool|"skill":|invoke.*skill|functional-validation|gate-validation|security-scan|create-validation-plan/i.test(conversationText);

    if (hasSkillInvocation) {
      process.exit(0);
    }

    // Count how many implementation tool calls have happened
    // (rough heuristic: check for Edit/Write/Bash patterns in conversation)
    const editCount = (conversationText.match(/"Edit"|"Write"|"MultiEdit"/g) || []).length;

    // Only warn after significant implementation work without skills
    if (editCount < 5) {
      process.exit(0);
    }

    const message =
      'SKILL MANDATE WARNING: Multiple code changes made without ANY skill invocation. ' +
      'This is a documented recurring violation. Invoke /functional-validation, ' +
      '/gate-validation-discipline, or other relevant skills NOW.';

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
