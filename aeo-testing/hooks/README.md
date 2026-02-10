# Testing - Quality Gates Hooks

Pre-commit and code validation quality enforcement hooks for Claude Code operations.

**Hooks are disabled by default.** The configuration below runs a full CI pipeline (black, isort, flake8, mypy, pytest + coverage) before every Bash command — far too heavy for general use. Copy the relevant sections into your `hooks.json` selectively, or add a guard script that checks whether the command is `git commit` before running the suite.

## Reference Configuration

To enable, copy desired entries into the `hooks` object in `hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "black --check .", "timeout": 30000 },
          { "type": "command", "command": "isort --check-only .", "timeout": 30000 },
          { "type": "command", "command": "flake8 . --max-line-length=88", "timeout": 30000 },
          { "type": "command", "command": "mypy . --ignore-missing-imports", "timeout": 60000 },
          { "type": "command", "command": "pytest tests/ --quiet", "timeout": 120000 },
          { "type": "command", "command": "pytest --cov=. --cov-report=term-missing --cov-fail-under=80", "timeout": 120000 },
          { "type": "command", "command": "echo 'Command review: ${command}' | tee -a .claude/command-log.txt", "timeout": 5000 }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "test -f ${file_path} && echo 'Overwriting existing file: ${file_path}'", "timeout": 5000 }
        ]
      }
    ]
  }
}
```

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

## Blocking Behavior Warning

Claude Code's hooks spec does not support a `blocking` field — **all hooks block by default** if the command exits non-zero. To make a hook advisory-only (non-blocking), append `|| true` to the command string so it always exits 0.

## Customization

| Setting | Description |
|---------|-------------|
| `commands` | Adjust commands based on your project's tools and standards |
| `coverage` | Modify coverage threshold in the pytest `--cov-fail-under` flag (default: 80) |
