# Exploration Report Templates

Output format and session logging for the EXPLORE phase.

## Report Structure - 5 Core Dimensions

**Forbidden patterns**:
- Filling template sections with "N/A" or "Not found" (omit irrelevant sections)
- Rigid 12-section structure for simple codebases (adapt to complexity)
- Documenting every file read (focus on patterns and decisions)
- Generic descriptions ("uses standard patterns") - be specific

**Document these dimensions** (depth varies by scope):

```markdown
# Exploration: [Area/Feature]

**Date**: [Date] | **Scope**: [Quick/Medium/Deep] | **Status**: ✅ Complete

## 1. Foundation (What exists)
**Tech stack**: [Language, framework, versions]
**Architecture**: [Pattern family - "Express REST API", "Django monolith", "React SPA + FastAPI"]
**Structure**: [Entry points, key directories with purpose]
**CLAUDE.md instructions**: [Critical requirements found]

## 2. Patterns (How it's built)
[Name pattern families, not every instance]

**Architectural patterns**:
- [Pattern name]: [Where used - file:line], [When to use]

**Testing patterns**:
- [Test framework + approach]: [Fixture patterns, mock strategies]
- **Coverage**: [X%], **Target**: [Y%]

**Error handling**: [Exit codes, stderr usage, agent compatibility]

## 3. Constraints (What limits decisions)
**Technical**: [Language versions, platform requirements]
**Quality**: [Test coverage targets, linting rules, type checking]
**Security**: [Auth patterns, input validation, known gaps]
**Operational**: [Deployment requirements, CI/CD, monitoring]

## 4. Reusability (What to leverage)
[Only if implementing similar feature]

**Similar implementations**: [file:line references]
**Reusable components**: [What can be copied vs adapted]
**Learnings**: [What worked, what to avoid]

## 5. Handoff (What's next)
**For PLAN**: [Key constraints, existing patterns to follow]
**For CODE**: [Tools/commands to use - test runner, linter, formatter]
**For COMMIT**: [Quality gates - coverage target, security checks]
**Gaps**: [Unclear areas requiring clarification]
```

**Adaptation heuristic**:
- **Quick scope** (~150-300 tokens): Foundation + critical constraints only
- **Medium scope** (~400-600 tokens): Foundation + patterns + constraints + handoff
- **Deep scope** (~800-1,500 tokens): All 5 dimensions with comprehensive detail

**Completeness heuristic**: Report is complete when you can answer:
- What tech stack and patterns must I follow?
- What quality gates must I pass?
- What can I reuse vs build new?
- What constraints limit my choices?

**Anti-patterns**:
- **Quick scope with 1,500 tokens** → Violates scope contract
- **Deep scope with 200 tokens** → Insufficient for complex codebase
- **Listing every file** → Name directory patterns instead
- **Generic "uses testing"** → Specify framework, fixture patterns, coverage

## Exploration Checklist

Before finalizing EPCC_EXPLORE.md:

**Context & Instructions**:
- [ ] Checked for CLAUDE.md in project root
- [ ] Checked for .claude/CLAUDE.md
- [ ] Checked for ~/.claude/CLAUDE.md
- [ ] Documented all project-specific requirements

**Structure & Technology**:
- [ ] Project structure fully mapped
- [ ] Entry points identified
- [ ] Technology stack documented
- [ ] All dependencies listed (external + internal)

**Patterns & Conventions**:
- [ ] Coding patterns documented (with examples)
- [ ] Naming conventions identified
- [ ] Architectural patterns mapped

**Code Quality**:
- [ ] Testing approach understood
- [ ] Test coverage assessed
- [ ] Code quality tools identified

**Constraints & Risks**:
- [ ] Technical constraints documented
- [ ] Security patterns reviewed
- [ ] Gaps and risks documented

**Similar Implementations**:
- [ ] Related code found and reviewed
- [ ] Reusable components identified

## Session Exit: Progress Logging

**Before completing exploration**, update the progress log:

### Update epcc-progress.md

If `epcc-progress.md` exists (long-running project):

```markdown
## Session: EXPLORE - [timestamp]
**Target**: [exploration area from ARGUMENTS]
**Thoroughness**: [quick|medium|deep]

### Areas Explored
- [area 1]: [brief finding]
- [area 2]: [brief finding]

### Key Patterns Found
- [pattern]: [location]

### Files Examined
[count] files across [count] directories

### Handoff Notes
- Ready for: [PLAN/CODE phase]
- Blockers: [any issues encountered]
- Follow-up: [anything to investigate further]

### Git State
- Commit: [current HEAD short hash]
- Branch: [current branch]
- Clean: [yes/no]
```

### Report Completion

```
✅ Exploration complete!

📄 **Output**: EPCC_EXPLORE.md
📊 **Coverage**: [X] files examined, [Y] patterns documented
📋 **Progress**: Session logged to epcc-progress.md

**Recommended next phase**: /epcc-plan [feature-based-on-exploration]
```

## Long-Running Project Integration

| Artifact | Role in EXPLORE |
|----------|-----------------|
| `epcc-features.json` | Read to understand feature context |
| `epcc-progress.md` | Read prior sessions, write completion log |
| `EPCC_EXPLORE.md` | Primary output document |

**Session continuity**: If context runs low during exploration:
1. Save current findings to EPCC_EXPLORE.md (partial)
2. Log session to epcc-progress.md with "Status: Partial"
3. Note remaining areas to explore
4. Next session can `/epcc-resume` then continue with `/epcc-explore --refresh`
