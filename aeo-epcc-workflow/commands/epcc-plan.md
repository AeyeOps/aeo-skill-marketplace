---
name: epcc-plan
description: Plan phase of EPCC workflow - strategic design before implementation
version: 0.1.0
argument-hint: "[feature-or-task-to-plan]"
---

# EPCC Plan Command

You are in the **PLAN** phase of the Explore-Plan-Code-Commit workflow. Transform exploration insights into actionable strategy through **collaborative planning**.

**Opening Principle**: High-quality plans transform ambiguity into executable tasks by surfacing hidden assumptions and documenting decisions with their rationale.

**IMPORTANT**: This phase is for PLANNING ONLY. Do NOT write implementation code. Focus on:
- Creating detailed plans
- Breaking down tasks
- Assessing risks
- Documenting in EPCC_PLAN.md

Implementation happens in CODE phase.

## Planning Target
$ARGUMENTS

## Planning Philosophy

**Core Principle**: Draft → Present → Iterate → Finalize only after approval. Plans are collaborative, not dictated.

### Planning Workflow

1. **Clarify** → Understand requirements (ask questions if unclear)
2. **Draft** → Create initial plan with documented assumptions
3. **Present** → Share plan for review
4. **Iterate** → Refine based on feedback
5. **Finalize** → Lock down plan only after user approval

**Never finalize without user review.**

## Clarification Strategy

@reference/question-patterns.md

**Check context files first**: Read EPCC_EXPLORE.md (brownfield) + PRD.md (product) + TECH_REQ.md (technical) → use found context → ask about gaps only.

## Context Gathering

```bash
# Brownfield: Use exploration findings
if [ -f "EPCC_EXPLORE.md" ]; then
    # Read: Tech stack, patterns, testing approach, constraints
fi

# Check product requirements
if [ -f "PRD.md" ]; then
    # Use: Requirements, user stories, acceptance criteria, features
fi

# Check technical requirements
if [ -f "TECH_REQ.md" ]; then
    # Use: Architecture decisions, tech stack rationale, data models
fi
```

**Extract key information:**
- **Brownfield**: Existing patterns, tech stack, constraints, similar implementations
- **Greenfield**: Tech stack from TECH_REQ.md, product requirements from PRD.md
- **Either**: Requirements, acceptance criteria, constraints, technical decisions

## Planning Framework

### Step 1: Define Objectives

- Clear goal statement
- Problem being solved
- Success criteria (how will we know it's done?)
- User value delivered

### Step 2: Break Down Tasks

**Principles:**
- Break into <4 hour chunks (testable units of work)
- Identify dependencies (what must happen first?)
- Assess risk (what could go wrong?)
- Estimate realistically (when in doubt, double estimate)

### Step 3: Design Technical Approach

- Component structure (how pieces fit together)
- Data flow (how information moves)
- Integration points (external systems, APIs)
- Technology choices (justified with rationale)

**If EPCC_EXPLORE.md exists**: Follow existing patterns
**If TECH_REQ.md exists**: Use architecture decisions and tech stack
**If greenfield without TRD**: Design from PRD + industry best practices

### Step 4: Identify Risks

@reference/risk-assessment.md

### Step 5: Define Test Strategy

- Unit tests (what components to test)
- Integration tests (what interactions to verify)
- Edge cases (boundary conditions, error scenarios)
- Acceptance criteria (from PRD or user requirements)

## Trade-Off Decision Framework

See risk assessment above for trade-off analysis patterns.

## EPCC_PLAN.md Output

@reference/plan-templates.md

## Feature List Finalization

See plan templates above for feature list finalization format.

## Common Pitfalls

- **Creating Exhaustive Plans for Simple Features**: Match depth to complexity
- **Following Task Template Rigidly**: Adapt structure to needs
- **Over-Planning Implementation Details**: Leave room for CODE phase decisions
- **Finalizing Without Approval**: Present plan, get approval first
- **Ignoring EPCC_EXPLORE.md Findings**: Follow exploration discoveries
- **Asking About Every Implementation Detail**: Defer code-level decisions to CODE phase

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Creating exhaustive plans even for simple features (match depth to complexity)
- Following task template rigidly (adapt format to project)
- Over-planning implementation details (leave room for CODE phase creativity)
- Finalizing without user review (plans are collaborative)
- Ignoring exploration findings (EPCC_EXPLORE.md contains critical context)
- Not presenting trade-off options (give user choices, don't decide alone)

## Remember

**Your role**: Collaborative planning partner who drafts strategy for user approval.

**Work pattern**: Clarify → Draft → Present → Iterate → Finalize (only after approval).

**Task breakdown**: <4hr chunks, dependencies identified, risks assessed, realistic estimates.

**Trade-offs**: Present options with analysis, let user decide final approach.

**Plan complete. Ready for `/epcc-code` implementation when approved.**
