---
description: Turn any prompt, doc, or task into a rigorous Claude Code /goal condition
argument-hint: <prompt | file path | description of the work>
---

# Goal Craft

Transform the input in `$ARGUMENTS` into a rigorous, evaluator-ready Claude Code
`/goal` completion condition.

## What this command does

1. **Reads the input** — a loose prompt, a file path, or a description of work.
2. **Engineers a condition** — applies the goal-engineering recipe to produce a
   copy-paste-ready `/goal` line.
3. **Self-reviews it** — runs the quality rubric and tightens any weak clause.
4. **Recommends how to run it** — names the fitting execution mode.

## Usage

```
/goal-craft make the auth tests stop being flaky
/goal-craft docs/checkout-spec.md
/goal-craft migrate every fetchUser call to the new userClient
```

## Implementation steps

When this command is invoked:

### 1. Capture and resolve the input

The raw input is `$ARGUMENTS`.

- If `$ARGUMENTS` is empty, stop and ask the user what work the goal should
  cover. Do not invent a goal.
- If `$ARGUMENTS` looks like a file path, use the Read tool to read that file
  and treat its contents as the input. If the path does not exist, report the
  exact path and ask the user to correct it.
- Otherwise treat `$ARGUMENTS` as the literal description of the work.

### 2. Engage the goal-engineering skill

Use the **goal-engineering** skill. Apply its six-step transformation procedure:
find the true end state, make it measurable, specify an evidence-forcing check,
capture constraints, add a turn or time bound, then self-review.

If the input shape matches a common pattern (tests passing, green build,
refactor to a budget, migration, backlog drain, spec implementation, coverage,
performance, dependency upgrade, lint cleanup), also consult the
**condition-library** skill and start from the matching template instead of
writing from scratch. Fill every placeholder.

### 3. Self-review before presenting

Run the goal-engineering self-review rubric. Confirm the condition is
transcript-provable, has exactly one end state, names a check that forces
evidence into the transcript, lists constraints, carries a bound, and is under
4,000 characters. Fix every failing item — do not present a condition with a
known weakness.

### 4. Present the result

Output exactly this structure:

```
## Crafted /goal condition

/goal <the full condition, on one line, ready to paste>

## Anatomy
- End state:   <one line>
- Check:       <one line>
- Constraints: <one line each>
- Bound:       <one line>

## Assumptions
<any interpretation or proxy made when the input was vague — or "none">

## Self-review
<rubric result: all clear, or what was tightened and why>

## Recommended orchestration
<one line: which execution mode fits, and why>
```

Keep the `/goal` line on its own line with no backticks or prose inside it, so
the user can select and copy it in one action.

### 5. Offer to run it

After presenting, tell the user they can run the goal with `/goal-run` — and
that `/goal-run` accepts an optional mode (`handoff`, `headless`, or `self`).

## Important notes

- **State every assumption.** When the input is vague, the measurable proxy
  chosen is a decision the user must be able to veto. Always surface it.
- **Never present an unbounded condition.** Every condition ends with a turn or
  time clause.
- **Do not start executing the goal.** This command only crafts the condition.
  Execution is `/goal-run`.

## Error handling

If any step fails:

- Report the specific problem (missing input, unreadable file path).
- Do not produce a half-formed condition — ask for what is missing instead.
