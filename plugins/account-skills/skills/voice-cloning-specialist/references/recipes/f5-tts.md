# F5-TTS recipe

**License:** MIT code, **CC-BY-NC-4.0 checkpoints** (trained on Emilia). Personal and research use only. Source: https://github.com/SWivid/F5-TTS (verified 2026-10-07).

## Install

```bash
# Install the PyTorch build for your platform first (see README), then:
pip install f5-tts
# or, for training:
git clone https://github.com/SWivid/F5-TTS && cd F5-TTS && pip install -e .
```

## Zero-shot cloning

```bash
f5-tts_infer-cli --model F5TTS_v1_Base \
  --ref_audio reference.wav \
  --ref_text "Exact transcript of reference.wav." \
  --gen_text "Text to speak in the cloned voice."
```

- Keep the reference under 12 s with about 1 s of trailing silence; total length per generation (prompt + output) is about 30 s, so chunk long text.
- Leaving `--ref_text ""` makes it transcribe the reference with ASR (more GPU memory, risk of mismatch).
- Gradio UI: `f5-tts_infer-gradio`. Docker: `ghcr.io/swivid/f5-tts:main`.

## Fine-tune

The Gradio fine-tune app covers transcription, vocabulary check, data preparation, training, testing, and checkpoint pruning:

```bash
f5-tts_finetune-gradio
```

CLI path:
1. Make `metadata.csv` with `wav_path|text`, 3–12 s clips, 24 kHz mono.
2. Prepare: `python src/f5_tts/train/datasets/prepare_csv_wavs.py <input_dir> data/<name>_pinyin` (the tokenizer suffix is appended to the dataset name; a wrong vocab path is the most common failure).
3. Train from the v1 Base checkpoint:
   ```bash
   accelerate launch src/f5_tts/train/finetune_cli.py --exp_name F5TTS_v1_Base \
     --dataset_name <name> --finetune --learning_rate 1e-5 \
     --batch_size_per_gpu 3200 --batch_size_type frame --epochs 50 --save_per_updates 500
   ```
   These values come from the research brief; confirm flags with `--help` in your installed version.
4. A fine-tuned single-speaker checkpoint still needs a reference clip at inference.

For a new language, supply a custom vocabulary with `--tokenizer custom --tokenizer_path vocab.txt`.
