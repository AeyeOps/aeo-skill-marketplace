#!/usr/bin/env bash
set -euo pipefail

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.local/share/claude}"
LOG_FILE="${LOG_FILE:-$PWD/kill-claude-cache.$(date +%Y%m%d-%H%M%S).log}"
TRACE="${TRACE:-0}"
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

if [[ "$TRACE" == "1" ]]; then
  set -x
fi

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  printf '[%s] %s\n' "$(timestamp)" "$*"
}

run_cmd() {
  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY_RUN $*"
  else
    "$@"
  fi
}

describe_pid() {
  local pid="$1"
  local exe cmd
  exe="$(readlink -f "/proc/$pid/exe" 2>/dev/null || true)"
  cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  log "PID=$pid EXE=${exe:-unknown} CMD=${cmd:-unknown}"
}

find_claude_pids() {
  local proc pid exe base
  for proc in /proc/[0-9]*; do
    pid="${proc#/proc/}"
    exe="$(readlink -f "$proc/exe" 2>/dev/null || true)"
    base="$(basename "${exe:-}")"
    if [[ "$base" == "claude" ]]; then
      printf '%s\n' "$pid"
    fi
  done
  pgrep -x claude 2>/dev/null || true
}

list_cache_dirs() {
  if [[ ! -d "$CLAUDE_HOME" ]]; then
    return 0
  fi

  find "$CLAUDE_HOME" -mindepth 1 -maxdepth 4 -type d \
    \( -iname '*cache*' -o -name 'GPUCache' \) | sort -u
}

log "Starting Claude cleanup"
log "PWD=$PWD"
log "CLAUDE_HOME=$CLAUDE_HOME"
log "LOG_FILE=$LOG_FILE"
log "TRACE=$TRACE DRY_RUN=$DRY_RUN"

log "Pre-kill Claude process scan:"
mapfile -t pids < <(find_claude_pids | sort -un)
if [[ "${#pids[@]}" -eq 0 ]]; then
  log "No Claude processes detected."
else
  for pid in "${pids[@]}"; do
    describe_pid "$pid"
  done
fi

if [[ "${#pids[@]}" -gt 0 ]]; then
  log "Sending SIGTERM to Claude PIDs: ${pids[*]}"
  run_cmd kill "${pids[@]}" 2>/dev/null || true
  sleep 2
fi

mapfile -t survivors < <(find_claude_pids | sort -un)
if [[ "${#survivors[@]}" -gt 0 ]]; then
  log "Survivors after SIGTERM:"
  for pid in "${survivors[@]}"; do
    describe_pid "$pid"
  done
  log "Sending SIGKILL to survivors: ${survivors[*]}"
  run_cmd kill -9 "${survivors[@]}" 2>/dev/null || true
  sleep 1
fi

mapfile -t final_pids < <(find_claude_pids | sort -un)
if [[ "${#final_pids[@]}" -gt 0 ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY_RUN: Claude processes still running because no signals were actually sent."
    for pid in "${final_pids[@]}"; do
      describe_pid "$pid"
    done
  else
    log "ERROR: Claude processes still running after SIGKILL."
    for pid in "${final_pids[@]}"; do
      describe_pid "$pid"
    done
    exit 1
  fi
else
  log "No Claude processes remain."
fi

log "Enumerating cache directories under $CLAUDE_HOME"
mapfile -t cache_dirs < <(list_cache_dirs)
if [[ "${#cache_dirs[@]}" -eq 0 ]]; then
  log "No cache directories found."
  if [[ -d "$CLAUDE_HOME" ]]; then
    log "Top-level contents of $CLAUDE_HOME:"
    find "$CLAUDE_HOME" -mindepth 1 -maxdepth 2 | sort
  else
    log "Claude home does not exist."
  fi
else
  for cache_dir in "${cache_dirs[@]}"; do
    log "Removing cache dir: $cache_dir"
    run_cmd rm -rf "$cache_dir"
  done
fi

log "Post-clean cache scan:"
mapfile -t remaining_cache_dirs < <(list_cache_dirs)
if [[ "${#remaining_cache_dirs[@]}" -eq 0 ]]; then
  log "No cache directories remain under $CLAUDE_HOME."
else
  log "ERROR: Some cache directories still remain:"
  printf '%s\n' "${remaining_cache_dirs[@]}"
  exit 1
fi

log "Claude cleanup complete."
log "Saved log to $LOG_FILE"
