# Testing - Quality Gates Hooks

Pre-commit and code validation quality enforcement hooks for Claude Code operations.

## Event Mapping Caveats

| Original Event | New Mapping | Notes |
|---------------|-------------|-------|
| `PreCommit` | `PreToolUse` (matcher: `Bash`) | **Caveat:** Fires on ALL Bash tool invocations, not just git commits. Formatting checks (black, isort), linting (flake8), type checking (mypy), and test execution (pytest) will run before every Bash command. This is very expensive -- consider guarding with a commit-specific check or using a PreCommit hook runner externally. |
| `PreDeploy` | Removed | No equivalent event in Claude Code hooks spec. |
| `PreToolUse` | `PreToolUse` (kept) | Already compliant structure. Merged into the same event. |

## Removed Hooks (No Valid Equivalent)

### PreDeploy
- Security vulnerability scan via `security-reviewer` agent (`--strict --check-dependencies`)
- Dependency vulnerability check (`python -m safety check --json`)
- Security linting for Python (`bandit -r . -f json -o bandit-report.json`)
- Test coverage verification via `test-generator` agent (`--verify-coverage`)

## Customization

| Setting | Description |
|---------|-------------|
| `blocking` | Set to `false` on individual hooks to convert errors to warnings |
| `commands` | Adjust commands based on your project's tools and standards |
| `coverage` | Modify coverage threshold in the pytest `--cov-fail-under` flag (default: 80) |
