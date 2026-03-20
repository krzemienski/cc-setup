# Critic Review: CC-Setup Optimization Plan

**Date**: 2026-03-19
**Plan**: plans/260319-1929-cc-setup-optimization/plan.md
**Verdict**: **ITERATE**

## Overall Assessment

The plan correctly identifies the three real problems (incomplete install, secret leakage in backup, plugin overlap risk) and proposes a reasonable incremental fix. However, it lacks the specificity needed for unambiguous execution on the two hardest tasks: secret stripping and MCP env-var substitution. The architect's must-fix items are valid and the plan does not yet address them.

## Pre-commitment Predictions vs Actual

| Prediction | Result |
|---|---|
| Underspecified secret-stripping | CONFIRMED — backup.sh:34 is raw `cp`, plan says "sed/jq" without specifying fields |
| diff.sh missing from scope | CONFIRMED — zero coverage for skills, claude.json, mcp.json |
| envsubst macOS issue | PARTIAL — available via homebrew on this machine, but plan doesn't declare dependency |
| Phase 3 too vague | CONFIRMED — no methodology, output format, or decision criteria |
| Validation gaps | CONFIRMED — no partial-env testing, no post-substitution JSON check |

## Critical Findings

### C1. backup.sh secret stripping has no concrete mechanism

**Evidence**: `backup.sh` line 34: `cp "$HOME/.mcp.json" "$REPO_DIR/mcp/mcp.json.template"` — raw copy, zero secret handling.

Plan line 47 says: `Strip API keys from MCP configs before saving to repo (sed/jq to replace real keys with ${PLACEHOLDER})` but secrets are in heterogeneous locations:
- `mcp.json.template:14` — `"CONTEXT7_API_KEY"` in `headers` object
- `mcp.json.template:34` — `"FIRECRAWL_API_KEY"` in `env` object
- `mcp.json.template:45` — `"GITHUB_PERSONAL_ACCESS_TOKEN"` in `env` object
- `claude.json.template:7` — `"X-Goog-Api-Key"` in `headers` object

**Impact**: This is the bug that caused the push rejection. Without a concrete mechanism, two developers could implement incompatible approaches.

**Fix**: Enumerate the 4 known keys and their jq paths explicitly. Example:
```bash
jq '.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  | .mcpServers["firecrawl-mcp"].env.FIRECRAWL_API_KEY = "${FIRECRAWL_API_KEY}"
  | .mcpServers.context7.headers.CONTEXT7_API_KEY = "${CONTEXT7_API_KEY}"'
```

### C2. install.sh MCP env-var substitution approach is unspecified

**Evidence**: `install.sh` lines 74-77 deploy mcp.json.template via raw `cp` with ZERO substitution. Existing settings.json uses per-field `sed` with `__VAR__` syntax (lines 44-49). MCP templates use `${VAR}` syntax — incompatible approaches.

**Impact**: Executor must make a design decision that should be in the plan. `sed` on `${VAR}` patterns breaks on values containing `/` or `&`. `envsubst` requires documenting a homebrew dependency.

**Fix**: Pick ONE approach. Recommended: `envsubst` for MCP configs (handles `${VAR}` natively), document `brew install gettext` as prerequisite. Or migrate everything to `${VAR}` syntax.

## Major Findings

### M1. diff.sh absent from plan scope

**Evidence**: `diff.sh` has zero coverage for skills, claude.json, or mcp.json (confirmed via grep). After adding skills and claude.json deployment, diff.sh will silently report "No differences found" for drifted artifacts.

**Fix**: Add diff.sh to Phase 1. Add skills directory diff and MCP config structural diffs (excluding secret values).

### M2. health.sh has no skills coverage

**Evidence**: `health.sh` checks hooks, plugins, MCP servers, rules, agents, settings.json — zero skills verification. Phase 6 validation ("Run health.sh and confirm all green") passes even if skills deployment completely fails.

**Fix**: Add to Phase 1 or 5: check `~/.claude/skills/{cc-health,cc-sync,cc-index}/SKILL.md` exist.

### M3. restore.sh fix is incomplete

**Evidence**: Plan lines 51-52 say "Deploy claude.json MCP config" and "Deploy skills" but restore.sh has the same env-var substitution gap as install.sh. restore.sh's current secret-preservation approach (lines 22-26) covers settings.json but has no MCP equivalent.

**Fix**: Explicitly state restore.sh needs the same substitution mechanism as install.sh. Consider extracting shared logic into `lib/secrets.sh`.

### M4. Phase 3 has no methodology

**Evidence**: Plan lines 59-65 say "Map all 17 enabled plugins" with no specification for: how to enumerate skills, what "overlap" means, output format, or decision criteria.

**Fix**: Specify: enumerate each plugin's SKILL.md triggers, cross-reference against hook filenames and rule filenames, output a markdown table with recommendations.

## Minor Findings

1. Plan says "28 hooks" but repo/CLAUDE.md says 26.
2. Phase 4 (diagram) has no acceptance criteria for "done."
3. Phase 2 is ~15 minutes of work; could fold into Phase 1.
4. Known-keys list (4 keys) isn't marked as needing updates when MCP servers change.

## What's Missing

- **Partial .env handling**: What happens when only some env vars are set? envsubst produces empty strings; sed leaves literals. No fallback specified.
- **Post-substitution JSON validation**: Malformed JSON possible after substitution. Architect's should-fix #4 not addressed.
- **MCP file rollback**: install.sh backs up `~/.claude/` but NOT `~/.mcp.json` or `~/.claude.json`.
- **Skills coexistence confirmation**: `~/.claude/skills/` has 200+ plugin skills. Plan should confirm custom skills deploy alongside (they do, but state it).
- **Two placeholder syntaxes**: `__VAR__` vs `${VAR}` coexist. Plan doesn't address unifying.

## Ambiguity Risks

| Quote | Interp A | Interp B | Risk |
|---|---|---|---|
| "Strip API keys...sed/jq to replace real keys with ${PLACEHOLDER}" | sed regex matching key-like values | jq with explicit paths for known keys | Interp A false-positives on non-secrets |
| "Deploy skills/ -> ~/.claude/skills/" | rsync 3 skill dirs into existing dir | replace entire skills directory | Interp B deletes all plugin skills |

## Perspective Notes

- **Executor**: Phase 1 has 8 items across 3 scripts, each requiring unresolved design decisions. Would need 3+ clarifying questions before starting.
- **Stakeholder**: "backup.sh never captures real API keys" needs a concrete test — grep for key patterns in output, not eyeballing.
- **Skeptic**: Phase 3 (plugin audit) could be deferred. 17 plugins work today. Should this gate the critical script fixes?

## Verdict Justification

ITERATE, not REJECT. Architecture is sound — incremental patching is correct. But the two hardest tasks (secret stripping, env-var substitution) need concrete design decisions made IN the plan, not deferred to the executor. One revision pass addressing: (a) concrete secret-stripping jq paths, (b) explicit envsubst vs sed choice, (c) diff.sh in scope, (d) post-substitution validation would make this ACCEPT-worthy.

Reviewed in THOROUGH mode. No escalation to ADVERSARIAL warranted.

## Ralplan Gate

| Gate | Status | Reason |
|---|---|---|
| Principle/Option Consistency | **Pass** | Option A aligns with principles #1 and #5 |
| Alternatives Depth | **Pass** | Option B fairly characterized, rejection rationale sound |
| Risk/Verification Rigor | **Fail** | No explicit risks, validation misses partial-env and JSON validity |

## Open Questions

- Should `__VAR__` and `${VAR}` placeholder syntaxes be unified in this effort?
- Are project templates (ios/web/python) deployed by install.sh? Plan doesn't mention them.
- Should health.sh verify custom skills specifically, or is general skills directory presence sufficient?
