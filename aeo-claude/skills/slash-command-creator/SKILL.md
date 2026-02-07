---
name: slash-command-creator
description: Author custom Claude Code slash commands as reusable Markdown prompt templates. Covers frontmatter configuration, argument handling, variable substitution, and workflow automation patterns. Invoke when designing new commands, debugging command syntax, or converting repetitive prompts into reusable shortcuts.
---

# Slash Command Creator

Create effective Claude Code slash commands - reusable prompt templates stored as Markdown files.

## Quick Reference

| Scope | Location | Label in /help |
|-------|----------|----------------|
| Project | `.claude/commands/*.md` | (project) |
| Personal | `~/.claude/commands/*.md` | (user) |

## File Structure

```markdown
---
description: Brief description shown in /help
argument-hint: <required> [optional]
allowed-tools: Bash(git *), Read, Edit
model: claude-sonnet-4-20250514
disable-model-invocation: false
---

Your prompt template here with $ARGUMENTS or $1, $2, etc.
```

## Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | All args as single string | `/cmd foo bar` -> `"foo bar"` |
| `$1`, `$2`... | Positional args | `/cmd foo bar` -> `$1="foo"`, `$2="bar"` |
| `@path/file` | Include file contents | `Review @src/main.py` |
| `` `!command` `` | Execute bash, include output | `` `!git status` `` |

## Frontmatter Fields

| Field | Purpose | Default |
|-------|---------|---------|
| `description` | Shown in /help, enables discoverability | First line of prompt |
| `argument-hint` | Shows in autocomplete | None |
| `allowed-tools` | Restrict tool access | Inherits from conversation |
| `model` | Override model | Inherits from conversation |
| `disable-model-invocation` | Prevent auto-invocation | `false` |

## Creation Process

1. **Identify the workflow** - What repetitive task needs automation?
2. **Choose scope** - Project-specific or personal?
3. **Design the prompt** - Keep it focused on one task
4. **Add variables** - Use `$ARGUMENTS` for flexibility
5. **Set frontmatter** - Add description and hints
6. **Test and iterate** - Refine based on usage

## When to Use Slash Commands vs Skills

**Use slash commands for:**
- Quick, single-file prompts
- Frequent manual invocations
- Simple templates and reminders
- Team workflows in version control

**Use Skills instead for:**
- Multi-file resources (scripts, references, assets)
- Complex workflows with validation
- Capabilities Claude should auto-discover
- Detailed procedural knowledge

## Best Practices

1. **Meaningful names** - `/review-pr` not `/rp`
2. **Clear descriptions** - Help discoverability in /help
3. **Single responsibility** - One task per command
4. **Use argument hints** - Guide users on expected input
5. **Version control** - Check into git for team sharing
6. **Abstract patterns** - Make commands reusable across scenarios

## References

Consult these resources when creating slash commands:

- **[examples.md](references/examples.md)** - Read when you need complete working examples or want to show the user reference implementations. Covers git workflows, code review, documentation, testing, scaffolding, and utilities.

- **[patterns.md](references/patterns.md)** - Read when implementing specific features: variable handling, file inclusion (`@path`), bash execution (`` `!cmd` ``), tool restrictions, multi-step workflows, or output formatting.

- **[template.md](references/template.md)** - Starting template for new commands. Copy and customize the structure.
