# Running Fable 5.1 as an agent

Source: Prompting Claude Fable 5.1, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1, retrieved 2026-09-28.

## Contents

1. System prompt for an unattended run
2. Progress the user can see
3. Tool-call batching
4. Continuations on open items
5. Subagents
6. What scripts/agent_loop.py does
7. Reading the run summary

## 1. System prompt for an unattended run

In this order: the role; project or skill rules; optionally `progress-updates-request`; then `fable-operating-autonomously` and `fable-delivering-work` last. They go in from the first request, because changing the system prompt mid-run invalidates earlier thinking blocks. Add `fable-targeted-edits` and `fable-scope-and-tests` for coding agents. `kit.py build --mode agent --progress` produces this prompt.

The autonomy text keeps the need for confirmation on destructive actions ("Stop only for destructive actions or genuine scope changes the user must decide"). Keep a guard in the harness as well.

## 2. Progress the user can see

Set `thinking.display: "updates"` with its beta header and render non-empty thinking blocks as status lines. Fable 5.1 writes fewer updates than Fable 5, most noticeably at high effort in long tool chains. When several consecutive steps produce nothing readable, send `silent-stretch-reminder` as a turn-scoped system message, at most two or three times per run.

## 3. Tool-call batching

In coding and computer-use loops Fable 5.1 may issue one implied call per turn. After each round of tool results, add `batch-tool-calls-nudge` at the end of the request; a turn-scoped system message keeps it out of the cached prefix.

## 4. Continuations on open items

A text-only end of turn is a report. If the checklist still has open items and no blocker is stated, reply with `continuation-open-items` naming them; stop after two or three automatic continuations and hand back to the user.

## 5. Subagents

Let the lead keep working: the tool that starts a subagent returns at once, each result comes back in a later user message, and a separate tool lets the lead wait when it chooses. Run subagents at lower effort where evals show quality holds. If it delegates trivial work, add `subagent-damping`.

## 6. What scripts/agent_loop.py does

- Tools `list_dir`, `read_file`, `write_file`, `edit_file`, `run_command`, `todo`, all `strict: true`, confined to `--cwd`.
- `thinking: {"type": "adaptive", "display": "updates"}`; effort defaults to `high`; `max_tokens` 128,000.
- After each round of tool results: the batching nudge, plus the silent-stretch reminder when due, in one turn-scoped system message.
- Append-only history, verified before each request (`prefix_edits` in the summary).
- Up to `--max-continuations` (default 2) continuation messages when a turn ends with open todo items, then `waiting-for-user`.
- On `stop_reason: "refusal"` the run stops with `status: "refused"`, `stop_details`, and the permitted fallback targets in the summary.
- `run_command` refuses deletes, force pushes, hard resets, `git clean -f`, dropped tables, `--no-verify`, and similar unless `--allow-destructive`.
- `--budget-seconds N` appends `elapsed Ns / Ns` to each message sent back.
- `--dry-run` writes and audits the first request without calling the API.

## 7. Reading the run summary

`agent-logs/summary.json`: `status` (`done`, `waiting-for-user`, `refused`, `max_tokens`, `max_turns`, `http_NNN`), `turns`, `tool_calls`, `continuations`, `reminders`, `prefix_edits` (must be 0), token counts including cache reads and writes, `cost_usd`, `open_items`, and on refusal `stop_details` and `fallback_targets`.
