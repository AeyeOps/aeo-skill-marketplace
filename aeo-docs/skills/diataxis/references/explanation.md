# Explanation mode — full reference

An explanation **builds mental models**. The reader is experienced, has a working grasp of *what* the system does, and wants to understand *why* it works the way it does. The output is a conceptual narrative, not a procedure.

## Section template

The template below is a **maximal menu**, not a checklist. A focused decision-explainer might use only Big Picture + Core Concepts + Key Design Decisions + Trade-offs (4 sections); a deep system explainer might use most of them. Pick the sections that earn their keep for *this* topic and drop the rest — long explanations with empty filler sections are worse than short ones that say what matters. The same advice applies inside subsections: if a "Future directions" or "Industry patterns" subsection has nothing real to say, leave it out.

```markdown
# Understanding [Concept/System]

> **Purpose**: This document explains [what aspect of understanding this provides]
> **Audience**: [Who benefits — usually experienced practitioners or stakeholders]
> **Prerequisite knowledge**: [What readers should already understand before starting]

## The big picture

[High-level conceptual overview that frames the rest of the document. Few paragraphs at most.]

### Why this matters

[Why understanding this concept changes how the reader interacts with the system.]

## Historical context

### The problem space

[What problems led to this design existing in the first place.]

### Evolution of solutions

[How approaches to this problem have evolved — only as much history as helps the reader contextualize the current state.]

### Current state

[Where we are now and why we're here.]

## Core concepts

### [Fundamental concept 1]

**What it is**: [Clear, precise definition]
**Why it exists**: [The problem it solves]
**How it relates**: [Connection to other concepts in this doc]

```[diagram if helpful]
[Visual representation]
```

**Mental model**: Think of this like [helpful analogy]. [The analogy is doing real work — pick one that surfaces the right intuitions, not a cute one.]

### [Fundamental concept 2..N]

[Same shape — definition, motivation, connections, optional analogy.]

## Architectural design

### Design principles

1. **[Principle name]**: [What it means]
   - **Rationale**: [Why this principle was chosen]
   - **Impact**: [How it shapes the system]
   - **Trade-offs**: [What was given up for it]

2. **[Next principle]**: [Continue pattern]

### Key design decisions

#### Decision: [Specific architectural choice]

**Context**: [Situation that required this decision]

**Options considered**:

1. **Option A**: [Description] — Pros / Cons
2. **Option B**: [Description] — Pros / Cons

**Choice made**: [Which option and why]
**Consequences**: [What this decision means for users / developers]

[For deeper architectural decisions, an ADR may live in `docs/decisions/` instead — see `architecture-docs` skill. This section is for the *narrative* context that helps readers internalize the *why*.]

## Trade-offs and alternatives

### Performance vs. [other quality]

[Explain the balance struck and why.]

### Flexibility vs. simplicity

[Discuss how the system balances these.]

### Other trade-offs

[Additional compromises in the design — be honest about them.]

## Common misconceptions

### Misconception: [Common misunderstanding]

**Reality**: [Actual truth]
**Why the confusion**: [Source of the misunderstanding — often a leaky abstraction or a name that suggests something it isn't]

[Repeat for the 2-4 most consequential misconceptions.]

## Implications for practice

When working with [system], understanding these concepts means:
- [Practical implication 1]
- [Practical implication 2]
- [Practical implication 3]

### Patterns that emerge

Based on these principles, common patterns include:
- [Pattern 1]
- [Pattern 2]

## Connecting to broader concepts

### Relationship to [related system or concept]

[How this fits with adjacent ideas the reader may already know.]

### Industry patterns

[How this fits into broader industry practices — only if it does. If the design is unusual, name that.]

### Future directions

[Where this concept or architecture might evolve. Speculative is fine here, but mark it as such.]

## Summary: the mental model

After understanding all of this, think of [system / concept] as:

[A synthesizing metaphor or model that captures the essence in one or two sentences.]

Key insights to remember:
1. [Most important understanding]
2. [Second key insight]
3. [Third key insight]

## See also

- **To follow along** → `../tutorials/[topic].md`
- **To solve a problem with this** → `../how-to/[task].md`
- **For specifications** → `../reference/[component].md`
- **Academic / external context** → [papers, blog posts that go deeper]
```

## Quality checklist

- [ ] **Clear purpose** — why understanding this matters in practice
- [ ] **Conceptual focus** — ideas and principles, not procedures
- [ ] **Historical context** — enough background to contextualize, not a museum tour
- [ ] **Design rationale** — the "why" behind decisions
- [ ] **Trade-off discussion** — honest about what was compromised
- [ ] **Mental models** — analogies and framings that aid intuition without misleading
- [ ] **Connections** — to other concepts, systems, industry practice

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Tutorial disguise | Teaching how to do something instead of explaining concepts | Focus on understanding; link to a tutorial |
| Reference dump | Listing specifications instead of building intuition | Link to the reference; stay at concept level |
| Implementation focus | Getting lost in code instead of concepts | Use code only to illustrate ideas, never as the substance |
| Opinion piece | Personal preferences presented as design rationale | Ground claims in actual design decisions, not taste |
| Academic thesis | Heavy theory with no practical grounding | Balance theory with real-world implications |

## Voice and register

- Thoughtful, fair, willing to acknowledge that other choices were viable. The reader is sophisticated; condescension lands badly.
- Use analogies that *work* — pick them for accuracy, not cuteness. A bad analogy creates a misconception.
- Discuss trade-offs without taking sides unless the system genuinely committed to one side. "We chose X over Y because..." is fine; "X is the right answer" usually isn't.
- It's OK to say a design was wrong in retrospect. Pretending past decisions were optimal is itself a misconception fuel.

## Output

- **Path**: `docs/explanation/`
- **Filenames**: `[concept]-design.md`, `[system]-architecture.md`, `understanding-[topic].md`, `[pattern]-explained.md`, `[technology]-concepts.md`

## Conceptual framework patterns

These are different organizing approaches you can take. Pick the one that fits the topic:

- **Bottom-up**: start with concrete examples, build to abstract principles
- **Top-down**: start with high-level concepts, drill into specifics
- **Historical narrative**: trace evolution from original problem to current solution
- **Comparative analysis**: explain by contrasting with alternatives
- **Analogical reasoning**: use familiar concepts to explain unfamiliar ones

## Success and failure indicators

**Success**: Readers gain conceptual understanding, complex ideas become clear, design decisions make sense, trade-offs are understood, readers can reason about the system on their own afterward.

**Failure**: Readers still don't understand why, explanations raise more questions than answers, concepts remain abstract and disconnected, no practical value from the understanding.
