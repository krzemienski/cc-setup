---
name: python-agent-sdk
description: Use when building AI agents with Python, creating custom tools, implementing hooks for monitoring/enforcement, connecting MCP servers, managing agent sessions, or needing programmatic control over Claude conversations. Covers query() for simple queries, ClaudeSDKClient for full-featured agents with tools/hooks, custom tool creation (in-process MCP servers as Python functions), pre/post hooks for validation and logging, MCP server integration, file operations, and session management.
---

# Python Agent SDK

Build production-ready AI agents with custom tools, hooks, and MCP integration using Python.

## Overview

The Python Agent SDK provides building blocks for creating agents powered by Claude. It offers two main interfaces:

- **`query()`** - Simple async function for one-shot queries
- **`ClaudeSDKClient`** - Full-featured client with custom tools, hooks, sessions, and MCP integration

Built on the agent harness powering Claude Code, the SDK provides automatic context management, file operations, web search, MCP extensibility, fine-grained permissions, and production essentials.

## Quick Start Decision Tree

```
Need to query Claude from Python?
│
├─ Simple one-shot query, no state needed?
│  └─> Use query()
│     └─> See: scripts/simple_query.py
│
└─ Need any of:
   ├─ Multi-turn conversation?
   ├─ Custom Python tools?
   ├─ Hooks for monitoring/enforcement?
   ├─ MCP server connections?
   ├─ Session resumption?
   │
   └─> Use ClaudeSDKClient
       ├─> Basic session: scripts/interactive_session.py
       ├─> Custom tools: scripts/custom_tool.py
       ├─> Hooks: scripts/hooks_example.py
       ├─> File ops: scripts/file_operations.py
       └─> MCP: scripts/mcp_integration.py
```

## Installation

```bash
# Install SDK
pip install claude-agent-sdk

# Prerequisites
# Python 3.10+
# Node.js (for Claude Code CLI)
npm install -g @anthropic-ai/claude-code
```

Authentication:
```bash
# API key (default)
export ANTHROPIC_API_KEY="your-key"

# Or Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Or Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
```

## Core Patterns

### Pattern 1: Simple Query

Use `query()` for one-shot questions without state:

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message, end="", flush=True)

anyio.run(main)
```

**When to use:** Quick scripts, CLIs, single questions

**Reference:** `scripts/simple_query.py`

### Pattern 2: Interactive Session

Use `ClaudeSDKClient` for multi-turn conversations:

```python
import anyio
from claude_agent_sdk import ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        # First message
        response = await client.send_message("Tell me a joke")
        print(response)
        
        # Follow-up (maintains context)
        response = await client.send_message("Explain why it's funny")
        print(response)

anyio.run(main)
```

**When to use:** Chatbots, assistants, stateful agents

**Reference:** `scripts/interactive_session.py`

### Pattern 3: Custom Tools

Create Python functions that Claude can invoke:

```python
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import Tool, ToolDefinition, ToolParameter

async def calculate(a: float, b: float, operation: str) -> dict:
    """Custom tool implementation"""
    if operation == "add":
        return {"result": a + b}
    elif operation == "multiply":
        return {"result": a * b}
    return {"error": "Unknown operation"}

# Define tool
tool = Tool(
    definition=ToolDefinition(
        name="calculate",
        description="Perform arithmetic: add or multiply",
        parameters=[
            ToolParameter(name="a", type="number", required=True),
            ToolParameter(name="b", type="number", required=True),
            ToolParameter(name="operation", type="string", required=True)
        ]
    ),
    handler=calculate
)

# Use with client
async with ClaudeSDKClient(tools=[tool]) as client:
    response = await client.send_message("What's 15 * 3?")
    print(response)
```

**When to use:** Domain-specific operations, API integrations, custom validation

**Reference:** `scripts/custom_tool.py`

### Pattern 4: Hooks for Monitoring

Add pre/post hooks to enforce policies or log operations:

```python
from claude_agent_sdk.types import ToolUseHook

async def pre_hook(tool_name: str, params: dict) -> dict:
    """Validate before tool runs"""
    print(f"[PRE] {tool_name} called with {params}")
    if tool_name == "delete_file" and params["path"].startswith("/system"):
        raise ValueError("Cannot delete system files")
    return params

async def post_hook(tool_name: str, params: dict, result: any):
    """Log after tool completes"""
    print(f"[POST] {tool_name} completed")

tool = Tool(
    definition=...,
    handler=...,
    hooks=ToolUseHook(pre_use=pre_hook, post_use=post_hook)
)
```

**When to use:** Auditing, policy enforcement, rate limiting, validation

**Reference:** `scripts/hooks_example.py`

### Pattern 5: MCP Integration

Connect external MCP servers for extended capabilities:

```python
mcp_servers = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": "your-token"}
    }
}

async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
    # Claude can now use tools from both MCP servers
    response = await client.send_message("List files and show my GitHub repos")
```

**When to use:** Database access, external APIs, pre-built integrations

**Reference:** `scripts/mcp_integration.py`

### Pattern 6: Session Resumption

Save and resume conversations:

```python
# Start session
async with ClaudeSDKClient() as client:
    session_id = client.session_id
    await client.send_message("Remember: my favorite color is blue")
    save_to_db(session_id)  # Save for later

# Resume later
saved_id = load_from_db()
async with ClaudeSDKClient(session_id=saved_id) as client:
    response = await client.send_message("What's my favorite color?")
    # Claude remembers from previous session
```

**When to use:** Long-running agents, user-specific conversations

**Reference:** `scripts/interactive_session.py` (resumable_session example)

## Common Use Cases

### 1. Research Assistant

```python
tools = [web_search_tool, summarize_tool, save_notes_tool]
async with ClaudeSDKClient(tools=tools) as client:
    response = await client.send_message(
        "Research the latest in quantum computing and summarize key findings"
    )
```

### 2. Code Analysis Agent

```python
tools = [analyze_file_tool, search_codebase_tool]
async with ClaudeSDKClient(tools=tools) as client:
    response = await client.send_message(
        "Find all uses of 'deprecated_function' and suggest replacements"
    )
```

**Reference:** `scripts/file_operations.py`

### 3. Customer Support Bot

```python
async def create_ticket(title: str, description: str) -> dict:
    # Custom tool for ticketing system
    pass

tools = [create_ticket_tool, search_kb_tool]
async with ClaudeSDKClient(tools=tools) as client:
    response = await client.send_message(
        f"User reports: {user_message}"
    )
```

### 4. Finance Agent

```python
# Enforce limits with hooks
async def validate_amount(tool: str, params: dict) -> dict:
    if params.get("amount", 0) > 10000:
        raise ValueError("Amount exceeds limit")
    return params

tools = [
    Tool(
        definition=process_payment_def,
        handler=process_payment,
        hooks=ToolUseHook(pre_use=validate_amount)
    )
]
```

**Reference:** `scripts/hooks_example.py` (policy_enforcement_example)

## API Reference

For complete API documentation including all parameters, return types, and advanced features, see:

**`references/api_reference.md`**

Contains:
- Complete `query()` and `ClaudeSDKClient` API
- All type definitions (Tool, ToolDefinition, ToolParameter, Hooks)
- MCP server configuration
- Authentication methods
- Settings and configuration
- Error handling patterns

## Best Practices

For production-ready patterns, gotchas, and proven approaches, see:

**`references/best_practices.md`**

Covers:
- Choosing query() vs ClaudeSDKClient
- Custom tool design principles
- Hook patterns (validation, logging, rate limiting)
- Session management security
- MCP server best practices
- Performance optimization
- Error handling and graceful degradation
- Security considerations
- Testing patterns
- Common gotchas

## Script Examples

All scripts are fully functional and can be run directly:

### Basic Usage
- **`scripts/simple_query.py`** - One-shot queries with `query()`
- **`scripts/interactive_session.py`** - Multi-turn conversations, streaming, resumption

### Advanced Features
- **`scripts/custom_tool.py`** - Creating custom Python tools
- **`scripts/hooks_example.py`** - Pre/post hooks for monitoring and enforcement
- **`scripts/file_operations.py`** - File analysis and codebase operations
- **`scripts/mcp_integration.py`** - Connecting external MCP servers

Each script includes:
- Multiple examples (basic → advanced)
- Inline documentation
- Commented alternatives
- Real working code

Run any script:
```bash
python scripts/simple_query.py
python scripts/interactive_session.py
```

## Decision Guide

**"Should I use the Python Agent SDK?"**

✅ **Yes, if you need:**
- Python integration with Claude
- Custom tools (in-process MCP servers)
- Hooks for monitoring/enforcement
- Multi-turn conversations
- Session management
- MCP server connections
- Programmatic agent control

❌ **No, use Claude API instead if:**
- Simple HTTP requests sufficient
- No custom tools needed
- No Python requirement
- No session management needed

**"Which interface should I use?"**

| Need | Use | Reference |
|------|-----|-----------|
| One-shot query | `query()` | simple_query.py |
| Multi-turn chat | `ClaudeSDKClient` | interactive_session.py |
| Custom Python tools | `ClaudeSDKClient` + `Tool` | custom_tool.py |
| Monitoring/enforcement | `ClaudeSDKClient` + hooks | hooks_example.py |
| External MCP servers | `ClaudeSDKClient` + `mcp_servers` | mcp_integration.py |
| File operations | Custom tools | file_operations.py |
| Session resumption | `ClaudeSDKClient` + `session_id` | interactive_session.py |

## Troubleshooting

### CLINotFoundError
```bash
npm install -g @anthropic-ai/claude-code
```

### Authentication Failed
```bash
export ANTHROPIC_API_KEY="your-key"
```

### MCP Connection Failed
- Verify MCP server is installed: `npx @modelcontextprotocol/server-filesystem --help`
- Check paths and permissions
- Verify environment variables for servers requiring auth

### Tool Not Found
- Ensure tool is registered in `tools=` parameter
- Verify tool name matches exactly in `ToolDefinition`
- Check tool parameters match what Claude is calling

For more troubleshooting, see `references/best_practices.md` → "Common Gotchas"

## Learning Path

1. **Start simple:** Run `scripts/simple_query.py` to understand basic usage
2. **Add interactivity:** Run `scripts/interactive_session.py` for multi-turn conversations
3. **Create custom tools:** Study `scripts/custom_tool.py` and create your own
4. **Add monitoring:** Implement hooks with `scripts/hooks_example.py`
5. **Integrate MCP:** Connect external servers with `scripts/mcp_integration.py`
6. **Build production agent:** Combine patterns using `references/best_practices.md`

## Additional Resources

- **API Reference:** Complete technical documentation (`references/api_reference.md`)
- **Best Practices:** Production patterns and gotchas (`references/best_practices.md`)
- **Official Docs:** https://docs.claude.com/en/docs/agent-sdk/overview
- **GitHub:** https://github.com/anthropics/claude-agent-sdk-python
