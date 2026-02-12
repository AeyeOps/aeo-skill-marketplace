---
name: trd
description: Technical Requirements Document generation through interactive interview
version: 0.1.0
argument-hint: "[initial-technical-context-or-project-name]"
---

# Technical Requirements Document (TRD) Generator

Generate comprehensive **TECH_REQ.md** through collaborative technical discovery. This command transforms architectural ambiguity into clear technical decisions that feed directly into the EPCC plan phase.

## What This Command Does

**Purpose**: Create Technical Requirements Document (TECH_REQ.md) that defines:
- Architecture patterns and component structure
- Technology stack with justified choices
- Data models and storage strategies
- Integration points and API design
- Security and compliance approach
- Performance and scalability plan

**Output**: `TECH_REQ.md` file

**Position in workflow**:
- **Optional input**: PRD.md (product requirements, if available)
- **This command**: Generate TECH_REQ.md through technical interview
- **Feeds into**: `/epcc-plan` (strategic implementation planning)

## TRD Discovery Philosophy

**Opening Principle**: Discover technical requirements through **structured questions and collaborative dialogue**, not assumptions.

**Do (Default Behavior)**:
- **Use AskUserQuestion proactively** for all technical decisions with 2-4 clear options
- Read PRD.md if available to understand product context
- Ask about architecture, stack, infrastructure aligned with product needs
- Present technology options with tradeoffs (not recommendations as facts)
- Match technical depth to project complexity
- Document rationale for every technical decision

**Don't**:
- Assume tech stack without asking ("I'll use React and PostgreSQL" → Ask first!)
- Make technology recommendations without presenting alternatives and tradeoffs
- Skip reading PRD.md if it exists
- Ask about implementation details (belongs in CODE phase)
- Force comprehensive TRD for simple projects

**Remember**: You're discovering technical requirements, not implementing. Focus on WHAT technologies and WHY, defer HOW to CODE phase.

## Discovery Objectives

**What we're discovering**:

1. **Architecture** (Patterns, service boundaries, component structure)
2. **Technology Stack** (Languages, frameworks, tools, libraries)
3. **Data Models** (Storage, schemas, relationships)
4. **Integrations** (APIs, third-party services, authentication)
5. **Security** (Auth, compliance, data protection)
6. **Performance** (Scalability, caching, optimization)

**Depth adaptation**:
- **Simple project** → Focus on stack + data + basic security
- **Medium project** → Add integrations + performance + detailed security
- **Complex project** → Comprehensive architecture + compliance + high-scale design

## Clarification Strategy

@reference/question-patterns.md

## Interview Mode Selection

Present mode choice to user with clear time/depth tradeoffs:

### Quick TRD
**When**: Simple architecture, well-known tech stack, minimal integrations, clear technical path
**Coverage**: Core stack decisions, basic security, simple data model
**Question count**: ~8-12 structured questions focused on essentials

### Comprehensive TRD
**When**: Complex architecture, multiple technology decisions, many integrations, compliance requirements
**Coverage**: Deep architecture exploration across all 6 discovery phases
**Question count**: ~25-35 structured questions + conversational deep-dives

**Adapt mode during interview**: If complexity emerges, suggest switching to comprehensive.

## Discovery Phases

@reference/trd-interview-phases.md

## Adaptive Interview Heuristics

@reference/trd-tech-evaluation.md

## TECH_REQ.md Output Structure

@reference/trd-templates.md

## After Generating TECH_REQ.md

**Confirm completeness:**
```
✅ TECH_REQ.md generated and saved

This document captures:
- Architecture: [Pattern chosen]
- Tech Stack: [Key technologies with rationale]
- Data Model: [Storage approach]
- Security: [Auth/compliance approach]
- Scalability: [Scale strategy]
[+ PRD Alignment if PRD.md existed]

Next steps - Enter the EPCC workflow:
- Review the TRD and let me know if anything needs adjustment
- When ready, begin EPCC cycle with `/epcc-explore` (brownfield) or `/epcc-plan` (greenfield)

Questions or changes to the TRD?
```

## Technical Feature Enrichment

See adaptive interview heuristics above for tech evaluation and feature enrichment patterns.

## Usage Examples

```bash
# With project context
/trd "Real-time collaboration platform"

# After creating PRD
/trd  # Will find and read PRD.md automatically

# Without context
/trd
# Will ask: "What technical project would you like to define requirements for?"
```

## Common Pitfalls

- **Assuming Tech Stack Without Asking**: Don't prescribe → Ask using AskUserQuestion
- **Making Technology Recommendations as Facts**: Present options with tradeoffs, let user decide
- **Following Template Rigidly**: Match depth to technical complexity
- **Including Implementation Details**: Focus on technology choices and architecture patterns
- **Ignoring PRD.md When Present**: Read PRD.md first, reference context
- **Using Conversation When AskUserQuestion Fits**: Structured questions for decisions with 2-4 options

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Assuming standard tech stack (ask about stack choices, don't assume)
- Following template rigidly (simple project ≠ comprehensive TRD)
- Making technology recommendations (present options with tradeoffs)
- Skipping PRD.md (always check and read if exists)
- Including implementation details (architecture and stack, not classes and functions)
- Not justifying technology choices (every choice needs rationale vs alternatives)
- Not researching unfamiliar technologies (use WebSearch for benchmarks)

## Remember

**Your role**: Technical discovery partner who autonomously gathers context and interviews collaboratively using structured questions.

**Work pattern**: Read PRD.md → Explore codebase (if brownfield) → Research options (WebSearch) → Ask (AskUserQuestion for decisions) → Clarify → Document technical requirements with research insights.

**AskUserQuestion usage**: PRIMARY method for all technical decisions with 2-4 options. Conversation for follow-ups.

**TRD depth**: Simple project = simple TRD. Complex project = comprehensive TRD. Always adapt to technical complexity.

**Technology choices**: Research with WebSearch → Present options with tradeoffs → Let user decide → Document rationale.

**TECH_REQ.md complete - ready to feed into `/epcc-plan` for implementation planning!**
