#!/usr/bin/env bash
set -euo pipefail

DEBUG_DIR="${DEBUG_DIR:-$HOME/.claude/debug}"
PATTERN="${PATTERN:-keybindings|voice|record|microphone|audio|warmup}"

latest_debug_file() {
  find "$DEBUG_DIR" -type f -name '*.txt' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | awk '{print $2}'
}

if [[ ! -d "$DEBUG_DIR" ]]; then
  echo "Debug dir not found: $DEBUG_DIR" >&2
  exit 1
fi

debug_file="$(latest_debug_file)"
if [[ -z "$debug_file" ]]; then
  echo "No Claude debug files found in $DEBUG_DIR" >&2
  exit 1
fi

echo "Watching: $debug_file"
echo "Filter:   $PATTERN"
echo "Press Ctrl+C to stop."
echo

tail -n 0 -F "$debug_file" | rg --line-buffered -i "$PATTERN"
