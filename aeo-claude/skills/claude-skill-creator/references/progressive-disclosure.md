# Progressive Disclosure Patterns

This document explains how Claude navigates skills and how to structure content for optimal loading.

## How Claude Reads Skills

Claude navigates skills like a filesystem, reading files only when needed.

### Three-Level Loading Model

| Level | When Loaded | Content | Token Cost |
|-------|-------------|---------|------------|
| **Level 1** | Always at startup | `name` + `description` | ~100 tokens per skill |
| **Level 2** | When skill triggers | SKILL.md body | Under 5k tokens |
| **Level 3+** | As needed | Referenced files | Effectively unlimited |

### Example Workflow

1. User asks about revenue metrics
2. Claude reads SKILL.md, sees reference to `reference/finance.md`
3. Claude invokes bash to read just that file
4. Other files (`sales.md`, `product.md`) remain unloaded (zero context tokens)

---

## Pattern: High-Level Guide with References

Keep SKILL.md as a navigation hub:

```markdown
# SKILL.md

**Basic usage**: [Core workflows are in this file]

**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

---

## Pattern: Domain-Specific Organization

Organize content by domain so Claude loads only relevant content:

**In SKILL.md:**
```markdown
# BigQuery Skill

## Quick reference by domain
**Revenue/billing**: [reference/finance.md](reference/finance.md)
**Pipeline/opportunities**: [reference/sales.md](reference/sales.md)
**Usage/features**: [reference/product.md](reference/product.md)
```

When user asks about sales metrics, Claude reads only `reference/sales.md`.

---

## Pattern: Conditional Details

Show basics in SKILL.md, reference details only when needed:

```markdown
## Creating documents
Use the document library to create new files.

## Editing documents
For simple edits, modify XML directly.

**For tracked changes and redlining**: See [REDLINING.md](REDLINING.md)
**For OOXML internals**: See [OOXML.md](OOXML.md)
```

---

## Reference Depth Rules

### One Level Deep Only

References should link directly from SKILL.md. Avoid nested references.

**Good:**
```
SKILL.md
├── references to → advanced.md
├── references to → examples.md
└── references to → reference.md
```

**Bad:**
```
SKILL.md
├── references to → advanced.md
│                   └── references to → details.md
│                                       └── references to → more.md
```

**Why:** Claude may only partially read deeply nested files, missing important context.

---

## Table of Contents for Long Files

For reference files exceeding 100 lines, include a table of contents:

```markdown
# API Reference

## Contents
- [Authentication and setup](#authentication-and-setup)
- [Core methods](#core-methods)
- [Advanced features](#advanced-features)
- [Error handling patterns](#error-handling-patterns)
- [Code examples](#code-examples)

## Authentication and setup
...
```

Claude can see the full scope even when previewing, then read complete sections.

---

## Link Format Best Practices

### Relative Links
Always use relative paths from SKILL.md location:

```markdown
See [advanced.md](advanced.md)
See [reference/finance.md](reference/finance.md)
See [scripts/analyze.py](scripts/analyze.py)
```

### Avoid Absolute Paths
Don't use:
```markdown
See [/home/user/skills/my-skill/advanced.md](/home/user/skills/my-skill/advanced.md)
```

### Forward Slashes Only
Always use `/`, never `\`:
```markdown
# Good
See [reference/guide.md](reference/guide.md)

# Bad
See [reference\guide.md](reference\guide.md)
```

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
