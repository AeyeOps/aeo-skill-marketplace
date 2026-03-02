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

### Step 0.5: Source Reading

<source_reading>
Before evaluating, identify and read every primary source file in scope.

When the focus area references a command template that calls a script, that script is a
primary source — read it, because the template's description of what the script does may
be incomplete or outdated. The same applies to configs, schemas, and any file referenced
by another file you've read.

Follow reference chains, because a script that calls another script makes both relevant
to your findings: if file A calls file B which reads file C, all three are in scope.

Build a file inventory as you go. Any finding that references a file you haven't read
belongs in NEEDS_VALIDATION, not ERRORS — because you're reasoning from description
rather than source.
</source_reading>

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
- Location: [file:line, section, or concept]
- Evidence: [direct observation — what you read in the source that confirms this]
- Risk: [why critical]
- Action: [specific next step]

If your evidence is an inference about behavior in a file you haven't read, this belongs
in NEEDS_VALIDATION until you read that file.

**ERRORS FOUND** (Severity: HIGH/MEDIUM/LOW)
- Location: [file:line, section, or concept]
- Evidence: [direct observation — what you read in the source that confirms this]
- Impact: [what breaks or fails]
- Fix: [concrete solution]

If your evidence is an inference about behavior in a file you haven't read, this belongs
in NEEDS_VALIDATION until you read that file.

**ALIGNMENT ISSUES** (Conflicts with codebase or conventions)
- Current: [what exists]
- Proposed: [what conflicts]
- Resolution: [how to align]

**MISSING** (Gaps needing attention)

**IMPROVEMENTS** (Better alternatives with expected benefit)

**VALIDATED** (Confirmed with citations)

**NEEDS VALIDATION** (Default category for unverified concerns)

Use this for any concern where:
- You identified a potential issue but haven't read the implementation files to confirm
- The evidence comes from documentation/comments rather than source code
- You're reasoning about behavior across components without verifying the integration point

Promote to ERRORS only after reading the relevant source and confirming the problem exists.

## Artifact Inventory

List every file you read during this review, because this allows the reader to verify
your coverage and identify files you may have missed.

- `path/to/file.py` — relevant to: [what aspect of the review it informed]

## Scorecard

After all findings sections, output this human-readable scorecard table:

```
## Scorecard

| Category           | Count | Action needed? |
|--------------------|-------|----------------|
| Critical           |     X | YES            |
| Errors             |     X | YES            |
| Alignment issues   |     X | YES            |
| Missing            |     X | YES            |
| Needs validation   |     X | YES            |
| Improvements       |     X | no             |
| Validated          |     X | no             |
| **Status**         |       | **PASS / NEEDS_ACTION** |
```

Rules for Action needed column: Critical, Errors, Alignment, Missing, Needs validation = YES when count > 0. Improvements and Validated are always "no".

## Machine-Parseable Summary

Immediately after the scorecard, output this exact summary block (parsed by automation hooks):

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
- The scorecard and summary block appear at the very end of your response, in that order
