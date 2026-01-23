# Claude Skill Creation - Quick Reference

## CRITICAL RULES

| Rule | Requirement |
|------|-------------|
| START SMALL | Max 3 files for new skills |
| NO PLACEHOLDERS | Every file must have content |
| COMPLETE BEFORE LINKING | Write file, then add link |
| FILE COUNT | 1-3 simple, 4-6 moderate, 7-10 complex, 15+ NEVER |

---

## Frontmatter Template

```yaml
---
name: processing-pdfs
description: What it does. Use when [trigger conditions].
allowed-tools: Read, Grep, Glob  # Optional
---
```

### Field Limits

| Field | Limit | Notes |
|-------|-------|-------|
| `name` | 64 chars | Lowercase, hyphens, no reserved words |
| `description` | 1024 chars | Third person, include WHAT + WHEN |
| `allowed-tools` | Optional | Comma-separated tool list |

### Naming Convention (Gerund Form)

Use verb + -ing:
- `processing-pdfs` not `pdf-processor`
- `analyzing-data` not `data-analyzer`
- `generating-commits` not `commit-generator`

---

## Description Formula

```
[What it does] + [Key capabilities] + Use when [triggers]
```

**Good:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF documents or form automation.
```

**Bad:**
```yaml
description: Helps with documents and files when needed.
```

---

## 6-Step Creation Process

1. **Understand** - Gather concrete usage examples
2. **Plan** - Identify resources needed (STOP: Can this be 1-3 files?)
3. **Initialize** - Run `python scripts/init_skill.py <name>`
4. **Edit** - Implement SKILL.md and referenced files
5. **Package** - Run `python scripts/package_skill.py <dir>`
6. **Iterate** - Test and refine

---

## Script Commands

### Initialize New Skill
```bash
python scripts/init_skill.py <skill-name> [--path <dir>] [--with-scripts] [--with-references]

# Examples
python scripts/init_skill.py processing-pdfs
python scripts/init_skill.py analyzing-data --with-references
```

### Validate and Package
```bash
python scripts/package_skill.py <skill-dir> [--output <file.skill>] [--no-package]

# Examples
python scripts/package_skill.py ./my-skill
python scripts/package_skill.py ./my-skill --no-package  # Validate only
```

---

## File Structure Patterns

### Simple (1-3 files)
```
skill-name/
└── SKILL.md
```

### With References (3-4 files)
```
skill-name/
├── SKILL.md (navigation hub)
├── reference.md
└── examples.md
```

### With Scripts (5-7 files)
```
skill-name/
├── SKILL.md
├── guide.md
└── scripts/
    ├── script1.py
    └── script2.py
```

### What NOT to Include
- README.md (skill IS the documentation)
- INSTALLATION_GUIDE.md
- CHANGELOG.md
- Test files
- License files (belongs in plugin)

---

## Progressive Disclosure

**Three-Level Loading:**

| Level | When Loaded | Cost | Content |
|-------|-------------|------|---------|
| 1 | Always (startup) | ~100 tokens | Frontmatter only |
| 2 | When triggered | <5k tokens | SKILL.md body |
| 3+ | As needed | 0 until read | Referenced files |

**Reference Pattern:**
```markdown
**Basic usage**: [instructions here]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
```

**One Level Deep Only:**
```
SKILL.md → advanced.md     ✓
SKILL.md → advanced.md → details.md     ✗
```

---

## MCP Tool References

**Always use fully qualified names:**
```markdown
Use `ServerName:tool_name` for [action].

Examples:
- `Salesforce:query` - Run SOQL queries
- `mcp__context7__get-library-docs` - Fetch documentation
- `mcp__mssql__query` - Execute SQL queries
```

---

## Dynamic Doc Retrieval

### Primary: Context7
```
1. mcp__context7__resolve-library-id with "claude code skills"
2. mcp__context7__get-library-docs with ID + topic "skills"
```

### Fallback: WebFetch
```
WebFetch url="https://code.claude.com/docs/en/skills"
prompt="Extract skill file structure, frontmatter requirements"
```

---

## Validation Checklist

- [ ] SKILL.md under 500 lines
- [ ] Name ≤64 chars, description ≤1024 chars
- [ ] Description includes "what" AND "when"
- [ ] All referenced files exist with content
- [ ] No empty placeholder files
- [ ] File count within limits (3 simple, 6 moderate)
- [ ] MCP tools use fully qualified names
- [ ] Tested with realistic scenarios

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Claude doesn't load skill | Check description specificity, verify file location |
| "Tool not found" error | Use fully qualified MCP tool name: `Server:tool` |
| Claude loads wrong content | Reorganize SKILL.md references |
| File reference broken | Use forward slashes, verify relative path |
| Multiple skills conflict | Make descriptions more specific |

---

## Do's and Don'ts

**Do:**
- Start with 1-3 files
- Use gerund naming (`processing-pdfs`)
- Write third-person descriptions
- Complete files before referencing
- Use `Server:tool` for MCP tools
- Add TOC to files >100 lines

**Don't:**
- Create 15+ file structures
- Reference files you haven't written
- Use generic descriptions
- Nest references more than one level
- Use first person ("I can help")
