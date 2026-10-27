# LLM-style TTS fine-tuning with Unsloth or Hugging Face Trainer

Covers Orpheus, Sesame CSM, Llasa, Spark-TTS, and OuteTTS: models that predict audio-codec tokens with a language-model backbone, so standard LLM fine-tuning tools work on them. Unsloth publishes Colab notebooks for several of them (https://github.com/unslothai/unsloth); this recipe summarizes the approach rather than reproducing a notebook.

## Check the license first

| Model | Weights | Commercial? | Verified |
|---|---|---|---|
| Orpheus 3B (`canopylabs/orpheus-3b-0.1-ft`) | Apache-2.0, Llama-3.2-3B derivative | Conditional — Llama 3.2 terms likely apply | 2026-10-07 — https://github.com/canopyai/Orpheus-TTS |
| Sesame CSM-1B | Apache-2.0, Llama-3.2-1B backbone, gated | Conditional; card forbids imitating people without consent | 2026-10-07 — https://huggingface.co/sesame/csm-1b |
| Llasa-1B | CC-BY-NC-4.0 | No | 2026-10-07 — https://huggingface.co/HKUSTAudio/Llasa-1B |
| Spark-TTS 0.5B | CC-BY-NC-SA-4.0 | No | 2026-10-07 — https://huggingface.co/SparkAudio/Spark-TTS-0.5B |
| OuteTTS 1.0-0.6B | Apache-2.0 | Yes | 2026-10-07 — https://huggingface.co/OuteAI |

## Approach

1. **Pre-tokenize the audio** into the model's codec tokens: SNAC (24 kHz) for Orpheus, Mimi for CSM, X-codec2 for Llasa, BiCodec for Spark. Each model's repo or notebook includes the encoder step. The labels are codec tokens, not waveforms.
2. **Format each example** as the model's prompt template: text (plus speaker name or context) followed by the target audio tokens.
3. **Train a 16-bit LoRA**, not 4-bit; quantized training noticeably hurts audio quality (Unsloth guidance). Typical starting points: rank 16–64, learning rate around 2e-4, 1–3 epochs on roughly 1,000+ clips. Save often and audition.
4. **Choose the right base.** Starting from Orpheus `-ft` converges to a consistent voice faster than the `-pretrained` base. CSM is a base model: give it speaker context at inference or the voice drifts.
5. **Expressive tags** such as `<laugh>` and `<sigh>` in transcripts (Orpheus convention) teach controllable non-verbal sounds if they occur in your recordings.

## Orpheus official path

The Orpheus repo ships `finetune/train.py` and `finetune/config.yaml` (Hugging Face Trainer). Serve the result with vLLM (`pip install orpheus-speech`) or export to GGUF for llama.cpp.

## CSM official path

The CSM model card documents fine-tuning with the Transformers Trainer (Transformers 4.52.1 or newer). The GitHub repo itself has had no commits since 2025-05-27.
