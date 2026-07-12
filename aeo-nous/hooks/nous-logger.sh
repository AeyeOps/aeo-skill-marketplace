#!/bin/bash
# Nous Activity Logger
# Reads Claude Code status JSON from stdin, enriches with timestamp/host,
# appends to activity JSONL. No stdout output - safe to use in pipeline.

LOGFILE="$HOME/.claude/statusline-activity.jsonl"
LOCKFILE="$HOME/.claude/.statusline-rotate.lock"
LOG_ROTATE_AT=1000
LOG_KEEP=500

input=$(cat)

# Skip entries where context window is not yet populated (session startup)
if echo "$input" | jq -e '.context_window.used_percentage == null' >/dev/null 2>&1; then
    exit 0
fi

# Enrich and append
# Fixed .000 millisecond field: BSD date (macOS) has no %N. meta_ts must match
# nous.py's strict .NNNZ pattern (write_extraction_cursor), which .000Z does.
ts=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
host=$(hostname)
echo "$input" | jq -c --arg ts "$ts" --arg host "$host" '{meta_ts: $ts, meta_host: $host} + .' >> "$LOGFILE"

# Log rotation (non-blocking)
if [ "$(wc -l < "$LOGFILE" 2>/dev/null || echo 0)" -ge "$LOG_ROTATE_AT" ]; then
    (
        flock -n 9 || exit 0
        tail -"$LOG_KEEP" "$LOGFILE" > "$LOGFILE.tmp" && mv "$LOGFILE.tmp" "$LOGFILE"
    ) 9>"$LOCKFILE" 2>/dev/null
fi
