#!/usr/bin/env python3
"""check_dataset.py — sanity-check a folder of voice clips before training.

Reports clip count, total minutes, sample-rate / channel / bit-depth consistency, and
flags clips that are silent, clipped, too short, or too long. Optionally checks a
transcript manifest (pipe-delimited CSV/.list or JSONL) and compares total minutes to
the length of the source recording, which catches slicers that silently drop audio.

Runs on the Python standard library alone (PCM WAV via `wave`). Uses numpy for speed and
soundfile for FLAC/float WAV when they are installed; neither is required.

Usage:
  check_dataset.py <folder> [--min-sec 2] [--max-sec 15] [--recursive]
                   [--manifest metadata.csv|train.list|train.jsonl]
                   [--source-minutes 45.0] [--json] [--strict]

Exit codes: 0 = ran (problems are reported, not fatal); 1 = bad arguments or no clips;
3 = --strict and at least one problem was found.
"""
from __future__ import annotations

import argparse
import array
import json
import math
import os
import sys
import wave
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:  # optional, speeds up sample statistics a lot
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    np = None

try:  # optional, adds FLAC/OGG and float WAV support
    import soundfile as sf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sf = None

AUDIO_EXTS_STDLIB = {".wav"}
AUDIO_EXTS_SF = {".wav", ".flac", ".ogg"}

SILENCE_RMS_DBFS = -50.0   # whole-clip RMS below this = effectively silent
CLIP_LEVEL = 0.999         # |sample| at or above this fraction of full scale counts as clipped
CLIP_FRACTION = 0.0005     # more than 0.05% clipped samples = flag the clip


@dataclass
class Clip:
    path: str
    duration: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    bits: str = ""
    peak_dbfs: float = float("-inf")
    rms_dbfs: float = float("-inf")
    clipped_fraction: float = 0.0
    flags: list[str] = field(default_factory=list)
    error: str = ""


def _dbfs(x: float) -> float:
    return 20.0 * math.log10(x) if x > 0 else float("-inf")


def _stats_from_floats(samples) -> tuple[float, float, float]:
    """Return (peak, rms, clipped_fraction) for samples scaled to [-1, 1]."""
    if np is not None:
        a = np.abs(np.asarray(samples, dtype=np.float64))
        if a.size == 0:
            return 0.0, 0.0, 0.0
        return float(a.max()), float(np.sqrt(np.mean(a * a))), float(np.mean(a >= CLIP_LEVEL))
    n = len(samples)
    if n == 0:
        return 0.0, 0.0, 0.0
    peak = 0.0
    sq = 0.0
    clipped = 0
    for s in samples:
        v = s if s >= 0 else -s
        if v > peak:
            peak = v
        sq += v * v
        if v >= CLIP_LEVEL:
            clipped += 1
    return peak, math.sqrt(sq / n), clipped / n


def _pcm_to_floats(raw: bytes, sampwidth: int):
    """Decode little-endian PCM bytes into floats in [-1, 1] without numpy if needed."""
    if np is not None:
        if sampwidth == 1:
            return (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
        if sampwidth == 2:
            return np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
        if sampwidth == 3:
            b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
            v = np.where(v >= 1 << 23, v - (1 << 24), v)
            return v.astype(np.float64) / float(1 << 23)
        if sampwidth == 4:
            return np.frombuffer(raw, dtype="<i4").astype(np.float64) / float(1 << 31)
        raise ValueError(f"unsupported sample width {sampwidth}")
    if sampwidth == 1:
        return [(b - 128) / 128.0 for b in raw]
    if sampwidth == 2:
        a = array.array("h")
        a.frombytes(raw)
        if sys.byteorder == "big":
            a.byteswap()
        return [s / 32768.0 for s in a]
    if sampwidth == 3:
        out = []
        for i in range(0, len(raw) - 2, 3):
            v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if v >= 1 << 23:
                v -= 1 << 24
            out.append(v / float(1 << 23))
        return out
    if sampwidth == 4:
        a = array.array("i")
        a.frombytes(raw)
        if sys.byteorder == "big":
            a.byteswap()
        return [s / float(1 << 31) for s in a]
    raise ValueError(f"unsupported sample width {sampwidth}")


def analyze(path: Path) -> Clip:
    clip = Clip(path=str(path))
    try:
        if sf is not None:
            info = sf.info(str(path))
            data, sr = sf.read(str(path), dtype="float64", always_2d=False)
            clip.sample_rate = int(sr)
            clip.channels = int(info.channels)
            clip.bits = info.subtype
            frames = info.frames
            clip.duration = frames / float(sr) if sr else 0.0
            samples = data.reshape(-1) if hasattr(data, "reshape") else data
        else:
            with wave.open(str(path), "rb") as w:
                clip.sample_rate = w.getframerate()
                clip.channels = w.getnchannels()
                width = w.getsampwidth()
                clip.bits = f"PCM_{width * 8}"
                frames = w.getnframes()
                clip.duration = frames / float(clip.sample_rate) if clip.sample_rate else 0.0
                samples = _pcm_to_floats(w.readframes(frames), width)
        peak, rms, clipped = _stats_from_floats(samples)
        clip.peak_dbfs = round(_dbfs(peak), 2)
        clip.rms_dbfs = round(_dbfs(rms), 2)
        clip.clipped_fraction = round(clipped, 6)
    except (wave.Error, EOFError, ValueError, RuntimeError, OSError) as exc:
        hint = "" if sf is not None else " (float/compressed WAV needs: pip install soundfile)"
        clip.error = f"{type(exc).__name__}: {exc}{hint}"
    return clip


def load_manifest(path: Path) -> dict[str, str]:
    """Map clip basename -> transcript from pipe-delimited CSV/.list or JSONL manifests."""
    texts: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("{"):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                audio = row.get("audio") or row.get("audio_path") or row.get("path") or row.get("wav") or ""
                text = row.get("text") or row.get("transcript") or ""
                if audio:
                    texts[Path(str(audio)).name] = str(text)
                continue
            parts = line.split("|")
            if len(parts) >= 2:
                # LJSpeech/F5: file|text ; Piper multi-speaker: file|speaker|text ;
                # GPT-SoVITS .list: path|speaker|lang|text  -> text is always the last field.
                name = Path(parts[0]).name
                if not Path(name).suffix:
                    name += ".wav"
                texts[name] = parts[-1].strip()
    return texts


def main() -> int:
    ap = argparse.ArgumentParser(description="Sanity-check a folder of voice clips before training.")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--min-sec", type=float, default=2.0, help="flag clips shorter than this (default 2)")
    ap.add_argument("--max-sec", type=float, default=15.0, help="flag clips longer than this (default 15)")
    ap.add_argument("--recursive", action="store_true", help="scan subfolders too")
    ap.add_argument("--manifest", type=Path, help="metadata.csv / .list / .jsonl to cross-check transcripts")
    ap.add_argument("--source-minutes", type=float,
                    help="length of the original recording; warns if clips total differs by >10%%")
    ap.add_argument("--json", action="store_true", help="print a JSON report instead of text")
    ap.add_argument("--strict", action="store_true", help="exit 3 if any problem is found")
    args = ap.parse_args()

    if not args.folder.is_dir():
        print(f"error: not a folder: {args.folder}", file=sys.stderr)
        return 1

    exts = AUDIO_EXTS_SF if sf is not None else AUDIO_EXTS_STDLIB
    pattern = "**/*" if args.recursive else "*"
    files = sorted(p for p in args.folder.glob(pattern) if p.is_file() and p.suffix.lower() in exts)
    skipped = sorted(p for p in args.folder.glob(pattern)
                     if p.is_file() and p.suffix.lower() in {".flac", ".mp3", ".ogg", ".m4a"} and p.suffix.lower() not in exts)
    if not files:
        print(f"error: no audio clips ({', '.join(sorted(exts))}) found in {args.folder}", file=sys.stderr)
        return 1

    clips = [analyze(p) for p in files]
    ok = [c for c in clips if not c.error]

    for c in ok:
        if c.duration < args.min_sec:
            c.flags.append(f"short<{args.min_sec:g}s")
        if c.duration > args.max_sec:
            c.flags.append(f"long>{args.max_sec:g}s")
        if c.rms_dbfs < SILENCE_RMS_DBFS:
            c.flags.append("silent")
        if c.clipped_fraction > CLIP_FRACTION:
            c.flags.append("clipped")
        if c.channels > 1:
            c.flags.append("stereo")

    rates = sorted({c.sample_rate for c in ok})
    channels = sorted({c.channels for c in ok})
    depths = sorted({c.bits for c in ok})
    total_sec = sum(c.duration for c in ok)
    total_min = total_sec / 60.0

    problems: list[str] = []
    if len(rates) > 1:
        problems.append(f"mixed sample rates {rates}: resample everything to your model's rate")
    if len(channels) > 1:
        problems.append(f"mixed channel counts {channels}: convert all clips to mono")
    errored = [c for c in clips if c.error]
    if errored:
        problems.append(f"{len(errored)} file(s) could not be read")
    flagged = [c for c in ok if c.flags]
    if flagged:
        problems.append(f"{len(flagged)} clip(s) flagged")

    source_check = None
    if args.source_minutes:
        diff = abs(total_min - args.source_minutes) / args.source_minutes
        source_check = {"source_minutes": args.source_minutes, "clip_minutes": round(total_min, 2),
                        "difference_pct": round(diff * 100, 1)}
        if diff > 0.10:
            problems.append(f"clips total {total_min:.1f} min vs source {args.source_minutes:.1f} min "
                            f"({diff * 100:.0f}% off): the slicer may have dropped audio")

    manifest_check = None
    if args.manifest:
        if not args.manifest.is_file():
            problems.append(f"manifest not found: {args.manifest}")
        else:
            texts = load_manifest(args.manifest)
            names = {Path(c.path).name for c in clips}
            missing_text = sorted(n for n in names if not texts.get(n, "").strip())
            missing_audio = sorted(n for n in texts if n not in names)
            manifest_check = {"entries": len(texts), "clips_without_transcript": missing_text,
                              "manifest_rows_without_audio": missing_audio}
            if missing_text:
                problems.append(f"{len(missing_text)} clip(s) have no transcript in the manifest")
            if missing_audio:
                problems.append(f"{len(missing_audio)} manifest row(s) point to missing audio")

    report = {
        "folder": str(args.folder),
        "clips": len(clips),
        "readable": len(ok),
        "total_minutes": round(total_min, 2),
        "mean_clip_seconds": round(total_sec / len(ok), 2) if ok else 0,
        "sample_rates": rates,
        "channels": channels,
        "bit_depths": depths,
        "numpy": np is not None,
        "soundfile": sf is not None,
        "skipped_unsupported": [str(p) for p in skipped],
        "flagged": [{"path": c.path, "flags": c.flags, "duration": round(c.duration, 2),
                     "rms_dbfs": c.rms_dbfs, "peak_dbfs": c.peak_dbfs} for c in flagged],
        "errors": [{"path": c.path, "error": c.error} for c in errored],
        "source_check": source_check,
        "manifest_check": manifest_check,
        "problems": problems,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Folder:        {args.folder}")
        print(f"Clips:         {len(clips)} ({len(ok)} readable)")
        print(f"Total audio:   {total_min:.2f} min (mean clip {report['mean_clip_seconds']} s)")
        print(f"Sample rates:  {', '.join(str(r) for r in rates) or '-'} Hz"
              f"{'  OK consistent' if len(rates) == 1 else '  MIXED'}")
        print(f"Channels:      {', '.join(str(c) for c in channels) or '-'}")
        print(f"Bit depth:     {', '.join(depths) or '-'}")
        if skipped:
            print(f"Skipped:       {len(skipped)} non-WAV file(s) (pip install soundfile to read FLAC/OGG)")
        if flagged:
            print("Flagged clips:")
            for c in flagged:
                print(f"  {Path(c.path).name:40s} {','.join(c.flags):24s} "
                      f"{c.duration:6.2f}s  rms {c.rms_dbfs} dBFS  peak {c.peak_dbfs} dBFS")
        for c in errored:
            print(f"  ERROR {Path(c.path).name}: {c.error}")
        if source_check:
            print(f"Source check:  clips {source_check['clip_minutes']} min vs source "
                  f"{source_check['source_minutes']} min ({source_check['difference_pct']}% off)")
        if manifest_check:
            print(f"Manifest:      {manifest_check['entries']} rows; "
                  f"{len(manifest_check['clips_without_transcript'])} clip(s) without text; "
                  f"{len(manifest_check['manifest_rows_without_audio'])} row(s) without audio")
        if problems:
            print("Problems:")
            for p in problems:
                print(f"  - {p}")
        else:
            print("Result:        OK no problems found")

    if args.strict and problems:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
