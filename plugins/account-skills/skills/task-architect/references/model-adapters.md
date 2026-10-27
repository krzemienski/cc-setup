# Model Adapters

Optional per-model tuning. When the executing agent's model is known, apply the matching block (append it to the generated artifact's orchestration section, or use it to adjust how the skill itself behaves). Current as of July 2026 — re-verify against vendor docs when a new model generation ships.

## Claude Fable 5 / Opus 4.8 (Anthropic)

- Set the effort parameter from the complexity table (high/xhigh/max for High and Critical tiers) with max_tokens ≥ 64k at the top tiers; raise effort before rewriting the plan if reasoning looks shallow.
- Instructions are followed literally across ALL sections — state scope explicitly wherever it matters, and keep the artifact internally consistent (contradictions get obeyed faithfully, both halves).
- XML-tagged sections are native structure; keep them.
- Emphasis language (CRITICAL/MUST/ALWAYS) is reserved for irreversible operations — the model over-triggers on it otherwise.
- Prefer blocking subagents for accuracy-critical steps; asynchronous where speed matters more.

## Kimi K3 (Moonshot)

- Reasoning is always on: do not script step-by-step chains; specify verification checkpoints (what must be true before each phase transition).
- K3 is highly proactive: bound scope explicitly. State in the artifact what is out of scope, and require it to surface options + its recommended assumption rather than silently expanding scope.
- Preserve full reasoning history across turns; if the harness drops it, say so and request restoration before continuing.
- Structured system prompts with clear sections work well; keep the task document's XML-tagged skeleton.

## GPT-5.6 / 5.2 (OpenAI)

- Include agentic persistence language: "keep going until every checkbox is verifiably complete; decompose the objective into all required sub-requests; if a constraint can't be fully satisfied, state the residual gap and complete the rest."
- Calibrate context-gathering: aggressive for High/Critical tiers (no tool-call cap); capped (~2 calls) for Simple tiers with permission to proceed under uncertainty.
- Give concrete length/verbosity guidance — the model adheres to it well ("updates of 1–2 sentences at phase transitions only").
- Avoid conflicting instructions anywhere in the artifact; GPT-5.x models surface contradictions as erratic behavior rather than questions.
