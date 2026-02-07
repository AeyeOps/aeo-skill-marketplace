---
name: nous-overview
description: |
  Nous self-improving context system overview. Use when the user asks about "nous",
  "learnings", "knowledge extraction", "context injection", "how does memory work",
  "how are learnings captured", or wants to understand the self-improvement pipeline.
---

# Nous: Self-Improving Context System

## Architecture

Nous operates through two Claude Code hooks and a statusline logging integration:

- **SessionStart hook**: Injects recent learnings and knowledge into Claude's context at the beginning of every session. Reads from per-project `.claude/nous/` storage and prepends relevant entries so Claude benefits from prior session insights.
- **Stop hook**: Monitors context window usage percentage (via statusline activity data). When thresholds are met, spawns extraction workers to analyze the session transcript and extract structured JSONL entries.
- **Activity Logger** (`hooks/nous-logger.sh`): A minimal script that reads status JSON from stdin, enriches it with timestamp and hostname, and silently appends to `~/.claude/statusline-activity.jsonl`. Produces no stdout output -- it is designed to run in a pipeline without interfering with any visual statusline.

## Statusline Architecture (Wrapper/Tee Pattern)

Nous does **not** replace the user's statusline. Instead, `/nous:setup` generates a thin wrapper script (`~/.claude/nous-statusline.sh`) that acts as a tee:

```
Claude Code status JSON (stdin)
  │
  ├──→ nous-logger.sh  (appends enriched JSONL to activity log, silent)
  │
  └──→ user's original statusline command  (visual output preserved as-is)
```

This means:
- **Users who already have a statusline** keep their exact visual output. Nous just piggybacks the data stream for logging.
- **Users with no statusline** get silent logging only. They can optionally adopt the bundled `hooks/statusline-example.sh` for a visual status bar.
- **The logger and the visual renderer are fully decoupled.** The logger (`nous-logger.sh`) never writes to stdout. The example statusline (`statusline-example.sh`) never writes to the activity log. The wrapper is the only piece that connects them.

## Data Flow

```
~/.claude/nous-statusline.sh (wrapper, set as statuslineCommand)
  → reads stdin (status JSON from Claude Code)
  → pipes to hooks/nous-logger.sh
      → enriches with meta_ts, meta_host
      → appends to ~/.claude/statusline-activity.jsonl
  → pipes to user's original statusline (if any)
      → renders visual output to stdout
  → Stop hook reads statusline-activity.jsonl
      → if context >10%, spawns `claude --print` extraction workers
      → workers read the session transcript
      → extract JSONL entries to inbox fragments (.claude/nous/{learnings,knowledge}/inbox.jsonl.*)
      → flush_inbox() consolidates fragments into engram.jsonl / cortex.jsonl
      → next SessionStart hook injects recent entries from engram.jsonl / cortex.jsonl
```

## Lenses

Extraction uses two perspectives (lenses), each with its own prompt and output format:

- **Learnings** (behavioral): What future sessions should do differently. Captures workflow improvements, tool usage patterns, error avoidance strategies, and user preferences. Stored in `learnings/engram.jsonl`.
- **Knowledge** (factual): What exists in the project. Captures architecture decisions, file locations, API patterns, configuration details, and discovered facts. Stored in `knowledge/cortex.jsonl`.

Each lens runs as a separate `claude --print` worker process, reading the same transcript but extracting different types of information.

## Per-Project Storage

Each project maintains its own nous state in `.claude/nous/`:

```
.claude/nous/
├── extraction_cursor.json          # Tracks last extracted timestamp to avoid re-processing
├── learnings/
│   ├── inbox.jsonl.*               # Raw extraction fragments (temporary, per-worker)
│   └── engram.jsonl                # Consolidated learnings (injected at session start)
└── knowledge/
    ├── inbox.jsonl.*               # Raw extraction fragments (temporary, per-worker)
    └── cortex.jsonl                # Consolidated knowledge (injected at session start)
```

The `extraction_cursor.json` file prevents duplicate extraction across sessions. Inbox fragments are named with unique suffixes per worker invocation and consolidated during the flush step.

## Context Threshold Behavior

The Stop hook reads the current context window percentage and applies these rules:

| Context % | Action |
|-----------|--------|
| **<10%** | Skip entirely -- session too short to contain useful extractable content |
| **10-70%** | Flush inbox fragments to engram/cortex + fire extraction workers for new content |
| **70-85%** | Flush inbox only -- context too full for safe extraction worker spawning |
| **>=85%** | Flush inbox + block with `/clear` recommendation -- context nearly exhausted |

## Statusline Dependency

The activity logger is **required** for nous to function. It provides the context window percentage that drives all threshold decisions. Without it, the Stop hook cannot determine whether extraction should run.

The logger must be wired into the statusline pipeline because that is how Claude Code exposes status data. Run `/nous:setup` to configure the wrapper automatically. The setup preserves any existing visual statusline -- it only adds silent JSONL logging alongside it.
