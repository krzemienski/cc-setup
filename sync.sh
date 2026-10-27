#!/usr/bin/env bash
# Pull the latest account-sync branch and re-run the installer.
#   ./sync.sh            pull + install
#   ./sync.sh --dry-run  pull + show what would change
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"
BEFORE="$(git rev-parse HEAD)"
git pull --ff-only origin account-sync
AFTER="$(git rev-parse HEAD)"
if [ "$BEFORE" != "$AFTER" ]; then
  echo "Plugins changed since last sync (re-upload these to claude.ai):"
  git diff --name-only "$BEFORE" "$AFTER" -- plugins | cut -d/ -f2 | sort -u | sed 's/^/  - /'
fi
exec "$REPO_DIR/install.sh" "$@"
