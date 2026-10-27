# Fine-tuning a custom voice and zero-shot quick paths

Read `references/data-prep.md` first. Model choices and licenses are in `references/model-landscape.md`. Per-framework commands live in `references/recipes/`.

## Contents

1. [Zero-shot or fine-tune?](#1-zero-shot-or-fine-tune)
2. [Zero-shot quick paths](#2-zero-shot-quick-paths)
3. [Pick a fine-tuning base](#3-pick-a-fine-tuning-base)
4. [GPT-SoVITS end-to-end walkthrough](#4-gpt-sovits-end-to-end-walkthrough)
5. [Training discipline for small datasets](#5-training-discipline-for-small-datasets)
6. [Renting a GPU](#6-renting-a-gpu)
7. [Recipe index](#7-recipe-index)

## 1. Zero-shot or fine-tune?

| Situation | Path |
|---|---|
| Needs a usable clone today, has one clean 10 s clip | Zero-shot (section 2) |
| Wants the closest possible likeness of their own voice, has 5+ min of one-session audio and GPU access (local or rented) | Fine-tune (sections 3–5) |
| Has 1–5 min, Chinese/Japanese/Korean/English, consumer GPU | GPT-SoVITS fine-tune (section 4) |
| Wants to speak or sing *into a mic* and come out as the target voice | Voice conversion, not TTS: `recipes/rvc-applio.md` |
| CPU-only, needs a lightweight custom voice for edge devices | Piper training on a rented GPU, CPU inference: `recipes/piper.md` |

Try zero-shot first even when planning to fine-tune: it costs minutes and gives a baseline to beat.

## 2. Zero-shot quick paths

Both paths below are permissively licensed (see model-landscape.md) and need only a reference clip. Confirm consent before running either (SKILL.md, consent gate).

### Chatterbox (MIT, PerTh-watermarked output)

From the Resemble AI README:

```bash
pip install chatterbox-tts
```

```python
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")  # or "cpu" / "mps"
wav = model.generate(
    "Text to speak in the cloned voice.",
    audio_prompt_path="reference_10s.wav",
    exaggeration=0.5,   # README default; ~0.7+ for more expressive delivery
    cfg_weight=0.5,     # README default; ~0.3 for fast speakers or calmer pacing
)
ta.save("out.wav", wav, model.sr)
```

- English Turbo (350M, lower latency): `from chatterbox.tts_turbo import ChatterboxTurboTTS`; Nano for CPU: `ChatterboxTurboTTS.from_pretrained(device="cpu", nano=True)`.
- Other languages: `from chatterbox.mtl_tts import ChatterboxMultilingualTTS` and pass `language_id="fr"` (23 languages). Match the reference clip's language to the tag, or set `cfg_weight=0` to reduce accent transfer.
- Leave the PerTh watermark in place. It marks the audio as synthetic, which is what responsible use looks like.

### Qwen3-TTS (Apache-2.0)

From the Qwen README:

```bash
pip install -U qwen-tts
```

```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",   # 0.6B-Base for smaller GPUs
    device_map="cuda:0",
    dtype=torch.bfloat16,
)
wavs, sr = model.generate_voice_clone(
    text="Text to speak in the cloned voice.",
    language="English",
    ref_audio="reference.wav",
    ref_text="Exact transcript of reference.wav.",
)
sf.write("out.wav", wavs[0], sr)
```

- Reuse one voice across many lines with `create_voice_clone_prompt(...)` and pass the result as `voice_clone_prompt`.
- `x_vector_only_mode=True` drops the transcript requirement at some cost in similarity.

### Other strong zero-shot options

Dots.TTS (`dots.tts --prompt-audio ref.wav --prompt-text "..."`, Apache-2.0) and VoxCPM2 (`prompt_wav_path` + `prompt_text` + `reference_wav_path`, Apache-2.0) are both permissive and are covered in their recipes. Fish S2 Pro, Voxtral, Higgs TTS 3, and OmniVoice clone very well but carry non-commercial weights.

## 3. Pick a fine-tuning base

| Base | License | Data | When to choose |
|---|---|---|---|
| Dots.TTS soar | Apache-2.0 | 10+ min; 30–45 min one-session (practitioner) | Best-reported likeness of a person's own voice; 24 GB GPU or rented |
| VoxCPM2 (LoRA) | Apache-2.0 | 5–10 min (official) | 30 languages, 48 kHz, LoRA keeps the base intact; 16–24 GB GPU for training (docs: ~20 GB at batch 16), ~8 GB for inference |
| CosyVoice3-0.5B | Apache-2.0 | 10+ min | Smallest permissive model to ship; Chinese dialects |
| GPT-SoVITS v2Pro | MIT | 1–15 min | Little data, consumer GPU, WebUI-driven, EN/ZH/JA/KO/Yue |
| Qwen3-TTS Base | Apache-2.0 | single speaker | Already using Qwen3-TTS zero-shot; check speaker similarity before investing (one practitioner report of drift) |
| MOSS-TTS v1.5 | Apache-2.0 | 10+ min | 31 languages; 40–80 GB GPU for full SFT |
| F5-TTS v1 | MIT code / **NC weights** | 10+ min | Personal projects only |
| OmniVoice | Apache code / **NC weights** | 10+ min | 646 languages; personal projects only |

## 4. GPT-SoVITS end-to-end walkthrough

GPT-SoVITS is the most approachable fine-tune: a WebUI walks through every step, and it trains from as little as one minute of audio. Source: https://github.com/RVC-Boss/GPT-SoVITS (verified 2026-10-07).

**Version choice.** Use **v2Pro / v2ProPlus**, the latest tagged release (`20250606v2pro`). The README says v2Pro outperforms v4 at v2's hardware cost, and that v3/v4 do poorly on average-quality training sets and lean toward the reference clip instead of the training set. **V5** (pretrained `gsv-v5-pretrained`, branch `cuda_graph_accel_v5`) landed on 2026-10-06; use it only if the user wants the newest code and accepts early-release risk.

**Install.**
- Windows: download the integrated package from the README and run `go-webui.bat`.
- Linux: `conda create -n GPTSoVits python=3.10 && conda activate GPTSoVits && bash install.sh --device CU128 --source HF --download-uvr5` (choose `CU126`, `CU128`, `ROCM`, or `CPU`).
- macOS: same, with `--device MPS` or `CPU`. Training on Mac is slow; prefer a rented GPU.
- Launch: `python webui.py` (optionally followed by a UI language code) and open the local URL it prints.

**Dataset (tab 0/1A).**
1. Put the one-session recording (WAV) in a folder.
2. *UVR5* (optional): separate vocals or de-reverb only if needed — see data-prep.md section 5.
3. *Slicer*: slice into short clips. Check the output with `scripts/check_dataset.py <sliced_dir> --source-minutes <N>`.
4. *ASR*: pick the ASR model that matches the speaker's language (the Chinese ASR is built in; other languages use a Whisper-based option). It writes a `.list` file (`path|speaker|lang|text`).
5. *Proofread*: open the labeling tool and correct every transcript. Fix numbers, names, and punctuation.

**Training (tab 1B).**
1. Set the experiment name, choose the v2Pro pretrained models, and run the formatting steps (text, SSL features, semantic tokens) in order.
2. Train **SoVITS** first, then **GPT**. Start with the WebUI defaults and lower the batch size if you hit out-of-memory.
3. Save every few epochs so you can audition checkpoints.

Reference timings from practitioner reports (not official): with ~1 min of data on an RTX 3080, SoVITS 8 epochs ≈ 78 s and GPT 15 epochs ≈ 60 s. GPT-SoVITS publishes **no official VRAM figures**; consumer cards with 8–12 GB are commonly reported to work with reduced batch sizes.

**Inference (tab 1C).**
1. Load a SoVITS and a GPT checkpoint.
2. Give a 3–10 s reference clip from the training session plus its exact transcript.
3. Over-training the GPT stage causes repeated or skipped words. If that happens, step back to an earlier GPT checkpoint before changing anything else.

## 5. Training discipline for small datasets

These rules apply to every framework and prevent most wasted runs:

- **Save every epoch (or every few hundred steps) and audition early checkpoints first.** On small single-speaker sets, quality often peaks early (practitioner reports: epoch 4 of 31 for CosyVoice3; 3,200 steps holding all the gain of 6,400). Later checkpoints overfit: artifacts, robotic prosody, or only reproducing training sentences.
- **Hold out 20–50 sentences that are not in the training transcripts** and render them with every candidate checkpoint. Evaluate with `references/evaluation.md`.
- **Render 3–5 takes per sentence.** Autoregressive TTS is stochastic; judge the median take, and discard takes much shorter than the median (dropped words).
- **Change one thing at a time**, in this order: data → checkpoint → inference settings (CFG, temperature, steps, reference clip) → model.
- **Prefer LoRA** when the framework offers it and data is under ~15 minutes; it is harder to overfit and keeps the base intact.
- **Pin versions.** Follow each repo's Dockerfile or constraints file exactly; record the commit hash with each checkpoint.
- **A fine-tuned single-speaker checkpoint usually still wants a reference clip at inference** (F5-TTS, Dots.TTS continuation cloning). Use one of the training clips.

## 6. Renting a GPU

When the user lacks a suitable local GPU:

1. Rent a single 24 GB card (RTX 4090/3090) for most fine-tunes, or 40–80 GB for MOSS-TTS full SFT. RunPod, Modal, Lambda, and Vast are common choices; check current prices yourself.
2. Before installing anything, run `python -c "import torch; x=torch.randn(4096,4096,device='cuda'); print(torch.cuda.get_device_name(), (x@x).sum().item())"` to prove the GPU works.
3. Prefer hosts with a recent CUDA driver that matches the framework's PyTorch build.
4. Pull the dataset from the private Hugging Face repo pinned in data-prep.md.
5. Push every checkpoint you want to keep to a **private** HF model repo *before* terminating. A stopped pod is not a saved checkpoint.
6. Terminate (not just stop) the instance when finished.

## 7. Recipe index

| Recipe | File |
|---|---|
| Dots.TTS (top pick, Apache-2.0) | `references/recipes/dots-tts.md` |
| VoxCPM2 LoRA (Apache-2.0) | `references/recipes/voxcpm2.md` |
| CosyVoice 3 (Apache-2.0) | `references/recipes/cosyvoice3.md` |
| Qwen3-TTS fine-tune (Apache-2.0) | `references/recipes/qwen3-tts.md` |
| F5-TTS (NC weights) | `references/recipes/f5-tts.md` |
| RVC via Applio (voice conversion) | `references/recipes/rvc-applio.md` |
| Piper custom voice (CPU/edge) | `references/recipes/piper.md` |
| LLM-style TTS with Unsloth (Orpheus, CSM, Llasa, Spark) | `references/recipes/llm-tts-unsloth.md` |
