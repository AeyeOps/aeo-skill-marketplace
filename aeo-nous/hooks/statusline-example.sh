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
# === EXAMPLE MINIMAL STATUSLINE ===
#
# A bare-bones ~/.claude/statusline.sh with nous integration:
#
#   #!/bin/bash
#   input=$(cat)
#   model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
#   pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
#   printf "%s | ctx %d%%" "$model" "$pct"
#
#   # (paste the plugin triggers block from above here)
