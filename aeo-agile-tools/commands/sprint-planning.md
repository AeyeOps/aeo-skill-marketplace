---
name: sprint-planning
version: 0.1.0
description: Interactive sprint planning facilitator that guides backlog refinement, capacity planning, and sprint goal setting
argument-hint: "[sprint-number]"
---

# Sprint Planning Facilitator

You are facilitating a sprint planning session. Follow this structured process to help the team plan an effective sprint.

## Step 1: Gather Sprint Context

Use AskUserQuestion to collect essential planning inputs:

```
Questions to ask:
1. What sprint number is this? (use $ARGUMENTS if provided)
2. What is the sprint duration? (1 week / 2 weeks / 3 weeks)
3. How many team members are available this sprint?
4. Are there any known absences, holidays, or reduced capacity?
5. Were there any carryover items from the previous sprint?
```

## Step 2: Review Previous Sprint

Before planning forward, look back:

### Velocity Check
- What was the team's velocity in the last 3 sprints?
- Is there a trend (increasing, decreasing, stable)?
- Were previous sprint goals met?

### Carryover Assessment
If there are carryover items:
- Why were they not completed?
- Are they still the highest priority?
- Do estimates need adjustment?

## Step 3: Backlog Refinement

Delegate to the **product-owner** agent to ensure the backlog is ready:

```
Use the Task tool to spawn the product-owner agent:
- Review top-of-backlog items for completeness
- Verify each item has clear acceptance criteria
- Confirm priority ordering reflects current business needs
- Check that items meet the Definition of Ready
```

### Definition of Ready Checklist
For each candidate story, verify:
- [ ] User story is clearly written (As a... I want... So that...)
- [ ] Acceptance criteria are defined (Given/When/Then)
- [ ] Dependencies are identified and resolved (or planned)
- [ ] UX mockups attached (if applicable)
- [ ] Story is estimated by the team
- [ ] Story fits within a single sprint

## Step 4: Capacity Planning

### Calculate Available Capacity

```
Team Capacity Formula:
  Available days = team_members x sprint_days
  Subtract: PTO, holidays, meetings, support rotation
  Focus factor: multiply by 0.7 (typical) or 0.6 (new team)
  Capacity in points = available_days x focus_factor x avg_points_per_day
```

### Capacity Worksheet

Use AskUserQuestion to gather:
```
For each team member:
- Name
- Available days this sprint (after PTO/holidays)
- Any planned support/on-call duties
- Percentage allocated to sprint work vs maintenance
```

### Historical Baseline
```
Last 3 sprint velocities: [V1, V2, V3]
Average velocity: (V1 + V2 + V3) / 3
Recommended commitment: average velocity x 0.9 (safety margin)
```

## Step 5: Sprint Goal Setting

Delegate to the **scrum-master** agent for facilitation guidance:

```
Use the Task tool to spawn the scrum-master agent:
- Facilitate sprint goal definition
- Ensure the goal is outcome-oriented, not task-oriented
- Verify the goal is achievable within sprint capacity
- Confirm team alignment and commitment
```

### Sprint Goal Template
```markdown
Sprint [number] Goal:
  "By the end of this sprint, [who] will be able to [outcome]
   so that [business value]."

Success Criteria:
  - [ ] Criterion 1 (measurable)
  - [ ] Criterion 2 (measurable)
  - [ ] Criterion 3 (measurable)

Key Results:
  - Metric A moves from X to Y
  - Feature B is usable by persona C
```

### Goal Quality Checklist
- [ ] Focused: one primary theme, not a grab-bag
- [ ] Measurable: clear criteria for "done"
- [ ] Achievable: within sprint capacity
- [ ] Relevant: ties to product vision and roadmap
- [ ] Time-bound: completable within the sprint

## Step 6: Story Selection and Commitment

### Selection Process
1. Start with must-have items that support the sprint goal
2. Add supporting stories that enable the goal
3. Fill remaining capacity with high-priority independent items
4. Leave 10-15% buffer for unexpected work

### For Each Selected Story

Use AskUserQuestion to confirm with the team:
```
Story: [title]
Points: [estimate]
Dependencies: [list]
Assigned to: [team member or unassigned]

Does the team commit to this story? (Yes / Yes with concerns / No)
```

### Commitment Summary
```markdown
Sprint [N] Commitment:
  Total stories: [count]
  Total points: [sum]
  Capacity used: [percentage]
  Buffer remaining: [percentage]

  Stories by priority:
  1. [Must] Story A - [X] points
  2. [Must] Story B - [Y] points
  3. [Should] Story C - [Z] points
  ...
```

## Step 7: Risk and Dependency Mapping

### Dependency Matrix
```markdown
| Story | Depends On | External? | Risk Level | Mitigation |
|-------|-----------|-----------|------------|------------|
| A     | API team  | Yes       | High       | Early sync |
| B     | Story A   | No        | Medium     | Parallel start |
```

### Risk Register
For each identified risk:
```markdown
Risk: [description]
Probability: High / Medium / Low
Impact: High / Medium / Low
Mitigation: [action plan]
Owner: [who will monitor]
```

## Step 8: Sprint Plan Output

Generate the final sprint plan document:

```markdown
# Sprint [N] Plan

## Sprint Goal
[Goal statement]

## Team Capacity
- Available: [X] person-days
- Committed: [Y] story points
- Buffer: [Z]%

## Sprint Backlog

### Must Have (Sprint Goal)
| # | Story | Points | Owner | Dependencies |
|---|-------|--------|-------|-------------|
| 1 | ...   | ...    | ...   | ...         |

### Should Have
| # | Story | Points | Owner | Dependencies |
|---|-------|--------|-------|-------------|

### Could Have (Stretch)
| # | Story | Points | Owner | Dependencies |
|---|-------|--------|-------|-------------|

## Risks and Mitigations
[Risk register entries]

## Key Dates
- Sprint start: [date]
- Mid-sprint check: [date]
- Sprint review: [date]
- Sprint retrospective: [date]

## Team Agreements
- Daily standup: [time]
- Core hours: [range]
- Communication channel: [channel]
```

## Step 9: Final Confirmation

Use AskUserQuestion for final team commitment:
```
The sprint plan is ready. Please confirm:
1. Does the team commit to the sprint goal?
2. Is the sprint backlog achievable?
3. Are all risks acknowledged?
4. Any final concerns before we begin?
```

## Facilitation Tips

- **Timebox**: Keep planning to 2 hours per sprint week (2-week sprint = 4 hours max)
- **Whole team**: Everyone contributes to estimates and commitment
- **Focus on goal**: Stories support the goal; avoid unrelated work when possible
- **Break it down**: Stories larger than 8 points should be split
- **Speak up**: Better to raise concerns now than mid-sprint
- **Document**: Write the plan down so everyone references the same source
