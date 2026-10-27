# Condition Templates

Ten proven `/goal` condition templates. For each: the parameterized template,
then a filled example. Copy the template, replace every `{{placeholder}}`, run
the goal-engineering self-review, then hand to goal-orchestration.

Every template forces evidence, carries one end state, ships a default
constraint, and ends with a bound. Tighten the constraints per task.

---

## 1. tests-pass

Make a test suite, or a named subset, pass reliably.

**Template:**
```
/goal {{test_command}} exits 0 with Claude pasting the final summary line, and the suite passes on {{run_count}} consecutive runs to rule out flakiness; no test is weakened, skipped, marked .only/.skip, or deleted, and no file outside {{scope_path}} is modified; or stop after {{turn_budget}} turns and report which run failed and the failure output
```

**Filled example:**
```
/goal `npm test -- test/auth` exits 0 with Claude pasting the final summary line, and the suite passes on 5 consecutive runs to rule out flakiness; no test is weakened, skipped, marked .only/.skip, or deleted, and no file outside src/auth/ or test/auth/ is modified; or stop after 20 turns and report which run failed and the failure output
```

---

## 2. build-green

Get a build, compile, or typecheck step to exit clean.

**Template:**
```
/goal {{build_command}} exits 0 with Claude pasting the final lines of the output, every error and warning it reported is resolved at the source rather than suppressed, and {{constraint}}; or stop after {{turn_budget}} turns and report the remaining errors verbatim
```

**Filled example:**
```
/goal `npm run build` exits 0 with Claude pasting the final lines of the output, every error and warning it reported is resolved at the source rather than suppressed, and no `// @ts-ignore`, `any`, or `eslint-disable` is added to silence a problem; or stop after 25 turns and report the remaining errors verbatim
```

---

## 3. refactor-budget

Restructure code to a size or count budget while behavior stays locked.

**Template:**
```
/goal {{target}} is restructured so that {{budget_metric}}, proven with {{measuring_command}} output pasted for each affected file; {{build_command}} and {{test_command}} both exit 0 with summary lines pasted; and the public API exported before the refactor is all still importable with unchanged signatures; or stop after {{turn_budget}} turns and report which files still exceed the budget
```

**Filled example:**
```
/goal src/utils.ts is restructured so that every module under src/utils/ is 200 lines or fewer, proven with `wc -l` output pasted for each affected file; `npm run build` and `npm test` both exit 0 with summary lines pasted; and the public API exported before the refactor is all still importable with unchanged signatures; or stop after 30 turns and report which files still exceed the budget
```

---

## 4. migration

Move every call site from an old API, pattern, or library to a new one.

**Template:**
```
/goal every use of {{old_thing}} is migrated to {{new_thing}}, proven by {{search_command}} returning no matches with the output pasted; {{build_command}} and {{test_command}} both exit 0 with summary lines pasted; no behavior changes other than the migration itself; or stop after {{turn_budget}} turns and list any call sites that could not be migrated and why
```

**Filled example:**
```
/goal every use of the deprecated `fetchUser(` API is migrated to `userClient.get`, proven by `grep -rn "fetchUser(" src/` returning no matches with the output pasted; `npm run build` and `npm test` both exit 0 with summary lines pasted; no behavior changes other than the migration itself; or stop after 40 turns and list any call sites that could not be migrated and why
```

---

## 5. backlog-drain

Work a queue of issues or tasks until it is empty.

**Template:**
```
/goal every item in {{queue_source}} is resolved: for each, Claude has {{per_item_done}} and pasted the proof; Claude lists the remaining queue at the end of every turn and that list reaches zero; no item or file unrelated to the queue is touched; or stop after {{turn_budget}} turns and report the remaining queue
```

**Filled example:**
```
/goal every item in the checklist in TODO.md under the "v2 release" heading is resolved: for each, Claude has implemented the change, added or updated a test, and pasted the passing `npm test` output naming that test; Claude lists the remaining queue at the end of every turn and that list reaches zero; no item or file unrelated to the queue is touched; or stop after 50 turns and report the remaining queue
```

---

## 6. spec-implement

Implement every acceptance criterion in a design or spec document.

**Template:**
```
/goal every acceptance criterion in {{spec_path}} is implemented and individually verified; Claude prints a STATUS block each turn naming every criterion with the command output proving it; {{test_command}} exits 0; no criterion is marked done without surfaced proof; or stop after {{turn_budget}} turns and report which criteria remain
```

**Filled example:**
```
/goal every acceptance criterion in docs/checkout-spec.md is implemented and individually verified; Claude prints a STATUS block each turn naming every criterion with the command output proving it; `npm test` exits 0; no criterion is marked done without surfaced proof; or stop after 45 turns and report which criteria remain
```

---

## 7. coverage-target

Raise test coverage to a threshold without gaming the metric.

**Template:**
```
/goal test coverage for {{scope_path}} is at or above {{threshold}}, proven by Claude running {{coverage_command}} and pasting the coverage summary line; the added tests assert real behavior and would fail if that behavior broke (not trivial or assertion-free tests); {{test_command}} exits 0; or stop after {{turn_budget}} turns and report the coverage reached
```

**Filled example:**
```
/goal test coverage for src/payments/ is at or above 85% line coverage, proven by Claude running `npm run coverage` and pasting the coverage summary line; the added tests assert real behavior and would fail if that behavior broke (not trivial or assertion-free tests); `npm test` exits 0; or stop after 35 turns and report the coverage reached
```

---

## 8. performance-target

Hit a latency, throughput, or size number.

**Template:**
```
/goal {{metric}} is at or {{direction}} {{threshold}}, proven by Claude running {{measuring_command}} and pasting the result line on at least 3 separate runs; {{test_command}} still exits 0; {{correctness_constraint}}; or stop after {{turn_budget}} turns and report the best result achieved
```

**Filled example:**
```
/goal the search endpoint p95 latency is at or below 200ms, proven by Claude running `npm run bench:search` and pasting the p95 line on at least 3 separate runs; `npm test` still exits 0; the search results for the benchmark queries are byte-identical to the baseline Claude recorded on turn 1; or stop after 30 turns and report the best p95 achieved
```

---

## 9. dependency-upgrade

Upgrade a dependency and keep the build and tests green.

**Template:**
```
/goal {{package}} is upgraded to {{target_version}} in {{manifest_file}}, every breaking change from that upgrade is fixed at the call sites, {{build_command}} and {{test_command}} both exit 0 with summary lines pasted, and no other dependency version is changed; or stop after {{turn_budget}} turns and report the remaining breakage
```

**Filled example:**
```
/goal `react-router` is upgraded to version 7 in package.json, every breaking change from that upgrade is fixed at the call sites, `npm run build` and `npm test` both exit 0 with summary lines pasted, and no other dependency version is changed; or stop after 30 turns and report the remaining breakage
```

---

## 10. lint-clean

Drive lint or type warnings to zero — honestly, not by suppression.

**Template:**
```
/goal {{lint_command}} reports zero errors and zero warnings with Claude pasting the final count line, where every issue was fixed at the source — not suppressed with inline disables, rule-disabling config edits, or deletion of the flagged code unless deletion is the correct fix; {{test_command}} exits 0; or stop after {{turn_budget}} turns and report the remaining count by rule
```

**Filled example:**
```
/goal `npm run lint` reports zero errors and zero warnings with Claude pasting the final count line, where every issue was fixed at the source — not suppressed with inline disables, rule-disabling config edits, or deletion of the flagged code unless deletion is the correct fix; `npm test` exits 0; or stop after 25 turns and report the remaining count by rule
```

---

## Filling checklist

Before running any filled template, confirm:

- [ ] Every `{{placeholder}}` is replaced — none remain.
- [ ] Commands are the real commands for this project (checked against its
      `package.json`, `Makefile`, or equivalent).
- [ ] `{{scope_path}}` actually contains the work and nothing critical is
      wrongly excluded or included.
- [ ] `{{turn_budget}}` is sized to the task, not left at the example value.
- [ ] Constraints are tightened for anything fragile specific to this task.
- [ ] The condition is one sentence per clause, transcript-provable, and under
      4,000 characters.
