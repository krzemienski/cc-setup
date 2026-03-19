#!/usr/bin/env node
// PostToolUse hook: Remind to restart dev server after editing route or schema files.
// Stale Next.js/Turbopack caches cause false 500 errors — this is a top-5
// recurring issue across 60 days of sessions.
//
// Matches: Edit|Write|MultiEdit

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const filePath = toolInput.file_path || toolInput.path || '';

    // Only trigger for route files, schema files, and config files that affect runtime
    const needsRestart =
      /\/route\.(ts|js)$/.test(filePath) ||
      /\/page\.(tsx|jsx)$/.test(filePath) ||
      /schema\.(ts|js)$/.test(filePath) ||
      /drizzle\.config\.(ts|js)$/.test(filePath) ||
      /middleware\.(ts|js)$/.test(filePath) ||
      /next\.config\.(ts|js|mjs)$/.test(filePath);

    if (!needsRestart) {
      process.exit(0);
    }

    const message =
      'DEV SERVER: Route/schema/config file changed. ' +
      'Restart the dev server before smoke testing — stale caches cause false 500s.';

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
