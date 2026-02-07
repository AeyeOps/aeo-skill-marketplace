#!/bin/bash

# Ultrareview Loop Setup Script
# Creates state file and session token for ultrareview loop

set -euo pipefail

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
  # No project root found, use current directory
  echo "$PWD"
}

PROJECT_ROOT=$(find_project_root)

# Parse arguments
FOCUS_PARTS=()
MAX_ITERATIONS=10

# Parse options and positional arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      cat << 'HELP_EOF'
Ultrareview Loop - Automated validation cycle

USAGE:
  /ultrareview-loop [FOCUS...] [OPTIONS]

ARGUMENTS:
  FOCUS...    Initial focus area for ultrareview (passed to first /ultrareview)

OPTIONS:
  --max-iterations <n>    Maximum iterations before auto-stop (default: 10)
  -h, --help              Show this help message

DESCRIPTION:
  Starts an automated ultrareview validation loop. The stop hook alternates
  between /ultrareview and /ultrareview-fix until no actionable findings remain.

EXAMPLES:
  /ultrareview-loop "the API changes"
  /ultrareview-loop --max-iterations 15 "authentication flow"
  /ultrareview-loop  (validates entire preceding context)

STOPPING:
  - Automatically when no actionable findings remain
  - Automatically when --max-iterations is reached
  - Manually: ask "stop the ultrareview loop" (Claude deletes state file)
  - Manually: rm .claude/ultrareview-loop-*.local.md
HELP_EOF
      exit 0
      ;;
    --max-iterations)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --max-iterations requires a number argument" >&2
        exit 1
      fi
      if ! [[ "$2" =~ ^[0-9]+$ ]]; then
        echo "Error: --max-iterations must be a positive integer, got: $2" >&2
        exit 1
      fi
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    *)
      # Non-option argument - collect as focus parts
      FOCUS_PARTS+=("$1")
      shift
      ;;
  esac
done

# Join focus parts with spaces
INITIAL_FOCUS="${FOCUS_PARTS[*]:-}"

# Generate unique session token (full UUID for distinctiveness)
TOKEN="ulr-$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen 2>/dev/null || od -x /dev/urandom | head -1 | awk '{OFS="-"; print $2$3,$4,$5,$6,$7$8$9}')"

# Create state file with YAML frontmatter
mkdir -p "$PROJECT_ROOT/.claude"

# Quote initial_focus for YAML if it contains special chars
if [[ -n "$INITIAL_FOCUS" ]]; then
  INITIAL_FOCUS_YAML="\"$INITIAL_FOCUS\""
else
  INITIAL_FOCUS_YAML="null"
fi

# Use token in filename to avoid collisions between sessions
STATE_FILE="$PROJECT_ROOT/.claude/ultrareview-loop-${TOKEN}.local.md"

cat > "$STATE_FILE" <<EOF
---
token: "$TOKEN"
session_id: null
iteration: 1
max_iterations: $MAX_ITERATIONS
phase: review
initial_focus: $INITIAL_FOCUS_YAML
started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---
EOF

# Output setup confirmation
cat <<EOF
Ultrareview loop activated!

Token: $TOKEN
Iteration: 1
Max iterations: $MAX_ITERATIONS
Phase: review
Focus: $(if [[ -n "$INITIAL_FOCUS" ]]; then echo "$INITIAL_FOCUS"; else echo "(entire context)"; fi)

The loop will cycle: ultrareview -> ultrareview-fix -> ultrareview -> ...
until no actionable findings remain.

To stop manually: ask "stop the ultrareview loop"
State file: $STATE_FILE
EOF
