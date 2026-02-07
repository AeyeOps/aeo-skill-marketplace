# Slash Command Patterns

## Table of Contents
- [Variable Patterns](#variable-patterns) - $ARGUMENTS, positional, defaults
- [File Inclusion Patterns](#file-inclusion-patterns) - @file, dynamic, glob
- [Bash Execution Patterns](#bash-execution-patterns) - `!command`, multiple, conditional
- [Tool Restriction Patterns](#tool-restriction-patterns) - allowed-tools configurations
- [Multi-Step Workflow Patterns](#multi-step-workflow-patterns) - sequential, conditional, iterative
- [Output Format Patterns](#output-format-patterns) - reports, checklists, JSON
- [Model Override Patterns](#model-override-patterns) - haiku, sonnet selection
- [Invocation Control Patterns](#invocation-control-patterns) - manual-only, hints
- [Composition Patterns](#composition-patterns) - base/specialized, chains
- [Error Handling Patterns](#error-handling-patterns) - graceful degradation, validation

## Variable Patterns

### All Arguments as String
```markdown
Process: $ARGUMENTS
```
`/cmd foo bar baz` -> `$ARGUMENTS = "foo bar baz"`

### Positional Arguments
```markdown
File: $1
Function: $2
Options: $3
```
`/cmd src/main.py calculate --verbose` -> `$1="src/main.py"`, `$2="calculate"`, `$3="--verbose"`

### Default Values (via prompt)
```markdown
Review $ARGUMENTS

If no arguments provided, review all staged changes.
```

## File Inclusion Patterns

### Single File Reference
```markdown
Analyze the code in @src/utils/helpers.js
```

### Multiple File References
```markdown
Compare @src/old-version.js with @src/new-version.js
```

### Dynamic File Reference
```markdown
Review the file: @$1
```
Usage: `/review src/main.py`

### Glob Pattern Description
```markdown
Find all TypeScript files matching: $ARGUMENTS
Then review each for type safety.
```

## Bash Execution Patterns

### Simple Command Output
```markdown
Current git status:
`!git status`

Based on this, suggest next steps.
```

### Multiple Commands
```markdown
Project state:
- Git: `!git status --short`
- Branch: `!git branch --show-current`
- Recent: `!git log --oneline -5`
```

### Conditional Execution
```markdown
Check test results:
`!npm test 2>&1 || echo "Tests failed"`

If tests failed, analyze and suggest fixes.
```

## Tool Restriction Patterns

### Read-Only Analysis
```yaml
allowed-tools: Read, Glob, Grep
```

### Git Operations Only
```yaml
allowed-tools: Bash(git *)
```

### Specific Commands
```yaml
allowed-tools: Bash(npm test *), Bash(npm run build *)
```

### Multiple Tool Types
```yaml
allowed-tools: Read, Edit, Bash(git *), Bash(npm *)
```

## Multi-Step Workflow Patterns

### Sequential Steps
```markdown
1. First, check current state: `!git status`
2. Then analyze changes in @$1
3. Finally, suggest improvements
```

### Conditional Workflow
```markdown
Review @$1

If file is:
- TypeScript: Check types, interfaces, null safety
- Python: Check types, docstrings, imports
- SQL: Check injection risks, performance
```

### Iterative Process
```markdown
For each file in $ARGUMENTS:
1. Read the file
2. Identify issues
3. Suggest fixes
4. Move to next file

Summarize all findings at end.
```

## Output Format Patterns

### Structured Report
```markdown
Output as:

## Summary
[1-2 sentence overview]

## Findings
- [CRITICAL] ...
- [HIGH] ...
- [MEDIUM] ...

## Recommendations
1. ...
2. ...
```

### Checklist Format
```markdown
Output as checklist:

- [ ] Item 1
- [ ] Item 2
- [x] Completed item
```

### JSON Output
```markdown
Output results as JSON:
{
  "status": "success|failure",
  "findings": [...],
  "suggestions": [...]
}
```

## Model Override Patterns

### Fast Model for Simple Tasks
```yaml
model: claude-3-5-haiku-20241022
```

### Full Model for Complex Analysis
```yaml
model: claude-sonnet-4-20250514
```

## Invocation Control Patterns

### Manual Only (No Auto-Discovery)
```yaml
disable-model-invocation: true
```
Use for destructive operations or commands with side effects.

### With Argument Hints
```yaml
argument-hint: <file> [--fix] [--verbose]
```
Shows users expected format in autocomplete.

## Composition Patterns

### Base + Specialized Commands
Create a base `/review` then specialized versions:
- `/review-security` - Security focus
- `/review-perf` - Performance focus
- `/review-types` - Type safety focus

### Workflow Chains
Document that commands work together:
```markdown
Workflow: /branch -> /commit -> /pr

This command is step 2 of 3.
Previous: /branch created the feature branch
Next: /pr will create the pull request
```

## Error Handling Patterns

### Graceful Degradation
```markdown
Try to analyze @$1

If file doesn't exist, list similar files and ask for clarification.
If file is binary, report that and skip.
```

### Validation First
```markdown
Before proceeding:
1. Verify $1 is a valid file path
2. Verify file exists
3. Verify file is readable

If any check fails, explain what's wrong.
```
