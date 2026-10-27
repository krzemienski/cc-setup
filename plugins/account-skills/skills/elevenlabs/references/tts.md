# Text-to-Speech Reference

## Contents
- [API Endpoints](#api-endpoints)
- [Voice Settings](#voice-settings)
- [Streaming](#streaming)
- [Prompting & Expression](#prompting--expression)
- [Pronunciation Control](#pronunciation-control)
- [Output Formats](#output-formats)

## API Endpoints

### Convert Text to Speech

```python
# Standard generation
audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    text="Text to convert",
    voice_settings={
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    },
    output_format="mp3_44100_128"
)

# Save to file
with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### Streaming

```python
# Stream for real-time playback
audio_stream = client.text_to_speech.convert_as_stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5",  # Use Flash for lowest latency
    text="Streaming audio content",
    output_format="pcm_16000"  # Raw PCM for real-time
)

for chunk in audio_stream:
    # Process/play chunk immediately
    process_audio(chunk)
```

### Input Streaming (Chunked Text)

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

def text_generator():
    yield "Hello, "
    yield "this is "
    yield "chunked input."

# Stream text input, stream audio output
audio_stream = client.text_to_speech.convert_with_timestamps(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5",
    text=text_generator(),
    enable_streaming=True
)
```

## Voice Settings

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `stability` | 0.0-1.0 | 0.5 | Higher = more consistent, lower = more expressive |
| `similarity_boost` | 0.0-1.0 | 0.75 | Higher = closer to original voice |
| `style` | 0.0-1.0 | 0.0 | Exaggerates voice style (increases latency) |
| `use_speaker_boost` | bool | True | Enhances voice similarity |
| `speed` | 0.7-1.2 | 1.0 | Playback speed (v2.5+ only) |

```python
voice_settings = {
    "stability": 0.3,        # More expressive
    "similarity_boost": 0.9,  # High fidelity to voice
    "style": 0.2,            # Slight style boost
    "use_speaker_boost": True,
    "speed": 1.1             # Slightly faster
}
```

**Stability guidelines:**
- 0.0-0.3: Maximum variability, emotional range
- 0.3-0.5: Balanced expression
- 0.5-0.7: Consistent but natural
- 0.7-1.0: Maximum consistency, robotic at extremes

## Prompting & Expression

### Text-Based Emotion Direction (v3)

v3 model responds to emotional context in surrounding text:

```python
# Direct emotion in text
texts = [
    "(Excited) I can't believe we won!",
    "(Sad) I'm sorry for your loss.",
    "(Whisper) Don't tell anyone, but...",
    "*laughs* That's hilarious!",
    "WHAT?! That's incredible!"
]
```

### SSML Support

```python
# Break tags for pauses
text = 'Hello! <break time="1.0s" /> This is after a pause.'

# Phoneme tags (Turbo v2 only, English)
text = 'The word <phoneme alphabet="cmu" ph="T AH0 M EY1 T OW2">tomato</phoneme> sounds different.'
```

**Break tag options:**
- `<break time="0.5s" />` - Specific duration
- `<break strength="weak" />` - Weak pause
- `<break strength="medium" />` - Medium pause  
- `<break strength="strong" />` - Strong pause
- `<break strength="x-strong" />` - Extra strong pause

## Pronunciation Control

### Pronunciation Dictionaries

```python
# Create dictionary
dictionary = client.pronunciation_dictionaries.add_from_file(
    name="Technical Terms",
    file=open("pronunciations.pls", "rb")
)

# PLS format example:
# <?xml version="1.0" encoding="UTF-8"?>
# <lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon">
#   <lexeme><grapheme>API</grapheme><phoneme>ˈeɪ.piˌaɪ</phoneme></lexeme>
# </lexicon>

# Use dictionary in TTS
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    text="The API is working.",
    pronunciation_dictionary_locators=[
        {"pronunciation_dictionary_id": dictionary.id}
    ]
)
```

### Phoneme Notation

| System | Format | Example |
|--------|--------|---------|
| IPA | International Phonetic Alphabet | `/təˈmeɪtoʊ/` |
| CMU | ARPABET | `T AH0 M EY1 T OW2` |

## Output Formats

### Audio Formats

| Format | Quality | Size | Use Case |
|--------|---------|------|----------|
| `mp3_44100_128` | High | Medium | General distribution |
| `mp3_44100_64` | Medium | Small | Bandwidth-limited |
| `mp3_22050_32` | Lower | Smallest | Maximum compression |
| `pcm_16000` | Lossless | Large | Real-time processing |
| `pcm_24000` | Lossless | Larger | Higher quality processing |
| `pcm_44100` | Lossless | Largest | Studio quality |
| `ulaw_8000` | Telephony | Small | Phone systems |
| `alaw_8000` | Telephony | Small | European phone systems |
| `opus_16000` | Good | Small | WebRTC/streaming |
| `opus_24000` | Better | Small | Quality streaming |

### With Timestamps

```python
result = client.text_to_speech.convert_with_timestamps(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="Get word-level timing.",
    model_id="eleven_flash_v2_5"
)

# Access alignment data
for alignment in result.alignment:
    print(f"{alignment.char_start_times_ms}: {alignment.chars}")
```

## Character Limits

| Model | Max Characters |
|-------|----------------|
| eleven_v3 | 5,000 |
| eleven_multilingual_v2 | 10,000 |
| eleven_turbo_v2_5 | 40,000 |
| eleven_flash_v2_5 | 40,000 |

## Latency Optimization

1. **Model Selection**: Use Flash v2.5 for minimum latency (~75ms)
2. **Streaming**: Use `convert_as_stream()` for real-time playback
3. **Format**: Use PCM or Opus for streaming (no MP3 encoding delay)
4. **Text Chunking**: Stream text input for long content
5. **Voice Settings**: Avoid `style > 0` (adds latency)

```python
# Optimized for lowest latency
audio = client.text_to_speech.convert_as_stream(
    voice_id="voice_id",
    model_id="eleven_flash_v2_5",
    output_format="pcm_16000",
    voice_settings={
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0  # No style processing
    },
    text="Low latency audio"
)
```

## Projects (Long-form Audio)

```python
# Create project for audiobooks/podcasts
project = client.projects.create(
    name="My Audiobook",
    default_title_voice_id="voice_id",
    default_paragraph_voice_id="voice_id",
    default_model_id="eleven_multilingual_v2"
)

# Add chapters
chapter = client.projects.chapters.create(
    project_id=project.project_id,
    name="Chapter 1",
    content="Chapter content here..."
)

# Convert entire project
client.projects.convert(project_id=project.project_id)
```
