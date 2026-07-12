---
name: design-architecture
description: Orchestrate architecture design and documentation by delegating to simple-architect and simple-architecture-documenter
version: 0.1.0
argument-hint: "[design-brief]"
---

# Design Architecture Command

You orchestrate a complete architecture workflow for a project by coordinating two specialist agents: one that makes the architectural decisions and one that documents them.

## Design Brief
$ARGUMENTS

Parse the brief to establish:
- **Project type**: what is being built (web app, API, chat, e-commerce, CLI, etc.)
- **Team size**: solo, small, medium, or large — this drives the monolith-vs-microservices decision
- **Constraints**: scale expectations, timeline, existing stack, compliance needs

If no brief is provided, ask for a one-to-two sentence description of the project, its expected team size, and any hard constraints before proceeding.

## Workflow

### Step 1: Architecture decisions — delegate to @simple-architect
Hand the design brief to @simple-architect and request:
- Architecture pattern recommendation (monolith, modular monolith, or microservices) with reasoning tied to team size
- Technology stack selection with trade-offs
- Database and caching strategy
- Security approach appropriate to the project
- API design patterns
- Growth plan for the next 12-18 months
- Architecture Decision Records (ADRs) capturing the key choices

### Step 2: Documentation — delegate to @simple-architecture-documenter
Pass the decisions from Step 1 to @simple-architecture-documenter and request:
- System Context diagram (C4 Level 1) in Mermaid
- Container diagram (C4 Level 2) in Mermaid
- 4-section ADRs (Status, Context, Decision, Consequences) for each major decision
- A system overview readable by a new team member
- An API documentation template with example endpoints

Keep the steps in order: the documenter works from the architect's decisions, not in isolation.

### Step 3: Synthesize
Combine both agents' output into a single response:
- Lead with the recommended pattern and stack in one or two sentences
- Follow with the C4 diagrams and ADRs
- Close with the growth plan and concrete next steps

## Output Format

**Recommendation**: [pattern] with [stack summary]

### Architecture Decisions
- Pattern and reasoning
- Technology stack with trade-offs
- Data and caching strategy
- Security approach
- API design

### Documentation
- System Context diagram (C4 Level 1)
- Container diagram (C4 Level 2)
- ADRs for each major decision
- System overview

### Growth Plan & Next Steps
- Scaling considerations for the next 12-18 months
- Recommended first implementation milestones

## Examples

```bash
# Basic usage
/design-architecture "todo app for a small team"

# With a client requirement
/design-architecture "e-commerce platform for a 5-person startup with a mobile client"

# With scale and team hints
/design-architecture "real-time chat with 1000+ concurrent users, small team"
```

## Notes

- @simple-architect favors practical, incrementally scalable choices — start simple and grow.
- @simple-architecture-documenter limits diagrams to C4 Levels 1 and 2 to keep documentation approachable.
- Match the depth of the output to the brief: a small internal tool does not need the same rigor as a customer-facing platform.
