# PRD Discovery Phases & Feature Generation

Five interview phases for product requirements discovery, plus feature list generation.

## Phase 1: Understanding the Vision

**Objective**: Understand big picture and core problem

**Context**: Research with WebSearch/WebFetch("[product-type] best practices 2025") if unfamiliar domain.

**Use AskUserQuestion proactively for**:
- Project type: "Greenfield project vs Feature addition vs Refactor vs Bug fix?"
- User scope: "Personal project vs Small team vs Department/Org vs Public users?"
- Urgency: "Critical/ASAP vs Important/Planned vs Nice-to-have vs Exploratory?"

**Conversational follow-ups:**
- What problem are you trying to solve?
- Who would use this? What does success look like for them?
- Can you give concrete example of how someone would use this?
- What would happen if this didn't exist?

**Adapt based on answers**: Public-facing → security questions. Greenfield → architecture questions. Critical urgency → scope reduction focus.

## Phase 2: Core Features

**Objective**: Define what the product must do

**Context**: Research with WebSearch/WebFetch("[feature-type] UX patterns 2025") if unfamiliar patterns.

**Use AskUserQuestion proactively for**:
- MVP approach: "Bare Minimum vs Core+Polish vs Feature Complete vs Phased rollout?"
- Priority balance: "Speed First vs Balanced vs Quality First vs MVP then Harden?"

**Conversational follow-ups:**
- What's the ONE thing this absolutely must do?
- Walk me through typical user's journey - start to finish
- What makes this genuinely useful vs just a nice demo?
- Which features are must-haves for launch vs nice-to-haves?

**Prioritization framework:**
- P0 (Must Have): Can't launch without
- P1 (Should Have): Important but can wait
- P2 (Nice to Have): Future enhancements

Help user categorize: "Is this essential for launch, or could we add it later?"

## Phase 3: Technical Direction

**Objective**: Establish high-level technical approach

**Context**: Research with WebSearch/WebFetch("user personas for [target-audience]") if unfamiliar users.

**Use AskUserQuestion proactively for**:
- Environment: "Local only vs Cloud-hosted vs On-Premise vs Hybrid?"
- Data storage: "Relational DB vs Document store vs File storage vs In-Memory?" [multiSelect]
- Authentication: "No auth vs Basic (username/password) vs OAuth/SSO vs API Keys?"
- Integration needs: "Standalone vs API integrations vs Database connections vs File sync?" [multiSelect]

**Conversational follow-ups:**
- Real-time or batch processing?
- How many users? (scale expectations)
- Existing technologies to use or avoid?
- Any specific tech preferences or constraints?

**For simple projects**: Focus on core tech choices only
**For complex projects**: Deep dive on architecture, integrations, security

## Phase 4: Constraints & Scope

**Objective**: Define realistic boundaries

**Context**: Research with WebSearch/WebFetch("[industry] compliance requirements") if regulated domain.

**Use AskUserQuestion proactively for**:
- Timeline: "ASAP (days) vs 1-2 weeks vs 1-2 months vs 3+ months vs Exploratory?"
- Key constraints: "Budget vs Time vs Team Size vs Tech Skills vs Compliance?" [multiSelect]

**Conversational follow-ups:**
- Budget constraints? (estimate infrastructure costs if relevant)
- Security or compliance requirements? (HIPAA, SOC2, GDPR)
- What are you comfortable maintaining long-term?
- What is explicitly OUT of scope for first version?
- Minimum viable version if we had to cut features?

**Calibrate expectations**: "Building [X] typically takes [Y] time. Does that work?"

## Phase 5: Success Metrics

**Objective**: Define what "done" looks like

**Context**: Research with WebSearch/WebFetch("[product-type] KPIs and metrics 2025").

**Use AskUserQuestion proactively for**:
- Success metrics: "User adoption vs Performance/speed vs Cost savings vs User satisfaction vs Feature completion?" [multiSelect]

**Conversational follow-ups:**
- How will you know this is working well?
- What would make you consider this a success?
- How will people actually use this day-to-day?
- What specific criteria must be met to consider this complete?

## Adaptive Discovery Heuristics

**Weight questions toward high-impact unknowns**:

- **Public-facing projects** → Emphasize security, authentication, scale, compliance
- **Greenfield projects** → Emphasize architecture, technology choices, patterns
- **Brownfield projects** → Emphasize integration, existing patterns, backward compatibility
- **Critical urgency** → Focus on scope reduction: "What's absolute minimum to unblock you?"
- **Exploratory projects** → Encourage experimentation, discuss multiple approaches

## Feature List Generation

After creating PRD.md, automatically generate progress tracking files for multi-session work.

### Generate epcc-features.json

Parse the PRD "Core Features" section and create structured feature tracking.

**See**: @reference/output-templates.md for epcc-features.json structure and feature extraction rules.

### Initialize epcc-progress.md

**See**: @reference/output-templates.md for epcc-progress.md initialization pattern.

### Create Initial Git Commit

If in a git repository:

```bash
git add PRD.md epcc-features.json epcc-progress.md
git commit -m "feat: Initialize project from PRD

- PRD.md: Product requirements with [N] features
- epcc-features.json: Feature tracking initialized
- epcc-progress.md: Progress log started

Project: [Project Name]
Complexity: [Simple/Medium/Complex]"
```

### Report Generation Results

```markdown
## Progress Tracking Initialized

✅ **PRD.md** - Product requirements ([complexity] complexity)
✅ **epcc-features.json** - Feature list with [N] features:
   - P0 (Must Have): [X] features
   - P1 (Should Have): [Y] features
   - P2 (Nice to Have): [Z] features
✅ **epcc-progress.md** - Progress log initialized
[✅ **Git commit** - Initial project state committed]

### Next Steps

**For Technical Requirements**: `/trd` - Add technical specifications and architecture
**For Greenfield Projects**: `/epcc-plan` - Create implementation plan
**For Brownfield Projects**: `/epcc-explore` - Understand existing codebase first
**To check progress later**: `/epcc-resume` - Quick orientation and status
```

### Adaptive Feature Depth

Match feature list detail to project complexity:

| Complexity | Feature Count | Acceptance Criteria | Subtasks |
|------------|---------------|---------------------|----------|
| Simple | 3-10 | 2-3 per feature | None initially |
| Medium | 10-30 | 3-5 per feature | None initially |
| Complex | 30-100+ | 5-10+ per feature | TRD/Plan will add |
