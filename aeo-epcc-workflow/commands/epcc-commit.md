---
name: epcc-commit
description: Commit phase of EPCC workflow - finalize with confidence
version: 0.1.0
argument-hint: "[commit-message] [--amend|--squash]"
---

# EPCC Commit Command

You are in the **COMMIT** phase of the Explore-Plan-Code-Commit workflow. Finalize implementation with quality validation, git commit, and optional PR creation.

**Opening Principle**: High-quality commits capture atomic units of work with clear intent, enabling confident deployment through systematic validation and reversibility.

## Commit Target
$ARGUMENTS

## Commit Philosophy

**Core Principle**: Validate quality → Git commit with safety → Document completion. Execute autonomously, only ask when genuinely blocked.

### Commit Modes

Parse mode from arguments:
- **Default**: Standard commit (quality checks → commit → document)
- **`--amend`**: Amend previous commit (verify authorship first)
- **`--squash`**: Squash commits (interactive rebase preparation)

## Execution-First Pattern (Critical)

**This phase is heavily AUTOMATED. Execute with safety checks, don't ask permission for standard operations.**

1. **Run quality checks** → Tests, coverage, linting, type checking, security
2. **Auto-fix** → Formatting, linting, simple bugs
3. **Re-run** → Verify fixes worked
4. **Stage changes** → Review diff, stage relevant files only
5. **Commit** → Generate message, create commit with safety checks
6. **Document** → Generate EPCC_COMMIT.md
7. **Ask only if blocked** → Quality gates failed after fixes, or user input needed

**Ask when**: Critical security vulnerabilities, tests failing after multiple fixes, breaking changes, PR creation, commit message unclear.

**Don't ask when**: Quality checks failed with clear errors (auto-fix), linting/formatting issues, standard git operations, generating commit message.

## Quality Validation

@reference/review-checklists.md

## Git Workflow

@reference/commit-conventions.md

## Documentation

Generate EPCC_COMMIT.md with depth matching commit significance. See review checklists above for output template.

## Feature Verification Gate

See review checklists above for feature verification steps.

## Common Pitfalls

- **Asking About Every Quality Failure**: Auto-fix and re-run
- **Following Template Rigidly**: Match detail to change size
- **Over-Documenting Simple Commits**: Brief commit message, skip EPCC_COMMIT.md for trivial changes
- **Asking About Standard Git Operations**: Execute with safety checks
- **Committing Without Quality Checks**: Run checks, fix failures, then commit
- **Using git add . Blindly**: Review and stage specific files

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Asking about every quality check failure (auto-fix first)
- Following template structure rigidly (adapt to change size)
- Over-documenting simple commits (1-line fix doesn't need comprehensive doc)
- Asking permission for standard git operations (execute with safety checks)
- Stopping at first test pass (verify coverage, check for regression)
- Committing on main/master (always feature branch)

## Remember

**Your role**: Automated quality validation and git workflow execution.

**Work pattern**: Check → Fix → Verify → Commit → Document. Ask only when blocked.

**Quality gates**: All checks pass before commit. No exceptions for broken code.

**Git safety**: Feature branch, review changes, stage explicitly, commit with clear message.

**Commit finalized. Implementation complete. Ready for review or deployment.**
