# Speech-to-Text Reference (Scribe)

## Contents
- [Models](#models)
- [Basic Transcription](#basic-transcription)
- [Timestamps & Diarization](#timestamps--diarization)
- [Real-time Streaming](#real-time-streaming)
- [Large Files](#large-files)
- [Language Detection](#language-detection)

## Models

| Model | Languages | Latency | Best For |
|-------|-----------|---------|----------|
| `scribe_v1` | 99 | Batch | High accuracy, batch processing |
| `scribe_v2_realtime` | 90 | ~150ms | Live transcription |

## Basic Transcription

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

# From file
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1",
    language_code="en"  # Optional, auto-detected if omitted
)

print(result.text)
```

### From URL

```python
result = client.speech_to_text.convert(
    audio_url="https://example.com/audio.mp3",
    model_id="scribe_v1"
)
```

### Supported Formats

- **Audio**: MP3, WAV, FLAC, OGG, M4A, AAC, WMA, AIFF
- **Video**: MP4, MKV, AVI, MOV, WebM (audio extracted automatically)
- **Max size**: 3GB
- **Max duration**: 10 hours

## Timestamps & Diarization

### Word-level Timestamps

```python
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1",
    timestamps_granularity="word"
)

for word in result.words:
    print(f"[{word.start:.2f}s - {word.end:.2f}s] {word.text}")
```

### Speaker Diarization

Identify and separate up to 32 speakers:

```python
result = client.speech_to_text.convert(
    file=open("meeting.mp3", "rb"),
    model_id="scribe_v1",
    diarize=True,
    timestamps_granularity="word"
)

# Group by speaker
current_speaker = None
for word in result.words:
    if word.speaker_id != current_speaker:
        current_speaker = word.speaker_id
        print(f"\n[Speaker {current_speaker}]")
    print(word.text, end=" ")
```

### Timestamp Granularity Options

| Value | Description |
|-------|-------------|
| `"none"` | No timestamps |
| `"word"` | Per-word timing |
| `"segment"` | Per-segment timing |

## Real-time Streaming

For live audio transcription using Scribe v2:

```python
import asyncio
import websockets
import json

async def realtime_transcription():
    uri = "wss://api.elevenlabs.io/v1/speech-to-text/stream"
    
    headers = {"xi-api-key": "your-api-key"}
    
    async with websockets.connect(uri, extra_headers=headers) as ws:
        # Send configuration
        await ws.send(json.dumps({
            "type": "config",
            "model_id": "scribe_v2_realtime",
            "language_code": "en",
            "sample_rate": 16000
        }))
        
        # Stream audio chunks
        async def send_audio():
            # Your audio source here
            while True:
                chunk = get_audio_chunk()  # 16-bit PCM
                await ws.send(chunk)
        
        # Receive transcriptions
        async def receive_transcripts():
            async for message in ws:
                data = json.loads(message)
                if data["type"] == "transcript":
                    print(data["text"])
        
        await asyncio.gather(send_audio(), receive_transcripts())
```

### WebSocket Message Types

**Sent:**
- `config`: Initial configuration
- Binary audio: Raw PCM chunks

**Received:**
- `transcript`: Partial/final transcription
- `error`: Error message

## Large Files

### Chunked Processing

For files longer than 8 minutes, use chunked processing for faster results:

```python
import concurrent.futures
from pydub import AudioSegment

def transcribe_chunk(chunk_data, chunk_index):
    result = client.speech_to_text.convert(
        file=chunk_data,
        model_id="scribe_v1"
    )
    return chunk_index, result.text

# Split audio into chunks
audio = AudioSegment.from_mp3("long_audio.mp3")
chunk_duration = 5 * 60 * 1000  # 5 minutes in ms
chunks = [audio[i:i+chunk_duration] for i in range(0, len(audio), chunk_duration)]

# Process up to 4 chunks concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for i, chunk in enumerate(chunks):
        chunk_bytes = chunk.export(format="mp3")
        futures.append(executor.submit(transcribe_chunk, chunk_bytes, i))
    
    # Collect results in order
    results = sorted([f.result() for f in futures], key=lambda x: x[0])
    full_transcript = " ".join([r[1] for r in results])
```

## Language Detection

```python
# Auto-detect language
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1"
    # Omit language_code for auto-detection
)

print(f"Detected language: {result.detected_language}")
```

### Supported Languages (Scribe v1 - 99 languages)

Major languages include: English, Spanish, French, German, Chinese, Japanese, Korean, Portuguese, Italian, Russian, Arabic, Hindi, and 87 more.

## Audio Events Detection

Scribe can detect non-speech audio events:

```python
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1",
    tag_audio_events=True
)

# Audio events appear in transcript as tags
# e.g., "[music]", "[applause]", "[laughter]"
print(result.text)
```

## Output Format

### Response Structure

```python
{
    "text": "Full transcription text",
    "words": [
        {
            "text": "word",
            "start": 0.0,
            "end": 0.5,
            "speaker_id": "speaker_0",  # If diarize=True
            "confidence": 0.98
        }
    ],
    "detected_language": "en",
    "language_probability": 0.99
}
```

## Billing

- Billed per minute of audio (rounded up)
- Minimum charge: 1 minute
- Concurrent processing uses parallel billing

## Concurrency Limits

| Plan | Max Concurrent |
|------|----------------|
| All Plans | 4 |

For files > 8 minutes, you can use up to 4 parallel chunks.
