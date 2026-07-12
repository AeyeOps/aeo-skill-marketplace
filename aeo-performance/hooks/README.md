# Performance - Monitoring Hooks

Lightweight per-tool usage logging for Claude Code operations.

## What exists

### performance_logger.py

A `PreToolUse` hook that appends one log entry per matching tool invocation to `.claude/performance.json` in the current working directory. For each call it records:

- `timestamp`, `session_id`, `hook_event`, `tool_name`
- `Read`: `file_path`, plus `file_size` when the file exists
- `Bash`: `command_length`
- `Edit` / `Write`: `file_path` and `content_length`

The log is capped at the most recent 1000 entries. The script swallows all errors and always exits 0, so it never blocks or fails a tool call.

## Wiring

`hooks.json` wires the script on `PreToolUse` for the tools it understands:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Bash|Edit|Write",
        "hooks": [
          { "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/performance_logger.py || true", "timeout": 5000 }
        ]
      }
    ]
  }
}
```

`|| true` keeps the hook advisory so it can never block a tool call, even though the script already self-guards by exiting 0 on any error.

## Notes

- Requires `python3` on `PATH`.
- Output lands in `.claude/performance.json` under the current working directory; delete the file to reset the log.
- Analysis of the collected data (reporting, cost estimation, bottleneck detection) is left to your own tooling — no reporting scripts ship with this plugin.
