# Example 1: Voice Ramble → Structured Debugging Task

## Before: Raw Voice Ramble

```
"So um I was thinking we should probably look into that performance issue
we've been having with the dashboard because like users keep complaining
that it takes forever to load when there's a bunch of data and I think
maybe we could cache some stuff or optimize the SQL queries or something
because right now it's just way too slow and people are getting frustrated
you know and I'm not really sure if it's the database or the frontend
rendering or what but we definitely need to figure it out soon"
```

**Problems with this input:**
- Unstructured, conversational tone
- No clear task definition
- Missing context about tech stack
- No workflow or steps
- Vague solutions ("maybe cache" / "or something")
- No success criteria
- No skills or tools specified
- Missing all mandatory workflows

---

## After: Enhanced Structured Prompt

### Transformation Applied:

#### 1. Task Summary (Extracted from ramble)
```xml
<task_summary>
Optimize dashboard loading performance when displaying large datasets by
implementing caching strategies and query optimization to reduce load times
and improve user experience.
</task_summary>
```

**What Changed:**
- Voice ramble → Clear, concise goal statement
- "that performance issue" → "dashboard loading performance with large datasets"
- "maybe cache or optimize" → "implement caching strategies and query optimization"

#### 2. Context (Added structure)
```xml
<context>
<domain>Web Application Performance Optimization</domain>
<technical_context>
- Component: Dashboard with data visualization
- Issue: Slow loading with large datasets
- User impact: Extended wait times causing frustration
- Suspected causes: Database queries, frontend rendering, lack of caching
</technical_context>
<constraints>
- Must maintain data accuracy and consistency
- Should achieve sub-2-second load time
- Solution must be scalable to handle growing data
- Cannot break existing dashboard functionality
</constraints>
</context>
```

**What Changed:**
- Added domain classification
- Structured technical context from scattered mentions
- Inferred reasonable constraints from problem description

#### 3. Skills Inventory (Injected mandatory workflow)
```xml
<skills_inventory>
**MANDATORY: Complete before starting**

Relevant Skills:
- systematic-debugging: For structured root cause analysis
- serena: For code analysis of dashboard and query implementations

Action Required:
1. Use Skill tool to load: systematic-debugging
2. Use Skill tool to load: serena
3. Follow their guidance
</skills_inventory>
```

**What Changed:**
- Added MANDATORY skills inventory (missing from original)
- Detected relevant skills based on task type (performance debugging)
- Provided clear action items

#### 4. MCP Tools Inventory (Injected mandatory workflow)
```xml
<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Recommended MCP Tools:
- mcp__sequential-thinking__sequentialthinking: For systematic optimization analysis
- mcp__serena__get_symbols_overview: To understand dashboard code structure
- mcp__serena__find_symbol: To locate query functions and rendering logic
- mcp__serena__search_for_pattern: To find caching patterns or identify bottlenecks

Avoid:
- grep for code search (use mcp__serena__* instead)
- cat for file reading (use mcp__serena__get_symbols_overview instead)
</mcp_tools_inventory>
```

**What Changed:**
- Added MANDATORY MCP tools inventory (missing from original)
- Recommended specific Serena MCP tools for code analysis
- Recommended sequential-thinking for complex optimization analysis
- Specified bash tools to avoid

#### 5. Ultrathinking Framework (Detected complexity)
```xml
<thinking_framework>
**Use for complex multi-step problems requiring systematic reasoning**

WHEN TO USE:
- Performance optimization requires multiple investigation paths
- Multiple valid optimization approaches exist
- Trade-offs must be evaluated systematically

HOW TO USE:
1. Call mcp__sequential-thinking__sequentialthinking tool
2. Set thoughtNumber=1, estimate totalThoughts (8-12 for this task)
3. Think through investigation incrementally:
   - Thought 1: Analyze current implementation
   - Thought 2: Identify bottleneck (database vs frontend)
   - Thought 3: Evaluate caching strategy options
   - Thought 4: Evaluate query optimization options
   - Thought 5: Consider trade-offs
   - Continue as needed
</thinking_framework>
```

**What Changed:**
- Detected this as a complex optimization problem
- Added ultrathinking framework (completely missing from original)
- Provided specific thinking structure for this optimization task

#### 6. Mandatory Rules (Injected all 7 rules)
```xml
<mandatory_rules>
<rule id="1" priority="CRITICAL">
**NEVER write unit tests unless explicitly requested**
Application to this task: Focus on optimization implementation, not test creation.
</rule>

<rule id="2" priority="CRITICAL">
**NEVER propose code changes without reading the existing code first**
Application to this task: Read all dashboard and query code BEFORE proposing optimizations.
</rule>

<!-- Rules 3-7 with task-specific applications -->
</mandatory_rules>
```

**What Changed:**
- Added ALL 7 mandatory rules (completely missing from original)
- Applied each rule to this specific task
- Provided violation detection guidance

#### 7. Structured Workflow (Created 3-phase approach)
```xml
<workflow>
<phase_1>**Investigation & Root Cause Analysis**
1. Complete skills inventory (load systematic-debugging, serena)
2. Complete MCP tools inventory
3. Start sequential thinking session
4. Use Serena MCP to understand code
5. Gather evidence for hypotheses
6. Identify actual bottleneck
</phase_1>

<phase_2>**Solution Design**
1. Continue sequential thinking to evaluate solutions
2. Evaluate caching, query optimization, frontend optimization
3. Choose solution based on root cause
4. Design implementation
5. Verify design meets constraints
</phase_2>

<phase_3>**Implementation & Validation**
1. Read existing code with Serena (Rule #2)
2. Implement optimization incrementally
3. If caching: Define invalidation strategy
4. If queries: Optimize and add indexes
5. If frontend: Implement virtualization
6. Validate with measurements
7. Document optimization
</phase_3>
</workflow>
```

**What Changed:**
- Vague idea ("maybe cache or optimize") → 3-phase structured workflow
- No steps → Clear, executable steps in each phase
- No investigation plan → Systematic root cause analysis
- No implementation guide → Detailed implementation steps

#### 8. Success Criteria (Added measurable outcomes)
```xml
<success_criteria>
- Root cause identified with evidence
- Dashboard load time reduced to under 2 seconds
- Solution implemented without breaking functionality
- Performance improvement verified with before/after metrics
- Optimization follows existing code patterns
- Solution is scalable
- Implementation documented
</success_criteria>
```

**What Changed:**
- No success criteria → 7 measurable outcomes
- "way too slow" → "under 2 seconds" (specific target)
- No verification → "verified with before/after metrics"

#### 9. Execution Trigger (Added clear starting point)
```xml
<execution_trigger>
You are now configured to optimize dashboard performance following all
guidelines, mandatory workflows, and rules specified above.

Begin by completing the skills inventory (load systematic-debugging and serena),
then complete the MCP tools inventory, and finally start a sequential thinking
session to systematically investigate the performance bottleneck.
</execution_trigger>
```

**What Changed:**
- No starting point → Clear first steps
- Reinforces mandatory workflow order

---

## Summary of Transformation

### Structure Added:
- ✅ Clear task summary (1-2 sentences)
- ✅ Organized context (domain, technical, constraints)
- ✅ Skills inventory (systematic-debugging, serena)
- ✅ MCP tools inventory (sequential-thinking, Serena MCP)
- ✅ Ultrathinking framework (for complexity)
- ✅ All 7 mandatory rules
- ✅ 3-phase structured workflow
- ✅ Measurable success criteria
- ✅ Clear execution trigger

### Guidelines Applied:
- ✅ Opus 4.5: Read code first, investigate before solving, avoid overengineering
- ✅ Sonnet 4.5: Systematic approach, context awareness
- ✅ Claude Code: Skills usage, MCP tools, systematic debugging

### From Ramble to Production:
| Aspect | Before | After |
|--------|--------|-------|
| Structure | None (voice ramble) | 9-section XML prompt |
| Task clarity | "that performance issue" | "Optimize dashboard loading with large datasets" |
| Workflows | None | 4 mandatory workflows |
| Tools | None mentioned | Serena MCP, sequential-thinking specified |
| Success | Vague ("figure it out") | 7 measurable criteria |
| Actionability | Low (no steps) | High (3-phase workflow) |
| Guideline compliance | 0% | 100% (Opus 4.5, Sonnet 4.5, Claude Code) |

---

## Key Enhancements

### 1. From Vague to Specific
- **Before:** "that performance issue"
- **After:** "dashboard loading performance when displaying large datasets"

### 2. From Speculation to Investigation
- **Before:** "maybe we could cache stuff or optimize SQL queries or something"
- **After:** Systematic 3-phase investigation with sequential thinking to identify root cause before choosing solution

### 3. From No Workflows to Complete Workflows
- **Before:** No mention of skills, tools, or systematic processes
- **After:** Skills inventory, MCP tools inventory, ultrathinking framework, all 7 mandatory rules

### 4. From No Success Criteria to Measurable Outcomes
- **Before:** "definitely need to figure it out soon"
- **After:** 7 specific, measurable criteria including performance targets, validation requirements, and documentation

### 5. From Uncertainty to Structure
- **Before:** "I'm not really sure if it's the database or the frontend rendering or what"
- **After:** Systematic hypothesis generation and testing via sequential thinking to identify actual bottleneck

---

## Why This Transformation Matters

**For the User:**
- Clear understanding of what needs to be done
- Systematic approach prevents guessing
- Measurable outcomes define success
- Skills and tools provide proven patterns

**For Claude:**
- Structured workflow ensures nothing is missed
- Mandatory rules prevent common mistakes
- Guidelines ensure high-quality approach
- Actionable steps enable immediate execution

**For the Project:**
- Solution addresses root cause, not symptoms
- Implementation follows best practices
- Performance improvements are verified
- Documentation supports future maintenance

---

**Result:** Voice ramble transformed into production-ready debugging prompt following Opus 4.5, Sonnet 4.5, and Claude Code best practices.
