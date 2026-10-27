# Research Strategies Reference

How to research weak sections effectively — source priority, execution patterns, conflict resolution, and evidence quality.

## Source Priority Order

Always prefer earlier sources. Move to later sources only when earlier ones cannot close the gap.

### Priority 1: Codebase Analysis (Most Trusted)
The repo itself is the most authoritative source for "how things work here."

**When to use:** Decision rationale, implementation patterns, sequencing, system impact
**How:**
```bash
# Find patterns and conventions
grep -r "pattern_name" --include="*.ts" -l
find . -name "*.swift" -path "*/Auth/*"

# Understand architecture
cat README.md
cat CLAUDE.md 2>/dev/null
cat ARCHITECTURE.md 2>/dev/null
ls -la src/ lib/ app/

# Trace dependencies
grep -r "import.*ModuleName" --include="*.ts" -l
```

**MCP tools (prefer when available):**
- Serena MCP: `find_symbol`, `get_symbols_overview`, `find_referencing_symbols`
- Context7 MCP: Library documentation lookup

### Priority 2: Project Documentation
README, architecture docs, ADRs (Architecture Decision Records), and inline documentation.

**When to use:** Understanding design decisions, finding documented conventions, verifying requirements trace
**How:** Read files in `docs/`, `doc/`, `.github/`, root-level `.md` files

### Priority 3: Origin Documents
The brief, spec, roadmap, or ticket that spawned the plan being deepened.

**When to use:** Verifying scope boundaries, checking requirements fidelity, confirming design intent
**How:** Follow `origin:` frontmatter or `@file` references in the document

### Priority 4: Official Documentation
Framework docs, API references, library guides. The authoritative external source.

**When to use:** Validating technical decisions, checking API behavior, confirming best practices
**How:**
```bash
# Web search for official docs
# Prefer: docs.framework.com, developer.apple.com, official GitHub repos
# Avoid: Medium posts, StackOverflow answers, outdated tutorials
```

**MCP tools:**
- Context7 MCP: `resolve-library-id` → `query-docs` for up-to-date library documentation
- Web search: Target official documentation sites

### Priority 5: External Best Practices
Industry patterns, OWASP guidelines, security benchmarks, performance references.

**When to use:** Risk treatment, security hardening, performance targets, when official docs don't address the specific concern
**How:** Web search targeting authoritative sources (OWASP, NIST, RFC specifications, vendor security guides)

---

## Research Execution Patterns

### Pattern 1: Quick Lookup (1 source, 1 search)
**Use when:** A single decision needs rationale, or one fact needs verification.
**Effort:** 1 tool call.
**Example:** "Does bcrypt have a max password length?" → search official bcrypt docs.

### Pattern 2: Repo-Grounded Research (2-3 searches + code reading)
**Use when:** Understanding how a pattern is already used in the codebase before recommending an approach.
**Effort:** 2-4 tool calls.
**Example:** "How does this repo handle auth already?" → grep for auth patterns, read existing auth files, check middleware.

### Pattern 3: Comparative Research (3-5 searches)
**Use when:** A key decision has multiple valid options and the plan doesn't explain why one was chosen.
**Effort:** 3-6 tool calls.
**Example:** "JWT vs session cookies — which fits this architecture?" → check existing auth, search official framework auth docs, compare approaches for this stack.

### Pattern 4: Deep Domain Research (5+ searches + documentation reading)
**Use when:** High-risk section in a domain requiring current, authoritative guidance (security, compliance, migration safety).
**Effort:** 5-10 tool calls.
**Example:** "Is this migration strategy safe for production with 10M rows?" → check migration tooling docs, search for batch migration patterns, review rollback strategies, check existing migration history.

### Choosing the Right Pattern
- **Quick Lookup** for score 2 sections with one clear gap
- **Repo-Grounded** for score 2-3 sections needing codebase context
- **Comparative** for Key Decisions sections lacking tradeoff analysis
- **Deep Domain** for score 4+ sections in high-risk domains

---

## Research Output Format

For each finding, capture:

```xml
<research_finding section="[section being deepened]" source_type="[codebase|project_docs|origin|official_docs|external]">
  <finding>[What was discovered]</finding>
  <evidence>[Specific evidence — file path, doc quote, search result]</evidence>
  <plan_impact>[How this changes or strengthens the plan section]</plan_impact>
  <confidence level="high|medium|low">[Why this confidence level]</confidence>
</research_finding>
```

---

## Conflict Resolution

When research findings contradict each other:

1. **Repo evidence vs generic advice** → Repo wins. The codebase is the ground truth for "how things work here."
2. **Official docs vs blog posts** → Official docs win. Blog posts may be outdated or opinionated.
3. **Two official sources conflict** → Record the tradeoff explicitly in the plan. Don't pretend the conflict doesn't exist.
4. **Origin document vs research** → Surface as an open question. Don't silently override the product owner's intent.

---

## Evidence Quality Standards

### High Quality
- Specific file path with line reference: "src/auth/middleware.ts uses the AuthProvider protocol pattern (line 42-67)"
- Official documentation with version: "Next.js 15 docs recommend App Router for new projects (as of 2026)"
- Concrete measurement: "Current migration scripts process ~50k rows/minute based on batch-003 logs"

### Low Quality — Upgrade Before Using
- Generic claim: "It's best practice to use JWT" → WHY? For THIS architecture? Says WHO?
- Undated blog post: "This Medium post recommends..." → When? Still current? Official?
- Assumed behavior: "The framework probably handles this" → Verify. Read the actual code or docs.

### Unacceptable — Do Not Use
- "I think..." without evidence
- StackOverflow answers from 3+ years ago without verification
- Recommendations that contradict the codebase's existing patterns without explaining why deviation is warranted
