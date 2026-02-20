#!/bin/bash
# Fast sync guard for Stop hook — checks context threshold, blocks if >65%
# All other Stop work (extraction, flush) runs async in nous.py
LOG="$HOME/.claude/aeo-nous.log"
[ -n "$NOUS_SUBPROCESS" ] && exit 0
STATUSLINE="$HOME/.claude/statusline-activity.jsonl"
THRESHOLD=65  # Authoritative block threshold; nous.py handles extraction thresholds independently

input=$(cat)

session_id=$(printf '%s' "$input" | jq -r '.session_id // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')
stop_hook_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
ts=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
project=${cwd:-"?"}

log_guard() {
  jq -n -c --arg ts "$1" --argjson pid $$ \
    --arg sid "${session_id:0:8}" --arg project "$project" \
    --arg event "$2" \
    '{ts:$ts,pid:$pid,sid:$sid,project:$project,role:"guard",event:$event}' >> "$LOG"
}

log_guard "$ts" "GUARD_ENTER"

if [ "$stop_hook_active" = "true" ]; then
  log_guard "$ts" "GUARD_SKIP stop_hook_active"
  exit 0
fi

if [ ! -f "$STATUSLINE" ]; then
  ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
  log_guard "$ts_exit" "GUARD_EXIT no_statusline"
  exit 0
fi

pct=$(tail -100 "$STATUSLINE" | jq -r --arg sid "$session_id" --arg cwd "$cwd" \
  'select(.session_id == $sid and .cwd == $cwd) | .context_window.used_percentage' \
  | tail -1)

if [ -z "$pct" ] || [ "$pct" = "null" ]; then
  ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
  log_guard "$ts_exit" "GUARD_EXIT no_match"
  exit 0
fi

if [ "$pct" -gt "$THRESHOLD" ] 2>/dev/null; then
  printf '{"decision":"block","reason":"Context at %s%%. Run /clear (not /compact) to start fresh. Learnings have been extracted and will be injected automatically.\\n\\nOptional: Before clearing, ask Claude for a concise continuation prompt that captures current task state - copy it, /clear, then paste to resume."}' "$pct"
  ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
  log_guard "$ts_exit" "GUARD_BLOCK ctx=${pct}%"
  exit 0
fi

ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
log_guard "$ts_exit" "GUARD_EXIT ctx=${pct}%"
exit 0
