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

This appends a small **trigger block** to the bottom of your `~/.claude/statusline.sh` that pipes status JSON to the nous activity logger in the background. Your statusline rendering is untouched — nous just piggybacks on the periodic tick.

If you have no statusline yet, setup creates a minimal one for you.

### Manual configuration

If you prefer not to use `/nous:setup`, add the trigger block from `hooks/statusline-example.sh` (a reference doc) to the bottom of your statusline script. The key requirement is that `hooks/nous-logger.sh` receives Claude Code's status JSON on stdin each tick.

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

### Integration Reference (`hooks/statusline-example.sh`)
A commented reference file (not executable) showing how to add the nous trigger to any user-owned statusline. See the file for the exact block to paste.

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

## Migration

If you have `~/.claude/nous-statusline.sh` (the old wrapper approach), it is no longer needed. Run `/nous:setup` to append the trigger directly to your statusline, then delete the old wrapper.

## License

MIT
