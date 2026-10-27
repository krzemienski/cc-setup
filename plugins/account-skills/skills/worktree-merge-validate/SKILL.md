---
name: worktree-merge-validate
description: >
  Review, complete, merge, and validate all git worktrees back into main.
  Analyzes every worktree's spec and code, finishes incomplete work, builds
  dependency-aware merge order, merges sequentially with conflict resolution,
  and functionally validates after each merge — no mocks, real system proof.
  Detects project type (iOS, web, CLI, API, full-stack) and routes to correct
  validation. Orchestrates functional-validation, e2e-validate,
  gate-validation-discipline, no-mocking-validation-gates, and
  full-functional-audit. Use when consolidating worktrees, merging feature
  branches, finishing stalled auto-claude tasks, or validating a merged
  codebase. Triggers: "merge worktrees", "consolidate branches", "finish
  auto-claude tasks", "land all worktrees", "worktree audit", "clean up
  branches", or when multiple git worktrees need to land on main.
---

# Auto-Claude Worktrees: Review, Complete, Merge, and Validate

## Role

You are a senior engineering lead consolidating git worktrees back into main.
Each worktree represents a feature branch — potentially with its own spec,
implementation plan, and progress artifacts. Your job: analyze every worktree,
finish incomplete ones, merge them in a safe order, and ensure the final
application is fully functional. Fix every issue you find immediately.

This is a long-running task. Plan your work clearly and make steady,
incremental progress. Spend your entire output context working systematically.
Do not stop until the task is complete.

---

## Validation Skill Stack

This skill orchestrates five companion skills that enforce real-system
validation at every stage. These are non-negotiable — invoke them as described.

| Skill | Role in This Workflow | When to Invoke |
|-------|----------------------|----------------|
| **gate-validation-discipline** | Evidence-based completion verification. Personally examine every artifact, cite specific proof, match evidence to criteria. | Before marking ANY gate, task, or phase complete. At every phase entry/exit. |
| **no-mocking-validation-gates** | Guard rail that catches mock/stub creation. If you think "let me add a mock fallback" — this skill explains why that's wrong and what to do instead. | Whenever facing integration challenges, timeouts, or API issues. Before writing any workaround code. |
| **functional-validation** | The Iron Rule + platform detection + single-feature validation protocol. Defines WHAT to validate and HOW per platform. | After every merge — validate the merged feature's acceptance criteria against the real running system. |
| **e2e-validate** | Full execution engine with workflows, scripts, templates, and CI mode. Handles analyze → plan → execute → report pipeline. | For comprehensive validation runs after merge batches land. Use `--fix` flag to auto-remediate failures. |
| **full-functional-audit** | Breadth-first audit of every screen/endpoint with team coordination. 5-phase EXPLORE → PLAN → EXECUTE → REMEDIATE → VERDICT protocol. | Phase 5 of this workflow — the full post-merge application audit. |

### Invocation Pattern

At every validation checkpoint, follow this sequence:

```
1. gate-validation-discipline → confirm rules loaded, bind evidence standards
2. functional-validation → detect platform, define PASS criteria, validate
3. e2e-validate (if comprehensive run needed) → full pipeline with evidence
4. gate-validation-discipline → verify evidence, cite proof, mark complete
```

The Iron Rule from functional-validation governs everything:
```
IF the real system doesn't work, FIX THE REAL SYSTEM.
NEVER create mocks, stubs, test doubles, or test files.
ALWAYS validate through the same interfaces real users experience.
```

---

## Project Type Detection

Detect the project type to route validation correctly. The **functional-validation**
and **e2e-validate** skills both have platform detection built in — defer to them.
But understand the routing:

| Indicator | Project Type | Validation Approach |
|-----------|-------------|---------------------|
| `.xcodeproj`, `.xcworkspace`, `Package.swift` | **iOS/macOS** | Simulator screenshots, video, logs via `xcrun simctl` |
| `package.json` with React/Vue/Next, `playwright.config` | **Web Frontend** | Playwright browser automation, screenshots |
| `Cargo.toml` with `[[bin]]`, `go.mod` with `main.go`, CLI binary | **CLI** | Binary execution, exit codes, stdout capture |
| REST routes, OpenAPI spec, Express/Vapor/FastAPI handlers | **Backend API** | `curl` requests, response body verification |
| Multiple of the above | **Full-Stack** | Bottom-up: Database → API → Frontend |

Platform-specific validation references are bundled with this skill:
- [references/ios-validation.md](references/ios-validation.md) — Simulator, screenshots, video, logs
- [references/web-validation.md](references/web-validation.md) — Playwright / agent-browser, console/network monitoring
- [references/cli-validation.md](references/cli-validation.md) — Binary execution, exit codes, stdout/stderr
- [references/api-validation.md](references/api-validation.md) — curl, CRUD lifecycle, error cases
- [references/fullstack-validation.md](references/fullstack-validation.md) — Bottom-up validation order, cross-layer integration

---

## Spec System Comprehension

Many auto-claude projects use a structured spec system at `.auto-claude/specs/`.
When it exists, it's the richest source of intent. When it doesn't, fall back
to git history and code analysis.

**Read [references/spec-system.md](references/spec-system.md)** for the full
inventory of spec files and how to interpret each one.

### Quick Reference — Key Spec Files

| File | What It Tells You |
|------|-------------------|
| `spec.md` | Source of truth: acceptance criteria define PASS for functional-validation |
| `requirements.json` | Dependencies and preconditions — drives merge ordering |
| `context.json` | Integration points — predicts conflict risk |
| `implementation_plan.json` | Planned approach — assess completeness against this |
| `task_metadata.json` | Status (done/in-progress/blocked), category |
| `memory/session_insights/` | Previous agent recommendations — read before continuing work |

### When No Spec System Exists

Fall back to: PR descriptions → commit messages → README changes → code
comments/TODOs → the diff itself. Infer intent, define your own acceptance
criteria, get human confirmation if available.

---

## The Six Phases

```
Phase 1: Deep Analysis of Every Worktree
Phase 2: Screen/Endpoint Inventory
Phase 3: Merge Orchestration Plan
Phase 4: Sequential Merge Execution      ← functional-validation after each
Phase 5: Full Application Functional Audit ← full-functional-audit
Phase 6: Cleanup and Final Validation      ← e2e-validate final run
```

Each phase has entry and exit gates enforced by **gate-validation-discipline**.

---

## Phase 1: Deep Analysis of Every Worktree

### Entry Gate (gate-validation-discipline)
- [ ] Main branch builds cleanly
- [ ] Real system starts (backend health check, app launch, etc.)
- [ ] Baseline established: what main looks like RIGHT NOW

### Discovery

```bash
git worktree list
ls .auto-claude/specs/ 2>/dev/null
```

Catalog all worktrees. Correlate each with its spec directory (if present).
Identify orphans in both directions.

### Per-Worktree Analysis

For EACH worktree, produce a structured report:

**1. Read All Available Context**
- Specs exist: read every file in the spec directory completely
- No specs: read commit history, branch diff, any documentation
- Always read `memory/session_insights/` — previous agents left advice

**2. Analyze Code Changes**
```bash
git diff main...<branch> --stat
git diff main...<branch>  # Every line of every changed file
```

**3. Assess Branch Health**
- Builds cleanly? Unresolved conflicts? TODO/FIXME markers?
- What does `build-progress.txt` say?

**4. Categorize**

| Category | Meaning | Action |
|----------|---------|--------|
| **Ready to merge** | Complete per spec, builds, low conflict risk | Merge in order |
| **Needs completion** | Incomplete work identified | Finish it first |
| **Needs conflict resolution** | Overlaps with other branches | Plan merge order carefully |
| **Abandon** | Stale, broken, superseded, or duplicate | Skip, document why |

**5. Report Template**
```
Branch: <name>
Spec: <number and slug, or "none">
Summary: <one paragraph>
Completeness: <percentage, specific gaps>
Build status: <compiles / fails / unknown>
Conflict risk: <files overlapping with other branches>
Dependencies: <which features must merge first>
Surfaces affected: <screens/endpoints/commands>
Category: Ready / Needs completion / Needs conflict resolution / Abandon
```

### Completing Incomplete Worktrees

For every "Needs completion" worktree:

1. Read the spec or infer intent
2. Read `memory/session_insights/` — follow the previous agent's recommendations
3. Identify specific gaps between current state and acceptance criteria
4. Implement the remaining work **on that branch**
5. Build and verify on that branch
6. Invoke **functional-validation** to validate the feature works
7. Invoke **gate-validation-discipline** to verify evidence before marking ready
8. Update the report — branch should now be "Ready to merge"

### Exit Gate (gate-validation-discipline)
- [ ] Every worktree has a structured report with cited evidence
- [ ] Every "Needs completion" branch completed and validated
- [ ] Main branch still clean and unmodified

---

## Phase 2: Screen/Endpoint Inventory

Build the full inventory of user-facing surfaces. This drives Phase 5's audit.

If **full-functional-audit** is available, its Phase 1 (EXPLORE) protocol
handles this — use it. Otherwise, do it manually per project type:

- **iOS/macOS**: Parse SwiftUI Views / UIKit ViewControllers, trace navigation
- **Web**: Parse routes and page components, trace navigation
- **CLI**: Catalog commands, subcommands, flags, arguments
- **API**: Catalog endpoints (method + path), request/response schemas

Cross-reference every surface with which worktree branches touch it.

### Exit Gate (gate-validation-discipline)
- [ ] Complete inventory with cited source files
- [ ] Each surface mapped to touching worktree branches

---

## Phase 3: Merge Orchestration Plan

### Dependency Graph Rules

| Pattern | Rule |
|---------|------|
| Zero file overlap | Independent — merge in any order |
| Branch B needs Branch A's changes | Merge A first |
| Same files touched | Conflict cluster — merge sequentially |
| Project config modified (`.pbxproj`, `package-lock.json`, migrations) | High conflict risk — extra care |

### Merge Order Principles

1. **Infrastructure first** — database, config, shared models
2. **Independent branches next** — zero-overlap, low risk
3. **Dependent branches in dependency order**
4. **Conflict clusters last** — highest risk

### Produce the Plan

| Order | Branch | Category | Conflict Risk | Dependencies | Validation Criteria |
|-------|--------|----------|---------------|--------------|---------------------|

Present this plan. Get human confirmation if available.

### Exit Gate (gate-validation-discipline)
- [ ] Linear merge order with rationale
- [ ] Pre-defined PASS criteria per branch from spec.md
- [ ] Main branch still clean

---

## Phase 4: Sequential Merge Execution

One merge at a time. Complete each fully before starting the next.

### Pre-Merge (every merge)
- [ ] `git status` — main is clean
- [ ] Build passes
- [ ] `git diff main...<branch>` — confirm expected changes

### Merge
```bash
git checkout main
git merge <branch>
```

**If conflicts:**
- Use spec files as resolution guides
- Pay special attention to project config files
- Preserve the intent documented in specs
- If ambiguous: choose what doesn't break existing functionality

### Post-Merge Validation (every merge)

Invoke **functional-validation** with the merged feature's acceptance criteria:

1. **Build** — zero errors. If fails: revert, fix, retry
2. **Launch** — real app starts without crash
3. **Feature validation** — exercise acceptance criteria against real system
4. **Regression check** — spot-check 5+ unrelated surfaces
5. **Evidence review** — invoke **gate-validation-discipline**, cite proof

Invoke **no-mocking-validation-gates** if you feel any temptation to mock.

### Post-Merge Decision

| Outcome | Action |
|---------|--------|
| All validation passes | Remove worktree, delete branch, commit, update progress |
| Build fails, fixable | Fix in-place, re-validate, proceed |
| Build fails, unfixable | `git merge --abort` or `git reset --hard HEAD~1`, document |
| Functional issues found | Immediate Remediation Protocol → fix → verify → proceed |

### After Each Merge
- Re-diff remaining branches against updated main
- Update conflict predictions and merge order if needed

### Exit Gate (gate-validation-discipline)
- [ ] All mergeable branches landed
- [ ] Main builds cleanly — cited build output
- [ ] Real system runs — cited health check
- [ ] All merged features validated — cited evidence per feature

---

## Phase 5: Full Application Functional Audit

Invoke **full-functional-audit** for the comprehensive audit. It handles:
- EXPLORE: inventory every surface (builds on Phase 2)
- PLAN: assign validation work with resource isolation
- EXECUTE: validate every interaction on every surface
- REMEDIATE: fix every issue found immediately (non-deferrable)
- VERDICT: produce final PASS/FAIL report

If **full-functional-audit** is not available, use **e2e-validate --execute --fix**
as the execution engine, following the per-surface audit checklist:

**Per Surface**: navigation works, every interactive element triggers correctly,
every input validates, lists populate with real data, all state variations
render, layout adapts, backend integration returns real data.

**Any issue = immediate fix.** See Immediate Remediation Protocol below.

### Exit Gate (gate-validation-discipline)
- [ ] Every surface audited with cited evidence
- [ ] Every issue fixed and verified — cited commit hashes
- [ ] Every merged feature's acceptance criteria met — cited proof
- [ ] VERDICT.md produced (if using full-functional-audit)

---

## Phase 6: Cleanup and Final Validation

### Cleanup
```bash
git worktree list        # Only main should remain
git worktree prune
git branch -d <merged>   # Delete merged branches
```

### Final Validation

Invoke **e2e-validate** for a final comprehensive run:
```
e2e-validate --execute --report
```

This produces the definitive evidence set for the completed codebase.

### Final Gate Sequence (gate-validation-discipline)
1. Build succeeds (clean build) — cite output
2. Real system starts — cite health check
3. Full functional validation passes — cite e2e-validate report
4. `git log --oneline` confirms all expected merges — cite log

**All four pass with cited evidence. If any fails: remediate, re-run.**

---

## Immediate Remediation Protocol

When any issue is found at any phase — fix it NOW. No deferral. No backlog.

```
1. STOP current audit flow
2. Document: surface, element, expected vs actual behavior
3. Diagnose root cause — read source, trace the code path
4. Invoke no-mocking-validation-gates — confirm you're not about to mock
5. Implement the minimal correct fix
6. Build — confirm it compiles
7. Invoke functional-validation — confirm fix resolves the issue
8. Test adjacent elements — confirm no regressions
9. Invoke gate-validation-discipline — cite evidence of fix
10. Commit: fix(<surface>): <what was broken and how>
11. Only after all pass: resume the audit
```

No severity threshold. Everything gets fixed. One fix, one commit.

---

## Progress Tracking

Maintain `worktree-merge-progress.json` at the repository root:

```json
{
  "phase": "merge_execution",
  "worktrees": {
    "branch-name": {
      "status": "analyzing | completing | ready | merging | merged | abandoned",
      "spec": "123-feature-slug",
      "completeness": 85,
      "conflict_risk": "low | medium | high",
      "merge_order": 3,
      "validation_result": "pass | fail | pending"
    }
  },
  "surfaces_audited": {
    "HomeScreen": { "status": "passed", "issues_found": 2, "issues_fixed": 2 }
  },
  "merge_log": [
    { "branch": "...", "merged_at": "...", "conflicts": false, "validation": "pass" }
  ]
}
```

Update after every significant action. If resuming in a new context window,
read this file + recent `git log` first.

### Git Hygiene
- Commit after every merge and every fix
- Descriptive messages: `merge(<branch>): ...` and `fix(<surface>): ...`
- Codebase always clean, buildable, runnable between actions

---

## Sub-Agent Orchestration

When subagents are available, use them for parallelism:

**Team Alpha — Worktree Analysis** (parallel, one per worktree):
Read specs, diff branches, assess health, produce reports.
Each agent invokes **gate-validation-discipline** at initialization.

**Team Beta — Surface Audit** (parallel, per surface group):
Each agent gets unique surfaces + dedicated test environment.
Each invokes **functional-validation** per surface.
Resource isolation: no shared simulators, no shared browser instances.
Follow **full-functional-audit**'s team coordination protocol.

**Team Gamma — Merge Execution** (sequential, one at a time):
Exclusive write access to main. Invokes **functional-validation** post-merge
and **gate-validation-discipline** before marking merge complete.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|---------------------|
| Merge all branches at once | Can't isolate which branch broke what | One merge at a time, validate between |
| Skip validation "to save time" | 10x longer debugging a broken main | Validate after every merge |
| Mock the backend for testing | Mocks diverge from reality | Invoke no-mocking-validation-gates, fix the real system |
| Defer "minor" issues | 50 minor issues = unusable app | Immediate Remediation Protocol |
| Batch fixes into one commit | Can't bisect, can't revert | One fix, one commit |
| Trust build success = works | Build checks syntax, not behavior | Run the app, invoke functional-validation |
| Claim PASS without evidence | Gate-validation-discipline exists for this | Cite specific proof for every completion |

---

## When NOT to Use

- **Single feature or bug fix validation** — use `functional-validation` directly
- **No worktrees to merge** (single-branch project) — use `e2e-validate` or `full-functional-audit`
- **Code review without execution** — use `code-review`
- **Performance profiling** — use dedicated profiling tools
- **TDD projects requiring test files** — this skill forbids all mocks/test files
- **Fewer than 3 worktrees** — manual merge + `functional-validation` may be simpler

## Conflicts

- **full-functional-audit** — Overlapping scope in Phase 5. Use `worktree-merge-validate` when you have multiple worktrees to consolidate AND audit. Use `full-functional-audit` alone when main is already clean and you just need a comprehensive audit.
- **e2e-validate** — Complementary: this skill uses `e2e-validate` as its execution engine for comprehensive validation runs. Use `e2e-validate` alone for one-shot validation without the merge workflow.

## Related Skills

- **functional-validation** — Iron Rule philosophy and platform-specific validation protocol. Invoked after every merge.
- **e2e-validate** — Full execution engine with workflows, scripts, templates. Invoked for comprehensive validation runs.
- **gate-validation-discipline** — Evidence-based completion verification. Invoked at every phase gate.
- **no-mocking-validation-gates** — Guard rail against mock/stub creation. Active throughout.
- **full-functional-audit** — Breadth-first audit of every screen/endpoint. Invoked in Phase 5.
- **verification-before-completion** — Behavioral pre-completion checks. Invoked before claiming any phase complete.
- **visual-inspection** — Systematic visual QA for UI screenshots (iOS HIG, WCAG 2.2). Used during Phase 5 audit.
- **agent-browser** — Browser automation for web platform validation. Used by e2e-validate/functional-validation for web projects.
- **preflight** — Pre-session environment checks. Run before starting Phase 1 to catch blockers early.
- **create-validation-plan** — Creates gated plans; use when planning the merge sequence as a formal plan.
- **transform-validation-prompt** — Transforms prompts to embed validation gates. Use when converting ad-hoc merge instructions into gated workflows.
- **ios-validation-runner** — iOS-specific simulator automation; used by functional-validation for iOS projects.

---

## Evidence Artifacts

Every validation produces files. Evidence is what separates a claim from a fact.

Create `worktree-merge-evidence/` at the repository root, organized by phase:

```
worktree-merge-evidence/
├── manifest.json              # Master evidence index
├── phase-1-analysis/          # Branch reports + baseline evidence
├── phase-4-merges/            # Per-merge: build logs, screenshots, curl, video
│   └── merge-001-<branch>/
│       └── validation/        # screenshots/, curl-responses/, cli-outputs/, logs/, video/
├── phase-5-audit/             # Full audit: screenshots, responses, VERDICT.md
├── phase-6-final/             # Final build, health check, git log, e2e report
└── remediation/               # Per-fix: before + after evidence, commit hash, description
    └── fix-001-<slug>/        # before.png, after.png, commit-hash.txt, description.md
```

**Read [references/evidence-standards.md](references/evidence-standards.md)** for
the full directory structure, manifest JSON schema, naming conventions,
platform-specific collection patterns (iOS screenshots + video, Playwright
captures, curl responses, CLI stdout), and remediation evidence templates.

### Evidence Rules

1. **File existence is not evidence.** Always READ screenshots, always PARSE JSON responses.
2. **Before AND after for every remediation.** Prove it was broken. Prove it's fixed.
3. **Number evidence sequentially.** `01-`, `02-`, `03-` within each directory.
4. **Name evidence descriptively.** `01-login-screen.png` not `screenshot1.png`.
5. **Capture logs BEFORE launching the app.** Start log streaming first, then launch.
6. **Update manifest.json after every evidence capture.** This is the audit trail.

### Evidence Types by Platform

| Platform | Primary Evidence | Secondary Evidence |
|----------|-----------------|-------------------|
| **iOS/macOS** | Simulator screenshots (.png), screen recordings (.mov) | App logs, build output, health checks |
| **Web** | Playwright/agent-browser screenshots (.png) | Console errors (.txt), network failures (.txt), responsive viewport captures |
| **CLI** | stdout/stderr captures (.txt), exit codes | Output files produced by CLI, timing data |
| **API** | curl response bodies (.json), HTTP status codes | Response headers, timing, database state verification |
| **Full-Stack** | All of the above, organized bottom-up | Cross-layer integration evidence |

---

## Documentation Outputs

These deliverables go into `worktree-merge-evidence/`. Each links to raw evidence.

| Document | Phase | Contents |
|----------|-------|----------|
| `disposition.md` | 1 | Per-worktree: branch, spec, completeness, build status, category, action taken |
| `merge-log.md` | 4 | Per-merge: order, branch, conflicts, resolution, build result, validation result, evidence path |
| `remediation-log.md` | 4-5 | Per-fix: surface, element, issue, root cause, fix, commit, before/after evidence paths |
| `final-state.md` | 6 | Checklist: zero worktrees, build passes, system runs, all surfaces validated, all fixes committed — each with cited evidence path |
| `manifest.json` | All | Machine-readable index of every evidence artifact (see [references/evidence-standards.md](references/evidence-standards.md)) |
