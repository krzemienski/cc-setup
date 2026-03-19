# Performance Optimization

## Model Selection Strategy

**Haiku 4.5** (90% of Sonnet capability, 3x cost savings):
- Lightweight agents with frequent invocation
- Pair programming and code generation
- Worker agents in multi-agent systems

**Sonnet 4.6** (Best coding model):
- Main development work
- Orchestrating multi-agent workflows
- Complex coding tasks

**Opus 4.5** (Deepest reasoning):
- Complex architectural decisions
- Maximum reasoning requirements
- Research and analysis tasks

## Sequential Thinking (MANDATORY for complex requests)

Before implementing ANY non-trivial request, use the `sequentialthinking` MCP tool to:
1. Break down the user's request into discrete steps
2. Identify ambiguities and assumptions
3. Plan the approach before writing code
4. Consider edge cases and failure modes

**NEVER rush to code.** Think first, implement second.

## Context Window Management

Avoid last 20% of context window for:
- Large-scale refactoring
- Feature implementation spanning multiple files
- Debugging complex interactions

Lower context sensitivity tasks:
- Single-file edits
- Independent utility creation
- Documentation updates
- Simple bug fixes

## Extended Thinking + Plan Mode

Extended thinking is enabled by default, reserving up to 31,999 tokens for internal reasoning.

For complex tasks requiring deep reasoning:
1. Ensure extended thinking is enabled (on by default)
2. Enable **Plan Mode** for structured approach
3. Use multiple critique rounds for thorough analysis
4. Use split role sub-agents for diverse perspectives

## Documentation Lookup (MANDATORY)

Before implementing anything involving a library, framework, or API:
1. Use **Context7 MCP** (`resolve-library-id` → `query-docs`) to fetch current documentation
2. Use **deepwiki MCP** for GitHub repository documentation
3. Do NOT rely on training data — docs change. Always fetch fresh.

## Build Troubleshooting

If build fails:
1. Use **build-error-resolver** agent
2. Analyze error messages
3. Fix incrementally
4. Verify after each fix — compilation success is NOT functional validation
