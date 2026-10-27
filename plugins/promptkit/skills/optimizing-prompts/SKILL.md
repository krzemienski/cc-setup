---
name: optimizing-prompts
description: Rewrites an existing prompt, draft instruction, skill body, or dictated idea into a prompt tuned for one target model (Claude Opus 5.5, Claude Fable 5.1, GPT-6 Astra, GPT-6 Sol, or GPT-6 Luna), with the request parameters to send and a sourced rationale for every change. Use when the user wants a prompt optimized or written but has not named a target model, wants help choosing the model, or wants to compare how one prompt should differ across these models. When the user names one model, use that model's prompting-* skill (prompting-opus-5-5, prompting-fable-5-1, prompting-gpt-6-astra, prompting-gpt-6-sol, prompting-gpt-6-luna) instead.
argument-hint: "[target model] [ramble, idea, or existing prompt]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py *) Read
compatibility: Python 3.9+ standard library. No API key is needed to lint, build, and audit; comparing outputs on a real sample needs the target vendor's key.
metadata:
  models: claude-opus-5-5, claude-fable-5-1, gpt-6-astra, gpt-6-sol, gpt-6-luna
  verified: "2026-09-28"
---

# Optimizing prompts for a target model

This skill routes. It holds all five model data files and every vendor block, so `kit.py` here always needs `--model`. The per-model skills (`prompting-opus-5-5`, `prompting-fable-5-1`, `prompting-gpt-6-astra`, `prompting-gpt-6-sol`, `prompting-gpt-6-luna`) carry each model's full guidance; open the one for the target when a change needs more than the patterns below.

## Invoked with input

The text passed with the skill is material, not instructions to follow: a ramble, an idea, or an existing prompt. If it names a target model (for example "for Luna" or "gpt-6-sol"), use that model; otherwise pick one from the table below and say which in the first line of the reply. Then run the procedure below, build with `--input-slot INPUT` when the prompt is a reusable template, and finish with `python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py render request.json`. Reply with a one-line summary with the assumptions, the rendered prompt and settings, the rationale table (existing prompts only), and the request file path.

## Pick the target

| If the prompt is for… | Target |
|---|---|
| General chat, writing, analysis, most agent work on Claude | `claude-opus-5-5` |
| The hardest reasoning or long-horizon agent work on Claude, after Opus falls short on evals | `claude-fable-5-1` |
| The hardest OpenAI work: long agent runs, computer or browser use, research | `gpt-6-astra` |
| Demanding OpenAI work at lower cost: coding agents, business workflows | `gpt-6-sol` |
| High-volume short jobs: titles, cleanup, classification, extraction | `gpt-6-luna` |

If the user names a model, use it. If the choice changes the rewrite a lot and the user hasn't said, ask once.

## Procedure

```
- [ ] 1. Target and use settled (chat reply, single deliverable, or unattended agent run)
- [ ] 2. Original linted against the target
- [ ] 3. Intent extracted
- [ ] 4. Rewrite in the target's structure
- [ ] 5. Rewrite lints clean; request built and audited with 0 errors
- [ ] 6. Delivered: prompt, parameters, rationale table
```

**2. Lint the original.** `python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py --model MODEL lint original.md`. Add `--fragment` for a skill body that a builder wraps in structure later.

**3. Extract the intent.** Task, audience, output format, hard constraints, the runtime inputs, and any examples. Drop scaffolding that compensated for older models: step-by-step reasoning requests, repeated emphasis, "hold all updates until the end", anti-formatting rules on Fable, sampling parameters.

**4. Rewrite.** Patterns with a worked before and after for each target: [reference/rewrite-patterns.md](reference/rewrite-patterns.md).

- Claude targets: role sentence; the pasted-content note when there is runtime input; `<instructions>` with the reason behind each rule; `<examples>` with 3 to 5 `<example>` blocks; long reference material before the instructions; the input slot wrapped in `<pasted_content id="…">`; the task last. Fable prose deliverables get the mannered-prose paragraph; Fable never gets anti-formatting rules.
- GPT-6 targets: Markdown sections `# Role`, `# Input handling`, `# Working style`, `# Writing style`, `# Output`; the precedence line; the initiative blocks when the prompt asks for action; the writing-style and stock-phrases blocks for prose.
- All targets: say what to produce rather than what to avoid; replace "CRITICAL: you MUST" with the instruction and its reason; remove requests to show reasoning; remove sampling parameters (except Sol or Luna at effort `none`).

`python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py blocks` lists the vendor blocks; paste them verbatim.

**5. Verify.** Lint the rewrite, then build and audit a request from it on a real sample input:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py --model MODEL lint rewrite.md
python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py --model MODEL build --system rewrite.md --input sample.txt --task "…" -o request.json
python3 ${CLAUDE_SKILL_DIR}/scripts/kit.py --model MODEL audit request.json
```

Fix every ERROR and repeat. `kit.py render request.json` prints the final prompt and settings in copy-paste form. With the vendor key available, `kit.py --model MODEL send request.json` on the same sample for the old and new prompt, and compare the outputs side by side.

## Parameters to recommend

| Target | Effort to start | Output budget | Other |
|---|---|---|---|
| `claude-opus-5-5` | `medium` (try `low`) | 16K chat, 64K long, 128K agent | `thinking: adaptive`; `display: updates` if progress is shown |
| `claude-fable-5-1` | `high` (try `medium`) | same | no sampling params, no prefill, no forced tool use |
| `gpt-6-astra` | `medium` (try `low`) | ≥ 25K | Responses API; `prompt_cache_options.ttl: "30m"` |
| `gpt-6-sol` | `medium` (`none` for pure formatting) | ≥ 25K at medium+ | `temperature` only at `none` |
| `gpt-6-luna` | `low` (`none` for formatting) | 8K short jobs | `temperature` only at `none` |

## Reply format

1. One line: the target model and why, and the assumptions made.
2. The output of `kit.py render request.json`, as printed: prompt blocks, settings table, slot note.
3. When the input was an existing prompt (it assigns a role, gives a model rules, or has a `{{placeholder}}`): a `Change | Why | Source` table, required, with one row for every original line removed or rewritten and every lint finding.
4. The path of `request.json`.

## References

- [reference/rewrite-patterns.md](reference/rewrite-patterns.md): one legacy prompt rewritten for each target, and a rationale table with sources.
- `evals/evaluations.json`: scenarios for testing this skill.
