# Input Recipes

A worked recipe for every input type. Each recipe shows where the end state
hides, what to extract, and an example input transformed into a complete,
copy-paste-ready `/goal` condition. Match the input to the closest recipe, then
apply the six-step procedure from `SKILL.md`.

---

## 1. Vague one-liner

**Where the end state hides:** it does not — it must be inferred. The risk is
inventing an unmeasurable goal. The move is to pick the closest *measurable
proxy* and state the assumption so the user can correct it.

**Extract:** the implied outcome → a measurable proxy → the cheapest proof.

**Example input:** *"clean up the API folder"*

**Condition:**
```
/goal `npm run lint src/api` and `npm run typecheck` both exit 0 with Claude pasting each summary line, every file in src/api is 300 lines or fewer (proven with `wc -l`), and no exported symbol in src/api/index.ts is removed or renamed; or stop after 20 turns and list what remains
```

**Assumption to state:** "clean up" is read as lint-clean + type-clean + a
300-line-per-file budget, preserving the public surface. Confirm before running.

---

## 2. Design / spec doc

**Where the end state hides:** in the acceptance criteria. Each criterion is one
checkable clause.

**Extract:** the explicit acceptance criteria; if none are labeled, derive a
numbered list from the doc and reference it.

**Example input:** *"implement everything in docs/checkout-spec.md"*

**Condition:**
```
/goal every acceptance criterion listed in docs/checkout-spec.md is implemented and individually verified, with Claude printing a STATUS block each turn that names each criterion and shows the command output proving it; `npm test` exits 0; no criterion is marked done without surfaced proof; or stop after 45 turns and report which criteria remain
```

**Note:** if the doc has no acceptance criteria, first have Claude extract them
into a numbered checklist, then point the condition at that checklist.

---

## 3. Bug report

**Where the end state hides:** in the reproduction. The failing repro becomes
the passing check. Always pin a regression test so "fixed" is provable.

**Extract:** the exact reproduction steps → a failing test or command → its
passing form.

**Example input:** *"users get logged out after 5 minutes even with 'remember
me' checked"*

**Condition:**
```
/goal a regression test that reproduces the premature-logout bug exists, fails on the current code, and passes after the fix, with Claude pasting both the failing and passing runs; the full `npm test` suite still exits 0; the session-expiry logic is the only behavior changed and no test is weakened or skipped; or stop after 25 turns and report the root cause found
```

---

## 4. Refactor request

**Where the end state hides:** in a structural budget — size, count, or shape —
paired with a hard "behavior unchanged" constraint.

**Extract:** the structural target → the measuring command → the behavior-lock.

**Example input:** *"split the giant utils.ts into smaller modules"*

**Condition:**
```
/goal src/utils.ts is split so that every resulting module under src/utils/ is 200 lines or fewer (proven with `wc -l` output pasted for each file), all imports across the repo are updated, `npm run build` and `npm test` both exit 0 with summary lines pasted, and the public exports available before the split are all still importable; or stop after 30 turns and report remaining oversized modules
```

---

## 5. Migration

**Where the end state hides:** in completeness — *every* call site — plus a
green build and test suite proving nothing broke.

**Extract:** the old thing → the new thing → "every occurrence" → build/test
proof.

**Example input:** *"migrate from the old fetchUser API to the new userClient"*

**Condition:**
```
/goal every call site of the deprecated fetchUser API is migrated to userClient, proven by `grep -rn "fetchUser(" src/` returning no matches (output pasted), `npm run build` and `npm test` both exit 0 with summary lines pasted, and no behavior in the affected modules changes other than the API call itself; or stop after 40 turns and list any call sites that could not be migrated and why
```

---

## 6. Issue / task backlog

**Where the end state hides:** in an empty queue, plus a per-item definition of
done so items are not closed superficially.

**Extract:** the queue source → the per-item done check → the empty-queue proof.

**Example input:** *"work through the issues labeled 'good-first-issue'"*

**Condition:**
```
/goal every issue labeled good-first-issue is resolved: for each, Claude has implemented the fix, added or updated a test, and pasted the passing `npm test` output naming that test; the queue is empty (Claude lists the remaining labeled issues each turn and the list reaches zero); no unrelated issue or file is touched; or stop after 60 turns and report the remaining queue
```

**Note:** if issues live in an external tracker, have Claude pull the list into
the transcript first so the evaluator can see the queue shrink.

---

## 7. Performance target

**Where the end state hides:** in a number, with the exact command that measures
it. Pin the measurement so the evaluator reads one comparable line.

**Extract:** the metric → the threshold → the measuring command → a
no-regression constraint.

**Example input:** *"the search endpoint is too slow, speed it up"*

**Condition:**
```
/goal the search endpoint p95 latency is at or below 200ms, proven by Claude running `npm run bench:search` and pasting the p95 line on at least 3 separate runs; `npm test` still exits 0; the search results returned for the benchmark queries are unchanged from the pre-optimization baseline Claude recorded at the start; or stop after 30 turns and report the best p95 achieved
```

**Assumption to state:** a measurable benchmark command must exist; if it does
not, the first turn's job is to create one, and the condition should say so.

---

## 8. Cleanup / tech debt

**Where the end state hides:** in a count driven to zero — lint warnings, TODO
comments, dead files, type errors, deprecated calls.

**Extract:** the thing to count → the counting command → zero.

**Example input:** *"get rid of all the TODO comments in the codebase"*

**Condition:**
```
/goal `grep -rn "TODO" src/` returns no matches (output pasted), where each TODO has been either resolved by implementing the described work or converted into a tracked issue referenced in a code comment — not merely deleted; `npm test` exits 0; or stop after 35 turns and report the count of TODOs remaining and how each was handled
```

**Note the constraint** "not merely deleted" — without it, Claude can satisfy a
count-to-zero goal by erasing the markers. Count-based conditions almost always
need a "how, not just whether" constraint.

---

## Cross-cutting reminders

- **State every assumption.** When the input is vague, the proxy you chose is a
  decision the user should get to veto. Put it in the Assumptions block.
- **One end state.** If a recipe seems to need two, the second is usually a
  constraint ("…and no test is skipped") or a check, not a co-equal finish line.
- **Always bound.** Every example above ends with a turn clause. Never omit it.
- **Force the evidence.** Every example requires Claude to paste output. A
  condition that names a check but not its surfacing is half-written.
