# Python SDK Reference

## Contents
- [Installation](#installation)
- [Authentication](#authentication)
- [Client Configuration](#client-configuration)
- [Async Operations](#async-operations)
- [Error Handling](#error-handling)
- [Streaming Patterns](#streaming-patterns)
- [File Handling](#file-handling)
- [Other SDKs](#other-sdks)

## Installation

```bash
pip install elevenlabs
```

**Optional dependencies:**

```bash
# For audio playback
pip install elevenlabs[audio]

# For async support (included by default)
pip install aiohttp
```

## Authentication

### Environment Variable (Recommended)

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

```python
from elevenlabs import ElevenLabs

# Automatically uses ELEVENLABS_API_KEY
client = ElevenLabs()
```

### Explicit API Key

```python
client = ElevenLabs(api_key="your-api-key")
```

### From Config File

```python
import os
from elevenlabs import ElevenLabs

# Load from .env or config
from dotenv import load_dotenv
load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
```

## Client Configuration

### Custom Base URL

```python
# For data residency (EU)
client = ElevenLabs(
    api_key="your-api-key",
    base_url="https://eu.residency.elevenlabs.io"
)

# For India
client = ElevenLabs(
    api_key="your-api-key",
    base_url="https://in.residency.elevenlabs.io"
)
```

### Timeout Configuration

```python
import httpx

client = ElevenLabs(
    api_key="your-api-key",
    timeout=httpx.Timeout(60.0, connect=10.0)
)
```

### Custom HTTP Client

```python
import httpx

http_client = httpx.Client(
    timeout=60.0,
    limits=httpx.Limits(max_connections=100)
)

client = ElevenLabs(
    api_key="your-api-key",
    httpx_client=http_client
)
```

## Async Operations

### Async Client

```python
from elevenlabs import AsyncElevenLabs
import asyncio

async def generate_audio():
    client = AsyncElevenLabs()
    
    audio = await client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text="Async audio generation"
    )
    
    return audio

result = asyncio.run(generate_audio())
```

### Concurrent Generation

```python
import asyncio
from elevenlabs import AsyncElevenLabs

async def generate_multiple(texts: list[str]):
    client = AsyncElevenLabs()
    
    tasks = [
        client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            text=text
        )
        for text in texts
    ]
    
    results = await asyncio.gather(*tasks)
    return results

texts = ["Hello", "World", "Async is fast"]
audios = asyncio.run(generate_multiple(texts))
```

### Async Streaming

```python
async def stream_audio():
    client = AsyncElevenLabs()
    
    async for chunk in await client.text_to_speech.convert_as_stream(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text="Streaming async audio"
    ):
        process_chunk(chunk)

asyncio.run(stream_audio())
```

## Error Handling

### Exception Types

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
    print(f"Status: {e.status_code}")
    print(f"Body: {e.body}")
    
    if e.status_code == 401:
        print("Invalid or missing API key")
    elif e.status_code == 403:
        print("Forbidden - check permissions")
    elif e.status_code == 404:
        print("Resource not found (invalid voice_id?)")
    elif e.status_code == 422:
        print("Validation error - check parameters")
    elif e.status_code == 429:
        print("Rate limited - implement backoff")
    elif e.status_code >= 500:
        print("Server error - retry later")
```

### Retry Logic

```python
import time
from elevenlabs import ElevenLabs
from elevenlabs.core import ApiError

def generate_with_retry(text: str, max_retries: int = 3):
    client = ElevenLabs()
    
    for attempt in range(max_retries):
        try:
            return client.text_to_speech.convert(
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                text=text
            )
        except ApiError as e:
            if e.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.status_code >= 500:
                wait_time = 2 ** attempt
                print(f"Server error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
    raise Exception("Max retries exceeded")
```

### Async Retry with Tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_audio_reliable(text: str):
    client = AsyncElevenLabs()
    return await client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text=text
    )
```

## Streaming Patterns

### Save Stream to File

```python
def save_audio(text: str, output_path: str):
    client = ElevenLabs()
    
    audio_stream = client.text_to_speech.convert_as_stream(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text=text
    )
    
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
```

### Real-time Playback

```python
from elevenlabs import ElevenLabs, stream

client = ElevenLabs()

audio_stream = client.text_to_speech.convert_as_stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5",
    text="Real-time streaming audio"
)

# Play audio in real-time (requires audio extra)
stream(audio_stream)
```

### Chunked Input Streaming

```python
def text_chunks():
    """Generator yielding text chunks."""
    yield "This is the first part. "
    yield "This is the second part. "
    yield "And finally, the conclusion."

# Stream text in, stream audio out
audio_stream = client.text_to_speech.convert_as_stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text=text_chunks()
)
```

## File Handling

### Audio File Input

```python
# From file path
with open("audio.mp3", "rb") as f:
    result = client.speech_to_text.convert(file=f)

# From bytes
audio_bytes = get_audio_bytes()
result = client.speech_to_text.convert(
    file=("audio.mp3", audio_bytes, "audio/mpeg")
)
```

### Audio File Output

```python
# Generator output - iterate to get bytes
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    text="Hello"
)

# Collect all chunks
audio_bytes = b"".join(audio)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### Voice Clone Files

```python
# Multiple audio files for cloning
voice = client.voices.clone(
    name="My Clone",
    files=[
        open("sample1.mp3", "rb"),
        open("sample2.mp3", "rb"),
        open("sample3.wav", "rb")
    ]
)
```

## Common Patterns

### Voice Lookup by Name

```python
def get_voice_by_name(name: str):
    client = ElevenLabs()
    voices = client.voices.get_all()
    
    for voice in voices.voices:
        if voice.name.lower() == name.lower():
            return voice
    
    raise ValueError(f"Voice '{name}' not found")

# Usage
voice = get_voice_by_name("George")
audio = client.text_to_speech.convert(
    voice_id=voice.voice_id,
    text="Hello!"
)
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_text(item):
    client = ElevenLabs()
    text, output_path = item
    
    audio = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text=text
    )
    
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    return output_path

# Process multiple texts in parallel
items = [
    ("Hello world", "output1.mp3"),
    ("Goodbye world", "output2.mp3"),
    ("Testing audio", "output3.mp3")
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_text, items))
```

## Other SDKs

### JavaScript/TypeScript

```bash
npm install @elevenlabs/elevenlabs-js
```

```typescript
import { ElevenLabs } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabs({
    apiKey: process.env.ELEVENLABS_API_KEY
});

const audio = await client.textToSpeech.convert({
    voiceId: "JBFqnCBsd6RMkjVDRZzb",
    text: "Hello from TypeScript!"
});
```

### React

```bash
npm install @elevenlabs/react
```

```tsx
import { useConversation } from "@elevenlabs/react";

function ConversationComponent() {
    const { status, startConversation, endConversation } = useConversation({
        agentId: "your-agent-id",
        onMessage: (message) => console.log(message)
    });
    
    return (
        <button onClick={status === "idle" ? startConversation : endConversation}>
            {status === "idle" ? "Start" : "End"} Conversation
        </button>
    );
}
```

### Swift (iOS)

```swift
import ElevenLabs

let client = ElevenLabsClient(apiKey: "your-api-key")

let audio = try await client.textToSpeech.convert(
    voiceId: "JBFqnCBsd6RMkjVDRZzb",
    text: "Hello from Swift!"
)
```

### Kotlin (Android)

```kotlin
val client = ElevenLabsClient(apiKey = "your-api-key")

val audio = client.textToSpeech.convert(
    voiceId = "JBFqnCBsd6RMkjVDRZzb",
    text = "Hello from Kotlin!"
)
```
