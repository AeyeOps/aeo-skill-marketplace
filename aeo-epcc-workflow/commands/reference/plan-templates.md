# Plan Output Templates & Feature Finalization

EPCC_PLAN.md output template and feature list finalization for the PLAN phase.

## EPCC_PLAN.md Output Template

```markdown
# Plan: [Feature Name]

**Created**: [Date] | **Effort**: [Xh] | **Complexity**: [Simple/Medium/Complex]

## 1. Objective
**Goal**: [What we're building - 1 sentence]
**Why**: [Problem solved - user value]
**Success**: [2-3 measurable criteria]

## 2. Approach
[High-level how - architectural pattern, tech stack choices with rationale]

**From EPCC_EXPLORE.md**: [Patterns to follow, constraints to respect] (if brownfield)
**From TECH_REQ.md**: [Architecture, tech stack, data models, integrations] (if available)
**From PRD.md**: [Product requirements informing technical approach] (if available)
**Integration points**: [External systems, existing components]
**Trade-offs**: [Decision made | Rationale | Alternatives considered]

## 3. Tasks
[Break into <4hr chunks, identify dependencies, assess risk]

**Phase N: [Name]** (~Xh)
1. [Task] (Xh) - [Brief description] | Deps: [None/Task X] | Risk: [L/M/H]

**Total**: ~Xh

## 4. Quality Strategy
**Tests**: [Unit/integration focus, edge cases, target coverage X%]
**Validation**: [Acceptance criteria from objective]

## 5. Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [High-likelihood or high-impact risks only] | H/M/L | [Specific action] |

**Assumptions**: [Critical assumptions that could invalidate plan]
**Out of scope**: [Deferred work]
```

**Depth heuristic**:
- **Simple** (~200-400 tokens): Add button, fix bug, refactor function
- **Medium** (~500-800 tokens): New feature, integration, significant refactor
- **Complex** (~1,000-1,500 tokens): System redesign, multi-component feature

**Anti-patterns**:
- **Simple feature with 1,200-token plan** → Violates proportionality
- **Complex system with 300-token plan** → Insufficient for CODE phase
- **Task "Implement authentication" (8h)** → Too large, break into <4hr chunks
- **No risk assessment** → Missing critical planning dimension
- **Generic "follow best practices"** → Specify which patterns from EPCC_EXPLORE.md

## Feature List Finalization

After creating EPCC_PLAN.md, finalize the feature list for multi-session progress tracking.

### Step 1: Check/Create Feature List

```bash
if [ -f "epcc-features.json" ]; then
    echo "Found epcc-features.json - validating and finalizing features..."
else
    echo "Creating epcc-features.json from EPCC_PLAN.md..."
fi
```

### Step 2: Validate Features Against Plan

If `epcc-features.json` exists, ensure all plan tasks map to features:

**Validation actions:**
- Add missing features for unmapped plan tasks
- Add plan tasks as subtasks to matching features
- Flag features without corresponding plan tasks for review

### Step 3: Add Implementation Order and Dependencies

Update `epcc-features.json` with implementation sequence:

```json
{
  "features": [
    {
      "id": "F001",
      "name": "User Authentication",
      "implementationOrder": 1,
      "dependencies": [],
      "blockedBy": [],
      "estimatedHours": 8,
      "planReference": "EPCC_PLAN.md#phase-1-foundation",
      "subtasks": [
        {"name": "Set up JWT integration", "status": "pending", "estimatedHours": 2},
        {"name": "Create user schema", "status": "pending", "estimatedHours": 1},
        {"name": "Implement login endpoint", "status": "pending", "estimatedHours": 2},
        {"name": "Add auth middleware", "status": "pending", "estimatedHours": 1.5},
        {"name": "Write tests", "status": "pending", "estimatedHours": 1.5}
      ]
    }
  ]
}
```

**Order rules:**
- P0 features before P1 before P2
- Dependencies must be implemented first
- Infrastructure features (INFRA-*) typically first
- Group related features for efficient context switching

### Step 4: Ensure Subtasks Are <4 Hours

Break down any subtasks larger than 4 hours.

### Step 5: Add Acceptance Criteria from Plan

Ensure each feature has testable acceptance criteria:
- Map from PRD success criteria
- Map from plan test strategy
- Must be testable (verifiable yes/no)
- Include both happy path and error cases

### Step 6: Update Progress Log

Append planning session to `epcc-progress.md`:

```markdown
---

## Session [N]: Planning Complete - [Date]

### Summary
Implementation plan created with task breakdown, dependencies, and risk assessment.

### Plan Overview
- **Total Phases**: [N]
- **Total Tasks**: [M]
- **Estimated Effort**: [X] hours
- **Critical Path**: [List of blocking dependencies]

### Implementation Order
1. INFRA-001: Database Setup (P0, no dependencies)
2. F001: User Authentication (P0, depends on INFRA-001)
3. F002: Task CRUD (P0, depends on F001)
...

### Next Session
Begin implementation with `/epcc-code F001` (or first feature in order)

---
```

### Step 7: Report Finalization Results

```markdown
## Plan Complete - Feature List Finalized

✅ **EPCC_PLAN.md** - Implementation strategy documented
✅ **epcc-features.json** - Feature list finalized:
   - [N] total features with implementation order
   - [M] total subtasks (<4hr each)
   - All dependencies mapped
   - Acceptance criteria defined
✅ **epcc-progress.md** - Planning session logged

### Implementation Sequence

| Order | Feature | Priority | Est. Hours | Dependencies |
|-------|---------|----------|------------|--------------|
| 1 | INFRA-001: Database | P0 | 4h | None |
| 2 | F001: User Auth | P0 | 8h | INFRA-001 |
| ... | ... | ... | ... | ... |

### Next Steps

**Ready to implement!** Start with:
/epcc-code F001  # Or first feature in implementation order
```

### Feature Immutability Enforcement

After plan approval:
- Feature definitions (name, description, acceptanceCriteria) are FROZEN
- Only `passes`, `status`, and `subtasks[].status` may be modified
- New features MAY be added but existing ones CANNOT be changed
- IT IS CATASTROPHIC TO REMOVE OR EDIT FEATURE DEFINITIONS
