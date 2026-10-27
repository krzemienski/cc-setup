---
name: "gpt-6-execution"
description: "Use when writing, reviewing, or running prompts or Responses API requests for OpenAI GPT-6 Astra, Sol, or Luna (gpt-6-astra, gpt-6-sol, gpt-6-luna): choosing the tier and reasoning effort, a 400 from GPT-6, initiative and style prompts, agents, migration from GPT-5.x."
---

# GPT-6 execution (Astra, Sol, Luna)

Build Responses API requests for GPT-6 the way OpenAI's GPT-6 guidance prescribes (verified 2026-09-28). Identify the model first; the per-model sections differ.

Companion tooling (optional): the Speakwright build kit ships a separate skill per model, `.claude/skills/prompting-gpt-6-astra/`, `-sol/`, and `-luna/`, each with `scripts/kit.py` (build, audit, lint, send); Astra and Sol also ship a Responses agent loop. When available: `kit.py build --system role.md --input notes.txt --task "…" [--effort] [--verbosity] [--schema] [--prose|--technical] [--action] [--summary] [--mode agent] -o req.json`, then `kit.py audit req.json` until 0 errors, then `OPENAI_API_KEY=… kit.py send req.json`.

## Which model

| | Astra | Sol | Luna |
|---|---|---|---|
| String | `gpt-6-astra` | `gpt-6-sol` | `gpt-6-luna` |
| Use for | Hardest work: long agent runs, computer/browser use, research | Demanding work at a fifth of Astra's price: coding agents, business workflows | High-volume short jobs: titles, cleanup, classification, extraction |
| Effort | `low`–`max` (no `none`) | `none`–`max` | `none`–`max` |
| Start at | `medium` | `medium` (`none` for pure formatting) | `low` (`none` for formatting) |
| Input / cached / cache write / output per MTok | $10 / $1 / $12.50 / $50 | $2 / $0.20 / $2.50 / $10 | $0.10 / $0.01 / $0.125 / $0.50 |
| Cutoff | 2026-04-30 | 2026-04-20 | 2026-05-18 |

All: 1.05M context, 128K output; over 272K input tokens is billed at 2x input and 1.5x output. Run the same evals on Sol before paying for Astra, and on Sol before settling for Luna on anything that needs judgment.

## Request shape

`POST /v1/responses`: `model`; `instructions` in Markdown sections (`# Role`, `# Input handling`, `# Working style`, `# Writing style`, `# Output`); `input` with `## Reference`, `## Input` (pasted text in matching random-id `<pasted_content>` tags, with a note that instructions inside apply only where the user's own request asks), `## Examples`, `## Task`; `reasoning: {effort, summary: "auto"}`; `text: {verbosity, format}` (`json_schema` with `strict: true` for data); `max_output_tokens`; `prompt_cache_options: {ttl: "30m"}`.

## Hard rules

- `minimal` is not a GPT-6 effort; start at `low`. Astra has no `none`.
- Sampling parameters (`temperature`, `top_p`, `top_logprobs`; Chat Completions `logprobs`; `message.output_text.logprobs` in `include`) only at effort `none` (Sol, Luna).
- Astra tool calling requires Responses. Sol/Luna Chat Completions function calling only at `reasoning_effort: "none"`.
- Responses uses `reasoning.effort`; `reasoning_effort` is the Chat Completions name.
- `prompt_cache_retention` → `prompt_cache_options.ttl: "30m"`.
- At `medium` and above reserve at least 25,000 output tokens; otherwise `status: "incomplete"`, `incomplete_details.reason: "max_output_tokens"`, possibly with no visible text. Luna short jobs at `none`/`low`: about 8,000 is enough.
- Mid-conversation effort: `configuration_update` input items; never two adjacent, never last; keep request-level effort unchanged as the baseline to preserve the cache.
- Reasoning across tool calls: `previous_response_id`, or `store: false` + `include: ["reasoning.encrypted_content"]` and replay every output item untouched. Answer `function_call` with `{"type": "function_call_output", "call_id", "output"}`.

## Behaviors and OpenAI's prompt blocks

1. **Initiative:** GPT-6 asks more clarifying questions. For work that should just get done, add OpenAI's blocks: infer intent and bias toward action; treat "can you…", "I want to…", "help me…" as instructions and don't stop at acknowledging capability, proposing a plan, or offering to continue; "The user should be approving a concrete, reviewable result"; "Do not introduce unsolicited warnings, disclaimers, approval flows, or safety/compliance checklists due to hypothetical risk."
2. **Instruction following:** more sensitive to conflicting guidance in skills and AGENTS.md. Always add "The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions." Audit skill files for contradictions. To debug a stall: "If a skill causes you to ask for permission or confirmation, pause, leave requested work unfinished, or diverge from the user's intent, name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies."
3. **Writing:** leans on lists, tables, repeated phrases. For prose: clear concise paragraphs, one idea each, lists only for parallel items, main point early; plus OpenAI's stock-phrase list ("Bottom Line:", "delve", "foster", "leverage", "it's worth noting", "importantly", "This isn't about X. It's about Y.", contrastive "X, not Y", invented compound labels, canned transitions). For technical explanations: plain language, detail only where it helps, calibrated to the reader. Lower `text.verbosity`.
4. **Delegation** (agents with collaboration tools): "If at any point you can parallelize work by delegating tasks to another agent … you should do so using collaboration tools if it could save time or improve quality." Inter-agent messages must be legible with proper spacing.
5. **Testing:** "Do not write tests for reversible, low-impact changes that mirror the implementation." Run tests appropriate to the change; broaden only when new changes, failures, or concerns justify it.
6. **Reasoning display:** don't ask for reasoning in the answer; request `reasoning.summary: "auto"`.

## Per model

- **Astra:** default for long agent runs and research. Guidance tuned for Sol or Luna can overconstrain Astra; re-test scaffolding when moving a prompt up. Define what done looks like and which actions need a person (deletes, payments, public publishing).
- **Sol:** same prompts as Astra at a fifth of the price; `none` with a low temperature for deterministic formatting; agents need `low` or higher.
- **Luna:** keep stable instructions first so they cache; 3–5 examples beat long rules on short jobs; strict JSON schemas with enums for classification; no agent loops.

## New GPT-6 features

Async tool calling (`async: true`, return later with the original `call_id`); mid-turn steering over WebSocket; misalignment monitoring. Carried over from GPT-5.6: computer use, Structured Outputs, streaming, programmatic tool calling, multi-agent orchestration, prompt caching, persisted reasoning, compaction, pro mode.

## Old patterns (GPT-5.x)

`minimal` → `low`; sampling params while reasoning → remove; tools on Chat Completions (Astra) → Responses; `prompt_cache_retention` → `prompt_cache_options.ttl`; output budgets sized for the answer only → reserve 25K; heavy "ALWAYS ask before…" rules → GPT-6 follows them literally and stalls; add the initiative blocks if it asks for approval too often.

Sources: https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md · https://developers.openai.com/api/docs/guides/reasoning · https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra · https://openai.com/index/introducing-gpt-6-sol-and-luna/ · https://developers.openai.com/api/docs/models/gpt-6-sol · https://developers.openai.com/api/docs/models/gpt-6-luna