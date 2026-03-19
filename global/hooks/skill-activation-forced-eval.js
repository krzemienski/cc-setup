#!/usr/bin/env node
// UserPromptSubmit hook: Forces explicit skill evaluation and invocation
// before any implementation work begins.
//
// Requires Claude to scan available skills, evaluate relevance, and
// invoke all matching skills BEFORE writing any code.

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const userMessage = (data.message || data.content || '').trim();
    const lowerMessage = userMessage.toLowerCase();

    // Skip for slash commands (they ARE skill invocations)
    if (/^\//.test(lowerMessage)) {
      process.exit(0);
    }

    // Skip for pure greetings and acknowledgments (exact or near-exact)
    const skipExact = [
      /^(hi|hello|hey|thanks|thank you|ok|yes|no|sure|looks good|lgtm|cool|great|nice|got it|understood)\s*[.!?]*$/i,
    ];
    for (const pattern of skipExact) {
      if (pattern.test(userMessage)) {
        process.exit(0);
      }
    }

    // Skip for very short read-only questions (1-3 words ending in ?)
    const wordCount = userMessage.trim().split(/\s+/).length;
    if (wordCount <= 3 && userMessage.endsWith('?')) {
      process.exit(0);
    }

    // Skip for git/meta operations
    if (/^(commit|push|pr |status|help|cancel|clear)\b/.test(lowerMessage)) {
      process.exit(0);
    }

    // Skip for continuation prompts from session restore
    if (/please continue|continue the conversation|continue from where/i.test(lowerMessage)) {
      process.exit(0);
    }

    // Everything else gets the skill reminder — even short messages
    // The previous version skipped messages < 5 words which let actionable
    // requests like "fix the build" or "do the todos" slip through
    const message =
      'SKILL CHECK: Before implementing, scan available skills. ' +
      'Invoke any that match (even 1% chance). ' +
      'Key: functional-validation, gate-validation-discipline, create-validation-plan, security-scan.';

    const output = {
      hookSpecificOutput: {
        hookEventName: "UserPromptSubmit",
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));
  } catch (e) {
    process.exit(0);
  }
});
