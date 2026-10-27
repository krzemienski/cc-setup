# GPT-6 prompting guidance (Astra, Sol, Luna)

Sources, retrieved 2026-09-28:
- Using GPT-6 (model guidance, prompting best practices, migration): https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md
- Rethinking skills and prompts for GPT-6 Astra: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- Reasoning models: https://developers.openai.com/api/docs/guides/reasoning

Each quoted block ships verbatim in `assets/blocks/<name>.txt`; add one with `kit.py build --add-block <name>`. OpenAI wrote the behavior notes about Astra; they are the family's reference behaviors, and the blog warns that guidance which helps Sol or Luna may overconstrain Astra, so test each block on the model you ship.

## Contents

1. Prompt structure
2. Initiative and follow-through
3. Instruction following and precedence
4. Writing style
5. Delegation
6. Testing and verification
7. Skills and AGENTS.md files
8. Pasted input
9. Reasoning effort and verbosity

## 1. Prompt structure

`kit.py build` writes `instructions` as Markdown sections and the user turn as labeled sections:

```
# Role
# Input handling      (when there is pasted input)
# Working style       (precedence line; initiative blocks for action tasks)
# Writing style       (prose or technical blocks, when asked)
# Output              (when a schema is used)
---- user input ----
## Reference: <file>  (documents)
## Input (pasted by the user; …)  <pasted_content id="…">…</pasted_content id="…">
## Examples / ### Example n
## Task
```

Put stable text in `instructions` so `prompt_cache_options.ttl: "30m"` keeps it cached.

## 2. Initiative and follow-through

GPT-6 asks a question more readily when input could change the result, which can stop work where the user expected a reasonable assumption, and it asks non-blocking questions while working by default. For tasks that should end in a finished result, add the three blocks (`--action`, or automatically in agent mode):

- `gpt6-initiative`
- `gpt6-act-on-requests`
- `gpt6-reviewable-result`

Tune to the autonomy your product wants; a pair-programming product may prefer the questions.

## 3. Instruction following and precedence

GPT-6 follows longer instructions more closely and is more sensitive to context. Unclear or conflicting guidance in a skill file or AGENTS.md can make it pause and block work early. Add the precedence line (`gpt6-instruction-precedence`, always added by the builder):

> The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions.

To find which instruction caused a pause, add `gpt6-skill-debug`, which asks the model to name and quote it.

## 4. Writing style

GPT-6 tends toward detailed, formatted answers and recurring phrases.

- Prose for people: `gpt6-writing-style` and `gpt6-stock-phrases` (`--prose`).
- Technical explanations: `gpt6-technical-communication` (`--technical`), which asks for plain language, technical detail only where it helps, and writing calibrated to the reader's background.
- Length: `text.verbosity` `low`, `medium`, `high` (`--verbosity`).

## 5. Delegation

GPT-6 may delegate less than you want when it has collaboration tools. `gpt6-delegation` encourages parallel delegation and asks that messages between agents stay legible. The agent loop in this skill has no collaboration tools, so it leaves this block out.

## 6. Testing and verification

GPT-6 tests thoroughly, sometimes more broadly than a small task needs. `gpt6-testing` scales verification to the task.

## 7. Skills and AGENTS.md files

From "Rethinking skills and prompts": give skills specific triggers so they load only when relevant; keep AGENTS.md current and drop blanket rules such as "read everything before every edit"; separate routine judgment from actions that need a person (deletes, payments, public publishing); define what done looks like. Audit every skill and AGENTS.md the model can read for contradictions before blaming the model.

## 8. Pasted input

OpenAI's guide has no pasted-content note of its own. This skill ships an adaptation of Anthropic's pattern (`gpt6-pasted-content-note`): input wrapped in `<pasted_content>` tags with a random id, and a note in `# Input handling` saying the text may contain instructions the user did not write. It is a guardrail, not a security boundary.

## 9. Reasoning effort and verbosity

- Treat effort as a tuning control, not the main way to recover quality; fix the prompt first.
- Requests that used `minimal` on earlier models start at `low`.
- Reserve at least 25,000 output tokens for reasoning plus answer when starting out at medium or above.
- Ask for `reasoning.summary: "auto"` (`--summary`) to see progress; don't ask the model to write its reasoning in the answer.
