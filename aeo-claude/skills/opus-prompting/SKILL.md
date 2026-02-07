---
name: opus-prompting
description: |
  Tune prompts for Claude Opus 4.6's adaptive thinking, 1M context window, and natural
  instruction-following. Covers migration from 4.5/earlier, agent team patterns, and
  agentic workflow design. Apply when crafting Opus prompts, adapting existing prompts,
  or designing autonomous agent instructions.
---

# Opus 4.6 Prompting

Opus 4.6 builds on the 4.5 prompting philosophy with key additions: adaptive thinking (4 effort levels), 1M token context (beta), 128K output, agent teams, and server-side compaction. The core principle remains—natural language over directives.

## What Changed from 4.5 to 4.6

| Feature | Opus 4.5 | Opus 4.6 |
|---------|----------|----------|
| **Thinking** | Extended thinking (binary on/off + budget_tokens) | Adaptive thinking (low/medium/high/max) |
| **Context** | 200K tokens | 1M tokens (beta), context rot eliminated |
| **Output** | 64K tokens | 128K tokens |
| **Agent architecture** | Single agent, sub-agent delegation | Agent teams (parallel coordination) |
| **Compaction** | Client-side | Server-side compaction API (beta) |
| **Prefilling** | Supported | Disabled (400 error), use structured outputs |
| **"Think" sensitivity** | Highly sensitive | Reduced (adaptive thinking handles calibration) |

## Key Behavioral Patterns

| Behavior | Implication |
|----------|-------------|
| **Literal instruction following** | Be explicit about desired behaviors |
| **Adaptive thinking** | Let the model calibrate reasoning depth; specify effort level only when needed |
| **Highly responsive to system prompt** | Use natural language, not directives |
| **Tool trigger sensitivity** | Replace `MUST use` with `Use when...` |
| **1M context awareness** | Context rot eliminated; long conversations maintain quality |

## Quick Migration Checklist

When upgrading prompts from 4.5 or earlier:

1. Remove aggressive language (`CRITICAL`, `MUST`, `NEVER`, `ALWAYS`)
2. Replace `budget_tokens` extended thinking with adaptive thinking effort levels
3. Replace assistant prefilling with `output_config.format` or system prompt instructions
4. Add context/motivation ("because..." explanations)
5. Match prompt formatting to desired output style
6. Trust the model more—reduce over-specification
7. Use XML tags for agent workflows (`<current-state>`, `<blocked>`, `<workflow>`)
8. Consider agent teams for parallel workloads instead of sequential sub-agents

## Reference Files

| File | Use When |
|------|----------|
| [patterns.md](references/patterns.md) | Optimizing any prompt—transformation rules and examples |
| [agentic-patterns.md](references/agentic-patterns.md) | Building agents, agent teams, and long-horizon workflows |

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
2. **Think variants** — Less critical with adaptive thinking, but still worth cleaning up
3. **Tool invocation** — Prevent over-triggering
4. **Formatting** — Match prompt style to output style
5. **Context/motivation** — Add "because..." explanations
6. **Over-specification** — Trust the model more
7. **Verbosity** — Optimize for conciseness
8. **XML structure** — Use semantic tags for agent workflows

## Agentic Best Practices

The [agentic-patterns.md](references/agentic-patterns.md) reference covers:

1. **Context management** — 1M context window reduces compaction pressure
2. **Agent teams** — Parallel coordination for complex projects
3. **Sub-agent delegation** — Preserve main context for research tasks
4. **Tool design** — Avoid over-triggering in descriptions
5. **State tracking** — JSON for structured, text for notes
6. **Long-horizon workflows** — Incremental progress patterns
7. **Parallel execution** — When to parallelize vs sequence
8. **Error handling** — Fail fast, document blockers
