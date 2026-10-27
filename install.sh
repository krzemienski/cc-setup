#!/usr/bin/env bash
# Install every plugin and skill from this marketplace (claude-account) into
# Claude Code, OMP, and the shared ~/.agents/skills folder.
#
#   ./install.sh --dry-run       show what would happen, change nothing
#   ./install.sh                 turn on the plugins listed in enabled.json (your claude.ai state),
#                                skipping any you already run from another marketplace
#   ./install.sh --all           turn on every plugin in the bundle, not just enabled.json
#   ./install.sh --force-dupes   also install plugins you already have elsewhere (hooks may run twice)
#   ./install.sh --only claude|omp|skills
#
# OMP reads Claude Code's plugin registry (~/.claude/plugins/installed_plugins.json and
# enabledPlugins), so the Claude Code step covers OMP too. The omp step only checks that.
# Every config file it touches is copied to .backups/<timestamp>/ first.
# It never deletes anything.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKET="claude-account"
DRY=0; FORCE=0; ONLY="all"; ALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --force-dupes) FORCE=1 ;;
    --all) ALL=1 ;;
    --only) shift; ONLY="$1" ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

TS="$(date +%Y%m%dT%H%M%S)"
REPORT_DIR="$REPO_DIR/.sync"; mkdir -p "$REPORT_DIR"
LOG="$REPORT_DIR/install-$TS.log"
log() { echo "$*" | tee -a "$LOG"; }
run() { if [ "$DRY" = 1 ]; then log "  [dry-run] $*"; else log "  \$ $*"; "$@" >>"$LOG" 2>&1 || { log "  ! failed (exit $?): $*"; return 1; }; fi; }

command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }

# ---------- backups ----------
BK="$REPO_DIR/.backups/$TS"
backup() { for f in "$@"; do [ -e "$f" ] && { mkdir -p "$BK$(dirname "$f")"; cp -p "$f" "$BK$f"; }; done; return 0; }
if [ "$DRY" = 0 ]; then
  backup "$HOME/.claude/plugins/installed_plugins.json" "$HOME/.claude/plugins/known_marketplaces.json" \
         "$HOME/.claude/settings.json" "$HOME/.omp/agent/config.yml" "$HOME/.omp/agent/mcp.json"
  log "backups: $BK"
fi

# ---------- plugin list + duplicate detection ----------
PLAN="$REPORT_DIR/plan-$TS.json"
python3 - "$REPO_DIR" "$HOME/.claude/plugins/installed_plugins.json" "$FORCE" "$MARKET" "$HOME/.claude/settings.json" "$ALL" > "$PLAN" <<'PY'
import json, sys, os
repo, inst_path, force, market, settings_path = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4], sys.argv[5]
take_all = sys.argv[6] == "1"
mk = json.load(open(os.path.join(repo, ".claude-plugin", "marketplace.json")))
wanted = None
enabled_file = os.path.join(repo, "enabled.json")
if not take_all and os.path.exists(enabled_file):
    wanted = set(json.load(open(enabled_file))["enabled"])
installed = {}
if os.path.exists(inst_path):
    data = json.load(open(inst_path))
    plugs = data.get("plugins", data)
    for key in plugs:
        if "@" in key:
            name, mkt = key.rsplit("@", 1)
            installed.setdefault(name, []).append(mkt)
# Only a plugin that is ENABLED from another marketplace counts as a duplicate:
# an installed-but-disabled copy elsewhere never loads, so we still install ours.
enabled = {}
if os.path.exists(settings_path):
    for key, on in (json.load(open(settings_path)).get("enabledPlugins") or {}).items():
        if on and "@" in key:
            name, mkt = key.rsplit("@", 1)
            enabled.setdefault(name, []).append(mkt)
plan = []
for p in mk["plugins"]:
    other_enabled = [m for m in enabled.get(p["name"], []) if m != market]
    already = market in enabled.get(p["name"], [])
    if wanted is not None and p["name"] not in wanted:
        action = "off-in-claude-ai"
    else:
        action = "already-installed" if already else ("skip-duplicate" if other_enabled and not force else "install")
    plan.append({"name": p["name"], "action": action, "enabled_elsewhere": other_enabled,
                 "installed_elsewhere": [m for m in installed.get(p["name"], []) if m != market]})
print(json.dumps(plan, indent=2))
PY
N_INSTALL=$(python3 -c "import json,sys;print(sum(p['action']=='install' for p in json.load(open('$PLAN'))))")
N_DUP=$(python3 -c "import json,sys;print(sum(p['action']=='skip-duplicate' for p in json.load(open('$PLAN'))))")
N_OFF=$(python3 -c "import json,sys;print(sum(p['action']=='off-in-claude-ai' for p in json.load(open('$PLAN'))))")
log "plan: $N_INSTALL to install, $N_DUP skipped as duplicates, $N_OFF left off (off in claude.ai; --all to include) (see $PLAN)"
TO_INSTALL=$(python3 -c "import json;print('\n'.join(p['name'] for p in json.load(open('$PLAN')) if p['action']=='install'))")

# ---------- Claude Code ----------
if [ "$ONLY" = all ] || [ "$ONLY" = claude ]; then
  log "== Claude Code"
  if command -v claude >/dev/null; then
    if python3 -c "import json,sys;sys.exit(0 if '$MARKET' in json.load(open('$HOME/.claude/plugins/known_marketplaces.json')) else 1)" 2>/dev/null; then
      run claude plugin marketplace update "$MARKET" || true
    else
      run claude plugin marketplace add "$REPO_DIR" || true
    fi
    while IFS= read -r p; do [ -n "$p" ] && { run claude plugin install "$p@$MARKET" || true; }; done <<< "$TO_INSTALL"
  else
    log "  claude CLI not found; skipped"
  fi
fi

# ---------- OMP ----------
if [ "$ONLY" = all ] || [ "$ONLY" = omp ]; then
  log "== OMP"
  # OMP loads Claude Code plugins from ~/.claude/plugins/installed_plugins.json + enabledPlugins,
  # and skills from ~/.agents/skills. Installing into OMP's own registry as well would load every
  # hook twice, so this step only reports what OMP will see.
  python3 - "$HOME/.claude/plugins/installed_plugins.json" "$MARKET" <<'PY' | tee -a "$LOG"
import json, sys, os
path, market = sys.argv[1], sys.argv[2]
n = 0
if os.path.exists(path):
    n = sum(1 for k in json.load(open(path)).get("plugins", {}) if k.endswith("@" + market))
print(f"  OMP will load {n} {market} plugins from Claude Code's registry"
      + ("" if n else " (none yet: start Claude Code once so it fetches them)"))
PY
fi

# ---------- ~/.agents/skills (Codex, OpenCode, OMP, Gemini CLI and other agentskills readers) ----------
if [ "$ONLY" = all ] || [ "$ONLY" = skills ]; then
  log "== ~/.agents/skills"
  DEST="$HOME/.agents/skills"; [ "$DRY" = 0 ] && mkdir -p "$DEST"
  python3 - "$REPO_DIR" "$DEST" "$DRY" "$REPORT_DIR/skills-$TS.json" <<'PY' | tee -a "$LOG"
import os, sys, glob, json
repo, dest, dry, out = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4]
linked, kept, conflicts = [], [], []
for skill_md in sorted(glob.glob(os.path.join(repo, "plugins", "*", "**", "SKILL.md"), recursive=True)):
    src = os.path.dirname(skill_md)
    plugin = os.path.relpath(src, os.path.join(repo, "plugins")).split(os.sep)[0]
    if "/templates/" in src or "/node_modules/" in src or src == os.path.join(repo, "plugins", plugin):
        continue  # skip skill templates and plugin roots that only look like skills
    name = os.path.basename(src)
    target = os.path.join(dest, name)
    if os.path.islink(target) and os.path.realpath(target) == os.path.realpath(src):  # already ours
        kept.append(name); continue
    if os.path.lexists(target):
        # keep the user's existing skill; expose ours under a plugin-qualified name
        alt = os.path.join(dest, f"{plugin}--{name}")
        if os.path.lexists(alt):
            conflicts.append({"skill": name, "plugin": plugin}); continue
        target = alt
    if not dry:
        # relative target: works from macOS and from any VM that mounts the home folder elsewhere
        os.symlink(os.path.relpath(src, os.path.dirname(target)), target)
    linked.append(os.path.basename(target))
json.dump({"linked": linked, "already_linked": kept, "unresolved_conflicts": conflicts}, open(out, "w"), indent=2)
print(f"  linked {len(linked)}, already linked {len(kept)}, unresolved {len(conflicts)}{' (dry-run)' if dry else ''}")
PY
fi

log "done. log: $LOG"
