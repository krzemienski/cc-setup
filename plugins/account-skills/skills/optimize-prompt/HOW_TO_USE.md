# Optimize Prompt - Comprehensive User Guide

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Input Types](#input-types)
4. [Enhancement Process](#enhancement-process)
5. [Output Structure](#output-structure)
6. [Complete Examples](#complete-examples)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**Optimize Prompt** transforms raw, unstructured input into production-ready prompts that follow Opus 4.5 and Sonnet 4.5 best practices with mandatory workflow injection.

### What This Skill Does

**Accepts:**
- Voice rambles (transcribed speech)
- Semi-structured ideas
- File path requests
- Incomplete prompts

**Produces:**
- Structured XML prompts
- Mandatory workflows (skills, MCP tools, ultrathinking, rules)
- Clear task summaries
- Phased workflows
- Success criteria

**Does NOT:**
- Execute the prompt (only creates it)
- Implement code (only structures the task)
- Make architectural decisions (provides framework)

---

## Quick Start

### Basic Invocation

**Simple Enhancement:**
```
"Enhance this prompt: [your raw input]"
```

**With File Output:**
```
"Enhance this prompt and save to prompts/task.xml: [your raw input]"
```

**With Clarification:**
If input is ambiguous, the skill will ask 1-2 questions:
- What's the primary goal?
- What context is important?
- Are there specific constraints?

### 30-Second Examples

**Example 1: Voice to Structured**
```
Input: "So I was thinking we should look at that auth bug"

Output: Structured prompt with:
- Task: Debug authentication service
- Skills: systematic-debugging, serena
- MCP tools: mcp__sequential-thinking
- Workflow: Investigation → Root cause → Fix
- All mandatory rules
```

**Example 2: File Path to Full Task**
```
Input: "Analyze src/auth/login.ts"

Output: Structured prompt with:
- Task: Code analysis of login.ts
- Skills: serena
- MCP tools: mcp__serena__get_symbols_overview
- Workflow: Read → Analyze → Report
- Rule emphasis: Read code first (Rule #2)
```

---

## Input Types

### Type 1: Voice Rambles

**Characteristics:**
- Unstructured, conversational
- Filler words ("um", "like", "you know")
- Stream of consciousness
- Missing technical details

**Example Input:**
```
"Okay so like we've been having this issue with the dashboard
where it's super slow when there's a lot of data and I think
maybe we could cache some stuff or optimize the queries or
something because users are complaining about it"
```

**What Gets Enhanced:**
- Voice ramble → Clear task summary
- Vague idea ("optimize queries or something") → Specific investigation plan
- No structure → Phased workflow with ultrathinking
- Missing workflows → Skills + MCP tools inventories added
- No success criteria → Measurable performance goals

---

### Type 2: Semi-Structured Ideas

**Characteristics:**
- Has some structure but incomplete
- Missing context or constraints
- No mandatory workflows
- Unclear success criteria

**Example Input:**
```
"Build a new feature for exporting user reports to PDF with
custom branding and filtering options"
```

**What Gets Enhanced:**
- Incomplete idea → Full context (domain, tech stack, constraints)
- No workflows → Skills inventory + MCP tools inventory
- Vague feature → Specific implementation phases
- No rules → All 7 mandatory rules added
- Missing criteria → Clear success metrics

---

### Type 3: File Path Requests

**Characteristics:**
- Simple file reference
- Single sentence
- Missing entire task structure

**Example Input:**
```
"Check components/Dashboard/MetricsPanel.tsx"
```

**What Gets Enhanced:**
- File path → Full code analysis task
- No context → Component analysis framework
- Missing workflow → Read → Analyze → Report flow
- No tools specified → Serena MCP tools recommended
- Single step → Multi-phase analysis workflow

---

### Type 4: Incomplete Prompts

**Characteristics:**
- Some structure exists
- Missing mandatory workflows
- No skills/MCP tools inventories
- Missing critical rules

**Example Input:**
```
"Debug the authentication service - tokens are expiring
too early in the production environment"
```

**What Gets Enhanced:**
- Partial prompt → Complete with all sections
- No workflows → All mandatory workflows added
- Missing investigation → Sequential thinking framework
- No skills → systematic-debugging, serena identified
- No success criteria → Clear debugging goals

---

## Enhancement Process

### Phase 1: Input Analysis

**Step 1: Detect Input Type**
```
Voice ramble? → Look for conversational patterns, filler words
Semi-structured? → Look for partial structure, missing sections
File path? → Look for file references
Incomplete prompt? → Look for missing mandatory workflows
```

**Step 2: Extract Core Intent**
```
Questions Answered:
- What is the user trying to accomplish?
- What type of task? (analysis, feature, bug fix, optimization)
- What's the complexity level? (simple, moderate, complex)
- What context is implied but unstated?
- What constraints should be considered?
```

**Step 3: Identify Task Category**
```
Categories:
- Code Analysis: Understand existing code
- Feature Implementation: Build something new
- Bug Fix/Debugging: Diagnose and fix issues
- Refactoring: Improve code structure
- Optimization: Improve performance
- Documentation: Create or update docs
```

### Phase 2: Guideline Application

**Apply Relevant Guidelines by Task Type:**

**For Code Analysis:**
```
Opus 4.5:
- Code exploration REQUIRED (Rule #2: read before changing)
- Investigate before answering (minimize hallucinations)

Serena MCP:
- Use find_symbol to locate code elements
- Use get_symbols_overview for file structure
- Use find_referencing_symbols for usage tracing

Mandatory:
- Skills inventory (check for serena, systematic-debugging)
- MCP tools inventory (recommend Serena over grep/find)
```

**For Feature Implementation:**
```
Opus 4.5:
- Be explicit with requirements
- Add context (domain, constraints)
- Avoid overengineering (simplest solution that works)

Sonnet 4.5:
- Parallel tool calling when possible
- Balanced verbosity

Mandatory:
- Skills inventory
- MCP tools inventory
- Read existing code first (Rule #2)
- NEVER write tests unless explicitly asked (Rule #1)
```

**For Debugging:**
```
Opus 4.5:
- Minimize hallucinations - investigate first
- Long-horizon reasoning for complex bugs

Ultrathinking:
- REQUIRED for complex debugging (Rule #7)
- Sequential thinking via mcp__sequential-thinking

Serena MCP:
- Use find_referencing_symbols to trace usage
- Analyze code structure systematically

Mandatory:
- Skills inventory (systematic-debugging)
- MCP tools inventory (sequential-thinking, Serena)
- All debugging rules enforced
```

### Phase 3: Workflow Injection

**For EVERY enhanced prompt:**

1. **Skills Inventory Template** (filled with detected skills)
2. **MCP Tools Inventory Template** (filled with recommended tools)
3. **Ultrathinking Framework** (if task is complex)
4. **All 7 Mandatory Rules** (always included)

**Skill Detection Logic:**
```
IF task involves code analysis OR refactoring:
  → Recommend: serena, systematic-debugging

IF task involves feature implementation:
  → Recommend: test-driven-development (ONLY if tests explicitly requested)

IF task involves git operations:
  → Recommend: git-commit-helper

IF task involves AWS/cloud:
  → Recommend: aws-solution-architect

IF task involves content/research:
  → Recommend: content-trend-researcher

IF task involves creating prompts:
  → Recommend: prompt-factory
```

**MCP Tool Detection Logic:**
```
IF task involves code analysis:
  → Recommend: mcp__serena__* tools
  → Specifically: find_symbol, get_symbols_overview, find_referencing_symbols

IF task involves file operations:
  → Recommend: mcp__filesystem__* tools
  → Instead of: cat, sed, awk, find

IF task involves git:
  → Recommend: mcp__git__* tools
  → Instead of: raw git commands

IF task is complex/architectural:
  → Recommend: mcp__sequential-thinking__sequentialthinking
```

### Phase 4: Structure & Format

**Output XML Structure:**

```xml
<enhanced_prompt>
  <task_summary>...</task_summary>
  <context>...</context>
  <skills_inventory>...</skills_inventory>
  <mcp_tools_inventory>...</mcp_tools_inventory>
  <thinking_framework>...</thinking_framework>
  <mandatory_rules>...</mandatory_rules>
  <workflow>
    <phase_1>...</phase_1>
    <phase_2>...</phase_2>
    <phase_3>...</phase_3>
  </workflow>
  <success_criteria>...</success_criteria>
  <execution_trigger>...</execution_trigger>
</enhanced_prompt>
```

### Phase 5: Quality Validation

**7-Point Validation Checklist:**

1. ✓ **Completeness**
   - Task summary present?
   - Context provided?
   - All mandatory workflows included?
   - Workflow defined?
   - Success criteria specified?

2. ✓ **Guideline Compliance**
   - Opus 4.5 principles applied?
   - Sonnet 4.5 principles applied?
   - Claude Code best practices applied?

3. ✓ **Mandatory Workflows**
   - Skills inventory template present and filled?
   - MCP tools inventory present and filled?
   - Ultrathinking framework (if needed)?
   - All 7 mandatory rules present?

4. ✓ **Skill Detection**
   - Relevant skills identified correctly?
   - Skills listed in inventory section?

5. ✓ **Tool Detection**
   - Relevant MCP tools identified?
   - Tools listed in MCP inventory section?
   - MCP tools preferred over bash?

6. ✓ **Actionability**
   - Workflow has clear, executable steps?
   - No ambiguous instructions?
   - Success criteria measurable?

7. ✓ **XML Validity**
   - All tags properly opened/closed?
   - Proper nesting?
   - No syntax errors?

---

## Output Structure

### Section Breakdown

#### 1. Task Summary
```xml
<task_summary>
Clear, concise description of what needs to be accomplished.
Should be 1-2 sentences, specific and actionable.
</task_summary>
```

**Example:**
```xml
<task_summary>
Optimize dashboard loading performance when displaying large datasets by
implementing query caching and query optimization strategies.
</task_summary>
```

#### 2. Context
```xml
<context>
<domain>[Problem domain: web dev, data science, etc.]</domain>
<technical_context>[Technologies, frameworks, patterns involved]</technical_context>
<constraints>[Limitations, requirements, standards to follow]</constraints>
</context>
```

**Example:**
```xml
<context>
<domain>Web Application Performance Optimization</domain>
<technical_context>
- Frontend: React dashboard with data visualization
- Backend: Node.js with PostgreSQL database
- Current issue: 5+ second load time with 10k+ records
</technical_context>
<constraints>
- Must maintain data accuracy
- Should achieve sub-1-second load time
- Solution must be scalable to 100k+ records
- Cannot change database schema drastically
</constraints>
</context>
```

#### 3. Skills Inventory
```xml
<skills_inventory>
**MANDATORY: Complete before starting**

Available Skills to Check:
- [skill-1]
- [skill-2]

Relevant Skills for This Task:
- [skill-name]: [why it's relevant]

Action Required:
1. Use Skill tool to load: [skill-1]
2. Use Skill tool to load: [skill-2]
3. Follow their guidance
</skills_inventory>
```

#### 4. MCP Tools Inventory
```xml
<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Recommended MCP Tools:
- [mcp-tool-1]: [purpose]
- [mcp-tool-2]: [purpose]

Avoid:
- [bash-equivalent]: [why to avoid]
</mcp_tools_inventory>
```

#### 5. Thinking Framework
```xml
<thinking_framework>
**REQUIRED: Use sequential thinking for [reason]**

1. Call mcp__sequential-thinking__sequentialthinking
2. Systematically analyze: [aspects]
3. Generate hypothesis
4. Verify against constraints
5. Propose solution
</thinking_framework>
```

#### 6. Mandatory Rules
```xml
<mandatory_rules>
[All 7 rules included with explanations and violation detection]
</mandatory_rules>
```

#### 7. Workflow
```xml
<workflow>
<phase_1>
**[Phase Name]**
1. [Step 1]
2. [Step 2]
...
</phase_1>

<phase_2>
**[Phase Name]**
[Depends on phase 1 results]
...
</phase_2>

<phase_3>
**[Phase Name]**
[Final implementation/validation]
...
</phase_3>
</workflow>
```

#### 8. Success Criteria
```xml
<success_criteria>
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Verification method]
</success_criteria>
```

#### 9. Execution Trigger
```xml
<execution_trigger>
You are now configured to execute this task following all guidelines,
mandatory workflows, and rules specified above.

Begin by completing the skills inventory, then proceed through each phase.
</execution_trigger>
```

---

## Complete Examples

### Example 1: Voice Ramble → Debugging Task

**Input:**
```
"So we've been getting complaints from users that the app crashes
when they try to upload large files like over 50 megs and I think
it might be a memory thing or maybe timeout but I'm not really sure"
```

**Enhanced Output:**
```xml
<enhanced_prompt>

<task_summary>
Debug application crashes occurring when users upload files larger than 50MB,
investigating memory issues and timeout configurations as potential root causes.
</task_summary>

<context>
<domain>File Upload System Debugging</domain>
<technical_context>
- User-reported: App crashes with files >50MB
- Suspected causes: Memory issues, timeouts
- Environment: Production application (stack unknown - investigate)
</technical_context>
<constraints>
- Must fix without breaking existing upload functionality
- Solution should handle files up to 100MB+ safely
- Should not significantly impact server resources
</constraints>
</context>

<skills_inventory>
**MANDATORY: Complete before starting**

Available Skills to Check:
- systematic-debugging
- serena

Relevant Skills for This Task:
- systematic-debugging: Structured approach to root cause analysis
- serena: Code analysis for upload handling logic

Action Required:
1. Use Skill tool to load: systematic-debugging
2. Use Skill tool to load: serena
3. Follow systematic debugging workflow
</skills_inventory>

<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Recommended MCP Tools:
- mcp__sequential-thinking__sequentialthinking: For systematic bug investigation
- mcp__serena__get_symbols_overview: Understand upload code structure
- mcp__serena__find_symbol: Locate upload handlers
- mcp__serena__search_for_pattern: Find memory/timeout configs

Avoid:
- Using grep for code search (use Serena instead)
- Using find for file discovery (use Serena)
</mcp_tools_inventory>

<thinking_framework>
**REQUIRED: Use sequential thinking for systematic debugging**

This is a complex debugging task requiring hypothesis generation and testing.

1. Call mcp__sequential-thinking__sequentialthinking
2. Generate hypotheses systematically:
   - Hypothesis 1: Memory limit exceeded on server
   - Hypothesis 2: Request timeout too short
   - Hypothesis 3: Client-side memory issue
   - Hypothesis 4: File validation logic failing
3. Test each hypothesis with evidence
4. Identify root cause
5. Propose fix
</thinking_framework>

<mandatory_rules>
<rule id="1" priority="CRITICAL">
**NEVER write unit tests unless explicitly requested**
Reason: User wants bug fixed, not test coverage
</rule>

<rule id="2" priority="CRITICAL">
**NEVER propose changes without reading code first**
Tools: Use Serena MCP to read upload handling code
Action: Read file upload logic before proposing fixes
</rule>

<rule id="3" priority="HIGH">
**ALWAYS use Serena MCP for code analysis**
Reason: Need to understand upload implementation
</rule>

<rule id="4" priority="HIGH">
**ALWAYS complete skills inventory**
Action: Load systematic-debugging and serena
</rule>

<rule id="5" priority="HIGH">
**ALWAYS complete MCP tools inventory**
Action: Use sequential-thinking and Serena tools
</rule>

<rule id="6" priority="MEDIUM">
**ALWAYS use ultrathinking for complex problems**
Applied: Using sequential thinking for debugging
</rule>

<rule id="7" priority="MEDIUM">
**ALWAYS use sequential thinking for debugging**
Applied: This IS a debugging task - using sequential thinking
</rule>
</mandatory_rules>

<workflow>
<phase_1>
**Investigation & Hypothesis Generation**

1. Complete skills inventory (load systematic-debugging, serena)
2. Complete MCP tools inventory
3. Start sequential thinking session (mcp__sequential-thinking)
4. Generate hypotheses:
   - Memory limit hypothesis
   - Timeout hypothesis
   - Client-side hypothesis
   - Validation hypothesis
5. Use Serena MCP to read upload handling code:
   - mcp__serena__search_for_pattern: Find "upload" patterns
   - mcp__serena__get_symbols_overview: Understand file structure
   - mcp__serena__find_symbol: Locate upload handler functions
6. Gather evidence for each hypothesis:
   - Check server memory limits
   - Check timeout configurations
   - Review client-side upload code
   - Examine file validation logic
</phase_1>

<phase_2>
**Root Cause Identification**

1. Test each hypothesis with sequential thinking:
   - thoughtNumber=1: Analyze memory limit evidence
   - thoughtNumber=2: Analyze timeout evidence
   - thoughtNumber=3: Analyze client-side evidence
   - thoughtNumber=4: Synthesize findings
2. Identify root cause based on evidence (don't assume)
3. Verify root cause explains the 50MB threshold
4. Document findings
</phase_2>

<phase_3>
**Solution Design & Implementation**

1. Based on identified root cause, design fix:
   - If memory: Increase limits or implement streaming uploads
   - If timeout: Adjust timeout or implement chunked uploads
   - If client: Fix client-side memory handling
   - If validation: Fix or remove problematic validation
2. Read existing implementation with Serena (Rule #2)
3. Implement fix following existing patterns
4. Test with files: 10MB, 50MB, 75MB, 100MB
5. Verify no regression on smaller files
6. DO NOT write tests unless user explicitly asks (Rule #1)
7. Document the fix and configuration changes
</phase_3>
</workflow>

<success_criteria>
- Root cause identified with evidence
- Fix implemented without breaking existing uploads
- Files up to 100MB upload successfully
- No crashes or errors during upload
- Solution verified with multiple file sizes
- Performance remains acceptable
</success_criteria>

<execution_trigger>
You are now configured to debug this file upload crash issue following all
guidelines, mandatory workflows, and systematic debugging rules.

Begin by completing the skills inventory, loading systematic-debugging and serena,
then start a sequential thinking session for hypothesis generation.
</execution_trigger>

</enhanced_prompt>
```

**Transformation Summary:**
- Voice ramble → Structured debugging task
- Vague suspicion → Systematic hypothesis generation
- No workflow → 3-phase investigation with sequential thinking
- Missing tools → Serena MCP + sequential-thinking recommended
- No success criteria → Clear verification steps
- All 7 mandatory rules included

---

### Example 2: File Path → Code Analysis

**Input:**
```
"Analyze src/services/PaymentProcessor.ts"
```

**Enhanced Output:**
```xml
<enhanced_prompt>

<task_summary>
Perform comprehensive code analysis of the PaymentProcessor service to understand
its structure, dependencies, functionality, and identify any potential issues or
improvement opportunities.
</task_summary>

<context>
<domain>Code Analysis - Payment Processing Service</domain>
<technical_context>
- Target: src/services/PaymentProcessor.ts
- Language: TypeScript
- Domain: Payment processing (critical functionality)
</technical_context>
<constraints>
- Analysis only - no changes unless requested
- Must understand complete service functionality
- Should identify security considerations
- Payment processing requires careful handling
</constraints>
</context>

<skills_inventory>
**MANDATORY: Complete before starting**

Available Skills to Check:
- serena

Relevant Skills for This Task:
- serena: Symbol-level code analysis capabilities

Action Required:
1. Use Skill tool to load: serena
2. Follow Serena's code analysis workflow
</skills_inventory>

<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Recommended MCP Tools:
- mcp__serena__get_symbols_overview: Understand PaymentProcessor structure
- mcp__serena__find_symbol: Find specific methods/classes
- mcp__serena__find_referencing_symbols: See where PaymentProcessor is used
- mcp__serena__search_for_pattern: Find patterns (error handling, validation, etc.)

Avoid:
- cat/grep for reading (use Serena instead)
- find for searching (use Serena instead)
- Manual parsing (Serena provides structure)
</mcp_tools_inventory>

<mandatory_rules>
<rule id="1" priority="CRITICAL">
**NEVER write unit tests unless explicitly requested**
Reason: Task is analysis only
</rule>

<rule id="2" priority="CRITICAL">
**NEVER propose changes without reading code first**
Applied: This task IS about reading code
Action: Use Serena to thoroughly read PaymentProcessor.ts
</rule>

<rule id="3" priority="HIGH">
**ALWAYS use Serena MCP for code analysis**
Applied: Using Serena MCP for this entire task
</rule>

<rule id="4" priority="HIGH">
**ALWAYS complete skills inventory**
Action: Load serena skill
</rule>

<rule id="5" priority="HIGH">
**ALWAYS complete MCP tools inventory**
Action: Use Serena MCP tools listed above
</rule>

<rule id="6" priority="MEDIUM">
**ALWAYS use ultrathinking for complex problems**
Note: Not needed for straightforward code analysis
</rule>

<rule id="7" priority="MEDIUM">
**ALWAYS use sequential thinking for debugging**
Note: This is analysis, not debugging
</rule>
</mandatory_rules>

<workflow>
<phase_1>
**Service Structure Analysis**

1. Complete skills inventory (load serena)
2. Complete MCP tools inventory
3. Use mcp__serena__get_symbols_overview for src/services/PaymentProcessor.ts
4. Identify:
   - Class structure and inheritance
   - Public methods and their purposes
   - Private methods and helpers
   - Properties and their types
   - Dependencies and imports
</phase_1>

<phase_2>
**Functionality Analysis**

1. Use mcp__serena__find_symbol to examine each public method
2. Understand payment flow:
   - How payments are initiated
   - Validation logic
   - Error handling patterns
   - Success/failure handling
3. Identify security-critical code:
   - Sensitive data handling
   - Authentication/authorization
   - Input validation
   - Error message exposure
4. Map dependencies:
   - External services (payment gateways, etc.)
   - Internal services
   - Utility functions
</phase_2>

<phase_3>
**Usage Analysis & Reporting**

1. Use mcp__serena__find_referencing_symbols on PaymentProcessor
2. Identify all usage locations
3. Understand usage patterns:
   - How is it instantiated?
   - Which methods are most used?
   - Are there edge cases in usage?
4. Compile comprehensive analysis report including:
   - Service structure overview
   - Payment flow documentation
   - Security considerations identified
   - Dependencies mapped
   - Usage patterns documented
   - Potential improvement opportunities (if any)
   - Code quality observations
</phase_3>
</workflow>

<success_criteria>
- Complete understanding of PaymentProcessor structure
- All public methods documented with purposes
- Payment flow clearly mapped
- Security considerations identified
- Dependencies fully documented
- Usage patterns understood
- Comprehensive analysis report provided
</success_criteria>

<execution_trigger>
You are now configured to analyze PaymentProcessor.ts following all guidelines
and using Serena MCP tools exclusively for code analysis.

Begin by completing the skills inventory, loading serena, then use
get_symbols_overview to start the analysis.
</execution_trigger>

</enhanced_prompt>
```

**Transformation Summary:**
- Simple file path → Full code analysis task
- No structure → 3-phase analysis workflow
- No tools → Serena MCP tools specified
- No success criteria → Clear analysis deliverables
- All mandatory rules included (with appropriate applicability notes)

---

## Advanced Usage

### File Output

**Save enhanced prompt to file:**
```
"Enhance and save to prompts/optimize-dashboard.xml:
Fix dashboard performance with large datasets"
```

**Output location:**
```
prompts/optimize-dashboard.xml
```

**Benefits:**
- Reusable prompts for repeated tasks
- Team distribution
- Version control
- Template library building

### Batch Enhancement

**Enhance multiple inputs:**
```
"Enhance these prompts and save to prompts/ directory:
1. Debug authentication timeout
2. Optimize SQL queries
3. Add user export feature"
```

**Outputs:**
```
prompts/debug-auth.xml
prompts/optimize-sql.xml
prompts/user-export.xml
```

### Custom Clarification

**When skill asks for clarification:**
```
Skill: "What's the primary goal for this task?"
You: "Improve dashboard load time from 5s to under 1s"

Skill: "What constraints should I consider?"
You: "Cannot change database schema, must stay under budget"
```

**Result:** More targeted enhancement with specific context

---

## Best Practices

### 1. Provide Context Upfront

**❌ Minimal Context:**
```
"Fix the bug"
```

**✅ Rich Context:**
```
"Debug authentication service in production where user tokens
are expiring after 5 minutes instead of the configured 30 minutes"
```

**Impact:** Rich context = better skill detection, better tool recommendations, clearer success criteria

### 2. Include Constraints

**❌ No Constraints:**
```
"Make the dashboard faster"
```

**✅ With Constraints:**
```
"Optimize dashboard to load in under 1 second with 10k records,
without changing the database schema, staying under $500/month AWS budget"
```

**Impact:** Constraints guide architectural decisions and solution design

### 3. Be Specific About Goals

**❌ Vague Goal:**
```
"Improve the code"
```

**✅ Specific Goal:**
```
"Refactor the payment processing service to reduce cyclomatic complexity
and improve testability while maintaining backward compatibility"
```

**Impact:** Specific goals = measurable success criteria

### 4. Trust the Mandatory Workflows

**Don't skip:**
- Skills inventory (loads proven patterns)
- MCP tools inventory (uses better tools)
- Ultrathinking (prevents premature solutions)
- Mandatory rules (prevents common mistakes)

**Why:** These workflows are based on Opus 4.5, Sonnet 4.5, and Claude Code best practices.

### 5. Use File Output for Reusability

**For repeated tasks:**
```
"Enhance and save to prompts/weekly-review.xml:
Analyze this week's git commits and summarize changes"
```

**Benefits:**
- Consistent workflow for recurring tasks
- Share with team
- Version control
- Template library

### 6. Leverage Skill Detection

**The skill automatically detects:**
- serena for code analysis
- systematic-debugging for debugging
- test-driven-development for testing (only if explicitly requested)
- aws-solution-architect for AWS tasks
- prompt-factory for prompt creation

**Result:** You get specialized guidance automatically

### 7. Trust MCP Tool Recommendations

**The skill prefers:**
- mcp__serena__* over grep/find/cat
- mcp__filesystem__* over bash file ops
- mcp__git__* over raw git commands
- mcp__sequential-thinking for complex problems

**Why:** MCP tools are more reliable, powerful, and context-aware

---

## Troubleshooting

### Issue: Enhancement Too Generic

**Symptom:** Output lacks specific guidance

**Cause:** Input too vague

**Solution:** Provide more context
```
Before: "Fix the problem"
After: "Debug memory leak in Node.js service causing OOM errors
in production after 6 hours of uptime"
```

### Issue: Wrong Skills Detected

**Symptom:** Skill recommends irrelevant skills

**Cause:** Unclear task type

**Solution:** Be explicit about task category
```
Before: "Look at the code"
After: "Perform security audit of authentication code"
```

### Issue: Missing Ultrathinking

**Symptom:** Complex task without sequential thinking framework

**Cause:** Complexity not detected

**Solution:** Indicate complexity explicitly
```
Before: "Refactor the app"
After: "Refactor monolithic application to microservices architecture,
maintaining backward compatibility while migrating incrementally"
```

### Issue: Output Too Verbose

**Symptom:** Enhanced prompt is excessively long

**Cause:** Multiple concerns in single input

**Solution:** Break into separate enhancements
```
Instead of: "Fix bugs A, B, and C, add features X and Y, refactor Z"
Do: Enhance each separately for focused prompts
```

### Issue: Mandatory Rules Not Applicable

**Symptom:** Some rules seem irrelevant to task

**Note:** All 7 rules are ALWAYS included. Some may not apply to specific tasks but are included for completeness and consistency.

**Example:** Rule #1 (no tests) always included even for analysis tasks where tests aren't relevant.

---

## Quick Reference

### Input Type Detection

| Input Characteristic | Detected As | Enhancement Applied |
|----------------------|-------------|---------------------|
| Conversational, filler words | Voice ramble | Structure + workflows + clarity |
| Partial structure | Semi-structured | Complete missing sections |
| File path only | File path request | Full analysis workflow |
| Missing workflows | Incomplete prompt | Add all mandatory workflows |

### Task Type Guidelines

| Task Type | Opus 4.5 | Sonnet 4.5 | Skills | MCP Tools |
|-----------|----------|------------|--------|-----------|
| Code Analysis | Read first, investigate | Context aware | serena | Serena MCP |
| Feature | Explicit, context, avoid overengineering | Parallel tools | - | sequential-thinking |
| Debugging | Investigate, long-horizon | Balanced verbosity | systematic-debugging | sequential-thinking, Serena |
| Optimization | Context, avoid overengineering | Parallel tools, efficient | - | sequential-thinking |

### Mandatory Workflows Checklist

- ✓ Skills inventory template (always)
- ✓ MCP tools inventory template (always)
- ✓ Ultrathinking framework (if complex)
- ✓ All 7 mandatory rules (always)

### Quality Validation

1. Completeness
2. Guideline compliance
3. Mandatory workflows
4. Skill detection
5. Tool detection
6. Actionability
7. XML validity

---

**Ready to enhance your prompts?**

```
"Enhance this prompt: [your raw input here]"
```

**The skill handles the rest.**
