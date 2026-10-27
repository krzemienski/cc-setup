#!/usr/bin/env bash
# SessionStart (nick-core): give sessions that lack Nick's global CLAUDE.md
# (claude.ai, mobile, cloud workspaces) the same operating directives.
# On his Mac ~/.claude/CLAUDE.md already loads, so stay silent there to avoid a double injection.
# Fail-open: every path exits 0; a broken hook must never block a session from starting.
set -uo pipefail
cat >/dev/null 2>&1 || true   # drain stdin; the event payload is not needed

ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[ -n "$ROOT" ] || ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)" || exit 0
LOCAL="${HOME:-}/.claude/CLAUDE.md"
DIRECTIVES="$ROOT/directives/CLAUDE.md"
LIMIT=9000   # SessionStart output injected into context is size-capped; stay under it

if [ -f "$LOCAL" ] && head -n 1 "$LOCAL" 2>/dev/null | grep -q 'Operating Directives'; then
  exit 0
fi
[ -r "$DIRECTIVES" ] || exit 0

SIZE="$(wc -c < "$DIRECTIVES" 2>/dev/null | tr -d ' ')"
if [ -n "$SIZE" ] && [ "$SIZE" -le "$LIMIT" ]; then
  cat "$DIRECTIVES"
else
  echo "Nick's operating directives apply to every task in this session."
  echo "Before starting work, read \"$DIRECTIVES\" in full; rule files are in \"$ROOT/rules/\"."
  echo "Sections:"
  grep '^## ' "$DIRECTIVES" 2>/dev/null | sed 's/^## /- /'
fi
exit 0
