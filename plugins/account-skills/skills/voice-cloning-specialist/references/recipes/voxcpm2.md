# VoxCPM2 recipe

Apache-2.0 code and weights; 30 languages; 48 kHz output. Source: https://github.com/OpenBMB/VoxCPM and https://huggingface.co/openbmb/VoxCPM2 (verified 2026-10-07). Full guide: https://voxcpm.readthedocs.io/en/latest/finetuning/finetune.html

## Install

```bash
pip install voxcpm
```

## Zero-shot cloning

```python
import soundfile as sf
from voxcpm import VoxCPM

model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
wav = model.generate(
    text="Text to speak in the cloned voice.",
    prompt_wav_path="reference.wav",
    prompt_text="Exact transcript of reference.wav.",
    reference_wav_path="reference.wav",   # README: same clip again for best similarity
    cfg_value=2.0,                         # README default; community reports ~2.5 for more similarity
)
sf.write("clone.wav", wav, model.tts_model.sample_rate)
```

`reference_wav_path` alone (no `prompt_*`) clones timbre without continuation.

## Fine-tune

The README states that 5–10 minutes of audio is enough to adapt to a speaker, and recommends LoRA.

```bash
git clone https://github.com/OpenBMB/VoxCPM && cd VoxCPM && pip install -e .
# LoRA (recommended)
python scripts/train_voxcpm_finetune.py --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml
# Full fine-tune
python scripts/train_voxcpm_finetune.py --config_path conf/voxcpm_v2/voxcpm_finetune_all.yaml
# Or the training/inference WebUI
python lora_ft_webui.py    # then open http://localhost:7860
```

Edit `pretrained_path`, `train_manifest` (JSONL), `save_path`, and `tensorboard` in the config before running. Official guidance from the fine-tuning guide (verified 2026-10-07):

- **Single-speaker clone:** 5–50 clips, LoRA, rank 32 (alpha = r or 2r), learning rate 1e-4. The shipped LoRA config runs 1,000 steps and saves every 500 — lower `save_interval` to audition earlier checkpoints.
- **Style or language adaptation:** 50–500 clips, LoRA rank 64. **New language:** 500+ hours, full fine-tune.
- **Full fine-tune:** learning rate 1e-5; converges in about 1–2 epochs.
- The config's `sample_rate: 16000` is the AudioVAE encoder input rate; output is 48 kHz.

LoRA adapters can be hot-swapped at inference without merging.

## Hardware

- Inference: about 8 GB VRAM; RTF ≈0.30 on RTX 4090 (≈0.13 with Nano-vLLM). Apple Silicon inference via mlx-audio.
- Training (official docs, `batch_size=16`, `max_batch_tokens=8192`): LoRA **~20 GB**, full fine-tune **~40 GB**.
- The shipped LoRA config uses `batch_size: 2` with `grad_accum_steps: 8` (effective 16), which needs less memory; the Docker training README states at least 16 GB. On a 12 GB card, LoRA training is not documented to fit — rent a 24 GB GPU for training and run inference locally.
