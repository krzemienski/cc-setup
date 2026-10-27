---
name: verification-before-completion
description: |
  Enforce evidence-before-assertions discipline for all completion claims.
  Use when: about to claim work is complete/fixed/passing, before committing or creating PRs, before marking tasks done
  Covers: gate function (identify/run/read/verify/claim), claim-type verification matrix, red flag detection, rationalization prevention
  Keywords: verification, completion, evidence, gate, assertion, pre-commit, pre-push, claim-validation
---

# Verification Before Completion

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status:
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
5. ONLY THEN: Make the claim
```

## Verification Requirements by Claim Type

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | Previous run, "should pass" |
| Build succeeds | Build command: exit 0 | Linter passing |
| Bug fixed | Original symptom: passes | Code changed, assumed fixed |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags — STOP Immediately

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification
- About to commit/push/PR without verification
- Trusting agent success reports without independent check
- ANY wording implying success without having run verification

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence is not evidence |
| "Linter passed" | Linter is not compiler |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Saying "should work now" after code change | Code changes are not evidence; untested assumptions cause regressions | Run the verification command fresh, read full output, confirm zero failures |
| Trusting agent success reports without independent check | Agents can report success on partial completion or misinterpreted output | Run verification yourself; check exit codes, failure counts, actual output |
| Using linter pass as proof of build success | Linter checks syntax/style, not compilation or runtime correctness | Run the actual build command and confirm exit code 0 |
| Committing/pushing before running verification | Broken code reaches shared branches; CI catches what you should have | Always run full verification suite before any git commit or push |
| Checking only exit code, ignoring output content | Exit code 0 with "3 tests skipped" or warnings can hide real failures | Read full output — count failures, warnings, skipped items explicitly |

## When NOT to Use

- Exploratory coding where completion is not being claimed — just experimenting
- Reading/researching code without making changes — no claim to verify
- When another skill (e.g., `gate-validation-discipline`) is already enforcing verification

## Conflicts

- `gate-validation-discipline`: Both enforce evidence-before-claims. This skill is the lightweight version (single gate check); gate-validation-discipline is the comprehensive multi-gate protocol. Use this for quick pre-commit checks, gate-validation-discipline for formal milestone verification
- `functional-validation`: That skill defines WHAT to validate (real system, real UI); this skill defines WHEN to validate (before any completion claim). They are complementary, not alternatives

## Related Skills

- `gate-validation-discipline` — evidence verification loop for gates and checkpoints
- `functional-validation` — the Iron Rule for real-system validation
- `e2e-validate` — produces the evidence that gets verified
- `preflight` — pre-session checks before validation work begins
