---
name: ultrareview
description: |
  Deep validation protocol that examines preceding context for errors, unvalidated assumptions,
  alignment issues, gaps, and improvement opportunities. Produces a machine-parseable summary.
  Use when validating plans, code changes, configurations, or any work product before proceeding.
allowed-tools: Read, Glob, Grep, Bash(git status *), Bash(git diff *), Bash(find *)
model: claude-opus-4-6
---

# Ultra-Validation Protocol

Evaluate each validation dimension systematically. Question every assumption. Cross-reference against actual codebase artifacts.

## Focus Area
$ARGUMENTS

If no focus specified, validate the entire preceding context (plan, code changes, discussion, or proposal).

## Validation Steps

### Step 0: Deliverable Existence Check

<deliverable_check>
Based on the focus area, identify:
1. What concrete deliverable was requested? (code, config, documentation, etc.)
2. Does this deliverable exist?

If the requested deliverable does not exist, this is automatically a critical finding.
Do not proceed to validate planning artifacts as a substitute.
Status is NEEDS_ACTION until the deliverable exists.
</deliverable_check>

<context_detection>
Identify what you're validating:
- **Plan/Proposal**: Architecture design, implementation approach, technical spec
- **Code Changes**: Diff, new files, refactored code, PR
- **Discussion**: Requirements gathering, debugging session, design conversation
- **Configuration**: Environment setup, infrastructure, deployment config

Adapt your validation approach accordingly.
</context_detection>

<investigate_before_answering>
Read relevant files before making claims. If uncertain, state what you need to investigate.
</investigate_before_answering>

### Step 1: Assumption Inventory
List every assumption in the preceding context. For each:
- **VALIDATED**: Confirmed by examining actual code/config/docs (cite file:line)
- **UNVALIDATED**: Not yet verified against codebase
- **CONTRADICTED**: Evidence suggests assumption is wrong

### Step 2: Error & Risk Scan
Examine for issues appropriate to the context type:

**For Code:**
- Logic errors, null handling, type mismatches
- Missing error handlers, unhandled promises
- Race conditions, async timing issues
- Security vulnerabilities, exposed secrets
- Performance issues, N+1 queries, memory leaks

**For Plans/Proposals:**
- Unstated dependencies or prerequisites
- Scope gaps or undefined edge cases
- Integration risks with existing systems

**For Configuration:**
- Missing environment variables
- Security misconfigurations
- Incompatible version constraints

### Step 3: Omission Detection
Identify what's missing:
- Incomplete implementations or undefined behaviors
- Missing error handling for edge cases
- Absent tests for critical paths
- Undocumented assumptions

### Step 4: Codebase Alignment
Compare against existing patterns:
- Does approach match existing code structure and conventions?
- Are we violating established patterns?
- Will changes integrate cleanly?
- Are we introducing inconsistencies?

### Step 5: Enhancement Opportunities
- Can we reduce complexity?
- Are there safer, faster, or cleaner approaches?
- Can we consolidate duplicate logic?

## Output Format

**CRITICAL** (Resolve before proceeding)
- Risk: [why critical]
- Action: [specific next step]

**ERRORS FOUND** (Severity: HIGH/MEDIUM/LOW)
- Location: [file:line, section, or concept]
- Impact: [what breaks or fails]
- Fix: [concrete solution]

**ALIGNMENT ISSUES** (Conflicts with codebase or conventions)
- Current: [what exists]
- Proposed: [what conflicts]
- Resolution: [how to align]

**MISSING** (Gaps needing attention)

**IMPROVEMENTS** (Better alternatives with expected benefit)

**VALIDATED** (Confirmed with citations)

**NEEDS VALIDATION** (Requires investigation)

## Machine-Parseable Summary

Conclude with this exact summary block (parsed by automation hooks):

```
<ultrareview_summary>
status: [PASS|NEEDS_ACTION]
critical: [count]
errors: [count]
alignment: [count]
missing: [count]
improvements: [count]
needs_validation: [count]
validated: [count]
</ultrareview_summary>
```

Rules:
- Requirements stated in the focus area are required, not optional
- `status: PASS` only if critical=0 AND errors=0 AND alignment=0 AND missing=0 AND needs_validation=0
- `status: NEEDS_ACTION` if any actionable findings exist
- Count each distinct finding, not each bullet point
- The summary block appears at the very end of your response
