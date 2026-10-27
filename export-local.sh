#!/usr/bin/env bash
# Run on the Mac. Copies Mac-only config into this repo so it can sync to claude.ai:
#   - ~/.claude/CLAUDE.md and ~/.claude/rules/*.md        -> plugins/nick-core/{directives,rules}
#   - skills in ~/.claude/skills not already in the repo   -> plugins/nick-core/skills
#   - plugins enabled in Claude Code but not on claude.ai  -> plugins/<name> (+ marketplace.json)
# Then scans for secrets, commits only those paths, and pushes the account-sync branch.
#
#   ./export-local.sh --dry-run   list what would be copied
#   ./export-local.sh             copy, commit, push
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
CL="$HOME/.claude"
EXCL=(--exclude '.venv' --exclude 'node_modules' --exclude '__pycache__' --exclude '.git' --exclude '.env' --exclude '.env.*'
      --exclude '*.pid' --exclude '.DS_Store' --exclude '.in_use' --exclude '.credentials*' --exclude 'secrets')
command -v rsync >/dev/null && command -v python3 >/dev/null || { echo "needs rsync and python3" >&2; exit 1; }

copy() { if [ "$DRY" = 1 ]; then echo "  would copy $1 -> ${2#$REPO/}"; else mkdir -p "$2"; rsync -aL "${EXCL[@]}" "$1" "$2"; fi; }

echo "== nick-core directives and rules"
copy "$CL/CLAUDE.md" "$REPO/plugins/nick-core/directives/"
copy "$CL/rules/" "$REPO/plugins/nick-core/rules/"

echo "== local skills not already in the repo"
python3 - "$REPO" "$CL/skills" > "$REPO/.export-skills.txt" <<'PY'
import os, sys, glob
repo, src = sys.argv[1], sys.argv[2]
have = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(repo, "plugins", "*", "skills", "**", "SKILL.md"), recursive=True)
        if "/nick-core/" not in p}
for name in sorted(os.listdir(src)):
    path = os.path.realpath(os.path.join(src, name))
    if os.path.isdir(path) and os.path.isfile(os.path.join(path, "SKILL.md")) and name not in have:
        print(f"{name}\t{path}")
PY
N_SK=$(wc -l < "$REPO/.export-skills.txt" | tr -d ' ')
echo "  $N_SK skills"
while IFS=$'\t' read -r name path; do copy "$path/" "$REPO/plugins/nick-core/skills/$name/"; done < "$REPO/.export-skills.txt"

echo "== plugins enabled locally but missing from claude.ai"
python3 - "$REPO" "$CL/settings.json" "$CL/plugins/installed_plugins.json" > "$REPO/.export-plugins.txt" <<'PY'
import json, os, sys
repo, settings, installed = sys.argv[1:4]
have = {p["name"] for p in json.load(open(os.path.join(repo, ".claude-plugin", "marketplace.json")))["plugins"]}
enabled = [k for k, v in (json.load(open(settings)).get("enabledPlugins") or {}).items() if v]
inst = json.load(open(installed)); inst = inst.get("plugins", inst)
for key in sorted(enabled):
    name = key.rsplit("@", 1)[0]
    if name in have: continue
    entries = inst.get(key) or []
    path = entries[0].get("installPath") if entries and isinstance(entries[0], dict) else None
    print(f"{name}\t{path or 'MISSING'}\t{key}")
PY
while IFS=$'\t' read -r name path key; do
  if [ "$path" = MISSING ] || [ ! -d "$path" ]; then echo "  ! $key: no install path found, skipped"; continue; fi
  copy "$path/" "$REPO/plugins/$name/"
done < "$REPO/.export-plugins.txt"
echo "  $(wc -l < "$REPO/.export-plugins.txt" | tr -d ' ') plugins"

[ "$DRY" = 1 ] && { rm -f "$REPO/.export-skills.txt" "$REPO/.export-plugins.txt"; echo "dry-run: nothing written"; exit 0; }

echo "== marketplace.json"
python3 - "$REPO" <<'PY'
import json, os, sys
repo = sys.argv[1]; mpath = os.path.join(repo, ".claude-plugin", "marketplace.json")
mk = json.load(open(mpath)); have = {p["name"] for p in mk["plugins"]}
for name in sorted(os.listdir(os.path.join(repo, "plugins"))):
    pj = os.path.join(repo, "plugins", name, ".claude-plugin", "plugin.json")
    if name in have or not os.path.isfile(pj): continue
    meta = json.load(open(pj))
    mk["plugins"].append({"name": name, "source": f"./plugins/{name}", "description": (meta.get("description") or "")[:300], "version": meta.get("version") or "0.0.0"})
    print("  added", name)
json.dump(mk, open(mpath, "w"), indent=2)
PY

echo "== secret scan"
HITS=$(python3 - "$REPO/plugins/nick-core" $(cut -f1 "$REPO/.export-plugins.txt" | sed "s|^|$REPO/plugins/|") <<'PY'
import os, re, sys
token = re.compile(r'sk-ant-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[bp]-[0-9A-Za-z-]{20,}')
pem = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----\s*\n[A-Za-z0-9+/=]{40,}')
allow = {"AKIAIOSFODNN7EXAMPLE"}   # AWS's published documentation sample
for root in sys.argv[1:]:
    for d, _, files in os.walk(root):
        for f in files:
            p = os.path.join(d, f)
            try:
                t = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if any(m not in allow for m in token.findall(t)) or pem.search(t):
                print(p)
PY
)
if [ -n "$HITS" ]; then echo "Possible secrets found; nothing committed. Review:"; echo "$HITS"; exit 1; fi
echo "  clean"

echo "== commit and push"
cd "$REPO"
git add .claude-plugin/marketplace.json plugins/nick-core $(cut -f1 .export-plugins.txt | sed 's|^|plugins/|')
rm -f .export-skills.txt .export-plugins.txt
if git diff --cached --quiet; then echo "  nothing new"; exit 0; fi
git commit -q -m "feat: export Mac-only directives, skills and plugins" || { echo "commit failed; changes are staged" >&2; exit 1; }
git push -q origin account-sync || { echo "push failed; the commit is local, run: git push origin account-sync" >&2; exit 1; }
echo "  pushed"
echo "Upload these to claude.ai (Customize > Plugins > Add): nick-core and any plugin added above."
