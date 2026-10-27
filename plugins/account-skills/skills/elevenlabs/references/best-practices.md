# Best Practices Reference

## Contents
- [System Prompt Design](#system-prompt-design)
- [Tool Configuration](#tool-configuration)
- [Architecture Patterns](#architecture-patterns)
- [Voice Selection](#voice-selection)
- [Performance Optimization](#performance-optimization)
- [Testing & Iteration](#testing--iteration)
- [Security & Compliance](#security--compliance)

## System Prompt Design

### Structure Your Prompts

Organize prompts into clear sections:

```
# Personality
You are Alex, a friendly customer support agent for TechCorp. 
You're patient, knowledgeable, and always maintain a positive tone.

# Goal
Help customers resolve their technical issues efficiently.
Collect necessary information to troubleshoot problems.
Escalate complex issues to human agents when needed.

# Guardrails
- Never discuss competitor products
- Don't make promises about refunds or compensation
- Escalate any billing disputes to human agents
- Keep conversations professional and on-topic

# Tone
Friendly but professional. Use simple language.
Avoid jargon unless the customer uses it first.
```

### Be Concise

**Bad:**
```
You are a helpful assistant that should help users with their questions
about our products and services. You should be friendly and helpful and
try to answer their questions as best as you can while being polite.
```

**Good:**
```
You are a TechCorp support agent. Help users troubleshoot product issues.
Be concise, friendly, and escalate billing issues to humans.
```

### Action-Based Instructions

**Bad:**
```
You should try to understand what the user wants.
```

**Good:**
```
Ask clarifying questions when the issue is unclear.
Confirm you understood before providing solutions.
```

### Emphasize Critical Steps

```
# Critical: ALWAYS verify the user's account before discussing order details.
This step is important: Confirm the user's identity with their email or order number.
```

### Input/Output Normalization

Handle spoken vs. written format differences:

```
# Input Normalization
Users may say numbers as words. Convert to digits:
- "one two three" → "123"
- "triple five" → "555"

# Output Normalization
Format responses for speech:
- Say "nine one one" not "911"
- Say "three dollars and fifty cents" not "$3.50"
```

### Dedicated Guardrails Section

```
# Guardrails

## Never Do
- Share internal pricing or discount structures
- Confirm or deny information about other customers
- Make commitments beyond standard policy
- Discuss unreleased features or products

## Always Do
- Verify customer identity before account access
- Log all escalation requests
- Offer callback option for complex issues
```

## Tool Configuration

### Clear Tool Descriptions

**Bad:**
```python
{
    "name": "lookup",
    "description": "Look up stuff"
}
```

**Good:**
```python
{
    "name": "lookupOrder",
    "description": "Retrieve order details including status, items, shipping info, and delivery date. Use when customer asks about their order status or delivery.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "Order ID in format ORD-XXXXXX"
            }
        },
        "required": ["order_id"]
    }
}
```

### Document Tool Usage in Prompt

```
# Available Tools

## lookupOrder
Use to find order details when customer provides order ID.
Always confirm the order ID format (ORD-XXXXXX) before calling.

## checkInventory
Use when customer asks about product availability.
Requires product SKU - ask customer to provide it from product page.

## createTicket
Use for issues requiring follow-up or escalation.
Collect: customer email, issue summary, priority (low/medium/high).
```

### Handle Tool Errors

```
# Error Handling

If a tool returns an error:
1. Apologize for the inconvenience
2. Explain you're having technical difficulties
3. Offer to try again or escalate to human agent
4. Never expose raw error messages to users
```

## Architecture Patterns

### Specialized Agents

Keep agents focused on specific tasks:

```python
# Bad: One agent doing everything
giant_agent = create_agent(
    prompt="Handle sales, support, billing, and technical issues..."
)

# Good: Specialized agents
sales_agent = create_agent(prompt="Handle product inquiries and sales...")
support_agent = create_agent(prompt="Troubleshoot technical issues...")
billing_agent = create_agent(prompt="Handle billing questions...")
```

### Orchestrator Pattern

Use workflows to route between specialists:

```python
workflow = create_workflow(
    nodes=[
        {"id": "router", "type": "agent", "agent_id": router_agent.agent_id},
        {"id": "sales", "type": "agent", "agent_id": sales_agent.agent_id},
        {"id": "support", "type": "agent", "agent_id": support_agent.agent_id}
    ],
    edges=[
        {"from": "router", "to": "sales", "condition": {"type": "llm", "prompt": "User wants to buy something"}},
        {"from": "router", "to": "support", "condition": {"type": "llm", "prompt": "User has technical issue"}}
    ]
)
```

### Clear Handoff Criteria

```
# Handoff Criteria

## Transfer to Sales
- User asks about pricing
- User wants to upgrade plan
- User mentions competitor products

## Transfer to Technical Support
- User reports error messages
- User can't access features
- User needs configuration help

## Transfer to Human
- User explicitly requests human
- Issue unresolved after 3 attempts
- User expresses frustration
```

## Voice Selection

### Match Voice to Use Case

| Use Case | Voice Characteristics |
|----------|----------------------|
| Customer support | Warm, patient, clear |
| Sales | Energetic, confident |
| Narration | Measured, authoritative |
| Assistant | Friendly, conversational |
| IVR/Phone | Clear, professional |

### Voice Consistency

Use the same voice throughout an experience:

```python
# Define voice once
SUPPORT_VOICE = {
    "voice_id": "JBFqnCBsd6RMkjVDRZzb",
    "model_id": "eleven_flash_v2_5",
    "stability": 0.6,
    "similarity_boost": 0.8
}

# Use everywhere
agent = create_agent(tts=SUPPORT_VOICE)
greeting = generate_tts(**SUPPORT_VOICE, text="Welcome!")
```

### Test Voices with Your Content

```python
# Test key phrases before deploying
test_phrases = [
    "Your order ORD-123456 has shipped.",
    "I understand your frustration.",
    "Let me transfer you to a specialist.",
    "Is there anything else I can help with?"
]

for phrase in test_phrases:
    audio = generate_tts(voice_id=voice_id, text=phrase)
    # Listen and evaluate
```

## Performance Optimization

### Latency Optimization

1. **Model Selection**
   ```python
   # Real-time: Use Flash v2.5
   model_id = "eleven_flash_v2_5"  # ~75ms latency
   
   # Quality-critical: Use Multilingual v2
   model_id = "eleven_multilingual_v2"
   ```

2. **Streaming**
   ```python
   # Always stream for real-time
   audio = client.text_to_speech.convert_as_stream(...)
   ```

3. **Voice Settings**
   ```python
   # Avoid style (adds latency)
   voice_settings = {
       "stability": 0.5,
       "similarity_boost": 0.75,
       "style": 0.0  # Keep at 0 for low latency
   }
   ```

4. **Output Format**
   ```python
   # PCM for streaming (no encoding delay)
   output_format = "pcm_16000"
   
   # Opus for WebRTC
   output_format = "opus_16000"
   ```

### RAG Optimization

```python
# RAG adds ~500ms latency

# Minimize chunks
knowledge_base = {
    "max_chunks": 3  # Only retrieve what's needed
}

# Pre-filter content
# Include only relevant documents in knowledge base
```

### Concurrent Processing

```python
# Process long audio in parallel
from concurrent.futures import ThreadPoolExecutor

# Up to 4 concurrent STT requests
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(transcribe_chunk, chunks)
```

## Testing & Iteration

### Define Success Criteria

```python
evaluation = {
    "criteria": [
        "Customer's primary question was answered",
        "No incorrect information was provided",
        "Conversation stayed professional",
        "Appropriate escalation if needed"
    ]
}
```

### Test Systematically

```python
test_scenarios = [
    {
        "name": "Simple inquiry",
        "input": "What are your business hours?",
        "expected": "Provides hours, offers more help"
    },
    {
        "name": "Complex troubleshooting",
        "input": "My app crashes when I try to upload",
        "expected": "Asks clarifying questions, provides steps"
    },
    {
        "name": "Angry customer",
        "input": "This is ridiculous! I've been waiting for days!",
        "expected": "Acknowledges frustration, stays calm, offers solution"
    }
]
```

### Iterate Targeted Changes

1. **Analyze failures** - Review conversations that didn't meet criteria
2. **Identify patterns** - What common issues emerge?
3. **Make one change** - Adjust prompt, tool, or configuration
4. **Test again** - Verify improvement without regression
5. **Document** - Record what worked and what didn't

### Regression Testing

```python
# Use simulation API for automated testing
for scenario in test_scenarios:
    result = client.conversational_ai.simulate(
        agent_id=agent.agent_id,
        scenario=scenario
    )
    assert result.meets_criteria(scenario["expected"])
```

## Security & Compliance

### API Key Management

```python
# Never hardcode
# Bad
client = ElevenLabs(api_key="sk-xxxxx")

# Good
client = ElevenLabs()  # Uses ELEVENLABS_API_KEY env var
```

### Webhook Validation

```python
import hmac
import hashlib

def validate_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# Always validate before processing
if not validate_webhook(request.body, request.headers["X-Signature"], WEBHOOK_SECRET):
    return Response(status=401)
```

### Data Privacy

```python
# Enable zero retention for sensitive data
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    text="Sensitive content",
    request_options={"headers": {"x-zero-retention": "true"}}
)
```

### Enterprise Data Residency

```python
# EU data residency
client = ElevenLabs(
    base_url="https://eu.residency.elevenlabs.io"
)

# India data residency
client = ElevenLabs(
    base_url="https://in.residency.elevenlabs.io"
)
```

### Conversation Privacy

```python
agent = create_agent(
    privacy_config={
        "retention_days": 30,  # Auto-delete after 30 days
        "pii_redaction": True,  # Redact PII in logs
        "recording_enabled": False  # Don't record calls
    }
)
```

### HIPAA Compliance

For healthcare applications:
1. Sign BAA with ElevenLabs
2. Use enterprise tier
3. Enable appropriate data residency
4. Configure zero retention where applicable
5. Implement proper access controls
