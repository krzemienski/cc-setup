---
name: goal-workflow
description: End-to-end workflow that takes any input and produces, then runs, a Claude Code /goal. Use whenever the user gives a task, idea, voice ramble, design doc, ticket, or rough description and wants Claude to "make a goal and run it", "goalify this", "set this up as an autonomous run", "turn this into a /goal and execute it", or "keep working until this is done". This is the one-stop entry point that routes input through condition design and execution orchestration so the user gets a finished, self-terminating run rather than a single reply. Ships an installable /goalify slash command. Delegates condition wording to goal-condition-architect and execution to goal-loop-orchestrator.
---

# Goal Workflow

The single entry point for "give me any input, I'll make a `/goal` and run it." This skill orchestrates the other two in the series:

```
any input  →  [goal-condition-architect]  →  /goal <condition>  →  [goal-loop-orchestrator]  →  runs to completion
```

Use this when the user wants the *whole* thing handled. Use the individual skills directly when they only want the condition written, or only want an existing condition run.

## The pipeline

### Stage 1 — Understand the input
Read whatever the user gave you and identify the **end state**: when is this unambiguously done? Inputs come in many shapes — a one-liner, a rambling voice note, a design doc, a ticket, a backlog. Pull the verifiable outcome out of it. If there genuinely isn't one (open-ended or subjective work), say so now and offer `/loop` or a plain prompt instead of forcing a goal. Don't proceed with an unprovable target.

If the input is ambiguous on the end state, ask **one** sharp clarifying question (what counts as done?) rather than guessing. Everything downstream depends on this.

### Stage 2 — Craft the condition
Apply **goal-condition-architect**: build a single condition with the four-part anatomy — one measurable end state, a stated check, the constraints that matter, and a turn/time bound — and make every criterion transcript-provable (a "show the output" step for each). Output the literal `/goal <condition>` in a fenced block. Keep it under 4,000 characters; distill, don't paste.

Show the user the crafted command and the bound you chose, with a one-line rationale. This is the natural confirmation point: a goal starts a turn the moment it's set, so let the user see the condition before it runs unless they've told you to go straight through.

### Stage 3 — Orchestrate the run
Apply **goal-loop-orchestrator**: check preconditions (trust accepted, hooks not disabled), decide on auto mode for unattended turns, and pick the execution mode (interactive / headless `-p` / remote).

How the goal actually starts matters and is easy to get wrong: `/goal` is parsed from **user input**, and a custom slash command (or this skill) only **expands into a prompt** — neither can self-execute `/goal`. So Claude's job here is to hand over the trigger, not pull it: present the exact `/goal <condition>` line for the user to paste (interactive), or the `claude -p "/goal <condition>"` wrapper for an unattended/headless kickoff. The user (or the headless invocation) is what sets the goal and starts the loop.

Then, during the loop, enforce the evidence-surfacing discipline so each turn lands real proof in the transcript — this is what lets the evaluator actually confirm completion, and it's the Iron Rule in goal form: real-system proof, no mocks, no stubs, no skipped checks. Bake the durable part of that discipline into the condition's "show the output" clauses (Stage 2), because the condition directs every turn even after this skill's guidance scrolls out of context.

### Stage 4 — Monitor to completion
Watch the evaluator's reason via `/goal` status. If it converges, let it finish — the goal clears itself and records an achieved entry. If it stalls (reason repeats, same error recurs, turns climb with no movement, or the loop tries to cheat), stop and diagnose per the orchestrator's stall-recovery guidance rather than waiting for the bound. Report completion with the achieved-status summary (duration, turns, token spend) as proof.

## Decision: full pipeline vs. just one stage

- **"goalify this" / "set this up and run it"** → full pipeline, all four stages.
- **"write me a goal for X"** → Stage 2 only (architect); hand back the command.
- **"run this goal: /goal ..."** → Stage 3-4 only (orchestrator).
- **Open-ended / subjective work** → don't goalify; recommend `/loop` or a normal prompt and explain why a goal won't confirm.

## The /goalify command

This skill ships a ready-to-install custom slash command, `/goalify`, that invokes this pipeline on whatever argument or context you give it. Installation and the command body are in **references/goalify-command.md**. Once installed, `/goalify migrate the parser to the new API until tests pass` runs the whole flow: craft the condition, then set the `/goal`.

## How this composes with your ecosystem

The series slots into the named-skill layering you already use. A condition's "show the output" clauses and "no mocks" constraints are the goal-language form of functional-validation, no-mocking-validation-gates, and gate-validation-discipline — the evaluator becomes the gate, and surfaced real-system evidence is what it checks. When a task already has a create-validation-plan output, lift each phase's exit criteria straight into the condition's checklist. When MCP servers are available in the session (sequential-thinking for decomposing a fuzzy input into a checkable end state, context7 for verifying a library's current API before writing the check, memory for carrying the condition and run outcome across sessions), use them at the stage where they help — decomposition in Stage 1, check accuracy in Stage 2, continuity in Stage 4.

## Reference files

- **references/goalify-command.md** — The installable `/goalify` slash command: where it goes, its frontmatter, and its body. Read when the user wants the command set up.
- **references/worked-examples.md** — Full input-to-running-goal walkthroughs across task types (vague one-liner, design doc, backlog, migration). Read for end-to-end examples of the pipeline in action.
