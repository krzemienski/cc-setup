# Fable 5.1 API rules and migration

Sources, retrieved 2026-09-28:
- What's new in Claude Fable 5.1: https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1
- Effort: https://platform.claude.com/docs/en/build-with-claude/effort
- Refusals and fallback: https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback

## Contents

1. Request shape
2. Errors (400) and fixes
3. Beta headers
4. Thinking blocks
5. Refusals, fallback, and billing
6. Caching and cost
7. Migration checklist

## 1. Request shape

```json
{
  "model": "claude-fable-5-1",
  "max_tokens": 16000,
  "system": [{"type": "text", "text": "…", "cache_control": {"type": "ephemeral"}}],
  "messages": [{"role": "user", "content": "…"}],
  "thinking": {"type": "adaptive", "display": "updates"},
  "output_config": {"effort": "high"}
}
```

At `high` and above set a large `max_tokens`; it is a hard limit on thinking plus reply.

## 2. Errors (400) and fixes

| Sent | Fix |
|---|---|
| Non-default `temperature`, `top_p`, or `top_k` | Remove them. Adjust behavior with effort and prompt text. |
| Assistant prefill (last message role `assistant`) | Continuation text goes in a user message; JSON goes through `output_config.format`. |
| `tool_choice` `{"type": "any"}` or `{"type": "tool", …}` (error text: `tool_choice: type "tool" and "any" are not supported for this model.`) | Keep `auto` or `none`; strict tool plus a prompt line saying when to use it. |
| `thinking` disabled, enabled, or `budget_tokens` | `{"type": "adaptive"}` or omit; control depth with effort. |
| Replayed thinking block after the prefix changed (accounts created on or after 2026-08-31) | Append-only history, or `drop_block` binding with its beta header. |

## 3. Beta headers

| Feature | Header |
|---|---|
| `thinking.display: "updates"` | `thinking-display-updates-2026-08-18` |
| Turn-scoped system messages (`clear_at: "next_user_message"`) | `mid-conversation-system-clear-at-2026-08-21` |
| Per-message effort (`{"role": "system", "content": "", "output_config": {"effort": …}}`) | `mid-conversation-output-config-2026-07-01` |
| `thinking.block_binding` | `thinking-binding-controls-2026-08-01` |

Anthropic also lists content provenance (text watermark, C2PA credentials) among Fable 5.1's new features.

## 4. Thinking blocks

Earlier models can't read Fable 5.1 thinking blocks, and editing earlier turns invalidates them. Keep one conversation per model; when retrying on a fallback model, send a history without Fable's thinking blocks.

## 5. Refusals, fallback, and billing

- A decline returns HTTP 200 with `stop_reason: "refusal"` and a `stop_details` object naming the policy area. `kit.py send` exits 3.
- Permitted fallback targets: Claude Opus 4.8 and Claude Opus 5.
- Billing: a refusal that arrives before any output is billed when it is in a category with few false positives. Before 2026-09-24 these were not billed.
- Reduce false positives with the phrasing and tool-output changes in the prompting guide, section 12.

## 6. Caching and cost

$10 input, $50 output, $0.25 cache read, $12.50 five-minute and $20 one-hour cache writes per MTok; batch half price. A cache read costs 2.5% of input, so put the stable prefix (system prompt, tools, documents) first with `cache_control`, and change effort per message rather than per request so the cache survives.

## 7. Migration checklist

```
- [ ] model: claude-fable-5-1
- [ ] temperature, top_p, top_k removed
- [ ] assistant prefill removed
- [ ] forced tool_choice replaced with auto + strict tool + prompt text
- [ ] thinking adaptive; effort set explicitly (start high) and re-swept
- [ ] max_tokens large at high and above
- [ ] anti-formatting and narration-suppressing lines removed
- [ ] thinking.display set to updates (or summarized) where users watch progress
- [ ] history append-only; fallback path strips Fable thinking blocks
- [ ] refusal handling: stop_reason refusal, stop_details, fallback to Opus 4.8 or Opus 5
- [ ] kit.py audit: 0 errors
```
