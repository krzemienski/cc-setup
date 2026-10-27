#!/usr/bin/env python3
"""
MCP Integration Example - Connecting MCP Servers via SDK

Demonstrates how to connect and use MCP (Model Context Protocol)
servers through the Python Agent SDK for extended functionality.
"""

import anyio
from claude_agent_sdk import ClaudeSDKClient


async def basic_mcp_connection():
    """
    Example: Connect to an MCP server
    
    MCP servers provide pre-built tools and integrations.
    The SDK handles connection management automatically.
    """
    # MCP server configuration
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
        }
    }
    
    async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
        print("MCP Filesystem Server Demo")
        print("=" * 60)
        
        print("\n[User]: List files in the allowed directory")
        response = await client.send_message(
            "What files are in the directory you have access to?"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def multiple_mcp_servers():
    """
    Example: Using multiple MCP servers simultaneously
    
    You can connect to multiple MCP servers to combine capabilities
    """
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_TOKEN": "your_github_token_here"
            }
        },
        "sqlite": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
        }
    }
    
    async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
        print("Multiple MCP Servers Demo")
        print("=" * 60)
        
        print("\n[User]: What MCP tools do you have available?")
        response = await client.send_message(
            "List all the tools you have available from MCP servers"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def mcp_with_custom_tools():
    """
    Example: Combining MCP servers with custom tools
    
    You can use both MCP servers and custom Python tools together
    """
    from claude_agent_sdk.types import Tool, ToolDefinition, ToolParameter
    
    # Custom tool
    async def summarize_data(data: str) -> str:
        """Custom tool to summarize data"""
        lines = data.split('\n')
        return f"Data summary: {len(lines)} lines, {len(data)} characters"
    
    custom_tools = [
        Tool(
            definition=ToolDefinition(
                name="summarize_data",
                description="Summarize data statistics",
                parameters=[
                    ToolParameter(name="data", type="string", required=True)
                ]
            ),
            handler=summarize_data
        )
    ]
    
    # MCP server
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        }
    }
    
    async with ClaudeSDKClient(
        tools=custom_tools,
        mcp_servers=mcp_servers
    ) as client:
        print("MCP + Custom Tools Demo")
        print("=" * 60)
        
        print("\n[User]: Read a file and summarize it")
        response = await client.send_message(
            "Read the test.txt file and use the summarize_data tool on its contents"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def mcp_server_discovery():
    """
    Example: Discovering available MCP server tools
    
    Useful for understanding what capabilities are available
    """
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"]
        },
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": "your_api_key_here"
            }
        }
    }
    
    async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
        print("MCP Tool Discovery Demo")
        print("=" * 60)
        
        # Ask Claude to explore available tools
        print("\n[User]: What tools are available from the MCP servers?")
        response = await client.send_message(
            "List and describe all the tools available from the connected MCP servers. "
            "Organize them by server."
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def mcp_with_error_handling():
    """
    Example: Proper error handling with MCP servers
    
    Shows how to handle MCP connection failures gracefully
    """
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
        }
    }
    
    try:
        async with ClaudeSDKClient(mcp_servers=mcp_servers) as client:
            print("MCP Error Handling Demo")
            print("=" * 60)
            
            print("\n[User]: Try to access a file")
            response = await client.send_message(
                "Read the contents of test.txt"
            )
            print(f"[Claude]: {response}")
            
            print("\n" + "=" * 60)
    
    except ConnectionError as e:
        print(f"[ERROR] Failed to connect to MCP server: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


async def common_mcp_servers_guide():
    """
    Guide: Common MCP Servers and Their Uses
    
    This is a reference, not an executable example
    """
    examples = {
        "Filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "<directory>"],
            "use_case": "File reading, writing, directory operations"
        },
        "GitHub": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": "<token>"},
            "use_case": "Repository operations, issues, PRs"
        },
        "Git": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-git", "<repo-path>"],
            "use_case": "Git operations (commit, branch, log)"
        },
        "SQLite": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "<db-path>"],
            "use_case": "Database queries and operations"
        },
        "PostgreSQL": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres"],
            "env": {"DATABASE_URL": "<connection-string>"},
            "use_case": "PostgreSQL database operations"
        },
        "Brave Search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": "<api-key>"},
            "use_case": "Web search capabilities"
        },
        "Slack": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {
                "SLACK_BOT_TOKEN": "<token>",
                "SLACK_TEAM_ID": "<team-id>"
            },
            "use_case": "Slack messaging and channel operations"
        },
        "Google Drive": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gdrive"],
            "use_case": "Google Drive file operations"
        }
    }
    
    print("Common MCP Servers Reference")
    print("=" * 60)
    for name, config in examples.items():
        print(f"\n{name}:")
        print(f"  Use case: {config['use_case']}")
        print(f"  Command: {config['command']}")
        print(f"  Args: {' '.join(config['args'])}")
        if 'env' in config:
            print(f"  Environment: {', '.join(config['env'].keys())}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Show common MCP servers guide
    anyio.run(common_mcp_servers_guide)
    
    # Note: The other examples require actual MCP servers to be installed
    # Uncomment and configure with your actual MCP server paths:
    
    # anyio.run(basic_mcp_connection())
    # anyio.run(multiple_mcp_servers())
    # anyio.run(mcp_with_custom_tools())
    # anyio.run(mcp_server_discovery())
    # anyio.run(mcp_with_error_handling())
