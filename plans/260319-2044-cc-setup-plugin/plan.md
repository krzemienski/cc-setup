# Plan v2: Convert cc-setup into a Claude Code Plugin

**Date:** 2026-03-19
**Status:** REVISED — Incorporating Architect + Critic feedback (iteration 1)
**Consensus:** Both reviewers agreed on simplified scope

## RALPLAN-DR Summary

### Principles
1. **Single source of truth** — One repo, two delivery mechanisms with clear boundaries
2. **No overlap** — Deduplicate agents aggressively; remove unless proven unique
3. **Plugin for portable components** — Agents, skills, commands go in plugin (auto-discovered)
4. **install.sh for config components** — Rules, CLAUDE.md, settings.json, hooks, output-styles stay deployed via script (path-dependent, can't be portable)
5. **Secret safety** — No API keys in repo; .env + inject at runtime

### Decision Drivers
1. **Hook stability** — Hooks use `__dirname` traversals to `~/.claude/`; moving them breaks 3+ critical hooks. Keep them in settings.json.
2. **CLAUDE.md ownership** — OMC manages 83% of CLAUDE.md. cc-setup must not overwrite OMC's block.
3. **Agent token cost** — 55+ agents across plugins is wasteful. Cut cc-setup agents to ~10 unique ones.

### Viable Options

**Option A: Hybrid Plugin (CHOSEN)**
- Plugin delivers: agents (~10 unique), skills (3), commands (3)
- install.sh delivers: rules/, CLAUDE.md (non-OMC only), settings.json (with hooks), output-styles/, MCP configs
- Pros: Plugin auto-discovery for agents/skills/commands; hooks stay stable in ~/.claude/hooks/; no double-fire; no __dirname breakage
- Cons: Two delivery mechanisms (but with clear, non-overlapping responsibilities)

**Option B: Full Plugin (REJECTED)**
- Rejected by Architect + Critic: hooks can't safely move to plugin due to __dirname parent traversals in session-init.cjs, scout-block.cjs, hook-logger.cjs. Plugin hooks.json + settings.json hooks = double-fire. ${CLAUDE_PLUGIN_ROOT} not available inside scripts.

**Option C: No Plugin (REJECTED)**
- No versioning, no marketplace discovery, no enable/disable per-agent. Doesn't solve the stated goal.

### ADR (Architecture Decision Record)
- **Decision:** Hybrid approach — plugin for agents/skills/commands, install.sh for everything else
- **Drivers:** Hook path dependencies, CLAUDE.md ownership, agent dedup savings
- **Alternatives considered:** Full plugin (breaks hooks), no plugin (no improvement)
- **Why chosen:** Maximizes plugin benefits while avoiding the 3 CRITICAL hook migration issues
- **Consequences:** Must maintain install.sh alongside plugin; health.sh checks both
- **Follow-ups:** Consider ESM conversion of hooks if plugin hook support improves

---

## Phase 1: Plugin Scaffold & Manifest (15 min)

**Goal:** Create plugin directory structure in cc-setup repo

### 1.1 Create plugin structure
```
cc-setup/
├── .claude-plugin/
│   ├── plugin.json            # Plugin manifest
│   └── marketplace.json       # Self-hosted marketplace
├── commands/                   # Slash commands (NEW)
│   ├── cc-health.md
│   ├── cc-sync.md
│   └── cc-install.md
├── agents/                     # ~10 unique agents (MOVED from global/agents/)
│   ├── brainstormer.md
│   ├── docs-manager.md
│   ├── fullstack-developer.md
│   ├── git-manager.md
│   ├── journal-writer.md
│   ├── mcp-manager.md
│   ├── project-manager.md
│   ├── researcher.md
│   ├── tester.md
│   └── ui-ux-designer.md
├── skills/                     # 3 auto-activating skills (MOVED from skills/)
│   ├── cc-health/SKILL.md
│   ├── cc-sync/SKILL.md
│   └── cc-index/SKILL.md
├── global/                     # NON-PLUGIN items (deployed by install.sh)
│   ├── CLAUDE.md               # Only non-OMC content (~33 lines)
│   ├── settings.json.template  # Includes all hook registrations
│   ├── rules/                  # 10 rule files
│   ├── hooks/                  # All hook scripts (stay here, not in plugin)
│   │   ├── *.js, *.cjs
│   │   ├── lib/
│   │   ├── notifications/
│   │   └── scout-block/
│   └── output-styles/
├── lib/secrets.sh
├── mcp/                        # MCP config templates
├── install.sh                  # Deploys global/* + registers plugin marketplace
├── backup.sh
├── restore.sh
├── diff.sh
├── health.sh
├── .env.template
└── README.md
```

### 1.2 Create plugin.json
```json
{
  "name": "cc-setup",
  "version": "1.0.0",
  "description": "Nick's Claude Code environment — unique agents, skills, and commands not provided by other plugins",
  "author": { "name": "Nick" },
  "repository": "https://github.com/krzemienski/cc-setup",
  "license": "MIT",
  "keywords": ["environment", "config", "agents", "workflow"]
}
```

### 1.3 Create marketplace.json
```json
{
  "name": "cc-setup-marketplace",
  "owner": { "name": "Nick" },
  "plugins": [
    {
      "name": "cc-setup",
      "source": ".",
      "description": "Nick's Claude Code environment — unique agents, skills, and commands",
      "strict": false
    }
  ]
}
```

### Success Criteria
- [ ] `.claude-plugin/plugin.json` is valid JSON with required `name` field
- [ ] `.claude-plugin/marketplace.json` is valid JSON with required `name`, `owner`, `plugins`
- [ ] Plugin root has `commands/`, `agents/`, `skills/` directories

---

## Phase 2: Agent Overlap Audit & Deduplication (45 min)

**Goal:** Cut cc-setup agents from 25 to ~10 by removing those duplicated by ECC/OMC

### 2.1 Dedup rule
**Default: REMOVE from cc-setup.** Keep ONLY if you can name a concrete behavioral difference that materially affects output quality vs. the OMC/ECC version.

### 2.2 Expected dedup results

**KEEP in cc-setup plugin (~10 agents):**
| Agent | Reason to keep |
|-------|---------------|
| brainstormer.md | No OMC/ECC equivalent |
| docs-manager.md | OMC has writer (haiku) but no full docs lifecycle manager |
| fullstack-developer.md | No OMC/ECC equivalent — multi-stack implementation |
| git-manager.md | OMC has git-master but cc-setup's version integrates with cc-sync workflow |
| journal-writer.md | No OMC/ECC equivalent — incident documentation |
| mcp-manager.md | No OMC/ECC equivalent — MCP tool discovery/execution |
| project-manager.md | No OMC/ECC equivalent — progress tracking |
| researcher.md | No OMC/ECC equivalent at this detail level |
| tester.md | OMC has test-engineer but cc-setup's version includes functional validation |
| ui-ux-designer.md | No OMC/ECC equivalent at this scope |

**REMOVE from cc-setup (~15 agents):**
| Agent | Covered by |
|-------|-----------|
| architect.md | OMC: architect (opus) |
| build-error-resolver.md | ECC: build-error-resolver |
| code-reviewer.md | OMC: code-reviewer (opus), ECC: code-reviewer |
| code-simplifier.md | OMC: code-simplifier (opus) |
| database-reviewer.md | ECC: database-reviewer |
| debugger.md | OMC: debugger (sonnet) |
| doc-updater.md | ECC: doc-updater |
| e2e-runner.md | ECC: e2e-runner |
| go-build-resolver.md | ECC: go-build-resolver |
| go-reviewer.md | ECC: go-reviewer |
| planner.md | OMC: planner (opus) |
| python-reviewer.md | ECC: python-reviewer |
| refactor-cleaner.md | ECC: refactor-cleaner |
| security-reviewer.md | OMC: security-reviewer (sonnet) |
| tdd-guide.md | ECC: tdd-guide |

### 2.3 Validation
- [ ] Each REMOVE decision verified: the covering plugin IS installed and enabled
- [ ] Each KEEP decision justified with a specific behavioral difference
- [ ] Agent count reduced from 25 to ≤12

---

## Phase 3: Component Migration (60 min)

**Goal:** Move qualifying components to plugin directories

### 3.1 Move agents
- Copy the ~10 KEEP agents from `global/agents/` to plugin `agents/` at repo root
- DO NOT move hooks (they stay in `global/hooks/`)
- No path updates needed — agent .md files don't have hardcoded paths

### 3.2 Move skills
- Move `skills/cc-health/`, `skills/cc-sync/`, `skills/cc-index/` to plugin `skills/` at repo root
- Update SKILL.md references if any point to `~/cc-setup/` (use relative paths instead)

### 3.3 Create commands
New slash commands for the plugin:

**commands/cc-health.md:**
```markdown
---
name: cc-health
description: Run health check on Claude Code configuration
---
Run ~/cc-setup/health.sh and report results.
```

**commands/cc-sync.md:**
```markdown
---
name: cc-sync
description: Sync Claude Code config between ~/.claude/ and ~/cc-setup
---
[Same content as current skills/cc-sync/SKILL.md usage section]
```

**commands/cc-install.md:**
```markdown
---
name: cc-install
description: Deploy cc-setup configuration to this machine
---
Run ~/cc-setup/install.sh and report results.
```

### 3.4 Update install.sh
Modify install.sh to:
1. Deploy `global/CLAUDE.md` — **MERGE**, not overwrite. Preserve `<!-- OMC:START -->` to `<!-- OMC:END -->` block. Only update content outside those markers.
2. Deploy `global/rules/` → `~/.claude/rules/`
3. Deploy `global/settings.json.template` → `~/.claude/settings.json` (with hook registrations + secret injection)
4. Deploy `global/hooks/` → `~/.claude/hooks/` (all hook scripts + lib)
5. Deploy `global/output-styles/` → `~/.claude/output-styles/`
6. Print: `"Plugin components: run /plugin marketplace add ~/cc-setup then /plugin install cc-setup@cc-setup-marketplace"`
7. **DO NOT deploy agents/ or skills/** — plugin handles those now

### 3.5 Update backup.sh
- Backup `~/.claude/rules/` → `global/rules/`
- Backup `~/.claude/hooks/` → `global/hooks/`
- Backup `~/.claude/settings.json` → `global/settings.json.template` (with secret stripping)
- Backup `~/.claude/CLAUDE.md` → `global/CLAUDE.md`
- **DO NOT backup agents** — they're now managed in plugin `agents/` directly

### Success Criteria
- [ ] Plugin `agents/` has ~10 agent files
- [ ] Plugin `skills/` has 3 skill directories
- [ ] Plugin `commands/` has 3 command files
- [ ] `global/agents/` removed or emptied (agents are now in plugin root)
- [ ] install.sh no longer deploys agents or skills to ~/.claude/
- [ ] install.sh preserves OMC block in CLAUDE.md

---

## Phase 4: Context Hierarchy Optimization (30 min)

**Goal:** Document and optimize the context chain

### 4.1 Context flow (post-migration)
```
System Prompt (Claude Code built-in)
  └── ~/.claude/CLAUDE.md (deploy: install.sh, ~50 lines non-OMC + OMC block)
        └── ~/.claude/rules/*.md (deploy: install.sh, 10 files)
              └── Hooks in settings.json (deploy: install.sh, fire per-event)
                    └── Plugin skills (deploy: plugin auto-discovery, on-demand)
                          └── Plugin agents (deploy: plugin auto-discovery, invoked by Task)
                                └── Plugin commands (deploy: plugin auto-discovery, user-invoked)
                                      └── Project .claude/CLAUDE.md (per-project overrides)
```

### 4.2 Delivery boundary map
| Component | Delivery | Why |
|-----------|----------|-----|
| CLAUDE.md | install.sh (merge) | OMC ownership + always-loaded context |
| rules/*.md | install.sh | Always-loaded, not a plugin component type |
| settings.json | install.sh | User config + hook registrations |
| hooks/*.js | install.sh → ~/.claude/hooks/ | Path-dependent (__dirname traversals) |
| output-styles/ | install.sh | Not a plugin component type |
| MCP configs | install.sh (with secrets) | Secret injection required |
| agents/*.md | **Plugin** | Portable, no path dependencies |
| skills/*/SKILL.md | **Plugin** | Portable, auto-discovered |
| commands/*.md | **Plugin** | Portable, auto-discovered |

### 4.3 CLAUDE.md split
Separate cc-setup content from OMC content:
- `global/CLAUDE.md` should contain ONLY cc-setup's "Operating Manual" (~33 lines)
- install.sh merges this below any existing `<!-- OMC:END -->` marker
- If no OMC block exists, install.sh writes the full file

### 4.4 Verify enforcement hooks
These hooks are in `global/hooks/` (deployed by install.sh) and registered in `settings.json.template`:
- [x] `block-test-files.js` → No mocks/stubs
- [x] `skill-activation-forced-eval.js` → Check skills before work
- [x] `evidence-gate-reminder.js` → Evidence before completion
- [x] `plan-before-execute.js` → Plan before code
- [x] `read-before-edit.js` → Read before write
- [x] `subagent-context-enforcer.js` → No empty-context subagents

### Success Criteria
- [ ] Context flow diagram created (Mermaid)
- [ ] Delivery boundary documented
- [ ] install.sh merge logic for CLAUDE.md implemented
- [ ] All 6 enforcement hooks confirmed in settings.json.template

---

## Phase 5: Installation & Validation (30 min)

**Goal:** Install plugin + run install.sh and verify everything works

### 5.1 Install sequence
```bash
# 1. Run install.sh for config components
cd ~/cc-setup && ./install.sh

# 2. Register marketplace (in Claude Code session)
/plugin marketplace add ~/cc-setup

# 3. Install plugin
/plugin install cc-setup@cc-setup-marketplace

# 4. Restart Claude Code to load new plugin
```

### 5.2 Validation checklist
- [ ] `/cc-health` command visible in `/help` and executes health.sh
- [ ] `/cc-sync` command visible and describes backup/restore/diff
- [ ] `/cc-install` command visible and describes install workflow
- [ ] Plugin agents visible: `brainstormer`, `docs-manager`, `fullstack-developer`, etc.
- [ ] No duplicate agents (search for `architect.md` — should come from OMC/ECC only, not cc-setup)
- [ ] Hooks fire correctly: create a test file → block-test-files.js should warn
- [ ] Skills listed in available skills
- [ ] health.sh passes all checks
- [ ] diff.sh shows config in sync

### 5.3 Rollback procedure
If validation fails:
```bash
# Revert to pre-migration state
cd ~/cc-setup && ./restore.sh
# Disable plugin if it causes issues
# /plugin disable cc-setup@cc-setup-marketplace
```

### Success Criteria
- [ ] All 9 validation checks pass
- [ ] No duplicate components across plugins
- [ ] Rollback tested and documented

---

## Phase 6: Documentation & Diagrams (30 min)

**Goal:** Create system diagram and updated README

### 6.1 Mermaid system diagram
Create in `docs/system-architecture.md`:
- Context hierarchy flow
- Plugin vs install.sh boundary
- Component inventory with source attribution

### 6.2 Update README.md
- Primary install: `./install.sh` + `/plugin marketplace add ~/cc-setup`
- What the plugin delivers (agents, skills, commands)
- What install.sh delivers (rules, hooks, CLAUDE.md, settings, MCP)
- Overlap audit results (which agents removed, why)
- Secret management workflow (.env → inject_secrets)

### Success Criteria
- [ ] Mermaid diagram in docs/
- [ ] README covers both delivery mechanisms
- [ ] Overlap audit documented with keep/remove rationale

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Plugin agents conflict with OMC/ECC agents by name | Plugin agents are namespaced as `cc-setup:agent-name` |
| install.sh overwrites OMC block in CLAUDE.md | Merge logic: detect OMC markers, preserve them, write cc-setup content outside |
| Hooks registered in both plugin + settings.json | NOT POSSIBLE — hooks are ONLY in settings.json, not in plugin |
| Secret leakage in plugin | Plugin contains NO secrets. Only install.sh injects secrets into MCP configs |
| Breaking existing workflow | backup.sh + restore.sh provide full rollback |

## Reflection Improvements (filed from post-planning review)

### Issue 1: Agent dedup needs line-by-line verification
**Problem:** KEEP/REMOVE decisions based on name/description matching only. Actual prompt content of cc-setup's `tester.md` vs OMC's `test-engineer` not deeply compared.
**Fix:** Phase 2 must include reading the actual body of each "borderline" agent (tester, git-manager, ui-ux-designer) AND the OMC/ECC equivalent, then documenting the concrete behavioral difference.
**Phase affected:** Phase 2

### Issue 2: CLAUDE.md merge logic needs real implementation spec
**Problem:** Phase 3.4 says "merge, not overwrite" but the actual sed/awk/bash logic for detecting OMC markers and splicing content isn't specified.
**Fix:** Add concrete implementation to Phase 3.4:
```bash
# CLAUDE.md merge logic pseudocode:
# 1. If ~/.claude/CLAUDE.md exists AND contains <!-- OMC:START -->:
#    a. Extract everything between <!-- OMC:START --> and <!-- OMC:END --> (inclusive)
#    b. Read cc-setup's global/CLAUDE.md (non-OMC content only, ~33 lines)
#    c. Write: [OMC block] + [newline] + [cc-setup content]
# 2. If ~/.claude/CLAUDE.md exists but NO OMC markers:
#    a. Prepend existing content, append cc-setup content
# 3. If ~/.claude/CLAUDE.md does not exist:
#    a. Write cc-setup content directly
```
**Phase affected:** Phase 3, Phase 4

### Issue 3: Plugin removal needs dependency verification before action
**Problem:** Overlap audit flags 3 plugins for removal (skills-search, start, kaizen) but doesn't verify no existing plans/workflows/scripts reference their skill prefixes.
**Fix:** Add verification step to Phase 2:
```bash
# Before removing any plugin, verify no references exist:
grep -r "start:" ~/cc-setup/plans/ ~/.claude/ 2>/dev/null
grep -r "kaizen:" ~/cc-setup/plans/ ~/.claude/ 2>/dev/null
grep -r "skills-search:" ~/cc-setup/plans/ ~/.claude/ 2>/dev/null
```
Only proceed with removal if grep returns zero matches.
**Phase affected:** Phase 2

### Issue 4: health.sh needs update for dual-delivery model
**Problem:** health.sh currently checks `~/.claude/hooks/*.js` and `~/.claude/agents/`. After migration, agents live in the plugin cache, not `~/.claude/agents/`. health.sh will report false failures.
**Fix:** Phase 5 must update health.sh to:
- Check plugin agents via `~/.claude/plugins/` paths OR skip agent count check (plugin handles it)
- Add plugin installation check: verify cc-setup plugin is enabled
- Keep hook checks as-is (hooks still in `~/.claude/hooks/`)
**Phase affected:** Phase 5

### Issue 5: Removed agents must be cleaned from ~/.claude/agents/
**Problem:** install.sh previously deployed all 25 agents to `~/.claude/agents/`. After migration, the 15 removed agents will still exist in `~/.claude/agents/` as stale files unless explicitly cleaned.
**Fix:** Phase 3.4 must add cleanup step:
```bash
# Remove agents that are now covered by OMC/ECC (deployed by plugin, not install.sh)
REMOVE_AGENTS=(architect build-error-resolver code-reviewer code-simplifier database-reviewer debugger doc-updater e2e-runner go-build-resolver go-reviewer planner python-reviewer refactor-cleaner security-reviewer tdd-guide)
for agent in "${REMOVE_AGENTS[@]}"; do
    rm -f "$HOME/.claude/agents/${agent}.md"
done
```
**Phase affected:** Phase 3

### Issue 6: global/CLAUDE.md in repo currently contains OMC block
**Problem:** `global/CLAUDE.md` is 195 lines, 162 of which are the OMC block. The plan says it should contain "only non-OMC content (~33 lines)" but nobody has actually split it yet.
**Fix:** Phase 3 must explicitly split `global/CLAUDE.md`:
1. Extract lines after `<!-- OMC:END -->` into new `global/CLAUDE.md` (~33 lines)
2. Delete the OMC block from the repo copy — OMC manages its own block at runtime
3. Update backup.sh to strip OMC block when backing up CLAUDE.md
**Phase affected:** Phase 3

---

## Effort Estimate (Revised)
- Phase 1: 15 min (scaffold)
- Phase 2: 60 min (audit + decisions + line-by-line agent comparison + dep verification)
- Phase 3: 90 min (migration + install.sh update + CLAUDE.md split + stale agent cleanup)
- Phase 4: 30 min (context optimization + merge logic implementation)
- Phase 5: 45 min (install + validate + health.sh update + rollback test)
- Phase 6: 30 min (docs + diagram)
- **Total: ~4.5 hours**
