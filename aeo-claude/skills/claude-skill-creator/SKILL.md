---
name: claude-skill-creator
description: Author high-quality Claude Code skills with proper frontmatter, trigger-optimized descriptions, progressive disclosure structure, and MCP tool integration. Includes file organization patterns, testing approaches, and performance tuning. Consult when building new skills, debugging activation issues, or refactoring existing skill content.
---

# Claude Skill Creator

Comprehensive guide for authoring high-quality Claude skills.

## CRITICAL RULES - READ BEFORE CREATING ANY SKILL

**These rules are NON-NEGOTIABLE. Violating them wastes tokens and breaks skills.**

### Rule 1: START SMALL
- **Maximum files for new skill: 3** (SKILL.md + 2 supporting)
- Only add more files after the skill works

### Rule 2: NO PLACEHOLDERS
- **NEVER create empty files**
- **NEVER reference files you haven't written**
- If you write `See [guide.md]`, then guide.md MUST exist with content

### Rule 3: COMPLETE BEFORE LINKING
- Write the referenced file BEFORE adding the link to SKILL.md
- Test that each referenced file exists and has content

### Rule 4: FILE COUNT LIMITS

| Complexity | Max Files | When to Use |
|------------|-----------|-------------|
| Simple | 1-3 | Most skills |
| Moderate | 4-6 | Multi-domain skills |
| Complex | 7-10 | Rare, justify each file |
| **15+ files** | **NEVER** | **You are over-engineering** |

### Before Creating ANY File, Ask:
1. Can this fit in SKILL.md? - Do that
2. Will I complete this file RIGHT NOW? - If no, don't create it
3. Am I anticipating future needs? - Stop. Solve current problem only.

**Detailed anti-pattern examples**: See [references/anti-patterns.md](references/anti-patterns.md)

---

## Latest Official Documentation

Before creating skills, fetch current Anthropic specifications:

### Primary: Context7
1. Resolve: `mcp__context7__resolve-library-id` with "claude code skills"
2. Fetch: `mcp__context7__get-library-docs` with ID `/websites/code_claude_en` topic "skills"

### Fallback: WebFetch
```
WebFetch url="https://code.claude.com/docs/en/skills"
prompt="Extract skill file structure, frontmatter requirements, and best practices"
```

**Complete retrieval guide**: See [references/doc-retrieval.md](references/doc-retrieval.md)

---

## Core Principles

### The Context Window is a Public Good

Your skill shares context with system prompt, conversation history, other skills, and user requests.

**Loading Model:**
- **Level 1** (Always): `name` + `description` (~100 tokens per skill)
- **Level 2** (When triggered): SKILL.md body (<5k tokens)
- **Level 3+** (As needed): Referenced files (effectively unlimited)

**Best Practice:** Keep SKILL.md under 500 lines.

---

## Frontmatter Structure

```yaml
---
name: skill-name
description: What it does. Use when [triggers].
allowed-tools: Read, Grep, Glob  # Optional: restrict tool access
---
```

### Requirements

| Field | Limit | Notes |
|-------|-------|-------|
| `name` | 64 chars | Lowercase, hyphens only. No "anthropic"/"claude" |
| `description` | 1024 chars | Third person. Include WHAT + WHEN |
| `allowed-tools` | Optional | Comma-separated tool list |

### Naming Convention (Gerund Form)

Use verb + -ing:
- `processing-pdfs` not `pdf-processor`
- `analyzing-spreadsheets` not `spreadsheet-analyzer`
- `generating-commits` not `commit-generator`

### Description Formula

```
[What the skill does]. Use when [trigger conditions].
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

## File Organization

### Directory Patterns

**Simple (1 file):**
```
my-skill/
└── SKILL.md
```

**With References (3-4 files):**
```
my-skill/
├── SKILL.md
├── reference.md
└── examples.md
```

**With Scripts (5-7 files):**
```
pdf-skill/
├── SKILL.md
├── FORMS.md
└── scripts/
    ├── analyze_form.py
    └── fill_form.py
```

**Complete guide**: See [references/file-organization.md](references/file-organization.md)

### What NOT to Include

- README.md (skill IS the documentation)
- INSTALLATION_GUIDE.md
- CHANGELOG.md
- Test files
- License files (belongs in plugin)

---

## Progressive Disclosure

Claude navigates skills like a filesystem, reading files only when needed.

**Keep references one level deep from SKILL.md:**
```
SKILL.md
├── references to → advanced.md     ✓
├── references to → reference.md    ✓
└── references to → examples.md     ✓
```

**Avoid nested references:**
```
SKILL.md → advanced.md → details.md → more.md    ✗
```

**For files >100 lines:** Include a table of contents.

**Complete patterns**: See [references/progressive-disclosure.md](references/progressive-disclosure.md)

---

## MCP Tool References

Always use fully qualified tool names: `ServerName:tool_name`

```markdown
Use `Salesforce:query` for SOQL queries.
Use `BigQuery:bigquery_schema` for table schemas.
Use `mcp__context7__get-library-docs` for documentation.
```

**Why:** Tool names conflict across servers. Qualified names ensure correct invocation.

**Complete guide**: See [references/mcp-tools.md](references/mcp-tools.md)

---

## 6-Step Creation Process

### Step 1: Understand
Gather concrete usage examples. Ask: "What would trigger this skill?"

### Step 2: Plan
Identify resources needed. **STOP AND CHECK:** Can this be 1-3 files?

### Step 3: Initialize
Run `python scripts/init_skill.py <skill-name> --path <output-dir>`

### Step 4: Edit
Implement SKILL.md and referenced files. **Every file you reference must exist.**

### Step 5: Package
Run `python scripts/package_skill.py <skill-dir>` to validate and package.

### Step 6: Iterate
Test with realistic scenarios. Refine based on Claude's navigation patterns.

---

## Testing

Use the three-agent pattern:
1. **Claude A** (Author): Describes desired behavior
2. **Claude B** (Tester): Uses skill in realistic scenarios
3. **You** (Observer): Watch navigation, refine based on observations

**Watch for:**
- Unexpected file access order
- Missed references
- Ignored files (may be unnecessary)

**Complete guide**: See [references/testing.md](references/testing.md)

---

## Troubleshooting

### Skill Doesn't Load

1. Check YAML frontmatter syntax (opening/closing `---`)
2. Verify file location: `.claude/skills/<name>/SKILL.md`
3. Check description specificity - is it triggering?

### Broken References

1. Verify all referenced files exist
2. Check paths use forward slashes (`/`)
3. Ensure no placeholder files

### Multiple Skills Conflict

1. Make descriptions more specific
2. Use "Use when [specific scenario]" phrases
3. Consider merging related skills

---

## Security

**Only use skills from trusted sources:**
- Skills you created
- Skills from Anthropic
- Verified, audited skills

Skills can direct Claude to invoke tools in unintended ways. Audit untrusted skills thoroughly.

---

## Quick Reference

### Checklist

- [ ] SKILL.md under 500 lines
- [ ] Name ≤64 chars, description ≤1024 chars
- [ ] Description includes "what" AND "when"
- [ ] All referenced files exist with content
- [ ] No empty placeholder files
- [ ] File count within limits (3 for simple, 6 for moderate)
- [ ] MCP tools use fully qualified names
- [ ] Tested with realistic scenarios

### Do's
- Start with 1-3 files
- Write third-person descriptions
- Use gerund naming (`processing-pdfs`)
- Complete files before referencing

### Don'ts
- Create 15+ file structures
- Reference files you haven't written
- Use generic descriptions
- Nest references more than one level

---

## Examples

Complete working examples:
- [examples/simple-skill.md](examples/simple-skill.md) - Single-file skill
- [examples/multi-file-skill.md](examples/multi-file-skill.md) - Multi-file with references
- [examples/code-skill.md](examples/code-skill.md) - Skill with scripts

---

## Claude CLI Plugin Commands

The Claude CLI has direct plugin management commands (not just interactive `/plugin`):

```bash
claude plugin marketplace add <source>    # Add marketplace from URL, path, or GitHub repo
claude plugin marketplace list            # List configured marketplaces
claude plugin marketplace remove <name>   # Remove a marketplace
claude plugin marketplace update [name]   # Update marketplace(s)
claude plugin validate <path>             # Validate plugin/marketplace manifest
claude plugin install <plugin>            # Install plugin from marketplace
```

**Supported marketplace sources:**
- Local paths: `/path/to/marketplace` or `./relative/path`
- GitHub repos: `owner/repo` (shorthand)
- Git URLs: `https://github.com/owner/repo.git`
- Direct marketplace.json URLs

**Not supported:** Azure DevOps URLs (use local clone instead)

---

## Additional Resources

- **Quick Reference**: See [QUICK-REFERENCE.md](QUICK-REFERENCE.md)
- **Official Docs**: https://code.claude.com/docs/en/skills
- **Plugin Integration**: https://code.claude.com/docs/en/plugins-reference
