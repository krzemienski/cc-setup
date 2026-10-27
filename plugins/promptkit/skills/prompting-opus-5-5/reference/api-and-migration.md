# Opus 5.5 API rules and migration

Sources, retrieved 2026-09-28:
- What's new in Claude Opus 5.5: https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5
- Structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Effort: https://platform.claude.com/docs/en/build-with-claude/effort

## Contents

1. Request shape
2. Errors (400) and how to fix them
3. Beta headers
4. Thinking blocks and the conversation
5. Refusals
6. Caching
7. Migration checklist from Opus 5

## 1. Request shape

```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 16000,
  "system": [{"type": "text", "text": "…", "cache_control": {"type": "ephemeral"}}],
  "messages": [{"role": "user", "content": "…"}],
  "thinking": {"type": "adaptive", "display": "summarized"},
  "output_config": {"effort": "medium", "format": {"type": "json_schema", "schema": {}}}
}
```

Headers: `x-api-key`, `anthropic-version: 2023-06-01`, `content-type: application/json`, and `anthropic-beta` only for the beta features used.

`thinking.display`: `omitted` (default; thinking blocks come back with an empty `thinking` field), `summarized`, or `updates` (beta; text the model writes between tool calls arrives as readable thinking blocks).

## 2. Errors (400) and how to fix them

| Sent | Fix |
|---|---|
| `thinking.type` `disabled` or `enabled`, or `budget_tokens` | Send `{"type": "adaptive"}` or omit `thinking`; lower `output_config.effort` to think less. |
| `tool_choice` `any` or `tool` | Keep `auto` (or `none`). Set `strict: true` on the tool and state when to use it; for JSON output use `output_config.format`. |
| Last message has role `assistant` (prefill) | Put continuation text in a user message ("Your previous response ended with …; continue from there.") or use a schema. |
| `computer_20251124` tool on the Claude API | Use `computer_toolset_20260801`. |
| Replayed thinking block after the prefix changed (accounts created on or after 2026-08-31) | Keep history append-only, or set `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` with the `thinking-binding-controls-2026-08-01` beta. |
| Beta feature without its header | Add the header from section 3. |

Sampling parameters (`temperature`, `top_p`, `top_k`): Anthropic's Opus 5.5 pages retrieved for this skill do not state the rule for Opus 5.5 directly; the Fable 5.1 page documents that non-default values return 400 with always-on thinking. The audit warns; remove them.

## 3. Beta headers

| Feature | Header value |
|---|---|
| `thinking.display: "updates"` | `thinking-display-updates-2026-08-18` |
| Turn-scoped system messages (`clear_at: "next_user_message"`) | `mid-conversation-system-clear-at-2026-08-21` |
| Per-message effort (system message with `output_config.effort`) | `mid-conversation-output-config-2026-07-01` |
| `thinking.block_binding` | `thinking-binding-controls-2026-08-01` |

Several values go in one comma-separated `anthropic-beta` header.

A turn-scoped system message:

```json
{"role": "system", "content": "The user hasn't heard from you in a while — say in a few words what you're doing, then continue.", "clear_at": "next_user_message"}
```

A per-message effort change (empty content):

```json
{"role": "system", "content": "", "output_config": {"effort": "high"}}
```

## 4. Thinking blocks and the conversation

Thinking blocks are bound to the model and to the conversation prefix. Replay assistant turns exactly as returned, including thinking blocks, and only append. Editing the system prompt, tools, or an earlier message mid-run invalidates the thinking blocks after the change. So anything that must be in the system prompt for an agent run (the standing instruction about how turns end) goes in from the first request. Opus 5.5 reads thinking blocks from Opus 5 and earlier Opus, Sonnet, and Haiku models; Fable 5.1 and Mythos 5.1 read Opus 5.5's blocks.

## 5. Refusals

Safeguard classifiers cover biology, cybersecurity, and `reasoning_extraction` (requests to reproduce the model's reasoning). A decline returns HTTP 200 with `stop_reason: "refusal"` and `stop_details` naming the category. `kit.py send` exits 3 on a refusal. Server-side fallback (`fallbacks: "default"`, beta) retries on another model, except for `reasoning_extraction`. To avoid `reasoning_extraction` declines, ask for the conclusion and its justification, and read summarized thinking if you need the reasoning.

## 6. Caching

Put stable text first (system prompt, tools, documents) and mark the end of the stable part with `cache_control`. Minimum cacheable prompt: 512 tokens. Cache read $0.20 per MTok against $4 input. Changing top-level effort between requests invalidates the cache; use per-message effort instead.

## 7. Migration checklist from Opus 5

```
- [ ] model: claude-opus-5-5
- [ ] thinking: adaptive (delete disabled/enabled and budget_tokens)
- [ ] output_config.effort set explicitly; sweep low and medium on your evals
- [ ] max_tokens leaves room for thinking (16K chat, 64K long, 128K agent)
- [ ] forced tool_choice replaced with auto + strict tool + prompt text
- [ ] assistant prefill removed
- [ ] temperature, top_p, top_k removed
- [ ] instructions to write reasoning into the reply removed
- [ ] output_format moved to output_config.format
- [ ] computer_20251124 replaced with computer_toolset_20260801 (Claude API)
- [ ] thinking.display set if a UI shows text between tool calls
- [ ] responses read by block type, not content[0]
- [ ] kit.py audit: 0 errors
```
