# Dots.TTS recipe

Apache-2.0 code and weights. Source: https://github.com/studio-dots-ai/dots.tts and https://huggingface.co/dots-studio/dots.tts-soar (verified 2026-10-07). The GitHub org is `studio-dots-ai`; the Hugging Face org is `dots-studio`.

## Install

```bash
python -m venv .venv && source .venv/bin/activate   # Python 3.10–3.12
git clone https://github.com/studio-dots-ai/dots.tts && cd dots.tts
pip install -e '.[full]' -c constraints/recommended.txt
```

If pip reports a conflict involving `gradio` in the constraints file, remove that line and retry (practitioner report).

## Zero-shot cloning

```bash
dots.tts \
  --model-name-or-path dots-studio/dots.tts-soar \
  --text "Text to speak in the cloned voice." \
  --prompt-audio reference.wav \
  --prompt-text "The exact transcript of reference.wav." \
  --output clone.wav
```

- Keep the reference around 10 s; the README says longer audio does not help.
- `--prompt-text` must match the reference exactly; mismatches cause word errors.
- `--prompt-audio` alone gives x-vector-only cloning (timbre only, lower similarity).
- `--optimize` compiles the model (about 3 minutes of warmup on H800) and is recommended for repeated or streaming use.
- Checkpoints: `dots.tts-soar` (best similarity), `dots.tts-mf` / `-mf-2steps` / `-mf-1step` (faster, distilled), `-mf-2steps-stts` (double streaming).

## Fine-tune

1. Build a JSONL manifest, one row per clip: `{"fid": "clip_0001", "audio": "/abs/path/clip_0001.wav", "text": "Transcript."}`. Use 48 kHz mono WAVs. Hold out ~5% as a validation JSONL.
2. Copy `configs/dots_tts.yaml` (it is a smoke config) and set:
   - `train.pretrained_model_path` → `dots-studio/dots.tts-soar`
   - `train_data.sources` / `val_data.sources` → your JSONL files
   - `train.output_dir` → where checkpoints go
   - `train.max_train_steps` → start small and save often (see fine-tuning.md section 5)
3. Train: `accelerate launch scripts/train_dots_tts.py --config configs/my_voice.yaml`
4. Audition checkpoints with `--model-name-or-path <checkpoint dir>` plus a training clip as `--prompt-audio`. Without a prompt, a fine-tuned single-speaker checkpoint samples in its learned voice.
5. Optional: distill your fine-tune to MeanFlow for low latency with `scripts/train_dots_tts_meanflow.py` (see README for `--teacher-model-path`).

## Hardware

Inference peaks at about 7.9 GB (soar) / 5.7 GB (mf) on H800 per the README. Training memory is not documented; a 24 GB GPU is the practical floor (community).
