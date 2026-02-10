# The audit plan likely destroys meaningful plugin data

**The repository `AeyeOps/aeo-skill-marketplace` is private and inaccessible from the public internet**, so I cannot inspect the files directly. However, by cross-referencing the official Claude Code hooks specification against the file names and audit descriptions you provided, I can give a confident architectural analysis: **the "non-standard fields" being flagged almost certainly contain functional plugin configuration data, and stripping them risks breaking skill functionality.**

Here's why, and what you should verify.

## The hooks.json spec is extremely strict and narrow

The official Claude Code hooks specification (from `code.claude.com/docs/en/hooks` and `code.claude.com/docs/en/plugins-reference`) defines a **very tight schema** for `hooks/hooks.json` files inside plugins:

```json
{
  "description": "Optional human-readable description",
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "shell-command-here",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Only these fields are valid** at each level: `description` and `hooks` at the top level; `matcher` and `hooks` in each matcher group; `type`, `command`/`prompt`, and `timeout` in each hook handler. Valid event names are `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `Notification`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`, `SubagentStop`, `SubagentStart`, and `PreCompact`. That's the entire schema. Any field outside this structure is technically "non-standard" from the hooks spec perspective.

## The flagged filenames are NOT hooks files — they're config files

This is the critical insight. The standard plugin hooks directory contains **exactly one auto-discovered file**: `hooks/hooks.json`. The standard layout is:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── hooks/
│   ├── hooks.json            # THE hooks config (auto-discovered)
│   └── scripts/              # Helper scripts called by hooks
├── skills/
│   └── skill-name/
│       └── SKILL.md
├── commands/
├── agents/
└── README.md
```

The files you listed — **`notifications.json`, `compliance.json`, `quality_gates.json`, `auto_recovery.json`, `performance_monitor.json`** — are clearly not hooks configuration files. Their names describe **functional domains** (compliance rules, quality gates, auto-recovery logic, performance monitoring thresholds, notification routing). These are almost certainly **support configuration files** that the hook scripts read at runtime. A typical pattern would be:

1. `hooks.json` defines a `PostToolUse` hook that runs `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/compliance-check.sh`
2. That script reads `${CLAUDE_PLUGIN_ROOT}/hooks/compliance.json` to load its rules
3. The script applies those rules and returns a pass/fail result

If the audit plan treats these files as "hooks files with non-standard fields" and strips everything except the hooks schema fields, **it will gut the functional configuration these scripts depend on**.

## Two scenarios for what "non-standard fields" means

There are two possible interpretations of what the audit found, and the implications differ drastically:

**Scenario A: Extra fields embedded inside hooks.json files.** Some plugins may have added custom fields (like `notifications`, `compliance_rules`, `recovery_config`) directly inside their `hooks.json` alongside the standard `hooks` object. Claude Code would silently ignore these extra top-level fields, so they're harmless noise — but they also represent a data-architecture mistake (config data shouldn't live in the hooks file). In this case, stripping them is fine **only if that data is also stored elsewhere** or isn't referenced by any scripts. If scripts parse their own `hooks.json` to read these fields, stripping them breaks the scripts.

**Scenario B: Separate `.json` files in `hooks/` directories misidentified as hooks files.** The audit may have scanned the `hooks/` directory, found files other than `hooks.json`, and flagged all their contents as "non-standard hooks fields" because they don't match the hooks schema. This would be a **categorization error** — these aren't hooks files at all, they're configuration files that live alongside hooks. Stripping or reformatting them would destroy plugin configuration.

Based on the file naming pattern (`notifications.json`, `compliance.json`, `quality_gates.json`, `auto_recovery.json`, `performance_monitor.json`), **Scenario B is more likely**. These names describe distinct operational concerns with their own configuration schemas, not hooks lifecycle events.

## What the "compliant" reference tells you

You mentioned `aeo-nous/hooks/hooks.json` as a reference/compliant file. If that plugin has a clean `hooks/hooks.json` with only the standard schema fields and **no** extra `.json` files in its `hooks/` directory, it's "compliant" simply because it's a simpler plugin that doesn't need additional configuration. More complex skills — like one providing compliance checking, quality gates, or auto-recovery — **inherently need more configuration data**. Comparing them to a minimal reference and calling the extras "non-standard" conflates schema compliance with feature complexity.

## What you should verify before executing the audit plan

Since I cannot access the private repo, here are the exact things to check:

- **Open each flagged file** (`notifications.json`, `compliance.json`, etc.) and examine whether they contain hooks schema structures (event names, matcher groups, hook handlers) with extra fields bolted on, OR whether they contain entirely different data (rules, thresholds, config objects, routing tables). If the latter, they are not hooks files and should not be touched.

- **Search each plugin's `hooks.json`** for the `command` fields and trace what scripts they reference. Then check if those scripts read any of the flagged `.json` files. A simple `grep -r "notifications.json\|compliance.json\|quality_gates.json\|auto_recovery.json\|performance_monitor.json" .` across the repo will reveal dependencies.

- **Check the `plugin.json` manifests** for each skill. The `hooks` field in `plugin.json` can be a string path (`"./hooks/hooks.json"`) or an inline object. If it only points to `hooks.json`, the other files are configuration, not hooks.

- **Look for a `CLAUDE.md` or `.claude/` directory** at the repo root. This may contain project-level instructions that describe the intended architecture and why these files exist.

## The correct fix is separation, not deletion

If the audit goal is standards compliance, the right approach is to **ensure `hooks.json` files contain only valid hooks schema fields** while preserving the additional configuration files as-is. The separation should be architectural:

```
hooks/
├── hooks.json           # Pure hooks config (events, matchers, handlers)
├── config/              # Plugin-specific configuration
│   ├── compliance.json
│   ├── quality_gates.json
│   ├── notifications.json
│   ├── auto_recovery.json
│   └── performance_monitor.json
└── scripts/             # Hook scripts that read from config/
    ├── compliance-check.sh
    └── monitor.sh
```

If any non-standard fields are embedded directly in `hooks.json`, extract them into separate config files and update the scripts to read from the new locations. But **do not delete the data**. These fields represent the actual intelligence of the skills — the rules, thresholds, and behavior configurations that make a compliance checker check compliance or a quality gate enforce quality.

## Bottom line

The "non-standard fields" are almost certainly **meaningful skill configuration data** that happens to live in or alongside hooks files. The hooks spec is deliberately minimal (it only defines event routing and command execution), so any plugin doing something substantive — compliance checking, quality gating, auto-recovery, performance monitoring — necessarily carries configuration data beyond what the hooks schema defines. The audit plan's instinct to enforce schema compliance is sound, but executing it as field-stripping rather than data-separation will likely break plugins. Verify by tracing script dependencies before removing anything.