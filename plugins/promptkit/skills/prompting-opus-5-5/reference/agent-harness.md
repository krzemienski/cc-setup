# Running Opus 5.5 as an agent

Source: Prompting Claude Opus 5.5, sections on unattended runs, progress updates, and harnesses (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), retrieved 2026-09-28.

## Contents

1. The standing instruction about how turns end
2. Treating a text-only turn as a report
3. Progress the user can see
4. Append-only history
5. What scripts/agent_loop.py does
6. Reading the run summary

## 1. The standing instruction about how turns end

For unattended runs, Anthropic provides a system-prompt addition (`assets/blocks/opus-unattended-standing-instruction.txt`) that begins "A standing instruction from the user, the person you are working for. It is about how your turns end." It lists the ways a turn ends too early (asking permission to continue, offering to carry on, listing non-blocking decisions, stopping at a milestone) and says the only stops the user wants are ones where nothing can move without them. It ends: "This does not override the need for confirmation on risky or destructive actions."

Place it at the end of the system prompt from the first request (`kit.py build --mode agent` does this). Leave it out of human-in-the-loop products, where stopping to ask is correct. Expect more tool calls and output tokens with it.

## 2. Treating a text-only turn as a report

An end of turn with only text is a report, not proof the task is finished. Keep a checklist the model updates (a todo tool or file). If a turn ends with open items and no stated blocker, send a short user message naming them (`continuation-open-items`):

> Your task list still has open items: {items}. Continue with them. If one is blocked, say what is blocking it.

Stop after two or three automatic continuations and hand back to the user. If a background command or subagent is still running, wait for it and return its output as the next user message.

## 3. Progress the user can see

1. Receive progress: `thinking.display: "updates"` with the `thinking-display-updates-2026-08-18` beta. Render non-empty thinking blocks as status lines.
2. Ask for predictable progress in the system prompt (`progress-updates-request`, added by `--progress`): a line of intent before starting, brief updates, a recap that stands on its own.
3. For content the user must see verbatim mid-turn (a code snippet), declare a send-message tool from the first request.
4. When several consecutive tool steps produce nothing readable (five is a reasonable threshold), append a turn-scoped system message (`silent-stretch-reminder`), at most two or three times per run:

> The user hasn't heard from you in a while — say in a few words what you're doing, then continue.

## 4. Append-only history

Replay each assistant turn exactly as returned, thinking blocks included, and only append. Per-turn nudges go in turn-scoped system messages (`clear_at: "next_user_message"`) so the system prompt never changes mid-run. Changing effort for one turn uses a per-message effort message, not a new top-level value.

## 5. What scripts/agent_loop.py does

- Tools: `list_dir`, `read_file`, `write_file`, `edit_file`, `run_command`, `todo`, all `strict: true`, confined to `--cwd`.
- System prompt: a short role, your `--system` file, the progress request, then the standing instruction last.
- `thinking: {"type": "adaptive", "display": "updates"}`, `output_config.effort` (default `medium`), `max_tokens` 128,000.
- After each round of tool results: the silent-stretch reminder when due, as a turn-scoped system message.
- Text-only end of turn with open todo items: up to `--max-continuations` (default 2) continuation messages, then status `waiting-for-user`.
- `run_command` refuses deletes, force pushes, hard resets, `git clean -f`, dropped tables, `--no-verify`, and similar unless `--allow-destructive` is passed. The refusal tells the model to continue with independent work and report the blocker.
- `--budget-seconds N` appends `elapsed Ns / Ns` to each message sent back.
- `--dry-run` writes the first request, audits it with `kit.py`'s rules, and exits without calling the API.
- Every request is logged to `--log-dir` with the key replaced by `${ANTHROPIC_API_KEY}`.

## 6. Reading the run summary

`agent-logs/summary.json` fields: `status` (`done`, `waiting-for-user`, `refused`, `max_tokens`, `max_turns`, `http_NNN`), `turns`, `tool_calls`, `continuations`, `reminders`, `prefix_edits` (must be 0; anything else means the history was edited and thinking blocks may be rejected), token counts, `cost_usd`, and `open_items`.
