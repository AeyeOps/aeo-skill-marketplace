---
name: opus-prompting
description: |
  Tune prompts specifically for Claude Opus 4.5's literal instruction-following behavior.
  Covers system prompt optimization, migration from earlier Claude versions, debugging
  unexpected outputs, and agentic workflow patterns. Apply when crafting Opus prompts,
  adapting 3.x/4.0 prompts, or designing autonomous agent instructions.
---

# Opus 4.5 Prompting

Opus 4.5 behaves differently from earlier Claude models—more literal, more responsive to system prompts. This skill provides patterns for optimizing prompts accordingly.

## Key Behavioral Changes

| Behavior | Implication |
|----------|-------------|
| **Literal instruction following** | Be explicit about desired behaviors |
| **Sensitive to "think" word** | Use `consider`, `evaluate`, `reflect` instead |
| **Highly responsive to system prompt** | Dial back aggressive language |
| **Tool trigger sensitivity** | Replace `MUST use` with `Use when...` |
| **Context awareness** | Model tracks remaining token budget |

## Quick Migration Checklist

When upgrading prompts from Claude 3.7/4.0:

1. Remove aggressive language (`CRITICAL`, `MUST`, `NEVER`, `ALWAYS`)
2. Replace `think step by step` with `consider` or `evaluate`
3. Add context/motivation ("because..." explanations)
4. Match prompt formatting to desired output style
5. Remove over-specified examples (trust the model)
6. Use gentler tool invocation language
7. Add XML tags for agent workflows (`<current-state>`, `<blocked>`, `<workflow>`)

## Reference Files

| File | Use When |
|------|----------|
| [patterns.md](references/patterns.md) | Optimizing any prompt—comprehensive transformation rules and examples |
| [agentic-patterns.md](references/agentic-patterns.md) | Building agents, MCPs, long-horizon workflows with Opus 4.5 |

## Utility Script

The `scripts/analyze-prompt.py` script analyzes prompts for deprecated patterns:

```bash
echo "Your prompt text" | python3 scripts/analyze-prompt.py
```

Configure thresholds in `scripts/config.json`:
- `min_words`: Minimum words to trigger analysis (default: 1)
- `enabled`: Enable/disable the analyzer (default: true)

## Pattern Categories

The [patterns.md](references/patterns.md) reference covers:

1. **Aggressive language** — Soften `MUST`, `NEVER`, `CRITICAL`
2. **Think variants** — Replace when extended thinking disabled
3. **Tool invocation** — Prevent over-triggering
4. **Formatting** — Match prompt style to output style
5. **Context/motivation** — Add "because..." explanations
6. **Over-specification** — Trust the model more
7. **Verbosity** — Optimize for conciseness
8. **XML structure** — Use semantic tags for agent workflows

## Agentic Best Practices

The [agentic-patterns.md](references/agentic-patterns.md) reference covers:

1. **Context management** — Progress summaries at 20% remaining
2. **Sub-agent delegation** — Preserve main context
3. **Tool design** — Avoid over-triggering in descriptions
4. **State tracking** — JSON for structured, text for notes
5. **Long-horizon workflows** — Incremental progress patterns
6. **Parallel execution** — When to parallelize vs sequence
7. **Error handling** — Fail fast, document blockers
