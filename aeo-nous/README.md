# aeo-nous

Self-improving context system for Claude Code.

## What it does

- **SessionStart**: Injects recent learnings and knowledge into Claude's context
- **Stop**: Monitors context usage, extracts new learnings/knowledge when thresholds are met
- **Activity Logger**: Silently logs status data to JSONL for threshold tracking (non-intrusive)

## Installation

```bash
# If aeo-skill-marketplace is already added
/plugin install aeo-nous@aeo-skill-marketplace
```

## Setup

After installation, configure the statusline logging:
```bash
/nous:setup
```

This generates a **wrapper script** (`~/.claude/nous-statusline.sh`) that:
1. Passes status JSON to the nous activity logger (silent JSONL append)
2. Passes the same data to your **existing statusline** (if you had one)

Your current visual statusline is preserved. The only addition is silent logging.

### No existing statusline?

The wrapper will just log with no visual output. If you want a visual status bar, the plugin bundles an example at `hooks/statusline-example.sh` that shows context %, git info, and model name.

### Manual configuration

If you prefer not to use `/nous:setup`, you can wire things up manually. The key requirement is that `hooks/nous-logger.sh` receives Claude Code's status JSON on stdin each tick. How you arrange that is up to you.

## How It Works

### Session Start (Context Injection)
Reads `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and recent entries from:
- `.claude/nous/learnings/engram.jsonl` (behavioral learnings)
- `.claude/nous/knowledge/cortex.jsonl` (project knowledge)

### Stop Hook (Extraction)
Based on context window usage (from statusline activity log):
- **<10%**: Skip
- **10-70%**: Flush inbox + fire extraction workers
- **70-85%**: Flush inbox only
- **>=85%**: Flush + block with /clear recommendation

Extraction workers run `claude --print` to analyze the session transcript and output JSONL entries.

### Activity Logger (`hooks/nous-logger.sh`)
A minimal script that reads status JSON from stdin, enriches it with `meta_ts` and `meta_host`, and appends to `~/.claude/statusline-activity.jsonl`. Produces no stdout -- safe to use in a pipeline. Handles log rotation automatically (keeps last 500 lines when file exceeds 1000).

### Example Statusline (`hooks/statusline-example.sh`)
An optional visual statusline that renders a compact terminal bar with:
- Context window usage percentage with color-coded progress bar
- Git branch and working tree status
- Lines added/removed
- Active model identifier

This is provided as a convenience. You can use any statusline you like (or none at all).

### Lens System
Two extraction lenses:
- **Learnings**: Behavioral deltas - what future sessions should do differently
- **Knowledge**: Project facts - architecture, patterns, discoveries

## Data Storage

Per-project in `.claude/nous/`:
```
.claude/nous/
├── extraction_cursor.json          # Last extracted timestamp
├── learnings/
│   ├── inbox.jsonl.*               # Raw extraction fragments
│   └── engram.jsonl                # Flushed learnings
└── knowledge/
    ├── inbox.jsonl.*               # Raw extraction fragments
    └── cortex.jsonl                # Flushed knowledge
```

## Migration from Manual Hooks

If you previously had nous configured as hooks in `~/.claude/settings.json`, remove the old SessionStart and Stop entries pointing to `aeo_learn_and_compact.py` to avoid double-firing.

If your statuslineCommand previously pointed directly to the plugin's `hooks/statusline.sh`, re-run `/nous:setup` to switch to the new wrapper approach. The old `statusline.sh` has been split into `nous-logger.sh` (logging) and `statusline-example.sh` (visual rendering).

## License

MIT
