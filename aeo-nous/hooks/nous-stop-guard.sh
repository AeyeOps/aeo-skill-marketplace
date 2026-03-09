#!/bin/bash
# Fast sync guard for Stop hook — checks context threshold, blocks if high
# All other Stop work (extraction, flush) runs async in nous.py
#
# Stop hook event schema (received as JSON on stdin):
#
#   Common fields (all hook events):
#     session_id          — current session identifier
#     transcript_path     — path to conversation JSONL
#     cwd                 — current working directory
#     permission_mode     — "default", "plan", "acceptEdits", "dontAsk", or "bypassPermissions"
#     hook_event_name     — "Stop"
#     agent_id            — (subagent only) unique subagent identifier; absent on main thread
#     agent_type          — (subagent or --agent) agent name, e.g. "Explore", "security-reviewer"
#
#   Stop-specific fields:
#     stop_hook_active    — true when Claude is already continuing from a prior stop hook
#     last_assistant_message — text content of Claude's final response
#
#   Decision output (JSON on stdout):
#     {"decision":"block","reason":"..."} — prevents Claude from stopping
#     exit 0 with no output              — allows Claude to stop
#
#   Access: input=$(cat); printf '%s' "$input" | jq -r '.field_name'

LOG="$HOME/.claude/aeo-nous.log"

STATUSLINE="$HOME/.claude/statusline-activity.jsonl"
THRESHOLD=80  # Authoritative block threshold; nous.py handles extraction thresholds independently

input=$(cat)

session_id=$(printf '%s' "$input" | jq -r '.session_id // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')
stop_hook_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
# Provenance: skip non-interactive sessions (subagents, team leads, --agent)
agent_id=$(printf '%s' "$input" | jq -r '.agent_id // ""')
agent_type=$(printf '%s' "$input" | jq -r '.agent_type // ""')
ts=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
project=${cwd:-"?"}

log_guard() {
  jq -n -c --arg ts "$1" --argjson pid $$ \
    --arg sid "${session_id:0:8}" --arg project "$project" \
    --arg event "$2" \
    '{ts:$ts,pid:$pid,sid:$sid,project:$project,role:"guard",event:$event}' >> "$LOG"
}

log_guard "$ts" "GUARD_ENTER"

# Only guard interactive human sessions — skip subagents, team leads, --agent
if [ -n "$agent_id" ] || [ -n "$agent_type" ]; then
  log_guard "$ts" "GUARD_SKIP agent=${agent_type:-$agent_id}"
  exit 0
fi

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

if [ "$pct" -ge "$THRESHOLD" ] 2>/dev/null; then
  printf '{"decision":"block","reason":"Context at %s%%. Run /clear (not /compact) to start fresh. Learnings have been extracted and will be injected automatically.\\n\\nOptional: Before clearing, ask Claude for a concise continuation prompt that captures current task state - copy it, /clear, then paste to resume."}' "$pct"
  ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
  log_guard "$ts_exit" "GUARD_BLOCK ctx=${pct}%"
  exit 0
fi

ts_exit=$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')
log_guard "$ts_exit" "GUARD_EXIT ctx=${pct}%"
exit 0
