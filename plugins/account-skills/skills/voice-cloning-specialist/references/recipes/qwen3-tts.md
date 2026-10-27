# Qwen3-TTS recipe

Apache-2.0 code and weights; 10 languages; 0.6B and 1.7B. Source: https://github.com/QwenLM/Qwen3-TTS, its `finetuning/README.md`, and https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base (verified 2026-10-07).

## Install

```bash
pip install -U qwen-tts
pip install -U flash-attn --no-build-isolation   # optional; then pass attn_implementation="flash_attention_2"
```

## Zero-shot cloning

See `references/fine-tuning.md` section 2 for the full snippet. Key points:
- Use a `-Base` checkpoint (`Qwen3-TTS-12Hz-1.7B-Base` or `0.6B-Base`) for cloning.
- `ref_audio` accepts a path, URL, base64 string, or `(numpy_array, sample_rate)`; `ref_text` is its exact transcript.
- Build a reusable prompt once with `create_voice_clone_prompt(...)` and pass `voice_clone_prompt=` for consistent output across many lines.
- "Design then clone": synthesize a reference with the VoiceDesign model, then clone it — useful for inventing a character voice, not for copying a person.

## Fine-tune (single speaker)

The repo supports **single-speaker** fine-tuning of the `-Base` checkpoints; multi-speaker is listed as future work.

```bash
git clone https://github.com/QwenLM/Qwen3-TTS.git && cd Qwen3-TTS/finetuning
```

1. **Input JSONL**, one object per line, with `audio` (training clip), `text` (its transcript), and `ref_audio` (a reference clip of the speaker). The README strongly recommends using the **same `ref_audio` for every row**; it improves speaker consistency.
   ```jsonl
   {"audio": "./data/utt0001.wav", "text": "She said she would be here by noon.", "ref_audio": "./data/ref.wav"}
   ```
2. **Extract audio codes:**
   ```bash
   python prepare_data.py --device cuda:0 \
     --tokenizer_model_path Qwen/Qwen3-TTS-Tokenizer-12Hz \
     --input_jsonl train_raw.jsonl --output_jsonl train_with_codes.jsonl
   ```
3. **Train** (README example values; lower `--batch_size` on smaller GPUs — the README's script example uses 2):
   ```bash
   python sft_12hz.py --init_model_path Qwen/Qwen3-TTS-12Hz-1.7B-Base \
     --output_model_path output --train_jsonl train_with_codes.jsonl \
     --batch_size 32 --lr 2e-6 --num_epochs 10 --speaker_name my_voice
   ```
   Checkpoints are written per epoch to `output/checkpoint-epoch-N`; audition early ones first.

The README gives no VRAM figure for training. Practitioner caution: one blind test found a fine-tuned 1.7B model sounded clean but drifted away from the speaker. Measure speaker similarity against held-out real recordings (`references/evaluation.md`) before committing to long runs.
