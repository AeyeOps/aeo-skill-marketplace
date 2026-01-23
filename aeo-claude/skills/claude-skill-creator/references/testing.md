# Testing Skills

This document covers testing methodologies and iteration patterns for Claude skills.

## Three-Agent Testing Pattern

Use three Claude instances for rapid iteration:

### Roles

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Claude A** | Skill Author | Describes what the skill should do |
| **Claude B** | Tester | Uses the skill in realistic scenarios |
| **You** | Observer | Watches behavior, refines based on observations |

### Why This Works

- Claude A understands agent needs
- You provide domain expertise
- Claude B reveals gaps through real usage
- Iterative refinement based on observed behavior vs assumptions

---

## Testing Workflow

### Step 1: Basic Functionality

Test that the skill loads and triggers correctly:

1. Ask Claude to list available skills
2. Verify your skill appears
3. Ask a question that should trigger the skill
4. Confirm the skill was used

### Step 2: Navigation Testing

Test how Claude explores the skill:

1. Ask questions about different topics covered by the skill
2. Watch which files Claude reads
3. Note any unexpected navigation patterns
4. Check if all file references work

### Step 3: Edge Cases

Test boundary conditions:

1. Questions at the edge of skill's domain
2. Ambiguous queries that might trigger multiple skills
3. Requests requiring deep reference material
4. Unusual input formats

---

## Observation Patterns

Watch for these behaviors during testing:

### Unexpected Exploration Paths

**Symptom:** Claude reads files in different order than anticipated.

**Fix:** Your structure may not be as intuitive as you thought. Reorganize or add clearer signposts.

### Missed Connections

**Symptom:** Claude fails to follow references to important files.

**Fix:** Make links more explicit or prominent. Consider moving content to SKILL.md.

### Overreliance on Certain Sections

**Symptom:** Claude repeatedly reads the same file.

**Fix:** Consider moving that content into main SKILL.md for faster access.

### Ignored Content

**Symptom:** Claude never accesses a bundled file.

**Fix:** File might be unnecessary or poorly signaled. Consider removing it.

---

## Validation Checklist

Before shipping a skill, verify:

### Structure
- [ ] SKILL.md under 500 lines
- [ ] All referenced files exist
- [ ] All referenced files have content (no placeholders)
- [ ] File references use correct relative paths
- [ ] No deeply nested references (one level only)

### Frontmatter
- [ ] Name under 64 characters
- [ ] Description under 1024 characters
- [ ] Description includes "what" AND "when"
- [ ] Third-person voice in description

### Functionality
- [ ] Skill triggers on expected queries
- [ ] Navigation patterns are intuitive
- [ ] All workflows complete successfully
- [ ] MCP tools use fully qualified names

### Quality
- [ ] No broken file references
- [ ] No empty placeholder files
- [ ] Files >100 lines have table of contents
- [ ] Scripts have execute permissions

---

## Iteration Based on Observations

After testing, iterate based on what you observe:

| Observation | Action |
|-------------|--------|
| Skill doesn't trigger | Improve description with more trigger terms |
| Wrong file read first | Reorganize SKILL.md structure |
| File never read | Remove or merge into another file |
| File read repeatedly | Move content to SKILL.md |
| Navigation confusing | Add clearer section headers |

---

## Debugging Commands

```bash
# Check skill file exists
ls ~/.claude/skills/my-skill/SKILL.md

# View frontmatter
head -n 15 ~/.claude/skills/my-skill/SKILL.md

# Check all files exist
ls -la ~/.claude/skills/my-skill/

# Verify file references work
# (in Claude) "Read the file reference/guide.md from my-skill"
```

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
