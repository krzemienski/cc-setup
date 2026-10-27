# Confidence Scoring Reference

Detailed checklist triggers for identifying weak sections in plans, prompts, and roadmaps.

## How Scoring Works

For each section in the document, count how many checklist triggers apply. Add bonuses for risk relevance and critical-section status.

```
gap_score = trigger_count + risk_bonus + critical_section_bonus
```

- **trigger_count**: Number of problems from the checklist below
- **risk_bonus**: +1 if the document's risk profile includes this section's domain (e.g., auth section in a security-sensitive plan)
- **critical_section_bonus**: +1 for Key Decisions, Tasks, System Impact, Risks, Validation, or Workflows in moderate-to-complex documents

**Selection thresholds:**
- Score ≥ 2 → candidate for deepening
- Score = 1 in high-risk domain with material relevance → also candidate
- Select top 2-5 sections by score (1-2 for light-pass)

---

## Plan Section Checklists

### Overview / Objective
- [ ] Objective is vague or could describe many different projects
- [ ] No connection between objective and success criteria
- [ ] Missing "why" — rationale for doing this work

### Context / Background
- [ ] References patterns or conventions but never uses them in decisions
- [ ] Cites sources that don't materially shape the plan
- [ ] High-risk work lacks appropriate grounding in existing system
- [ ] Context is generic rather than specific to this codebase or domain

### Requirements / Success Criteria
- [ ] Requirements are vague or disconnected from tasks
- [ ] Success criteria are missing or not measurable
- [ ] Tasks don't clearly advance the stated requirements
- [ ] Origin requirements (from brief/spec) not carried forward

### Key Decisions
- [ ] A decision is stated without rationale
- [ ] Rationale doesn't explain tradeoffs or rejected alternatives
- [ ] Decision doesn't connect to requirements, scope, or constraints
- [ ] Obvious design fork exists but no explanation of why one path was chosen
- [ ] Decision relies on assumption that hasn't been validated

### Open Questions
- [ ] Product-level blockers are hidden as assumptions
- [ ] Planning-owned questions are incorrectly deferred to implementation
- [ ] Resolved questions have no clear basis in evidence
- [ ] Deferred items are too vague to be actionable later

### Technical Design
- [ ] Uses wrong medium (pseudo-code where diagram would be clearer, or vice versa)
- [ ] Contains actual implementation code instead of design sketches
- [ ] Doesn't connect to key decisions or task structure
- [ ] Missing for complex work (DSL design, multi-component integration, complex data flow)

### Tasks / Implementation Units
- [ ] Dependency order unclear or likely wrong
- [ ] File paths or artifacts are missing where they should be explicit
- [ ] Tasks too large (>2-3 per plan unit) or too granular (micro-steps)
- [ ] Approach notes thin or don't reference patterns to follow
- [ ] Verification criteria vague or absent

### System-Wide Impact
- [ ] Affected interfaces, middleware, entry points missing
- [ ] Failure propagation underexplored
- [ ] State lifecycle, caching, or data integrity risks absent
- [ ] Integration coverage weak for cross-layer work

### Risks & Dependencies
- [ ] Risks listed without mitigation strategy
- [ ] Rollout, monitoring, or support implications missing
- [ ] External dependency assumptions weak or unstated
- [ ] Security, privacy, performance, or data risks absent where they obviously apply

### Validation / Verification
- [ ] No validation gates present for executable tasks
- [ ] PASS criteria are vague ("it works", "no errors", "tests pass")
- [ ] Evidence is not captured to disk (ephemeral validation)
- [ ] Evidence is captured but never reviewed
- [ ] Mock patterns present (test files, stubs, in-memory DBs)
- [ ] No regression validation for multi-phase work

---

## Prompt / Instructions Section Checklists

### Role / Identity
- [ ] Role is generic ("You are a helpful assistant")
- [ ] Expertise claims don't match the task complexity
- [ ] No behavioral constraints or guardrails

### Objective / Purpose
- [ ] Purpose could describe many different prompts
- [ ] No connection between purpose and output specification
- [ ] Missing scope boundaries (what NOT to do)

### Workflows / Phases
- [ ] Steps are vague or could be interpreted multiple ways
- [ ] No decision points or branching logic for different inputs
- [ ] Missing error handling or failure recovery
- [ ] Workflow assumes ideal conditions without fallback

### Decision Trees / Routing
- [ ] Routing logic has gaps (inputs that don't match any branch)
- [ ] Default behavior undefined
- [ ] Branches lead to dead ends

### Output Specifications
- [ ] Output format not specified or underspecified
- [ ] No examples of expected output (missing few-shot demonstrations)
- [ ] Success criteria not measurable
- [ ] Edge cases not addressed

### Validation Criteria
- [ ] No way to verify the prompt produced correct output
- [ ] Criteria are subjective ("looks good", "is helpful")
- [ ] No evidence collection mechanism
- [ ] Missing mock detection for executable prompts

### Edge Cases / Error Handling
- [ ] Happy path only — no consideration of failures
- [ ] Error messages or recovery actions not specified
- [ ] Ambiguous inputs not addressed
- [ ] Resource constraints not considered (context limits, token budgets)

---

## Roadmap Section Checklists

### Phase Definitions
- [ ] Phases are too large (should be split)
- [ ] Phase boundaries are unclear
- [ ] Dependencies between phases not explicit

### Phase Gate Criteria
- [ ] Gates missing entirely
- [ ] Gate criteria vague or not measurable
- [ ] No regression requirement (Phase N re-validates Phase N-1)
- [ ] No evidence specification for gate passage

### Risk Register
- [ ] Risks identified but no mitigation strategy
- [ ] Missing risks that are obvious for the domain
- [ ] Risk severity/probability not assessed
- [ ] No contingency for high-severity risks

---

## Scoring Examples

**Example 1: Key Decisions section in auth plan**
- Trigger: Decision stated without tradeoff analysis (+1)
- Trigger: Obvious alternatives not addressed (+1)
- Risk bonus: Auth is security-sensitive (+1)
- Critical bonus: Key Decisions in complex plan (+1)
- **Score: 4** → Strong candidate

**Example 2: Context section in simple CLI tool plan**
- Trigger: Context is generic, not repo-specific (+1)
- No risk bonus (low-risk domain)
- No critical bonus (Context isn't critical-section)
- **Score: 1** → Skip unless user insists

**Example 3: Validation section in payment processing plan**
- Trigger: No validation gates present (+1)
- Trigger: PASS criteria are vague (+1)
- Risk bonus: Payments are high-risk (+1)
- Critical bonus: Validation in complex plan (+1)
- **Score: 4** → Must deepen
