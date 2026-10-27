# Voice Management Reference

## Contents
- [Voice Types](#voice-types)
- [Browsing Voices](#browsing-voices)
- [Voice Cloning](#voice-cloning)
- [Voice Design](#voice-design)
- [Pronunciation Dictionaries](#pronunciation-dictionaries)
- [Voice Library](#voice-library)

## Voice Types

| Type | Creation Time | Quality | Use Case |
|------|---------------|---------|----------|
| Default | Instant | Excellent | Quick start, prototyping |
| Voice Library | Instant | Varies | Wide selection, community |
| Instant Voice Clone (IVC) | ~30 seconds | Good | Fast custom voice |
| Professional Voice Clone (PVC) | Hours-days | Excellent | Production, high fidelity |
| Voice Design | ~1 minute | Good | Create unique AI voices |

## Browsing Voices

### List All Voices

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

# Get all available voices
voices = client.voices.get_all()

for voice in voices.voices:
    print(f"{voice.name} ({voice.voice_id})")
    print(f"  Category: {voice.category}")
    print(f"  Labels: {voice.labels}")
```

### Get Specific Voice

```python
voice = client.voices.get(voice_id="JBFqnCBsd6RMkjVDRZzb")
print(voice.name)  # "George"
print(voice.settings)
```

### Default Voice Settings

```python
settings = client.voices.get_default_settings()
print(settings.stability)
print(settings.similarity_boost)
```

## Voice Cloning

### Instant Voice Clone (IVC)

Quick cloning from short audio samples:

```python
# Clone from audio file
voice = client.voices.clone(
    name="My Voice Clone",
    files=[
        open("sample1.mp3", "rb"),
        open("sample2.mp3", "rb")  # Multiple samples improve quality
    ],
    description="Clone of my voice"
)

print(f"Voice ID: {voice.voice_id}")

# Use the cloned voice
audio = client.text_to_speech.convert(
    voice_id=voice.voice_id,
    text="Hello from my cloned voice!"
)
```

**IVC Requirements:**
- Minimum: 30 seconds of audio
- Recommended: 1-2 minutes
- Clear audio, minimal background noise
- Single speaker only
- Varied speech patterns (not monotone)

### Professional Voice Clone (PVC)

High-fidelity cloning with extended training:

```python
# Submit for professional cloning
voice = client.voices.clone_professional(
    name="Professional Clone",
    files=[
        open("recording1.wav", "rb"),
        open("recording2.wav", "rb"),
        open("recording3.wav", "rb")
    ],
    description="Professional voice clone for production use"
)

# Status check (training takes time)
status = client.voices.get(voice_id=voice.voice_id)
print(f"Training status: {status.training_status}")
```

**PVC Requirements:**
- Minimum: 30 minutes of audio
- Recommended: 1-3 hours
- Studio quality recordings
- Diverse content and emotions
- Longer training time (hours to days)

**Note:** PVC is not optimized for v3 model. Use IVC or designed voices for v3.

## Voice Design

Create unique AI voices from text descriptions:

```python
# Generate voice from description
voice_preview = client.voice_design.generate_preview(
    text="Hello, this is a preview of my new voice design.",
    voice_description="A warm, friendly female voice with a slight British accent. Professional but approachable.",
    age="middle_aged",
    gender="female",
    accent="british"
)

# If you like the preview, create the voice
voice = client.voice_design.create_voice_from_preview(
    voice_name="Warm British Female",
    voice_description="Professional, warm, British accent",
    preview_id=voice_preview.preview_id
)
```

### Voice Design Parameters

| Parameter | Options |
|-----------|---------|
| `gender` | male, female |
| `age` | young, middle_aged, old |
| `accent` | american, british, australian, indian, etc. |
| `accent_strength` | 0.0-2.0 (subtle to strong) |

## Pronunciation Dictionaries

### Creating Dictionary

```python
# From PLS file
dictionary = client.pronunciation_dictionaries.add_from_file(
    name="Technical Terms",
    file=open("pronunciations.pls", "rb"),
    description="Custom pronunciations for technical terms"
)

# Add individual rules
client.pronunciation_dictionaries.add_rules(
    pronunciation_dictionary_id=dictionary.id,
    rules=[
        {
            "string_to_replace": "API",
            "type": "phoneme",
            "phoneme": "ˈeɪ piː ˈaɪ",
            "alphabet": "ipa"
        },
        {
            "string_to_replace": "SQL",
            "type": "alias",
            "alias": "sequel"
        }
    ]
)
```

### PLS File Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0" 
         xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" 
         xml:lang="en-US">
    <lexeme>
        <grapheme>API</grapheme>
        <phoneme>ˈeɪ piː ˈaɪ</phoneme>
    </lexeme>
    <lexeme>
        <grapheme>SQL</grapheme>
        <alias>sequel</alias>
    </lexeme>
    <lexeme>
        <grapheme>GIF</grapheme>
        <phoneme>dʒɪf</phoneme>
    </lexeme>
</lexicon>
```

### Using Dictionaries

```python
audio = client.text_to_speech.convert(
    voice_id="voice_id",
    text="The API uses SQL to query GIF metadata.",
    pronunciation_dictionary_locators=[
        {
            "pronunciation_dictionary_id": dictionary.id,
            "version_id": dictionary.version_id  # Optional, uses latest if omitted
        }
    ]
)
```

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| `phoneme` | IPA/CMU pronunciation | API → /ˈeɪ piː ˈaɪ/ |
| `alias` | Replace with different text | SQL → "sequel" |

### Phoneme Notation

**IPA (International Phonetic Alphabet):**
```
tomato → /təˈmeɪtoʊ/
```

**CMU (ARPABET):**
```
tomato → T AH0 M EY1 T OW2
```
Numbers indicate stress: 0 = no stress, 1 = primary, 2 = secondary

## Voice Library

### Browse Community Voices

```python
# Search voice library
voices = client.voices.get_shared_voices(
    page_size=20,
    search="narrator",
    gender="male",
    age="middle_aged",
    language="en",
    use_cases=["narration", "audiobook"]
)

for voice in voices.voices:
    print(f"{voice.name}: {voice.description}")
```

### Add Library Voice

```python
# Add shared voice to your account
voice = client.voices.add_shared_voice(
    public_user_id="public_user_id",
    voice_id="shared_voice_id",
    new_name="My Narrator Voice"
)
```

### Share Your Voice

```python
# Share voice to library
client.voices.edit_settings(
    voice_id="your_voice_id",
    settings={
        "is_shared": True,
        "share_settings": {
            "name": "Friendly Assistant",
            "description": "Warm, approachable voice for assistants",
            "labels": ["friendly", "warm", "assistant"],
            "use_cases": ["assistant", "explainer"]
        }
    }
)
```

## Voice Settings Management

### Edit Voice

```python
client.voices.edit(
    voice_id="voice_id",
    name="Updated Name",
    description="Updated description",
    labels={
        "accent": "american",
        "gender": "male",
        "use_case": "narration"
    }
)
```

### Update Default Settings

```python
client.voices.edit_settings(
    voice_id="voice_id",
    settings={
        "stability": 0.6,
        "similarity_boost": 0.8,
        "style": 0.1,
        "use_speaker_boost": True
    }
)
```

### Delete Voice

```python
client.voices.delete(voice_id="voice_id")
```

## Multi-Voice Agents

For conversational agents, configure multiple voices:

```python
agent = client.conversational_ai.agents.create(
    conversation_config={
        "agent": {
            "prompt": {"prompt": "..."},
            "voices": [
                {
                    "voice_id": "voice_1",
                    "name": "Main",
                    "use_for": ["default"]
                },
                {
                    "voice_id": "voice_2", 
                    "name": "Excited",
                    "use_for": ["excited", "happy"]
                }
            ]
        }
    }
)
```

**Limit:** Maximum 10 voices per agent.

## Voice Limits

| Voice Type | Plan Limits |
|------------|-------------|
| Custom Voices | Varies by plan |
| Instant Clones | Varies by plan |
| Professional Clones | Limited, higher plans |
| Voice Library | Unlimited access |
