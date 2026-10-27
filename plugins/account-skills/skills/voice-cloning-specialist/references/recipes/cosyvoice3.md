# CosyVoice 3 recipe

Apache-2.0 code and weights; Fun-CosyVoice3-0.5B-2512 supersedes CosyVoice 2. Source: https://github.com/FunAudioLLM/CosyVoice and https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (verified 2026-10-07).

## Install

Follow the README and the repo Dockerfile exactly; this project is sensitive to versions.

```bash
git clone --recursive https://github.com/FunAudioLLM/CosyVoice && cd CosyVoice
conda create -n cosyvoice -y python=3.10
conda activate cosyvoice
pip install -r requirements.txt
```

Practitioner-reported pitfalls (not in the README):
- Install `pynini` from conda-forge (`conda install -c conda-forge pynini==2.1.5`) if pip fails to build it.
- `conda activate` does nothing in non-interactive shells; call the env's Python by absolute path in scripts.
- The inference functions return generators. Consume the whole generator and concatenate the chunks, or audio is silently truncated.

## Zero-shot cloning

Use the zero-shot inference example in the README with a short reference clip and its transcript. CosyVoice 3 supports bi-streaming with latency as low as 150 ms.

## Fine-tune

The README points to training and inference scripts in `examples/libritts`. Adapt that recipe:
1. Prepare your clips and transcripts in the recipe's Kaldi-style data directory layout (see the recipe's data-prep stage).
2. Point the config's pretrained model at Fun-CosyVoice3-0.5B-2512.
3. Run the recipe's stages in order, saving a checkpoint every epoch.

Practitioner report: about 22 s per epoch for 45 min of audio on an RTX 4090, with the best checkpoint at epoch 4 of 31. Checkpoints are about 2 GB each, so prune as you go.

## Hardware

0.5B parameters. CUDA on Linux is the supported path; no official VRAM figure.
