# Critic Review: cc-setup Full Audit Fix Plan (Revised)

**Reviewer:** Critic
**Date:** 2026-03-20
**Plan:** `/Users/nick/cc-setup/plans/260320-1014-cc-setup-full-audit/plan.md`
**Architect Review:** `/Users/nick/cc-setup/plans/reports/architect-260320-1014-cc-setup-audit-review.md`
**Mode:** THOROUGH (no escalation to ADVERSARIAL -- findings are isolated, not systemic)

---

## VERDICT: APPROVE

**Overall Assessment:** The revised plan correctly incorporates all MUST items from the Architect's review (hooks merge algorithm, extraKnownMarketplaces path, post-merge validation, scalar key categorization, diff.sh fix, afplay documentation). The phased structure is sound, acceptance criteria are testable, and the merge algorithm is now specified with sufficient precision for an executor. Two findings need attention but neither blocks execution.

---

## Pre-commitment Predictions

Before detailed investigation, I predicted:
1. **Hook registration event/matcher mismatches** -- CONFIRMED (2 of 6 hooks have wrong or incomplete suggestions)
2. **Merge algorithm edge cases unspecified** -- NOT CONFIRMED (the algorithm is adequately specified after revision)
3. **Missing file references or stale line numbers** -- PARTIALLY CONFIRMED (line numbers are approximate but the plan acknowledges this)
4. **Platform gating incomplete** -- NOT CONFIRMED (macOS-only servers correctly identified)
5. **Deprecated/dead code registered as active** -- CONFIRMED (skill-dedup.cjs is deprecated)

---

## Critical Findings

None.

---

## Major Findings

**1. Phase 5: `skill-dedup.cjs` is deprecated and should NOT be registered**

The plan lists `skill-dedup.cjs` as one of the 6 hooks to register in Phase 5. However, the file's own header (lines 6-7) states:

> `@deprecated DISABLED in v2.9.1 due to race condition with parallel sessions.`
> `Hook file kept for reference; will be redesigned in future release.`

Registering a deprecated, known-broken hook would introduce a race condition bug described in the file itself ("concurrent sessions overwrite manifest, orphaning skills").

- Confidence: HIGH
- Why this matters: Registering a deprecated hook with a known race condition could cause skill files to be moved/orphaned across concurrent Claude Code sessions.
- Fix: Remove `skill-dedup.cjs` from the Phase 5 registration list. The plan should register 5 hooks, not 6. Update the overall success criteria from "All 26 hook files are deployed AND registered" to acknowledge that `skill-dedup.cjs` is deployed but intentionally unregistered. Alternatively, delete the file entirely if it serves no reference purpose.

**2. Phase 5: `documentation-context-check.js` has wrong event type in the registration table**

The plan's table says:
> `documentation-context-check.js | PreToolUse | Write|Edit|MultiEdit`

But the hook's own source code (line 2) declares itself as:
> `// UserPromptSubmit hook: Remind to check documentation...`

And line 58 confirms:
> `hookEventName: "UserPromptSubmit"`

This hook reads `data.message` (user prompt content), not tool inputs. It fires on user messages, not tool calls. Registering it as PreToolUse with a tool matcher would mean it never fires.

- Confidence: HIGH
- Why this matters: A wrongly-registered hook silently does nothing. The executor would register it, it would pass syntax checks, but it would never trigger.
- Fix: Change the table entry to: `documentation-context-check.js | UserPromptSubmit | (empty)`. Note: the plan already says "The executor must verify by reading hook source" -- this safety net is good, but the table itself should be corrected so the plan is usable as-is without requiring the executor to override it.

---

## Minor Findings

**1. Phase 5: `usage-context-awareness.cjs` registration is incomplete**

The hook's header (line 3) says "UserPromptSubmit & PostToolUse Hook" -- it handles two event types. The plan only registers it for UserPromptSubmit. The executor should check whether it needs a PostToolUse registration as well, or whether the UserPromptSubmit-only registration is intentional (the hook may use internal throttling to decide which event to respond to).

**2. Phase 5: `privacy-block.cjs` matcher may be too narrow**

The plan suggests `Write|Edit|MultiEdit`, but the hook's privacy checker (`lib/privacy-checker.cjs:210`) documents `toolName` as "Read, Write, Bash, etc." and the hook handles Read paths and Bash commands explicitly. A matcher of `Read|Write|Edit|MultiEdit|Bash` would match its actual scope. However, the plan's safety net note about executor verification covers this.

**3. Phase 1: `teammateMode` and `semantic_search` listed as user-wins scalars but absent from template**

The scalar key categorization lists `teammateMode` and `semantic_search` as user-wins keys, but neither exists in `global/settings.json.template`. This is not a bug (user-wins means "don't overwrite if user has it"), but it creates confusion about whether these should be added to the template baseline. If they are user-only keys that cc-setup never sets, they don't need to be in the categorization at all -- the merge logic only needs to know about keys that appear in the template.

**4. Open questions file referenced but not linked inline**

The plan references `/Users/nick/cc-setup/plans/open-questions.md` at the end but does not link specific open questions to the phases they affect. The question about "duplicate agents in plugin agents/ vs global/agents/" is directly relevant to Phase 2 Task 2.1 and should be resolved before execution (diff the overlapping files).

---

## What's Missing

- **Hook count in success criteria needs updating.** Success criterion #6 says "All 26 hook files are deployed AND registered." With `skill-dedup.cjs` deprecated, this should say "25 of 26 hooks registered; skill-dedup.cjs deployed but intentionally unregistered (deprecated)."
- **No rollback procedure for Phase 1.** The plan specifies post-merge validation that aborts on count decrease, but doesn't specify what happens to the install.sh run itself. Does the script exit non-zero? Does it continue deploying rules/hooks/CLAUDE.md? A merge abort should halt the entire install with a clear error and instructions.
- **diff.sh CLAUDE.md comparison is structurally broken.** `diff.sh:35` compares the raw template `global/CLAUDE.md` against the deployed `~/.claude/CLAUDE.md`, but install.sh always MERGES CLAUDE.md (prepending OMC block). This means diff.sh will always show a difference. The plan addresses the settings.json diff false positive (Task 2.4) but not the CLAUDE.md one.

---

## Ambiguity Risks

- `"dedupe_by_command(user_hooks_for_matcher + template_hooks_for_matcher)"` -- The ordering (user first, then template) implies user entries take precedence in dedup. This is correct but should be stated explicitly: "When the same command string appears in both user and template, keep the user's version (preserves any user modifications to hook arguments)."

---

## Multi-Perspective Notes

- **Executor:** The plan is executable as-is for Phases 1-4 and 6. Phase 5 requires the executor to override 2 of 6 table entries (documentation-context-check event type, skill-dedup removal). The "verify by reading source" note provides the safety net, but correcting the table avoids wasted investigation time.
- **Stakeholder:** The plan solves the stated problem (data loss on install). The phased approach with remote validation in Phase 6 provides confidence.
- **Skeptic:** The jq merge approach is the weakest link long-term (maintenance trap for new array keys). The post-merge count validation is the right mitigation. The ADR correctly acknowledges this tradeoff.

---

## Verdict Justification

APPROVE. The plan is well-structured, addresses all Architect MUST/SHOULD items, and has testable acceptance criteria. The two Major findings (skill-dedup registration, documentation-context-check wrong event type) are real errors that the executor would waste time on, but the plan's own safety net ("executor must verify by reading hook source") prevents them from causing runtime damage. The Minor findings and missing items are genuine but do not block execution.

No escalation to ADVERSARIAL mode was warranted -- the findings are isolated inaccuracies in the Phase 5 hook table, not systemic plan quality issues.

Realist check: Both Major findings affect Phase 5 only (hook registration). Even if the executor followed the table blindly, the worst case is 2 hooks that don't fire (documentation-context-check) or a deprecated hook that is registered but exits early due to its own internal disabled logic (skill-dedup). Neither causes data loss or system instability.

---

## Open Questions (unscored)

- Should `skill-dedup.cjs` be deleted from the hooks directory entirely rather than deployed-but-unregistered? Deploying dead code creates confusion for future audits.
- The open-questions.md asks about diffing global/agents/ vs plugin agents/ before deletion. This should be done (a quick diff) but is unlikely to surface meaningful divergence given the plugin is the actively maintained source.
- `serena` MCP server classification as macOS-only (per open questions) -- it uses `uvx` (Python) and may be cross-platform. Low risk either way.

---

*Ralplan summary row:*
- Principle/Option Consistency: **Pass** -- jq-only approach aligns with "zero new dependencies" principle; merge strategy aligns with "non-destructive deployments"
- Alternatives Depth: **Pass** -- Option B (external merge tool) fairly evaluated with clear invalidation rationale
- Risk/Verification Rigor: **Pass** -- Post-merge count validation addresses the maintenance trap; acceptance criteria are concrete and testable
- Deliberate Additions (if required): N/A (not deliberate mode)
