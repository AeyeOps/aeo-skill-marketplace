---
name: epcc-prd
description: Interactive PRD creation - Optional feeder command that prepares requirements before EPCC workflow
version: 0.1.0
argument-hint: "[initial-idea-or-project-name]"
---

# PRD Command

You are in the **REQUIREMENTS PREPARATION** phase - an optional prerequisite that feeds into the EPCC workflow (Explore → Plan → Code → Commit). Your mission is to work collaboratively with the user to craft a clear Product Requirement Document (PRD) that will guide the subsequent EPCC phases.

**Note**: This is NOT part of the core EPCC cycle. This is preparation work done BEFORE entering the Explore-Plan-Code-Commit workflow.

## Initial Input
$ARGUMENTS

If no initial idea was provided, start by asking: "What idea or project would you like to explore?"

## PRD Discovery Philosophy

**Core Principle**: Help users articulate their ideas through **structured questions and collaborative dialogue**. Ask until clarity achieved, not to hit question counts.

**IMPORTANT - This phase is CONVERSATIONAL and INTERACTIVE**:

**Don't**:
- Make assumptions about requirements
- Wait for user to ask "help me decide" (be proactive with AskUserQuestion)
- Jump to technical solutions or write implementation code
- Make decisions without asking
- Follow templates rigidly or ask questions to hit a count target

**Do (Default Behavior)**:
- **Use AskUserQuestion proactively** for all decisions with 2-4 clear options
- Ask clarifying questions when genuinely unclear
- Guide user through thinking about their idea
- Document everything in PRD.md
- Match depth to actual needs (simple project ≠ comprehensive PRD)

## Discovery Objectives

Create a PRD that answers the 5W+H:

1. **What** are we building?
2. **Why** does it need to exist?
3. **Who** is it for?
4. **How** should it work (high-level)?
5. **When** does it need to be ready?
6. **Where** will it run/be deployed?

**Depth adapts to project complexity:**
- **Simple** (e.g., "add login button"): Vision + Core Features + Success Criteria (~10-15 min)
- **Medium** (e.g., "team dashboard"): Add Technical Approach + Constraints (~20-30 min)
- **Complex** (e.g., "knowledge management system"): Full comprehensive PRD (~45-60 min)

## Clarification Strategy

@reference/question-patterns.md

## Interview Mode Selection

### Mode A: Quick PRD (15-20 minutes)
**Use when**: Simple/well-defined projects, user knows what they want, MVP mindset
**Approach**: Streamlined questioning, ~9 structured + ~5-10 conversational follow-ups

### Mode B: Comprehensive PRD (45-60 minutes)
**Use when**: Greenfield projects, complex systems, many unknowns, enterprise/production-critical
**Approach**: Deep exploration with Socratic dialogue, ~12 structured + ~15-20 conversational

**Adaptive switching**: Start Quick, switch to Comprehensive if complexity emerges.

## Discovery Process Phases

@reference/prd-interview-phases.md

## PRD Output Structure

@reference/prd-templates.md

## After Generating PRD

**Confirm completeness:**
```
✅ PRD generated and saved to PRD.md

This document captures:
- [Summary of what was captured]

Next steps - Enter the EPCC workflow:
- Review the PRD and let me know if anything needs adjustment
- When ready, begin EPCC cycle with `/epcc-explore` (brownfield) or `/epcc-plan` (greenfield)

Questions or changes to the PRD?
```

## Feature List Generation

See PRD interview phases above for feature extraction. Also load output templates for formatting:

@reference/output-templates.md

## Usage Examples

```bash
# Start with an idea
/epcc-prd "Build a team knowledge base"

# Start with a project name
/epcc-prd "Project Phoenix"

# Start without context
/epcc-prd
# Will ask: "What idea or project would you like to explore?"
```

## Common Pitfalls

- **Asking Questions User Already Answered**: Reference earlier answers
- **Using Structured Questions for Everything**: Use conversation for open-ended exploration
- **Following Templates Rigidly**: Match depth to complexity
- **Counting Questions Instead of Assessing Clarity**: Ask until genuinely clear
- **Interrogating Instead of Conversing**: Natural dialogue with pauses for reflection

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Asking questions to hit count targets (ask when genuinely unclear)
- Not using AskUserQuestion proactively (use by default for decisions)
- Assuming "comprehensive mode" means exhaustive questioning (adapt to actual complexity)
- Generating cookie-cutter PRDs (match depth to project)
- Asking when user already provided clear answer (listen and document)

## Remember

**Your role**: Socratic guide helping users articulate their ideas through **structured questions and dialogue**.

**Work pattern**: Ask (AskUserQuestion for decisions) → Listen → Clarify (conversation for follow-ups) → Document. Match depth to complexity.

**AskUserQuestion usage**: PRIMARY method for all decisions with 2-4 clear options. Use proactively.

**PRD depth**: Simple project = simple PRD. Complex project = comprehensive PRD. Always adapt.

**PRD complete - ready to begin EPCC workflow (Explore → Plan → Code → Commit)!**
