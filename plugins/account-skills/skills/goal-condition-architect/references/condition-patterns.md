# Condition patterns and bounds

Adapt these templates to the input. Every one names the **proof artifact** the evaluator must see, because the evaluator reads only the transcript. Replace bracketed parts; keep the "show ..." clauses — they are what makes the goal confirmable.

## Choosing a bound

Always include a bound unless the user explicitly wants it to run unbounded. Pick from work size:

| Work size | Suggested bound |
| --- | --- |
| Small, single target (one test file green, one function done) | `or stop after 10 turns` |
| Medium (a module, a feature with a few criteria) | `or stop after 20 turns` |
| Large (multi-file migration, full design doc) | `or stop after 30-40 turns` |
| Backlog / queue drain | scale to queue length; `or stop after 25 turns` is a safe default |
| Time-boxed by the user | use a time clause: `or stop after 45 minutes` |

A bound is a safety net, not a target. The condition should still be reachable well before it. If a goal regularly hits its bound, the condition is probably unprovable or the work is underscoped — revisit, don't just raise the bound.

## Pattern: test-until-green

```
/goal All tests in [path/scope] pass. Run `[test command]` and show the full summary line proving 0 failures. Fix the implementation, not the tests — do not modify, skip, xfail, or delete any test, and do not add mocks or stubbed return values. Stop after [N] turns and report the last failing test if not green by then.
```

## Pattern: migration / API swap

```
/goal Every call site of [old API] is migrated to [new API]: `grep -rn "[old symbol]" [src dir]` returns nothing (show its output), and `[build command]` exits 0 (show the exit status) and `[test command]` passes (show the summary). Constraints: public signatures in [entrypoint] are unchanged; no call site is deleted to make the grep pass. Stop after [N] turns and list remaining call sites if any.
```

## Pattern: refactor to a size/complexity budget

```
/goal Every file in [dir] is at most [N] lines: run `wc -l [dir]/*` (or the recursive equivalent) and show the output proving no file exceeds [N]. Behavior is preserved: `[test command]` still passes (show the summary). Do not move code into a single dumping-ground file to game the count, and do not delete tests. Stop after [N] turns and show the largest remaining file if over budget.
```

## Pattern: design-doc acceptance criteria

```
/goal The [feature] described in [doc] is complete, proven by ALL of: (1) [criterion 1] — [how to show it]; (2) [criterion 2] — [how to show it]; (3) [criterion 3] — [how to show it]. The goal holds only when every item is demonstrated in the transcript. Constraints: [what must not change]; no mocks or stubbed implementations. Stop after [N] turns and summarize which criteria remain unmet.
```

## Pattern: backlog / queue drain

```
/goal The queue of [items, e.g. open issues labeled bug] is empty: after each item, run `[list command]` and show its output; the goal holds only when that command shows an empty list. Each item resolved must reference the [commit/PR/file] that resolved it. Do not remove an item without a real change. Stop after [N] turns and list what remains.
```

## Pattern: doc / changelog sync

```
/goal [Doc, e.g. CHANGELOG.md] has an entry for every [unit, e.g. PR merged this week]: show the command that enumerates the units (e.g. `gh pr list --state merged --search "merged:>=[date]"`) and show the resulting doc section so each unit maps to an entry. Do not invent entries for units that do not exist. Stop after [N] turns and list any unit still missing an entry.
```

## Pattern: data / build pipeline produces a verified artifact

```
/goal Running `[pipeline command]` produces [artifact] that passes [validation]: show the command's exit status and the validation output (e.g. row count, schema check, checksum). Use real input data from [source] — no sample, fake, or truncated data. Stop after [N] turns and show the failing validation if the artifact is not valid.
```

## Composition note

These compose with named skills you already layer (functional-validation, no-mocking-validation-gates, gate-validation-discipline, e2e-validate). The condition's "show ..." clauses and "no mocks" constraints are the goal-language encoding of those gates: the evaluator becomes the gatekeeper, and the surfaced evidence is what it checks. When a task already has a validation plan, lift its phase exit criteria straight into the condition's checklist.
