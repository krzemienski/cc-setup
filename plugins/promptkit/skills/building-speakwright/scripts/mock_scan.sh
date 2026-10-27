#!/usr/bin/env bash
# mock_scan: fail when the repository contains mocks, stubs, test doubles, or test files.
# The Iron Rule for Speakwright: fix the real system instead. Exit 1 on any hit.
# Skipped: .claude/ and tools/skill-source/ (skill eval fixtures, not product code), .planning/ evidence.
# usage: mock_scan.sh [repo-root]
set -euo pipefail
ROOT="${1:-.}"
EXCLUDE=(--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build \
         --exclude-dir=.expo --exclude-dir=ios/Pods --exclude-dir=.planning --exclude-dir=.claude \
         --exclude-dir=evidence --exclude-dir=agent-logs --exclude-dir=skill-source)
hits=0

files=$(find "$ROOT" \( -path '*/node_modules' -o -path '*/.git' -o -path '*/.claude' -o -path '*/.planning' -o -path '*/tools/skill-source' \) -prune -o \
  -type f \( -name '*.test.*' -o -name '*.spec.*' -o -name '*_test.*' -o -name 'test_*.py' \) -print -o \
  -type d \( -name '__mocks__' -o -name '__tests__' -o -name 'mocks' -o -name 'stubs' -o -name 'fixtures-mock' \) -print)
if [ -n "$files" ]; then echo "test or mock files:"; echo "$files"; hits=1; fi

pattern='jest\.mock\(|vi\.mock\(|jest\.fn\(|vi\.fn\(|sinon\.|from ["'"'"']msw|require\(["'"'"']nock|nock\(|mockResolvedValue|mockReturnValue|MockProvider|TEST_MODE|isTestMode|FAKE_API|createMock|unittest\.mock|MagicMock|fake-indexeddb|new InMemory'
code=$(grep -RInE "${EXCLUDE[@]}" --include='*.ts' --include='*.tsx' --include='*.js' --include='*.mjs' --include='*.py' --include='*.json' "$pattern" "$ROOT" || true)
if [ -n "$code" ]; then echo "mock patterns in code:"; echo "$code"; hits=1; fi

deps=$(grep -RInE --include=package.json --exclude-dir=node_modules '"(jest|vitest|msw|nock|sinon|@testing-library/[^"]+|fake-indexeddb)"\s*:' "$ROOT" || true)
if [ -n "$deps" ]; then echo "mock or unit-test dependencies:"; echo "$deps"; hits=1; fi

if [ "$hits" -eq 0 ]; then echo "mock_scan: clean"; else echo "mock_scan: FAIL — remove these and validate against the real system"; fi
exit "$hits"
