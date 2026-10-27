#!/usr/bin/env python3
"""
Simple Query Example - Basic Python Agent SDK Usage

This demonstrates the simplest way to use the Python Agent SDK
for one-shot queries without needing session management.
"""

import anyio
from claude_agent_sdk import query


async def simple_query_example():
    """
    Basic query example - streams responses from Claude
    
    Use this pattern when you need:
    - Simple one-shot queries
    - No session state
    - No custom tools
    - Streaming responses
    """
    prompt = "What is 2 + 2? Explain your reasoning."
    
    print("Sending query to Claude...")
    print("-" * 50)
    
    async for message in query(prompt=prompt):
        print(message, end="", flush=True)
    
    print("\n" + "-" * 50)
    print("Query complete!")


async def query_with_system_prompt():
    """
    Query with custom system prompt
    """
    prompt = "Write a haiku about Python"
    system_prompt = "You are a poetic assistant who specializes in technical poetry."
    
    print("Query with custom system prompt...")
    print("-" * 50)
    
    async for message in query(
        prompt=prompt,
        system_prompts=[system_prompt]
    ):
        print(message, end="", flush=True)
    
    print("\n" + "-" * 50)


if __name__ == "__main__":
    # Run simple query
    anyio.run(simple_query_example)
    
    # Run with system prompt
    # anyio.run(query_with_system_prompt)
