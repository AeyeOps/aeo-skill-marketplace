# AskUserQuestion Patterns

Shared interactive elicitation guidance for EPCC commands.

## When to Use AskUserQuestion (PRIMARY METHOD)

**Use AskUserQuestion for** (default for all decisions):
- Decisions with 2-4 clear options
- Technology choices (database, hosting, auth, frameworks)
- Architecture decisions (monolith vs microservices vs serverless)
- Infrastructure decisions (cloud provider, deployment approach)
- Priority/scope decisions (MVP vs comprehensive)
- Mode selection (quick vs comprehensive)

**Pattern**:
```typescript
AskUserQuestion({
  questions: [{
    question: "What [decision area] fits your needs?",
    header: "ShortLabel",  // max 12 chars
    multiSelect: false,    // true for non-exclusive choices
    options: [
      {
        label: "Option A",
        description: "Benefit A, tradeoff A, best for scenario A"
      },
      {
        label: "Option B",
        description: "Benefit B, tradeoff B, best for scenario B"
      },
      {
        label: "Option C",
        description: "Benefit C, tradeoff C, best for scenario C"
      },
      {
        label: "Option D",
        description: "Benefit D, tradeoff D, best for scenario D"
      }
    ]
  }]
})
```

## When to Converse Naturally (FALLBACK)

**Use conversation for**:
- Open-ended exploration ("Tell me about your data model")
- Clarifying context ("What scale are we targeting?")
- Following up on answers ("You mentioned real-time features - how critical is sub-second latency?")
- Discussing custom/hybrid approaches not fitting 2-4 options
- Truly unique situations

**Don't use conversation for**:
- Standard technology choices (database, hosting, auth → use AskUserQuestion)
- Decisions already answered in existing docs (read first)
- Implementation details (defer to CODE phase)

## Question Decision Framework

**Ask when:**
- User provides vague ideas ("make it better", "improve performance")
- Multiple valid interpretations exist
- Scope unclear
- Need concrete examples
- Prioritization ambiguous
- Technical options exist
- User jumps to solution before defining problem

**Don't ask when:**
- User already provided clear answer
- Question doesn't add value
- You're interrogating instead of conversing
- Stalling instead of documenting what you know
- User explicitly says "let's move forward"
- Existing docs already clarified it (read PRD.md, TECH_REQ.md, EPCC_EXPLORE.md first)

## Question Frequency Heuristic

**Ask until clarity achieved**, not to hit targets. Typical ranges by phase:

- **Vision phase**: Exploratory questioning until problem/solution understood
- **Features phase**: Prioritization-focused until must-haves identified
- **Technical phase**: Option-driven until key decisions made
- **Constraints phase**: Fact-gathering until boundaries clear
- **Success phase**: Metric-defining until "done" criteria established

**Rule**: If user can't answer clearly after 2-3 attempts, you're asking wrong question or too early. Reframe or gather more context first.

## Common Decision Categories

- Project type (Greenfield, Feature Addition, Refactor, Bug Fix)
- User scope (Just me, Small team, Department, Public)
- Urgency (Critical, Important, Nice-to-have, Exploratory)
- MVP approach (Bare Minimum, Core + Polish, Feature Complete, Phased)
- Environment (Local, Cloud, On-Premise, Hybrid)
- Data storage (Relational, Document, File, In-Memory)
- Authentication (None, Basic, OAuth/SSO, API Keys)
- Timeline (ASAP, 1-2 weeks, 1-2 months, 3+ months)

## Research & Exploration Context

Before asking questions, gather context:
- **WebSearch/WebFetch**: Use for technology comparisons, best practices, domain standards, official docs when unfamiliar
- **/epcc-explore**: Use for brownfield projects to discover existing architecture, tech stack, patterns
- **PRD.md/TECH_REQ.md**: Read existing docs first - don't re-ask what's documented

**Decision heuristic**: Research when comparing options or learning domain; explore brownfield for existing patterns; skip if user provided sufficient context.

## Check Context Files First

**Before asking questions**:
```bash
if [ -f "PRD.md" ]; then
    # Read PRD.md to understand product context
    # Reference dynamically: "Based on the feature in PRD.md..."
fi

if [ -f "TECH_REQ.md" ]; then
    # Read TECH_REQ.md for technical decisions already made
fi

if [ -f "EPCC_EXPLORE.md" ]; then
    # Read exploration findings for existing patterns
fi
```

**If context docs missing**: Ask about the context first to inform decisions.

## Conversation Principles

### Be Collaborative, Not Prescriptive

- **Don't dictate**: "You should use React for this"
- **Do guide**: "For UI, we could use React (popular, ecosystem) or Vue (simpler) or Svelte (fast). Given your [requirement], which sounds better?"

### Present Tradeoffs

- **Don't guarantee**: "This will definitely work"
- **Do qualify**: "This approach would likely work well, though we'd need to validate performance with real data"

### Ask Follow-ups When Vague

- "Can you give me an example of what that would look like?"
- "Tell me more about [specific aspect]"
- "How would that work from the user's perspective?"
- "You mentioned high scale - can you quantify that?"

### Reflect Back Periodically

"So if I understand correctly, you want to build [X] that helps [users] do [task] by [method]. The key challenges are [Y] and [Z]. Does that sound right?"
