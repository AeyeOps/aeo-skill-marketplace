#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${LOG_FILE:-$PWD/voice-keyprobe.$(date +%Y%m%d-%H%M%S).log}"

restore_tty() {
  stty sane 2>/dev/null || true
}

trap restore_tty EXIT INT TERM

describe_sequence() {
  local hex="$1"
  case "$hex" in
    "1b 5b 42")
      printf 'down\n'
      ;;
    "1b 5b 31 3b 35 42")
      printf 'ctrl+down\n'
      ;;
    "1b 5b 31 3b 35 46")
      printf 'ctrl+end\n'
      ;;
    "1b 5b 33 3b 32 7e")
      printf 'shift+delete\n'
      ;;
    "1b 5b 31 3b 32 42")
      printf 'shift+down\n'
      ;;
    "1b 5b 31 3b 36 42")
      printf 'ctrl+shift+down\n'
      ;;
    *)
      printf 'unknown\n'
      ;;
  esac
}

exec > >(tee -a "$LOG_FILE") 2>&1

printf 'Voice key probe\n'
printf 'Log file: %s\n' "$LOG_FILE"
printf 'Press keys in this terminal. Press Ctrl+C to stop.\n'
printf 'Expected ctrl+down bytes in xterm-style terminals: 1b 5b 31 3b 35 42\n'
printf 'Expected ctrl+end bytes in xterm-style terminals:  1b 5b 31 3b 35 46\n'
printf 'Expected shift+delete bytes in xterm-style terminals: 1b 5b 33 3b 32 7e\n\n'

stty -echo -icanon time 1 min 0

while true; do
  chunk=""
  if ! IFS= read -rsn1 first; then
    continue
  fi
  chunk+="$first"

  while IFS= read -rsn1 -t 0.05 next; do
    chunk+="$next"
  done

  hex="$(printf '%s' "$chunk" | od -An -t x1 | tr -s ' ' | sed 's/^ //; s/ $//')"
  shell_escaped="$(printf '%q' "$chunk")"
  label="$(describe_sequence "$hex")"

  printf '[%s] hex=%s shell=%s label=%s\n' \
    "$(date '+%H:%M:%S')" \
    "$hex" \
    "$shell_escaped" \
    "$label"
done
