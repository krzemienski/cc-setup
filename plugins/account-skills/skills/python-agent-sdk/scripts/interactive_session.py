#!/usr/bin/env python3
"""
Interactive Session Example - Multi-turn Conversations with Claude

Demonstrates using ClaudeSDKClient for stateful, interactive
conversations with session management and context preservation.
"""

import anyio
from claude_agent_sdk import ClaudeSDKClient


async def basic_interactive_session():
    """
    Basic interactive session with multi-turn conversation
    
    Use ClaudeSDKClient when you need:
    - Multi-turn conversations
    - Session state management
    - Custom tools or hooks
    - More control over the interaction
    """
    async with ClaudeSDKClient() as client:
        print("Starting interactive session...")
        print("=" * 60)
        
        # First message
        print("\n[User]: Tell me a joke about Python")
        response = await client.send_message("Tell me a joke about Python")
        print(f"[Claude]: {response}")
        
        # Follow-up message (maintains context)
        print("\n[User]: Explain why it's funny")
        response = await client.send_message("Explain why it's funny")
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)
        print("Session complete!")


async def streaming_interactive_session():
    """
    Interactive session with streaming responses
    
    Shows real-time token streaming for better UX
    """
    async with ClaudeSDKClient() as client:
        print("Starting streaming interactive session...")
        print("=" * 60)
        
        messages = [
            "Write a short story about a debugging adventure",
            "Now make it into a haiku"
        ]
        
        for user_message in messages:
            print(f"\n[User]: {user_message}")
            print("[Claude]: ", end="", flush=True)
            
            # Stream the response token by token
            async for token in client.send_message_stream(user_message):
                print(token, end="", flush=True)
            
            print()  # Newline after streaming completes
        
        print("\n" + "=" * 60)


async def session_with_system_prompt():
    """
    Session with custom system prompt and settings
    """
    # Custom system prompt
    system_prompt = """You are a technical mentor specializing in Python development.
    Always provide practical, actionable advice with code examples."""
    
    async with ClaudeSDKClient(
        system_prompts=[system_prompt],
        setting_sources=["project"]  # Load project-specific settings
    ) as client:
        print("Technical mentor session started...")
        print("=" * 60)
        
        print("\n[User]: How should I structure a Python project?")
        response = await client.send_message(
            "How should I structure a Python project?"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def resumable_session():
    """
    Create a session that can be resumed later
    
    Demonstrates session persistence
    """
    # Start a session and get session ID
    async with ClaudeSDKClient() as client:
        session_id = client.session_id
        print(f"Started session: {session_id}")
        print("=" * 60)
        
        print("\n[User]: Remember that my favorite color is blue")
        response = await client.send_message(
            "Remember that my favorite color is blue"
        )
        print(f"[Claude]: {response}")
        
        print("\n[Saving session ID for later]")
        print(f"Session ID: {session_id}")
    
    # Later: Resume the session
    print("\n\n[Later: Resuming session...]")
    async with ClaudeSDKClient(session_id=session_id) as client:
        print(f"Resumed session: {session_id}")
        print("=" * 60)
        
        print("\n[User]: What's my favorite color?")
        response = await client.send_message("What's my favorite color?")
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run basic interactive session
    anyio.run(basic_interactive_session)
    
    # Uncomment to try other examples:
    # anyio.run(streaming_interactive_session)
    # anyio.run(session_with_system_prompt)
    # anyio.run(resumable_session)
