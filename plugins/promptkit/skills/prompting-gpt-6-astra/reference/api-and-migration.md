# GPT-6 API rules and migration (Responses API)

Sources, retrieved 2026-09-28:
- Using GPT-6: https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md
- Reasoning models: https://developers.openai.com/api/docs/guides/reasoning
- Model pages: https://developers.openai.com/api/docs/models/gpt-6-astra, …/gpt-6-sol, …/gpt-6-luna
- Introducing GPT-6 Sol and Luna: https://openai.com/index/introducing-gpt-6-sol-and-luna/

## Contents

1. The family at a glance
2. Request shape
3. Parameter rules
4. Reasoning across tool calls
5. Mid-conversation configuration
6. Caching and cost
7. Reading the response
8. Migration checklist

## 1. The family at a glance

| | Astra | Sol | Luna |
|---|---|---|---|
| Model string | `gpt-6-astra` | `gpt-6-sol` | `gpt-6-luna` |
| Use for | Highest capability: long agentic work, computer and browser use, research | Demanding professional work at a fifth of Astra's price | High-volume everyday tasks: titles, cleanup, classification, extraction |
| Effort | `low`…`max` (no `none`) | `none`…`max` | `none`…`max` |
| Default effort | `medium` | `medium` | `medium` (this skill starts at `low`) |
| Input / cached / cache write / output per MTok | $10 / $1 / $12.50 / $50 | $2 / $0.20 / $2.50 / $10 | $0.10 / $0.01 / $0.125 / $0.50 |
| Knowledge cutoff | 2026-04-30 | 2026-04-20 | 2026-05-18 |
| Context, max output | 1.05M, 128K | 1.05M, 128K | 1.05M, 128K |

All three: requests over 272K input tokens are billed at 2x input and 1.5x output.

## 2. Request shape

```json
POST https://api.openai.com/v1/responses
{
  "model": "gpt-6-sol",
  "instructions": "# Role\n…",
  "input": [{"role": "user", "content": "## Task\n…"}],
  "reasoning": {"effort": "medium", "summary": "auto"},
  "text": {"verbosity": "medium", "format": {"type": "json_schema", "name": "out", "schema": {}, "strict": true}},
  "max_output_tokens": 25000,
  "prompt_cache_options": {"ttl": "30m"}
}
```

Header: `Authorization: Bearer $OPENAI_API_KEY`.

## 3. Parameter rules

| Rule | Detail |
|---|---|
| Sampling parameters | `temperature`, `top_p`, `top_logprobs` are accepted only at effort `none` (Sol, Luna). Otherwise remove them, and remove `message.output_text.logprobs` from `include` (Chat Completions: also `logprobs`). |
| `minimal` | Not an effort for GPT-6. Start at `low`. |
| Astra and `none` | Astra has no `none`. |
| Chat Completions tools | Astra: tool calling requires Responses. Sol, Luna: Chat Completions function calling only at `reasoning_effort: "none"`. |
| Effort name | Responses uses `reasoning.effort`; `reasoning_effort` is the Chat Completions name. |
| Caching | `prompt_cache_retention` is replaced by `prompt_cache_options.ttl: "30m"`. |
| Output budget | Reserve at least 25,000 tokens at medium and above when starting out. |
| Structured output | `text.format` with `type: "json_schema"` and `strict: true`. |

`kit.py audit` checks each of these.

## 4. Reasoning across tool calls

Two ways to keep the model's reasoning between tool calls:

- Stored responses: send `previous_response_id` and only the new items (`function_call_output`).
- Stateless: `store: false` and `include: ["reasoning.encrypted_content"]`, then pass back every output item (reasoning, `function_call`, `function_call_output`) untouched. OpenAI: pass all items between the last user message and your function call output into the next request unchanged.

A function call arrives as `{"type": "function_call", "call_id": "…", "name": "…", "arguments": "<JSON string>"}`; answer with `{"type": "function_call_output", "call_id": "…", "output": "<string>"}`.

## 5. Mid-conversation configuration

Change effort mid-conversation with `configuration_update` input items; keep `reasoning.effort` at request level as the baseline. When replaying history, keep each update at its original position, never put two updates back to back, and never end a request with one. Other GPT-6 features: async tool calling (`async: true` on a tool), mid-turn steering (WebSocket), and asynchronous misalignment-monitoring alerts.

## 6. Caching and cost

Stable text first, in `instructions`; set `prompt_cache_options.ttl: "30m"`; watch `usage.input_tokens_details.cached_tokens`. `kit.py send` and the agent loop compute cost per request, including the 272K surcharge.

## 7. Reading the response

- `output_text` (convenience) or `output[]` items of type `message` with `output_text` content.
- `reasoning` items carry `summary[]` when `reasoning.summary` is set.
- `status: "incomplete"` with `incomplete_details.reason: "max_output_tokens"` means the budget ran out, possibly during reasoning before any visible text. Raise `max_output_tokens` or lower effort.
- A `refusal` content item in a message means the model declined.

## 8. Migration checklist

```
- [ ] Responses API (/v1/responses) for anything with tools on Astra
- [ ] model string set; effort chosen from the model's list and set explicitly
- [ ] minimal replaced with low
- [ ] temperature/top_p/top_logprobs removed unless effort is none (Sol, Luna)
- [ ] prompt_cache_retention replaced with prompt_cache_options.ttl "30m"
- [ ] max_output_tokens ≥ 25,000 at medium and above
- [ ] json_schema outputs use strict: true
- [ ] instruction-precedence line added; skills and AGENTS.md audited for conflicts
- [ ] prompts that ask for written-out reasoning replaced with reasoning.summary "auto"
- [ ] reasoning carried across tool calls (previous_response_id or encrypted_content)
- [ ] kit.py audit: 0 errors
```

OpenAI's Codex repository also offers a migration helper: `$openai-docs migrate this project to the GPT-6 model family`.
