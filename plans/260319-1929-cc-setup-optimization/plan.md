# CC-Setup Full Optimization & Installation Plan (v2)

## RALPLAN-DR Summary

### Principles
1. **Single source of truth** — cc-setup repo is the canonical config; machine state is a deployment artifact
2. **No secrets in git** — all credentials use `${ENV_VAR}` placeholders, resolved at install time
3. **Context efficiency** — minimize token overhead from hooks/rules while maximizing signal
4. **Zero overlap** — no duplicate functionality between custom skills, plugins, hooks, and MCP servers
5. **Install = complete** — running `install.sh` should produce a fully working setup, not a partial one

### Decision Drivers
1. **install.sh is incomplete** — skills, claude.json MCP config, and project templates are not deployed
2. **backup.sh leaks secrets** — MCP configs copied raw without stripping API keys (caused push rejection)
3. **17 plugins with 400+ skills** — high overlap probability with custom hooks/rules; context bloat risk

### Viable Options

**Option A: Patch existing scripts (Recommended)**
- Fix install.sh, backup.sh, restore.sh, diff.sh, health.sh to handle all artifacts
- Add concrete secret-stripping and injection via shared lib/secrets.sh
- Audit plugin overlap and document
- Create system diagram
- Pros: Minimal change, builds on working foundation, fast to implement
- Cons: Doesn't address plugin pruning (deferred to user decision after audit)

**Option B: Full rewrite with plugin consolidation**
- Rewrite all scripts with proper secret management
- Prune overlapping plugins, restructure repo
- Pros: Cleaner long-term
- Cons: High risk of breaking working setup, over-engineering for current needs

**Alternative rejected:** Option B — current scripts work correctly for covered scope. Issue is coverage gaps, not architectural flaws.

---

## Phases

### Phase 1: Shared Secret Management Library

Create `lib/secrets.sh` with two functions used by all scripts.

**Known secret locations (4 keys across 2 MCP configs):**

| File | jq path | Env var | Format |
|------|---------|---------|--------|
| mcp.json | `.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN` | `GITHUB_PERSONAL_ACCESS_TOKEN` | env object |
| mcp.json | `.mcpServers["firecrawl-mcp"].env.FIRECRAWL_API_KEY` | `FIRECRAWL_API_KEY` | env object |
| mcp.json | `.mcpServers.context7.headers.CONTEXT7_API_KEY` | `CONTEXT7_API_KEY` | headers object |
| claude.json | `.mcpServers.stitch.headers["X-Goog-Api-Key"]` | `GOOGLE_API_KEY` | headers object |

**`strip_secrets(file)`** — replaces real values with `${ENV_VAR}` placeholders:
```bash
jq '
  .mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PERSONAL_ACCESS_TOKEN}" |
  .mcpServers["firecrawl-mcp"].env.FIRECRAWL_API_KEY = "${FIRECRAWL_API_KEY}" |
  .mcpServers.context7.headers.CONTEXT7_API_KEY = "${CONTEXT7_API_KEY}"
' "$file"
# claude.json variant:
jq '.mcpServers.stitch.headers["X-Goog-Api-Key"] = "${GOOGLE_API_KEY}"' "$file"
```

**`inject_secrets(file)`** — replaces `${ENV_VAR}` placeholders with .env values using `sed`:
```bash
sed -e "s|\${GITHUB_PERSONAL_ACCESS_TOKEN}|${GITHUB_PERSONAL_ACCESS_TOKEN:-}|g" \
    -e "s|\${FIRECRAWL_API_KEY}|${FIRECRAWL_API_KEY:-}|g" \
    -e "s|\${CONTEXT7_API_KEY}|${CONTEXT7_API_KEY:-}|g" \
    -e "s|\${GOOGLE_API_KEY}|${GOOGLE_API_KEY:-}|g" "$file"
```
Note: `sed` chosen over `envsubst` because `envsubst` is not default on macOS.

**`validate_json(file)`** — post-substitution check:
```bash
jq . "$file" > /dev/null 2>&1 || { echo "ERR: $file is not valid JSON after substitution"; return 1; }
```

### Phase 2: Fix All Scripts

**install.sh additions:**
- [ ] Source `lib/secrets.sh`
- [ ] Deploy `mcp/claude.json.template` → `~/.claude.json` via `inject_secrets` + `validate_json`
- [ ] Deploy `mcp/mcp.json.template` → `~/.mcp.json` via `inject_secrets` + `validate_json` (replace raw `cp`)
- [ ] Deploy `skills/` → `~/.claude/skills/` (rsync, same pattern as rules/hooks/agents)
- [ ] Run `validate_json` on settings.json, .mcp.json, .claude.json after deploy

**backup.sh fixes:**
- [ ] Source `lib/secrets.sh`
- [ ] Replace raw `cp` at line 34 with `strip_secrets` for mcp.json.template
- [ ] Replace `jq` extract at line 40 with `jq '{mcpServers}' | strip_secrets` for claude.json.template

**restore.sh additions:**
- [ ] Source `lib/secrets.sh`
- [ ] Deploy `claude.json` MCP config via `inject_secrets`
- [ ] Deploy skills (rsync)
- [ ] Run `validate_json` on all deployed JSON files

**diff.sh additions:**
- [ ] Add skills diff: `diff <(ls ~/cc-setup/skills/) <(ls ~/.claude/skills/)`
- [ ] Add MCP config diff (after stripping secrets from live copy for safe comparison)

**health.sh additions:**
- [ ] Add skills presence check: verify `~/.claude/skills/cc-health/SKILL.md` etc. exist
- [ ] Add MCP JSON validation: `jq . ~/.mcp.json > /dev/null && jq . ~/.claude.json > /dev/null`

### Phase 3: Update .env.template

```
# MCP Server API Keys
GITHUB_PERSONAL_ACCESS_TOKEN=__YOUR_TOKEN__    # github.com → Settings → Developer settings → PAT
FIRECRAWL_API_KEY=__YOUR_KEY__                 # firecrawl.dev → Dashboard → API Keys
CONTEXT7_API_KEY=__YOUR_KEY__                  # context7.com → Account → API Keys
GOOGLE_API_KEY=__YOUR_KEY__                    # console.cloud.google.com → APIs & Services → Credentials
```

### Phase 4: Plugin & Skill Overlap Audit

- [ ] Map all 17 enabled plugins and their primary skills
- [ ] Cross-reference with custom hooks (28) and rules (10)
- [ ] Identify overlapping functionality (e.g., block-test-files hook vs plugin test-blocking skills)
- [ ] Document findings in `plans/reports/` — which plugins to keep, which are redundant
- [ ] Present recommendations to user (plugin pruning is a user decision)

### Phase 5: System Diagram — Context Inheritance Map

Create a Mermaid diagram showing:
- [ ] CLAUDE.md (global ~/.claude/) → project CLAUDE.md → .claude/rules/ → hooks → skills
- [ ] Hook lifecycle: SessionStart → UserPromptSubmit → PreToolUse → PostToolUse → SubagentStart/Stop → Stop
- [ ] MCP server topology grouped by purpose (code intel, web, design, memory, dev tools)
- [ ] Plugin layer interaction with custom config
- [ ] cc-setup repo → deploy scripts → installed config relationship

### Phase 6: Cleanup & Documentation

- [ ] Remove `archive/` reference from README.md
- [ ] Update README with: skills, project templates, lib/ directory, env vars needed
- [ ] Document context flow for future maintainability

### Phase 7: Functional Validation

- [ ] Run `install.sh` and verify ALL artifacts deployed (settings, CLAUDE.md, rules, hooks, agents, skills, both MCP configs)
- [ ] Run `health.sh` — all checks green including new skills/MCP checks
- [ ] Run `backup.sh` and `grep` output for real API key patterns (must find zero)
- [ ] Run `diff.sh` — should show "in sync" for all artifact types
- [ ] Verify at least 2 MCP servers respond (e.g., `jq . ~/.mcp.json` valid, health.sh passes)
- [ ] `git add -A && git diff --cached` — verify no secrets in staged changes
- [ ] Commit and push clean — no GitHub secret scanning blocks

## Success Criteria
1. `install.sh` deploys ALL artifacts including skills and both MCP configs with secrets injected
2. `backup.sh` strips all 4 known API keys before writing to repo
3. `diff.sh` detects drift in skills and MCP configs (not just rules/hooks/agents)
4. `health.sh` validates skills presence and MCP JSON integrity
5. All JSON files pass `jq` validation after deploy
6. Plugin overlap audit completed with documented recommendations
7. System diagram accurately represents context inheritance flow
8. Git push succeeds without secret scanning blocks

## ADR: Secret Management Approach

**Decision:** sed-based substitution with shared lib/secrets.sh
**Drivers:** macOS compatibility (no envsubst), heterogeneous key locations, need for both inject and strip directions
**Alternatives considered:** envsubst (not default on macOS), per-script inline sed (DRY violation), git-crypt (overkill for config templates)
**Why chosen:** Works on stock macOS, single enforcement point, bidirectional (strip for backup, inject for deploy)
**Consequences:** New keys must be added to lib/secrets.sh, .env.template, and the jq paths table above
**Follow-ups:** If >10 keys accumulate, consider migrating to a key-value loop approach
