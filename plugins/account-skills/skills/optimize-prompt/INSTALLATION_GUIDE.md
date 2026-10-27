# Optimize Prompt - Complete Installation & Usage Guide

This guide covers installation and usage of the complete Optimize Prompt system:
- **Skill**: `optimize-prompt` (template-driven prompt enhancement)
- **Slash Command**: `/enhance-prompt` (quick CLI access)
- **Agent**: `prompt-optimizer` (subagent for automatic enhancement)

---

## Quick Installation (All Components)

```bash
# Navigate to skills factory root
cd /path/to/claude-code-skills-factory

# Install skill (project-level)
cp -r generated-skills/optimize-prompt .claude/skills/

# Install slash command (project-level)
cp -r generated-commands/enhance-prompt .claude/commands/

# Install agent (project-level)
cp .claude/agents/prompt-optimizer.md .claude/agents/

# Restart Claude Code
# All three components now available!
```

---

## Component Overview

### 1. optimize-prompt Skill

**What it is:** Template-driven skill with all enhancement intelligence embedded in SKILL.md

**When to use:** Invoke manually or automatically when enhancing prompts

**How to invoke:**
```
"Use the optimize-prompt skill to transform this ramble: [input]"
```

**What it does:**
- Analyzes raw input (voice/idea/file/incomplete)
- Applies Opus 4.5 and Sonnet 4.5 guidelines
- Injects mandatory workflows (skills inventory, MCP tools, ultrathinking, rules)
- Formats with semantic XML
- Validates quality (7-point checklist)
- Returns or saves enhanced prompt

### 2. /enhance-prompt Slash Command

**What it is:** Quick CLI command for instant prompt enhancement

**When to use:** Fastest way to enhance prompts from command line

**How to invoke:**
```
/enhance-prompt [your raw input]
```

**What it does:**
- Wraps the optimize-prompt skill with convenient syntax
- Same transformation capabilities
- Cleaner invocation
- File output support

### 3. prompt-optimizer Agent

**What it is:** Specialized subagent for automatic prompt enhancement

**When to use:** Automatically invoked when enhancing/optimizing prompts

**How to invoke:**
- Automatic: "Optimize this prompt: [input]"
- Explicit: Use Task tool with subagent_type='prompt-optimizer'

**What it does:**
- Same as skill but in separate context window
- Preserves main conversation context
- Can be explicitly delegated complex enhancement tasks

---

## Installation Options

### Option 1: Project-Level (Recommended for Teams)

Install in your project's `.claude/` directory - shared with team via git:

```bash
# Skill
cp -r generated-skills/optimize-prompt .claude/skills/

# Command
cp -r generated-commands/enhance-prompt .claude/commands/

# Agent
cp .claude/agents/prompt-optimizer.md .claude/agents/

# Commit to git
git add .claude/
git commit -m "Add optimize-prompt system (skill, command, agent)"
git push
```

**Benefits:**
- Shared with entire team
- Version controlled
- Project-specific configurations possible

### Option 2: User-Level (Personal)

Install in your home directory - available in all projects:

```bash
# Skill
cp -r generated-skills/optimize-prompt ~/.claude/skills/

# Command
cp -r generated-commands/enhance-prompt ~/.claude/commands/

# Agent
cp .claude/agents/prompt-optimizer.md ~/.claude/agents/

# Restart Claude Code
```

**Benefits:**
- Available in all your projects
- Personal configurations
- No need to install per project

### Option 3: Mixed (Recommended for Solo Developers)

- **Skill + Command:** User-level (use everywhere)
- **Agent:** Project-level (team collaboration)

```bash
# User-level
cp -r generated-skills/optimize-prompt ~/.claude/skills/
cp -r generated-commands/enhance-prompt ~/.claude/commands/

# Project-level
cp .claude/agents/prompt-optimizer.md .claude/agents/
```

---

## Usage Guide

### Using the Skill

**Invocation:**
```
"Use optimize-prompt skill to enhance: [raw input]"
"Transform this voice ramble with optimize-prompt: [ramble]"
```

**Example:**
```
User: "Use optimize-prompt to optimize this: Debug the login function in auth.ts"

Claude: [Analyzes input]
        [Applies guidelines]
        [Injects workflows]
        [Outputs enhanced XML prompt with all mandatory sections]
```

### Using the Slash Command (Fastest)

**Invocation:**
```
/enhance-prompt [raw input]
```

**Examples:**
```
/enhance-prompt Build a payment API with Stripe and PostgreSQL

/enhance-prompt Analyze components/Dashboard.tsx

/enhance-prompt so I want to refactor this auth system because it's
really messy and using old patterns from 2018

/enhance-prompt Optimize the checkout flow
```

**With File Output:**
```
/enhance-prompt Build user registration endpoint and save to prompts/registration.xml
```

### Using the Agent (Automatic or Explicit)

**Automatic Invocation:**
```
"Optimize this prompt for Opus 4.5: [prompt text]"
"Enhance this idea: [incomplete idea]"
```

Claude will automatically delegate to prompt-optimizer agent.

**Explicit Invocation (for complex enhancement):**
```
"Use the prompt-optimizer agent to transform this complex voice ramble: [long ramble]"
```

---

## What Gets Injected

Every enhanced prompt includes these mandatory components:

### 1. Skills Inventory ✓

```xml
<skills_inventory>
**MANDATORY: Complete before starting**

Step 1: List Available Skills
Step 2: Identify Matching Skills
Step 3: Load Skills (use Skill tool)
Step 4: Follow Guidance

Relevant skills: [detected based on task type]
</skills_inventory>
```

**Skill Detection Logic:**
- Code tasks → `serena`, `systematic-debugging`
- Frontend → `frontend-development`, `ui-styling`
- Backend → `backend-development`
- Testing → `test-driven-development` (only if tests requested!)
- Design → `ui-ux-pro-max`, `frontend-design-pro`
- Mobile → `mobile-development`, `ios-swift-expert`
- Database → `databases`
- DevOps → `devops`
- Git → `git-commit-helper`
- Cloud → `aws-solution-architect`

### 2. MCP Tools Inventory ✓

```xml
<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Step 1: Check Available MCP Servers
Step 2: Identify Specialized Tools
Step 3: Prefer MCP Over Bash

Recommended MCP tools: [detected based on operations needed]

Always prefer MCP tools over bash equivalents.
</mcp_tools_inventory>
```

**MCP Tool Detection Logic:**
- Code analysis → `mcp__serena__find_symbol`, `mcp__serena__get_symbols_overview`
- File operations → `mcp__filesystem__*`
- Git operations → `mcp__git__*`
- Complex reasoning → `mcp__sequential-thinking__sequentialthinking`
- Web research → `mcp__tavily__*`, `mcp__firecrawl-mcp__*`
- Browser automation → `mcp__playwright__*`, `mcp__puppeteer__*`

### 3. Ultrathinking Framework ✓ (when moderate to complex)

```xml
<thinking_framework>
**Use for complex multi-step problems**

WHEN TO USE:
- Architectural decisions
- Debugging complex issues
- Multiple valid approaches
- Optimization problems
- Large refactorings

HOW TO USE:
1. Call mcp__sequential-thinking__sequentialthinking
2. Incrementally reason through steps
3. Generate and test hypotheses
4. Iterate until solution found

TRIGGER PHRASES:
- "think" < "think hard" < "think harder" < "ultrathink"
</thinking_framework>
```

### 4. Mandatory Rules ✓ (all 7, always)

```xml
<mandatory_rules>
<rule id="1" priority="CRITICAL">
NEVER write unit tests unless explicitly requested
</rule>

<rule id="2" priority="CRITICAL">
NEVER propose code changes without reading code first
</rule>

<rule id="3" priority="HIGH">
ALWAYS use Serena MCP for code analysis
</rule>

<rule id="4" priority="HIGH">
ALWAYS complete skills inventory first
</rule>

<rule id="5" priority="HIGH">
ALWAYS complete MCP tools inventory first
</rule>

<rule id="6" priority="MEDIUM">
ALWAYS use ultrathinking for complex problems
</rule>

<rule id="7" priority="MEDIUM">
ALWAYS use sequential thinking for debugging
</rule>
</mandatory_rules>
```

---

## Complete Example Transformations

### Example 1: Voice Ramble → Debug Task

See: `examples/example_1_voice_to_structured.md`

**Input (90 words):**
```
"So um I was thinking we should probably look into that performance issue
we've been having with the dashboard because like users keep complaining..."
```

**Output (~3,800 words):**
- Clear task summary
- Structured context
- Skills inventory (systematic-debugging, serena)
- MCP tools inventory (sequential-thinking, Serena MCP)
- Ultrathinking framework (performance optimization)
- All 7 mandatory rules
- 3-phase workflow with detailed steps
- Measurable success criteria
- Execution trigger

**Key Transformations:**
- Voice → Clear task
- Vague idea → Systematic investigation
- No workflows → All mandatory workflows
- No rules → All 7 rules
- No structure → 3-phase execution plan

### Example 2: File Path → Analysis Task

See: `examples/example_2_file_path_to_analysis.md`

**Input (1 sentence):**
```
"Analyze src/services/PaymentProcessor.ts"
```

**Output (~2,500 words):**
- Comprehensive analysis framework
- Security awareness (payment domain)
- Symbol-level analysis with Serena MCP
- All mandatory workflows
- Clear deliverables

---

## Validation & Quality

### 7-Point Quality Checklist

Every enhanced prompt is validated against:

1. ✓ **Completeness** - All required sections present
2. ✓ **Guideline Compliance** - Opus 4.5, Sonnet 4.5, Claude Code
3. ✓ **Mandatory Workflows** - Skills, MCP tools, ultrathinking, rules
4. ✓ **Skill Detection** - Relevant skills identified correctly
5. ✓ **Tool Detection** - MCP tools recommended over bash
6. ✓ **Actionability** - Clear, executable workflow steps
7. ✓ **XML Validity** - Proper structure and syntax

### Guideline Compliance

**Opus 4.5:**
- ✅ Be explicit with instructions
- ✅ Add context to improve performance
- ✅ Avoid overengineering
- ✅ Code exploration REQUIRED (Rule #2)
- ✅ Minimize hallucinations (investigate first)
- ✅ Long-horizon reasoning (ultrathinking framework)

**Sonnet 4.5:**
- ✅ Parallel tool calling optimization
- ✅ Balanced verbosity
- ✅ Context awareness

**Claude Code Best Practices:**
- ✅ Skills inventory and usage
- ✅ MCP tools over bash
- ✅ Specific instructions
- ✅ Git workflows

---

## Best Practices

### For Best Results:

1. **Be specific in your input**
   - Poor: "Fix the bug"
   - Good: "Debug 500 error in POST /api/login when credentials invalid"

2. **Provide context when available**
   - Include tech stack mentions
   - Mention frameworks or libraries
   - Note any constraints

3. **Let the system ask questions**
   - If input is vague, you'll be asked 1-2 clarifying questions
   - Answer them for better enhancement

4. **Review the enhanced prompt**
   - Check that skills make sense for your task
   - Verify MCP tools are appropriate
   - Confirm mandatory rules align with your needs

5. **Iterate if needed**
   - "Add more emphasis on security"
   - "Make it more concise"
   - "Focus more on performance"

---

## Troubleshooting

### Issue: Skill not found

**Solution:**
```bash
# Verify installation
ls .claude/skills/optimize-prompt/SKILL.md
# or
ls ~/.claude/skills/optimize-prompt/SKILL.md

# If missing, reinstall
cp -r generated-skills/optimize-prompt .claude/skills/
```

### Issue: Slash command not working

**Solution:**
```bash
# Verify installation
ls .claude/commands/enhance-prompt/enhance-prompt.md
# or
ls ~/.claude/commands/enhance-prompt/enhance-prompt.md

# Restart Claude Code
```

### Issue: Agent not automatically invoked

**Solution:**
Check agent description trigger words:
- "optimize prompt"
- "enhance prompt"
- "transform this"
- "apply guidelines"

Or invoke explicitly:
```
"Use the prompt-optimizer agent to optimize this: [input]"
```

### Issue: Enhanced prompt missing workflows

**Solution:**
This indicates a validation failure. Report as a bug. All enhanced prompts should have:
- Skills inventory ✓
- MCP tools inventory ✓
- Mandatory rules (all 7) ✓
- Ultrathinking framework (if moderate to complex) ✓

### Issue: Wrong skills recommended

**Solution:**
Be more explicit about task type:
- "This is a React frontend task: [input]"
- "This is Python backend work: [input]"
- "This is a debugging task: [input]"

---

## Advanced Usage

### Combining with Other Skills

Enhanced-prompt works well with:

```
"Use optimize-prompt to optimize this, then use prompt-factory to create
variations: [input]"

"Enhance this debugging task, then use systematic-debugging to execute it: [input]"
```

### Batch Enhancement

```
"Enhance these 3 tasks:
1. [task 1]
2. [task 2]
3. [task 3]"
```

Result: Single enhanced prompt covering all 3 tasks with unified workflow.

### Custom Rules

```
"Enhance this prompt and add the mandatory rule: Always use React Server Components"
```

The system will inject:
```xml
<rule id="8" priority="HIGH">
ALWAYS use React Server Components for data fetching.
Reason: [Your provided reason]
</rule>
```

---

## File Organization

### Recommended Structure

```
your-project/
├── .claude/
│   ├── skills/
│   │   └── optimize-prompt/         # Skill
│   │       ├── SKILL.md
│   │       ├── README.md
│   │       ├── HOW_TO_USE.md
│   │       └── examples/
│   ├── commands/
│   │   └── enhance-prompt/          # Slash command
│   │       ├── enhance-prompt.md
│   │       └── README.md
│   └── agents/
│       └── prompt-optimizer.md       # Agent
├── prompts/                          # Your enhanced prompts
│   ├── feature-tasks/
│   ├── debugging-tasks/
│   └── optimization-tasks/
└── ...
```

### Organizing Optimize Prompts

Create a `prompts/` folder to store enhanced prompts:

```bash
mkdir -p prompts/{features,bugs,optimizations,analysis}

# Save enhanced prompts with descriptive names
/enhance-prompt Build API endpoint and save to prompts/features/user-registration.xml
/enhance-prompt Debug auth error and save to prompts/bugs/jwt-expiration.xml
```

---

## Testing Your Installation

### Test 1: Skill Works

```
User: "Use optimize-prompt skill to enhance: Build a REST API"

Expected: Enhanced XML prompt with:
- Task summary ✓
- Context ✓
- Skills inventory ✓
- MCP tools inventory ✓
- Mandatory rules (all 7) ✓
- Workflow ✓
- Success criteria ✓
```

### Test 2: Slash Command Works

```
User: /enhance-prompt Debug the login function

Expected: Same enhanced prompt as skill test
```

### Test 3: Agent Auto-Invocation

```
User: "Optimize this prompt for Opus 4.5: [prompt text]"

Expected: Claude delegates to prompt-optimizer agent automatically
```

### Test 4: Mandatory Workflows Present

```
User: /enhance-prompt Refactor auth system

Expected Output Must Include:
- <skills_inventory> section ✓
- <mcp_tools_inventory> section ✓
- <mandatory_rules> with all 7 rules ✓
- <thinking_framework> (if moderate complexity) ✓
```

---

## Performance Benchmarks

Based on testing:

| Input Type | Processing Time | Output Size | Workflows Injected |
|------------|----------------|-------------|-------------------|
| Voice Ramble (100 words) | < 10 sec | ~4,000 words | 4/4 |
| File Path (1 sentence) | < 5 sec | ~2,500 words | 4/4 |
| Semi-Structured (50 words) | < 8 sec | ~3,000 words | 4/4 |
| Incomplete Prompt (200 words) | < 12 sec | ~3,500 words | 4/4 |

**Workflows Injected (always 4/4):**
1. Skills inventory
2. MCP tools inventory
3. Ultrathinking framework (if moderate/complex)
4. Mandatory rules (all 7)

---

## Customization

### Adding Custom Rules

Edit `.claude/agents/prompt-optimizer.md` and add to the Mandatory Rules section:

```xml
<rule id="8" priority="HIGH">
[Your custom rule]
Reason: [Why this rule matters]
</rule>
```

### Adding Custom Skill Detection

Edit SKILL.md and update skill detection logic:

```xml
IF task = "your-specific-task-type":
  → Recommend: your-custom-skill
```

### Changing Default Output Location

In the slash command, modify file output behavior:

```yaml
# Change default output directory
Default output: prompts/enhanced-{timestamp}.xml
```

---

## Uninstallation

### Remove All Components

```bash
# Skill
rm -rf .claude/skills/optimize-prompt
# or
rm -rf ~/.claude/skills/optimize-prompt

# Command
rm -rf .claude/commands/enhance-prompt
# or
rm -rf ~/.claude/commands/enhance-prompt

# Agent
rm .claude/agents/prompt-optimizer.md
# or
rm ~/.claude/agents/prompt-optimizer.md

# Restart Claude Code
```

---

## Support & Resources

### Documentation

- **SKILL.md** - Complete enhancement framework
- **HOW_TO_USE.md** - Comprehensive usage guide
- **README.md** - Quick reference
- **examples/** - Before/after transformations

### Related Tools

- **prompt-factory** - Create domain-specific prompt builders
- **systematic-debugging** - Structured debugging workflows
- **serena (MCP)** - Symbol-level code analysis

### Official Documentation

- [Opus 4.5 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Opus 4.5 Migration](https://github.com/anthropics/claude-code/tree/main/plugins/claude-opus-4-5-migration)

---

## FAQ

**Q: Do I need all three components?**
A: No. Install what fits your workflow:
- Slash command only: Quick CLI enhancement
- Skill + Command: Manual invocation + CLI
- All three: Maximum flexibility (manual, CLI, automatic)

**Q: Can I modify the mandatory rules?**
A: Yes! Edit the agent or skill SKILL.md. Rules are templates you can customize.

**Q: Will this work with Sonnet 4.5 and Opus 4.5?**
A: Yes! The enhancement framework applies guidelines for both models.

**Q: Do enhanced prompts work with other LLMs (ChatGPT, Gemini)?**
A: The guidelines are Claude-specific, but XML formatting and structured workflows apply broadly.

**Q: Can I enhance already-enhanced prompts?**
A: Yes, for further refinement. The system detects existing workflows and updates them.

**Q: Do I need Python installed?**
A: No! This is a template-driven system. All intelligence is in SKILL.md - zero Python code.

---

## Checklist: Installation Complete

- [ ] Skill installed (`.claude/skills/optimize-prompt/` or `~/.claude/skills/optimize-prompt/`)
- [ ] Command installed (`.claude/commands/enhance-prompt/` or `~/.claude/commands/enhance-prompt/`)
- [ ] Agent installed (`.claude/agents/prompt-optimizer.md`)
- [ ] Claude Code restarted
- [ ] Tested skill: "Use optimize-prompt skill to enhance: Test task"
- [ ] Tested command: `/enhance-prompt Test task`
- [ ] Tested agent auto-invocation: "Optimize this prompt: Test"
- [ ] Verified all 4 mandatory workflows present in output
- [ ] Verified all 7 mandatory rules present in output

---

**You're ready to transform raw input into production-ready prompts!** 🚀
