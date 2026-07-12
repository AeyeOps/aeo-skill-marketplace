# Resume Strategies

Legacy migration and missing state handling for the RESUME phase.

## Legacy Repo Detection (Migration to EPCC v3)

If `PRD.md` exists but `epcc-features.json` does NOT exist, this is a legacy EPCC repo.

### Step 1: Detect Legacy State

```python
legacy_files = {
    "PRD.md": exists("PRD.md"),
    "TECH_REQ.md": exists("TECH_REQ.md"),
    "EPCC_PLAN.md": exists("EPCC_PLAN.md"),
    "EPCC_EXPLORE.md": exists("EPCC_EXPLORE.md")
}

v3_files = {
    "epcc-features.json": exists("epcc-features.json"),
    "epcc-progress.md": exists("epcc-progress.md")
}

if any(legacy_files.values()) and not any(v3_files.values()):
    trigger_migration_prompt()
```

### Step 2: Migration Prompt

Use AskUserQuestion tool:
```json
{
  "questions": [{
    "question": "Legacy EPCC repo detected (PRD.md found, no feature tracking). Migrate to EPCC v3?",
    "header": "Migrate?",
    "multiSelect": false,
    "options": [
      {"label": "Yes, migrate", "description": "Parse PRD.md/TECH_REQ.md, generate epcc-features.json and epcc-progress.md"},
      {"label": "No, skip", "description": "Continue without v3 tracking (limited session continuity)"}
    ]
  }]
}
```

### Step 3: Migration Execution

If user confirms migration:

#### 3a. Parse PRD.md for Features

Look for feature sections in PRD.md:
- "Core Features" / "Features" / "Functional Requirements"
- Priority markers: P0, P1, P2 or Must Have, Should Have, Nice to Have

Extract each feature:
```json
{
  "id": "F001",
  "name": "[Feature name]",
  "description": "[Feature description]",
  "priority": "[P0/P1/P2]",
  "status": "pending",
  "passes": false,
  "source": "PRD.md#[section]"
}
```

#### 3b. Enrich with TECH_REQ.md (If Present)

If TECH_REQ.md exists, parse for technical subtasks and infrastructure requirements.

#### 3c. Generate epcc-features.json

```json
{
  "project": "[Project name from PRD]",
  "version": "3.0.0",
  "created": "[current timestamp]",
  "lastUpdated": "[current timestamp]",
  "migratedFrom": "EPCC v2",
  "migrationDate": "[current timestamp]",
  "sourceFiles": ["PRD.md", "TECH_REQ.md"],
  "WARNING": "Feature definitions are IMMUTABLE.",
  "features": [],
  "metrics": {
    "total": 0,
    "verified": 0,
    "inProgress": 0,
    "pending": 0,
    "percentComplete": 0
  }
}
```

#### 3d. Initialize epcc-progress.md

```markdown
# EPCC Progress Log

**Project**: [Project Name]
**Started**: [Original PRD date if available, else today]
**Migrated to v3**: [Today's date]
**Progress**: 0/X features (0%)

---

## Session: Migration - [timestamp]

### Migration from EPCC v2

Imported features from legacy EPCC setup:
- Source: PRD.md, TECH_REQ.md
- Features imported: X
- Infrastructure tasks: Y

### Feature Summary
| ID | Name | Priority | Status |
|----|------|----------|--------|
| F001 | [Name] | P0 | pending |
...

### Next Session
- Review imported features for accuracy
- Mark any already-completed features
- Begin implementation with `/epcc-code [feature-id]`
```

#### 3e. Git Commit Migration

```bash
git add epcc-features.json epcc-progress.md
git commit -m "chore: migrate to EPCC v3 tracking system

- Imported X features from PRD.md
- Added Y infrastructure tasks from TECH_REQ.md
- Initialized progress tracking

All features marked as pending. Run /epcc-resume --status to verify."
```

### Step 4: Feature Status Assessment

After migration, offer to mark completed features using AskUserQuestion with multiSelect.

### Step 5: Report Migration Results

```
🎉 **EPCC v3 Migration Complete**

**Project**: [Project Name]
**Features Imported**: X total
**Status**: ✅ Verified: [count] | ⬜ Pending: [count]

**Files Created**:
  - epcc-features.json (feature tracking)
  - epcc-progress.md (session log)

**Next Steps**:
1. Run `/epcc-resume` to see full status
2. Start work with `/epcc-code [feature-id]`
```

## Handling Missing State Files

### No epcc-features.json

```markdown
## EPCC Resume: No Feature Tracking

No `epcc-features.json` found. This project doesn't have structured feature tracking.

**Options**:
1. **Start fresh tracking**: Run `/prd` to create requirements and feature list
2. **Add tracking to existing plan**: Run `/epcc-plan` to generate feature list from EPCC_PLAN.md
3. **Continue without tracking**: Use standard EPCC commands without progress tracking
```

### No epcc-progress.md

```markdown
## EPCC Resume: No Progress Log

Found `epcc-features.json` but no `epcc-progress.md`.

Creating epcc-progress.md from current state...

[Generate initial progress log from epcc-features.json and git history]
```

## Output Formats

### Full Resume (Default)

```markdown
## EPCC Session Resume: [Project Name]

**Working Directory**: /path/to/project
**Branch**: [current-branch]
**Last Commit**: [sha] - [message]

---

### Progress: X/Y features (Z%)

| Status | Feature | Priority | Notes |
|--------|---------|----------|-------|
| ✅ | F001: [Name] | P0 | verified, commit: abc123 |
| 🔄 | F003: [Name] | P0 | in_progress, 2/5 subtasks |
| ⬜ | F004: [Name] | P1 | pending |

### Last Session Summary
[From epcc-progress.md]

### Recommended Next Action
**Continue**: [in_progress feature]
**Start work with**: `/epcc-code [feature-id]`
```

### Status Only (--status)

```markdown
## EPCC Progress: [Project Name]

**Progress**: X/Y features (Z%)
**Last Session**: [Date] - Completed [feature]
**Current**: [in_progress feature] | **Next**: [pending feature]
```

### Validation Mode (--validate)

```markdown
## EPCC Validation: [Project Name]

Running E2E checks on X verified features...

| Feature | E2E Status | Notes |
|---------|------------|-------|
| F001 | ✅ PASS | All criteria verified |
| F003 | ❌ FAIL | [issue description] |

### Regression Detected!
**Action Required**: Fix regressions before continuing.
**Recommended**: `/epcc-code [feature] --fix-regression`
```

## Integration with Other Commands

| State | Recommended Command |
|-------|---------------------|
| Feature in progress | `/epcc-code [feature-id]` |
| All features pending | `/epcc-code [highest-priority]` |
| Regressions detected | `/epcc-code [regressed-feature] --fix` |
| All features verified | `/epcc-commit` |
| No features defined | `/epcc-plan` |
