# aeo-nous

Self-improving context system for Claude Code.

## What it does

- **SessionStart**: Injects recent learnings and knowledge into Claude's context
- **Stop**: Monitors context usage, extracts new learnings/knowledge when thresholds are met
- **Statusline**: Provides terminal status bar with context %, git info, and model display

## Installation

```bash
# If aeo-skill-marketplace is already added
/plugin install aeo-nous@aeo-skill-marketplace
```

## Setup

After installation, configure the statusline dependency:
```bash
/nous:setup
```

Or manually add to `~/.claude/settings.json`:
```json
{
  "statusLine": {
    "type": "command",
    "command": "<plugin-install-path>/hooks/statusline.sh"
  }
}
```

## How It Works

### Session Start (Context Injection)
Reads `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and recent entries from:
- `.claude/nous/learnings/engram.jsonl` (behavioral learnings)
- `.claude/nous/knowledge/cortex.jsonl` (project knowledge)

### Stop Hook (Extraction)
Based on context window usage (from statusline):
- **<10%**: Skip
- **10-70%**: Flush inbox + fire extraction workers
- **70-85%**: Flush inbox only
- **>=85%**: Flush + block with /clear recommendation

Extraction workers run `claude --print` to analyze the session transcript and output JSONL entries.

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

## License

MIT
