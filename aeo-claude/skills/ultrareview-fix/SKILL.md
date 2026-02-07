---
name: ultrareview-fix
description: |
  Systematically address all findings from a preceding ultrareview validation. Works through
  errors, alignment issues, gaps, and improvements by priority. Use after running ultrareview
  to fix identified issues in plans or code.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet
model: claude-opus-4-6
---

# Ultra-Fix Protocol

Address findings from a preceding ultrareview validation. Work through each finding systematically, implementing fixes with precision and completeness.

## Scope
$ARGUMENTS

If no scope specified, address all findings from the most recent ultrareview output.

<context_detection>
Determine what you're fixing:

**Plan Mode:** Ultrareview analyzed a plan/proposal. Findings reference architecture or design decisions. The plan file exists in `.claude/plans/` or similar.

**Implementation Mode:** Ultrareview analyzed code changes. Findings reference specific `file:line` locations. Code files exist and need modification.

Adapt your fix strategy accordingly.
</context_detection>

<investigate_before_fixing>
Before modifying any artifact:
1. Read the current state of files you intend to change
2. Understand the context around each finding
3. Verify the finding is still applicable
4. Plan fixes that don't introduce new issues
</investigate_before_fixing>

## Finding Categories

| Marker | Category | Priority |
|--------|----------|----------|
| CRITICAL | Blockers | Fix immediately |
| ERRORS (HIGH) | Bugs/Issues | Fix before proceeding |
| ERRORS (MEDIUM/LOW) | Issues | Address systematically |
| ALIGNMENT ISSUES | Pattern conflicts | Align with codebase conventions |
| MISSING | Gaps | Fill identified gaps |
| NEEDS VALIDATION | Uncertainties | Investigate, then fix or dismiss |
| IMPROVEMENTS | Enhancements | Implement beneficial changes |

Skip VALIDATED items — these confirm correct behavior.

If ultrareview reported no actionable findings, confirm the context is ready and exit.

## Fix Protocol

### Phase 1: Extract and Prioritize
Parse the ultrareview output and create a task list for tracking progress. Use TaskCreate for each finding.

### Phase 2: Plan-Mode Fixes

For plans/proposals:
- Locate the relevant section in the plan file
- Understand the original intent
- Craft a revision that addresses the finding while preserving intent
- After all fixes, verify the plan still flows logically

### Phase 3: Implementation-Mode Fixes

For code/configuration:
- Read target files completely before editing
- Design fixes that integrate cleanly
- Implement with minimal disruption to working code
- Verify fixes don't break existing functionality

### Phase 4: Verification

**For Plans:** Re-read the complete plan, verify internal consistency.

**For Implementations:** Run relevant tests, check for linting/type errors, verify integration.

## Output Format

### Summary Report

**RESOLVED**
- [List each addressed finding with brief description of fix]

**DEFERRED** (if any)
- [Finding]: [Reason for deferral]

**INTRODUCED CHANGES**
- [Any additional changes beyond the findings]

**VERIFICATION STATUS**
- Tests: [pass/fail/not run]
- Lint: [clean/issues]
- Integration: [verified/needs manual check]

## Execution Rules

1. One finding at a time: mark in_progress, fix, verify, mark completed
2. Atomic changes: each fix should be independently valid
3. No scope creep: only address items from ultrareview findings
4. Document decisions: if you skip or defer, explain why
5. Preserve intent: fixes solve problems without changing goals
6. Use provided code snippets from ultrareview as starting points
7. Verify file:line references before editing

<post_fix_workflow>
After completing all fixes, inform the user they can run ultrareview again to verify fixes and catch any issues introduced by the changes.
</post_fix_workflow>
