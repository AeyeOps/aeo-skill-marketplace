# Slash Command Examples

## Table of Contents
- [Git Workflow Commands](#git-workflow-commands) - /commit, /branch, /pr
- [Code Review Commands](#code-review-commands) - /review, /explain
- [Documentation Commands](#documentation-commands) - /doc-function, /readme
- [Testing Commands](#testing-commands) - /test, /test-fix
- [Project Scaffolding](#project-scaffolding) - /new-component, /new-endpoint
- [Utility Commands](#utility-commands) - /todo, /deps, /clean

## Git Workflow Commands

### /commit - Conventional Commit
```markdown
---
description: Create a git commit with conventional commit format
argument-hint: [message]
allowed-tools: Bash(git:*)
---

Create a git commit for staged changes.

Use conventional commit format:
- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code restructuring
- test: adding tests
- chore: maintenance

Message: $ARGUMENTS
```

### /branch - Start New Feature
```markdown
---
description: Create and switch to a new feature branch
argument-hint: <branch-name>
allowed-tools: Bash(git:*)
---

1. Check git status is clean
2. Pull latest from main
3. Create branch: feature/$ARGUMENTS
4. Switch to new branch
```

### /pr - Create Pull Request
```markdown
---
description: Create a pull request with summary
argument-hint: [title]
allowed-tools: Bash(git:*), Bash(gh:*)
---

Create a pull request:
1. Push current branch to origin
2. Generate summary from commits since main
3. Create PR with title: $ARGUMENTS (or generate from branch name)
4. Include test plan section
```

## Code Review Commands

### /review - Security and Quality Review
```markdown
---
description: Review code for security, performance, and style
argument-hint: [file-or-directory]
allowed-tools: Read, Glob, Grep
---

Review $ARGUMENTS for:

1. **Security**: injection, XSS, secrets, auth issues
2. **Performance**: N+1 queries, unnecessary loops, memory leaks
3. **Style**: naming, complexity, dead code
4. **Errors**: missing error handling, edge cases

Output format:
- [CRITICAL] Security issues
- [HIGH] Performance problems
- [MEDIUM] Code quality
- [LOW] Style suggestions
```

### /explain - Code Explanation
```markdown
---
description: Explain code in simple terms
argument-hint: <file-path>
---

Explain @$1 in simple terms:

1. **Purpose**: What does this code do?
2. **Key components**: Main functions/classes
3. **Data flow**: How data moves through
4. **Dependencies**: External requirements
5. **Usage**: How to use this code
```

## Documentation Commands

### /doc-function - Document a Function
```markdown
---
description: Generate documentation for a function
argument-hint: <file:function-name>
allowed-tools: Read, Edit
---

Add comprehensive documentation to the function specified.

Include:
- Brief description
- Parameters with types
- Return value
- Exceptions/errors
- Usage example

Target: $ARGUMENTS
```

### /readme - Generate README
```markdown
---
description: Generate or update project README
allowed-tools: Read, Glob, Write
---

Generate a README.md based on:

1. Scan project structure
2. Read package.json/pyproject.toml/Cargo.toml
3. Identify main entry points
4. Extract existing documentation

Sections:
- Project title and description
- Installation
- Quick start
- Usage examples
- Configuration
- Contributing
```

## Testing Commands

### /test - Generate Tests
```markdown
---
description: Generate tests for a file or function
argument-hint: <file-path> [function-name]
allowed-tools: Read, Write
---

Generate tests for $ARGUMENTS:

1. Analyze the code structure
2. Identify edge cases
3. Create test cases for:
   - Happy path
   - Error conditions
   - Boundary values
   - Null/empty inputs

Match existing test framework in project.
```

### /test-fix - Fix Failing Test
```markdown
---
description: Analyze and fix a failing test
argument-hint: <test-file:test-name>
allowed-tools: Read, Edit, Bash(pytest:*), Bash(npm test:*)
---

Fix failing test: $ARGUMENTS

1. Run the test to see failure
2. Analyze error message
3. Check if test or implementation is wrong
4. Fix the appropriate code
5. Verify test passes
```

## Project Scaffolding

### /new-component - React Component
```markdown
---
description: Create a new React component with tests
argument-hint: <ComponentName>
allowed-tools: Write, Read
---

Create React component: $1

Files to create:
- src/components/$1/$1.tsx
- src/components/$1/$1.test.tsx
- src/components/$1/index.ts

Include:
- TypeScript types
- Props interface
- Basic styling hook
- Unit test skeleton
```

### /new-endpoint - API Endpoint
```markdown
---
description: Create a new API endpoint
argument-hint: <method> <path>
allowed-tools: Write, Read, Edit
---

Create API endpoint: $1 $2

Include:
- Route handler
- Request validation
- Error handling
- Response typing
- Basic test
```

## Utility Commands

### /todo - Find TODOs
```markdown
---
description: Find and list all TODO comments
allowed-tools: Grep
---

Find all TODO, FIXME, HACK, XXX comments in codebase.

Group by:
1. Priority (FIXME > TODO > HACK)
2. File location
3. Age (from git blame if available)
```

### /deps - Check Dependencies
```markdown
---
description: Check for outdated or vulnerable dependencies
allowed-tools: Bash(npm:*), Bash(pip:*), Bash(cargo:*), Read
---

Check project dependencies:

1. Identify package manager
2. List outdated packages
3. Check for security vulnerabilities
4. Suggest updates with breaking change warnings
```

### /clean - Clean Build Artifacts
```markdown
---
description: Remove build artifacts and caches
allowed-tools: Bash(rm:*), Bash(find:*)
---

Clean project:
- node_modules (prompt first)
- __pycache__
- .pytest_cache
- dist/build folders
- .next/.nuxt caches
- Coverage reports

Confirm before deleting large directories.
```
