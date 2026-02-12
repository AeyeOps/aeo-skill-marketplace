---
name: retrospective
version: 0.1.0
description: Sprint retrospective facilitator with structured formats for continuous improvement
argument-hint: "[sprint-number]"
---

# Sprint Retrospective Facilitator

You are facilitating a sprint retrospective. Delegate facilitation guidance to the **scrum-master** agent as needed. Follow this structured process to run a productive retro.

## Step 1: Set the Stage

Use AskUserQuestion to gather context:

```
1. What sprint number just ended? (use $ARGUMENTS if provided)
2. Was the sprint goal achieved? (Fully / Partially / Not achieved)
3. How many team members are participating?
4. Were there any significant incidents during the sprint?
```

### Prime Directive
Read this aloud to start every retro:

> "Regardless of what we discover, we understand and truly believe that everyone
> did the best job they could, given what they knew at the time, their skills
> and abilities, the resources available, and the situation at hand."
> — Norm Kerth

### Safety Check
Use AskUserQuestion:
```
On a scale of 1-5, how safe do you feel sharing honest feedback?
  1 - Not safe at all
  2 - Somewhat uncomfortable
  3 - Neutral
  4 - Mostly safe
  5 - Completely safe
```

If average is below 3, focus on building psychological safety before diving into issues.

## Step 2: Choose Retrospective Format

Use AskUserQuestion to let the team pick:

```
Which retrospective format would you like to use?
1. Start/Stop/Continue (classic, good for any sprint)
2. What Went Well / What Didn't / Action Items (structured)
3. Mad/Sad/Glad (emotion-focused, good for tough sprints)
4. 4Ls - Liked/Learned/Lacked/Longed For (balanced)
```

## Format A: Start / Stop / Continue

### Start (New practices to adopt)
Use AskUserQuestion:
```
What should we START doing?
Think about: new tools, practices, habits, or experiments that could help.
(Each person shares 1-3 items)
```

### Stop (Practices to drop)
```
What should we STOP doing?
Think about: waste, unnecessary meetings, unhelpful habits, friction points.
(Each person shares 1-3 items)
```

### Continue (Keep doing what works)
```
What should we CONTINUE doing?
Think about: what worked well, successful habits, helpful practices.
(Each person shares 1-3 items)
```

## Format B: What Went Well / What Didn't / Action Items

### What Went Well
Use AskUserQuestion:
```
What went well during Sprint [N]?
Consider: deliveries, collaboration, quality, process improvements.
(Each person shares 1-3 items)
```

### What Didn't Go Well
```
What didn't go well during Sprint [N]?
Consider: blockers, communication gaps, technical issues, scope problems.
(Each person shares 1-3 items)
```

### Root Cause Analysis
For each significant issue, apply the "5 Whys":
```markdown
Problem: [issue]
Why 1: [surface cause]
Why 2: [deeper cause]
Why 3: [systemic cause]
Why 4: [root cause area]
Why 5: [fundamental root cause]
Action: [targeted fix for root cause]
```

## Format C: Mad / Sad / Glad

### Mad (Frustrations)
```
What made you MAD or frustrated this sprint?
(Things that blocked you, caused rework, or felt wasteful)
```

### Sad (Disappointments)
```
What made you SAD or disappointed this sprint?
(Missed opportunities, things that didn't go as hoped)
```

### Glad (Celebrations)
```
What made you GLAD or proud this sprint?
(Wins, breakthroughs, good teamwork, personal growth)
```

## Format D: 4Ls

### Liked
```
What did you LIKE about this sprint?
```

### Learned
```
What did you LEARN during this sprint?
```

### Lacked
```
What did you feel was LACKING this sprint?
```

### Longed For
```
What did you LONG FOR during this sprint?
```

## Step 3: Identify Themes and Patterns

Group the feedback into themes:

```markdown
## Retrospective Themes

### Theme 1: [Name]
- Items: [grouped feedback items]
- Frequency: [how many people mentioned it]
- Impact: High / Medium / Low
- Category: Process / Technical / Communication / Quality

### Theme 2: [Name]
...
```

### Cross-Sprint Patterns
Compare with previous retrospective actions:
```markdown
Recurring themes (appeared in 2+ retros):
- [Theme]: appeared in sprints [N-2, N-1, N]
  Status of previous actions: [completed / in-progress / not started]
```

## Step 4: Generate Action Items

Use AskUserQuestion to vote on top priorities:
```
Which themes should we focus on? Pick your top 2:
(List the identified themes with brief descriptions)
```

### Action Item Template
For each selected theme, define a concrete action:

```markdown
## Action Items

### Action 1: [Clear, specific action]
- Owner: [single person responsible]
- Due: [by when — next retro at latest]
- Success measure: [how we know it worked]
- Category: Process / Technical / Communication

### Action 2: [Clear, specific action]
- Owner: [single person responsible]
- Due: [by when]
- Success measure: [how we know it worked]
- Category: Process / Technical / Communication
```

### Action Item Quality Rules
- **Limit to 2-3 actions**: more than 3 won't get done
- **Assign an owner**: unowned actions don't happen
- **Make it specific**: "improve communication" is vague; "post daily standup notes in #team-channel" is specific
- **Make it measurable**: define what success looks like
- **Review next retro**: follow up on every action

## Step 5: Sprint Metrics Review

Summarize the sprint quantitatively:

```markdown
## Sprint [N] Metrics

### Delivery
- Committed: [X] points across [Y] stories
- Completed: [A] points across [B] stories
- Completion rate: [A/X * 100]%
- Carryover: [list stories not completed]

### Quality
- Bugs found in sprint: [count]
- Bugs escaped to production: [count]
- Test coverage change: [delta]

### Process
- Sprint goal: Achieved / Partially / Not achieved
- Blockers encountered: [count]
- Average blocker resolution: [time]

### Velocity Trend
- Sprint N-2: [V1] points
- Sprint N-1: [V2] points
- Sprint N:   [V3] points
- Trend: Increasing / Stable / Decreasing
```

## Step 6: Retrospective Summary

Generate the final retrospective document:

```markdown
# Sprint [N] Retrospective Summary

**Date**: [date]
**Participants**: [count]
**Format**: [chosen format]
**Sprint Goal**: [Achieved / Partially / Not achieved]

## Key Takeaways
1. [Most important positive]
2. [Most important improvement area]
3. [Most impactful action item]

## Action Items
| # | Action | Owner | Due | Measure |
|---|--------|-------|-----|---------|
| 1 | ...    | ...   | ... | ...     |
| 2 | ...    | ...   | ... | ...     |

## Previous Action Items Follow-up
| # | Action | Status | Notes |
|---|--------|--------|-------|
| 1 | ...    | Done/In Progress/Not Started | ... |

## Team Sentiment
- Safety score: [average]
- Overall mood: [positive/neutral/negative]
- Energy level: [high/medium/low]
```

## Facilitation Tips

- **Timebox**: 45 min for 1-week sprint, 90 min for 2-week sprint
- **Equal voice**: ensure everyone speaks; use round-robin if needed
- **Focus forward**: retros improve the future, not blame the past
- **Follow through**: unactioned retros erode trust — always follow up
- **Vary formats**: rotate formats every few sprints to keep engagement high
- **Celebrate wins**: don't skip what went well; recognition fuels morale
