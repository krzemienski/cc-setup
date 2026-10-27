#!/usr/bin/env bash
# probe_audio.sh — report the facts that matter for voice cloning about one audio file:
# container/codec, duration, sample rate, channels, bit depth, integrated loudness (LUFS),
# true peak, sample peak, and a short verdict against common training targets.
#
# Usage: probe_audio.sh <audio-file> [--target-rate HZ]
# Requires: ffprobe and ffmpeg (from FFmpeg). Exits 2 with an install hint if missing.

set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") <audio-file> [--target-rate HZ]" >&2
  echo "  --target-rate HZ   sample rate your chosen model trains at (e.g. 24000, 44100, 48000)" >&2
}

if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 1
fi

FILE="$1"; shift
TARGET_RATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-rate) TARGET_RATE="${2:-}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

for bin in ffprobe ffmpeg; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "error: '$bin' not found on PATH." >&2
    echo "Install FFmpeg first:" >&2
    echo "  macOS:          brew install ffmpeg" >&2
    echo "  Debian/Ubuntu:  sudo apt-get install -y ffmpeg" >&2
    echo "  Fedora:         sudo dnf install -y ffmpeg" >&2
    echo "  Windows:        winget install Gyan.FFmpeg" >&2
    exit 2
  fi
done

if [[ ! -f "$FILE" ]]; then
  echo "error: file not found: $FILE" >&2
  exit 1
fi

probe() {
  ffprobe -v error -select_streams a:0 -show_entries "$1" -of default=noprint_wrappers=1:nokey=1 "$FILE" 2>/dev/null | head -n1
}

FORMAT=$(ffprobe -v error -show_entries format=format_name -of default=noprint_wrappers=1:nokey=1 "$FILE" | head -n1)
CODEC=$(probe stream=codec_name)
if [[ -z "$CODEC" ]]; then
  echo "error: no audio stream found in $FILE" >&2
  exit 1
fi
RATE=$(probe stream=sample_rate)
CHANNELS=$(probe stream=channels)
BITS=$(probe stream=bits_per_raw_sample)
[[ -z "$BITS" || "$BITS" == "N/A" || "$BITS" == "0" ]] && BITS=$(probe stream=bits_per_sample)
[[ "$BITS" == "N/A" || "$BITS" == "0" ]] && BITS=""
SAMPLE_FMT=$(probe stream=sample_fmt)
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FILE" | head -n1)

# Loudness (EBU R128) and true peak via loudnorm in analysis mode.
LOUD_JSON=$(ffmpeg -hide_banner -nostats -i "$FILE" -map 0:a:0 -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
LUFS=$(printf '%s\n' "$LOUD_JSON" | sed -n 's/.*"input_i" *: *"\([^"]*\)".*/\1/p')
TRUE_PEAK=$(printf '%s\n' "$LOUD_JSON" | sed -n 's/.*"input_tp" *: *"\([^"]*\)".*/\1/p')
LRA=$(printf '%s\n' "$LOUD_JSON" | sed -n 's/.*"input_lra" *: *"\([^"]*\)".*/\1/p')

# Sample peak and mean level via volumedetect.
VOL=$(ffmpeg -hide_banner -nostats -i "$FILE" -map 0:a:0 -af volumedetect -f null - 2>&1)
MAX_VOL=$(printf '%s\n' "$VOL" | sed -n 's/.*max_volume: *\([-0-9.inf]*\) dB.*/\1/p' | head -n1)
MEAN_VOL=$(printf '%s\n' "$VOL" | sed -n 's/.*mean_volume: *\([-0-9.inf]*\) dB.*/\1/p' | head -n1)

printf 'File:            %s\n' "$FILE"
printf 'Container/codec: %s / %s (%s)\n' "${FORMAT:-?}" "$CODEC" "${SAMPLE_FMT:-?}"
printf 'Duration:        %.2f s (%.2f min)\n' "${DURATION:-0}" "$(awk -v d="${DURATION:-0}" 'BEGIN{print d/60}')"
printf 'Sample rate:     %s Hz\n' "${RATE:-?}"
printf 'Channels:        %s\n' "${CHANNELS:-?}"
printf 'Bit depth:       %s\n' "${BITS:-unknown (compressed or float)}"
printf 'Loudness:        %s LUFS integrated, LRA %s LU\n' "${LUFS:-?}" "${LRA:-?}"
printf 'True peak:       %s dBTP\n' "${TRUE_PEAK:-?}"
printf 'Sample peak:     %s dBFS (mean %s dBFS)\n' "${MAX_VOL:-?}" "${MEAN_VOL:-?}"

echo "Checks:"
warn=0
case "$CODEC" in
  mp3|aac|opus|vorbis) echo "  WARN lossy codec ($CODEC): re-record or source WAV/FLAC for training data"; warn=1 ;;
esac
if [[ -n "${CHANNELS:-}" && "$CHANNELS" != "1" ]]; then
  echo "  WARN $CHANNELS channels: convert to mono (ffmpeg -i in -ac 1 out.wav)"; warn=1
fi
if [[ -n "${RATE:-}" && "$RATE" -lt 22050 ]]; then
  echo "  WARN sample rate ${RATE} Hz is below 22.05 kHz: limits quality for most TTS models"; warn=1
fi
if [[ -n "$TARGET_RATE" && -n "${RATE:-}" && "$RATE" != "$TARGET_RATE" ]]; then
  echo "  NOTE resample to ${TARGET_RATE} Hz for your model: ffmpeg -i \"$FILE\" -ar $TARGET_RATE -ac 1 -c:a pcm_s16le out.wav"
fi
if [[ -n "${MAX_VOL:-}" ]] && awk -v p="$MAX_VOL" 'BEGIN{exit !(p >= -0.1)}'; then
  echo "  WARN sample peak at/near 0 dBFS: likely clipping; re-record with peaks around -6 dBFS"; warn=1
fi
if [[ -n "${LUFS:-}" && "$LUFS" != "-inf" ]] && awk -v l="$LUFS" 'BEGIN{exit !(l < -35)}'; then
  echo "  WARN very quiet (${LUFS} LUFS): may be mostly silence or low gain"; warn=1
fi
if [[ "${LUFS:-}" == "-inf" ]]; then
  echo "  WARN file is digital silence"; warn=1
fi
if awk -v d="${DURATION:-0}" 'BEGIN{exit !(d < 3)}'; then
  echo "  NOTE under 3 s: too short even for a zero-shot reference (aim for ~10 s)"
fi
[[ $warn -eq 0 ]] && echo "  OK no format problems detected"
exit 0
