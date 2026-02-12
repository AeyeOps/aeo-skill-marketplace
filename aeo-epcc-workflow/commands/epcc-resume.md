---
name: epcc-resume
description: Resume multi-session work - runs startup checklist and identifies next action
version: 0.1.0
argument-hint: "[--status|--feature F001|--validate]"
---

# EPCC Resume Command

You are in the **RESUME** phase of the EPCC workflow. Your mission is to quickly orient and identify the next action for continuing multi-session work.

**Opening Principle**: Every session starts with clear context. No progress is lost when handoffs are done right.

## Arguments
$ARGUMENTS

### Resume Modes

Parse mode from arguments:
- **Default** (no flags): Full startup checklist + recommended action
- `--status`: Quick progress summary only (no action recommendation)
- `--feature F001`: Focus on specific feature, show its detailed status
- `--validate`: Run E2E checks on all "verified" features

## Prerequisites Check

```bash
# Check for EPCC state files
if [ ! -f "epcc-features.json" ] && [ ! -f "epcc-progress.md" ]; then
    if [ -f "PRD.md" ]; then
        # Legacy repo detected - trigger migration flow
        # See @reference/resume-strategies.md
    else
        echo "No EPCC progress tracking found."
        echo "Start a new tracked project with: /prd or /epcc-plan"
        exit 0
    fi
fi
```

## Legacy Repo Detection

@reference/resume-strategies.md

## Session Startup Checklist (Default Mode)

### Phase 1: Environment Verification
```bash
pwd
git branch --show-current
git status --short
git log --oneline -10
```

### Phase 2: Progress State Recovery
```bash
if [ -f "epcc-progress.md" ]; then
    head -100 epcc-progress.md
fi

if [ -f "epcc-features.json" ]; then
    cat epcc-features.json
fi
```

### Phase 3: Feature Analysis

Parse `epcc-features.json` to calculate:
- Total features, features passing (verified), in progress, pending
- Percentage complete

Identify:
- Current in-progress feature (if any)
- Highest-priority pending feature
- Any features that regressed

### Phase 4: Quick Verification (Optional)

If test command is known:
```bash
npm test    # or pytest, etc.
```
Report any failures, especially in previously-passing features.

## Output Formats

See resume strategies above for output format templates.

## Handling Missing State Files

See resume strategies above for missing state file handling.

## Integration with Other Commands

| State | Recommended Command |
|-------|---------------------|
| Feature in progress | `/epcc-code [feature-id]` |
| All features pending | `/epcc-code [highest-priority]` |
| Regressions detected | `/epcc-code [regressed-feature] --fix` |
| All features verified | `/epcc-commit` |
| No features defined | `/epcc-plan` |

## Autonomous Behavior

This command operates **autonomously** with minimal user interaction:

- **Don't ask, just report**: Run tests → report results. Analyze priorities → suggest action. Report missing files → suggest alternatives.
- **Only ask** if multiple valid next actions with equal priority, or critical decision required (e.g., major regression).

## Example Sessions

### Normal Resume
```
User: /epcc-resume
Claude: Progress: 3/8 features (37.5%)... Recommended: Continue F003
```

### Status Check
```
User: /epcc-resume --status
Claude: Progress: 3/8 (37.5%) | Last: F002 completed | Next: F003
```

### Feature Detail
```
User: /epcc-resume --feature F002
Claude: F002 - Task CRUD | Status: verified | Passes E2E: true
```

### Validation
```
User: /epcc-resume --validate
Claude: Running E2E checks on 3 verified features... [results]
```

## Remember

**Quick orientation enables confident continuation.**

**DO NOT**: Modify files, start implementation, change feature status

**DO**: Read state files, run checks, report status, suggest next action

This command is the **first step** of any resumed session.
