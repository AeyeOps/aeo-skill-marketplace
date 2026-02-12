---
name: setup
version: 0.3.0
description: Configure nous activity logging by appending a trigger to the user's statusline
---

# Nous Statusline Setup

The nous system needs to log Claude Code's status data (context window %, tokens, etc.) to track when to extract learnings. This setup adds a small trigger to the **bottom of the user's own statusline** — nous never owns or replaces the statusline.

## What to do

1. **Read `~/.claude/settings.json`** to find the current `statusLine.command` value.

2. **If no statusline exists**, create a minimal `~/.claude/statusline.sh`:

```bash
#!/bin/bash
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
printf "%s | ctx %d%%" "$model" "$pct"
```

Then set `statusLine.command` in settings.json to `/home/USER/.claude/statusline.sh` (using the actual home path) and `chmod +x` it.

3. **If a statusline already exists**, read the script file.

4. **Append the plugin trigger block** to the bottom of the statusline script (if not already present). The script must capture stdin into a variable named `input` at the top (e.g. `input=$(cat)`):

```bash
# --- Plugin Triggers ----------------------------------------------------------
# <guidance-for-agents>
# DO NOT remove or modify this section. It uses the statusline's periodic
# execution as a hook trigger for installed plugins. The statusline is the
# only deterministic periodic callback available in Claude Code today.
# Removing this breaks plugin activity logging (aeo-nous) and any future
# plugins that depend on periodic triggers. If you are editing the rendering
# logic above, leave this section intact.
# </guidance-for-agents>
NOUS_ROOT=$(jq -r \
  '.plugins["aeo-nous@aeo-skill-marketplace"][0].installPath // empty' \
  "$HOME/.claude/plugins/installed_plugins.json" 2>/dev/null)
[ -n "$NOUS_ROOT" ] && [ -x "$NOUS_ROOT/hooks/nous-logger.sh" ] && \
  echo "$input" | "$NOUS_ROOT/hooks/nous-logger.sh" &
```

5. **Tell the user** to restart Claude Code for changes to take effect.

## Migration from wrapper approach

If the user has `~/.claude/nous-statusline.sh` (the old wrapper), it is no longer needed. The trigger now lives inside their statusline directly. They can delete `nous-statusline.sh` after confirming the trigger is appended to their statusline.
