# Conversational AI Agents Reference

## Contents
- [Architecture Overview](#architecture-overview)
- [Creating Agents](#creating-agents)
- [Configuration](#configuration)
- [Knowledge Bases](#knowledge-bases)
- [Tools Integration](#tools-integration)
- [Workflows](#workflows)
- [WebSocket Connection](#websocket-connection)
- [Analytics & Evaluation](#analytics--evaluation)

## Architecture Overview

ElevenLabs Conversational AI consists of:
1. **ASR (Speech Recognition)**: Converts user speech to text
2. **LLM**: Processes conversation and generates responses
3. **TTS**: Converts responses to speech
4. **Turn-taking Model**: Manages conversation flow and interruptions

```
User Audio → ASR → LLM → TTS → Agent Audio
                ↑
          Knowledge Base + Tools
```

## Creating Agents

### Basic Agent

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

agent = client.conversational_ai.agents.create(
    name="Customer Support",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": """# Personality
You are a friendly customer support agent for TechCorp.

# Goal
Help customers with product questions and troubleshooting.

# Guardrails
- Never discuss competitor products
- Escalate billing issues to humans
- Be concise and helpful"""
            },
            "first_message": "Hi! Welcome to TechCorp support. How can I help you today?",
            "language": "en"
        },
        "asr": {
            "quality": "high",
            "provider": "elevenlabs"
        },
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb",
            "model_id": "eleven_flash_v2_5"
        },
        "turn": {
            "turn_timeout": 10,
            "interrupt_sensitivity": "medium"
        }
    }
)

print(f"Agent ID: {agent.agent_id}")
```

### With LLM Selection

```python
agent = client.conversational_ai.agents.create(
    name="Advanced Agent",
    conversation_config={
        "agent": {
            "prompt": {"prompt": "Your system prompt..."},
            "first_message": "Hello!",
            "language": "en"
        },
        "llm": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514"
        },
        "tts": {
            "voice_id": "voice_id"
        }
    }
)
```

### Available LLMs

| Provider | Models |
|----------|--------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| Anthropic | claude-sonnet-4-20250514 |
| Google | gemini-2.5-pro, gemini-2.5-flash |
| Custom | Any OpenAI-compatible endpoint |

## Configuration

### Turn-taking Settings

```python
"turn": {
    "turn_timeout": 10,          # Seconds before timeout (1-30)
    "interrupt_sensitivity": "medium",  # low/medium/high
    "interrupt_agent_enabled": True,    # Allow user interruptions
    "max_duration_seconds": 1800,       # Max call duration
    "end_call_on_silence_seconds": 30   # Auto-end on silence
}
```

### Voice Settings

```python
"tts": {
    "voice_id": "JBFqnCBsd6RMkjVDRZzb",
    "model_id": "eleven_flash_v2_5",  # Low latency
    "stability": 0.5,
    "similarity_boost": 0.75,
    "optimize_streaming_latency": 3,  # 0-4, higher = lower latency
    "language": "en"  # Override agent language
}
```

### Multi-language Support

```python
agent = client.conversational_ai.agents.create(
    name="Multilingual Agent",
    conversation_config={
        "agent": {
            "prompt": {"prompt": "You are a multilingual assistant..."},
            "language": "en",  # Default language
            "language_detection_enabled": True,
            "supported_languages": ["en", "es", "fr", "de"]
        }
    }
)
```

## Knowledge Bases

### Creating Knowledge Base

```python
# Create knowledge base
kb = client.conversational_ai.knowledge_base.create(
    name="Product Documentation"
)

# Add document
doc = client.conversational_ai.knowledge_base.add_document(
    knowledge_base_id=kb.knowledge_base_id,
    file=open("product_manual.pdf", "rb")
)

# Or from URL
doc = client.conversational_ai.knowledge_base.add_document(
    knowledge_base_id=kb.knowledge_base_id,
    url="https://docs.example.com/manual"
)
```

### Attaching to Agent

```python
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    conversation_config={
        "agent": {
            "prompt": {"prompt": "Use the knowledge base to answer questions..."},
            "knowledge_base": {
                "knowledge_base_id": kb.knowledge_base_id,
                "max_chunks": 5  # Number of chunks to retrieve
            }
        }
    }
)
```

### Limits

| Plan | Max Size | Max Documents |
|------|----------|---------------|
| Non-Enterprise | 20MB | - |
| Enterprise | 1GB | - |

**Note**: RAG adds ~500ms latency per query.

## Tools Integration

### Client Tools

Execute in the user's browser:

```python
agent = client.conversational_ai.agents.create(
    conversation_config={
        "agent": {
            "prompt": {"prompt": "..."},
            "tools": [
                {
                    "type": "client",
                    "name": "showNotification",
                    "description": "Display a notification to the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "type": {"type": "string", "enum": ["info", "warning", "error"]}
                        },
                        "required": ["message"]
                    }
                }
            ]
        }
    }
)
```

### Server Tools (Webhooks)

```python
"tools": [
    {
        "type": "server",
        "name": "lookupOrder",
        "description": "Look up order details by order ID",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        },
        "webhook": {
            "url": "https://api.yoursite.com/orders/lookup",
            "headers": {
                "Authorization": "Bearer ${API_KEY}"
            }
        }
    }
]
```

### MCP Tools

Connect to Model Context Protocol servers:

```python
"tools": [
    {
        "type": "mcp",
        "name": "calendar",
        "description": "Manage calendar events",
        "mcp_server": {
            "url": "https://mcp.calendar.example.com/sse"
        }
    }
]
```

### System Tools

Built-in ElevenLabs tools:

```python
"tools": [
    {
        "type": "system",
        "name": "end_call",
        "description": "End the conversation"
    },
    {
        "type": "system",
        "name": "transfer_call",
        "description": "Transfer to human agent",
        "parameters": {
            "phone_number": "+15551234567"
        }
    },
    {
        "type": "system",
        "name": "language_detection",
        "description": "Detect user's language"
    }
]
```

## Workflows

Visual conversation flows with multiple agents:

### Creating Workflow

```python
workflow = client.conversational_ai.workflows.create(
    name="Support Flow",
    nodes=[
        {
            "id": "greeting",
            "type": "agent",
            "agent_id": greeting_agent.agent_id
        },
        {
            "id": "technical",
            "type": "agent", 
            "agent_id": tech_agent.agent_id
        },
        {
            "id": "billing",
            "type": "agent",
            "agent_id": billing_agent.agent_id
        }
    ],
    edges=[
        {
            "from": "greeting",
            "to": "technical",
            "condition": {
                "type": "llm",
                "prompt": "User has a technical question"
            }
        },
        {
            "from": "greeting",
            "to": "billing",
            "condition": {
                "type": "llm",
                "prompt": "User has a billing question"
            }
        }
    ]
)
```

### Edge Types

| Type | Description |
|------|-------------|
| `unconditional` | Always follow |
| `llm` | LLM evaluates condition |
| `expression` | Code expression |
| `forward` | Continue to next |
| `backward` | Return to previous |

## WebSocket Connection

### Getting Signed URL

```python
# For agent
signed_url = client.conversational_ai.conversations.get_signed_url(
    agent_id=agent.agent_id
)

# For workflow  
signed_url = client.conversational_ai.conversations.get_signed_url(
    workflow_id=workflow.workflow_id
)
```

### Client Connection (JavaScript)

```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
    signedUrl: signedUrl,
    onMessage: (message) => {
        console.log("Agent:", message.text);
    },
    onModeChange: (mode) => {
        console.log("Mode:", mode.mode); // "speaking" | "listening"
    },
    onStatusChange: (status) => {
        console.log("Status:", status);
    },
    onError: (error) => {
        console.error("Error:", error);
    }
});

// End conversation
await conversation.endSession();
```

### Phone Integration

```python
# Assign phone number to agent
client.conversational_ai.agents.assign_phone_number(
    agent_id=agent.agent_id,
    phone_number_id="phone_number_id"
)

# Make outbound call
call = client.conversational_ai.calls.create(
    agent_id=agent.agent_id,
    to_number="+15551234567",
    from_number="+15559876543"
)
```

## Analytics & Evaluation

### Success Criteria

```python
agent = client.conversational_ai.agents.create(
    conversation_config={
        "agent": {
            "prompt": {"prompt": "..."},
            "evaluation": {
                "criteria": [
                    "User's question was answered",
                    "User was satisfied with the response",
                    "No escalation was needed"
                ]
            }
        }
    }
)
```

### Data Collection

```python
"data_collection": {
    "fields": [
        {
            "name": "customer_sentiment",
            "type": "string",
            "description": "Customer sentiment at end of call"
        },
        {
            "name": "issue_resolved",
            "type": "boolean"
        }
    ]
}
```

### Webhooks

```python
# Configure post-call webhook
client.conversational_ai.agents.update(
    agent_id=agent.agent_id,
    webhook_url="https://yoursite.com/webhook",
    webhook_events=["conversation.ended", "conversation.error"]
)
```

### Webhook Payload Validation

```python
import hmac
import hashlib

def validate_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Billing

- Billed per minute of conversation
- Includes ASR, LLM, and TTS usage
- Tool calls may incur additional API costs
