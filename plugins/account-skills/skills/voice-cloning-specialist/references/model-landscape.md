# Open-source voice cloning landscape

Every license and capability claim below was read from the project's own LICENSE file, README, or Hugging Face model card on the date in the **Verified** column. The field moves monthly. If today is more than ~60 days after the verification date, or the user plans commercial use, re-open the linked source before relying on a row.

## Contents

1. [How to read this file](#how-to-read-this-file)
2. [Fine-tunable TTS with permissive weights](#1-fine-tunable-tts-with-permissive-weights)
3. [Zero-shot / other TTS with permissive or conditional weights](#2-zero-shot-and-other-tts-permissive-or-conditional-weights)
4. [Non-commercial weights](#3-non-commercial-weights)
5. [Voice conversion (audio to audio)](#4-voice-conversion-audio-to-audio)
6. [TTS without cloning](#5-tts-without-cloning)
7. [License traps](#license-traps)
8. [Hardware tiers](#hardware-tiers)
9. [Tooling and leaderboards](#tooling-and-leaderboards)
10. [Legacy and superseded](#legacy-and-superseded)
11. [Practitioner evidence (secondary)](#practitioner-evidence-secondary)

## How to read this file

- **Code / weights**: code license, then weights license. They often differ, and the weights license is the one that governs the voice you produce.
- **Commercial?**: whether the weights license allows commercial use of the model and its outputs. "Conditional" means yes with terms you must read.
- **Clone input**: what zero-shot cloning needs at inference. "+ transcript" means pass the exact words spoken in the reference clip.
- **Fine-tune**: whether the project ships official training code, and the entry point.
- Parameter counts are from the safetensors totals on Hugging Face when they differ from the marketing name.

## 1. Fine-tunable TTS with permissive weights

These are the default picks when the user wants the best likeness of their own voice and has 5+ minutes of clean audio.

| Project | Code / weights | Commercial? | Clone input | Fine-tune | Notes | Verified |
|---|---|---|---|---|---|---|
| **Dots.TTS** (soar) | Apache-2.0 / Apache-2.0 | Yes | ~10 s reference ("longer audio won't yield better results") + exact prompt text | Yes: `scripts/train_dots_tts.py`, JSONL `{"fid","audio","text"}`; MeanFlow distillation script | ~2.2B; 48 kHz output; streaming first chunk 69–225 ms and ~5.7–7.9 GB peak inference memory (H800, `--optimize`); benchmarked on 24 languages; v0.3.1 | 2026-10-07 — https://github.com/studio-dots-ai/dots.tts · https://huggingface.co/dots-studio/dots.tts-soar |
| **CosyVoice 3** (Fun-CosyVoice3-0.5B-2512) | Apache-2.0 / Apache-2.0 | Yes | Short prompt (length not stated in README) | Yes: recipes under `examples/libritts` | 0.5B; 9 languages + 18+ Chinese dialects; bi-streaming, latency as low as 150 ms; supersedes CosyVoice 2 (still downloadable) | 2026-10-07 — https://github.com/FunAudioLLM/CosyVoice · https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 |
| **Qwen3-TTS** | Apache-2.0 / Apache-2.0 | Yes | 3 s + transcript (`ref_audio` + `ref_text`), or `x_vector_only_mode` | Yes, single-speaker only: `finetuning/prepare_data.py` then `sft_12hz.py` (fine-tune the `-Base` checkpoints) | 0.6B and 1.7B (≈1.93B weights); 10 languages; latency as low as 97 ms; released 2026-01-22 | 2026-10-07 — https://github.com/QwenLM/Qwen3-TTS · https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base |
| **VoxCPM2** | Apache-2.0 / Apache-2.0 | Yes | Short reference clip (+ transcript for best similarity) | Yes, LoRA or full: `scripts/train_voxcpm_finetune.py --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml` (`..._all.yaml` for full); from 5–10 min of audio | ≈2.3B; 30 languages; 48 kHz output; ~8 GB VRAM for inference; training docs: LoRA ~20 GB / full ~40 GB at batch 16; RTF ≈0.30 on RTX 4090, ≈0.13 with Nano-vLLM; tag 2.0.3 | 2026-10-07 — https://github.com/OpenBMB/VoxCPM · https://huggingface.co/openbmb/VoxCPM2 |
| **MOSS-TTS v1.5** | Apache-2.0 / Apache-2.0 | Yes | Reference clip (length not stated) | Yes: `moss_tts_delay/finetuning/prepare_data.py` + `sft.py` | "8B" (≈8.49B weights); 31 languages; llama.cpp config fits 8 GB GPUs; streaming is a separate MOSS-TTS-Realtime model (180 ms TTFB). GitHub org is `OpenMOSS`, HF org is `OpenMOSS-Team` | 2026-10-07 — https://github.com/OpenMOSS/MOSS-TTS · https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5 |
| **GPT-SoVITS** | MIT / MIT | Yes | 5 s zero-shot | Yes, from ~1 min of data: WebUI pipeline (slice → UVR5 → ASR → proofread → train); `s1_train.py`, `s2_train.py`, `s2_train_v3_lora.py` | EN/ZH/JA/KO/Cantonese. Latest GitHub *release* is still `20250606v2pro`; README says v2Pro beats v4 at v2 cost. **V5** landed 2026-10-06 (`s2Gv5dev`/`s2Gv5turbo`, HF package `v5-20261005`) — treat as bleeding edge. No official VRAM figures | 2026-10-07 — https://github.com/RVC-Boss/GPT-SoVITS · https://huggingface.co/lj1995/GPT-SoVITS |

## 2. Zero-shot and other TTS (permissive or conditional weights)

| Project | Code / weights | Commercial? | Clone input | Fine-tune | Notes | Verified |
|---|---|---|---|---|---|---|
| **Chatterbox** | MIT / MIT | Yes | Reference clip (README example uses a ~10 s clip) | No official script | Turbo 350M (EN), Nano 110M (EN, ~3× realtime on 8 CPU cores), Multilingual V3 500M (23 languages). Emotion exaggeration control. **PerTh watermark on all output** (`resemble-perth`) | 2026-10-07 — https://github.com/resemble-ai/chatterbox · https://huggingface.co/ResembleAI/chatterbox |
| **IndexTTS-2 / 2.5** | bilibili Model Use License (code and weights) | Conditional: royalty-free commercial use below 100M MAU / RMB 1B revenue; may not be used to improve other models (except non-commercial) | Single reference clip | No official scripts | Explicit emotion control (emotion reference audio, `emo_alpha`, 8-value vector, or from text); 2 languages (2.5: 5 — adds ja, es, ar); RTF 0.326 (2) / 0.207 (2.5) on RTX 4090 | 2026-10-07 — https://github.com/index-tts/index-tts · https://huggingface.co/IndexTeam/IndexTTS-2 |
| **Zonos v0.1** | Apache-2.0 / Apache-2.0 | Yes | 10–30 s speaker sample | No | 44 kHz; ~2× realtime on RTX 4090; 6 GB+ VRAM; last commit Mar 2025 | 2026-10-07 — https://github.com/Zyphra/Zonos |
| **OpenVoice v2** | MIT / MIT | Yes | Short reference (tone-color converter) | No | 6 native languages (EN, ES, FR, ZH, JA, KO); cross-lingual tone color; last commit Apr 2025 — lower ceiling than fine-tuned models | 2026-10-07 — https://github.com/myshell-ai/OpenVoice |
| **Dia / Dia2** (Nari Labs) | Apache-2.0 / Apache-2.0 | Yes | Audio prompt + transcript, best at 5–10 s (`example/voice_clone.py`); Dia2 via `--prefix-speaker-1/2` | No official script | English only; dialogue-oriented; Dia2 1B/2B (Nov 2025) | 2026-10-07 — https://github.com/nari-labs/dia · https://github.com/nari-labs/dia2 |
| **Sesame CSM-1B** | Apache-2.0 / Apache-2.0 (gated; Llama-3.2-1B backbone) | Conditional (Llama 3.2 terms likely apply; card forbids mimicking people without consent) | Context segments (audio + transcript); random voice without context | Transformers Trainer (≥4.52.1) per HF card | English; repo last commit 2025-05-27 | 2026-10-07 — https://github.com/SesameAILabs/csm · https://huggingface.co/sesame/csm-1b |
| **Orpheus TTS** | Apache-2.0 / Apache-2.0 (Llama-3.2-3B derivative) | Conditional (Llama 3.2 license terms likely also apply) | Text–audio pairs in the prompt; README notes it was not explicitly trained for zero-shot cloning | Yes: `finetune/train.py` + Unsloth notebook | 3B; SNAC 24 kHz; vLLM serving; last commit Dec 2025 | 2026-10-07 — https://github.com/canopyai/Orpheus-TTS · https://huggingface.co/canopylabs/orpheus-3b-0.1-ft |
| **OuteTTS 1.0-0.6B** | Apache-2.0 | Yes | `interface.create_speaker(audio.wav)` | Not stated | Llama-OuteTTS-1.0-1B is **CC-BY-NC-SA-4.0** (non-commercial) — check which checkpoint | 2026-10-07 — https://huggingface.co/OuteAI |
| **pocket-tts** (Kyutai) | MIT / CC-BY-4.0 (gated) | Yes, with attribution | WAV reference; `export-voice` saves a reusable embedding | No | CPU-first (2 cores), ~200 ms to first audio per README; 7 languages; README prohibits cloning without consent; v3.3.0 | 2026-10-07 — https://github.com/kyutai-labs/pocket-tts · https://huggingface.co/kyutai/pocket-tts |

## 3. Non-commercial weights

Fine for personal projects, research, and private experiments with your own voice. Not for products, client work, or monetized content unless a specific grant applies.

| Project | Code / weights | Commercial? | Clone input | Fine-tune | Notes | Verified |
|---|---|---|---|---|---|---|
| **Fish Audio S2 Pro** | Fish Audio Research License / same (**code too**) | No — separate written license from Fish Audio | Typically 10–30 s + exact transcript (`--prompt-text`) | LoRA: `fish_speech/train.py --config-name text2semantic_finetune`, merge with `tools/llama/merge_lora.py` (docs advise against fine-tuning RL-trained checkpoints) | Slow AR 4B + Fast AR 400M (≈4.56B); 80+ languages; ≥24 GB GPU recommended; TTFA ~100 ms on H200 | 2026-10-07 — https://github.com/fishaudio/fish-speech · https://huggingface.co/fishaudio/s2-pro |
| **Voxtral TTS** (Mistral) | No code repo (served via vLLM-Omni) / CC-BY-NC-4.0 | No (commercial via Mistral's paid API) | As little as 3 s; voice prompt 5–25 s | Not offered | 3.4B + 390M + 300M; 9 languages; ≥16 GB GPU; 70 ms latency at concurrency 1 on H200; released 2026-03-23. In mlx-audio: preset voices only, no cloning | 2026-10-07 — https://huggingface.co/mistralai/Voxtral-4B-TTS-2603 · https://mistral.ai/news/voxtral-tts |
| **Higgs TTS 3** (Boson) | Apache-2.0 repo holds **v2** code / Boson Higgs TTS 3 Research & Non-Commercial License | No, except the **Creator Use Grant**: monetized podcasts, videos, audiobooks, social posts with credit to Boson. Not for APIs or products. **Bans using the model or its outputs to train other speech models** | Reference + transcript ("materially improves cloning fidelity") | No training code | ≈4.65B; 100+ languages; H100 RTF 0.147 | 2026-10-07 — https://huggingface.co/bosonai/higgs-tts-3-4b · https://github.com/boson-ai/higgs-audio |
| **OmniVoice** (k2-fsa) | Apache-2.0 / **CC-BY-NC** (card text); bundled audio tokenizer under Boson Higgs Audio 2 Community License | No | 3–10 s + `ref_text` | Yes: `examples/run_finetune.sh`, `run_finetune_lora.sh` | 612M (Qwen3-0.6B base); 646 languages; RTF as low as 0.025 | 2026-10-07 — https://github.com/k2-fsa/OmniVoice · https://huggingface.co/k2-fsa/OmniVoice |
| **Breeze TTS 2** (BreezeBlue) | Apache-2.0 / BreezeBlue Research & Non-Commercial License v1.1 (covers derivatives and self-hosted outputs) | No (only output from the paid hosted API is commercial) | Clean audio + exact transcript | No (inference only) | ≈3.5B by weights; EN/ZH; 12 GB GPU min (24 GB with `--fast-all`); released 2026-08-25 | 2026-10-07 — https://huggingface.co/BreezeBlue/Breeze-TTS-2 · https://github.com/breezeblue-ai/breeze-tts |
| **F5-TTS** | MIT / **CC-BY-NC-4.0** ("due to the training data Emilia") | No | <12 s reference (clipped to ~12 s) + transcript; 30 s total per generation | Yes: `src/f5_tts/train/finetune_cli.py`, Gradio `f5-tts_finetune-gradio` | ~336M DiT; 24 kHz; release 1.1.22 | 2026-10-07 — https://github.com/SWivid/F5-TTS · https://huggingface.co/SWivid/F5-TTS |
| **XTTS-v2** (Coqui) | MPL-2.0 (idiap fork) / Coqui Public Model License | No — and no way to obtain one | 6 s | Yes (recipes under `recipes/ljspeech`) | 17 languages; Coqui is gone; https://coqui.ai/cpml returns 404; maintained only as the `coqui-tts` fork (0.27.5, 2026-01-26). Legacy | 2026-10-07 — https://huggingface.co/coqui/XTTS-v2 · https://github.com/idiap/coqui-ai-TTS |
| **Spark-TTS 0.5B** | Apache-2.0 / **CC-BY-NC-SA-4.0** (changed from Apache 2.0) | No | Prompt audio (ZH/EN) | No official training code | Last commit Apr 2025 | 2026-10-07 — https://github.com/SparkAudio/Spark-TTS · https://huggingface.co/SparkAudio/Spark-TTS-0.5B |
| **Llasa-1B** | — / CC-BY-NC-4.0 | No | Speech prompt | External `zhenye234/LLaSA_training` | — | 2026-10-07 — https://huggingface.co/HKUSTAudio/Llasa-1B |
| **VibeVoice-1.5B** | MIT / MIT, card says research use only | Not recommended by Microsoft for commercial or real-world use | — | — | **TTS code removed from the repo 2025-09-05** ("widespread misuse"); weights still on HF; outputs watermarked. Do not recommend | 2026-10-07 — https://github.com/microsoft/VibeVoice · https://huggingface.co/microsoft/VibeVoice-1.5B |

## 4. Voice conversion (audio to audio)

Voice conversion turns a recording of one person speaking or singing into another voice. It is not text-to-speech. Users often say "clone my voice" when they mean this; ask whether the input is text or audio.

| Project | Code / weights | Commercial? | Input | Notes | Verified |
|---|---|---|---|---|---|
| **Applio** (RVC) | MIT / MIT | Yes | Train on 10–30+ min of dry speech or singing | Realtime tab (since v3.5.0); latest release v3.6.5 (2026-09-19); README says maintenance mode, "will no longer receive frequent updates" | 2026-10-07 — https://github.com/IAHispano/Applio |
| **RVC WebUI** (RVC-Boss) | MIT | Yes | Same as Applio | Original project; release v2.3.260718 | 2026-10-07 — https://github.com/RVC-Boss/Retrieval-based-Voice-Conversion-WebUI |
| **Seed-VC** | GPL-3.0 / GPL-3.0 | Yes, under GPL terms | Zero-shot, 1–30 s reference | **Archived 2025-11-21.** Real-time-only fork: `jiaheguo521/seed-vc-realtime` (GPL-3.0, active Jul 2026) | 2026-10-07 — https://github.com/Plachtaa/seed-vc |

## 5. TTS without cloning

Offer these only when the user needs a good voice, not *their* voice.

| Project | Code / weights | Commercial? | Notes | Verified |
|---|---|---|---|---|
| **Kokoro-82M** | Apache-2.0 / Apache-2.0 | Yes | Preset voices only; CPU-friendly; StyleTTS2-derived | 2026-10-07 — https://huggingface.co/hexgrad/Kokoro-82M |
| **Piper** | GPL-3.0 code / per-voice licenses | Code yes (GPL); voices vary | No zero-shot, but you can *train* a custom voice (`python3 -m piper.train fit --ckpt_path <medium checkpoint>`); ONNX for CPU/Raspberry Pi; project says it is "looking for maintainers" | 2026-10-07 — https://github.com/OHF-Voice/piper1-gpl |
| **Supertonic 3** | MIT samples / OpenRAIL-M | Yes, with OpenRAIL use restrictions | ~99M, ONNX, 31 languages; no local cloning (custom voices are a paid Supertone service) | 2026-10-07 — https://huggingface.co/Supertone/supertonic-3 |

## License traps

> **F5-TTS:** the code is MIT but the released checkpoints are CC-BY-NC-4.0 because they were trained on the Emilia dataset. Do not recommend for commercial products. Verified 2026-10-07 — https://github.com/SWivid/F5-TTS

> **XTTS-v2:** code is MPL-2.0 but the weights are under the Coqui Public Model License (non-commercial). Coqui shut down, the license page now returns 404, and there is nobody left to grant a commercial license. Verified 2026-10-07 — https://huggingface.co/coqui/XTTS-v2

> **Fish Speech / Fish Audio S2 Pro:** both the code and the weights are under the Fish Audio Research License. Commercial use needs a separate written agreement with Fish Audio. Verified 2026-10-07 — https://github.com/fishaudio/fish-speech

> **OmniVoice:** Apache-2.0 code, CC-BY-NC weights, plus a Boson-licensed audio tokenizer inside the weights folder. Verified 2026-10-07 — https://huggingface.co/k2-fsa/OmniVoice

> **Higgs TTS 3:** the Creator Use Grant allows monetized *content* with credit, not products or APIs, and the license forbids using its outputs to train other speech models — so do not use Higgs to generate synthetic training data for another model. Verified 2026-10-07 — https://huggingface.co/bosonai/higgs-tts-3-4b

> **Spark-TTS, Llasa-1B, Llama-OuteTTS-1B:** non-commercial weights despite Apache-licensed code or siblings. Verified 2026-10-07 — links in the table above.

> **Llama-based models (Orpheus, CSM):** the model card says Apache-2.0, but the backbone is Llama 3.2, whose community license likely also applies. Read both before commercial use.

> **IndexTTS-2 is the reverse trap:** its custom "bilibili Model Use License" looks restrictive but permits commercial use below 100M MAU / RMB 1B revenue. Verified 2026-10-07 — https://github.com/index-tts/index-tts

> **Fine-tunes inherit the base license.** A LoRA or full fine-tune of a non-commercial checkpoint is still non-commercial, even when trained only on your own voice.

## Hardware tiers

Inference figures come from the READMEs above. Training memory is rarely documented officially; tiers marked *(community)* come from practitioner reports, not project docs.

| Hardware | Zero-shot cloning | Fine-tuning |
|---|---|---|
| CPU only | pocket-tts, Chatterbox Nano, GPT-SoVITS (slow), Kokoro/Piper (no cloning) | Do not train locally — use free Colab or rent a GPU |
| Apple Silicon | mlx-audio: Qwen3-TTS, VoxCPM2, OmniVoice, Chatterbox, MOSS-TTS, Higgs, CSM | Rent a cloud GPU; MLX training of TTS is immature *(community)*; run the result locally with mlx-audio |
| 8 GB NVIDIA | Chatterbox, Qwen3-TTS 0.6B, CosyVoice3, VoxCPM2 (~8 GB), Dots.TTS mf (~5.7 GB) | GPT-SoVITS v2Pro (reduce batch size), RVC/Applio, Piper *(community)* |
| 12–16 GB | Qwen3-TTS 1.7B, Dots.TTS soar (~7.9 GB), Breeze TTS 2 (12 GB), Voxtral (≥16 GB) | CosyVoice3, F5-TTS, GPT-SoVITS *(community)*; VoxCPM2 LoRA at 16 GB only with the default small batch (its Docker training README states ≥16 GB) |
| 24 GB (RTX 3090/4090, or rented) | Fish S2 Pro (≥24 GB), all of the above | VoxCPM2 LoRA (~20 GB at batch 16, official docs); Dots.TTS full fine-tune, Qwen3-TTS SFT, Orpheus LoRA *(community)* |
| 40–80 GB (A100/H100) | Everything | VoxCPM2 full fine-tune (~40 GB at batch 16, official docs); MOSS-TTS v1.5 full fine-tune *(community)* |

## Tooling and leaderboards

- **mlx-audio** (MIT) — Apple Silicon runtime; cloning confirmed for Qwen3-TTS, OmniVoice, VoxCPM2, Chatterbox, CSM, Higgs Audio v2/v3, MOSS-TTS. Each model keeps its own weights license. Verified 2026-10-07 — https://github.com/Blaizzy/mlx-audio
- **Hugging Face Open TTS Leaderboard** — WER scored with Qwen3-ASR-1.7B, speaker similarity as cosine of WavLM speaker embeddings (seed-tts-eval model), plus RTFx and CPU/GPU time-to-first-audio. Space created 2026-09-07. Its metrics measure intelligibility and similarity, not naturalness. Verified 2026-10-07 — https://huggingface.co/spaces/hf-audio/open_tts_leaderboard
- **Discovery:** https://huggingface.co/models?pipeline_tag=text-to-speech (sort by trending). With the Hugging Face MCP connected, `hf_fs ls hf://models/trending` and `search hf://models <query>` give live results.

## Legacy and superseded

Use only for a specific need the user names: XTTS-v2 (non-commercial, unmaintained upstream), Tortoise (slow), StyleTTS2 (fast single-speaker fine-tunes), Parler-TTS (text-described voices, not cloning), so-vits-svc (superseded by RVC/Applio), Seed-VC (archived), VibeVoice TTS (code removed), CosyVoice 2 (superseded by 3). Their current state was not re-verified in this pass except where they appear in a table above.

## Practitioner evidence (secondary)

These findings come from a research brief compiled for this skill and were **not independently re-verified**. Cite them as practitioner reports, not benchmarks.

- A single-person blind self-voice test (NexusTrade, Aug 2026; 45 min of one-session phone audio, 11 systems) ranked fine-tuned Dots.TTS soar first and fine-tuned MOSS-TTS v1.5 a close second; MOSS ranked near the bottom zero-shot, so zero-shot rankings say little about fine-tuning potential. The same test found a fine-tuned Qwen3-TTS 1.7B produced "great audio, not my voice", and that pooling clips from different sessions was the largest quality loss.
- Arena Elo figures (Breeze TTS 2 ≈1,215 on the Artificial Analysis Speech Arena, Aug 2026; Voxtral, Breeze, and Fish S2 Pro statistically close on the cloning arena) were reported via an aggregator blog, not read from the arenas directly.
