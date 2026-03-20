---
name: research
description: Multi-source research on technical topics. Produces a structured findings summary with sources and recommendations. Supports three subtypes: technical (how to implement), options (compare alternatives), feasibility (can we do this).
triggers:
  - "research"
  - "investigate"
  - "find out"
  - "what are the options"
  - "look into"
  - "explore options"
---

# Research

Conduct structured multi-source research and deliver actionable findings.

## Steps

### 1. Classify the Subtype

Identify which subtype applies:

- **technical** — How to implement something. Focus: APIs, patterns, constraints, examples.
- **options** — Compare alternatives. Focus: trade-offs, scoring, recommendation.
- **feasibility** — Can we do this? Focus: blockers, risks, prerequisites, viability verdict.

If unclear, infer from the request. State the subtype before proceeding.

### 2. Define Scope

State in one sentence what you are researching and what is out of scope.

### 3. Gather from All Applicable Sources

Run searches in parallel across every relevant source:

- **Web search** (`WebSearch` / `mcp__claude_ai_exa__web_search_exa`) — current docs, articles, changelogs
- **Code search** (`mcp__claude_ai_exa__get_code_context_exa`) — real usage examples, library internals
- **Official docs** (`mcp__claude_ai_Context7__resolve-library-id` + `query-docs`) — authoritative API reference
- **Package registries** — npm, PyPI, crates.io; check download counts, last publish, open issues
- **GitHub** (`gh search repos`, `gh search code`) — battle-tested implementations, community solutions

Skip sources that are clearly irrelevant (e.g. package registries for a pure architectural question).

### 4. Synthesize Findings

#### For `technical`:
- How it works (mechanism, key concepts)
- Implementation steps or pattern
- Known constraints, gotchas, version requirements
- Best available library or built-in approach

#### For `options`:
- List each option with: description, pros, cons, maturity, license
- Score each on the criteria that matter for the request (performance, DX, size, etc.)
- Clear recommendation with rationale

#### For `feasibility`:
- Viability verdict: FEASIBLE / FEASIBLE WITH CAVEATS / NOT FEASIBLE
- Prerequisites and blockers
- Estimated effort (HIGH / MEDIUM / LOW)
- Risks and mitigations
- Recommended path forward

### 5. Output Findings

Present results in this structure:

```
## Research: <topic>
Subtype: technical | options | feasibility

### Summary
<2-4 sentence executive summary with the key takeaway>

### Findings
<subtype-specific content from step 4>

### Sources
- <Title or description>: <URL>
- ...

### Recommendation
<Single clear recommendation or verdict. What should be done next.>

### Open Questions
<Anything that requires user input or further investigation to resolve. Omit if none.>
```

## Notes

- Cite every claim that comes from an external source.
- Distinguish verified facts from inferences — label inferences explicitly.
- If sources conflict, surface the conflict and explain which to trust and why.
- Do not produce implementation code unless the user asks to proceed after reviewing findings.
