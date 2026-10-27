# northstar

Turn any prompt, document, bug report, or backlog into a rigorous Claude Code
`/goal` completion condition — then run it to completion.

## Overview

Claude Code's `/goal` command sets a completion condition and keeps Claude
working across turns until a separate fast model confirms the condition is met.
The hard part is not running a goal — it is **writing a condition** that the
evaluator can judge correctly and that Claude can actually finish.

`northstar` is the plugin for that. It takes any input, no matter how vague, and
engineers it into a well-formed `/goal` condition: one measurable end state, a
check that forces evidence into the transcript, the constraints that must not
break, and a turn or time bound. Then it runs the goal in whichever of three
execution modes fits.

## Components

### Skills

| Skill | What it does |
|-------|--------------|
| `goal-engineering` | Transforms any input into a rigorous `/goal` condition. Knows how the evaluator works and how to write conditions it can verify. |
| `goal-orchestration` | Runs a crafted condition across the three execution modes; bounds, monitors, and recovers a run. |
| `condition-library` | Ten proven, parameterized condition templates for recurring kinds of work. |

### Commands

| Command | What it does |
|---------|--------------|
| `/goal-craft <input>` | Turns a prompt, file path, or description into a ready-to-paste `/goal` condition with an anatomy breakdown and self-review. |
| `/goal-run [mode] [input]` | Executes a goal in `handoff`, `headless`, or `self` mode. Crafts the condition first if input is given. |
| `/goal-status` | Inspects a running or stalled goal, interprets the evaluator's reason, and recommends a recovery move. |

## Execution modes

A plugin cannot type the native `/goal` command into a live session, so "run the
goal" takes three real shapes — all supported:

- **Hand-off** (default) — produces the exact `/goal` line for you to paste,
  starting the real native goal loop with its genuine separate-model evaluator.
- **Headless** — runs `claude -p "/goal ..."` as a bounded subprocess for
  unattended or scripted execution.
- **Self-orchestrate** — runs the goal loop inside the current session, using a
  worker-blind subagent as the evaluator, for environments where native `/goal`
  is unavailable.

## Setup

No configuration, credentials, or external connectors are required. Install the
plugin and the skills and commands are available immediately.

For the **hand-off** and **headless** modes, the native `/goal` command must be
available — that means a workspace whose trust dialog has been accepted, and
`disableAllHooks` not set by managed policy. Where it is unavailable, use the
**self-orchestrate** mode, which works anywhere. Headless mode additionally needs
the `claude` CLI on `PATH`.

## Usage

Typical flow — craft, then run:

```
/goal-craft make the auth tests stop being flaky
/goal-run handoff
```

Craft and run in one step:

```
/goal-run self migrate every fetchUser call to the new userClient
```

Craft from a document:

```
/goal-craft docs/checkout-spec.md
```

Check on a goal that has been running a while:

```
/goal-status
```

The skills also trigger on their own — describing the work ("turn this into a
goal", "which execution mode should I use", "the goal is stuck") will engage the
matching skill without a command.

## How a condition is built

Every condition `northstar` produces has four parts:

1. **End state** — one measurable outcome (a test result, an exit code, a count,
   an empty queue).
2. **Check** — the exact command or observation that proves it, with the output
   required to be surfaced in the transcript.
3. **Constraints** — what must not break on the way (public APIs, unrelated
   files, behavior).
4. **Bound** — a turn or time clause so a stuck goal cannot run forever.

This structure exists because the `/goal` evaluator only reads the conversation —
it never runs commands or reads files. Every condition must therefore be
provable from Claude's own surfaced output.

## License

MIT — see `LICENSE`.
