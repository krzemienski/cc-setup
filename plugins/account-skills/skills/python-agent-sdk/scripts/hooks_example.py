#!/usr/bin/env python3
"""
Hooks Example - Monitoring and Enforcement with SDK Hooks

Demonstrates using hooks to:
- Monitor tool usage
- Enforce policies
- Log decisions
- Create human-in-the-loop checkpoints
- Track session lifecycle
"""

import anyio
import json
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import (
    Tool, ToolDefinition, ToolParameter,
    ToolUseHook, SessionHook
)


# Logging and monitoring hooks
class ToolUsageLogger:
    """Hook to log all tool usage for auditing"""
    
    def __init__(self):
        self.tool_calls = []
    
    async def pre_tool_use(self, tool_name: str, parameters: dict) -> dict:
        """Called before tool is invoked"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "parameters": parameters,
            "status": "starting"
        }
        self.tool_calls.append(log_entry)
        print(f"\n[PRE-HOOK] Tool '{tool_name}' called with: {parameters}")
        return parameters  # Can modify parameters if needed
    
    async def post_tool_use(self, tool_name: str, parameters: dict, result: any):
        """Called after tool completes"""
        # Update the log entry
        for entry in reversed(self.tool_calls):
            if entry["tool"] == tool_name and entry["status"] == "starting":
                entry["status"] = "completed"
                entry["result"] = str(result)[:100]  # Truncate for logging
                break
        
        print(f"[POST-HOOK] Tool '{tool_name}' completed")
    
    def get_audit_log(self):
        """Return complete audit log"""
        return json.dumps(self.tool_calls, indent=2)


class PolicyEnforcer:
    """Hook to enforce business rules and policies"""
    
    def __init__(self, max_amount: float = 10000):
        self.max_amount = max_amount
        self.rejected_calls = []
    
    async def pre_tool_use(self, tool_name: str, parameters: dict) -> dict:
        """Enforce policy before tool execution"""
        # Example: Prevent large financial transactions
        if tool_name == "process_payment" and "amount" in parameters:
            amount = parameters["amount"]
            if amount > self.max_amount:
                self.rejected_calls.append({
                    "tool": tool_name,
                    "amount": amount,
                    "limit": self.max_amount,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"\n[POLICY] ❌ Rejected: ${amount} exceeds limit ${self.max_amount}")
                raise ValueError(
                    f"Payment amount ${amount} exceeds maximum allowed ${self.max_amount}"
                )
        
        return parameters


class SessionLifecycleMonitor:
    """Hook to monitor session lifecycle"""
    
    async def on_session_start(self, session_id: str):
        """Called when session starts"""
        print(f"\n[SESSION] ✓ Session started: {session_id}")
        print(f"[SESSION] Timestamp: {datetime.now().isoformat()}")
    
    async def on_session_end(self, session_id: str):
        """Called when session ends"""
        print(f"\n[SESSION] ✓ Session ended: {session_id}")
        print(f"[SESSION] Duration: {datetime.now().isoformat()}")


# Example tools for demonstration
async def process_payment(amount: float, recipient: str) -> dict:
    """Process a payment (demo tool)"""
    return {
        "status": "success",
        "amount": amount,
        "recipient": recipient,
        "transaction_id": f"TXN-{int(amount)}"
    }


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email (demo tool)"""
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message_id": f"MSG-{hash(subject)}"
    }


async def logging_hooks_example():
    """
    Example: Using hooks to log all tool usage
    """
    logger = ToolUsageLogger()
    
    tools = [
        Tool(
            definition=ToolDefinition(
                name="process_payment",
                description="Process a payment transaction",
                parameters=[
                    ToolParameter(name="amount", type="number", required=True),
                    ToolParameter(name="recipient", type="string", required=True)
                ]
            ),
            handler=process_payment,
            hooks=ToolUseHook(
                pre_use=logger.pre_tool_use,
                post_use=logger.post_tool_use
            )
        ),
        Tool(
            definition=ToolDefinition(
                name="send_email",
                description="Send an email message",
                parameters=[
                    ToolParameter(name="to", type="string", required=True),
                    ToolParameter(name="subject", type="string", required=True),
                    ToolParameter(name="body", type="string", required=True)
                ]
            ),
            handler=send_email,
            hooks=ToolUseHook(
                pre_use=logger.pre_tool_use,
                post_use=logger.post_tool_use
            )
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Tool Usage Logging Demo")
        print("=" * 60)
        
        response = await client.send_message(
            "Send an email to john@example.com saying 'Meeting at 3pm' "
            "and process a $50 payment to Alice"
        )
        print(f"\n[Claude]: {response}")
        
        print("\n" + "=" * 60)
        print("\n[AUDIT LOG]")
        print(logger.get_audit_log())


async def policy_enforcement_example():
    """
    Example: Using hooks to enforce business rules
    """
    enforcer = PolicyEnforcer(max_amount=100.0)  # $100 limit
    
    tools = [
        Tool(
            definition=ToolDefinition(
                name="process_payment",
                description="Process a payment transaction",
                parameters=[
                    ToolParameter(name="amount", type="number", required=True),
                    ToolParameter(name="recipient", type="string", required=True)
                ]
            ),
            handler=process_payment,
            hooks=ToolUseHook(pre_use=enforcer.pre_tool_use)
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Policy Enforcement Demo")
        print("=" * 60)
        
        # This should succeed
        print("\n[User]: Process a $50 payment to Bob")
        response = await client.send_message("Process a $50 payment to Bob")
        print(f"[Claude]: {response}")
        
        # This should be rejected
        print("\n[User]: Process a $500 payment to Alice")
        try:
            response = await client.send_message("Process a $500 payment to Alice")
            print(f"[Claude]: {response}")
        except Exception as e:
            print(f"[ERROR]: {e}")
        
        print("\n" + "=" * 60)


async def session_lifecycle_example():
    """
    Example: Monitoring session lifecycle
    """
    lifecycle_monitor = SessionLifecycleMonitor()
    
    async with ClaudeSDKClient(
        session_hooks=SessionHook(
            on_start=lifecycle_monitor.on_session_start,
            on_end=lifecycle_monitor.on_session_end
        )
    ) as client:
        print("Session Lifecycle Demo")
        print("=" * 60)
        
        print("\n[User]: Hello!")
        response = await client.send_message("Hello!")
        print(f"[Claude]: {response}")
        
        print("\n[User]: Goodbye!")
        response = await client.send_message("Goodbye!")
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def combined_hooks_example():
    """
    Example: Combining multiple hook types
    """
    logger = ToolUsageLogger()
    enforcer = PolicyEnforcer(max_amount=100.0)
    lifecycle = SessionLifecycleMonitor()
    
    tools = [
        Tool(
            definition=ToolDefinition(
                name="process_payment",
                description="Process a payment transaction",
                parameters=[
                    ToolParameter(name="amount", type="number", required=True),
                    ToolParameter(name="recipient", type="string", required=True)
                ]
            ),
            handler=process_payment,
            hooks=ToolUseHook(
                pre_use=lambda tool, params: (
                    enforcer.pre_tool_use(tool, params)
                    and logger.pre_tool_use(tool, params)
                ),
                post_use=logger.post_tool_use
            )
        )
    ]
    
    async with ClaudeSDKClient(
        tools=tools,
        session_hooks=SessionHook(
            on_start=lifecycle.on_session_start,
            on_end=lifecycle.on_session_end
        )
    ) as client:
        print("Combined Hooks Demo")
        print("=" * 60)
        
        response = await client.send_message("Process a $75 payment to Charlie")
        print(f"\n[Claude]: {response}")
        
        print("\n" + "=" * 60)
        print("\n[FINAL AUDIT LOG]")
        print(logger.get_audit_log())


if __name__ == "__main__":
    # Run logging example
    anyio.run(logging_hooks_example)
    
    # Uncomment to try other examples:
    # anyio.run(policy_enforcement_example)
    # anyio.run(session_lifecycle_example)
    # anyio.run(combined_hooks_example)
