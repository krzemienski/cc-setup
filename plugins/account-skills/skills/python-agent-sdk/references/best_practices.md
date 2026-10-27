# Python Agent SDK Best Practices

Patterns, gotchas, and proven approaches for building production agents.

## Choosing query() vs ClaudeSDKClient

### Use `query()` when:
- Single question/answer
- No session state needed
- No custom tools
- Quick scripts or CLI tools
- Streaming is sufficient

### Use `ClaudeSDKClient` when:
- Multi-turn conversations
- Custom tools needed
- Hooks required
- Session resumption
- More control needed

## Custom Tool Design

### Keep Tools Focused

❌ **Bad - Does too much:**
```python
async def process_data(data: str, action: str, format: str, validate: bool):
    # One tool doing many unrelated things
    pass
```

✅ **Good - Single responsibility:**
```python
async def validate_json(data: str) -> dict:
    # One focused task
    pass

async def format_json(data: str, indent: int) -> str:
    # Another focused task
    pass
```

### Provide Clear Descriptions

❌ **Bad - Vague:**
```python
Tool(
    definition=ToolDefinition(
        name="process",
        description="Process data",
        parameters=[...]
    )
)
```

✅ **Good - Clear and specific:**
```python
Tool(
    definition=ToolDefinition(
        name="validate_json_schema",
        description="Validate JSON data against a schema. Returns validation errors if any. Example: validate_json_schema(data='{...}', schema='{...}')",
        parameters=[...]
    )
)
```

### Return Structured Data

❌ **Bad - String output:**
```python
async def analyze_file(path: str) -> str:
    return "File has 100 lines and 5000 bytes"
```

✅ **Good - Structured dict:**
```python
async def analyze_file(path: str) -> dict:
    return {
        "lines": 100,
        "bytes": 5000,
        "extension": ".py",
        "is_text": True
    }
```

### Handle Errors Gracefully

❌ **Bad - Crashes:**
```python
async def read_file(path: str) -> str:
    return open(path).read()  # Crashes if file missing
```

✅ **Good - Returns error info:**
```python
async def read_file(path: str) -> dict:
    try:
        content = Path(path).read_text()
        return {"content": content, "error": None}
    except FileNotFoundError:
        return {"content": None, "error": "File not found"}
    except Exception as e:
        return {"content": None, "error": str(e)}
```

## Hook Patterns

### Pre-Hooks for Validation

```python
async def validate_parameters(tool_name: str, params: dict) -> dict:
    """Enforce rules before tool execution"""
    if tool_name == "delete_file":
        if params["path"].startswith("/system"):
            raise ValueError("Cannot delete system files")
    return params
```

### Post-Hooks for Logging

```python
async def log_tool_use(tool_name: str, params: dict, result: any):
    """Audit trail for compliance"""
    log_entry = {
        "timestamp": datetime.now(),
        "tool": tool_name,
        "user": get_current_user(),
        "result": "success" if not isinstance(result, dict) or "error" not in result else "error"
    }
    save_to_audit_log(log_entry)
```

### Hooks for Rate Limiting

```python
class RateLimiter:
    def __init__(self, max_calls_per_minute: int = 10):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    async def pre_use(self, tool_name: str, params: dict) -> dict:
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if (now - t).seconds < 60]
        
        if len(self.calls) >= self.max_calls:
            raise ValueError(f"Rate limit exceeded: {self.max_calls}/min")
        
        self.calls.append(now)
        return params
```

## Session Management

### Save Session IDs for Resumption

```python
# Start session
async with ClaudeSDKClient() as client:
    session_id = client.session_id
    # Save to database or file
    save_session_id(user_id, session_id)
    
    response = await client.send_message("Hello")

# Resume later
saved_session_id = load_session_id(user_id)
async with ClaudeSDKClient(session_id=saved_session_id) as client:
    response = await client.send_message("Continue our conversation")
```

### Don't Share Sessions Across Users

❌ **Bad - Security risk:**
```python
# Global session shared by all users
global_client = ClaudeSDKClient()
```

✅ **Good - Per-user sessions:**
```python
# Create session per user
async def get_client_for_user(user_id: str):
    session_id = load_session_id(user_id)
    return ClaudeSDKClient(session_id=session_id)
```

## MCP Server Best Practices

### Validate Server Availability

```python
async def connect_with_validation():
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"]
        }
    }
    
    try:
        async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
            # Verify connection by asking about available tools
            response = await client.send_message(
                "List the tools available from the filesystem MCP server"
            )
            print(f"Connected successfully: {response}")
    except ConnectionError as e:
        print(f"Failed to connect to MCP server: {e}")
        # Fallback logic
```

### Use Environment Variables for Secrets

❌ **Bad - Hardcoded:**
```python
mcp_servers = {
    "github": {
        "env": {"GITHUB_TOKEN": "ghp_abc123"}  # Don't do this!
    }
}
```

✅ **Good - Environment variable:**
```python
import os

mcp_servers = {
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}
    }
}
```

### Limit File System Access

❌ **Bad - Too broad:**
```python
mcp_servers = {
    "filesystem": {
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]  # Root access!
    }
}
```

✅ **Good - Restricted path:**
```python
mcp_servers = {
    "filesystem": {
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/app/data"]
    }
}
```

## Performance Optimization

### Use Streaming for Long Responses

```python
# ❌ Bad - Waits for entire response
response = await client.send_message("Write a long essay...")
print(response)  # User waits...

# ✅ Good - Shows progress
async for token in client.send_message_stream("Write a long essay..."):
    print(token, end="", flush=True)  # Real-time feedback
```

### Batch Operations in Tools

❌ **Bad - Multiple calls:**
```python
for file in files:
    result = await client.send_message(f"Analyze {file}")
```

✅ **Good - Single batched call:**
```python
async def analyze_files_batch(files: list[str]) -> dict:
    results = {}
    for file in files:
        results[file] = analyze_single_file(file)
    return results

# Register as tool and use once
result = await client.send_message(f"Analyze these files: {files}")
```

### Limit Tool Result Sizes

```python
async def search_large_dataset(query: str) -> dict:
    results = perform_search(query)
    
    # ✅ Truncate large results
    if len(results) > 100:
        return {
            "results": results[:100],
            "total_count": len(results),
            "truncated": True
        }
    
    return {"results": results, "truncated": False}
```

## Error Handling Patterns

### Graceful Degradation

```python
async def robust_agent():
    # Try MCP server first
    try:
        mcp_servers = {"filesystem": {...}}
        async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
            response = await client.send_message("List files")
    except ConnectionError:
        # Fall back to custom tool
        tools = [custom_list_files_tool]
        async with ClaudeSDKClient(tools=tools) as client:
            response = await client.send_message("List files")
```

### Retry with Backoff

```python
import asyncio

async def send_with_retry(client, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.send_message(message)
        except RateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## Security Best Practices

### Validate Tool Inputs

```python
async def execute_command(command: str) -> dict:
    # ✅ Whitelist allowed commands
    allowed_commands = {"ls", "pwd", "echo"}
    cmd = command.split()[0]
    
    if cmd not in allowed_commands:
        return {"error": f"Command '{cmd}' not allowed"}
    
    # Execute safely
    result = subprocess.run(command, shell=True, capture_output=True)
    return {"output": result.stdout.decode()}
```

### Sanitize File Paths

```python
async def read_user_file(path: str) -> dict:
    # ✅ Prevent directory traversal
    safe_base = Path("/app/user-data").resolve()
    requested_path = (safe_base / path).resolve()
    
    if not requested_path.is_relative_to(safe_base):
        return {"error": "Access denied"}
    
    return {"content": requested_path.read_text()}
```

### Audit Sensitive Operations

```python
sensitive_operations = ["delete_file", "execute_command", "access_database"]

async def audit_hook(tool_name: str, params: dict, result: any):
    if tool_name in sensitive_operations:
        audit_log = {
            "timestamp": datetime.now(),
            "tool": tool_name,
            "user": get_current_user(),
            "params": params,
            "success": "error" not in result
        }
        save_audit_log(audit_log)
```

## Testing Patterns

### Test Custom Tools Independently

```python
import pytest

@pytest.mark.asyncio
async def test_calculate_tool():
    result = await calculate(10, 5, "add")
    assert result == 15
    
    result = await calculate(10, 5, "multiply")
    assert result == 50
```

### Mock MCP Servers for Testing

```python
@pytest.mark.asyncio
async def test_with_mock_mcp():
    # Don't connect to real MCP servers in tests
    # Use custom tools that mimic MCP behavior
    mock_tools = [create_mock_filesystem_tool()]
    
    async with ClaudeSDKClient(tools=mock_tools) as client:
        response = await client.send_message("List files")
        assert "file1.txt" in response
```

## Common Gotchas

### 1. Forgetting `async`/`await`

❌ **Bad:**
```python
def my_tool(input: str):  # Missing async!
    return process(input)
```

✅ **Good:**
```python
async def my_tool(input: str):
    return process(input)
```

### 2. Not Using Context Manager

❌ **Bad:**
```python
client = ClaudeSDKClient()
response = await client.send_message("Hello")
# Session not closed!
```

✅ **Good:**
```python
async with ClaudeSDKClient() as client:
    response = await client.send_message("Hello")
# Automatically closed
```

### 3. Blocking Operations in Hooks

❌ **Bad:**
```python
async def slow_hook(tool, params):
    time.sleep(5)  # Blocks event loop!
    return params
```

✅ **Good:**
```python
async def fast_hook(tool, params):
    await asyncio.sleep(0.1)  # Non-blocking
    return params
```

### 4. Large Tool Results

❌ **Bad:**
```python
async def read_huge_file(path: str) -> str:
    return Path(path).read_text()  # Could be gigabytes!
```

✅ **Good:**
```python
async def read_file_summary(path: str) -> dict:
    content = Path(path).read_text()
    return {
        "size": len(content),
        "lines": len(content.split('\n')),
        "preview": content[:1000]  # First 1000 chars
    }
```
