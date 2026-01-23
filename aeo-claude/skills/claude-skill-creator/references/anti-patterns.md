# Skill Creation Anti-Patterns

This document details common mistakes when creating Claude skills and how to avoid them.

## The #1 Mistake: Over-Engineering

**Problem:** Creating a comprehensive skill structure with 15-20 referenced files, but only implementing 3-4 of them.

### Why This Happens

1. Progressive disclosure pattern encourages creating an index first
2. Enthusiasm for completeness leads to ambitious scope
3. Time runs out before filling in all referenced files
4. Result: Skill with broken links and empty promises

### Impact

- Claude follows link to non-existent file - confusion and wasted tokens
- User loses trust in skill quality
- Wasted tokens loading an incomplete index
- Maintenance burden (unfinished files linger forever)

---

## The Right Approach: Start Small

### Step-by-Step Process

```
Step 1: Create SKILL.md with minimal scope (1-3 topics)
Step 2: Immediately create any referenced files
Step 3: Test the skill - does it solve the problem?
Step 4: (Optional) Add 1-2 more files only if proven necessary
Step 5: Stop when problem is solved
```

### NOT This:

```
Step 1: Plan comprehensive skill with 20 topics
Step 2: Create SKILL.md referencing all 20 files
Step 3: Create 4 files, run out of time
Step 4: Ship incomplete skill with broken references
```

---

## File Count Guidelines

| Skill Complexity | Max Files | When to Use |
|-----------------|-----------|-------------|
| Simple | 1-3 | Most skills - single domain, focused purpose |
| Moderate | 4-6 | Multi-domain skills, multiple workflows |
| Complex | 7-10 | Rare! Enterprise skills, extensive reference docs |
| **15+ files** | **NEVER** | **You are over-engineering** |

---

## Example: Right-Sized vs Over-Engineered

### Good - Focused Skill (3 files)

```
pdf-skill/
├── SKILL.md (main patterns + quick start)
├── forms.md (form filling details)
└── extraction.md (text extraction details)
```

**Why it works:**
- Every file exists and has content
- Clear, focused purpose
- Easy to maintain

### Bad - Over-Engineered Skill (20 files, half empty)

```
pdf-skill/
├── SKILL.md (references 20 files)
├── basics/
│   ├── installation.md (empty)
│   ├── quick-start.md (empty)
│   └── configuration.md (empty)
├── advanced/
│   ├── forms.md (has content)
│   ├── encryption.md (empty)
│   ├── compression.md (empty)
│   └── optimization.md (empty)
└── [12 more empty files]
```

**Problems:**
- Broken links everywhere
- Wasted tokens on empty promises
- Maintenance nightmare
- Claude gets confused

---

## Gatekeeping Questions

Before creating any skill, ask yourself:

1. **Can this be 1 file?** If yes, do that.
2. **If multi-file, can I complete ALL files RIGHT NOW?** If no, reduce scope.
3. **Am I creating placeholders?** If yes, stop.
4. **Would the user actually need this depth?** If uncertain, start smaller.
5. **Am I solving a current problem or anticipating future ones?** Focus on current.

---

## Recovery: Fixing Over-Engineered Skills

If you've already created an over-engineered skill:

1. **Audit all files** - List which have content, which are empty
2. **Remove empty files** - Delete any file without substantial content
3. **Fix broken references** - Update SKILL.md to remove links to deleted files
4. **Consolidate** - Can remaining files be merged into fewer files?
5. **Test** - Verify skill still works with reduced file count

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
