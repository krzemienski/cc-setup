#!/usr/bin/env bash
# gate_evidence: check that every evidence file a gate names exists and is non-empty,
# then print each one's size and first lines so the reviewer reads them.
# usage: gate_evidence.sh EVIDENCE_DIR file1 [file2 ...]   exit 1 when any is missing or empty
set -uo pipefail
DIR="$1"; shift
missing=0
for f in "$@"; do
  path="$DIR/$f"
  if [ ! -e "$path" ]; then echo "MISSING $path"; missing=1; continue; fi
  if [ -d "$path" ]; then n=$(find "$path" -type f -size +0 | wc -l); echo "DIR     $path ($n non-empty files)"; [ "$n" -gt 0 ] || missing=1; continue; fi
  if [ ! -s "$path" ]; then echo "EMPTY   $path"; missing=1; continue; fi
  echo "OK      $path ($(wc -c <"$path") bytes)"
  case "$path" in *.png|*.jpg|*.zip|*.wav|*.m4a) ;; *) head -n 5 "$path" | sed 's/^/        /';; esac
done
[ "$missing" -eq 0 ] && echo "gate_evidence: all present" || echo "gate_evidence: FAIL"
exit "$missing"
