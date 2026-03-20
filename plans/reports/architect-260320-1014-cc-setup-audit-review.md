# Architectural Review: cc-setup Full Audit Fix Plan

**Reviewer:** Architect  
**Date:** 2026-03-20  
**Plan:** `/Users/nick/cc-setup/plans/260320-1014-cc-setup-full-audit/plan.md`  
**Verdict:** ITERATE (2 issues must be addressed before execution)

---

## Summary

The plan is well-structured and correctly identifies the highest-severity bugs. The phased approach with clear acceptance criteria is sound. However, the plan contains one critical technical misunderstanding about the jq merge behavior that would cause the fix to be incomplete, and misses two hardcoded paths and one platform-specific hook command. These must be resolved before execution.

---

## Analysis

### 1. jq Deep-Merge: Correct for Objects, Broken for Arrays (CRITICAL)

The plan states the current `jq -s '.[0] * .[1]'` at `install.sh:55` destroys user data and proposes replacing it with a "smart merge function." The diagnosis is correct, but the plan's understanding of *what* is safe is incomplete.

**Verified behavior of `jq -s '.[0] * .[1]'`:**

- **Object keys (`enabledPlugins`, `extraKnownMarketplaces`, `env`):** Deep-merged correctly. Template key `{"c": true}` is added alongside existing `{"a": true, "b": true}`. These are SAFE with the current approach.
- **Array values within `hooks` event types:** REPLACED entirely. The template's PreToolUse array obliterates the user's PreToolUse array. This is the actual data-loss vector.
- **Top-level scalars (`model`, `effortLevel`):** Template wins (last-writer-wins). This is the secondary concern -- template values silently override user preferences.

The plan's Task 1.1 correctly calls for "union-merging hooks by event type + matcher" and "template entries added, existing user entries preserved." This is the right goal, but the implementation guidance is too vague on a genuinely tricky problem:

**The hooks merge has a nested structure problem:** Each event type (e.g., `PreToolUse`) contains an array of matcher groups, each of which contains an array of hooks. Deduplication by "command string" must handle:
- Same matcher, different hooks (union the hooks array)
- Same matcher, same hook command (deduplicate)  
- Different matchers within same event type (preserve both)
- User-added matcher groups not in template (preserve)

**Recommendation:** The merge function should iterate event types as object keys (safe with `*`), then for each event type, merge arrays by matcher string, then within each matcher group, union the hooks arrays by command string. Pseudocode:

```
for each event_type in (template_hooks UNION user_hooks):
  for each matcher in (template_matchers UNION user_matchers):
    hooks = dedupe_by_command(template_hooks + user_hooks)
```

This is ~20-30 lines of jq, not ~15 as the plan estimates. Still feasible, but the executor needs this spelled out.

**References:**
- `install.sh:55` -- current naive merge
- `global/settings.json.template:18-187` -- hooks structure with nested arrays

### 2. Missing Hardcoded Path: `extraKnownMarketplaces` (MEDIUM)

The plan identifies `/Users/nick` in `statusLine` (line 191) but misses line 216:

```json
"path": "/Users/nick/.cache/plugins/github.com-vercel-vercel-plugin"
```

This is in `extraKnownMarketplaces.vercel-vercel-plugin.source.path` and will break on any other machine. It needs the same `__HOME__` placeholder treatment as statusLine.

**Reference:** `global/settings.json.template:216`

### 3. Missing Platform Issue: `afplay` in Stop Hook (LOW-MEDIUM)

The Stop hook at line 123 runs:
```bash
[ "$PROJEKT_TERMINAL" = "1" ] && afplay /System/Library/Sounds/Submarine.aiff || true
```

`afplay` is macOS-only. On Linux this will fail silently due to `|| true`, so it is not a crash bug, but it is a platform-awareness gap the plan claims to address comprehensively. Either:
- Gate it behind `uname -s` in the hook command itself, or
- Accept the silent failure as benign (document this decision)

**Reference:** `global/settings.json.template:123`

### 4. Scalar Key Merge Direction Not Fully Specified (MEDIUM)

Task 1.1 says "template wins for env/model config; user wins for preferences like effortLevel." This bidirectional merge policy is correct but needs to be explicit about WHICH keys are user-wins vs template-wins. Currently the plan lists 4 user-wins keys but the template has ~8 scalar keys total. The executor needs a definitive list.

**Suggested categorization:**
- **Template-wins:** `env.*`, `includeCoAuthoredBy`, `permissions`
- **User-wins:** `model`, `effortLevel`, `alwaysThinkingEnabled`, `autoUpdatesChannel`, `skipDangerousModePermissionPrompt`
- **Union-merge:** `enabledPlugins`, `extraKnownMarketplaces`, `hooks`, `autoAllowedTools`

### 5. global/agents/ Removal: Safe (CONFIRMED)

Verified: 25 files in `global/agents/`, 10 files in plugin `agents/`. Cross-referencing:
- 15 of the 25 global agents are in the `STALE_AGENTS` list at `install.sh:96` (architect, build-error-resolver, code-reviewer, etc.)
- The remaining 10 (brainstormer, docs-manager, fullstack-developer, git-manager, journal-writer, mcp-manager, project-manager, researcher, tester, ui-ux-designer) all exist in `agents/` (plugin directory)
- `install.sh` never deploys from `global/agents/` -- confirmed by reading the full script
- `diff.sh:27-32` is the only consumer, and that block is being removed

**Verdict:** Safe to delete. No downstream dependencies.

### 6. Platform Detection Approach: Sufficient but Incomplete (MINOR)

The plan correctly chooses "one template, strip at deploy time" over separate templates. The list of macOS-only servers (tuist, xcode, pencil, serena) is correct based on `mcp/mcp.json.template:75-92` and `mcp/claude.json.template:3-19`.

However, `tuist` uses `/opt/homebrew/bin/tuist` which is a Homebrew ARM64 path. On Intel Macs this would be `/usr/local/bin/tuist`. The plan does not address this, but it is pre-existing and out of scope for this audit.

### 7. Hook Registration: Verified Correct (Phase 5)

26 hook files deployed. 20 registered in template. 6 unregistered confirmed:
- `documentation-context-check.js` -- not in template
- `post-edit-simplify-reminder.cjs` -- not in template
- `privacy-block.cjs` -- not in template
- `scout-block.cjs` -- not in template
- `skill-dedup.cjs` -- not in template
- `usage-context-awareness.cjs` -- not in template

The plan's note to "verify by reading hook source" before finalizing event types is correct and prudent.

### 8. diff.sh Settings Comparison is Broken (MISSING FROM PLAN)

`diff.sh:42` compares the raw template against the deployed settings.json:
```bash
diff <(jq 'del(.env)' "$REPO_DIR/global/settings.json.template") <(jq 'del(.env)' "$HOME/.claude/settings.json")
```

After the merge changes, the deployed settings.json will always have MORE keys than the template (user additions, OMC-injected hooks, extra plugins). This diff will always show differences, making it a permanent false positive. The plan does not address this.

**Recommendation:** Either (a) change the diff to only compare template keys exist in deployed (subset check), or (b) accept the diff will always show expected differences and document this. Add this to Phase 2 scope.

---

## Consensus Addendum

### Antithesis (steelman)

**The strongest argument against the jq deep-merge approach:** The hooks merge logic creates a maintenance trap. Every new array-type key added to settings.json in the future will silently break (be replaced instead of merged) unless someone remembers to update the merge function's explicit key list. This is the same class of bug being fixed -- a "works until it doesn't" time bomb. An external merge tool with declarative merge strategies (Option B) would be self-documenting and future-proof, even at the cost of a Python/Node dependency.

Additionally, the jq merge function will be the most complex piece of bash in the entire repo (~25-30 lines of dense jq), making it the hardest to debug and the most likely to have subtle bugs in edge cases (e.g., what happens when a user has a matcher group with an empty hooks array?).

### Tradeoff tension

**Correctness vs. simplicity:** The plan chooses "no new dependencies" (KISS/YAGNI) over "declarative merge strategies" (correctness-by-construction). This is the right call for a personal config repo with one maintainer, but it means the merge function IS the critical section of the entire project and must be tested manually on every settings.json schema change. The plan's ADR consequence ("Future new array keys need to be added to the merge expression") correctly identifies this but underestimates its severity -- missing an array key means silent data loss, the exact bug being fixed.

### Synthesis

Keep the jq approach (no new dependencies) BUT add a defensive safeguard: after the merge, validate that the result contains at least as many `enabledPlugins` entries, at least as many hook command strings, and at least as many `autoAllowedTools` entries as the input user file. If any count decreases, abort the merge and fall back to the backup. This turns silent data loss into a loud failure. ~5 lines of bash, zero new dependencies.

---

## Recommendations (Prioritized)

1. **Add `extraKnownMarketplaces` path to `__HOME__` replacement** -- LOW effort, MEDIUM impact. Line 216 has hardcoded `/Users/nick`. (Phase 3 scope)

2. **Spell out the hooks array merge algorithm explicitly** -- MEDIUM effort, CRITICAL impact. The plan says "union-merge hooks by event type + matcher" but the executor needs the nested iteration logic described above. Without it, the fix may still lose hooks. (Phase 1 scope)

3. **Add post-merge count validation** -- LOW effort, HIGH impact. Compare enabledPlugins count, hook command count, autoAllowedTools count before/after merge. Abort if any decreased. (Phase 1 scope)

4. **Fix diff.sh settings comparison** -- LOW effort, MEDIUM impact. After merge changes, the current diff will always show false positives. Change to subset comparison or document expected differences. (Phase 2 scope)

5. **Categorize scalar keys explicitly** -- LOW effort, MEDIUM impact. Provide a definitive template-wins vs user-wins list so the executor does not have to guess. (Phase 1 scope)

6. **Document afplay as macOS-only benign failure** -- TRIVIAL effort, LOW impact. Add a comment in the template or accept the `|| true` guard. (Phase 3 scope)

---

## Verdict: ITERATE

Two changes required before execution:

1. **(MUST)** Expand Phase 1 Task 1.1 with the explicit hooks merge algorithm (event-type iteration, matcher-group union, command deduplication). The current description is too ambiguous for correct implementation.

2. **(MUST)** Add `extraKnownMarketplaces` path (line 216) to the `__HOME__` placeholder list in Phase 3.

Three changes recommended:

3. **(SHOULD)** Add post-merge count validation as a safety net in Phase 1.
4. **(SHOULD)** Fix diff.sh settings comparison in Phase 2.
5. **(SHOULD)** Add explicit scalar key categorization to Phase 1.

The plan's overall structure, phasing, and ADR reasoning are sound. The issues above are implementation-detail gaps, not architectural flaws.

---

## References

- `install.sh:55` -- current naive jq merge (the bug)
- `install.sh:96-104` -- stale agent cleanup (confirms global/agents/ is not deployed)
- `global/settings.json.template:18-187` -- hooks structure (nested arrays)
- `global/settings.json.template:191` -- hardcoded statusLine path (plan addresses)
- `global/settings.json.template:216` -- hardcoded extraKnownMarketplaces path (plan MISSES)
- `global/settings.json.template:123` -- macOS-only afplay command (plan misses)
- `diff.sh:27-32` -- agents diff block to remove (plan addresses)
- `diff.sh:42` -- settings diff that will become false-positive (plan misses)
- `lib/secrets.sh:27-33` -- inject_secrets function (context for Phase 3)
- `mcp/mcp.json.template:75-92` -- macOS-only servers serena + tuist (plan addresses)
- `mcp/claude.json.template:3-19` -- macOS-only servers xcode + pencil (plan addresses)
