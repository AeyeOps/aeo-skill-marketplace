# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Claude Code plugin marketplace** - a collection of 16 plugins containing reusable skills, agents, commands, and hooks for AI-assisted development. It is NOT a codebase with build/test commands; it's documentation and configuration files.

## Plugin Structure

Each plugin follows this layout:
```
aeo-{name}/
├── .claude-plugin/plugin.json    # Plugin metadata (name, version, description)
├── skills/{topic}/SKILL.md       # Domain knowledge loaded contextually
├── agents/{role}.md              # Autonomous workers with Task tool
├── commands/{action}.md          # Slash commands (/command-name)
└── hooks/{name}.json             # Event automation
```

The root `.claude-plugin/marketplace.json` indexes all plugins.

## Component Formats

### Agent frontmatter (required fields)
```yaml
---
name: agent-name
version: 0.1.0
description: Use this agent when... (include trigger examples)
model: opus|sonnet|haiku
color: blue|cyan|green|yellow|magenta|red|purple
tools: Read, Write, Edit, Grep, Glob  # or [Read, Write, ...] array syntax
---
```

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
Skills use `@relative/path.md` syntax to reference additional files.

### Hooks (JSON)
```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "type": "command", "command": "...", "blocking": true}],
    "PostToolUse": [...],
    "UserPromptSubmit": [...],
    "Stop": [...],
    "SubagentStop": [...],
    "PreCommit": [...],
    "PreDeploy": [...]
  }
}
```

## Key Plugins

| Plugin | Purpose | Key Commands |
|--------|---------|--------------|
| **aeo-epcc-workflow** | Explore-Plan-Code-Commit methodology | `/epcc-explore`, `/epcc-plan`, `/epcc-code`, `/epcc-commit`, `/prd`, `/trd` |
| **aeo-architecture** | System design, C4 diagrams, ADRs | `/design-architecture`, `/code-review`, `/refactor-code` |
| **aeo-tdd-workflow** | Test-driven development | `/tdd-feature`, `/tdd-bugfix` |
| **aeo-testing** | Quality gates, test generation | `/generate-tests` |
| **aeo-security** | Vulnerability scanning | `/security-scan`, `/permission-audit` |
| **aeo-n8n** | n8n workflow automation skills | (contextual skills) |

## Validation

```bash
# Validate a single plugin
claude plugin validate ./aeo-architecture

# Validate all plugins
for dir in aeo-*/; do claude plugin validate "./$dir"; done
```

## Loading Plugins

```bash
# Development - load directly
claude --plugin-dir ./aeo-architecture

# Marketplace install
/plugin marketplace add AeyeOps/aeo-skill-marketplace
/plugin install aeo-architecture@aeo-skill-marketplace
```

## Contributing a Plugin

1. Create `aeo-{name}/.claude-plugin/plugin.json`
2. Add components (agents, skills, commands, hooks)
3. Update `.claude-plugin/marketplace.json` to include the plugin
4. Validate with `claude plugin validate ./aeo-{name}`

## Cross-References

Skills and commands can reference other files with:
- `@../path/to/file.md` - Relative reference (loaded into context)
- `[link text](references/file.md)` - Markdown link for progressive disclosure
