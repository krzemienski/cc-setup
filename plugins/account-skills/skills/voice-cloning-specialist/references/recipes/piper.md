# Piper custom voice recipe (CPU and edge)

GPL-3.0 code; each voice has its own license on its model card. Source: https://github.com/OHF-Voice/piper1-gpl (verified 2026-10-07; v1.8.0; the project says it is looking for maintainers).

Piper has no zero-shot cloning. You train a small VITS voice from your recordings (on a GPU), then run it anywhere, including a Raspberry Pi, in real time on CPU via ONNX.

## Install (training)

```bash
git clone https://github.com/OHF-Voice/piper1-gpl && cd piper1-gpl
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[train]'
./build_monotonic_align.sh
```

You also need `build-essential`, `cmake`, `ninja`, and `espeak-ng`. See `docs/TRAINING.md` in the repo for the current flags.

## Dataset

`wavs/` + `metadata.csv` with `utt1.wav|Text` per line (multi-speaker: `utt1.wav|speaker|Text`), 22.05 kHz mono for medium quality. Validate with `scripts/check_dataset.py wavs/ --manifest metadata.csv`.

## Train

Fine-tuning from an existing medium checkpoint (Hugging Face dataset `rhasspy/piper-checkpoints`) is strongly recommended and much faster, even across languages:

```bash
python3 -m piper.train fit \
  --data.voice_name "my_voice" \
  --data.csv_path metadata.csv \
  --data.audio_dir wavs/ \
  --model.sample_rate 22050 \
  --data.espeak_voice "en-us" \
  --data.cache_dir cache/ \
  --data.config_path config.json \
  --data.batch_size 32 \
  --ckpt_path <medium checkpoint .ckpt>
```

Lower `--data.batch_size` on smaller GPUs (8 GB is community-reported to work).

## Export

```bash
python3 -m piper.train.export_onnx --checkpoint <last.ckpt> --output-file en_US-my_voice-medium.onnx
cp config.json en_US-my_voice-medium.onnx.json
```

ONNX export has been reported to fail on Apple Silicon; export on Linux.
