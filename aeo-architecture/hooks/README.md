# Architecture - Prompt Pattern Detector Hooks

Three lightweight `UserPromptSubmit` triggers that detect architecture-related prompts and invoke corresponding shell scripts.

## Consolidated Hooks

This `hooks.json` consolidates three previously separate hook files:

| Original File | Trigger Script | Purpose |
|--------------|----------------|---------|
| `architecture-design-hook.json` | `architecture_trigger.sh` | Detects architecture design prompts |
| `architecture-docs-hook.json` | `architecture_docs_trigger.sh` | Detects architecture documentation prompts |
| `parallel-architecture-hook.json` | `parallel_architecture_trigger.sh` | Detects parallel architecture analysis prompts |

All three fire on `UserPromptSubmit` with an empty matcher (matches all prompts). The shell scripts themselves contain the pattern-matching logic to determine whether to activate.
