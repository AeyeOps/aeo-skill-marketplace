# EPCC Workflow - Auto Recovery Hooks

Automated environment self-healing hooks for the Explore-Plan-Code-Commit workflow.

**Hooks are disabled by default** (`hooks.json` ships with an empty `hooks: {}`). The configuration below re-installs project dependencies, restores executable bits on shell scripts, and clears stale Python bytecode caches as work proceeds. Every command is inline and advisory (`|| true`) — no external script ships with, or is required by, this plugin. Copy the entries you want into the `hooks` object in `hooks.json` and test locally before relying on them.

## Reference Configuration

To enable, copy desired entries into the `hooks` object in `hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "[ -f requirements.txt ] && pip install -q -r requirements.txt || true", "timeout": 60000 },
          { "type": "command", "command": "[ -f package.json ] && npm install --silent || true", "timeout": 120000 }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "find . -type f -name '*.sh' -not -path './.git/*' -exec chmod +x {} + || true", "timeout": 10000 },
          { "type": "command", "command": "find . -type d -name '__pycache__' -not -path './.git/*' -exec rm -rf {} + || true", "timeout": 10000 }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "find . -type f -name '*.sh' -not -path './.git/*' -exec chmod +x {} + || true", "timeout": 10000 }
        ]
      }
    ]
  }
}
```

Each hook is self-contained. The `PostToolUse` entries re-install Python dependencies from `requirements.txt` and Node dependencies from `package.json` when those manifests are present. The `Stop` and `SubagentStop` entries restore executable permissions on `.sh` files and remove stale `__pycache__` directories, skipping `.git/` in both cases.

## Event Mapping Caveats

| Event | Behavior | Notes |
|-------|----------|-------|
| `PostToolUse` (matcher `Bash`) | Dependency recovery | **Caveat:** Fires after every Bash tool invocation, not just dependency changes. `pip install` / `npm install` runs whenever a manifest is present — narrow the matcher or add a guard if that overhead is unwanted. |
| `Stop` | Environment cleanup | Runs when the main agent finishes responding. Restores `.sh` executable bits and clears `__pycache__`. |
| `SubagentStop` | Environment cleanup | Runs when a subagent finishes. Restores `.sh` executable bits. |

## Blocking Behavior Warning

A hook signals a blocking error by exiting with code 2 (the tool call is prevented and Claude sees the output to self-correct); other non-zero exits are non-blocking and only surface in verbose mode. Appending `|| true` forces a zero exit, so a failed install or cleanup stays advisory and never blocks your work — which is why every command above uses it. Drop `|| true` only where you want a failure to halt the operation.

## Notes
- Every entry above is inline and copy-pasteable; no `auto_recover.sh` or other external script ships with this plugin.
- The commands assume a POSIX shell with `pip`, `npm`, `find`, and `chmod` available on `PATH`.
- Narrow the `PostToolUse` matcher or add a guard if you only want dependency recovery after specific commands.
- Test any enabled hook locally before relying on it, and monitor for recovery steps that repeatedly fail.
