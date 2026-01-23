# Dynamic Documentation Retrieval

This document explains how to fetch the latest official Claude skill documentation to ensure compliance with current specifications.

## Why Retrieve Latest Documentation

- Anthropic may update skill specifications
- New frontmatter fields may be added
- Best practices evolve over time
- Ensures skills comply with current standards

---

## Primary Method: Context7

Context7 provides structured, indexed documentation.

### Step 1: Resolve Library ID

```
Tool: mcp__context7__resolve-library-id
Parameter: libraryName = "claude code skills"
```

**Expected response:** Library ID like `/websites/code_claude_en`

### Step 2: Fetch Documentation

```
Tool: mcp__context7__get-library-docs
Parameters:
  - context7CompatibleLibraryID: "/websites/code_claude_en"
  - topic: "skills SKILL.md frontmatter"
  - mode: "code"
```

### Best Topics to Query

| Topic | What You Get |
|-------|--------------|
| `"skills SKILL.md frontmatter"` | Frontmatter requirements |
| `"skills file structure"` | Directory organization |
| `"skills progressive disclosure"` | Loading patterns |
| `"skills best practices"` | Quality guidelines |
| `"plugin skills entry"` | Plugin integration |

---

## Fallback Method: WebFetch

If Context7 is unavailable, use direct web fetch.

### Fetch Skills Documentation

```
Tool: WebFetch
Parameters:
  - url: "https://code.claude.com/docs/en/skills"
  - prompt: "Extract skill file structure, frontmatter requirements, and best practices"
```

### Fetch Plugin Skills Documentation

```
Tool: WebFetch
Parameters:
  - url: "https://code.claude.com/docs/en/plugins-reference"
  - prompt: "Extract plugin skills directory structure and plugin.json format"
```

---

## When to Retrieve Documentation

### Always Retrieve When:

1. **Creating new skills** - Ensure compliance from start
2. **Major skill updates** - Check for spec changes
3. **Troubleshooting skill loading** - Verify format compliance
4. **Adding new features** - Check if new options available

### Optional Retrieval:

- Minor text edits to existing skills
- Updating examples in reference files
- Bug fixes in scripts

---

## Key Specifications to Verify

After retrieval, verify these key specifications:

### Frontmatter

| Field | Requirement |
|-------|-------------|
| `name` | ≤64 characters, lowercase, hyphens, no reserved words |
| `description` | ≤1024 characters, third person, includes what + when |
| `allowed-tools` | Optional, comma-separated tool list |

### File Structure

| Rule | Specification |
|------|---------------|
| SKILL.md location | `skills/<skill-name>/SKILL.md` |
| Max SKILL.md size | 500 lines |
| Reference depth | One level only |
| File paths | Forward slashes, relative |

### Plugin Integration

| Field | Format |
|-------|--------|
| `skills[].id` | Unique identifier |
| `skills[].entry` | Relative path to SKILL.md |

---

## Example: Pre-Creation Check

Before creating a new skill:

```markdown
## Pre-Creation Documentation Check

1. Fetch latest specs:
   - mcp__context7__get-library-docs with topic "skills frontmatter"

2. Verify requirements:
   - name: max 64 chars ✓
   - description: max 1024 chars ✓
   - allowed-tools: optional ✓

3. Proceed with skill creation following verified specs
```

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
