---
name: create-meta-prompt
description: Create optimized prompts for Claude-to-Claude pipelines with research, planning, and execution stages. Use when building prompts that produce outputs for other prompts to consume, or when running multi-stage workflows (research -> plan -> implement).
triggers:
  - meta prompt
  - create prompt
  - prompt pipeline
  - claude-to-claude
---

<objective>
Create prompts optimized for Claude-to-Claude communication in multi-stage workflows. Outputs are structured with XML and metadata for efficient parsing by subsequent prompts.

Every execution produces a `SUMMARY.md` for quick human scanning. Each prompt gets its own folder in `.prompts/` with output artifacts, enabling clear provenance and chain detection.
</objective>

<workflow>
1. **Intake**: Determine purpose (Do/Plan/Research/Refine), gather requirements
2. **Chain detection**: Check `.prompts/*/` for existing research/plan files to reference
3. **Generate**: Create prompt using purpose-specific patterns
4. **Save**: Create folder `.prompts/{number}-{topic}-{purpose}/`
5. **Present**: Show decision tree for running
6. **Execute**: Run prompt(s) with dependency-aware execution
7. **Summarize**: Create SUMMARY.md for human scanning
</workflow>

<folder_structure>
```
.prompts/
├── 001-auth-research/
│   ├── completed/001-auth-research.md   # archived after run
│   ├── auth-research.md                 # full output (XML for Claude)
│   └── SUMMARY.md                       # executive summary (markdown for human)
├── 002-auth-plan/
│   ├── completed/002-auth-plan.md
│   ├── auth-plan.md
│   └── SUMMARY.md
└── 003-auth-implement/
    ├── completed/003-auth-implement.md
    └── SUMMARY.md
```
</folder_structure>

<intake>
If no context provided, ask for purpose: Do / Plan / Research / Refine.

If context provided, infer purpose from keywords:
- `implement`, `build`, `create`, `fix` → Do
- `plan`, `roadmap`, `strategy`, `phases` → Plan
- `research`, `understand`, `analyze`, `explore` → Research
- `refine`, `improve`, `iterate`, `update` → Refine

Extract topic identifier (kebab-case, e.g. `auth`, `stripe-payments`). Ask 2-4 clarifying questions based on purpose gaps. Confirm before generating.
</intake>

<prompt_structure>
All generated prompts include:

1. **Objective** — what to accomplish and why
2. **Context** — referenced files (@), dynamic context (!)
3. **Requirements** — specific instructions
4. **Output specification** — save location and structure
5. **Metadata** (Research/Plan only) — XML tags required in output
6. **SUMMARY.md requirement** — all prompts must produce one
7. **Success criteria** — how to verify it worked

For Research and Plan outputs, require these XML tags:
- `<confidence>` — confidence level in findings
- `<dependencies>` — what's needed to proceed
- `<open_questions>` — what remains uncertain
- `<assumptions>` — what was assumed

SUMMARY.md must contain: one-liner, Key Findings, Decisions Needed, Blockers, Next Step.
</prompt_structure>

<execution>
Detect dependencies by scanning prompts for `@.prompts/{number}-{topic}/` references.

**Sequential**: chained prompts where each depends on previous output — execute in order, stop on failure.

**Parallel**: independent prompts with no dependencies — spawn all Task agents in a single message.

**Mixed**: build dependency layers, run parallel within each layer, sequential between layers.

After each completion: validate output exists, is non-empty, has required metadata tags and SUMMARY.md. Archive prompt to `completed/` subfolder on success.

Show inline SUMMARY.md content in results so user sees findings without opening files.
</execution>

<failure_handling>
Sequential failure: stop chain, report completed/failed/not-started, offer retry or stop.

Parallel failure: continue others, collect all results, report failures with details, offer retry.

Missing dependencies: warn user, offer to create missing prompt first or continue anyway.
</failure_handling>

<success_criteria>
- Purpose and topic identified during intake
- Chain detection performed, relevant files referenced
- Prompt generated with correct structure for purpose
- Folder created in `.prompts/` with correct naming
- SUMMARY.md requirement and metadata requirements included
- Prompts executed in correct dependency order
- Output validated after each completion
- Successful prompts archived to `completed/`
- SUMMARY.md displayed inline in results
</success_criteria>
