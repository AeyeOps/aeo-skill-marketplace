---
name: release-notes
version: 0.1.0
description: Generate formatted release notes from git history, grouping commits by type
argument-hint: "<version-or-tag-range>"
---

# Release Notes Generator

Generate release notes by analyzing git history. Use `$ARGUMENTS` to determine the version or tag range.

## Step 1: Determine Range

Parse `$ARGUMENTS` to identify the commit range:

```
Argument formats:
  "v1.2.3"          → changes from previous tag to v1.2.3
  "v1.1.0..v1.2.0"  → changes between two tags
  "v1.2.3 v1.3.0"   → changes between two tags
  (empty)            → changes from last tag to HEAD
```

### Resolve the Range

Use Bash to determine the commit range:

```bash
# If no arguments, find the last two tags
git describe --tags --abbrev=0          # latest tag
git describe --tags --abbrev=0 HEAD~1   # previous tag

# If single version, find previous tag
git describe --tags --abbrev=0 $VERSION^

# List commits in range
git log --oneline --no-merges $FROM..$TO
```

## Step 2: Analyze Commits

Read the git log for the determined range:

```bash
# Full commit details
git log --format="%H|%s|%an|%ad" --no-merges $FROM..$TO

# Include file change stats
git log --stat --no-merges $FROM..$TO
```

### Classify Each Commit

Group commits by type using conventional commit prefixes or content analysis:

```markdown
Categories:
  feat:     → Added (new features)
  fix:      → Fixed (bug fixes)
  docs:     → Documentation
  refactor: → Changed (refactoring, improvements)
  perf:     → Performance
  test:     → Testing
  build:    → Build System
  ci:       → CI/CD
  chore:    → Maintenance
  security: → Security
  breaking: → Breaking Changes (BREAKING CHANGE in body or ! after type)
```

For commits without conventional prefixes, analyze the message:
- "add", "new", "introduce", "implement" → Added
- "fix", "resolve", "correct", "patch" → Fixed
- "update", "improve", "enhance", "refactor" → Changed
- "remove", "delete", "drop", "deprecate" → Removed
- "security", "vulnerability", "CVE" → Security

## Step 3: Extract Key Information

For each commit, extract:
- **Summary**: Clean, human-readable description
- **Scope**: Component or area affected (from commit scope or file paths)
- **Breaking changes**: Any backwards-incompatible changes
- **Related issues**: GitHub issue/PR references (#123)
- **Contributors**: Unique authors

### Detect Breaking Changes

Search for breaking change indicators:
```bash
# Check commit bodies for BREAKING CHANGE
git log --format="%H %s%n%b" $FROM..$TO | grep -B1 "BREAKING CHANGE"

# Check for ! in conventional commits (feat!: ...)
git log --oneline $FROM..$TO | grep -E "^[a-f0-9]+ \w+!:"
```

## Step 4: Generate Statistics

```bash
# Commit count
git rev-list --count $FROM..$TO

# Contributors
git log --format="%an" $FROM..$TO | sort -u

# Files changed
git diff --stat $FROM..$TO

# Lines changed
git diff --shortstat $FROM..$TO

# Most changed files
git diff --stat $FROM..$TO | sort -t'|' -k2 -rn | head -10
```

## Step 5: Format Release Notes

Generate the release notes in Keep a Changelog format:

```markdown
# Release Notes — [Version]

**Release date**: [YYYY-MM-DD]
**Tag**: [tag name]
**Commits**: [count] commits by [N] contributors

## Highlights

[2-3 sentence summary of the most significant changes in this release.
Focus on user-facing impact and key improvements.]

## Breaking Changes

> **Attention**: This release includes breaking changes. Review before upgrading.

- **[scope]**: [description of breaking change and migration path]

## Added
- [Feature description] ([#PR](link))
- [Feature description] ([#PR](link))

## Changed
- [Change description] ([#PR](link))

## Fixed
- [Bug fix description] ([#PR](link))

## Removed
- [Removed item description] ([#PR](link))

## Security
- [Security fix description] ([#PR](link))

## Performance
- [Performance improvement description] ([#PR](link))

## Documentation
- [Documentation change description]

## Internal
- [Build/CI/test changes — summarize, don't list individually]

---

## Contributors

Thanks to the following contributors for this release:
- @contributor1
- @contributor2

## Full Changelog

[FROM...TO](https://github.com/OWNER/REPO/compare/FROM...TO)
```

## Step 6: Write Output

Write the release notes to a file:

```
Default output: RELEASE_NOTES.md (in repository root)
Alternative: docs/releases/[version].md
```

### Formatting Rules

- Use imperative mood: "Add feature" not "Added feature"
- Start each entry with a verb: Add, Fix, Remove, Update, Improve
- Include PR/issue references where available
- Keep entries to one line when possible
- Group related small changes into single entries
- Omit merge commits and version bump commits
- Omit entries that only change whitespace or formatting
- Sort entries within each category by scope, then alphabetically

### Quality Checks

Before finalizing, verify:
- [ ] All breaking changes are prominently listed
- [ ] No duplicate entries
- [ ] No merge commits included
- [ ] PR/issue links are correct
- [ ] Contributor list is complete
- [ ] Version and date are accurate
- [ ] Highlights section summarizes key changes

## Usage Examples

```bash
# Generate notes for latest tag
/release-notes

# Generate notes for specific version
/release-notes v2.1.0

# Generate notes for a range
/release-notes v1.0.0..v2.0.0
```
