#!/bin/bash
# Fast sync guard for Stop hook — checks context threshold, blocks if >65%
# All other Stop work (extraction, flush) runs async in nous.py
LOG="$HOME/.claude/nous.log"
[ -n "$NOUS_SUBPROCESS" ] && exit 0
STATUSLINE="$HOME/.claude/statusline-activity.jsonl"
THRESHOLD=65  # Authoritative block threshold; nous.py handles extraction thresholds independently

input=$(cat)

session_id=$(printf '%s' "$input" | jq -r '.session_id // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')
stop_hook_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
ts=$(date '+%y%m%d%H%M%S.%3N')
project=${cwd:-"?"}

echo "$ts $session_id $project GUARD_ENTER" >> "$LOG"

if [ "$stop_hook_active" = "true" ]; then
  echo "$ts $session_id $project GUARD_SKIP stop_hook_active" >> "$LOG"
  exit 0
fi

if [ ! -f "$STATUSLINE" ]; then
  ts_exit=$(date '+%y%m%d%H%M%S.%3N')
  echo "$ts_exit $session_id $project GUARD_EXIT no_statusline" >> "$LOG"
  exit 0
fi

pct=$(tail -100 "$STATUSLINE" | jq -r --arg sid "$session_id" --arg cwd "$cwd" \
  'select(.session_id == $sid and .cwd == $cwd) | .context_window.used_percentage' \
  | tail -1)

if [ -z "$pct" ] || [ "$pct" = "null" ]; then
  ts_exit=$(date '+%y%m%d%H%M%S.%3N')
  echo "$ts_exit $session_id $project GUARD_EXIT no_match" >> "$LOG"
  exit 0
fi

if [ "$pct" -gt "$THRESHOLD" ] 2>/dev/null; then
  printf '{"decision":"block","reason":"Context at %s%%. Run /clear (not /compact) to start fresh. Learnings have been extracted and will be injected automatically.\\n\\nOptional: Before clearing, ask Claude for a concise continuation prompt that captures current task state - copy it, /clear, then paste to resume."}' "$pct"
  ts_exit=$(date '+%y%m%d%H%M%S.%3N')
  echo "$ts_exit $session_id $project GUARD_BLOCK ctx=${pct}%" >> "$LOG"
  exit 0
fi

ts_exit=$(date '+%y%m%d%H%M%S.%3N')
echo "$ts_exit $session_id $project GUARD_EXIT ctx=${pct}%" >> "$LOG"
exit 0
