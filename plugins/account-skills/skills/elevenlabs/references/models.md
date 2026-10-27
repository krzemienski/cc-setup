# Model Comparison Reference

## Contents
- [TTS Models Overview](#tts-models-overview)
- [Model Details](#model-details)
- [Selection Guide](#selection-guide)
- [STT Models](#stt-models)
- [LLM Options for Agents](#llm-options-for-agents)

## TTS Models Overview

| Model ID | Name | Latency | Quality | Languages | Char Limit |
|----------|------|---------|---------|-----------|------------|
| `eleven_flash_v2_5` | Flash v2.5 | ~75ms | Good | 32 | 40,000 |
| `eleven_turbo_v2_5` | Turbo v2.5 | ~250ms | Better | 32 | 40,000 |
| `eleven_multilingual_v2` | Multilingual v2 | Higher | Best | 29 | 10,000 |
| `eleven_v3` | Eleven v3 (Alpha) | Higher | Expressive | 70+ | 5,000 |
| `eleven_monolingual_v1` | Monolingual v1 | Low | Good | 1 (EN) | 10,000 |

## Model Details

### Flash v2.5 (`eleven_flash_v2_5`)

**Best for:** Real-time applications, streaming, low-latency requirements

```python
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    model_id="eleven_flash_v2_5",
    text="Ultra-low latency speech"
)
```

**Characteristics:**
- First byte latency: ~75ms
- Optimized for streaming
- Good quality for most applications
- 32 language support
- Speed control: 0.7-1.2x

**Limitations:**
- Numbers not normalized by default (Enterprise can enable)
- Slightly lower quality than Turbo/Multilingual

---

### Turbo v2.5 (`eleven_turbo_v2_5`)

**Best for:** Balanced latency and quality, general production use

```python
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    model_id="eleven_turbo_v2_5",
    text="Balanced performance speech"
)
```

**Characteristics:**
- First byte latency: ~250ms
- Higher quality than Flash
- Good for pre-generated content
- 32 language support
- Speed control: 0.7-1.2x
- Supports phoneme tags (English only)

**Unique Features:**
- SSML phoneme tags support
- Better number normalization

---

### Multilingual v2 (`eleven_multilingual_v2`)

**Best for:** Maximum quality, non-real-time applications, multi-language

```python
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    model_id="eleven_multilingual_v2",
    text="Premium quality multilingual speech"
)
```

**Characteristics:**
- Highest audio quality
- 29 language support
- Best voice fidelity
- Ideal for audiobooks, podcasts

**Limitations:**
- Higher latency than Flash/Turbo
- Smaller character limit (10k)

---

### Eleven v3 (`eleven_v3`)

**Best for:** Expressive dialogue, emotional content, voice acting

```python
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    model_id="eleven_v3",
    text="(Excited) This is so amazing! *laughs*"
)
```

**Characteristics:**
- Responds to emotional cues in text
- 70+ language support (most extensive)
- Natural conversation flow
- Supports directing delivery via text prompts

**Emotional Direction:**
```python
# Emotion in parentheses
"(Sad) I'm sorry to hear that."
"(Whisper) Don't tell anyone..."
"(Excited) We won!"

# Action markers
"*sighs* Fine, I'll do it."
"*laughs* That's hilarious!"

# Emphasis through caps/punctuation
"WHAT?! That's incredible!"
```

**Limitations:**
- Smallest character limit (5k)
- Professional Voice Clones not optimized (use IVC or designed voices)
- Higher latency
- Alpha status (may change)

---

### Monolingual v1 (`eleven_monolingual_v1`)

**Best for:** English-only applications, legacy compatibility

**Characteristics:**
- English only
- Low latency
- Legacy model

## Selection Guide

### Decision Tree

```
Need lowest latency?
├── Yes → Flash v2.5
└── No
    ├── Need emotional expression?
    │   ├── Yes → Eleven v3
    │   └── No
    │       ├── Need maximum quality?
    │       │   ├── Yes → Multilingual v2
    │       │   └── No → Turbo v2.5
```

### Use Case Recommendations

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| Live conversation | Flash v2.5 | Lowest latency |
| Streaming app | Flash v2.5 | Real-time requirements |
| Audiobook | Multilingual v2 | Maximum quality |
| Podcast | Multilingual v2 | Quality over speed |
| Voice assistant | Flash v2.5 or Turbo v2.5 | Latency-quality balance |
| Video game dialogue | Eleven v3 | Emotional expression |
| Narrator | Multilingual v2 or Turbo v2.5 | Quality + consistency |
| IVR/Phone | Turbo v2.5 | Balanced, clear speech |
| Multilingual app | v3 (70+ langs) or Multilingual v2 | Language coverage |

### Latency vs Quality Trade-off

```
Quality  ^
         |  ████ Multilingual v2
         |  ███ Eleven v3
         |  ██ Turbo v2.5
         |  █ Flash v2.5
         +------------------------->
              Latency (lower is left)
```

## STT Models

### Scribe v1 (`scribe_v1`)

**Best for:** Batch transcription, high accuracy

| Feature | Value |
|---------|-------|
| Languages | 99 |
| Accuracy | Highest |
| Features | Timestamps, diarization, audio events |
| Processing | Batch/file-based |

```python
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v1"
)
```

---

### Scribe v2 Realtime (`scribe_v2_realtime`)

**Best for:** Live transcription, streaming

| Feature | Value |
|---------|-------|
| Languages | 90 |
| Latency | ~150ms |
| Processing | Streaming/real-time |

```python
# Used with WebSocket streaming
# See STT reference for WebSocket implementation
```

## LLM Options for Agents

### Built-in LLMs

| Provider | Model | Characteristics |
|----------|-------|-----------------|
| OpenAI | gpt-4o | High quality, fast |
| OpenAI | gpt-4o-mini | Faster, lower cost |
| OpenAI | gpt-4-turbo | Large context |
| Anthropic | claude-sonnet-4-20250514 | Balanced quality |
| Google | gemini-2.5-pro | High quality |
| Google | gemini-2.5-flash | Fast, efficient |

### Custom LLM

Connect any OpenAI-compatible endpoint:

```python
agent = client.conversational_ai.agents.create(
    conversation_config={
        "llm": {
            "provider": "custom",
            "custom_llm": {
                "url": "https://your-llm.example.com/v1/chat/completions",
                "model": "your-model-name",
                "api_key": "your-api-key"
            }
        }
    }
)
```

### LLM Selection for Agents

| Priority | Recommendation |
|----------|----------------|
| Lowest latency | gpt-4o-mini or gemini-2.5-flash |
| Best quality | gpt-4o or claude-sonnet-4-20250514 |
| Cost efficiency | gpt-4o-mini |
| Large context | gpt-4-turbo |

## Feature Support Matrix

| Feature | Flash v2.5 | Turbo v2.5 | Multi v2 | v3 |
|---------|------------|------------|----------|-----|
| Streaming | ✓ | ✓ | ✓ | ✓ |
| Speed control | ✓ | ✓ | - | - |
| Phoneme tags | - | ✓ (EN) | - | - |
| Emotion direction | - | - | - | ✓ |
| SSML breaks | ✓ | ✓ | ✓ | ✓ |
| PVC optimized | ✓ | ✓ | ✓ | - |
| IVC optimized | ✓ | ✓ | ✓ | ✓ |
