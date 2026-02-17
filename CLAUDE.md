# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A **Claude Code plugin marketplace** — 17 plugins containing reusable skills, agents, commands, and hooks for AI-assisted development. This is NOT a runnable codebase; it's documentation and configuration files with no build/test/lint commands.

The root `.claude-plugin/marketplace.json` indexes all plugins. Each plugin lives in `aeo-{name}/` with a `.claude-plugin/plugin.json`.

## Validation

```bash
claude plugin validate ./aeo-architecture           # single plugin
for dir in aeo-*/; do claude plugin validate "./$dir"; done  # all plugins
```

## Loading Plugins

```bash
claude --plugin-dir ./aeo-architecture               # development
/plugin marketplace add AeyeOps/aeo-skill-marketplace  # marketplace install
/plugin install aeo-architecture@aeo-skill-marketplace
```

## Component Formats

### Agent frontmatter
```yaml
---
name: agent-name
description: Use this agent when... (include trigger examples)
model: opus|sonnet|haiku
tools: Read, Write, Edit, Grep, Glob
---
```
Standard fields: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`. This marketplace also uses non-standard `version` and `color` fields in agents.

### Command frontmatter
```yaml
---
name: command-name
version: 0.1.0
description: What this command does
argument-hint: "[optional-arg]"
---
```
Use `$ARGUMENTS` in command body to reference user input.

### Skill frontmatter
```yaml
---
name: skill-name
description: |
  Multi-line description with activation triggers. Loaded when context matches.
---
```

### Hooks (JSON)
```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "..."}]}],
    "PostToolUse": [...],
    "UserPromptSubmit": [...],
    "Stop": [...],
    "SubagentStop": [...],
    "SubagentStart": [...],
    "SessionStart": [...],
    "SessionEnd": [...],
    "PreCompact": [...],
    "Notification": [...],
    "PermissionRequest": [...],
    "PostToolUseFailure": [...],
    "TeammateIdle": [...],
    "TaskCompleted": [...]
  }
}
```

## Architecture — Cross-Cutting Patterns

### Agent model tiering (v0.3.0 convention)
- `opus` — complex reasoning tasks (architect, system-designer, performance-optimizer)
- `haiku` — read-only analysis (code-archaeologist)
- `sonnet` — everything else

### Invalid tool names to avoid
`MultiEdit` → use `Edit`. `LS` → use `Glob`. `TodoWrite` → use `TaskCreate`/`TaskUpdate`. Tools are always comma-separated strings, not arrays.

### Cross-plugin agent delegation
Commands invoke agents from other plugins via `@agent-name` references in their body. For example, `/security-scan` delegates to `@security-reviewer`, `@system-designer` (aeo-architecture), and `@qa-engineer` (aeo-testing). Six plugins declare companion requirements in their `plugin.json` description string (not a structured field): e.g., `"Requires companion plugins: aeo-testing, aeo-performance"`.

### @reference/ import mechanism
Skills and commands use `@reference/filename.md` inline directives in their body to load supporting files into context. Paths are always relative to the current file's directory. Cross-plugin `@../` references are broken — stay within the plugin's directory tree.

### Hook exit codes
- Exit 0: allow/pass
- Exit 2: blocking error — tool use is prevented and Claude sees stdout/stderr to self-correct (used by `use_uv.py`, `command_security_check.sh`)
- Other non-zero: non-blocking error — stderr shown in verbose mode but execution continues
- Append `|| true` to a hook command to make it advisory (never blocks)
- Stop hooks output JSON: `{"decision":"block","reason":"..."}`

### `${CLAUDE_PLUGIN_ROOT}` variable
Used in hook commands and MCP server configs to reference scripts relative to the plugin install location. Does NOT work in command markdown files. The old `$CLAUDE_PROJECT_DIR` was replaced in v0.2.0.

### `.local.md` ephemeral state convention
`*.local.md` files are gitignored and used for per-session state. The ultrareview-loop stores iteration state in `.claude/ultrareview-loop-{TOKEN}.local.md` with YAML frontmatter. Never commit these.

### Inline bash execution in skills
The `` ```! `` fence syntax (backticks followed by `!`) causes Claude Code to execute the command inline when the skill is invoked. Used by ultrareview-loop's setup script. Note: this feature has known parser bugs with `!` inside markdown inline code backticks.

### `allowed-tools` in skill frontmatter
Skills that function as bounded commands (ultrareview, ultraplan, ultrareview-loop) use `allowed-tools` and `model` fields in frontmatter to constrain execution — regular passive knowledge skills do not.

### Hooks with disabled-by-default pattern
Plugins with aggressive hooks document reference configurations in `hooks/README.md` while keeping `hooks.json` with an empty `"hooks": {}` object. See aeo-deployment, aeo-agile-tools.

## Key Subsystems

### Nous (aeo-nous) — self-improving memory
Most complex plugin. Three-script hook system:
- `nous-stop-guard.sh` (sync): blocks session exit when context >65%, prompts `/clear`
- `nous.py` (async): on SessionStart injects recent learnings/knowledge from JSONL files; on Stop extracts new learnings via `claude --print` subprocesses (strips `CLAUDECODE` env var to prevent hook recursion)
- `nous-logger.sh`: enriches statusline data, appends to `~/.claude/statusline-activity.jsonl` with auto-rotation at 1000 lines

Storage: per-project `.claude/nous/` — `learnings/engram.jsonl`, `knowledge/cortex.jsonl`, `extraction_cursor.json`.

### Ultrareview-loop (aeo-claude)
Automated review/fix cycle using Stop hook. State tracked in `.local.md` files with session-gated tokens to prevent cross-session interference. Reads `<ultrareview_summary>` blocks from assistant output to determine PASS/NEEDS_ACTION status.

### EPCC workflow (aeo-epcc-workflow)
Each phase writes artifact files to project root: `EPCC_EXPLORE.md`, `EPCC_PLAN.md`, `EPCC_CODE.md`, `EPCC_COMMIT.md`. Commands were refactored from 600-1400 lines each to <400 by extracting 16 reference files in `commands/reference/`.

## Contributing a Plugin

1. Create `aeo-{name}/.claude-plugin/plugin.json` (fields: name, version, description, author, license)
2. Add components (agents, skills, commands, hooks)
3. Update `.claude-plugin/marketplace.json` with name, description, category, source, tags
4. Validate with `claude plugin validate ./aeo-{name}`

## Changelog

Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Current version: v0.4.4. See `CHANGELOG.md` for full history.
