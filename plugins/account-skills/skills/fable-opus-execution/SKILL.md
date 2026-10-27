---
name: "fable-opus-execution"
description: "Use when writing, reviewing, or running prompts, API requests, or long-horizon agents for Claude Fable 5.1 (claude-fable-5-1, also Mythos 5.1), including Fable leading Opus subagents: effort, its 400s, refusals and Opus fallback, silent agents, one tool call per turn, whole-file rewrites, early stops. For Opus 5.5 alone use opus-5-5-execution."
---

# Claude Fable 5.1 execution

Build requests and agent harnesses for Claude Fable 5.1 the way Anthropic's Fable 5.1 guide prescribes (verified 2026-09-28). Opus 5.5 rules live in opus-5-5-execution.

Companion tooling (optional): the Speakwright build kit's `.claude/skills/prompting-fable-5-1/` skill ships `scripts/kit.py` (build, audit, lint, send) and a working unattended `scripts/agent_loop.py` (file, shell, todo tools; batching nudge; continuations; reminders; append-only check; destructive-command guard; request logs). When available, build with `kit.py`, audit to 0 errors, and dry-run agents with `--dry-run`.

## Facts

| | |
|---|---|
| Model string | `claude-fable-5-1` (Mythos 5.1: same capabilities, Project Glasswing only) |
| Context / max output | 1M / 128K |
| Price per MTok | $10 input, $50 output; cache read $0.25; cache write $12.50 (5 min) / $20 (1 h); batch $5 / $25 |
| Thinking | Always on (adaptive) |
| Effort | `low`, `medium`, `high` (default), `xhigh`, `max` |
| Refusal fallback targets | Claude Opus 4.8, Claude Opus 5 |

Anthropic: for most workloads start with Claude Opus; use Fable 5.1 for demanding reasoning and long-horizon agentic work, or when evals on Opus at higher effort still fall short. A common split is a Fable 5.1 lead (`high`) with Opus 5.5 subagents (`medium`). Fable 5.1 reads Opus 5.5 thinking blocks, so a conversation can move up from Opus to Fable and keep its reasoning; earlier models can't read Fable's blocks, so moving down drops them.

## Hard rules (400)

- Non-default `temperature`, `top_p`, `top_k`.
- Assistant prefill.
- `tool_choice` `{"type": "any"}` or `{"type": "tool", …}` ("not supported for this model"); `auto` and `none` work.
- `thinking` disabled/enabled or `budget_tokens`; send `{"type": "adaptive"}`.
- Replayed thinking blocks after the prefix changed (accounts created on or after 2026-08-31), unless `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` with beta `thinking-binding-controls-2026-08-01`.
- Betas: `display: "updates"` → `thinking-display-updates-2026-08-18`; `clear_at` → `mid-conversation-system-clear-at-2026-08-21`; per-message effort → `mid-conversation-output-config-2026-07-01`.

## Effort

Start at `high`, then test `low`, `medium`, `xhigh`, `max` on your evals; re-run the sweep even if you ran one on Fable 5. `medium` roughly matches Fable 5 at lower cost; `low` is often competitive with Opus and Sonnet on cost per task while scoring higher. At `low` it calls search less (raise effort or add the search instruction below). At `xhigh`/`max` it may draft long deliverables twice: run those at `high` unless you measured a gain; otherwise set a large `max_tokens` (thinking counts toward it; 128,000 for long turns) and append Anthropic's one-limit note with the real value. Change effort for one turn with per-message effort to keep the cache.

## Behaviors and fixes (verbatim text from the guide)

- **Silent during tool calls:** set `display: "updates"` and render non-empty thinking blocks; remove lines like "hold all findings for the final response"; if you want more, add: "Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture."
- **One tool call per turn in coding or computer-use loops:** at the end of the request after each round of tool results: "First privately list what you need next; then request every item that doesn't depend on another's result in this one response."
- **Describes the next step instead of doing it, or asks "Shall I apply this?":** add both blocks at the end of the system prompt from the first request: the one beginning "You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide." and the "# Delivering work" block beginning "The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it." If prompt length is tight, the first keeps most of the effect.
- **Dense prose:** add the mannered-prose paragraph to a user message (preferred), or "Please remove all mannered prose."
- **Too little formatting:** remove anti-formatting rules written for earlier models; say when formatting is appropriate.
- **Unmarked quotes from sources:** add one complete correct example (request, response, one-sentence rationale) to the system prompt, as in Anthropic's Harbor Bridge example.
- **Whole-file rewrites:** "The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing."
- **Scope creep in code:** "If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. … Commit tests only where the task asks for them or this repository already keeps tests for this kind of change … This is about extras only: implement every behavior the task asks for, completely."
- **Answers from memory about new names at low effort:** the guide's paragraph telling it to search a name it doesn't confidently recognize, using the name as written in at least one query.
- **Safeguard false positives:** ask "Are there any bugs in this program?" instead of "Does this program compile without errors?"; document lesser-known languages; keep base64 out of tool output.
- **Compaction:** prefer server-side; on the client, replace the history with one summary plus the new user turn, using Anthropic's six-point summary instruction (difficulties, options, decisions stated exactly, current state, open items, exact details), weighting the user's words over the model's.
- **Vision:** a crop-and-zoom tool or a container with PIL/OpenCV.

## Harness rules

1. Append-only history; verify each request's messages are a byte-identical prefix of the next.
2. Per-turn nudges (batching; silent-stretch reminder "The user hasn't heard from you in a while — say in a few words what you're doing, then continue." after about five silent steps, at most three times) go in turn-scoped system messages; leave earlier copies in place.
3. A text-only end of turn with open todo items is a report: send "Your task list still has open items: …. Continue with them. If one is blocked, say what is blocking it." at most two times, then surface the run for review.
4. Subagents: the spawn tool returns immediately, results arrive in a later user message, and a separate wait tool lets the lead keep working. If Opus subagents over-delegate: "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams that don't need to share state. For simple tasks, sequential operations, single-file edits, or tasks where you need to maintain context across steps, work directly rather than delegating."
5. Multi-agent time signal: append `elapsed Ns / Bs` to messages sent back; the budget is advisory, keep a hard timeout.
6. Refuse destructive commands (rm -r, force push, reset --hard, --no-verify, dropping tables) unless the user approves.

## Refusals and billing

A decline returns HTTP 200, `stop_reason: "refusal"`, and `stop_details` naming the policy area. Since 2026-09-24 a refusal that arrives before any output is billed when its category has few false positives. Fall back to Claude Opus 4.8 or Opus 5 without Fable's thinking blocks. Never ask for reasoning in replies.

## Old patterns

Sampling parameters, prefill, forced tool use → 400. Anti-formatting blocks and "hold findings for the end" lines → remove. Effort sweeps from Fable 5 → re-run.

Sources: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 · https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1 · https://platform.claude.com/docs/en/build-with-claude/effort · https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5