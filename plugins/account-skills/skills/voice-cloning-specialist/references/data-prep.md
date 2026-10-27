# Preparing voice data

Data quality decides most of the result. A clean, single-session recording fine-tuned on a mid-tier model beats a famous model trained on scraped clips. Work through these stages in order and run `scripts/check_dataset.py` after slicing and again before training.

## Contents

1. [How much audio](#1-how-much-audio)
2. [Recording spec](#2-recording-spec)
3. [What to read](#3-what-to-read)
4. [Inspect the raw recording](#4-inspect-the-raw-recording)
5. [Cleanup (only when needed)](#5-cleanup-only-when-needed)
6. [Loudness and resampling](#6-loudness-and-resampling)
7. [Slicing](#7-slicing)
8. [Transcription and proofreading](#8-transcription-and-proofreading)
9. [Manifest formats per framework](#9-manifest-formats-per-framework)
10. [Validate and pin the dataset](#10-validate-and-pin-the-dataset)

## 1. How much audio

| Goal | Minimum | Recommended | Notes |
|---|---|---|---|
| Zero-shot reference | 3–5 s (model-dependent) | One clean 10–15 s clip + exact transcript | Longer does not help most models (Dots.TTS: ~10 s; F5: under 12 s; OmniVoice: 3–10 s) |
| GPT-SoVITS fine-tune | 1 min | A few minutes to ~15 min | Official minimum is 1 min |
| VoxCPM2 LoRA | 5 min | 5–10+ min | Official guidance is "5–10 minutes" |
| Dots.TTS / CosyVoice3 / Qwen3-TTS fine-tune | ~10 min | 30–45 min from **one session** | 30–45 min is practitioner-reported, not an official requirement |
| RVC / Applio voice conversion | 10 min | 10–30+ min of dry speech (add singing if you want singing) | No transcripts needed |

One session beats more sessions. Recording in different rooms, with different mics, or on different days bakes inconsistent room tone into the model. If the user only has scraped clips from videos, set expectations: zero-shot from the single best clip may beat fine-tuning on a mixed pile.

## 2. Recording spec

- **Capture:** WAV or FLAC, **24-bit, 48 kHz (or 44.1 kHz), mono**. Keep these masters untouched.
- **Training copies:** 16-bit PCM WAV, mono, resampled to the model's native rate (section 6). A 16-bit 44.1 kHz WAV is a safe universal target when the model is not yet chosen.
- **Never** start from MP3/AAC/Opus for training data. Lossy artifacts get learned.
- **Levels:** peaks around −6 dBFS; nothing touching 0 dBFS. `scripts/probe_audio.sh` reports sample peak and true peak.
- **Mic:** any decent USB or XLR mic; a modern phone in a quiet room works. Use the *same* mic, distance (a fist to a hand-width away), and angle for the whole session. Use a pop filter or speak slightly off-axis.
- **Room:** small and dead. A closet full of clothes or a room with blankets on hard surfaces beats a large untreated room. Turn off HVAC, fans, fridges; silence notifications.
- **Session:** one sitting, water nearby, short breaks without moving the mic. Re-take a sentence rather than patching a fluff.

## 3. What to read

- Read in the **style you want out**. Narration in, narration out; conversational in, conversational out.
- Cover phonetic variety: short and long sentences, questions, exclamations, numbers, dates, names, and lists.
- Include the emotions or delivery you want the model to be able to produce, in proportion to how often you need them.
- Public-domain text works (e.g., Harvard sentences for coverage, then book passages for flow). Keep a text copy of everything read — it becomes the transcript ground truth.

## 4. Inspect the raw recording

```bash
scripts/probe_audio.sh session.wav --target-rate 24000
```

Fix any WARN (lossy codec, stereo, clipping, near-silence) before going further. Re-record if the file is clipped; clipping cannot be repaired cleanly.

## 5. Cleanup (only when needed)

On a clean one-session recording, enhancement often makes results *worse* (practitioner-reported). A/B: train or clone once on untouched audio and once on cleaned audio, and keep cleanup only if it wins by ear.

- **Music or other speakers present — separate vocals first:** `audio-separator` (UVR models, `pip install audio-separator`) or Demucs (`demucs --two-stems=vocals file.wav`). GPT-SoVITS and Applio bundle UVR5.
- **Reverb/echo:** UVR de-reverb/de-echo models via audio-separator or the UVR5 tab.
- **Background noise:** DeepFilterNet (`pip install deepfilternet`, then `deepFilter in.wav -o out/`) or Resemble Enhance (`resemble-enhance in_dir out_dir --denoise_only`). Apply lightly; over-processing produces a metallic voice that the model learns.
- **Other speakers in the recording:** pyannote diarization, then keep only the target speaker's segments.

Confirm current flags with each tool's `--help`; they change between releases.

Prefer local tools for cleanup. Cloud "voice isolator" or "enhance" web services upload the recording to a third party; use them only with the speaker's (or, for a deceased person, the family's) agreement, and never for someone else's voice without it.

**Two voices that are both speech** (a TV, a co-host talking over the speaker) cannot be fully separated by vocal-separation models, which split speech from music and noise. Diarize and keep only clean single-speaker segments instead of trying to "remove" the other voice.

## 6. Loudness and resampling

Normalize training audio consistently and resample once, to the target model's native rate:

```bash
ffmpeg -i master.wav -af loudnorm=I=-23:TP=-2:LRA=7 -ar 24000 -ac 1 -c:a pcm_s16le train.wav
```

| Native rate | Models |
|---|---|
| 16 kHz | RVC feature extraction (Applio handles this internally) |
| 22.05 kHz | Piper (medium quality) |
| 24 kHz | F5-TTS, CosyVoice, Orpheus, Higgs, Chatterbox |
| 44.1 kHz | Fish S2 Pro, Zonos |
| 48 kHz | Dots.TTS, VoxCPM2 (output; VoxCPM2 references are 16 kHz) |

When in doubt, check the model's config or README for `sample_rate`.

## 7. Slicing

Target **4–12 s clips cut on sentence boundaries** (2–15 s is the outer acceptable range, which is what `check_dataset.py` flags by default).

Rules:
- Merge short fragments forward into the next clip rather than dropping them.
- Force-split anything over ~12 s at a comma or a pause longer than ~0.35 s.
- **Never silently drop long segments.** A slicer that discards everything it can't split cleanly can lose half a recording. Verify total clip minutes are within 10% of the source (`check_dataset.py --source-minutes`).
- Remove coughs, restarts, mouth clicks, off-mic lines, and long silences. A bad clip hurts more than a missing one.
- Keep ~0.2–0.5 s of natural silence at the edges; do not trim to the first phoneme.

Tools:
- **GPT-SoVITS WebUI** and **F5-TTS Gradio** include slicers that work well for their own pipelines.
- **Silero VAD** for speech regions (`pip install silero-vad`; see its README for `get_speech_timestamps`).
- **WhisperX** segment timestamps double as sentence boundaries (section 8).

## 8. Transcription and proofreading

- **WhisperX** gives word-level timestamps for slicing and transcripts in one pass:
  `whisperx audio.wav --model large-v3 --output_format json` (check `--help` for alignment-model flags in the installed version).
- Plain `openai-whisper` large-v3 or **Qwen3-ASR-1.7B** (what the HF Open TTS Leaderboard uses) are good alternatives.
- If the user read from a script, align against the script text instead of trusting ASR.
- **Proofread** numbers, names, and punctuation. Write numbers the way they were spoken ("twenty twenty-six", not "2026") unless the model's text normalizer handles it.
- For zero-shot references, the reference transcript must match the audio **exactly**. A mismatched `ref_text` is a top cause of unstable zero-shot output (Dots.TTS, Fish, Qwen3-TTS, F5).

## 9. Manifest formats per framework

| Framework | Layout |
|---|---|
| LJSpeech-style (F5-TTS, Piper, XTTS, many others) | `wavs/` + `metadata.csv` with `file|text` (Piper multi-speaker: `file|speaker|text`) |
| Dots.TTS | JSONL: `{"fid": "...", "audio": "/abs/path.wav", "text": "..."}` |
| OmniVoice | JSONL: `id`, `audio_path`, `text` |
| VoxCPM2, Qwen3-TTS, MOSS-TTS | JSONL via each repo's `prepare_data` / config — read the repo's example manifest |
| GPT-SoVITS | `.list` file `path|speaker|lang|text`, produced by its WebUI ASR step |
| RVC / Applio | A folder of WAVs; no transcripts |
| Hugging Face `datasets` | `Dataset.from_dict({"audio": paths, "text": texts}).cast_column("audio", Audio(sampling_rate=24000))` |

## 10. Validate and pin the dataset

```bash
python3 scripts/check_dataset.py wavs/ --manifest metadata.csv --source-minutes 45 --min-sec 2 --max-sec 15
```

Resolve every problem it reports: mixed sample rates or channels, silent or clipped clips, clips outside the duration window, clips without transcripts, manifest rows without audio, and a total that is more than 10% off the source. Use `--strict` in scripts so a bad dataset stops the pipeline (exit code 3).

Before any cloud training run, push the dataset to a **private** Hugging Face dataset repo (`push_to_hub("you/my-voice", private=True)`) so every run fetches the same artifact. Voice recordings are personal and biometric data; never make the repo public, and delete it when the user asks.
