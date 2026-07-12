# Shared Output Templates

Common document structure patterns used across PRD and TRD generation.

## Complexity-Matched Output

**Core principle**: Match document depth to project complexity. Simple project = simple document.

### Depth Heuristic

| Complexity | Token Target | When to Use |
|------------|-------------|-------------|
| Simple | ~300-600 | Single feature, clear problem, 1-2 user types, standard stack |
| Medium | ~600-1,200 | Multi-feature, moderate complexity, several integrations |
| Complex | ~1,200-2,500 | Platform/system, compliance needs, distributed, high scale |

### Complexity Detection Heuristics

- User story count
- Number of user types/personas
- Integration points mentioned
- Technical constraints listed
- Compliance requirements
- Scale expectations (users, data volume)

## Completeness Heuristic Pattern

Documents are ready when you can answer all checkpoint questions:
- What problem are we solving and why?
- Who are the users and what do they need?
- What are the must-have features/decisions?
- How will we measure success?
- What are we explicitly NOT doing?
- What's the entry point into the next phase?

## Anti-Pattern Checks

**Forbidden patterns across all output documents**:
- Comprehensive document for simple ideas (CRUD app ≠ 15-page doc)
- Filling sections with "TBD" or "To be determined" (omit unknowns, make them open questions)
- Technical implementation details in requirements docs (leave for CODE phase)
- Rigid template sections for minimal projects
- No success criteria or rationale

## Next Steps Pattern

```markdown
## Next Steps

This document feeds into the EPCC workflow. Choose your entry point:

**For Greenfield Projects** (new codebase):
1. Review & approve this document
2. Run `/epcc-plan` to create implementation plan (can skip Explore)
3. Begin development with `/epcc-code`
4. Finalize with `/epcc-commit`

**For Brownfield Projects** (existing codebase):
1. Review & approve this document
2. Run `/epcc-explore` to understand existing codebase and patterns
3. Run `/epcc-plan` to create implementation plan based on exploration
4. Begin development with `/epcc-code`
5. Finalize with `/epcc-commit`

**Note**: The core EPCC workflow is: **Explore → Plan → Code → Commit**.
```

## Feature List Generation Pattern

After creating a requirements document, generate progress tracking if applicable:

### epcc-features.json Structure

```json
{
  "_warning": "Feature definitions are IMMUTABLE. Only 'passes' and 'status' fields may be modified.",
  "project": "[Project Name]",
  "created": "[ISO timestamp]",
  "lastUpdated": "[ISO timestamp]",
  "source": "[Source document]",
  "features": [
    {
      "id": "F001",
      "name": "[Feature Name]",
      "description": "[Feature description]",
      "priority": "P0",
      "status": "pending",
      "passes": false,
      "acceptanceCriteria": ["[Testable criterion]"],
      "subtasks": [],
      "source": "[Document]#[section]"
    }
  ],
  "metrics": {
    "total": 0,
    "verified": 0,
    "inProgress": 0,
    "pending": 0,
    "percentComplete": 0
  }
}
```

### Feature Extraction Rules

- Extract all P0 (Must Have) features as high-priority
- Extract all P1 (Should Have) as medium-priority
- Extract all P2 (Nice to Have) as low-priority
- Generate acceptance criteria from success criteria and feature descriptions
- Feature count adapts to project complexity:
  - **Simple**: 3-10 features, 2-3 acceptance criteria each
  - **Medium**: 10-30 features, 3-5 acceptance criteria each
  - **Complex**: 30-100+ features, 5-10+ acceptance criteria each

### epcc-progress.md Initialization

```markdown
# EPCC Progress Log

**Project**: [Project Name]
**Started**: [Date]
**Progress**: 0/[N] features (0%)

---

## Session 0: [Document] Created - [Date]

### Summary
[Document type] created from initial exploration.

### Artifacts Created
- [Document].md - Requirements
- epcc-features.json - Feature tracking ([N] features)
- epcc-progress.md - This progress log

### Feature Summary
- **P0 (Must Have)**: [X] features
- **P1 (Should Have)**: [Y] features
- **P2 (Nice to Have)**: [Z] features

### Next Session
Run next EPCC phase command.

---
```

### Feature Immutability Notice

After creation, feature definitions are IMMUTABLE:
- Only `passes`, `status`, and `subtasks[].status` may be modified
- New features may be ADDED but existing ones cannot be changed
- IT IS CATASTROPHIC TO REMOVE OR EDIT FEATURE DEFINITIONS
