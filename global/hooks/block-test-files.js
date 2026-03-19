#!/usr/bin/env node
// PreToolUse hook: Block creation of test files, mock files, and stub files.
// Enforces the functional-validation mandate — no test frameworks, no mocks.
//
// Matches: Write, Edit, MultiEdit
// Blocks if file_path matches test/mock/stub patterns.

const TEST_PATTERNS = [
  /\.test\.[jt]sx?$/,
  /\.spec\.[jt]sx?$/,
  /_test\.go$/,
  /test_[^/]+\.py$/,
  /Tests?\.swift$/,
  /\.test\.py$/,
  /\/__tests__\//,
  /\/test\/.*\.(ts|js|tsx|jsx|py|go|swift)$/,
  /\.mock\.[jt]sx?$/,
  /\.stub\.[jt]sx?$/,
  /\/mocks\//,
  /\/stubs\//,
  /\/fixtures\//,
  /\/test-utils\//,
  /\.stories\.[jt]sx?$/,  // Storybook used as test substitute
];

// Allowlist — paths that look like tests but aren't
const ALLOWLIST = [
  /e2e-evidence/,
  /validation-evidence/,
  /\.claude\//,
];

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const toolInput = data.tool_input || {};
    const filePath = toolInput.file_path || toolInput.filePath || '';

    if (!filePath) {
      process.exit(0);
    }

    // Check allowlist first
    for (const allow of ALLOWLIST) {
      if (allow.test(filePath)) {
        process.exit(0);
      }
    }

    // Check test patterns
    for (const pattern of TEST_PATTERNS) {
      if (pattern.test(filePath)) {
        const output = {
          decision: "block",
          reason: `BLOCKED: "${filePath}" matches a test/mock/stub file pattern.\n\n` +
            `FUNCTIONAL VALIDATION MANDATE: Never create test files, mock files, or stub files.\n` +
            `Instead: Build and run the real system. Validate through actual user interfaces.\n` +
            `Use skill: functional-validation for the correct protocol.`
        };
        process.stdout.write(JSON.stringify(output));
        process.exit(0);
      }
    }

    // Not a test file, allow
    process.exit(0);
  } catch (e) {
    // Silent fail — never block on hook errors
    process.exit(0);
  }
});
