# Running GPT-6 as an agent

Sources, retrieved 2026-09-28: Using GPT-6 (https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md), Reasoning models (https://developers.openai.com/api/docs/guides/reasoning), Rethinking skills and prompts for GPT-6 Astra (https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

## Contents

1. Instructions for an agent run
2. Keeping reasoning across tool calls
3. Ending the run: done, blocked, or reporting
4. Decision boundaries
5. What scripts/agent_loop.py does
6. Reading the run summary

## 1. Instructions for an agent run

`# Role`, then `# Working style` with `gpt6-initiative`, `gpt6-act-on-requests`, `gpt6-reviewable-result`, `gpt6-instruction-precedence`, `gpt6-skill-debug`, `gpt6-testing` (and `gpt6-delegation` only when the agent has collaboration tools), then `# Writing style` with `gpt6-technical-communication`. Define what done looks like in the task itself: which checks must pass and what the final message must contain.

## 2. Keeping reasoning across tool calls

Use `previous_response_id` with stored responses, or `store: false` with `include: ["reasoning.encrypted_content"]` and a full, untouched replay of output items. Don't drop or reorder reasoning items between the last user message and a function call output. Request `reasoning.summary: "auto"` and show summaries as progress lines.

## 3. Ending the run: done, blocked, or reporting

A turn that ends without function calls is a report. If the checklist still has open items and no blocker is stated, reply with a user message naming them (`continuation-open-items`); stop after two or three automatic continuations. `status: "incomplete"` with `max_output_tokens` means the budget ran out; raise it (reserve at least 25,000 at medium and above) rather than continuing blindly.

## 4. Decision boundaries

Say which actions the agent may take on its own and which need a person: deletions, payments, publishing, force pushes. OpenAI's skills guidance recommends stating this explicitly instead of hoping the model infers it. The loop enforces the destructive part in code as well.

## 5. What scripts/agent_loop.py does

- `POST /v1/responses` with function tools `list_dir`, `read_file`, `write_file`, `edit_file`, `run_command`, `todo` (`strict: true`), confined to `--cwd`.
- `reasoning: {"effort": <start>, "summary": "auto"}`, `max_output_tokens` from the model's agent default, `prompt_cache_options.ttl: "30m"`.
- Default mode `previous_response_id`; `--stateless` switches to `store: false` + encrypted reasoning with full replay, verified append-only each turn.
- Arguments arrive as a JSON string; invalid JSON is returned to the model as a tool error.
- Continuations on open todo items (default at most 2), then `waiting-for-user`.
- Stops on `status: "incomplete"` or a refusal content item and records why.
- `run_command` refuses deletes, force pushes, hard resets, `git clean -f`, dropped tables, `--no-verify`, and similar unless `--allow-destructive`.
- Refuses effort `none` for agent runs (reasoning off).
- `--dry-run` writes and audits the first request without calling the API; every request is logged with the key replaced by `${OPENAI_API_KEY}`.

## 6. Reading the run summary

`agent-logs/summary.json`: `status` (`done`, `waiting-for-user`, `refused`, `incomplete: <reason>`, `max_turns`, `http_NNN`), `mode`, `turns`, `tool_calls`, `continuations`, `prefix_edits` (stateless mode; must be 0), token counts including cached and reasoning tokens, `cost_usd` summed per request, `open_items`.
