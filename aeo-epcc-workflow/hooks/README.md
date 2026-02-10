# EPCC Workflow - Auto Recovery Hooks

Automated error recovery and self-healing hooks for the Explore-Plan-Code-Commit workflow.

## Event Mapping Caveats

| Original Event | New Mapping | Notes |
|---------------|-------------|-------|
| `PostToolUse` | `PostToolUse` (kept) | Already compliant structure. |
| `Stop` | `Stop` (kept) | Wrapped flat array in correct `matcher`/`hooks` structure. |
| `SubagentStop` | `SubagentStop` (kept) | Wrapped flat array in correct `matcher`/`hooks` structure. |

## Recovery Scripts

### auto_recover.sh
General recovery script that:
- Installs Python dependencies from `requirements.txt` if present
- Installs Node.js dependencies from `package.json` if present
- Resets file permissions on `.sh` files to executable
- Clears Python `__pycache__` directories

## Blocking Behavior Warning

Claude Code's hooks spec does not support a `blocking` field — **all hooks block by default** if the command exits non-zero. Recovery hooks that should be advisory-only must append `|| true` to their commands to prevent failures from blocking operations.

## Notes
- Test recovery scripts thoroughly before deployment
- Monitor error.log for patterns that need addressing
