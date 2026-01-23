# Skill File Organization

This document covers directory structure patterns and file organization best practices for Claude skills.

## Directory Structure Patterns

### Pattern 1: Simple Skill (Single File)

Best for focused, single-purpose skills.

```
my-skill/
└── SKILL.md
```

**When to use:**
- Skill has one main workflow
- All guidance fits in ~300 lines
- No need for code or extensive reference material

---

### Pattern 2: Skill with Documentation

Best for skills needing additional reference material.

```
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (loaded as needed)
├── examples.md (loaded as needed)
└── workflows.md (loaded as needed)
```

**When to use:**
- Multiple related workflows
- Need separate reference documentation
- Want to keep SKILL.md under 500 lines

---

### Pattern 3: Skill with Code and Docs

Best for skills with executable utilities.

```
pdf-skill/
├── SKILL.md (main instructions)
├── FORMS.md (form-filling guide)
├── reference.md (API reference)
├── examples.md (usage examples)
└── scripts/
    ├── analyze_form.py (executed via bash, not loaded)
    ├── fill_form.py
    └── validate.py
```

**When to use:**
- Deterministic operations benefit from scripts
- Same code would be rewritten repeatedly
- Scripts need to execute, not load into context

---

### Pattern 4: Domain-Specific Organization

Best for skills serving multiple distinct domains.

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

**When to use:**
- Skill serves multiple business domains
- Users typically need only one domain at a time
- Domains have distinct terminology/schemas

---

## File Types and Their Purposes

| Type | Purpose | Token Cost | Best For |
|------|---------|------------|----------|
| **Instructions** (`.md`) | Flexible guidance | Loaded into context | Workflows, concepts |
| **Code** (`.py`, `.sh`) | Deterministic operations | Executed, not loaded | Utilities, validation |
| **Resources** (schemas, templates) | Reference materials | Loaded on demand | Data structures, examples |

---

## File Naming Conventions

### Skill Names
Use gerund form (verb + -ing):
- `processing-pdfs` not `pdf-processor`
- `analyzing-spreadsheets` not `spreadsheet-analyzer`
- `generating-commits` not `commit-generator`

### Reference Files
Use descriptive, lowercase names with hyphens:
- `form-validation.md` not `FormValidation.md`
- `api-reference.md` not `api_reference.md`

### Scripts
Use snake_case for Python, kebab-case for shell:
- `analyze_form.py`
- `fill-form.sh`

---

## What NOT to Include

These files should NOT be in skills:

| File | Why Not |
|------|---------|
| `README.md` | Skill IS the documentation |
| `INSTALLATION_GUIDE.md` | Setup should be in SKILL.md |
| `CHANGELOG.md` | Version history clutters skill |
| `LICENSE` | License info belongs in plugin, not skill |
| `test_*.py` | Tests are for development, not runtime |
| `.gitignore` | Git config not needed |

---

## File Size Guidelines

| File Type | Max Lines | If Exceeded |
|-----------|-----------|-------------|
| SKILL.md | 500 | Split into references |
| Reference files | 500 | Split by topic |
| Scripts | 500 | Refactor or split |

**For files >100 lines:** Include a table of contents at the top.

---

## Example: Table of Contents

For longer reference files:

```markdown
# API Reference

## Contents
- [Authentication](#authentication)
- [Core Methods](#core-methods)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)

## Authentication
...

## Core Methods
...
```

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
