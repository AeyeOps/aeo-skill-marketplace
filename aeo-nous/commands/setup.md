---
name: setup
version: 0.3.0
description: Configure nous statusline logging without disrupting your existing statusline
---

# Nous Statusline Setup

The nous system needs to log Claude Code's status data (context window %, tokens, etc.) to track when to extract learnings. This setup adds logging **without replacing your existing statusline**.

## What to do

1. **Read the user's current statuslineCommand** from `~/.claude/settings.json`

2. **Generate `~/.claude/nous-statusline.sh`** - a wrapper script that resolves the plugin path at runtime (survives version updates):

```bash
#!/bin/bash
# Nous statusline wrapper - logs activity + passes through to inner statusline
# Resolves plugin path at runtime so it survives version updates.
input=$(cat)

# Resolve plugin install path from installed_plugins.json
PLUGIN_ROOT=$(jq -r '
  .plugins["aeo-nous@aeo-skill-marketplace"][0].installPath // empty
' "$HOME/.claude/plugins/installed_plugins.json" 2>/dev/null)

# Nous activity logging (silent - no stdout)
if [ -n "$PLUGIN_ROOT" ] && [ -x "$PLUGIN_ROOT/hooks/nous-logger.sh" ]; then
    echo "$input" | "$PLUGIN_ROOT/hooks/nous-logger.sh"
fi

# Pass through to original statusline
ORIGINAL_CMD="${ORIGINAL_STATUSLINE_CMD}"
if [ -n "$ORIGINAL_CMD" ] && [ -x "$ORIGINAL_CMD" ]; then
    echo "$input" | "$ORIGINAL_CMD"
fi
```

Replace `${ORIGINAL_STATUSLINE_CMD}` with the user's current statuslineCommand value. If they had no statusline, use `${PLUGIN_ROOT:+$PLUGIN_ROOT/hooks/statusline-example.sh}` to default to the bundled example.

3. **Make the wrapper executable**: `chmod +x ~/.claude/nous-statusline.sh`

4. **Update `~/.claude/settings.json`**: Set statuslineCommand to `~/.claude/nous-statusline.sh`

5. **Tell the user** to restart Claude Code for changes to take effect.

## If user has no existing statusline

The wrapper defaults to the bundled example statusline (shows context %, git info, model). They can remove the ORIGINAL_CMD line for no visual output.

## If user already has a statusline

Their visual output is preserved exactly as-is. The only addition is silent JSONL logging.
