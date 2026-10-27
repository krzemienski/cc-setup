---
name: deepen-prompt-plan
description: "Stress-test and strengthen any existing plan, prompt, or instruction set with targeted research, confidence scoring, validation gate injection, and XML-structured output. Use when a plan or prompt exists but needs stronger grounding — better rationale, tighter sequencing, risk treatment, functional validation gates, or research-backed evidence. Works on any document type: PLAN.md, PROMPT.md, ROADMAP.md, task descriptions, agent instructions, or implementation plans. Use when asked to 'deepen', 'strengthen', 'stress-test', 'harden', 'ground', or 'validate' any plan or prompt. Also use when a plan feels thin, a prompt lacks validation gates, or decisions lack rationale. For creating plans from scratch, use create-plans or create-validation-plan instead."
---

# Deepen Prompt & Plan

<objective>
Take any existing plan, prompt, or instruction set and make it stronger through targeted analysis, research, and rewriting. This is a second-pass confidence check — not a rewrite from scratch.

The input already exists. The question is: "Is this grounded enough for the complexity and risk involved?"

This skill identifies weak sections, runs targeted research for those sections, injects functional validation where missing, and strengthens the document in place — all using proper semantic XML formatting.
</objective>

<what_this_skill_does>
- Scores confidence gaps across every section of the input document
- Selects the weakest 2-5 sections for targeted deepening
- Runs research (web search, documentation lookup, codebase analysis) for weak sections
- Injects or strengthens functional validation gates (Iron Rule: no mocks, real-system proof)
- Reformats output with clean semantic XML where appropriate
- Preserves the document's existing structure and intent
- Produces a stronger document, not a longer one
</what_this_skill_does>

<what_this_skill_does_not_do>
- Rewrite documents from scratch (use create-plans or create-meta-prompts for that)
- Add implementation code (pseudo-code and DSL sketches are allowed)
- Invent new requirements or change scope without surfacing them as open questions
- Turn plans into implementation scripts
- Replace the original author's intent or architectural decisions
</what_this_skill_does_not_do>

<essential_principles>

<principle name="stress_test_not_inflate">
Deepening increases justified confidence. It does not make the document longer for its own sake. If a section is already strong, leave it alone. Every addition must earn its place by closing a specific confidence gap.
</principle>

<principle name="selective_depth">
Focus on the weakest 2-5 sections rather than enriching everything. A plan with 3 rock-solid sections and 2 strengthened weak points is better than a plan where every section got a thin coat of paint.
</principle>

<principle name="iron_rule_enforcement">
If the document describes something that will be built and run, it must have validation gates. The Iron Rule applies: if the real system doesn't work, fix the real system. Never create mocks, stubs, test doubles, or test files. Every gate must have specific, observable, measurable PASS criteria defined BEFORE execution.
</principle>

<principle name="xml_structure">
Use semantic XML tags for structured content. Tags should be descriptive and self-documenting. Use attributes for metadata. Nest tags to represent hierarchy. This makes documents parseable by both humans and downstream Claude instances.

Example:
```xml
<task id="1" priority="high">
  <description>Create the API endpoint</description>
  <validation_gate id="VG-1" blocking="true">
    <pass_criteria>HTTP 201 with valid JSON body containing "id" field</pass_criteria>
    <evidence_command>curl -s -X POST localhost:3000/api/users | tee evidence/vg1.json | jq .</evidence_command>
  </validation_gate>
</task>
```
</principle>

<principle name="research_before_opinion">
When a section needs strengthening, prefer evidence over opinion. Check documentation, search for current best practices, analyze the codebase. A decision backed by "the official docs recommend X because Y" is stronger than "X seems like a good idea."
</principle>

<principle name="preserve_planning_boundary">
No implementation code. No git command choreography. No exact test command recipes (validation gate commands are the exception — those ARE the test). Pseudo-code sketches and architecture diagrams are allowed.
</principle>

</essential_principles>

<workflow>

**Phase narration (mandatory):** At each phase boundary, tell the user which phase you are entering and what it does. This is NOT optional — the user must always know where they are in the 6-phase process. Keep it to one sentence. Examples:
- "**Phase 0: Loading and classifying** — reading the document and building a risk profile."
- "**Phase 2: Scoring confidence gaps** — identifying which sections are weakest."
- "**Phase 5: Synthesizing** — rewriting the selected sections with research findings."

## Phase 0: Load and Classify

### 0.1 — Locate the Document

Accept the document path as an argument, from the conversation context, or by scanning common locations:

```bash
# Check common plan/prompt locations
find . -maxdepth 3 -name "*.md" \( -path "*/plans/*" -o -path "*/.planning/*" -o -path "*/.prompts/*" -o -path "*/PLAN.md" -o -path "*/PROMPT.md" \) 2>/dev/null | head -20
```

If multiple candidates exist, ask the user which document to deepen. Do not proceed without a valid file path.

Read the document completely. If it references an origin document (brief, roadmap, spec), read that too.

### 0.2 — Classify Document Type and Risk

Determine the document type:

| Type | Signals | Deepening Focus |
|------|---------|-----------------|
| **Implementation Plan** | Tasks, phases, file paths, verification | Sequencing, validation gates, system impact |
| **Prompt / Instructions** | Role definition, workflows, output specs | Clarity, edge cases, validation criteria |
| **Roadmap** | Phases, milestones, dependencies | Phase gate criteria, risk treatment, ordering |
| **Research Plan** | Questions, sources, methodology | Completeness, source quality, gap coverage |
| **Agent Instructions** | Tools, workflows, decision trees | Edge case handling, failure modes, validation |

Build a risk profile. These are high-risk signals that warrant deeper treatment:

- Authentication, authorization, or security-sensitive behavior
- Payments, billing, or financial flows
- Data migrations, backfills, or persistent data changes
- External APIs or third-party integrations
- Privacy, compliance, or user data handling
- Cross-platform parity or multi-surface behavior
- Significant rollout, monitoring, or operational concerns
- Prompts that will be executed autonomously without human review

### 0.3 — Decide Whether to Deepen

Not every document needs deepening. Use this heuristic:

- **Simple / Low-risk**: Usually skip unless user explicitly requests it. Offer to proceed to execution instead.
- **Moderate complexity**: Often benefits when 1-2 important sections are thin.
- **High complexity or high risk**: Almost always benefits from a targeted second pass.

If the document is already well-grounded, say so. Recommend moving to execution. If the user insists, do a light pass on at most 1-2 sections.

## Phase 1: Parse Structure

Map the document into its constituent sections. Look for these or their equivalents:

<section_taxonomy>
**For Plans:**
- Overview / Objective
- Context / Background
- Requirements / Success Criteria
- Scope Boundaries
- Research / Sources
- Key Decisions (with rationale)
- Open Questions
- Technical Design (pseudo-code, diagrams, data flow)
- Tasks / Implementation Units
- System-Wide Impact
- Risks & Dependencies
- Validation / Verification
- Operational Notes

**For Prompts / Instructions:**
- Role / Identity
- Objective / Purpose
- Context / Background
- Workflows / Phases
- Decision Trees / Routing
- Output Specifications
- Validation Criteria / Success Criteria
- Edge Cases / Error Handling
- Constraints / Boundaries
- Examples (few-shot)

**For Roadmaps:**
- Vision / Goals
- Phase Definitions
- Phase Gate Criteria
- Dependencies Between Phases
- Risk Register
- Milestone Definitions
</section_taxonomy>

Collect metadata: which sections exist, which are absent, what references are cited, what validation exists.

## Phase 2: Score Confidence Gaps

For each section, compute a confidence gap score.

Load detailed scoring rubric: [references/confidence-scoring.md](references/confidence-scoring.md)

**Scoring formula per section:**

```
gap_score = trigger_count + risk_bonus + critical_section_bonus
```

Where:
- **trigger_count** = number of checklist problems that apply (from the rubric)
- **risk_bonus** = +1 if the topic is high-risk AND this section is materially relevant to the risk
- **critical_section_bonus** = +1 for Key Decisions, Tasks/Implementation, System Impact, Risks, Validation, or Workflows in moderate-to-complex documents

**Selection threshold:**
- Score ≥ 2: candidate for deepening
- Score = 1 in a high-risk domain AND section is materially important: also a candidate
- Select the top **2-5 sections** by score
- For light-pass deepening (user insisted on simple doc): cap at **1-2 sections**

**Present the scoring table to the user before proceeding.** Transparency about what was selected and why builds trust and lets the user adjust the selection. Show each section with its trigger count, bonuses, total score, and which specific triggers fired. Example:

```
Confidence Gap Scores:
| Section         | Triggers | Risk | Critical | Total | Deepen? |
|-----------------|----------|------|----------|-------|---------|
| Key Decisions   |    2     |  +1  |    +1    |   4   |  YES    |
|   → Decisions stated without tradeoff analysis                  |
|   → Obvious alternatives not addressed                          |
| Risks           |    2     |  +1  |    +1    |   4   |  YES    |
|   → Risks listed without mitigation                             |
|   → Security risks absent where they obviously apply            |
| Validation      |    2     |  +1  |    +1    |   4   |  YES    |
|   → No validation gates present                                 |
|   → PASS criteria vague                                         |
| Context         |    1     |   0  |     0    |   1   |  no     |
| Overview        |    0     |   0  |     0    |   0   |  no     |
```

Ask: "These are the sections I'll deepen. Want to adjust before I proceed?" If the user is running this non-interactively (pipeline, subagent), proceed with the top-scored sections automatically.

## Phase 3: Research Weak Sections

For each selected section, choose the smallest useful research approach. Do not research everything — only what closes the identified gap.

Load research strategies: [references/research-strategies.md](references/research-strategies.md)

**Research priority order** (prefer earlier sources):
1. **Codebase analysis** — grep, find, read existing code for patterns and conventions
2. **Existing documentation** — README, CLAUDE.md, architecture docs in the repo
3. **Origin documents** — brief, spec, roadmap that the plan derives from
4. **Official documentation** — framework docs, API references, library guides (use web search or context7 MCP)
5. **External best practices** — industry patterns, security guidelines, performance benchmarks

**Research execution:**
- Run searches in parallel when independent
- Keep findings focused: strongest evidence only
- For each finding, note: what it changes in the plan, and where the evidence came from
- If findings conflict, prefer repo-grounded evidence over generic advice; prefer official docs over blog posts

**Present a compact research summary before proceeding.** The user should see what evidence was found and how it will inform the rewrite. Use this format:

```xml
<research_summary>
  <finding section="Key Decisions" source="OWASP Session Management Cheat Sheet">
    JWT with short-lived access tokens + refresh rotation is recommended for stateless APIs.
    Impact: Adds rationale and source to D1 decision.
  </finding>
  <finding section="Risks" source="codebase: src/middleware/logger.ts">
    Logging middleware already redacts sensitive fields (line 23).
    Impact: Risk R3 mitigation can reference existing safeguard.
  </finding>
</research_summary>
```

Keep it brief — 1-3 lines per finding. The goal is transparency, not a research report. If no research was needed (gap closeable from the document itself), say so and skip.

## Phase 4: Inject or Strengthen Validation

This phase applies specifically to documents that describe something that will be built and executed. Skip for pure research plans or documentation.

Load deepening patterns: [references/deepening-patterns.md](references/deepening-patterns.md)

**If the document has NO validation gates:**

Inject the mock detection preamble at the top:

```xml
<mock_detection_protocol>
Before executing any task, check intent:
- Creating .test.*, _test.*, *Tests.*, test_* files → STOP
- Importing mock libraries → STOP
- Creating in-memory databases → STOP
- Adding TEST_MODE or NODE_ENV=test flags → STOP
Fix the REAL system instead. No exceptions.
</mock_detection_protocol>
```

Then inject validation gates after each task or logical unit:

```xml
<validation_gate id="VG-{N}" blocking="true">
  <prerequisites>[Dependencies started + health checked]</prerequisites>
  <execute>[Real system interaction]</execute>
  <capture>[Commands that save output to evidence/ files]</capture>
  <pass_criteria>[Specific, observable, measurable — defined NOW not during execution]</pass_criteria>
  <review>[READ the evidence: Read tool for images, cat for text, jq for JSON]</review>
  <verdict>PASS → next task | FAIL → fix real system → re-run from prerequisites</verdict>
  <mock_guard>IF tempted to mock → STOP → fix real system</mock_guard>
</validation_gate>
```

Append a gate manifest at the end:

```xml
<gate_manifest>
  <total_gates>{N}</total_gates>
  <sequence>VG-1 → VG-2 → ... → VG-N</sequence>
  <policy>All gates BLOCKING. No advancement on FAIL.</policy>
  <evidence_dir>evidence/</evidence_dir>
  <regression>If ANY gate FAILS: fix → re-run from failed gate → do NOT skip</regression>
</gate_manifest>
```

**If the document HAS validation gates:**

Audit existing gates against quality standards:
- Are PASS criteria specific and measurable (not "it works")?
- Does every gate capture evidence to disk (not ephemeral)?
- Does every gate review evidence (not just check file exists)?
- Is mock detection present?
- Are there phase-level regression gates (Phase 2 re-validates Phase 1)?

Strengthen any gates that fail these checks.

## Phase 5: Synthesize and Rewrite

Strengthen only the selected sections. Keep the document coherent and preserve its overall structure.

**Size budget:** Deepening should make the document stronger, not bloated. Use these heuristics:
- Documents under 500 words: up to 3x growth is acceptable (thin docs need the most enrichment)
- Documents 500-1500 words: aim for under 2x growth
- Documents over 1500 words: aim for under 30% growth — at this size, every addition must displace or replace weak content
- If the output is growing beyond budget, you are enriching too many sections. Tighten selection.

**Allowed changes:**
- Clarify or strengthen decision rationale
- Tighten requirements trace or success criteria
- Reorder or split tasks when sequencing is weak
- Add missing references, file paths, or verification outcomes
- Expand risk treatment, system impact, or operational notes where justified
- Reclassify open questions (resolved vs deferred) when evidence supports it
- Inject or strengthen validation gates per Phase 4
- Add or strengthen XML structure for machine-parseable sections
- Add `<confidence>`, `<assumptions>`, `<open_questions>` metadata where valuable

**Forbidden changes:**
- Adding implementation code (imports, exact signatures, framework syntax)
- Rewriting the entire document from scratch
- Inventing new product requirements or changing scope silently
- Adding generic "insights" subsections that don't close a specific gap
- Removing existing content that was correct

**XML formatting guidance:**
Use semantic XML for structured content. Tags should be self-documenting. Attributes carry metadata. Nest for hierarchy. Keep prose sections as regular markdown — XML is for structured, parseable content only.

```xml
<task id="2" depends_on="1" platform="ios">
  <description>Implement the authentication flow</description>
  <files>Sources/Auth/AuthManager.swift, Sources/Auth/TokenStore.swift</files>
  <approach>Follow existing AuthProvider protocol pattern in Sources/Auth/</approach>
  <validation_gate id="VG-2" blocking="true">
    <pass_criteria>
      Simulator screenshot shows login screen → enter credentials → 
      dashboard appears with user name displayed in nav bar
    </pass_criteria>
  </validation_gate>
</task>
```

## Phase 6: Final Checks and Write

Before writing the updated document:

1. **Stronger, not longer** — confirm additions close specific gaps and the document stays within the size budget from Phase 5
2. **Planning boundary intact** — no implementation code leaked in
3. **Correct sections targeted** — the weakest sections were actually the ones deepened
4. **Origin intent preserved** — the document still serves its original purpose
5. **Validation gates present** — if building something, every task has a gate with measurable criteria
6. **XML well-formed** — tags open and close correctly, attributes are quoted

Write the updated document in place by default. If the user requests a separate file, append `-deepened` before `.md`.

</workflow>

<post_deepening>
After writing, present next steps:

**If substantive changes were made:**
1. **View diff** — show what changed and why
2. **Deepen further** — run another targeted pass on specific sections
3. **Execute** — begin implementing the plan
4. **Transform to gated prompt** — convert the full document into a validation-gated execution prompt (use transform-validation-prompt skill)

**If no substantive changes were warranted:**
- Say the document is already well-grounded
- Recommend execution as the next step
</post_deepening>

<reference_index>
All in `references/`:

- **confidence-scoring.md** — Detailed checklist triggers for every section type (plans, prompts, roadmaps), scoring rubric, and examples of gap identification
- **research-strategies.md** — Research source priority, execution patterns, conflict resolution, and evidence quality standards
- **deepening-patterns.md** — Platform-specific validation gate templates, XML formatting patterns, prompt strengthening patterns, and before/after examples
</reference_index>

<success_criteria>
A deepened document succeeds when:
- Only weak sections were modified (selective, not blanket)
- Every addition closes a specific, identified confidence gap
- Decisions have evidence-backed rationale (not opinion)
- Validation gates have specific, observable, measurable PASS criteria
- No mocks, stubs, or test files introduced
- XML structure is well-formed and semantically meaningful
- The document is stronger and roughly the same size (not bloated)
- Original intent and scope are preserved
- Open questions are surfaced, not silently resolved
</success_criteria>
