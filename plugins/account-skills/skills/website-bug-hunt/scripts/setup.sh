#!/usr/bin/env bash
# website-bug-hunt — Playwright engine setup
# Idempotent. Works in restricted Linux sandboxes (no root, ARM64) and normal machines.
set -e

WORKDIR="${1:-$PWD/hunt-workspace}"
mkdir -p "$WORKDIR/engine"
cd "$WORKDIR/engine"

# 1. Install playwright locally (no global npm prefix needed)
if [ ! -d node_modules/playwright ]; then
  npm init -y >/dev/null 2>&1 || true
  npm install playwright >/dev/null 2>&1
fi

# 2. Download the chromium binary (headless shell included)
npx playwright install chromium 2>&1 | tail -1 || true

# 3. Fix missing shared libs without root (common in sandboxes).
#    Check the headless shell's dynamic deps; fetch any missing lib as a .deb
#    via apt-get download (works unprivileged) and extract next to us.
LIBDIR="$WORKDIR/engine/extralibs"
mkdir -p "$LIBDIR"
SHELL_BIN=$(ls "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | head -1)
if [ -n "$SHELL_BIN" ]; then
  MISSING=$(ldd "$SHELL_BIN" 2>/dev/null | awk '/not found/ {print $1}')
  for lib in $MISSING; do
    # map lib name (e.g. libXdamage.so.1) to debian package (libxdamage1)
    pkg=$(echo "$lib" | sed -E 's/^lib//; s/\.so\.([0-9]+).*/\1/' | tr 'A-Z' 'a-z')
    pkg="lib${pkg}"
    (cd /tmp && apt-get download "$pkg" 2>/dev/null && dpkg -x "$pkg"*.deb "$LIBDIR" && rm -f "$pkg"*.deb) || \
      echo "WARN: could not fetch $pkg for $lib — try: sudo apt-get install $pkg"
  done
fi

# 4. Emit the env line every run must source
ARCH_DIR=$(find "$LIBDIR" -type d -name "*-linux-gnu" 2>/dev/null | head -1)
echo "export LD_LIBRARY_PATH=${ARCH_DIR:-$LIBDIR}:\$LD_LIBRARY_PATH" > "$WORKDIR/engine/env.sh"
echo "Setup complete. Before every run: source $WORKDIR/engine/env.sh"

# 5. Smoke test
export LD_LIBRARY_PATH="${ARCH_DIR:-$LIBDIR}:$LD_LIBRARY_PATH"
node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage();
  await p.goto('https://example.com', { timeout: 20000 });
  console.log('SMOKE OK:', await p.title());
  await b.close();
})().catch(e => { console.error('SMOKE FAIL:', e.message); process.exit(1); });"
