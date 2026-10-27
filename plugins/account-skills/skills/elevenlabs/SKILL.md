---
name: elevenlabs
description: Build production voice applications with ElevenLabs API - text-to-speech, speech-to-text, conversational AI agents, voice cloning, and audio generation with Python SDK integration.
license: MIT
---

# ElevenLabs API Skill

Build production voice applications with ElevenLabs: text-to-speech, speech-to-text, conversational AI agents, voice cloning, and audio generation.

## When to Use This Skill

Use this skill when working with:
- **Text-to-Speech (TTS)**: Convert text to natural speech with 5k+ voices in 32 languages
- **Speech-to-Text (STT)**: Transcribe audio with word-level timestamps and speaker diarization
- **Conversational AI Agents**: Build voice-first agents with LLM integration and workflows
- **Voice Management**: Clone voices, design new voices, manage pronunciation
- **Audio Generation**: Sound effects, music, voice changing, dubbing

## Quick Reference

| Capability | Key Endpoint | Reference |
|------------|--------------|-----------|
| Text-to-Speech | `POST /v1/text-to-speech/{voice_id}` | [tts.md](references/tts.md) |
| Speech-to-Text | `POST /v1/speech-to-text` | [stt.md](references/stt.md) |
| Agents | `POST /v1/convai/agents/create` | [agents.md](references/agents.md) |
| Voices | `GET /v1/voices` | [voices.md](references/voices.md) |

## Installation

```bash
pip install elevenlabs
```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="your-api-key")
# Or set ELEVENLABS_API_KEY environment variable
```

## Core Quickstarts

### Text-to-Speech

```python
from elevenlabs import ElevenLabs, play

client = ElevenLabs()

# Generate and play audio
audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    model_id="eleven_multilingual_v2",
    text="Hello! This is a test of ElevenLabs text to speech."
)
play(audio)

# Stream for real-time playback
audio_stream = client.text_to_speech.convert_as_stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5",
    text="Streaming audio for low-latency applications."
)
```

### Speech-to-Text

```python
# Transcribe audio file
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1",
    language_code="en"
)
print(result.text)

# With timestamps and speaker diarization
result = client.speech_to_text.convert(
    file=open("meeting.mp3", "rb"),
    model_id="scribe_v1",
    timestamps_granularity="word",
    diarize=True
)
for word in result.words:
    print(f"[{word.start:.2f}s] Speaker {word.speaker_id}: {word.text}")
```

### Conversational Agent

```python
# Create a voice agent
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": "You are a helpful support agent...",
            },
            "first_message": "Hi! How can I help you today?",
            "language": "en"
        },
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb"
        }
    }
)

# Get signed URL for WebSocket connection
signed_url = client.conversational_ai.conversations.get_signed_url(
    agent_id=agent.agent_id
)
```

## Model Selection Guide

| Model | Latency | Quality | Languages | Best For |
|-------|---------|---------|-----------|----------|
| `eleven_flash_v2_5` | ~75ms | Good | 32 | Real-time, low latency |
| `eleven_turbo_v2_5` | ~250ms | Better | 32 | Balanced performance |
| `eleven_multilingual_v2` | Higher | Best | 29 | Maximum quality |
| `eleven_v3` | Higher | Expressive | 70+ | Dialogue, emotion |

**Selection criteria:**
- **Real-time/streaming**: Use Flash v2.5 (75ms latency)
- **Quality-critical**: Use Multilingual v2
- **Expressive dialogue**: Use v3 (supports directing emotional delivery)
- **Maximum language coverage**: Use v3 (70+ languages)

See [models.md](references/models.md) for detailed model comparison.

## Voice Options

| Type | Description | Use Case |
|------|-------------|----------|
| Default Voices | Curated, optimized | Quick prototyping |
| Voice Library | 5k+ community voices | Wide selection |
| Instant Clone | 30-second sample | Custom voice, fast |
| Professional Clone | Extended training | Production, high fidelity |
| Voice Design | AI-generated from text | Create unique voices |

See [voices.md](references/voices.md) for voice management details.

## Output Formats

| Format | Sample Rates | Use Case |
|--------|--------------|----------|
| `mp3_44100_128` | 44.1kHz | General audio |
| `mp3_22050_32` | 22kHz | Compressed |
| `pcm_16000` | 16kHz | Real-time processing |
| `pcm_44100` | 44.1kHz | High-quality processing |
| `ulaw_8000` | 8kHz | Telephony |
| `opus_16000` | 16kHz | WebRTC/streaming |

## Concurrency & Rate Limits

| Plan | TTS Concurrent | STT Concurrent | Priority |
|------|----------------|----------------|----------|
| Free | 2 | 4 | 3 |
| Starter | 3 | 4 | 4 |
| Creator | 5 | 4 | 5 |
| Enterprise | Elevated | Elevated | 6 |

## Reference Documentation

- **[tts.md](references/tts.md)**: Text-to-Speech API, streaming, voice settings, SSML
- **[stt.md](references/stt.md)**: Speech-to-Text (Scribe), timestamps, diarization
- **[agents.md](references/agents.md)**: Conversational AI, workflows, tools, knowledge bases
- **[voices.md](references/voices.md)**: Voice management, cloning, pronunciation dictionaries
- **[models.md](references/models.md)**: Detailed model comparison and selection
- **[sdk.md](references/sdk.md)**: Python SDK patterns and advanced usage
- **[best-practices.md](references/best-practices.md)**: Prompting, architecture, testing

## Common Patterns

### Error Handling

```python
from elevenlabs import ElevenLabs
from elevenlabs.core import ApiError

client = ElevenLabs()

try:
    audio = client.text_to_speech.convert(
        voice_id="invalid_id",
        text="Test"
    )
except ApiError as e:
    if e.status_code == 401:
        print("Invalid API key")
    elif e.status_code == 422:
        print(f"Validation error: {e.body}")
    elif e.status_code == 429:
        print("Rate limited - retry with backoff")
```

### Async Operations

```python
from elevenlabs import AsyncElevenLabs
import asyncio

async def generate_audio():
    client = AsyncElevenLabs()
    audio = await client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text="Async generation"
    )
    return audio

asyncio.run(generate_audio())
```

### Webhook Validation

```python
import hmac
import hashlib

def validate_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Enterprise Features

- **Data Residency**: EU (`eu.residency.elevenlabs.io`), India (`in.residency.elevenlabs.io`)
- **Zero Retention Mode**: No data stored after processing
- **SSO**: OIDC/SAML integration
- **HIPAA Compliance**: Available with BAA
- **Elevated Limits**: Higher concurrency and rate limits

## Billing

- **TTS**: Billed per character
- **STT**: Billed per minute of audio
- **Agents**: Billed per minute of conversation
- Character counts include spaces and punctuation
