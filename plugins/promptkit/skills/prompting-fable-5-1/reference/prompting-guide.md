# Fable 5.1 prompting guidance

Source: Prompting Claude Fable 5.1, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1, retrieved 2026-09-28. Section order follows the guide. Every quoted block ships verbatim in `assets/blocks/<name>.txt`; add one with `kit.py build --add-block <name>`.

## Contents

1. Consider all effort levels
2. Ask for user-facing progress updates
3. Batch independent tool calls in agent loops
4. Keep the conversation history append-only
5. Writing density
6. Formatting in chat
7. Quoting retrieved sources
8. Finish the whole task
9. Compaction summaries
10. Keep changes and tests to what the task asks for
11. Search triggering at low effort
12. Reduce safeguard false positives
13. Prefer targeted edits over whole-file rewrites
14. Leave room for long outputs at xhigh and max
15. Let the lead agent keep working while subagents run
16. Vision: crop and zoom
17. Techniques shared by current Claude models

## 1. Consider all effort levels

Start at `high` (the default), then test `low`, `medium`, `xhigh`, `max` on your evals. Re-run the sweep even if you ran one on Fable 5; level names don't correspond to the same amount of thinking across models. Gains over Fable 5 are largest at higher settings. At `medium`, results roughly match Fable 5 at lower cost. At `low`, Fable 5.1 is often competitive with Opus and Sonnet on cost per task while scoring higher.

## 2. Ask for user-facing progress updates

Fable 5.1 writes fewer updates during long tool-calling turns than Fable 5, more so at higher effort and in longer tool chains. In order:

1. Check the client receives them: progress notes come back as thinking blocks, empty under the default `display: "omitted"`. Set `display: "updates"` (beta `thinking-display-updates-2026-08-18`) and render each non-empty thinking block as a status line, or `"summarized"`.
2. Remove prompt lines that suppress narration ("hold all findings for the final response").
3. If you want more, add (`progress-updates-request`):

> Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture.

## 3. Batch independent tool calls in agent loops

In coding and computer-use loops where the next independent calls are implied rather than requested, Fable 5.1 may issue them one per turn. Quality is unaffected, but each extra turn costs tokens, a round trip, and time. Add at the end of the current request (`batch-tool-calls-nudge`):

> First privately list what you need next; then request every item that doesn't depend on another's result in this one response.

`agent_loop.py` sends it as a turn-scoped system message after every round of tool results.

## 4. Keep the conversation history append-only

Append each assistant turn exactly as returned, thinking blocks included, and don't edit earlier turns. For accounts created on or after 2026-08-31, a thinking block replayed after its prefix (system prompt, tools, or any earlier message) changed returns 400, or is dropped with `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta `thinking-binding-controls-2026-08-01`). Adopt the pattern on every account so the same code works everywhere.

## 5. Writing density

Few stock phrases and little jargon, but prose can be denser than Fable 5's: longer sentences, fewer paragraph breaks. Add the mannered-prose paragraph (`mannered-prose`, added by `--prose`) to a user message (preferred) or the system prompt.

## 6. Formatting in chat

Fable 5.1 uses bold less and reaches for headers, lists, and quotation marks less than earlier models. Remove anti-formatting language written for earlier models, or replace it with a rule that says when formatting is appropriate (`fable-formatting-in-chat`, added in chat mode). The audit warns when a system prompt still carries an anti-formatting rule.

## 7. Quoting retrieved sources

When summarizing documents, Fable 5.1 is more likely than Fable 5 to reproduce passages without quotation marks. Add one complete correct example to the system prompt: the request, the response, and a sentence explaining why it is correct (`fable-quoting-example`, Anthropic's Harbor Bridge example).

## 8. Finish the whole task

On complex asynchronous work, Fable 5.1 sometimes describes the next step instead of doing it ("Next, I'll …") or asks permission for a step already requested ("Shall I apply this?"). Apply both system-prompt additions; if prompt length is tight, the first keeps most of the effect:

- `fable-operating-autonomously`, which begins: "You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work."
- `fable-delivering-work`, which begins: "# Delivering work / The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it."

Human-in-the-loop products (pair programming) can leave these out, since there "continue" is a normal reply.

## 9. Compaction summaries

If your client compacts long conversations itself, use Anthropic's summary instruction (`fable-compaction-summary`). It lists six things to preserve exactly (difficulties and how they were handled, options raised or set aside, decisions and constraints stated exactly, where things stand, open items, hard-to-reconstruct details) and weights the user's words over the model's own.

## 10. Keep changes and tests to what the task asks for

`fable-scope-and-tests`: report pre-existing bugs as follow-ups instead of fixing them; implement the reading of an ambiguous task the wording and code most directly support and state the assumption; keep scratch checks out of the repository; commit tests only where the task or the repository's practice calls for them, about one focused test per stated behavior; implement every requested behavior completely.

## 11. Search triggering at low effort

At `low`, Fable 5.1 answers from memory more often. Raise effort for those turns or add `fable-search-unfamiliar-names`, which tells it to search when a query centers on a name it does not confidently recognize or one from a fast-moving field, using the name as the user wrote it in at least one query.

## 12. Reduce safeguard false positives

False positives are rarer than at Fable 5's launch, and finding vulnerabilities in source code is permitted. Three situations raise them:

- Compile-check phrasing. Ask "Are there any bugs in this program?" rather than "Does this program compile without errors?" (`kit.py lint` and `audit` warn).
- Lesser-known programming languages. Give context on the language, for example its documentation.
- Base64 in tool output. Remove tools that return base64 data into context.

## 13. Prefer targeted edits over whole-file rewrites

Append to the system prompt or first user message (`fable-targeted-edits`):

> The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.

## 14. Leave room for long outputs at xhigh and max

Run long deliverables at `high` unless a gain is measured. At `xhigh`/`max`, set `max_tokens` for thinking plus reply and append the one-limit note to the end of the user message with the real value (`one-limit-note`; the builder fills in `max_tokens`).

## 15. Let the lead agent keep working while subagents run

If the agent can delegate, don't force the lead to wait: make the start-subagent tool return immediately, pass each result back in a later user message when ready, and give the lead a separate wait tool. The model still often waits; the savings come from runs where it doesn't.

## 16. Vision: crop and zoom

For dense charts, run the model as an agent with a container holding the raw images and PIL/OpenCV, or at least an image-cropping tool that returns a chosen region enlarged.

## 17. Techniques shared by current Claude models

Clear, direct instructions with reasons; 3 to 5 varied examples in `<example>` tags; XML tags separating instructions, context, examples, input; long documents first and the question last; say what to produce rather than what to avoid; structured outputs instead of prefill; "Use this tool when …" instead of emphatic triggers. Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
