# Research Playbook

Six research tracks. SKILL.md Step 4 selects which to run; this file defines how each runs and when it's done. All tracks share three rules: record findings and sources in memory, prefer official and recently-maintained sources, and time-box — research ends when the selection is defensible, not when the internet is exhausted.

## Contents
- R1 Solutions & libraries
- R2 Patterns & prior art
- R3 Official documentation
- R4 Compliance & security
- R5 Codebase & memory
- R6 Prompt techniques (Mode B)

---

## R1 Solutions & libraries

Run when: the task needs any non-trivial capability (auth, payments, charts, queues, parsing, real-time, export, etc.).

Process:
1. Write 2–5 targeted queries per capability: `"[capability] library [stack] [current year]"`, `"[capability] [framework] best library"`, problem-shaped queries ("intermittent OAuth session failures").
2. Collect 3–5 candidates per capability.
3. Evaluate each on: fitness for the actual requirement, maintenance (prefer commits/releases within ~6 months), documentation quality, license, security advisories / known issues, community traction.
4. Select; record winner, losers, and rejection reasons in memory.

Done when: every non-trivial capability has a selected library or a documented justification for custom code.

## R2 Patterns & prior art

Run when: architecture work, refactors, migrations, consolidations, or debugging recurring/known failure classes.

Process:
1. Query for the pattern, not the product: `"payment consolidation adapter pattern"`, `"webhook centralization architecture"`, `"[symptom] root cause"`.
2. Look for postmortems and "how X solved Y" write-ups — failure modes transfer better than success stories.
3. Extract 2–3 candidate architectures/approaches with trade-offs; the task document picks one and cites why.

Done when: the chosen approach names its rejected alternatives.

## R3 Official documentation

Run when: any library, SDK, or API is selected (R1) or already in use.

Process:
1. Pull official docs for the exact version in use (or the version selected).
2. Extract the patterns the task will use: initialization, the specific calls needed, error handling, idempotency/retry support, rate limits, breaking-change notes.
3. Prefer docs pulled through the documentation/memory system (e.g., Claude Mem MCP) or the vendor site over third-party tutorials.

Done when: every implementation phase can cite the documented pattern it follows. Never skip this track when a library was chosen.

## R4 Compliance & security

Run when: the task touches payments, authentication, health data, personal data, minors, finance, or any regulated domain — or the user names a standard (PCI, SOC 2, HIPAA, GDPR).

Process:
1. Identify the applicable standard(s); query the current version's requirements relevant to the task.
2. Translate requirements into concrete checkboxes (tokenization, no raw card storage, signature validation, data residency) — compliance lives in the Implementation section, not a footnote.
3. Add a validation item: evidence that each requirement is met.

Done when: every applicable requirement maps to at least one implementation or validation checkbox.

## R5 Codebase & memory

Run when: existing code is involved (almost always).

Process:
1. Check memory first for prior context on this codebase, topic, or team — reuse before rediscovering.
2. Inventory the codebase: structure, entry points, dependencies and versions, relevant flows.
3. Read every mentioned or relevant file end to end.
4. Save the complete analysis to memory with a cross-reference map.

Done when: every claim in the task document about existing code traces to a file actually opened.

## R6 Prompt techniques (Mode B only)

Run when: the deliverable is an enhanced prompt.

Process:
1. Match the prompt's job to technique candidates: tree-of-thought (branching decisions), zero-shot chain-of-thought (novel reasoning), few-shot examples (format-sensitive output), constrained writing (strict formats), role/persona (audience-specific tone), prompt chaining (multi-stage work), analogical reasoning (creative/strategic tasks).
2. Select the minimum set that serves the job — technique count is not a quality signal; one well-matched technique beats five decorative ones.
3. Verify the enhanced prompt has no internal contradictions; conflicts between instructions are the top failure mode of combined prompts.
4. Tune for the target model if known: explicit effort/reasoning settings, verbosity specs, persistence language, boundary setting — see [model-adapters.md](model-adapters.md).

Done when: the enhanced prompt states identity, purpose, context, task, constraints, and examples — and survives a read-through with zero contradictions.
