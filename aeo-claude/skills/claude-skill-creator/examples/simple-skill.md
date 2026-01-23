# Simple Skill Example (Single File)

A basic skill with all content in SKILL.md.

## Use Case
Generate commit messages by analyzing git diffs.

## File Structure
```
commit-helper/
└── SKILL.md
```

## Complete SKILL.md

```markdown
---
name: Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when committing code changes or creating pull requests.
---

# Git Commit Helper

Analyzes git diffs to generate clear, conventional commit messages.

## How to Use

1. Stage your changes: `git add .`
2. Ask Claude to generate a commit message
3. Claude will run `git diff --staged` and analyze the changes
4. Review and use the suggested message

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build process or auxiliary tool changes

## Examples

**Example 1: Feature addition**
```
feat(auth): add JWT token refresh

Implement automatic token refresh when access token expires.
Adds RefreshTokenService and updates AuthInterceptor.

Related: #123
```

**Example 2: Bug fix**
```
fix(api): handle null response from user endpoint

Add null check before accessing user.profile to prevent
NullPointerException when profile data is missing.

Fixes: #456
```

## Analysis Process

When generating messages, Claude:
1. Examines the `git diff --staged` output
2. Identifies the primary change type (feat, fix, etc.)
3. Determines affected scope (module/component)
4. Writes clear subject line (< 50 chars)
5. Adds body explaining "why" not "what"
6. Includes footer with issue references if applicable
```

## Key Points

- **Single file**: All instructions in SKILL.md
- **Clear trigger**: "committing code" and "pull requests" in description
- **Concrete examples**: Shows expected format and types
- **Process outline**: Explains how Claude will analyze diffs
