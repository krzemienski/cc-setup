---
name: reflect
description: Self-refinement framework for iterative quality improvement. Triggers on "reflect", "review my work", "check quality", "self-review".
argument-hint: Optional focus area or confidence threshold, e.g. "security" or "deep reflect if less than 90% confidence"
---

# Self-Refinement Framework

Reflect on the most recent response or output and assess its quality using structured criteria.

## Complexity Triage

Categorize the task before proceeding:

### Quick Path
Single-file edits, documentation updates, simple queries, straightforward bug fixes.
→ Skip to Final Verification checklist only.

### Standard Path
Multiple file changes, new feature implementation, architecture decisions, complex problem solving.
→ Full assessment + confidence score required (>4.0/5.0 to pass).

### Deep Path
Core system changes, security-related code, performance-critical sections, API design.
→ Full assessment + higher confidence threshold (>4.5/5.0 to pass).

## Assessment Checklist

### Completeness
- [ ] Does the solution fully address the stated request?
- [ ] Are all explicit requirements covered?
- [ ] Are implicit requirements addressed?

### Quality
- [ ] Is complexity appropriate — not over- or under-engineered?
- [ ] Could the approach be simplified without losing functionality?
- [ ] Are obvious improvements left on the table?

### Correctness
- [ ] Is the logic sound?
- [ ] Are edge cases considered (boundary values, null/empty inputs, concurrency)?
- [ ] Are there unintended side effects?

### Dependencies & Impact
- [ ] For any addition/deletion/modification: dependencies checked?
- [ ] Related decisions or superseding work identified?
- [ ] Ecosystem files that depend on changed items verified?
- [ ] Nothing recommended for removal without confirming no dependents exist?

**Hard rule**: Flag any unverified dependency before approving the work.

### Claims & Facts
- [ ] Performance claims backed by benchmarks or Big-O analysis?
- [ ] Technical facts cross-referenced with current documentation?
- [ ] Security assertions validated against standards?
- [ ] Best-practice claims cite authoritative sources?

### Generated Artifacts
- [ ] Cross-references to external tools/APIs/files verified to exist?
- [ ] No sensitive data in generated files (absolute paths with usernames, credentials)?
- [ ] Documentation counts/stats updated if referenced values changed?
- [ ] System state claims verified with actual commands, not memory?

**Hard rule**: Do not declare work complete until claims match verified reality.

## Decision Point

**Refinement needed?** [YES / NO]

If YES → identify issues, propose solutions, prioritize (critical first, style last), then implement.
If NO → proceed to Final Verification.

## Code-Specific Criteria

When output involves code, also evaluate:

### Existing Solutions
- [ ] Searched for existing libraries before writing custom code?
- [ ] Considered managed services for infrastructure concerns?
- [ ] Custom code justified by domain-specificity, performance, or security requirements?

### Architecture
- [ ] Naming uses domain language, not generic terms (utils, helpers, common)?
- [ ] Business logic separated from infrastructure?
- [ ] Responsibilities properly separated; no unnecessary coupling?
- [ ] SOLID principles followed where applicable?

### Code Quality
- [ ] No unnecessary complexity (cyclomatic complexity, nesting depth, function length)?
- [ ] No code smells: duplication, long parameter lists, magic numbers, god functions?
- [ ] Errors handled explicitly and consistently?
- [ ] Input validated at system boundaries?

## Non-Code Output Criteria

For documentation, explanations, analysis:

- [ ] Information well-organized with logical flow?
- [ ] Complex concepts explained simply for the intended audience?
- [ ] All aspects of the question addressed with examples where helpful?
- [ ] Limitations and caveats noted?
- [ ] Technical details accurate and verifiable?

## Final Verification Checklist

- [ ] At least one alternative approach considered?
- [ ] Assumptions verified?
- [ ] Simplest correct solution chosen?
- [ ] Another developer would understand this readily?
- [ ] All factual claims verified or sourced?
- [ ] Existing libraries checked before custom code?
- [ ] Tool/API/file references confirmed against actual inventory?
- [ ] Generated files scanned for sensitive information?
- [ ] All docs referencing changed values updated?
- [ ] Claims verified with commands, not memory?
- [ ] No active dependencies exist for anything recommended for deletion?

## Evaluation Report Format

```
## Reflection Report

### Completeness — X/5
Analysis: [evidence-based]
Issues: [if any]

### Quality — X/5
Analysis: [evidence-based]
Issues: [if any]

### Correctness — X/5
Analysis: [evidence-based]
Issues: [if any]

### Dependencies & Impact — X/5
Analysis: [evidence-based]
Issues: [if any]

### Claims & Facts — X/5
Analysis: [evidence-based]
Issues: [if any]

## Score Summary

| Criterion       | Score | Weight | Weighted |
|-----------------|-------|--------|----------|
| Completeness    | X/5   | 0.25   | X.XX     |
| Quality         | X/5   | 0.25   | X.XX     |
| Correctness     | X/5   | 0.25   | X.XX     |
| Dependencies    | X/5   | 0.15   | X.XX     |
| Claims & Facts  | X/5   | 0.10   | X.XX     |
| **Total**       |       |        | **X.XX/5.0** |

## Confidence

- Evidence strength: Strong / Moderate / Weak
- Criterion clarity: Clear / Ambiguous
- Confidence level: X.XX → High (>4.5) / Medium (4.0–4.5) / Low (<4.0)

## Refinement Actions

[List specific improvements to implement, or "None required"]
```

## Scoring Scale

| Score | Meaning                                      |
|-------|----------------------------------------------|
| 5     | Exceeds requirements, genuinely exemplary    |
| 4     | Meets all requirements, very few minor gaps  |
| 3     | Meets basic requirements, minor issues       |
| 2     | Partially meets requirements, notable gaps   |
| 1     | Fails to meet requirements                   |

## Iteration Loop

If confidence is below the threshold for the complexity path:

1. Document specific issues found
2. Implement the highest-priority fixes
3. Re-run this checklist
4. Repeat until threshold is met or issues are explicitly accepted with rationale
