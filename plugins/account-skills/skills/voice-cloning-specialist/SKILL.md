---
name: voice-cloning-specialist
description: Specialist guidance for open-source voice cloning and custom text-to-speech voices. Covers choosing a project (Dots.TTS, VoxCPM2, Qwen3-TTS, CosyVoice3, GPT-SoVITS, Chatterbox, Fish S2 Pro, F5-TTS, RVC/Applio and others), checking license and commercial-use terms, recording and cleaning voice samples, slicing and transcribing datasets, fine-tuning on a user's own audio, evaluating likeness, and serving the result, with consent checks built in. Use whenever the user wants to "clone a voice", "clone my voice", do "voice cloning", "train a TTS voice" on their samples, get "text to speech with my voice" or "in my voice", "fine-tune a voice model", make an AI voice from recordings, pick between open-source TTS or voice-conversion projects, fix a clone that does not sound like them, or prepare audio for voice training — even if they never say "cloning", such as "make an audiobook narrator that sounds like me" or "turn my podcast recordings into a voice model".
---

# Voice Cloning Specialist

Help users produce speech in a voice they have the right to use, with open-source tools, on the hardware they actually have. Most failures in this domain come from three places: bad training data, a license that does not allow the intended use, and picking a model from hype instead of fit. This skill addresses each in order.

Verified facts in this skill's references date from **2026-10-07**. The landscape changes monthly; see "Freshness" below.

## Ground rules

1. **Consent before cloning.** Before helping clone, fine-tune, or convert into any specific person's voice, establish whose voice it is and whether that person has agreed. Ask once, briefly, then proceed according to `references/ethics-consent.md`. The user's own voice needs no further checks. Decline cloning a real person without their consent, and decline any request aimed at impersonation, fraud, or getting past voice authentication, whatever reason is given. Explaining how the technology works in general, comparing models, or helping with an invented voice does not need the gate.
2. **License before recommendation.** The weights license, not the code license, decides what the user may do with their cloned voice. Before recommending a model, ask whether the use is personal or commercial (monetized content, a product, client work). For commercial use, recommend only models whose weights permit it, and say so explicitly. Name the license next to every model you recommend. `references/model-landscape.md` lists verified licenses with source links and a "License traps" section.
3. **No invented capabilities.** State features, flags, and numbers that appear in the references or that you have just checked in the project's README. When something is a practitioner report rather than official documentation, say so. When unsure, check the live repo instead of guessing.
4. **Keep watermarks.** Never help strip a watermark (for example Chatterbox's PerTh) from synthetic audio, and recommend disclosure when listeners could mistake the clone for the real person.

## Step 1 — Intake

Ask only for what is missing; many requests already answer several of these. Group the questions into one message.

- **Whose voice, and consent?** (Ground rule 1.)
- **Input:** will the user type text (text-to-speech), or speak or sing into a mic and want it to come out in the target voice (voice conversion)? People often say "clone my voice" for both.
- **Goal and quality bar:** a quick test, a reusable personal voice, an audiobook or podcast narrator, a real-time voice for an agent or stream, or a product feature?
- **Personal or commercial use, and where will it be published?** (Ground rule 2.) Platforms set their own rules on synthetic voices — Audible/ACX, for example, requires human narration unless Amazon authorizes otherwise. Check the target platform before the user invests in a voice; see `references/ethics-consent.md` section 6.
- **Audio available:** how many minutes, recorded how (one session or scattered clips, mic or phone, any music or other speakers)?
- **Hardware:** NVIDIA GPU and VRAM, Apple Silicon and RAM, CPU only, or willing to rent a cloud GPU?
- **Language(s)**, and any need for emotion control or low latency.

## Step 2 — Check the environment

When working on the user's machine, detect rather than ask:

```bash
uname -sm; python3 --version
command -v ffmpeg ffprobe || echo "ffmpeg missing"
nvidia-smi --query-gpu=name,memory.total --format=csv 2>/dev/null || echo "no NVIDIA GPU"
sysctl -n machdep.cpu.brand_string hw.memsize 2>/dev/null   # macOS: chip and RAM
df -h .                                                      # models and datasets need tens of GB
```

Ask before installing system packages, downloading model weights (often several GB), or starting GPU jobs.

## Step 3 — Choose the path

Use this decision flow, then pick a model from the defaults table.

1. **No specific person's voice needed** (any pleasant voice) → TTS without cloning: Kokoro (Apache-2.0) or Piper. Stop here.
2. **Audio in, audio out** (speaking or singing as the target voice, live voice changing) → **voice conversion**: RVC via Applio. See `references/recipes/rvc-applio.md`.
3. **Text in, wants a result today, has one clean ~10 s clip** → **zero-shot cloning.** Quick paths are in `references/fine-tuning.md` section 2.
4. **Text in, wants the closest likeness of a voice, has 5+ minutes of clean one-session audio and a GPU (local or rented)** → **fine-tune.** Run zero-shot first as a baseline, then fine-tune.
5. **CPU-only target device** → zero-shot with Chatterbox Nano or pocket-tts, or train a Piper voice on a rented GPU and run it on CPU.

### Default picks

| Need | Commercial use allowed | Personal / research only (better or broader in some cases) |
|---|---|---|
| Zero-shot, 8–16 GB GPU | Chatterbox (MIT), Qwen3-TTS (Apache-2.0), VoxCPM2 (Apache-2.0) | OmniVoice (646 languages) |
| Zero-shot, 24 GB GPU | Dots.TTS soar (Apache-2.0) | Fish S2 Pro, Voxtral TTS, Higgs TTS 3 |
| Fine-tune for best likeness | Dots.TTS soar, VoxCPM2 LoRA, CosyVoice3, MOSS-TTS v1.5 (all Apache-2.0) | F5-TTS, OmniVoice |
| Little data (1–5 min), consumer GPU | GPT-SoVITS v2Pro (MIT) | — |
| Apple Silicon | mlx-audio running Qwen3-TTS, VoxCPM2, or Chatterbox | mlx-audio running OmniVoice |
| CPU only | Chatterbox Nano (MIT), pocket-tts (CC-BY-4.0) | — |
| Emotion control | Chatterbox (exaggeration), IndexTTS-2 (commercial below its size thresholds) | Fish S2 Pro inline tags, Higgs control tokens |
| Voice conversion | Applio / RVC (MIT) | Seed-VC (GPL-3.0, archived) |

When recommending, give two or three options at most, each with: name, weights license, why it fits this user, hardware it needs, and a link from `references/model-landscape.md`. Mention the trade-off that matters most for them.

## Step 4 — Prepare the audio

Data quality matters more than model choice. Follow `references/data-prep.md`. Key rules:

- Record in **one session**, in one room, with one mic, in the style the user wants out. Capture 24-bit 48 kHz (or 44.1 kHz) mono WAV; train on 16-bit PCM at the model's native rate. Never train from MP3.
- Inspect recordings with `scripts/probe_audio.sh <file> [--target-rate HZ]`. It reports duration, sample rate, channels, bit depth, loudness (LUFS), and peaks, and warns on lossy codecs, stereo, clipping, and near-silence.
- Clean only when needed: separate vocals if there is music, denoise lightly, and A/B against the untouched audio, because enhancement often makes clones worse.
- Slice to 4–12 s clips on sentence boundaries without dropping audio; transcribe with WhisperX or Whisper and proofread.
- Validate with `scripts/check_dataset.py <clips_dir> [--manifest FILE] [--source-minutes N] [--strict]`. It reports clip count, total minutes, sample-rate and channel consistency, and flags silent, clipped, too-short, too-long, and untranscribed clips, plus a total that drifts more than 10% from the source.

Both scripts run with only ffmpeg and the Python standard library; numpy and soundfile are used when present.

## Step 5 — Clone or train

- **Zero-shot:** `references/fine-tuning.md` section 2 has working snippets for Chatterbox and Qwen3-TTS; Dots.TTS and VoxCPM2 snippets are in their recipes. Always pass the reference clip's exact transcript when the model accepts one.
- **Fine-tune:** pick a base with `references/fine-tuning.md` section 3, then follow the framework recipe:
  - `references/recipes/dots-tts.md` — Dots.TTS (Apache-2.0)
  - `references/recipes/voxcpm2.md` — VoxCPM2 LoRA (Apache-2.0)
  - `references/recipes/cosyvoice3.md` — CosyVoice 3 (Apache-2.0)
  - `references/recipes/qwen3-tts.md` — Qwen3-TTS (Apache-2.0)
  - `references/recipes/f5-tts.md` — F5-TTS (non-commercial weights)
  - `references/recipes/llm-tts-unsloth.md` — Orpheus, CSM, Llasa, Spark, OuteTTS
  - `references/recipes/piper.md` — Piper custom voice for CPU and edge
  - GPT-SoVITS has a full walkthrough in `references/fine-tuning.md` section 4.
- **Voice conversion:** `references/recipes/rvc-applio.md`, including model-file safety and live routing into Discord or OBS.

Follow the training discipline in `references/fine-tuning.md` section 5: save often, audition early checkpoints first, render several takes, change one variable at a time, and pin versions. Without a suitable local GPU, use the rental checklist in section 6, and push checkpoints to a private repository before terminating the machine.

When running training or long downloads yourself, run them in the background, report progress, and do not claim a run succeeded until you have seen its output.

## Step 6 — Evaluate and iterate

Use `references/evaluation.md`: a held-out sentence set, speaker similarity against real recordings, ASR word error rate, a duration check for dropped words, and a blind listening test that includes one real recording as a control. Metrics triage; ears decide. Its symptom table maps common complaints ("doesn't sound like me", "robotic", "skips words") to fixes, in the order data → checkpoint → inference settings → model.

## Step 7 — Use and serve

`references/serving.md` covers running the voice on each platform (CUDA, Apple Silicon via mlx-audio, CPU, Raspberry Pi), exposing an API, and speed levers. Before a cloned voice reaches anyone else, re-check the base model's license, keep or add a watermark, and gate any endpoint behind authentication.

## Answering comparison questions

For "which project should I use" or "is X better than Y" questions without a cloning task attached, answer directly from `references/model-landscape.md`: lead with a recommendation tied to the user's constraints, include the weights license for every model named, and separate official facts from practitioner reports. Rankings from single blind tests and aggregator blogs are secondary evidence; say so.

## Freshness

Every row in `references/model-landscape.md` carries a source URL and a verification date. When today is more than about 60 days after that date, when the user plans commercial use, or when the user mentions a model or version not listed, re-check the specific project before relying on it:

- Read the project's LICENSE and README (raw.githubusercontent.com works when GitHub pages are blocked) and the Hugging Face model card's license field.
- With the Hugging Face MCP connected, use its Hub tools to inspect a repo's card and to browse trending text-to-speech models.
- Tell the user what changed since the reference was written.

## Reference map

| File | Read when |
|---|---|
| `references/model-landscape.md` | Choosing or comparing models; any license or commercial-use question; hardware fit |
| `references/data-prep.md` | Recording, cleaning, slicing, transcribing, manifests, dataset validation |
| `references/fine-tuning.md` | Zero-shot snippets, choosing a fine-tuning base, GPT-SoVITS walkthrough, training discipline, renting a GPU |
| `references/recipes/*.md` | Step-by-step commands for one framework |
| `references/evaluation.md` | Judging likeness and quality; diagnosing a bad clone |
| `references/serving.md` | Running or deploying the finished voice |
| `references/ethics-consent.md` | Consent gate decisions, consent recordings, watermarking, disclosure, laws by jurisdiction, publishing-platform rules |
| `scripts/probe_audio.sh` | Inspecting any single audio file |
| `scripts/check_dataset.py` | Validating a folder of training clips |
