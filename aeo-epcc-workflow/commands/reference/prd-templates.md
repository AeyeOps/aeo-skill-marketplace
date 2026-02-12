# PRD Output Templates

Three complexity-matched PRD variants plus the full comprehensive template.

## Simple PRD (~300-500 tokens)

**When**: Single feature, clear problem, 1-2 user types, minimal unknowns

```markdown
# PRD: [Project Name]

**Created**: [Date] | **Complexity**: Simple

## Problem & Users
**Problem**: [What we're solving - 1-2 sentences]
**Users**: [Who needs this and what pain they have]

## Solution
**Core Features** (P0):
1. [Feature]: [What + Why essential]
2. [Feature]: [What + Why essential]

**Success**: [2-3 testable criteria]
**Out of Scope**: [What we're NOT doing]

## Next Steps
[Greenfield: /epcc-plan | Brownfield: /epcc-explore]
```

## Medium PRD (~600-1,000 tokens)

**When**: Multi-feature product, some technical complexity, 2-3 user types, defined constraints

Add to simple structure:
- **User Journeys**: Primary flow with key scenarios
- **Technical Approach**: High-level architecture, tech stack rationale
- **Constraints**: Timeline, budget, technical limitations
- **Feature Priority**: P0 (Must) / P1 (Should) / P2 (Nice to have)

## Complex PRD (~1,200-2,000 tokens)

**When**: Platform/system, multiple integrations, diverse user types, compliance needs, significant risks

Add to medium structure:
- **User Personas**: Detailed user types with needs/pain points
- **Detailed Journeys**: Multiple flows, edge cases, error scenarios
- **Technical Architecture**: Component structure, integration points, data flow
- **Security/Compliance**: Requirements, approach, validation
- **Risks & Mitigation**: What could go wrong, how to address
- **Dependencies**: External/internal, blockers
- **Phased Rollout**: If applicable

**Depth heuristic**: PRD complexity should match project complexity. Don't write comprehensive PRD for simple feature.

## Full PRD Template (Adapt to Complexity)

```markdown
# Product Requirement Document: [Project Name]

**Created**: [Date]
**Version**: 1.0
**Status**: Draft
**Complexity**: [Simple/Medium/Complex]

---

## Executive Summary
[2-3 sentence overview]

## Research Insights (if applicable)

**Product/UX** (from WebSearch/WebFetch):
- **[Best practice/pattern]**: [Key finding from UX research, user research, or domain standards]

**Documentation Identified**:
- **[Doc type]**: Priority [H/M/L] - [Why needed]

## Problem Statement
[What problem we're solving and why it matters]

## Target Users
### Primary Users
- Who they are
- What they need
- Current pain points

[Secondary users if applicable]

## Goals & Success Criteria
### Product Goals
1. [Specific, measurable goal]
2. [Specific, measurable goal]

### Success Metrics
- [Metric]: [Target]
- [Metric]: [Target]

### Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]

## Core Features

### Must Have (P0 - MVP)
1. **[Feature Name]**
   - What it does
   - Why essential
   - Estimated effort: [High/Medium/Low]

### Should Have (P1)
[If applicable]

### Nice to Have (P2)
[If applicable]

## User Journeys
### Primary Journey: [Name]
1. User starts at [point]
2. User does [action]
3. System responds with [response]
4. User achieves [outcome]

[Additional journeys for medium/complex projects]

## Technical Approach
[Include for Medium/Complex projects]

### Architecture Overview
[High-level description]

### Technology Stack
- [Component]: [Technology] - [Rationale]

### Integration Points
[If any]

### Data & Security
[Storage approach, authentication method]

## Constraints
[Include for Medium/Complex projects]

### Timeline
- Target: [Date]
- Key milestones: [If applicable]

### Budget
[If discussed]

### Technical Constraints
[If any]

### Security/Compliance
[If applicable]

## Out of Scope
[What we're explicitly NOT doing]

## Risks
[For Complex projects]

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [How to address] |

## Open Questions
[Anything still uncertain]

## Dependencies
[External or internal dependencies if any]

## Next Steps

This PRD feeds into the EPCC workflow. Choose your entry point:

**For Greenfield Projects** (new codebase):
1. Review & approve this PRD
2. Run `/epcc-plan` to create implementation plan (can skip Explore)
3. Begin development with `/epcc-code`
4. Finalize with `/epcc-commit`

**For Brownfield Projects** (existing codebase):
1. Review & approve this PRD
2. Run `/epcc-explore` to understand existing codebase and patterns
3. Run `/epcc-plan` to create implementation plan based on exploration
4. Begin development with `/epcc-code`
5. Finalize with `/epcc-commit`

**Note**: The core EPCC workflow is: **Explore → Plan → Code → Commit**. This PRD is the optional preparation step before that cycle begins.

---

**End of PRD**
```

**Completeness heuristic**: PRD is ready when you can answer:
- What problem are we solving and why does it matter?
- Who are the users and what do they need?
- What are the must-have features (P0) for MVP?
- How will we measure success?
- What are we explicitly NOT doing?
- What's the entry point into EPCC workflow (explore or plan)?

**Anti-patterns**:
- **Simple feature with 1,500-token PRD** → Violates complexity matching (use Simple template)
- **Complex platform with 400-token PRD** → Insufficient detail (missing risks, architecture, journeys)
- **Technical implementation in PRD** → "Use PostgreSQL with connection pooling" belongs in PLAN phase
- **Every section filled with "TBD"** → If unknown, make it an open question or omit
- **No success criteria** → Can't validate if solution works without measurable criteria
