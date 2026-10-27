# Example 2: File Path → Complete Code Analysis Task

## Before: Simple File Path Request

```
"Analyze src/services/PaymentProcessor.ts"
```

**Problems with this input:**
- Single sentence, no context
- No workflow or methodology
- No tools specified
- Missing all mandatory workflows
- No success criteria
- Unclear what "analyze" means
- No consideration of security (payment processing!)

---

## After: Enhanced Code Analysis Prompt

### Key Transformations:

#### 1. Task Summary
```xml
<task_summary>
Perform comprehensive code analysis of the PaymentProcessor service to understand
its structure, dependencies, functionality, and identify any potential issues or
improvement opportunities.
</task_summary>
```

**What Changed:**
- "Analyze" → "Comprehensive code analysis covering structure, dependencies, functionality, issues"
- Added clear scope: understand + identify opportunities

#### 2. Context
```xml
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
```

**What Changed:**
- Added domain classification (payment processing - critical!)
- Inferred TypeScript from .ts extension
- Added security awareness (payment data is sensitive)
- Set constraint: analysis only, no changes

#### 3. Skills & Tools Detected
```xml
<skills_inventory>
Relevant Skills:
- serena: Symbol-level code analysis capabilities
</skills_inventory>

<mcp_tools_inventory>
Recommended MCP Tools:
- mcp__serena__get_symbols_overview: Understand PaymentProcessor structure
- mcp__serena__find_symbol: Find specific methods/classes
- mcp__serena__find_referencing_symbols: See where PaymentProcessor is used
- mcp__serena__search_for_pattern: Find patterns (error handling, validation)
</mcp_tools_inventory>
```

**What Changed:**
- Detected serena skill as relevant for code analysis
- Recommended specific Serena MCP tools instead of generic grep/cat
- Emphasized symbol-level analysis over text search

#### 4. 3-Phase Analysis Workflow
```xml
<workflow>
<phase_1>**Service Structure Analysis**
1. Complete skills inventory (load serena)
2. Use mcp__serena__get_symbols_overview for PaymentProcessor.ts
3. Identify: classes, methods, properties, dependencies
</phase_1>

<phase_2>**Functionality Analysis**
1. Use mcp__serena__find_symbol to examine each public method
2. Understand payment flow
3. Identify security-critical code
4. Map dependencies
</phase_2>

<phase_3>**Usage Analysis & Reporting**
1. Use mcp__serena__find_referencing_symbols on PaymentProcessor
2. Identify usage patterns
3. Compile comprehensive analysis report
</phase_3>
</workflow>
```

**What Changed:**
- Single vague request → 3-phase structured analysis
- No methodology → Clear steps using Serena MCP
- Added security focus (critical for payments)
- Added usage tracing (understand integration)

#### 5. Success Criteria
```xml
<success_criteria>
- Complete understanding of PaymentProcessor structure
- All public methods documented with purposes
- Payment flow clearly mapped
- Security considerations identified
- Dependencies fully documented
- Usage patterns understood
- Comprehensive analysis report provided
</success_criteria>
```

**What Changed:**
- No criteria → 7 specific deliverables
- Vague "analyze" → Concrete outputs expected

---

## Comparison Table

| Aspect | Before | After |
|--------|--------|-------|
| **Input Length** | 1 sentence | Complete structured prompt |
| **Task Clarity** | "Analyze" (vague) | 7 specific analysis deliverables |
| **Methodology** | None | 3-phase workflow with Serena MCP |
| **Tools** | None mentioned | 4 Serena MCP tools specified |
| **Security Awareness** | None | Payment processing security considerations |
| **Workflows** | None | Skills + MCP tools inventories, all 7 rules |
| **Success Criteria** | None | 7 measurable outcomes |
| **Execution Plan** | None | Clear phase-by-phase approach |

---

## Why This Matters

### Security Awareness
**Before:** Just "analyze a file"
**After:** Recognizes payment processing → emphasizes security considerations

### Proper Tools
**Before:** Would likely use cat/grep
**After:** Uses Serena MCP for symbol-level analysis

### Comprehensive Scope
**Before:** Unclear what to analyze
**After:** Structure, functionality, security, dependencies, usage patterns

### Actionable Deliverables
**Before:** No deliverables defined
**After:** 7 specific analysis outputs expected

---

## Result

Simple file path transformed into:
- ✅ Comprehensive code analysis framework
- ✅ Security-aware approach for payment processing
- ✅ Symbol-level analysis using Serena MCP
- ✅ 3-phase structured workflow
- ✅ All mandatory workflows included
- ✅ Clear, measurable success criteria

**From one sentence to production-ready analysis prompt.**
