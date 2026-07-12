# Risk Assessment & Trade-Off Framework

Risk identification and trade-off decision patterns for the PLAN phase.

## Risk Identification

**What could go wrong?**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk description] | H/M/L | H/M/L | [How to address/prevent] |

**Common risk categories:**
- Technical (new technology, complexity, integration)
- Timeline (estimates off, dependencies blocking)
- Requirements (changing scope, unclear needs)
- Resources (team capacity, budget constraints)

## Trade-Off Decision Framework

**When multiple approaches exist:**

1. **Identify dimensions**: Performance, complexity, maintainability, time-to-ship, scalability
2. **Map each option** against dimensions
3. **Weight by priorities** (from PRD or user input)
4. **Present analysis**, let user decide (you recommend, they choose)

**Common trade-offs:**
- **Speed vs Quality**: MVP mindset vs production-grade
- **Simple vs Scalable**: Start simple, refactor later vs design for scale now
- **Build vs Buy**: Custom solution vs third-party (maintenance burden vs flexibility)
- **Performance vs Complexity**: Optimize now vs ship fast, optimize later
- **Flexibility vs Simplicity**: Configurable/extensible vs focused/opinionated

**Presentation pattern:**
```
We have 3 approaches for [decision]:

Option A: [Technology/Approach]
- Pros: [Benefits]
- Cons: [Tradeoffs]
- Best for: [When to use]

Option B: [Technology/Approach]
- Pros: [Benefits]
- Cons: [Tradeoffs]
- Best for: [When to use]

Option C: [Technology/Approach]
- Pros: [Benefits]
- Cons: [Tradeoffs]
- Best for: [When to use]

Given your [requirements/priorities], I recommend [Option]. What do you think?
```

## When to Push Back on Requirements

**Challenge when:**
- Estimate significantly exceeds timeline (identify scope reduction)
- Requirements conflict with each other (clarify priorities)
- Technical approach violates constraints from EPCC_EXPLORE.md
- Security/quality trade-offs are risky
- Scope creep detected (features added without timeline adjustment)

**Don't push back on:**
- User preferences for technology choices (unless clear technical blocker)
- Ambitious goals (help break into phases instead of saying "impossible")
- Requests for explanation (transparency builds trust)

**How to push back constructively:**
```
"I want to make sure we set realistic expectations. [Issue description].

We have options:
1. Reduce scope to [core features] to meet timeline
2. Extend timeline to [X weeks] for full feature set
3. Phased rollout: [MVP now] + [enhancements later]

What's most important for this project?"
```

## Parallel Planning Subagents (Optional)

For **very complex planning tasks**, deploy specialized planning agents **in parallel**:

**When to use:**
- Complex system architecture design
- Multi-technology evaluation
- Large-scale security threat modeling

```markdown
@system-designer Design high-level architecture for [feature].

Context:
- Project: [type and tech stack]
- Framework: [from EPCC_EXPLORE.md]
- Current architecture: [existing patterns]

Requirements (from PRD.md if available):
- [Functional requirements]
- [Non-functional requirements]

Constraints from EPCC_EXPLORE.md:
- [Existing patterns to follow]
- [Integration points]

Design: Component structure, data flow, integration points

Deliverable: Architecture diagram, component descriptions, scalability considerations
```
