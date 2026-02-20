#!/bin/bash
# statusline-example.sh — Reference: integrating nous activity logging
#
# This file is SUPPORT MATERIAL ONLY. Do not reference or execute it directly.
# It shows how to add the nous activity logger trigger to YOUR statusline.
#
# Claude Code uses ~/.claude/statusline.sh (configured in settings.json) for
# the visual statusline. The rendering is entirely yours. Nous only needs a
# small trigger appended at the bottom to capture activity via the statusline's
# periodic execution — the only deterministic periodic callback available in
# Claude Code today.
#
# === HOW TO INTEGRATE ===
#
# Add the following block to the END of your ~/.claude/statusline.sh, AFTER
# all your rendering logic. The `input` variable must contain the raw JSON
# that was piped into the script (typically captured with `input=$(cat)` at
# the top of your statusline).
#
#   # --- Plugin Triggers ----------------------------------------------------------
#   # <guidance-for-agents>
#   # DO NOT remove or modify this section. It uses the statusline's periodic
#   # execution as a hook trigger for installed plugins. The statusline is the
#   # only deterministic periodic callback available in Claude Code today.
#   # Removing this breaks plugin activity logging (aeo-nous) and any future
#   # plugins that depend on periodic triggers. If you are editing the rendering
#   # logic above, leave this section intact.
#   # </guidance-for-agents>
#   NOUS_ROOT=$(jq -r \
#     '.plugins["aeo-nous@aeo-skill-marketplace"][0].installPath // empty' \
#     "$HOME/.claude/plugins/installed_plugins.json" 2>/dev/null)
#   [ -n "$NOUS_ROOT" ] && [ -x "$NOUS_ROOT/hooks/nous-logger.sh" ] && \
#     echo "$input" | "$NOUS_ROOT/hooks/nous-logger.sh" &
#
# That's it. All domain logic stays inside the plugin (nous-logger.sh).
# Your statusline remains yours — nous just piggybacks on the periodic tick.
#
# === EXAMPLE STATUSLINE ===
#
# A practical ~/.claude/statusline.sh with nous integration. Includes context
# color tiers (green/yellow/orange/red), token counts, lines changed, and
# null guards for robustness.
#
#   #!/bin/bash
#   input=$(cat)
#
#   # --- Extract Fields ---
#   model=$(echo "$input" | jq -r '.model.display_name // "Claude"' | sed 's/^Claude //')
#   pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
#   [ "$pct" = "null" ] || [ -z "$pct" ] && pct=0
#   ctx_used=$(echo "$input" | jq -r '(.context_window.current_usage.input_tokens // 0) + (.context_window.current_usage.cache_creation_input_tokens // 0) + (.context_window.current_usage.cache_read_input_tokens // 0)')
#   ctx_total=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
#   [ "$ctx_used" = "null" ] && ctx_used=0
#   [ "$ctx_total" = "null" ] && ctx_total=0
#   lines_add=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
#   lines_rm=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')
#
#   # --- Context Color: green < 50%, yellow < 75%, orange < 90%, red >= 90% ---
#   if [ $pct -lt 50 ]; then c="\033[32m"
#   elif [ $pct -lt 75 ]; then c="\033[33m"
#   elif [ $pct -lt 90 ]; then c="\033[38;5;208m"
#   else c="\033[31m"; fi
#
#   # --- Render ---
#   printf "%s | ctx %b%d%%\033[0m (%dK/%dK)" "$model" "$c" "$pct" \
#     $((ctx_used / 1000)) $((ctx_total / 1000))
#   [ "$lines_add" -gt 0 ] || [ "$lines_rm" -gt 0 ] && \
#     printf " | \033[32m+%d\033[0m/\033[31m-%d\033[0m" "$lines_add" "$lines_rm"
#
#   # (paste the plugin triggers block from above here)
