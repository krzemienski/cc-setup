# cc-setup Full Audit Fix Plan

**Date:** 2026-03-20
**Scope:** 7 files primary, ~3 files secondary
**Complexity:** MEDIUM (no architectural redesign, targeted fixes to existing scripts)

---

## RALPLAN-DR Summary

### Principles
1. **Non-destructive deployments** -- install.sh must never silently destroy user state
2. **Single source of truth** -- each artifact lives in exactly one place; no dead-weight duplicates
3. **Portable by default** -- scripts work on macOS and Linux without manual post-install cleanup
4. **Complete template** -- settings.json.template must represent the full intended configuration
5. **Honest tooling** -- diff.sh and health.sh must compare/report on what install.sh actually deploys

### Decision Drivers
1. **Data loss risk** -- settings.json wipe is the highest-severity bug; user loses 45+ plugin registrations, model prefs, and OMC-injected hooks
2. **Signal-to-noise ratio** -- diff.sh false positives from dead global/agents/ erode trust in the tooling
3. **Multi-machine portability** -- hardcoded /Users/nick paths and macOS-only MCP servers block Linux deployment

### Options Considered

**Option A: Deep merge with jq (chosen)**
- Replace `jq -s '.[0] * .[1]'` with a custom jq expression that merges objects recursively but preserves user arrays (enabledPlugins, hooks, autoAllowedTools) by union rather than replacement.
- Pros: Single tool (jq), no new dependencies, handles the exact failure mode.
- Cons: jq array-merge expressions are verbose; hooks array merge needs careful key matching.

**Option B: External merge tool (jsonmerge, deepmerge CLI)**
- Use a Python/Node deep-merge utility with array-union strategy.
- Pros: Cleaner semantics, less jq complexity.
- Cons: Adds a runtime dependency (Python or Node package), breaks the "just bash + jq" contract.

**Invalidation of Option B:** cc-setup's install.sh is a portable bash script with only jq as a dependency. Adding a Python/Node merge tool increases the dependency surface for a problem solvable in ~15 lines of jq. YAGNI.

### ADR

- **Decision:** Deep-merge settings.json using jq with explicit array-union logic for known array/object keys.
- **Drivers:** Data loss prevention, zero new dependencies, predictable merge behavior.
- **Alternatives considered:** External merge tool (rejected: unnecessary dependency).
- **Why chosen:** Solves the critical bug with minimal change surface. jq is already required.
- **Consequences:** Merge logic is more verbose but self-contained. Future new array keys in settings.json need to be added to the merge expression.
- **Follow-ups:** Document the merge strategy in a comment block in install.sh so future maintainers know which keys get union-merged.

---

## Phase 1: Fix install.sh settings.json Management (CRITICAL)

**Objective:** Eliminate the data-loss bug where --clean or merge mode destroys user preferences.

### Tasks

**1.1 Replace naive jq merge with smart merge function**

Create a bash function `merge_settings()` in install.sh that handles three merge categories:

**Scalar key categorization:**
- **Template-wins:** `env.*`, `includeCoAuthoredBy`, `permissions` (config intent from cc-setup)
- **User-wins:** `model`, `effortLevel`, `alwaysThinkingEnabled`, `autoUpdatesChannel`, `skipDangerousModePermissionPrompt`, `teammateMode`, `semantic_search` (user preferences)
- **Union-merge:** `enabledPlugins`, `extraKnownMarketplaces`, `hooks`, `autoAllowedTools` (additive, never remove)

**Hooks array merge algorithm (nested structure):**
```
for each event_type in (template_hooks UNION user_hooks):
  for each matcher in (template_matchers UNION user_matchers for this event_type):
    hooks = dedupe_by_command(user_hooks_for_matcher + template_hooks_for_matcher)
```
Implementation: iterate event types as object keys, merge matcher groups by matcher string (preserve both if different matchers), within same matcher deduplicate hooks by `.command` string. ~25-30 lines of jq.

**Post-merge safety validation:**
After merge, compare counts: `enabledPlugins` entries, total hook command strings, `autoAllowedTools` entries. If ANY count decreased vs the input user file, ABORT the merge, restore from backup, and print error. This turns silent data loss into a loud failure.

**Files:** `install.sh` (lines 43-63)

**Acceptance criteria:**
- [ ] Running `install.sh` on a settings.json with 45 enabledPlugins retains all 45 plus any new ones from template
- [ ] Running `install.sh --clean` backs up existing settings.json to /tmp backup AND warns user, but still does a full overwrite (this is the documented behavior for --clean)
- [ ] User's hooks entries (e.g., OMC-injected hooks) survive merge mode
- [ ] User's model, effortLevel, alwaysThinkingEnabled, skipDangerousModePermissionPrompt are NOT overwritten by template values if they already exist
- [ ] Post-merge validation: enabledPlugins count >= pre-merge count
- [ ] Post-merge validation: hook command count >= pre-merge count
- [ ] If validation fails, merge is aborted and backup restored with clear error

**1.2 Fix --clean mode to warn explicitly**

When `--clean` is used, print a clear warning: "WARNING: --clean replaces settings.json entirely. Your enabledPlugins, hooks, and preferences will be reset. Backup saved to $BACKUP."

**Acceptance criteria:**
- [ ] --clean prints the warning before overwriting
- [ ] Backup path is printed in the warning message

---

## Phase 2: Clean Up Repo Structure

**Objective:** Remove dead weight and fix diff.sh false positives.

### Tasks

**2.1 Remove global/agents/ directory**

The 25 files in `global/agents/` are never deployed by install.sh. 15 of them overlap with OMC/ECC plugin agents (architect, code-reviewer, debugger, etc.) and are already cleaned as "stale agents" by install.sh lines 96-104. The other 10 are duplicates of the plugin `agents/` directory.

**Action:** Delete `global/agents/` entirely. The 10 unique agents (brainstormer, docs-manager, fullstack-developer, git-manager, journal-writer, mcp-manager, project-manager, researcher, tester, ui-ux-designer) are already served by the plugin via `agents/`.

**Files:** Remove `global/agents/` (25 files)

**Acceptance criteria:**
- [ ] `global/agents/` directory does not exist
- [ ] Plugin `agents/` directory still has all 10 agent files
- [ ] install.sh stale-agent cleanup block (lines 96-104) still works (it targets ~/.claude/agents/ not global/agents/)

**2.2 Fix diff.sh to stop comparing global/agents/**

Remove the agents diff block (lines 27-33) since install.sh does not deploy agents.

**Files:** `diff.sh`

**Acceptance criteria:**
- [ ] diff.sh no longer has an AGENTS section
- [ ] diff.sh still compares: rules, hooks, CLAUDE.md, settings.json, skills, MCP configs
- [ ] Running diff.sh with no changes reports "No differences found"

**2.3 Update health.sh agent reporting**

The health.sh USER AGENTS section (lines 62-73) checks ~/.claude/agents/ which now only has plugin-delivered agents. Clarify the output messaging.

**Files:** `health.sh`

**Acceptance criteria:**
- [ ] health.sh agent section output is accurate for the current delivery model

**2.4 Fix diff.sh settings.json comparison**

After the merge changes, deployed settings.json will always have MORE keys than the template (user additions, plugins, OMC hooks). The current `diff` on full files will always show false positives. Change to a subset check: verify that all template-managed keys exist and match in the deployed file, ignoring user-added keys.

**Files:** `diff.sh` (line 42)

**Acceptance criteria:**
- [ ] diff.sh settings comparison does not show false positives from user-added keys
- [ ] diff.sh still detects when a template-managed key (hooks, env) diverges from expected

---

## Phase 3: Add Platform Awareness

**Objective:** Make scripts work on both macOS and Linux without manual cleanup.

### Tasks

**3.1 Add OS detection to install.sh**

Add `OS=$(uname -s)` detection near the top. Use it to:
- Skip macOS-only MCP servers (tuist, xcode, pencil, serena) on Linux
- Use `$HOME` instead of hardcoded `/Users/nick` in statusLine

**Files:** `install.sh`, `global/settings.json.template`

**3.2 Fix statusLine and extraKnownMarketplaces paths**

Replace hardcoded `/Users/nick/` paths with `__HOME__` placeholder in the template:
- `statusLine.command` (line ~191): `/Users/nick/.claude/hud/omc-hud.mjs` → `__HOME__/.claude/hud/omc-hud.mjs`
- `extraKnownMarketplaces.vercel-vercel-plugin.source.path` (line ~216): `/Users/nick/.cache/plugins/...` → `__HOME__/.cache/plugins/...`

install.sh replaces `__HOME__` with `$HOME` at deploy time (same pattern as ANTHROPIC_* vars).

**Note:** The Stop hook's `afplay` command is macOS-only but guarded by `|| true`. Document this as benign on Linux rather than adding OS detection to the hook itself.

**Files:** `global/settings.json.template`, `install.sh`

**3.3 Add platform conditionals to MCP templates**

Option A (chosen): Keep one template, have install.sh strip macOS-only servers on Linux.
Option B: Separate templates per OS. Rejected -- duplication for 3 servers.

macOS-only servers to gate: `tuist`, `xcode`, `pencil`, `serena`.

**Files:** `install.sh`, `mcp/mcp.json.template`, `mcp/claude.json.template`

**Acceptance criteria (all of Phase 3):**
- [ ] On macOS: behavior identical to current (all MCP servers present, statusLine works)
- [ ] On Linux: no macOS-only MCP servers in deployed configs, statusLine uses correct $HOME path
- [ ] No hardcoded `/Users/nick` anywhere in templates

---

## Phase 4: Complete settings.json Template

**Objective:** Ensure the template reflects the full intended baseline configuration.

### Tasks

**4.1 Add missing preference keys to template**

Add with sensible defaults (matching current local values):
- `"alwaysThinkingEnabled": true` -- already present (line 226), confirmed
- `"effortLevel": "high"` -- already present (line 227), confirmed
- `"autoUpdatesChannel": "latest"` -- already present (line 228), confirmed
- `"skipDangerousModePermissionPrompt": true` -- already present (line 229), confirmed

On review: These keys ARE in the template already (lines 226-229). The audit finding about "missing" may have been comparing against an older template version. Verify at execution time; skip if already present.

**4.2 Add autoAllowedTools baseline**

Add an `autoAllowedTools` key with an empty array `[]` as baseline so the merge logic has a key to union-merge against.

**Files:** `global/settings.json.template`

**Acceptance criteria:**
- [ ] Template has all preference keys from the audit list
- [ ] Template validates as valid JSON
- [ ] `autoAllowedTools` key exists (even if empty array)

---

## Phase 5: Register Unregistered Hooks

**Objective:** Add the 6 deployed-but-unregistered hooks to settings.json.template.

### Hooks to register

| Hook file | Suggested event | Suggested matcher | Rationale |
|---|---|---|---|
| `documentation-context-check.js` | PreToolUse | Write\|Edit\|MultiEdit | Check doc context before edits |
| `post-edit-simplify-reminder.cjs` | PostToolUse | Edit\|Write\|MultiEdit | Remind about simplification after edits |
| `privacy-block.cjs` | PreToolUse | Write\|Edit\|MultiEdit | Block writes to private/sensitive paths |
| `scout-block.cjs` | PreToolUse | Bash\|Write\|Edit | Block broad scout/search operations |
| `skill-dedup.cjs` | PreToolUse | Agent | Prevent duplicate skill invocations |
| `usage-context-awareness.cjs` | UserPromptSubmit | (empty) | Inject usage context on each prompt |

**Files:** `global/settings.json.template`

**Note:** Before registering, read each hook file to confirm the correct event type and matcher. The table above is a best estimate based on naming conventions. The executor must verify by reading hook source.

**Acceptance criteria:**
- [ ] All 6 hooks appear in settings.json.template hooks section
- [ ] Each hook has the correct event type and matcher (verified from source)
- [ ] health.sh reports no empty hook matcher groups
- [ ] All hooks pass `node --check` syntax validation

---

## Phase 6: Deploy and Validate on Remote

**Objective:** Deploy fixed cc-setup to remote machine (home.hack.ski) and validate.

### Tasks

**6.1 Commit and push fixes**

Commit all changes with conventional commit format. Push to main.

**6.2 Pull and install on remote**

SSH to remote, pull latest, run `install.sh` (merge mode).

**6.3 Functional validation on remote**

Run the following checks on the remote machine:
- `health.sh` reports HEALTHY with 0 issues
- `diff.sh` reports no differences (or only expected ones)
- `jq '.enabledPlugins | length' ~/.claude/settings.json` shows preserved plugin count
- `jq '.hooks | to_entries | map(.value | length) | add' ~/.claude/settings.json` shows all hooks registered
- No hardcoded `/Users/nick` in any deployed config
- MCP configs have no macOS-only servers (if remote is Linux)

**Acceptance criteria:**
- [ ] Remote health.sh: HEALTHY, 0 issues
- [ ] Remote diff.sh: no false positives
- [ ] Remote settings.json: all enabledPlugins preserved from before install
- [ ] Remote settings.json: all hooks registered (template + any user additions)
- [ ] No unresolved placeholders in MCP configs (or clear warnings)

---

## Success Criteria (Overall)

1. `install.sh` merge mode preserves ALL existing user preferences, plugins, and hooks
2. `install.sh --clean` warns before overwriting and backs up
3. No dead code: global/agents/ removed, diff.sh accurate
4. Platform-portable: works on macOS and Linux without manual cleanup
5. settings.json template is complete with all known preference keys
6. All 26 hook files are deployed AND registered in settings.json
7. Remote deployment succeeds with health.sh HEALTHY

---

## Files in Scope

| File | Changes |
|---|---|
| `install.sh` | Smart merge function, OS detection, statusLine placeholder, MCP platform gating |
| `global/settings.json.template` | 6 hooks registered, autoAllowedTools added, statusLine placeholder, verify prefs |
| `diff.sh` | Remove agents comparison block |
| `health.sh` | Update agent reporting messaging |
| `mcp/mcp.json.template` | (no template changes; install.sh handles platform gating) |
| `mcp/claude.json.template` | (no template changes; install.sh handles platform gating) |
| `global/agents/` | DELETE entire directory (25 files) |

---

## Open Questions

See `/Users/nick/cc-setup/plans/open-questions.md`
