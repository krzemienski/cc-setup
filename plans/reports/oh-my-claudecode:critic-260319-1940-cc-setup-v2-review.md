# Critic Review: CC-Setup Optimization Plan v2

**Date**: 2026-03-19
**Plan**: plans/260319-1929-cc-setup-optimization/plan.md (v2)
**Prior reviews**: v1 critic (ITERATE), v1 architect (ITERATE), v2 architect (APPROVE)

---

**VERDICT: ACCEPT-WITH-RESERVATIONS**

## Overall Assessment

V2 is a substantial improvement over v1. All 5 critic must-fix items and all 7 architect recommendations were addressed. The plan is now specific enough to execute without design decisions being deferred to the implementer. Two issues remain: one CRITICAL (claude.json deploy would destroy app state without merge semantics) and one MAJOR (strip_secrets function contract is ambiguous). Both are narrowly scoped and fixable without restructuring the plan.

## Pre-commitment Predictions vs Actual

| Prediction | Result |
|---|---|
| jq paths may not match actual files | REFUTED — all 4 paths verified correct against live files |
| backup.sh line references may be stale | REFUTED — line 34 (cp) and line 40 (jq extract) both verified |
| install.sh MCP logic may differ from plan's assumption | CONFIRMED — plan correctly identifies raw cp at lines 74-77 |
| strip_secrets function contract ambiguous | CONFIRMED — one function, two incompatible jq expressions |
| sed approach may have escaping issues | PARTIALLY CONFIRMED — `&` in API key values would be misinterpreted by sed (latent, not currently triggered) |

## Critical Findings

### C1. claude.json deploy will destroy application state

**Evidence**: Plan line 81: `Deploy mcp/claude.json.template → ~/.claude.json via inject_secrets + validate_json`

The live `~/.claude.json` is 380KB with 70+ top-level keys (app state, user preferences, OAuth tokens, feature flags, usage stats). The template is 28 lines containing only `{mcpServers: {stitch, xcode, pencil}}`. A direct deploy (cp + sed) would overwrite the entire file, destroying the Claude Code installation.

- Confidence: HIGH
- Why this matters: Executing this step as written would break Claude Code entirely. User would lose all app state, OAuth sessions, and preferences.
- Fix: Specify merge semantics for claude.json, matching the pattern already used for settings.json in `install.sh:51-56`:
  ```
  # Read template mcpServers, inject secrets, merge into existing ~/.claude.json
  TEMPLATE_MCP=$(inject_secrets mcp/claude.json.template)
  jq --argjson mcp "$(echo "$TEMPLATE_MCP" | jq '.mcpServers')" '.mcpServers = $mcp' ~/.claude.json > ~/.claude.json.tmp
  mv ~/.claude.json.tmp ~/.claude.json
  ```
  Apply the same merge approach in restore.sh. Backup direction (extract only mcpServers) is already correct.

## Major Findings

### M1. strip_secrets function contract is ambiguous — will corrupt files

**Evidence**: Plan lines 52-61 show `strip_secrets(file)` as a single function, then present two separate jq expressions separated by a comment `# claude.json variant:`. The mcp.json jq expression sets 3 paths; the claude.json jq expression sets 1 path.

jq CREATES non-existent paths rather than skipping them. Running the combined 4-key expression against mcp.json.template would create a spurious `.mcpServers.stitch` entry. Running it against claude.json.template would create spurious `.mcpServers.github`, `.mcpServers["firecrawl-mcp"]`, and `.mcpServers.context7` entries.

- Confidence: HIGH (verified via `echo '{"a":1}' | jq '.mcpServers.stitch.headers["X-Goog-Api-Key"] = "x"'` — creates the full path)
- Why this matters: backup.sh would produce corrupted templates with phantom MCP server entries.
- Fix: Either (a) use two functions `strip_mcp_secrets(file)` and `strip_claude_secrets(file)`, or (b) use filename detection inside strip_secrets:
  ```bash
  strip_secrets() {
    local file="$1"
    case "$(basename "$file")" in
      *mcp*) jq '..3 mcp paths...' "$file" ;;
      *claude*) jq '..1 claude path...' "$file" ;;
    esac
  }
  ```

## Minor Findings

1. **sed `&` escaping**: The `inject_secrets` sed command uses `|` as delimiter (good), but `&` in a replacement value is interpreted by sed as "the matched pattern." If any API key ever contains `&`, injection will silently produce wrong values. Current keys don't contain `&`, but this is undocumented. ADR should note this limitation.

2. **TELEGRAM_BOT_TOKEN omitted from .env.template**: The v1 architect flagged `global/hooks/notifications/telegram_notify.sh:55` uses `TELEGRAM_BOT_TOKEN`. Phase 3's .env.template update lists only the 4 MCP keys. Not blocking since it's a hook-level secret (not MCP config), but completeness suggests including it.

3. **.env.template Phase 3 vs Phase 1 ordering**: Phase 3 updates .env.template, but Phase 1 creates lib/secrets.sh which references the same env vars. No functional issue, but listing .env.template update earlier would make the dependency clearer.

4. **Validation step 5 is weak**: `Verify at least 2 MCP servers respond (e.g., jq . ~/.mcp.json valid, health.sh passes)` — jq validity proves JSON structure, not that servers actually respond. This is fine as a plan-level check; just rename it to "Verify MCP config JSON validity" to avoid confusion.

5. **archive/ cleanup**: README line 35 references `archive/` which doesn't exist. Plan Phase 6 correctly identifies this.

## What's Missing

- **Merge semantics for claude.json in restore.sh**: Plan line 93 says `Deploy claude.json MCP config via inject_secrets` — same overwrite risk as install.sh. Needs the same merge approach.
- **First-install path for claude.json**: If `~/.claude.json` doesn't exist yet (fresh machine), the merge approach needs a fallback — the template alone is insufficient since Claude Code expects the full app state file. Plan should document: "If ~/.claude.json doesn't exist, skip MCP merge (Claude Code will create it on first run; user must re-run install.sh after first launch to inject MCP servers)."
- **Two placeholder syntaxes coexist**: `__VAR__` (settings.json) and `${VAR}` (MCP templates) remain separate. Acceptable for now, but the ADR should acknowledge this as tech debt.
- **Skills rsync --delete concern**: Plan line 83 says `rsync` for skills deploy. If `--delete` is used, it would remove all 200+ plugin-installed skills from `~/.claude/skills/`. If `--delete` is NOT used, stale custom skills persist. Plan should specify: rsync WITHOUT `--delete`, targeting only `cc-health/`, `cc-sync/`, `cc-index/` subdirectories.

## Ambiguity Risks

| Quote from plan | Interpretation A | Interpretation B | Risk |
|---|---|---|---|
| `Deploy mcp/claude.json.template → ~/.claude.json` (line 81) | Overwrite entire file | Merge mcpServers into existing file | A destroys 380KB of app state |
| `strip_secrets(file)` with two jq blocks (lines 52-61) | One function with conditional logic | Two separate functions | Single function with all paths creates phantom entries |
| `Deploy skills/ → ~/.claude/skills/ (rsync)` (line 83) | rsync --delete (clean deploy) | rsync without --delete (additive) | --delete removes all plugin skills |

## Multi-Perspective Notes

- **Executor**: The plan is now actionable for 6 of 7 phases. Phase 1 needs the function contract clarified (M1) before starting. Phase 2's install.sh claude.json deploy (C1) needs merge semantics specified. Otherwise, an executor could start on backup.sh fixes, diff.sh, and health.sh immediately.
- **Stakeholder**: The plan solves the stated problems (incomplete install, secret leakage, no audit). Success criteria are measurable. Phase 7 validation is concrete and testable.
- **Skeptic**: The strongest argument against this plan is that it adds complexity to scripts that were simple (if incomplete). Four scripts now depend on lib/secrets.sh, and the two-syntax placeholder approach (`__VAR__` vs `${VAR}`) means future maintainers must understand both. However, the alternative (do nothing) leaves the secret leakage bug and incomplete install. The complexity is justified.

## Verdict Justification

ACCEPT-WITH-RESERVATIONS. The plan is architecturally sound, addresses all v1 feedback, and is specific enough for execution. The two remaining issues (C1: claude.json merge semantics, M1: strip_secrets contract) are narrowly scoped and can be resolved by the executor with the fixes specified above — they don't require replanning.

Reviewed in THOROUGH mode. No escalation to ADVERSARIAL warranted — findings are isolated, not systemic.

**Realist Check**: C1 was pressure-tested and survives. The realistic worst case is complete loss of Claude Code app state (OAuth, preferences, usage history) requiring manual reconfiguration. No mitigating factors — there's no backup of ~/.claude.json in the current install.sh flow (it only backs up ~/.claude/ directory, not the root-level .claude.json). Detection would only happen after the damage. Severity CRITICAL is correctly rated.

M1 was pressure-tested. Realistic worst case: phantom MCP server entries in template files. These would be caught by the Phase 7 validation step (grep for unexpected entries) or by a careful code reviewer. Mitigated by: Phase 7's explicit backup.sh + grep validation step. Severity MAJOR is correctly rated — it produces wrong output but the validation phase would catch it before commit.

## Ralplan Gate

| Gate | Status | Reason |
|---|---|---|
| Principle/Option Consistency | **Pass** | Option A aligns with all 5 principles; Phase 1 shared lib satisfies principle #2 |
| Alternatives Depth | **Pass** | Option B fairly characterized, rejection rationale sound, ADR documents alternatives |
| Risk/Verification Rigor | **Pass** | Phase 7 has 7 concrete validation steps; success criteria are measurable |

## Open Questions

- Should the plan address the first-install case where ~/.claude.json doesn't exist yet?
- Should `__VAR__` and `${VAR}` placeholder syntaxes be unified in this effort, or documented as intentional tech debt?
- The v1 architect suggested `validate_no_raw_secrets(file)` as a third function — worth including?
