#!/bin/bash
# Hook profiler — temporary instrumentation for latency triage
# Same log format as nous.py: yyMMddHHMMSS.mmm session project message
[ -n "$NOUS_SUBPROCESS" ] && exit 0

LOG="$HOME/.claude/hook-profile.log"
input=$(cat)
read -r event session project <<< $(echo "$input" | jq -r '[.hook_event_name // "unknown", .session_id // "?", .cwd // "?"] | join(" ")')
pid=$$
ts_enter=$(date '+%y%m%d%H%M%S.%3N')
echo "$ts_enter $session $project PROFILE_ENTER event=$event pid=$pid" >> "$LOG"
ts_exit=$(date '+%y%m%d%H%M%S.%3N')
echo "$ts_exit $session $project PROFILE_EXIT event=$event pid=$pid" >> "$LOG"
exit 0
