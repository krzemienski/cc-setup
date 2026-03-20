# Architect Review: CC-Setup Optimization Plan

**Verdict: ITERATE**

The plan correctly identifies the three real problems (install gaps, secret leakage, overlap risk) and chooses the right option (Option A: patch, not rewrite). However, backup.sh secret stripping is more broken than the plan acknowledges, the proposed fix is underspecified, and two structural risks are missing entirely.

---

## Summary

The plan is architecturally sound in its phased approach and correctly rejects the full rewrite. However, Phase 1's secret-stripping proposal is dangerously vague given that it is the highest-severity item (the one that already caused a git push rejection). The plan says "sed/jq to replace real keys with `${PLACEHOLDER}`" without specifying the mechanism, and the current code at `backup.sh:33-36` does **zero** secret stripping on `.mcp.json` -- it is a raw `cp`. This needs a concrete, testable implementation spec before execution.

---

## Analysis

### 1. Architectural Soundness of Script Changes -- MOSTLY SOUND, ONE GAP

**install.sh** (`install.sh:74-77`): Currently deploys `.mcp.json` via raw `cp` from template. The template already contains `${PLACEHOLDER}` syntax (confirmed at `mcp/mcp.json.template:14,34,45`). But there is no env-var substitution step -- the file is copied verbatim with `${FIRECRAWL_API_KEY}` literals. This means MCP servers that need API keys will fail silently after install.

The plan says "Add env var substitution for MCP config placeholders" but does not specify the mechanism. `envsubst` would be the natural choice, but it is not installed by default on macOS. The existing settings.json approach uses `sed` with specific named replacements (`install.sh:44-49`), which is explicit but brittle. The plan should specify which approach to use.

**install.sh** is also missing: deploy of `skills/` directory (plan correctly identifies this) and deploy of `claude.json.template` (plan correctly identifies this).

**restore.sh** (`restore.sh:20-27`): The settings.json merge logic is sound -- extract current secrets, apply to template. But restore.sh has the same gaps as install.sh (no skills, no claude.json). The plan correctly identifies this.

**diff.sh** (`diff.sh:1-51`): Not mentioned in the plan at all. It should also be updated to diff skills/ and MCP configs, otherwise drift detection is incomplete.

### 2. Secret Management Approach -- CRITICALLY UNDERSPECIFIED

This is the highest-risk item and the plan's weakest point.

**The actual bug at `backup.sh:33-36`:**
```bash
if [ -f "$HOME/.mcp.json" ]; then
    cp "$HOME/.mcp.json" "$REPO_DIR/mcp/mcp.json.template"
    echo "  .mcp.json -> template"
fi
```
This is a **raw copy**. No stripping. The comment says "strip API keys" but the code does not. If the live `.mcp.json` has real API keys (which it will after install.sh does env-var substitution), those keys go straight into the repo.

**`backup.sh:39-41`** for claude.json is slightly better -- it extracts only `mcpServers` via jq -- but still copies the actual key values from `headers.X-Goog-Api-Key` without replacing them with placeholders.

**The plan says:** "Strip API keys from MCP configs before saving to repo (sed/jq to replace real keys with `${PLACEHOLDER}`)". This is insufficient because:

- The secret patterns are heterogeneous: `env.FIRECRAWL_API_KEY` (nested in env object), `env.GITHUB_PERSONAL_ACCESS_TOKEN` (nested in env object), `headers.CONTEXT7_API_KEY` (in headers), `headers.X-Goog-Api-Key` (in headers with different key name than env var).
- A naive sed approach will miss new keys added later.
- A jq approach needs to know which fields are secrets vs. which are config.

**What the plan should specify:** A concrete stripping strategy. The two viable approaches are:
- **Allowlist:** jq walk that replaces any value matching known env var names with `${VAR_NAME}`.
- **Pattern match:** jq walk that replaces any string value that looks like an API key (length > 20, alphanumeric) with a placeholder. This is more fragile but catches unknown keys.

### 3. Overlap Audit Scope -- ADEQUATE BUT NEEDS METHOD

The plan correctly scopes the audit to "17 plugins vs 28 hooks vs 10 rules." The cross-reference approach is right. However, it does not specify **how** to enumerate plugin skills -- you cannot just list them from the repo since plugins are external. The plan should note that the audit requires either:
- Running Claude Code and using the skill listing feature, or
- Checking `settings.json` `enabledPlugins` and looking up each plugin's manifest

Also missing: the audit should check whether any MCP servers overlap with plugin functionality (e.g., `repomix` MCP server vs. a plugin that wraps repomix).

### 4. System Diagram Abstractions -- GOOD SCOPE

The four proposed layers (CLAUDE.md flow, hook lifecycle, MCP topology, plugin layer) are the right abstractions. One addition: the diagram should show the **two distinct MCP config files** (`.mcp.json` and `.claude.json`) and which servers live where, since this split is non-obvious and the plan already identifies that `claude.json` deployment is missing.

### 5. Missing Considerations

**A. idempotency.** `install.sh` is not idempotent for MCP configs. Running it twice will overwrite a working `.mcp.json` (with real keys from .env substitution) with... another copy with real keys. Fine. But if .env is missing keys, it will downgrade a working config to one with broken placeholders. The plan should add a guard: skip MCP deploy if target has real keys and source has unresolved placeholders.

**B. diff.sh is not in scope.** The plan updates install.sh, backup.sh, restore.sh but not diff.sh. After adding skills and claude.json deployment, diff.sh will report false "in sync" because it does not check those artifacts. It should be added to Phase 1.

**C. .env.template is incomplete.** Currently (`/.env.template:1-9`) it only has ANTHROPIC_* vars. The plan correctly says to add MCP API key placeholders in Phase 2, but should explicitly list: `GITHUB_PERSONAL_ACCESS_TOKEN`, `FIRECRAWL_API_KEY`, `CONTEXT7_API_KEY`, `GOOGLE_API_KEY`. Also missing from both .env.template and the plan: `TELEGRAM_BOT_TOKEN` (used at `global/hooks/notifications/telegram_notify.sh:55`).

**D. The skills deployment target is unspecified.** The plan says deploy `skills/` to `~/.claude/skills/`. But skills also need to be registered in settings.json or discovered by Claude Code. The plan should verify whether simply copying the directory is sufficient or if there is a registration step.

---

## Consensus Addendum

### Antithesis (steelman against Option A)

The strongest argument for Option B (full rewrite) is that the secret management problem is **systemic, not local.** The current architecture has secrets scattered across three different template syntaxes: `__PLACEHOLDER__` in settings.json, `${ENV_VAR}` in MCP templates, and raw values that get copied through by backup.sh. A patch adds a fourth pattern (jq stripping in backup.sh). Each new MCP server or config file added in the future must correctly implement all relevant patterns, and there is no single enforcement point. A rewrite could unify secret handling into one mechanism (e.g., a single `secrets.sh` module that both install and backup source). The plan's "working foundation" argument is weakened by the fact that backup.sh's secret handling was already broken in production -- the foundation has a load-bearing crack.

### Tradeoff Tension

**Coverage completeness vs. deployment safety.** The plan's goal of "install = complete" (deploying ALL artifacts) is in tension with deployment safety. The more artifacts install.sh touches, the more damage a misconfigured .env or a bug in substitution logic can cause. Currently, install.sh's incompleteness is also its safety net -- it cannot break MCP configs it does not touch. Adding skills, claude.json, and env-var substitution for MCP configs means a single bad install.sh run could break Claude Code entirely (invalid JSON from bad sed, missing env vars producing literal `${}`). The plan needs a rollback strategy beyond the `/tmp` backup, or at minimum a post-deploy validation step that checks the deployed configs parse as valid JSON with no unresolved placeholders.

### Synthesis

Keep Option A (patch) but extract secret handling into a shared function. Create a `lib/secrets.sh` with:
- `strip_secrets_from_json <file>` -- replaces known env var values with `${NAME}` placeholders
- `inject_secrets_to_json <template> <output>` -- resolves `${NAME}` placeholders from .env
- `validate_no_raw_secrets <file>` -- verifies no unresolved real keys remain

Both install.sh and backup.sh source this file. This gives the architectural benefit of Option B (single enforcement point) without the rewrite risk. Add a post-deploy JSON validation step to install.sh that catches malformed output.

---

## Recommendations

1. **[CRITICAL] Specify concrete secret-stripping mechanism for backup.sh** -- effort: low -- impact: prevents another push rejection
2. **[HIGH] Add diff.sh to Phase 1 scope** -- effort: trivial -- impact: prevents false "in sync" reports
3. **[HIGH] Add post-deploy JSON validation to install.sh** -- effort: low -- impact: catches broken configs before they cause runtime failures
4. **[MEDIUM] Extract shared secret handling into lib/secrets.sh** -- effort: medium -- impact: prevents future secret-handling divergence
5. **[MEDIUM] Specify MCP env-var substitution mechanism** -- effort: low -- impact: install.sh MCP deploy will not work without this
6. **[LOW] Add TELEGRAM_BOT_TOKEN and all MCP keys to .env.template explicitly in Phase 2** -- effort: trivial -- impact: completeness
7. **[LOW] Verify skills deployment needs no registration step** -- effort: trivial -- impact: skills might not work after deploy

## References

- `backup.sh:33-36` -- raw cp of .mcp.json with zero secret stripping (the actual bug)
- `backup.sh:39-41` -- claude.json extracts mcpServers but preserves real key values
- `install.sh:74-77` -- deploys .mcp.json via raw cp with no env-var substitution
- `install.sh:44-49` -- settings.json uses sed-based placeholder replacement (different pattern than MCP)
- `mcp/mcp.json.template:14,34,45` -- three distinct `${ENV_VAR}` placeholders in mcp.json
- `mcp/claude.json.template:7` -- `${GOOGLE_API_KEY}` in headers (different structure than env-based keys)
- `.env.template:1-9` -- only ANTHROPIC_* vars, missing all MCP API keys
- `diff.sh:1-51` -- does not check skills/ or MCP configs
- `global/hooks/notifications/telegram_notify.sh:55` -- TELEGRAM_BOT_TOKEN not in .env.template
