# RVC via Applio recipe (voice conversion)

MIT code and weights. Source: https://github.com/IAHispano/Applio (verified 2026-10-07; latest release v3.6.5, 2026-09-19; the README says the project is now in maintenance mode).

RVC converts **audio to audio**: you speak or sing, and the output is in the target voice. It does not read text. Pair it with any TTS if the user also wants text input (TTS in a neutral voice, then convert).

## Install and run

- Windows: `run-install.bat`, then `run-applio.bat`.
- Linux/macOS: `./run-install.sh`, then `./run-applio.sh`.
- macOS support is limited; training wants an NVIDIA GPU (AMD via ROCm/ZLUDA is community-supported). Inference can run on CPU.

## Dataset

- 10–30+ minutes of **dry** (no reverb, no music) speech, 44.1 or 48 kHz mono WAV. Add singing if you want singing output.
- No transcripts. A folder of WAVs is enough; Applio slices it during preprocessing.
- Run `scripts/check_dataset.py <folder> --max-sec 600` first to catch silence, clipping, and mixed sample rates (long files are fine here, hence the raised `--max-sec`).

## Train (Train tab)

1. Preprocess the dataset at the sample rate of the pretrained base you choose (40k or 48k).
2. Extract features with the **RMVPE** pitch method.
3. Train with batch size 8–16 on an 8–12 GB card (community guidance), saving every 10–25 epochs.
4. Watch the generator loss in TensorBoard; stop around where it bottoms out before rising. Applio removed its old overtraining detector, so audition saved epochs by ear.
5. **Build the FAISS index.** It reduces leakage of the source speaker's timbre.

## Inference

- Index rate 0.5–0.75 and protect around 0.33 to preserve consonants (community defaults).
- Adjust pitch (semitones) when converting across genders.
- **Realtime tab** (since v3.5.0): live mic → converted voice, with ASIO support on Windows.

## Model file safety

RVC voice models are shared as PyTorch `.pth` checkpoints, which use Python's native object serialization and can execute arbitrary code when loaded. Load only models you trained yourself or that come from a source you trust, never random downloads, and prefer `.safetensors` or ONNX exports where available. Most community "celebrity" RVC models were also made without the speaker's consent; do not use them (see `references/ethics-consent.md`).

## Using the converted voice live (Discord, OBS, games)

1. Install a virtual audio cable (for example VB-Audio Virtual Cable on Windows or macOS).
2. In Applio's Realtime tab, set the input to your physical mic and the output to the virtual cable's input.
3. In Discord (or OBS, or the game), set the input device to the virtual cable's output.
4. Turn off Discord's noise suppression, echo cancellation, and automatic gain control for that device; they process the converted voice a second time and add artifacts.
5. Expect added latency. Applio publishes no fixed figure; it depends on GPU, chunk size, and pitch method. Measure it by recording yourself, and raise the chunk size if audio crackles.
6. Tell the people in the call that a voice changer is on when there is any chance they could be misled.

## Zero-shot alternative

Seed-VC (GPL-3.0) converts from a 1–30 s reference without training, but the upstream repo was archived on 2025-11-21. For live use, the community fork `jiaheguo521/seed-vc-realtime` keeps only the real-time path.
