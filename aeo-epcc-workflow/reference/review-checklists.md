# Review Checklists & Quality Validation

Quality validation workflow and feature verification gates for the COMMIT phase.

## Quality Validation Workflow

### Phase 1: Run Quality Checks

Execute checks from EPCC_EXPLORE.md (or sensible defaults if greenfield):

```bash
# Tests
[test-command]  # pytest, npm test, cargo test, etc.

# Coverage
[coverage-command]  # pytest --cov, npm run coverage, etc.

# Linting
[linter-command]  # ruff check, eslint, clippy, etc.

# Type checking
[type-check-command]  # mypy, tsc, etc.
```

**Auto-fix pattern**: Run → fix issues → re-run → proceed when all pass

**Quality gates** (must pass before commit):
- All tests passing
- Coverage meets target (from EPCC_EXPLORE.md or ≥80% default)
- No linting errors (warnings OK)
- Type checking clean
- No CRITICAL/HIGH security vulnerabilities

### Phase 2: Handle Failures

**Automatic fixes** (no user input):
- Formatting issues → Run formatter (black, prettier, rustfmt)
- Import issues → Run import organizer
- Linting auto-fixes → Run linter with --fix
- Simple type errors → Add type annotations

**Ask user when:**
- Can't fix after 2-3 attempts
- Fix requires changing requirements/approach
- Security vulnerability needs architectural change
- Tests fail with unclear root cause

### Commit Blockers

**Never commit when:**
- CRITICAL or HIGH security vulnerabilities unfixed
- Tests failing (even if "just flaky" - fix or skip properly with markers)
- On main/master branch (create feature branch first)
- Committing to someone else's commit without permission

**Pause to fix when:**
- Coverage dropped below target (add tests or document why)
- Multiple TODO/FIXME/DEBUG statements (clean up or track as issues)
- Linting failures (auto-fix or suppress with comments explaining why)
- Type errors (add annotations or use proper types)

**Principle**: Don't commit broken code. Fix or block commit.

## Error Recovery

### Tests Failed

```bash
# Run tests to see failures
[test-command]

# Common auto-fixes:
# - Import errors → fix imports
# - Syntax errors → fix syntax
# - Type errors → add annotations
# - Assertion failures → fix logic or update expected values

# Re-run after fix
[test-command]

# If still failing after 2-3 attempts, ask user
```

### Coverage Below Target

```bash
# Generate coverage report
[coverage-command]

# Identify uncovered lines
# Add tests for critical paths
# Or document why coverage acceptable in EPCC_COMMIT.md

# Re-run coverage
[coverage-command]
```

### Linting/Formatting Issues

```bash
# Auto-fix
[linter-command] --fix
[formatter-command]

# Re-run checks
[linter-command]

# If failures persist, check if legitimate exceptions
# Add suppression comments with explanations
```

### Security Vulnerabilities

```bash
# Review findings from CODE phase (in EPCC_CODE.md)
# Low/Medium: Document, create follow-up issue
# High: Fix before commit
# Critical: Block commit, fix immediately
```

## Feature Verification Gate

If `epcc-features.json` exists, apply additional verification gates.

### Pre-Commit Feature Check

```bash
if [ -f "epcc-features.json" ]; then
    # Check which feature is being committed
    # Verify all subtasks complete
    # Verify acceptance criteria met
    # Verify E2E tests passing
fi
```

### Feature Verification Rules

**For P0 (Must Have) features:**

| Requirement | Action if Not Met |
|-------------|-------------------|
| All subtasks complete | **BLOCK COMMIT** - Complete subtasks first |
| All acceptance criteria verified | **BLOCK COMMIT** - Run E2E verification |
| `passes: true` in epcc-features.json | **BLOCK COMMIT** - Verify before marking |
| Test evidence documented | **WARN** - Add screenshot/output reference |

**For P1/P2 features:**

| Requirement | Action if Not Met |
|-------------|-------------------|
| Feature incomplete | **WARN** - Allow commit but document in message |
| Some subtasks pending | **WARN** - Track as deferred work |

### Update Feature Status on Commit

When committing a verified feature:

```json
{
  "id": "F001",
  "status": "verified",
  "passes": true,
  "verifiedAt": "[ISO timestamp]",
  "commit": "[SHA]",
  "subtasks": [
    {"name": "...", "status": "complete"}
  ]
}
```

### Update Progress Log on Commit

Append commit entry to `epcc-progress.md`:

```markdown
---

## Commit: feat(F001) - [Date Time]

### Feature Completed
- **F001**: User Authentication - VERIFIED

### Quality Gates
| Gate | Status |
|------|--------|
| Tests | ✅ passing |
| Coverage | ✅ met target |
| Linting | ✅ No errors |
| Type Check | ✅ Clean |
| Security | ✅ No vulnerabilities |

### Progress Update
- **Before**: X/Y features (Z%)
- **After**: X+1/Y features (Z'%)
- **Next**: [next feature]

---
```

### Feature Completion Summary in EPCC_COMMIT.md

```markdown
## 5. Feature Completion Status

| Feature | E2E Status | Commit |
|---------|------------|--------|
| F001: User Authentication | ✅ VERIFIED | abc123 |
| F002: Task CRUD | 🔄 IN PROGRESS | - |

**Progress**: X/Y features (Z%)
```

### All Features Complete

When all features pass:

```markdown
## Project Complete!

All features verified and passing.

**Total**: N/N features (100%)
**Ready for**: Deployment / PR merge / Release

### Recommended Next Steps
1. Create release tag: `git tag v1.0.0`
2. Merge to main: `gh pr merge`
3. Deploy to production
```

## EPCC_COMMIT.md Output Template

```markdown
# Commit: [Feature Name]

**SHA**: [SHA] | **Branch**: [branch] | **Status**: [Committed/Pushed/PR]

## 1. Summary ([X files], [+Y -Z lines])
[1-2 sentences: what changed and why]

**Files**: [file:line] - [Purpose]
**Commit**: [type(scope): subject]

## 2. Validation (Tests [X%] | Quality [Clean/Findings] | Security [Clean/Findings])
**Tests**: [Status and coverage] - [X unit, Y integration]
**Quality**: [Linting/typing/formatting status]
**Security**: [Scan results or "Clean"]

## 3. Changes Detail
[Only for non-trivial commits]

**Behavioral changes**: [New functionality or modified behavior]
**Breaking changes**: [None / Describe]

## 4. Completion
**PR**: [URL if created, otherwise "Local commit only"]
**Next**: [Deploy / Merge / Review / Specific action needed]
```

**Depth heuristic**:
- **Trivial commit** (~100-200 tokens): Typo, formatting, simple fix
- **Standard commit** (~250-400 tokens): Feature, bug fix, refactor
- **Complex commit** (~500-700 tokens): Multi-file feature, architecture change
