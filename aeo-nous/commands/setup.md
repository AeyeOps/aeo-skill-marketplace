---
name: setup
version: 0.1.0
description: Configure the statusline dependency for nous context tracking
---

# Nous Statusline Setup

The nous system requires the **statusline** to track context window usage percentage. The statusline command cannot be set by a plugin hook -- it must be configured directly in the user's `settings.json`.

## Instructions for the user

1. **The statusline script** lives inside the installed plugin at:
   ```
   <plugin-install-path>/hooks/statusline.sh
   ```
   Because plugins are installed into a cache directory that changes with each version, the exact path will vary.

2. **Option A: Use the statusline-setup Task agent** (recommended if available)

   If the `statusline-setup` Task agent is available in your environment, invoke it to automatically locate the installed plugin path and configure the statusline for you.

3. **Option B: Manual configuration**

   Find the installed plugin path by looking in your Claude cache directory for the `aeo-nous` plugin, then add the following to `~/.claude/settings.json`:

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "<path-to-installed-plugin>/hooks/statusline.sh"
     }
   }
   ```

   Replace `<path-to-installed-plugin>` with the actual resolved path to the `aeo-nous` plugin installation directory.

4. **Restart Claude Code** for the statusline to take effect.

## What the statusline provides

Once configured, the statusline displays:
- Context window usage percentage (critical for nous extraction thresholds)
- Git branch and status information
- Active model identifier

The nous Stop hook reads the context percentage from `~/.claude/statusline-activity.jsonl` (written by the statusline script) to decide whether to trigger extraction workers.
