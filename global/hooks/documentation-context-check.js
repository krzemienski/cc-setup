#!/usr/bin/env node
// UserPromptSubmit hook: Remind to check documentation and use sequential
// thinking before starting any implementation work.
//
// Injects reminders to:
// 1. Check Context7/deepwiki for library/framework docs
// 2. Use sequential-thinking MCP to reason through the request
// 3. Explore the codebase before making changes

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const userMessage = (data.message || data.content || '').trim();
    const lowerMessage = userMessage.toLowerCase();

    // Skip for slash commands
    if (/^\//.test(lowerMessage)) {
      process.exit(0);
    }

    // Skip for pure greetings/acknowledgments
    if (/^(hi|hello|hey|thanks|thank you|ok|yes|no|sure|looks good|lgtm)\s*[.!?]*$/i.test(userMessage)) {
      process.exit(0);
    }

    // Skip for git/meta operations
    if (/^(commit|push|pr |status|help|cancel|clear)\b/.test(lowerMessage)) {
      process.exit(0);
    }

    // Skip for continuation prompts
    if (/please continue|continue the conversation|continue from where/i.test(lowerMessage)) {
      process.exit(0);
    }

    // Detect action intent — broader than before
    // Previous version required specific verbs AND 8+ words, missing many real requests
    const hasActionIntent = /(add|create|build|implement|fix|update|change|modify|refactor|set up|install|configure|write|make|do |analyze|investigate|debug|remove|delete|move|rename|migrate|convert|replace|improve|optimize|enhance|extend|integrate|connect|wire|hook|deploy|run|execute|test|validate|check|audit|review|scan|search|find|explore|research|look into)/i.test(lowerMessage);

    const wordCount = userMessage.trim().split(/\s+/).length;

    // Trigger for action-oriented messages with 3+ words
    // Previous threshold of 8 words was way too high
    if (wordCount < 3 || !hasActionIntent) {
      process.exit(0);
    }

    const message =
      'BEFORE IMPLEMENTING: (1) Think through the request step by step. ' +
      '(2) If using a library/API, check Context7 MCP for current docs. ' +
      '(3) Read full files before editing — never skim.';

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
