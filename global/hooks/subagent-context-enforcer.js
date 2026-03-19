#!/usr/bin/env node
// PreToolUse hook: When spawning subagents, ensure proper context is provided.
// Prevents blind delegation — subagents must receive relevant file paths,
// codebase context, and clear task descriptions.
//
// Matches: Agent

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const prompt = toolInput.prompt || '';

    // Check if the prompt contains sufficient context indicators
    const hasFilePaths = /\/[a-zA-Z][\w\-./]+\.[a-zA-Z]+/.test(prompt);
    const hasCodeContext = /(```|file:|path:|function |class |component |route |schema )/.test(prompt);
    const hasExploreIntent = /(explore|search|find|investigate|research|read|understand|analyze)/.test(prompt.toLowerCase());
    const isExploreAgent = (toolInput.subagent_type || '').toLowerCase().includes('explore');
    const isPlanAgent = (toolInput.subagent_type || '').toLowerCase().includes('plan');

    // Explore and Plan agents are gathering context — they don't need it upfront
    if (isExploreAgent || isPlanAgent) {
      process.exit(0);
    }

    // If prompt is short and lacks context, warn
    const promptWords = prompt.trim().split(/\s+/).length;
    const lacksContext = !hasFilePaths && !hasCodeContext && promptWords < 30;

    if (lacksContext && !hasExploreIntent) {
      const message =
        'SUBAGENT CONTEXT CHECK: This agent prompt appears to lack sufficient context.\n' +
        'Before delegating work to a subagent, ensure you have:\n' +
        '1. EXPLORED the relevant codebase area (use Explore agent or Glob/Grep/Read first)\n' +
        '2. PROVIDED specific file paths, function names, or code snippets in the prompt\n' +
        '3. DESCRIBED the full context — what exists, what needs to change, and why\n\n' +
        'Subagents without context produce generic, wrong, or conflicting output.\n' +
        'If you haven\'t read the code yet, use an Explore agent first to gather context.';

      const output = {
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          additionalContext: message
        }
      };

      process.stdout.write(JSON.stringify(output));
    }

    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
