# Running and serving a cloned voice

## Local inference by platform

| Platform | Option |
|---|---|
| NVIDIA GPU | Each project's own CLI or Python API (see recipes); vLLM-Omni / SGLang-Omni for models that support them (Dots.TTS, Fish S2 Pro, Voxtral, Higgs) |
| Apple Silicon | `mlx-audio` (MIT, https://github.com/Blaizzy/mlx-audio) — cloning with Qwen3-TTS, VoxCPM2, OmniVoice, Chatterbox, CSM, Higgs, MOSS-TTS; 4-bit or 8-bit conversions under `mlx-community/*` on Hugging Face |
| CPU | Chatterbox Nano, pocket-tts, GPT-SoVITS (slow), Piper/Kokoro (no cloning); GGUF builds where a project publishes them |
| Edge / Raspberry Pi | Piper ONNX with a trained custom voice |

## Serving as an API

- Several projects expose an OpenAI-compatible `/v1/audio/speech` endpoint through vLLM-Omni or SGLang-Omni. Check each project's README for the exact launch command and supported checkpoints.
- Dots.TTS, VoxCPM2, and F5-TTS ship Gradio apps for quick local demos. F5 also publishes `ghcr.io/swivid/f5-tts:main`.
- For a fine-tuned private model, a Hugging Face Inference Endpoint with a custom handler, or a small FastAPI wrapper around the project's Python API on a rented GPU, is enough.

## Performance levers

- Compile or graph-capture where offered: Dots.TTS `--optimize`, GPT-SoVITS v5 CUDA graphs, VoxCPM2 Nano-vLLM.
- 8-bit quantization is usually transparent; listen carefully at 4-bit, where prosody degrades first in codec-token models.
- Stream sentence by sentence for long text; most models are tuned for utterances under ~30 s.

## Before exposing a cloned voice to anyone else

- Re-read the weights license for the base model (`references/model-landscape.md`). A non-commercial base makes the whole service non-commercial.
- Keep or add a watermark and disclose synthetic audio (`references/ethics-consent.md`).
- Gate the endpoint: authentication, rate limits, and logging. An open endpoint that speaks in a real person's voice is a fraud tool.

## Optional MCP backends

If a Hugging Face MCP server is connected, its Space tools can run public TTS demo Spaces (for example a Qwen3-TTS or Chatterbox demo) for a quick listen without local setup. Treat this as a convenience only: public Spaces process the reference audio on third-party infrastructure, so do not upload someone's voice there without their consent, and do not depend on Spaces for real work.
