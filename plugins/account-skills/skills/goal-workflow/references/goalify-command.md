# The `/goalify` slash command

A custom Claude Code slash command that runs the goal-workflow pipeline on whatever you pass it: it crafts a transcript-provable `/goal` condition from your input and sets it running.

## Install

Save the body below to one of these locations (Claude Code reads both):

- **Project scope** (shared with the repo): `.claude/commands/goalify.md`
- **User scope** (available everywhere): `~/.claude/commands/goalify.md`

The filename is the command name, so `goalify.md` gives you `/goalify`. The `$ARGUMENTS` placeholder receives everything you type after the command.

## Usage

```text
/goalify migrate src/parser to the new tokenizer API until the build is clean and parser tests pass
```

With no argument, it operates on the current conversation context (useful right after pasting a design doc or discussing a task):

```text
/goalify
```

## Command body

Save exactly this as `goalify.md`:

```markdown
---
description: Turn any input into a transcript-provable /goal and run it
argument-hint: [what done looks like]
---

You are running the goal-workflow pipeline. Consult the goal-condition-architect
and goal-loop-orchestrator skills as you go.

Input: $ARGUMENTS
(If the input above is empty, use the current conversation context as the input.)

Do this in order:

1. UNDERSTAND — Identify the single verifiable end state in the input: when is
   this unambiguously done? If there is no provable end state (the work is
   open-ended or subjective), stop and say so, and suggest /loop or a normal
   prompt instead of a goal. If the end state is ambiguous, ask ONE clarifying
   question and stop.

2. CRAFT — Write ONE /goal condition using the four-part anatomy: (a) one
   measurable end state; (b) a stated check naming the command AND requiring its
   output be shown; (c) the constraints that matter, including "fix the
   implementation, not the tests" and "no mocks or stubbed returns" whenever the
   task could be cheated; (d) a turn or time bound matched to the work size.
   Every success criterion must have a "show / print the output" step, because
   the evaluator reads only the transcript and runs no tools. Keep it under
   4,000 characters; distill docs, don't paste them.

3. CONFIRM — Show me the exact /goal command in a fenced block and the bound you
   chose with a one-line rationale. Unless I've said to go straight through,
   wait for my go-ahead before handing it over (whoever runs /goal starts a turn
   immediately).

4. HAND OFF — Check preconditions (workspace trust accepted; hooks not
   disabled via managed policy). Confirm whether the run should be unattended
   (auto mode). Then give me the trigger to start the loop — you cannot start it
   yourself, because this command only expands into a prompt and /goal is parsed
   from my input. Present either: the exact `/goal <condition>` line for me to
   paste in this session, or the `claude -p "/goal <condition>"` wrapper for a
   headless kickoff. State which you recommend and why.

5. MONITOR (once I've started it) — As the loop runs, enforce evidence
   surfacing: every turn that claims progress must print the real command output
   (test summary, exit status, file counts, empty queue, clean git status) —
   never a mock, stub, skipped test, or fabricated result. If the loop stalls
   (the evaluator's reason repeats, the same error recurs, turns climb with no
   movement, or it tries to fake the proof), stop, diagnose root cause, and
   either fix the blocker or tell me to clear and re-set a corrected condition —
   do not wait for the bound. On completion, report the achieved-status summary
   (duration, turns, token spend).
```

## Notes

- `argument-hint` is what Claude Code shows as autocomplete help for the command.
- The command leans on the two underlying skills, so keep them installed alongside it; the command is the trigger, the skills carry the depth.
- Mechanic to keep straight: `/goalify` (like any custom command) expands into a prompt and **crafts** the `/goal` line — it does not start the loop. The loop starts only when `/goal <condition>` is entered as input.
- Headless usage is therefore two-step: run `/goalify <task>` interactively (or have it craft the condition), then kick off the loop unattended with `claude -p "/goal <condition>"`, which runs to completion in one invocation (Ctrl+C to interrupt). Running `claude -p "/goalify <task>"` only produces the condition; it won't run the goal because there is no interactive paste step in headless mode.
