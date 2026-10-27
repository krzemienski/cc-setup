# Optimize Prompt - Raw Input to Production-Ready Prompts

> Transform messy voice rambles, incomplete ideas, and file path requests into structured, guideline-compliant prompts with mandatory workflows.

## What is Optimize Prompt?

**Optimize Prompt** is a Claude Code skill that transforms any raw input into production-ready prompts following Opus 4.5 and Sonnet 4.5 best practices.

### Why Optimize Prompt?

✅ **Handles Messy Input** - Voice transcripts, incomplete ideas, file paths
✅ **Applies Best Practices** - Opus 4.5 + Sonnet 4.5 + Claude Code guidelines
✅ **Injects Workflows** - Skills inventory, MCP tools, ultrathinking, mandatory rules
✅ **Detects Skills & Tools** - Recommends relevant skills and MCP tools
✅ **Validates Quality** - 7-point validation before output
✅ **Flexible Output** - Return formatted or save to file

---

## Quick Start

### 30-Second Start

**Transform voice ramble:**
```
"Enhance this: So I was thinking we should analyze that auth bug
because it's been causing issues and maybe look at the login function"
```

**Transform file path:**
```
"Enhance this: Analyze src/components/Dashboard.tsx"
```

**Transform incomplete idea:**
```
"Enhance this: Build user registration API endpoint"
```

That's it! Get structured, guideline-compliant prompt with all mandatory workflows.

---

## What You Get

### Every Optimize Prompt Includes:

1. ✅ **Clear Task Summary** - Concise description of goal
2. ✅ **Full Context** - Domain, technical details, constraints
3. ✅ **Skills Inventory** - Mandatory checklist of relevant skills to load
4. ✅ **MCP Tools Inventory** - Recommended MCP tools (Serena, sequential-thinking, etc.)
5. ✅ **Ultrathinking Framework** - For complex multi-step problems
6. ✅ **Mandatory Rules** - All 7 critical rules (no tests unless asked, read code first, etc.)
7. ✅ **Structured Workflow** - Phased approach with clear steps
8. ✅ **Success Criteria** - Measurable outcomes
9. ✅ **Semantic XML** - Clean, parseable structure

---

## Input Types Supported

### 1. Voice Rambles
Unstructured spoken thoughts transcribed to text:
```
"Um so like we need to fix that thing in the dashboard where
it's super slow when loading data and maybe we could cache stuff"
```

### 2. Semi-Structured Ideas
Partial prompts missing context or workflows:
```
"Build a new feature for exporting reports to PDF"
```

### 3. File Path Requests
Simple file references needing full task structure:
```
"Check src/api/auth.ts"
```

### 4. Incomplete Prompts
Prompts missing mandatory workflows:
```
"Debug the authentication service - tokens are expiring too early"
```

---

## Mandatory Workflows Injected

### Every enhanced prompt includes these workflows:

#### 1. Skills Inventory
```xml
<skills_inventory>
MANDATORY: Check and load relevant skills before starting
- List available skills
- Identify matching skills for task
- Load with Skill tool
- Follow skill guidance
</skills_inventory>
```

#### 2. MCP Tools Inventory
```xml
<mcp_tools_inventory>
MANDATORY: Use MCP tools over bash equivalents
- mcp__serena__* for code analysis (NOT grep/find)
- mcp__filesystem__* for file ops (NOT cat/sed)
- mcp__git__* for git (NOT raw git commands)
- mcp__sequential-thinking for complex reasoning
</mcp_tools_inventory>
```

#### 3. Ultrathinking Framework
For complex tasks requiring systematic reasoning:
```xml
<thinking_framework>
Use mcp__sequential-thinking for:
- Architectural decisions
- Complex debugging
- Optimization problems
- Large refactorings
</thinking_framework>
```

#### 4. Mandatory Rules (7 Critical Rules)
```xml
<mandatory_rules>
Rule #1: NEVER write tests unless explicitly requested
Rule #2: NEVER propose changes without reading code first
Rule #3: ALWAYS use Serena MCP for code analysis
Rule #4: ALWAYS complete skills inventory first
Rule #5: ALWAYS complete MCP tools inventory first
Rule #6: ALWAYS use ultrathinking for complex problems
Rule #7: ALWAYS use sequential thinking for debugging
</mandatory_rules>
```

---

## Guideline Synthesis

### From Opus 4.5:
- Be explicit with instructions
- Add context to improve performance
- Avoid overengineering
- ALWAYS read code before proposing changes
- Minimize hallucinations (investigate first)
- Long-horizon reasoning with state tracking

### From Sonnet 4.5:
- Parallel tool calling optimization
- Balanced verbosity
- Context awareness
- Efficient communication

### From Claude Code Best Practices:
- CLAUDE.md usage
- Tool allowlists (MCP over bash)
- Skills inventory and loading
- Git workflows
- Specific instructions
- Course correction through questions

---

## File Structure

```
optimize-prompt/
├── SKILL.md              # Main skill (all intelligence here)
├── README.md             # This file
├── HOW_TO_USE.md         # Comprehensive usage guide
├── sample_inputs/        # Example raw inputs
│   ├── raw_voice_ramble.txt
│   ├── semi_structured_idea.txt
│   └── file_path_request.txt
├── expected_outputs/     # Example enhanced outputs
│   ├── enhanced_voice_ramble.xml
│   ├── enhanced_idea.xml
│   └── enhanced_file_request.xml
└── examples/             # Before/after transformations
    ├── example_1_voice_to_structured.md
    ├── example_2_incomplete_to_complete.md
    └── example_3_manual_workflows.md
```

---

## Installation

### For Claude Code Users

**Project-Level Installation:**
```bash
# Copy to project .claude/skills/
cp -r optimize-prompt /path/to/your/project/.claude/skills/

# Restart Claude Code
# Skill automatically loads when relevant
```

**User-Level Installation:**
```bash
# Copy to user ~/.claude/skills/
cp -r optimize-prompt ~/.claude/skills/

# Restart Claude Code
# Available across all projects
```

### Verification

After installation, test with:
```
"Enhance this prompt: Analyze the login function in src/auth.ts"
```

You should get a structured XML prompt with all mandatory workflows.

---

## Usage Examples

### Example 1: Voice Ramble → Structured Task

**Input:**
```
"Okay so we need to um you know fix that performance issue
in the dashboard where it's loading really slowly"
```

**Output:**
- Task: Optimize dashboard performance
- Skills: systematic-debugging, serena
- MCP tools: mcp__sequential-thinking, mcp__serena__*
- Workflow: Investigation → Root cause → Optimization
- All mandatory rules included
- Success criteria: 50% performance improvement

### Example 2: File Path → Full Task

**Input:**
```
"Analyze src/components/UserProfile.tsx"
```

**Output:**
- Task: Code analysis of UserProfile component
- Skills: serena
- MCP tools: mcp__serena__get_symbols_overview
- Workflow: Read → Analyze → Report findings
- Rule emphasis: Read code first (Rule #2)
- Success criteria: Complete component analysis

### Example 3: Incomplete Idea → Complete Prompt

**Input:**
```
"Build registration endpoint with email validation"
```

**Output:**
- Task: Feature implementation - user registration API
- Context: REST API, authentication domain
- Skills inventory check
- MCP tools inventory check
- Workflow: Understand existing → Design → Implement
- Rule emphasis: No tests unless asked (Rule #1)
- Success criteria: Working endpoint following patterns

---

## Key Features

### Smart Detection
- **Task Type**: Code analysis, feature, bug fix, optimization
- **Complexity**: Simple, moderate, complex (triggers ultrathinking)
- **Skills**: Detects relevant skills based on task
- **MCP Tools**: Recommends specialized tools over bash

### Quality Validation (7-Point Checklist)
1. ✓ Completeness (all sections present)
2. ✓ Guideline compliance (Opus 4.5, Sonnet 4.5, Claude Code)
3. ✓ Mandatory workflows (skills, MCP tools, ultrathinking, rules)
4. ✓ Skill detection (relevant skills identified)
5. ✓ Tool detection (MCP tools recommended)
6. ✓ Actionability (clear, executable steps)
7. ✓ XML validity (proper structure)

### Flexible Output
- **Default**: Return formatted prompt in response
- **File Output**: Save to specified path (prompts/task.xml)

---

## Use Cases

### Code Analysis
- Understand existing codebase
- Analyze specific files or modules
- Identify patterns and issues

### Feature Implementation
- Build new features following patterns
- Design before implementation
- Avoid overengineering

### Debugging
- Systematic root cause analysis
- Sequential thinking for complex bugs
- Hypothesis generation and testing

### Optimization
- Performance improvements
- Query optimization
- Caching strategies

### Refactoring
- Large-scale code improvements
- Pattern migration
- Technical debt reduction

---

## Best Practices

### 1. Provide Context
More context = better enhancement:
- ❌ "Fix the bug"
- ✅ "Fix authentication bug where tokens expire too early in production"

### 2. Be Specific About Goals
Clear goals = clear success criteria:
- ❌ "Make it faster"
- ✅ "Reduce dashboard load time by 50% with large datasets"

### 3. Include Constraints
Constraints guide decisions:
- Budget limits
- Timeline requirements
- Technology restrictions
- Compliance needs

### 4. Use File Output for Reusable Tasks
Save enhanced prompts for repeated use:
```
"Enhance and save to prompts/debug-auth.xml: Debug authentication issues"
```

### 5. Trust the Workflows
Don't skip mandatory workflows:
- Skills inventory prevents missing proven patterns
- MCP tools inventory prevents using inferior bash equivalents
- Ultrathinking prevents premature solutions
- Mandatory rules prevent common mistakes

---

## Performance Benchmarks

| Metric | Optimize Prompt | Manual Creation |
|--------|-----------------|-----------------|
| Time to structured prompt | < 1 min | 5-10 min |
| Mandatory workflows | 100% included | Often missing |
| Guideline compliance | Automatic | Manual effort |
| Skill detection | Automatic | Manual research |
| MCP tool recommendations | Automatic | Manual discovery |
| Quality validation | 7-point checklist | Variable |

---

## Limitations

### This Skill Cannot:
- Execute the enhanced prompt (only creates it)
- Implement code or features (only structures the task)
- Make architectural decisions (provides framework)
- Replace human judgment

### When NOT to Use:
- Prompt is already complete and well-structured
- Task is trivial single-step operation
- You want execution, not structure

---

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill instructions (for Claude)
- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Comprehensive user guide
- **sample_inputs/** - Example raw inputs
- **expected_outputs/** - Example enhanced outputs
- **examples/** - Before/after transformation examples

---

## Version

**Current Version:** 1.0.0
**Release Date:** December 2025
**Status:** Production-ready

---

## Related Skills

**Works well with:**
- **prompt-factory** - For creating domain-specific prompt builders
- **systematic-debugging** - For structured debugging workflows
- **serena** (MCP) - For code analysis
- **test-driven-development** - When tests are explicitly needed

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Enhance voice ramble | `"Enhance this: [voice transcript]"` |
| Enhance file path | `"Enhance this: Analyze [file path]"` |
| Enhance incomplete idea | `"Enhance this: [idea]"` |
| Save to file | `"Enhance and save to [path]: [input]"` |
| Ask for clarification | Skill asks automatically if needed |

---

**Ready to transform raw input into production-ready prompts?**

```
"Enhance this prompt: [your raw input here]"
```

**It's that simple.**
