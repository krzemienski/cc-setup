#!/usr/bin/env python3
"""
Custom Tool Example - Creating In-Process MCP Tools

Demonstrates how to create custom Python functions that Claude
can invoke as tools. These are in-process MCP servers that run
directly in your Python application.
"""

import anyio
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import Tool, ToolDefinition, ToolParameter


# Define a custom tool using a Python function
async def calculate_mortgage(
    principal: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    Calculate monthly mortgage payment
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate (e.g., 3.5 for 3.5%)
        years: Loan term in years
    
    Returns:
        Dictionary with payment details
    """
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / ((1 + monthly_rate) ** num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "rate": annual_rate,
        "term_years": years
    }


async def validate_code(code: str, language: str = "python") -> dict:
    """
    Validate code syntax and style
    
    Args:
        code: Source code to validate
        language: Programming language (default: python)
    
    Returns:
        Validation results
    """
    issues = []
    
    # Simple validation example
    if language == "python":
        if "import *" in code:
            issues.append("Avoid wildcard imports (import *)")
        if "\t" in code:
            issues.append("Use spaces instead of tabs")
        if "print(" in code and "# debug" not in code.lower():
            issues.append("Remove debug print statements")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "language": language,
        "lines": len(code.split("\n"))
    }


async def basic_custom_tool_example():
    """
    Example: Using custom tools with Claude
    """
    # Create tool definitions
    tools = [
        Tool(
            definition=ToolDefinition(
                name="calculate_mortgage",
                description="Calculate monthly mortgage payment and total interest",
                parameters=[
                    ToolParameter(
                        name="principal",
                        type="number",
                        description="Loan amount in dollars",
                        required=True
                    ),
                    ToolParameter(
                        name="annual_rate",
                        type="number",
                        description="Annual interest rate (e.g., 3.5 for 3.5%)",
                        required=True
                    ),
                    ToolParameter(
                        name="years",
                        type="integer",
                        description="Loan term in years",
                        required=True
                    )
                ]
            ),
            handler=calculate_mortgage
        ),
        Tool(
            definition=ToolDefinition(
                name="validate_code",
                description="Validate code syntax and style issues",
                parameters=[
                    ToolParameter(
                        name="code",
                        type="string",
                        description="Source code to validate",
                        required=True
                    ),
                    ToolParameter(
                        name="language",
                        type="string",
                        description="Programming language (default: python)",
                        required=False
                    )
                ]
            ),
            handler=validate_code
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Custom Tools Demo")
        print("=" * 60)
        
        # Claude can now use these tools
        print("\n[User]: Calculate my mortgage payment for a $300,000 loan")
        print("        at 3.5% interest over 30 years")
        response = await client.send_message(
            "Calculate my mortgage payment for a $300,000 loan at 3.5% interest over 30 years"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)
        print("\n[User]: Validate this Python code:")
        code_sample = """
from module import *

def my_function():
\tprint("Hello")
\treturn 42
"""
        response = await client.send_message(
            f"Validate this Python code:\n```python\n{code_sample}\n```"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def tool_with_streaming():
    """
    Custom tools work with streaming responses too
    """
    tools = [
        Tool(
            definition=ToolDefinition(
                name="calculate_mortgage",
                description="Calculate monthly mortgage payment",
                parameters=[
                    ToolParameter(name="principal", type="number", required=True),
                    ToolParameter(name="annual_rate", type="number", required=True),
                    ToolParameter(name="years", type="integer", required=True)
                ]
            ),
            handler=calculate_mortgage
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Streaming with Custom Tools")
        print("=" * 60)
        
        print("\n[User]: What would my monthly payment be for different loan amounts?")
        print("[Claude]: ", end="", flush=True)
        
        async for token in client.send_message_stream(
            "What would my monthly payment be for a $200k loan vs $400k loan, "
            "both at 4% for 30 years?"
        ):
            print(token, end="", flush=True)
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run basic custom tool example
    anyio.run(basic_custom_tool_example)
    
    # Uncomment to try streaming:
    # anyio.run(tool_with_streaming)
