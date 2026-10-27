# Python Agent SDK API Reference

Complete reference for the Python Agent SDK components, types, and patterns.

## Installation

```bash
pip install claude-agent-sdk
```

**Prerequisites:**
- Python 3.10+
- Node.js (for CLI)
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

## Core Functions

### `query()`

Simple async function for one-shot queries without session management.

**Signature:**
```python
async def query(
    prompt: str,
    system_prompts: list[str] | None = None,
    model: str | None = None
) -> AsyncIterator[str]
```

**Parameters:**
- `prompt` - The user's question or instruction
- `system_prompts` - Optional list of system prompts to customize behavior
- `model` - Optional model override (default uses settings)

**Returns:** AsyncIterator yielding response tokens

**Example:**
```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message, end="", flush=True)

anyio.run(main)
```

**Use When:**
- Simple one-shot queries
- No session state needed
- No custom tools required
- Streaming is acceptable

**Don't Use When:**
- Need multi-turn conversations
- Need custom tools or hooks
- Need session management

---

## ClaudeSDKClient

Full-featured client for interactive, stateful conversations with custom tools and hooks.

### Constructor

```python
ClaudeSDKClient(
    session_id: str | None = None,
    system_prompts: list[str] | None = None,
    setting_sources: list[str] | None = None,
    tools: list[Tool] | None = None,
    mcp_servers: dict | None = None,
    session_hooks: SessionHook | None = None,
    model: str | None = None
)
```

**Parameters:**

- `session_id` - Resume existing session (default: create new)
- `system_prompts` - Custom system prompts for agent behavior
- `setting_sources` - Load settings from: `["project"]` to load from `.claude/` directory
- `tools` - List of custom Python tools (in-process MCP servers)
- `mcp_servers` - External MCP server configurations
- `session_hooks` - Lifecycle hooks (on_start, on_end)
- `model` - Model override (e.g., "claude-sonnet-4-20250514")

### Methods

#### `send_message()`

Send a message and get complete response.

```python
async def send_message(self, message: str) -> str
```

**Example:**
```python
async with ClaudeSDKClient() as client:
    response = await client.send_message("Hello!")
    print(response)
```

#### `send_message_stream()`

Send a message and stream response tokens.

```python
async def send_message_stream(self, message: str) -> AsyncIterator[str]
```

**Example:**
```python
async with ClaudeSDKClient() as client:
    async for token in client.send_message_stream("Hello!"):
        print(token, end="", flush=True)
```

### Properties

- `session_id` - Current session ID (for resuming later)
- `message_history` - List of messages in current session

---

## Types

### Tool

Custom Python function exposed as a tool for Claude to invoke.

```python
@dataclass
class Tool:
    definition: ToolDefinition
    handler: Callable
    hooks: ToolUseHook | None = None
```

**Components:**
- `definition` - Tool metadata (name, description, parameters)
- `handler` - Async function implementing the tool
- `hooks` - Optional pre/post hooks for monitoring/enforcement

**Example:**
```python
from claude_agent_sdk.types import Tool, ToolDefinition, ToolParameter

async def calculate(a: float, b: float, operation: str) -> float:
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b

tool = Tool(
    definition=ToolDefinition(
        name="calculate",
        description="Perform arithmetic operations",
        parameters=[
            ToolParameter(name="a", type="number", required=True),
            ToolParameter(name="b", type="number", required=True),
            ToolParameter(
                name="operation",
                type="string",
                description="Operation: 'add' or 'multiply'",
                required=True
            )
        ]
    ),
    handler=calculate
)
```

### ToolDefinition

Describes a tool's interface.

```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: list[ToolParameter]
```

### ToolParameter

Defines a tool parameter.

```python
@dataclass
class ToolParameter:
    name: str
    type: str  # "string", "number", "integer", "boolean", "object", "array"
    description: str | None = None
    required: bool = False
    default: any = None
```

### ToolUseHook

Hooks for monitoring/enforcing tool usage.

```python
@dataclass
class ToolUseHook:
    pre_use: Callable[[str, dict], dict] | None = None
    post_use: Callable[[str, dict, any], None] | None = None
```

**Signatures:**
```python
async def pre_use(tool_name: str, parameters: dict) -> dict:
    # Called before tool invocation
    # Can modify parameters
    # Can raise exception to prevent invocation
    return parameters

async def post_use(tool_name: str, parameters: dict, result: any) -> None:
    # Called after tool completes
    # For logging, auditing, etc.
    pass
```

### SessionHook

Hooks for session lifecycle events.

```python
@dataclass
class SessionHook:
    on_start: Callable[[str], None] | None = None
    on_end: Callable[[str], None] | None = None
```

**Signatures:**
```python
async def on_start(session_id: str) -> None:
    # Called when session starts
    pass

async def on_end(session_id: str) -> None:
    # Called when session ends
    pass
```

---

## MCP Server Configuration

MCP servers are configured as a dictionary:

```python
mcp_servers = {
    "server_name": {
        "command": str,      # Executable command
        "args": list[str],   # Command arguments
        "env": dict | None   # Environment variables
    }
}
```

**Example:**
```python
mcp_servers = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": "ghp_xxx"}
    }
}

async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
    # Claude can now use tools from both MCP servers
    pass
```

---

## Authentication

### API Key (Default)

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Amazon Bedrock

```bash
export CLAUDE_CODE_USE_BEDROCK=1
# Configure AWS credentials separately
```

### Google Vertex AI

```bash
export CLAUDE_CODE_USE_VERTEX=1
# Configure Google Cloud credentials separately
```

---

## Settings and Configuration

### Project Settings

Create `.claude/` directory in your project:

```
project/
├── .claude/
│   ├── settings.json          # Project settings
│   ├── system_prompts.md      # Custom system prompts
│   └── skills/                # Project-specific skills
└── your_code.py
```

Load with:
```python
async with ClaudeSDKClient(setting_sources=["project"]) as client:
    # Loads settings from .claude/ directory
    pass
```

### Settings File Format

`.claude/settings.json`:
```json
{
  "model": "claude-sonnet-4-20250514",
  "temperature": 0.7,
  "max_tokens": 4096,
  "tools": {
    "allowed": ["bash", "file_read", "file_write"],
    "denied": ["web_search"]
  }
}
```

---

## Error Handling

### Common Exceptions

```python
from claude_agent_sdk.exceptions import (
    ClaudeSDKError,
    AuthenticationError,
    RateLimitError,
    ToolExecutionError
)

try:
    async with ClaudeSDKClient() as client:
        response = await client.send_message("Hello")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except ToolExecutionError as e:
    print(f"Tool failed: {e.tool_name}")
except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

### Tool Error Handling

```python
async def safe_tool(input: str) -> dict:
    try:
        # Tool logic
        return {"result": "success"}
    except Exception as e:
        # Return error in tool response
        return {"error": str(e)}
```

---

## Best Practices

### 1. Use Appropriate API

- **query()**: Simple one-shot queries
- **ClaudeSDKClient**: Everything else

### 2. Custom Tools

- Keep tools focused (single responsibility)
- Provide clear descriptions
- Include examples in description
- Handle errors gracefully
- Return structured data (dicts)

### 3. Hooks

- Use pre_use for validation/enforcement
- Use post_use for logging/auditing
- Don't block in hooks (keep them fast)
- Handle exceptions in hooks

### 4. Session Management

- Save session_id to resume later
- Close sessions explicitly with context manager
- Don't share sessions across users

### 5. MCP Servers

- Validate MCP server availability before use
- Use environment variables for secrets
- Handle connection failures gracefully
- Limit file system access paths

### 6. Performance

- Use streaming for long responses
- Batch related operations in tools
- Cache expensive computations
- Limit tool result sizes
