---
name: goal-condition-architect
description: Transform any input into a single, airtight Claude Code /goal completion condition. Use whenever the user wants to "set a goal", "make a /goal", "turn this into a goal", "give Claude a finish line", or describes substantial multi-turn work with a verifiable end state (migrate a module until tests pass, implement a design doc until all acceptance criteria hold, clear an issue backlog, split a file until each part is under a size budget). Also use when a vague task, voice ramble, design doc, ticket, or feature request needs to become an autonomous, self-terminating Claude Code run. Outputs a ready-to-paste /goal command engineered so the Haiku evaluator can actually confirm completion. Pair with goal-loop-orchestrator to run it.
---

# Goal Condition Architect

Turn any input — a one-line idea, a voice ramble, a design doc, a ticket, a backlog — into **one** Claude Code `/goal` condition that is verifiable, bounded, and engineered for the evaluator that judges it.

## The one fact that governs everything

`/goal` keeps Claude working across turns. After **each turn**, a small fast model (Haiku by default) reads the **conversation transcript so far** and decides yes/no on your condition, returning a short reason. "No" starts another turn with that reason as guidance; "yes" clears the goal.

The evaluator **runs no tools**. It does not execute commands, read files, or inspect the repo. It judges **only what Claude has surfaced as text in the transcript.**

Therefore the prime directive of a good condition:

> **Write the condition as something Claude's own visible output can prove. If the proof never lands in the transcript, the goal can never be confirmed — it will loop until it hits its bound.**

This is the same discipline as the Iron Rule: real-system proof, surfaced. A condition like "the code is correct" is unjudgeable. "`npm test` exits 0 and the run summary is shown in the reply" is judgeable, because Claude runs the tests and the result lands where the evaluator can read it.

## Workflow

1. **Extract the true end state.** Read the input and answer: *when is this unambiguously done?* If the input is vague ("clean up the auth module"), pin it to a measurable target ("every file in `src/auth` is under 300 lines and `npm test` passes"). If you cannot find a measurable end state, that is the finding — surface it and ask one clarifying question rather than inventing a fake one.

2. **Build the condition from the four-part anatomy** (below). Every condition needs the measurable end state and the stated check; add constraints and a bound when they apply (the bound almost always applies).

3. **Make it transcript-provable.** For every clause, name the artifact Claude must print so the evaluator can see it: the test summary, the exit code, the file count, the empty queue, the clean `git status`. If a clause can't be surfaced, rewrite it until it can.

4. **Fit the budget.** The condition can be up to **4,000 characters**. Aim well under that; tighter conditions evaluate more reliably. If the input is huge (a whole design doc), distill it to the acceptance criteria, don't paste it.

5. **Emit the literal command.** Output a single fenced block containing exactly `/goal <condition>` — paste-ready, one logical condition, no preamble inside the block.

6. **Hand off.** State the bound you chose and why, then offer to run it via **goal-loop-orchestrator** (which handles auto mode, evidence surfacing, monitoring, and recovery).

## The four-part anatomy

A condition that survives many turns has these parts. Weave them into prose — this is a directive Claude reads, not a form.

1. **One measurable end state** — a single observable: a test result, a build exit code, a file count, an empty queue, a clean working tree. One target, not five loosely related ones. If the work genuinely has several criteria, list them as an explicit checklist *within the one condition* and require all to hold.

2. **A stated check** — *how* Claude proves it, named concretely: `npm test exits 0`, `git status is clean`, `every file in src/parsers is ≤ 200 lines (show the wc -l output)`, `the issue queue is empty (show the gh issue list output)`. The check names the command **and** requires its output be shown.

3. **Constraints that matter** — what must *not* change on the way there: "no test file is modified", "the public API in `index.ts` is unchanged", "no new dependencies added". Constraints stop a goal from "succeeding" by cheating (deleting the failing test, stubbing the function). This is where you encode the Iron Rule: forbid mocks, stubs, and skipped tests explicitly when the task invites them.

4. **A bound** — almost always include one. Append a turn or time clause: `or stop after 20 turns`, `or stop after 45 minutes`. Claude reports progress against the bound each turn and the evaluator judges it from the transcript. A bound converts a possible infinite loop into a controlled stop you can inspect. Choose it from the work size (see references/condition-patterns.md for defaults).

## Quick examples

**Example 1 — vague input becomes provable**
Input: "get the auth tests green"
Output:
```
/goal All tests under test/auth pass: run `npm test -- test/auth` and show the full summary line proving 0 failures. Do not modify, skip, or delete any test to achieve this — fix the implementation. Stop after 15 turns and report the last failing test if not green by then.
```

**Example 2 — design doc becomes a checklist condition**
Input: "implement everything in DESIGN.md for the export feature"
Output:
```
/goal The export feature in DESIGN.md is complete, proven by all of: (1) `npm run build` exits 0 — show the exit status; (2) the new `exportToCsv` and `exportToJson` functions exist and their integration test `npm test -- export` passes — show the summary; (3) `README.md` documents both commands — show the diff. Constraints: no existing public export is renamed; no mocks or stubbed return values in the implementation. Stop after 30 turns and summarize remaining gaps if not all three hold.
```

**Example 3 — backlog becomes an empty-queue condition**
Input: "work through the bug-label issues"
Output:
```
/goal The queue of open issues labeled `bug` is empty: after each fix, run `gh issue list --label bug --state open` and show its output; the goal holds only when that command prints no issues. Each closed issue must reference the commit that fixed it. Do not close an issue without a real code change. Stop after 25 turns and list the issues still open if any remain.
```

## When the input has no verifiable end state

Some inputs are open-ended ("make the UI nicer", "explore options for caching"). `/goal` is the wrong tool for genuinely unbounded or subjective work — say so. Either (a) negotiate a measurable proxy ("three specific UX issues from the audit are fixed and screenshots are shown"), or (b) recommend `/loop` (time-interval re-runs) or a plain prompt instead. Don't manufacture a fake metric; an unprovable condition just loops to its bound and wastes turns.

## Reference files

Read these as needed — don't load everything up front:

- **references/goal-mechanics.md** — Ground-truth on how `/goal` works: the evaluator, status/clear/resume, headless `-p`, requirements, and how it compares to `/loop`, Stop hooks, and auto mode. Read when you need precise behavior or are explaining `/goal` to the user.
- **references/condition-patterns.md** — Ready-to-adapt templates per task type (test-until-green, migration, refactor-to-budget, backlog-drain, doc-sync, data-pipeline) plus recommended turn/time bounds by work size. Read when drafting a condition for a recognizable task shape.
- **references/anti-patterns.md** — The conditions that fail and why (unprovable claims, multi-goal soup, no bound, cheatable success, pasting whole docs). Read before finalizing to sanity-check your draft.
