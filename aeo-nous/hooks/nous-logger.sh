#!/bin/bash
# Nous Activity Logger
# Reads Claude Code status JSON from stdin, enriches with timestamp/host,
# appends to activity JSONL. No stdout output - safe to use in pipeline.

LOGFILE="$HOME/.claude/statusline-activity.jsonl"
LOCKFILE="$HOME/.claude/.statusline-rotate.lock"
LOG_ROTATE_AT=1000
LOG_KEEP=500

input=$(cat)

# Enrich and append
ts=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)
host=$(hostname)
echo "$input" | jq -c --arg ts "$ts" --arg host "$host" '{meta_ts: $ts, meta_host: $host} + .' >> "$LOGFILE"

# Log rotation (non-blocking)
if [ "$(wc -l < "$LOGFILE" 2>/dev/null || echo 0)" -ge "$LOG_ROTATE_AT" ]; then
    (
        flock -n 9 || exit 0
        tail -"$LOG_KEEP" "$LOGFILE" > "$LOGFILE.tmp" && mv "$LOGFILE.tmp" "$LOGFILE"
    ) 9>"$LOCKFILE" 2>/dev/null
fi
