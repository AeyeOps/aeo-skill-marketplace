---
name: opus-prompting
description: |
  Writing assistant that identifies artifact type (CLAUDE.md, skill, command, agent prompt)
  and surfaces relevant prompt patterns when invoked. Covers Claude's behavioral properties,
  over-specification prevention, and agentic workflow design.
---

# Prompt Writing Assistant

Claude follows natural language more literally than most models expect. The primary failure mode is **overtriggering and over-specification** — not under-compliance. Write less, trust more.

If unsure whether these behavioral properties are current, check the system date and search for the latest Claude model documentation.

## Claude Behavioral Properties

| Property | Implication |
|----------|-------------|
| Adaptive thinking (4 effort levels) | Let Claude calibrate reasoning depth; specify effort only at API level when needed |
| 200K context window (1M in beta) | Long conversations maintain quality; 1M requires beta access |
| Literal instruction following | Every instruction compounds — write guidelines, not rules |
| High system prompt responsiveness | Natural language over directives; aggressive language causes overtriggering |
| Overtriggering as primary failure mode | `MUST use [tool]` → tools fired when not needed; soften to `Use [tool] when...` |
| Overeagerness / overengineering | Claude adds features, docs, error handling beyond what's asked; scope constraints help |
| Prefilling deprecated | Assistant message prefilling is unsupported; use system prompt instructions or structured output |

## Applying These Patterns

Read these artifact-type blocks to identify which patterns matter most for your current task. Pattern numbers reference `references/patterns.md`.

### CLAUDE.md Instructions

**Key concern**: Over-specification compounds across every session. Each unnecessary rule burns token budget and can trigger the behaviors it's trying to prevent.

- Pattern 1 (Aggressive language) — soften or remove `MUST`/`NEVER`/`CRITICAL`; they cause overtriggering in instructions that persist across sessions
- Pattern 5 (Context/motivation) — one `because...` per constraint lets Claude generalize rather than memorize
- Pattern 6 (Over-specification) — describe intent, not exhaustive rules; three similar lines beat a premature abstraction

**Guidance**: Write guidelines a colleague would follow without needing to memorize them. If a rule triggers the behavior it's preventing (e.g., `NEVER be verbose` makes the prompt verbose), cut it.

### Skill Body (SKILL.md)

**Key concern**: The `description` field in frontmatter is a token-budget signal — it controls when the skill loads into context. Lead with what the skill *does when invoked*, not what subject it covers.

- Pattern 7 (Verbosity) — skill descriptions are ranking signals; every word must earn its place
- Pattern 6 (Over-specification) — progressive disclosure: frontmatter triggers loading, body provides depth
- Pattern 4 (Formatting) — match the skill's prose style to the output you want from the model

**Guidance**: First sentence of `description` should be a verb phrase naming the activation behavior (e.g., "identifies X and surfaces Y" not "covers X, Y, and Z"). See also: `claude-skill-creator` skill.

### Slash Command Template

**Key concern**: Command templates are read once per invocation. The model parses them linearly — structure (especially XML) matters more than in persistent context.

- Pattern 8 (XML structure) — use semantic tags (`<workflow>`, `<reference>`, `<current-state>`) to separate mutable from immutable sections
- Pattern 4 (Formatting) — prompt format influences output format; structure the template like you want the output
- Pattern 3 (Tool invocation) — conditional tool use (`Use [tool] when...`) prevents overtriggering in command workflows

**Guidance**: Front-load the command's purpose and exit criteria. `$ARGUMENTS` substitution is a command-only feature — if this content is in a skill, arguments won't route. See also: `slash-command-creator` skill.

### Agent System Prompt

**Key concern**: Agents are more literal than interactive sessions. Overtriggering is amplified because agents act autonomously on every instruction.

- Pattern 1 (Aggressive language) — `MUST`/`ALWAYS` in agent prompts cause pathological tool loops
- Pattern 3 (Tool invocation) — describe tools conditionally; agents will invoke every tool that sounds relevant
- Pattern 6 (Over-specification) — agents handle novel situations better with principles than with exhaustive rules

**Guidance**: Describe tool use conditionally (`Use X when Y`) not imperatively (`Always use X`). Test by asking: if this instruction fires incorrectly, what's the blast radius?

## Self-Check

Before outputting, run these three tests:

1. **Golden rule**: Would a colleague with minimal context understand this without asking clarifying questions?
2. **Self-defeating instructions**: Does any instruction trigger the behavior it's preventing? (`MUST NOT be verbose` is itself verbose; `NEVER overthink` invites overthinking)
3. **How vs what**: Am I specifying *how* when the reader only needs *what*? (If yes, cut the how — Claude will find an appropriate implementation)

## References

| File | Content |
|------|---------|
| `references/patterns.md` | 8 pattern categories with before/after examples and transformation rules |
| `references/agentic-patterns.md` | Agent teams, delegation, tool design, state tracking, error handling |
| `scripts/analyze-prompt.py` | CLI analyzer for deprecated patterns (configure via `scripts/config.json`) |
