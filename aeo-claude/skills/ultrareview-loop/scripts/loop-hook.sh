#!/bin/bash

# Ultrareview Loop Stop Hook
# Prevents session exit when an ultrareview-loop is active
# Alternates between ultrareview and ultrareview-fix phases
#
# Layers of protection:
# 1. Session_id match (hook-level gate)
# 2. Staleness check (24h auto-cleanup)
# 3. Max iterations (hard stop)
# 4. Token echo (model-level gate)

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Get current session_id from hook input
CURRENT_SESSION=$(echo "$HOOK_INPUT" | jq -r '.session_id')
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

# Find project root by walking up from cwd looking for .claude/ or .git/ directory
find_project_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/.claude" ]] || [[ -d "$dir/.git" ]]; then
      echo "$dir"
      return 0
    fi
    dir=$(dirname "$dir")
  done
  return 1
}

# Use || true to prevent set -e from triggering on return 1
PROJECT_ROOT=$(find_project_root) || true
if [[ -z "$PROJECT_ROOT" ]]; then
  # No .claude directory found - allow exit
  exit 0
fi

# Find all ultrareview-loop state files (token in filename)
shopt -s nullglob
STATE_FILES=("$PROJECT_ROOT"/.claude/ultrareview-loop-*.local.md)
shopt -u nullglob

if [[ ${#STATE_FILES[@]} -eq 0 ]]; then
  # No active loops - allow exit
  exit 0
fi

# Find OUR state file (matching session_id)
MY_STATE_FILE=""
for STATE_FILE in "${STATE_FILES[@]}"; do
  FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
  STORED_SESSION=$(echo "$FRONTMATTER" | grep '^session_id:' | sed 's/session_id: *//' | sed 's/^"\(.*\)"$/\1/')
  STARTED_AT=$(echo "$FRONTMATTER" | grep '^started_at:' | sed 's/started_at: *//' | sed 's/^"\(.*\)"$/\1/')

  # Check staleness (24 hours)
  if [[ -n "$STARTED_AT" ]]; then
    STARTED_EPOCH=$(date -d "$STARTED_AT" +%s 2>/dev/null || date -jf '%Y-%m-%dT%H:%M:%SZ' "$STARTED_AT" +%s 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    AGE_HOURS=$(( (NOW_EPOCH - STARTED_EPOCH) / 3600 ))
    if [[ $AGE_HOURS -gt 24 ]]; then
      echo "Stale ultrareview loop (${AGE_HOURS}h old). Cleaning up: $STATE_FILE" >&2
      rm "$STATE_FILE"
      continue
    fi
  fi

  # Check session_id
  if [[ "$STORED_SESSION" == "null" ]] || [[ -z "$STORED_SESSION" ]]; then
    # First run - capture this session as the loop owner
    TEMP_FILE="${STATE_FILE}.tmp.$$"
    sed "s/^session_id: .*/session_id: \"$CURRENT_SESSION\"/" "$STATE_FILE" > "$TEMP_FILE"
    mv "$TEMP_FILE" "$STATE_FILE"
    MY_STATE_FILE="$STATE_FILE"
    break
  elif [[ "$CURRENT_SESSION" == "$STORED_SESSION" ]]; then
    # This is our loop
    MY_STATE_FILE="$STATE_FILE"
    break
  fi
  # Otherwise, not our loop - continue checking other files
done

if [[ -z "$MY_STATE_FILE" ]]; then
  # No matching state file for this session - allow exit
  exit 0
fi

# Parse our state file
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$MY_STATE_FILE")
TOKEN=$(echo "$FRONTMATTER" | grep '^token:' | sed 's/token: *//' | sed 's/^"\(.*\)"$/\1/')
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
PHASE=$(echo "$FRONTMATTER" | grep '^phase:' | sed 's/phase: *//' | sed 's/^"\(.*\)"$/\1/')
INITIAL_FOCUS=$(echo "$FRONTMATTER" | grep '^initial_focus:' | sed 's/initial_focus: *//' | sed 's/^"\(.*\)"$/\1/')

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Ultrareview loop: State file corrupted (iteration: '$ITERATION')" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Ultrareview loop: State file corrupted (max_iterations: '$MAX_ITERATIONS')" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi

# Check max iterations
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "Ultrareview loop: Max iterations ($MAX_ITERATIONS) reached."
  rm "$MY_STATE_FILE"
  exit 0
fi

# Validate transcript
if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Ultrareview loop: Transcript not found" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi

# Read last assistant message (scan from end for performance on large transcripts)
LAST_LINE=$(tac "$TRANSCRIPT_PATH" | grep -m1 '"role":"assistant"' || true)
if [[ -z "$LAST_LINE" ]]; then
  echo "Ultrareview loop: No assistant messages in transcript" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi
if ! LAST_OUTPUT=$(echo "$LAST_LINE" | jq -r '.message.content | map(select(.type == "text")) | map(.text) | join("\n")' 2>&1); then
  echo "Ultrareview loop: Failed to parse transcript" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi

if [[ -z "$LAST_OUTPUT" ]]; then
  echo "Ultrareview loop: Empty assistant message" >&2
  rm "$MY_STATE_FILE"
  exit 0
fi

# Check for actionable findings using the structured summary block
# The ultrareview skill outputs: <ultrareview_summary>status: PASS|NEEDS_ACTION</ultrareview_summary>
HAS_ACTIONABLE=false

# Extract the summary block
if echo "$LAST_OUTPUT" | grep -q '<ultrareview_summary>'; then
  # Parse status from summary block
  REVIEW_STATUS=$(echo "$LAST_OUTPUT" | grep -o 'status: [A-Z_]*' | head -1 | sed 's/status: //')

  if [[ "$REVIEW_STATUS" == "NEEDS_ACTION" ]]; then
    HAS_ACTIONABLE=true
  elif [[ "$REVIEW_STATUS" == "PASS" ]]; then
    HAS_ACTIONABLE=false
  else
    # Fallback: check individual counts if status not found
    CRITICAL=$(echo "$LAST_OUTPUT" | grep -o 'critical: [0-9]*' | head -1 | sed 's/critical: //')
    ERRORS=$(echo "$LAST_OUTPUT" | grep -o 'errors: [0-9]*' | head -1 | sed 's/errors: //')
    ALIGNMENT=$(echo "$LAST_OUTPUT" | grep -o 'alignment: [0-9]*' | head -1 | sed 's/alignment: //')
    MISSING=$(echo "$LAST_OUTPUT" | grep -o 'missing: [0-9]*' | head -1 | sed 's/missing: //')
    NEEDS_VAL=$(echo "$LAST_OUTPUT" | grep -o 'needs_validation: [0-9]*' | head -1 | sed 's/needs_validation: //')

    TOTAL=$((${CRITICAL:-0} + ${ERRORS:-0} + ${ALIGNMENT:-0} + ${MISSING:-0} + ${NEEDS_VAL:-0}))
    if [[ $TOTAL -gt 0 ]]; then
      HAS_ACTIONABLE=true
    fi
  fi
else
  # No summary block found - conservatively assume actionable findings exist
  HAS_ACTIONABLE=true
fi

# Decision logic
if [[ "$PHASE" == "review" ]]; then
  if [[ "$HAS_ACTIONABLE" == "false" ]]; then
    echo "Ultrareview loop complete: No actionable findings detected."
    echo "   Iterations: $ITERATION"
    echo ""
    echo "   BEFORE ACCEPTING: Re-read initial_focus and verify you delivered it:"
    echo "   \"$INITIAL_FOCUS\""
    echo "   If not delivered, run /ultrareview-fix to continue implementation."
    rm "$MY_STATE_FILE"
    exit 0
  fi
  NEXT_PHASE="fix"
  COMMAND="/ultrareview-fix"
else
  NEXT_PHASE="review"
  if [[ "$INITIAL_FOCUS" != "null" ]] && [[ -n "$INITIAL_FOCUS" ]]; then
    COMMAND="/ultrareview $INITIAL_FOCUS"
  else
    COMMAND="/ultrareview"
  fi
fi

# Update state file
NEXT_ITERATION=$((ITERATION + 1))
TEMP_FILE="${MY_STATE_FILE}.tmp.$$"
sed -e "s/^iteration: .*/iteration: $NEXT_ITERATION/" \
    -e "s/^phase: .*/phase: $NEXT_PHASE/" \
    "$MY_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$MY_STATE_FILE"

# Build prompt with token verification
NEXT_PROMPT="<ultrareview_loop_continue>
<token>$TOKEN</token>
<phase>$NEXT_PHASE</phase>
<iteration>$NEXT_ITERATION</iteration>
<command>$COMMAND</command>
</ultrareview_loop_continue>

Before continuing, verify this is your loop:
1. State your token by completing: \"Confirmed: my loop token is ___\"
2. If your token does not match exactly: $TOKEN
   then stop and say \"This loop belongs to another session.\"
3. If it matches exactly, run: $COMMAND"

SYSTEM_MSG="Ultrareview loop iteration $NEXT_ITERATION (phase: $NEXT_PHASE)"

# Output JSON to block stop and inject prompt
jq -n \
  --arg prompt "$NEXT_PROMPT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
