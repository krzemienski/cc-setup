# Evaluating a cloned voice

Use metrics to triage candidates, then decide by ear. The Hugging Face Open TTS Leaderboard's own documentation describes its metrics as proxies that complement human judgment rather than replace it.

## Test set

- 20–50 sentences **not** in the training transcripts, mixing short (~10 words) and long (100+ words) passages, questions, numbers, and names.
- A few held-out **real recordings** of the speaker from the same session (not used for training or as the reference clip). Similarity is measured against these.
- Render **3–5 takes** per sentence per candidate. Generation is stochastic; score the median.

## Objective metrics

| Metric | What it catches | Tool |
|---|---|---|
| Speaker similarity (SIM) | "Sounds like someone else" | Cosine similarity of speaker embeddings: SpeechBrain ECAPA-TDNN (`speechbrain/spkrec-ecapa-voxceleb`) or WavLM speaker verification (what the HF leaderboard uses) |
| WER / CER | Mispronunciations, dropped or repeated words | Transcribe with Whisper large-v3 or Qwen3-ASR-1.7B, compare to input text with `jiwer` after normalizing case and punctuation |
| Naturalness (relative) | Robotic or noisy output | A MOS predictor such as UTMOS or DNSMOS; compare candidates, ignore absolute numbers |
| Duration ratio | Truncation, dropped phrases | Take length ÷ median take length for the same sentence; flag < 0.85 |

Caveat: ASR-based WER can rank a robotic but clearly articulated take above a natural one and can miss audible word drops (practitioner report). Never pick a checkpoint on WER alone.

## Minimal scoring script

Dependencies (install on the evaluation machine): `pip install speechbrain torchaudio openai-whisper jiwer`.

```python
"""Score generated takes for speaker similarity and WER.

Usage: python score.py real_dir/ takes_dir/ texts.tsv
  real_dir   held-out real recordings of the speaker (.wav)
  takes_dir  generated takes named <sentence_id>_<take>.wav
  texts.tsv  <sentence_id>\t<input text> per line
"""
import csv
import statistics
import sys
from pathlib import Path

import jiwer
import torch
import torchaudio
import whisper
from speechbrain.inference.speaker import EncoderClassifier

real_dir, takes_dir, texts_path = map(Path, sys.argv[1:4])
encoder = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
asr = whisper.load_model("large-v3")
norm = jiwer.Compose([jiwer.ToLowerCase(), jiwer.RemovePunctuation(), jiwer.RemoveMultipleSpaces(), jiwer.Strip()])


def embed(path: Path) -> torch.Tensor:
    wav, sr = torchaudio.load(str(path))
    wav = torchaudio.functional.resample(wav.mean(0, keepdim=True), sr, 16000)
    return encoder.encode_batch(wav).squeeze()


real = torch.stack([embed(p) for p in sorted(real_dir.glob("*.wav"))]).mean(0)
texts = {row[0]: row[1] for row in csv.reader(texts_path.open(encoding="utf-8"), delimiter="\t")}

sims, wers = [], []
for take in sorted(takes_dir.glob("*.wav")):
    sid = take.stem.rsplit("_", 1)[0]
    sim = torch.nn.functional.cosine_similarity(embed(take), real, dim=0).item()
    hyp = asr.transcribe(str(take))["text"]
    wer = jiwer.wer(norm(texts[sid]), norm(hyp))
    sims.append(sim)
    wers.append(wer)
    print(f"{take.name}\tSIM={sim:.3f}\tWER={wer:.3f}")

print(f"median SIM={statistics.median(sims):.3f}  median WER={statistics.median(wers):.3f}")
```

Run it once per checkpoint and compare medians. Higher SIM and lower WER are better; differences of a few hundredths in SIM are within noise.

## Blind A/B listening

1. Normalize every candidate clip to −16 LUFS: `ffmpeg -i in.wav -af loudnorm=I=-16:TP=-1.5 out.wav`.
2. Rename files to random IDs and keep the key elsewhere.
3. Listen in sets of 5–6 clips that include **one real recording as a control**. If the listener cannot pick out the real one, the clone is close.
4. Commit to a ranking before unblinding.
5. Test both short and long scripts; rankings often change with length.

## Iteration order

When results disappoint, change one thing at a time, in this order:
1. **Data:** single session, clean clips, correct transcripts.
2. **Checkpoint:** audition earlier ones before training longer.
3. **Inference settings:** reference clip choice, CFG/guidance, temperature, sampling steps.
4. **Model:** only after the above.

## Common symptoms

| Symptom | Likely cause | Fix |
|---|---|---|
| Sounds like a generic voice | Zero-shot only, under-trained, or base model drifts | Fine-tune; check SIM; try another base |
| Robotic or metallic | Over-processed training data; too few sampling steps | Train on less-processed audio; raise steps/NFE |
| Dropped or truncated words | Stochastic sampling; long inputs; generator not fully consumed | Render several takes and drop short ones; chunk text by sentence; consume streaming output fully |
| Repeats or skips words | Over-trained autoregressive stage (e.g., GPT-SoVITS GPT) | Use an earlier checkpoint |
| Mispronounces numbers or names | Text not normalized; vocabulary gaps | Spell numbers as words; add phonetic spellings; extend vocab (F5 custom tokenizer) |
| Breaths, hum, or room tone reproduced | Present in training data | Trim breaths, light denoise, re-record in one session |
| Only sounds right on training sentences | Overfitting | Earlier checkpoint, lower learning rate, or LoRA |
