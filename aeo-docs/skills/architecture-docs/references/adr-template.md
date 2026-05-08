# Architectural Decision Records — full reference

An ADR captures **one** significant architectural decision: the context, options, choice, and consequences. ADRs are immutable once accepted; superseding decisions get a new ADR that links back.

## Naming and numbering

```
docs/decisions/
├── 0001-record-architecture-decisions.md
├── 0002-use-postgres-not-mysql.md
├── 0003-event-driven-orders-vs-synchronous.md
└── ...
```

- Four-digit zero-padded sequence (`0001`, `0002`, ...) — predictable sort order in directory listings.
- Kebab-case title summarizing the decision in 4–8 words.
- Title leads with a verb where possible: *"use Postgres"*, *"adopt event-driven orders"*, *"deprecate the v1 API"*.

The first ADR is conventionally titled "Record Architecture Decisions" and is the meta-ADR establishing the practice itself in this codebase.

## Template

```markdown
# ADR-NNNN: [Decision title]

**Status**: Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-XXXX
**Date**: YYYY-MM-DD
**Deciders**: [people or roles]

## Context

[The forces at play. What is the issue we're addressing? What constraints, requirements, or facts about the system or organization make this decision necessary or non-trivial? Be specific — "we need to scale" is too vague; "the order pipeline is hitting 5k req/s sustained at peak and Postgres write IOPS is the bottleneck" is useful context.]

## Decision

[The change being proposed or accepted. State it as a positive assertion of what *will* be done, in present tense: "We will use Postgres logical replication to fan out order events to the analytics warehouse" — not "We considered using Postgres logical replication...".]

## Consequences

### Positive

- [Good outcomes from this decision]
- [Capabilities it unlocks]

### Negative

- [Costs, downsides, complexity introduced]
- [Things that get harder]

### Neutral

- [Other impacts that are neither positive nor negative — operational changes, new dependencies, retraining needs]

## Alternatives considered

### [Alternative 1 name]

[What it was, why it was a candidate, why it wasn't chosen.]

### [Alternative 2 name]

[Continue per alternative.]

[An ADR with no alternatives section is suspicious — if there were no alternatives, the decision probably isn't significant enough to warrant an ADR.]

## Implementation notes (optional)

[High-level implementation pointers. *Not* a full design doc — that's a separate artifact. Include only what's needed to execute the decision: which services change, what migration is needed, who owns the rollout.]

## Related decisions

- ADR-NNNN: [Related decision and how it relates]
- [Or: "None" if this stands alone.]
```

## Status lifecycle

| Status | Meaning |
|--------|---------|
| **Proposed** | Drafted but not yet accepted; under review |
| **Accepted** | Decided and in force |
| **Rejected** | Considered but explicitly not adopted (still useful as a record) |
| **Deprecated** | Was accepted, no longer in force, but no replacement |
| **Superseded by ADR-XXXX** | Replaced by a later decision; both records remain |

ADRs are *append-only*. Don't edit an Accepted ADR to reflect a new decision — write a new one with status `Accepted` that supersedes the old one, and update the old one's status to `Superseded by ADR-XXXX`.

## When to write an ADR

Write one when **any of these** is true:

- A future engineer will ask "why did we do it this way?" and the answer matters
- The choice was between two or more viable options where the path-not-taken would have been defensible
- The constraint behind the decision isn't visible from reading the code (compliance, vendor lock-in, organizational capability, deadline pressure)
- The decision will affect downstream work for months or years

## When **not** to write an ADR

Skip them when:

- The choice is trivially correct (use HTTPS, encrypt passwords at rest, use version control)
- The decision is an implementation detail the next engineer will figure out from the code
- It's a temporary fix you expect to revisit in weeks
- It's a personal preference dressed up as architecture (formatting, file layout, naming conventions — those go in a style guide, not an ADR)

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| ADR as proposal | Using the ADR format to *suggest* a decision before it's been made | Use a regular design doc for proposals; the ADR records the *accepted* outcome |
| Decision-of-the-week | Writing an ADR for every small choice | Reserve ADRs for decisions that will outlive the current sprint |
| Editing accepted ADRs | Quietly updating a past ADR to match new reality | Write a new ADR; mark the old one as superseded |
| One ADR per epic | Bundling multiple decisions into one record | One decision per ADR; cross-link if they're related |
| Empty consequences section | "There are no downsides to this decision" | If you can't think of trade-offs, you haven't thought hard enough |

## Voice

- Past tense for the *Context* (these are the forces that existed when we decided).
- Present-tense assertion for the *Decision* ("we use", "we will use", not "we considered using").
- Honest about *Consequences* — readers lose trust in ADRs that pretend everything was upside.
- Brief. A good ADR is 1–2 pages. If it's longer, the decision is probably actually multiple decisions.
