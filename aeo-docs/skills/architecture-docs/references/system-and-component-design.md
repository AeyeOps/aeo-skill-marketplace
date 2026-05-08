# System and component design — full reference

System and component design documents are prose-with-diagrams artifacts that capture the structure and behavior of a system (or one component within it). They're for engineers who need to *build against*, *integrate with*, or *extend* the thing.

Two templates: System Overview (for a whole system) and Component Design (for one piece of one).

## System Overview

```markdown
# [System Name] — Architecture Overview

**Audience**: [Engineers / architects / stakeholders. Be specific.]
**Last updated**: YYYY-MM-DD
**Owner**: [Team or role]

## Executive summary

[Two or three sentences. What is this system, what problem does it solve, what are the non-obvious things to know up front.]

## System context

[Embed or link to the C4 Context diagram — `docs/architecture/c4-context.md`.]

### Stakeholders

- **End users**: [Who and how they use it]
- **Administrators**: [Admin responsibilities and interfaces]
- **External systems**: [Integration points and dependencies]

### Business goals

- [Primary business objective]
- [Performance, scalability, security requirements that shape the design]

## High-level architecture

[Embed or link to the C4 Container diagram — `docs/architecture/c4-container.md`.]

### Key technologies

| Component | Technology | Why this choice |
|-----------|------------|-----------------|
| API layer | [e.g. Node.js / Express] | [Brief rationale, or link to ADR-NNNN] |
| Database | [e.g. PostgreSQL] | [Rationale or ADR link] |
| Cache | [e.g. Redis] | [Rationale or ADR link] |

[For non-obvious tech choices, prefer linking to an ADR over inlining the rationale.]

### Key data flows

[Sequence diagrams for the 2-4 most important user / system journeys. Use D2 or Mermaid.]

## Quality attributes

- **Performance**: [Targets — response time, throughput]
- **Availability**: [Uptime target, degradation behavior]
- **Security**: [Auth model, encryption, key management]
- **Scalability**: [Scaling dimensions and limits]

## Operational concerns

- **Deployment**: [Where it runs, how it's deployed]
- **Observability**: [Logs, metrics, tracing — what's instrumented]
- **Failure modes**: [What breaks, how it's detected, what happens]

## Decision log

The major architectural decisions for this system live as ADRs in `docs/decisions/`:

- ADR-0001: [Title and one-line summary]
- ADR-0002: [Title and one-line summary]

## See also

- C4 Context → `docs/architecture/c4-context.md`
- C4 Container → `docs/architecture/c4-container.md`
- API spec → `docs/api/openapi.yaml`
- User-facing docs → `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`
```

## Component Design

```markdown
# [Component Name] — Design

**Audience**: Engineers building or extending this component.
**Status**: [Proposed | Implemented | Deprecated]
**Last updated**: YYYY-MM-DD

## Purpose

[What this component does and why it exists. One paragraph.]

## Interface

### Public API

```typescript
interface [ComponentName] {
  method1(param: Type): Promise<ReturnType>;
  method2(param: Type): ReturnType;
}
```

[For HTTP components, link to or embed the relevant OpenAPI fragment. For library / module APIs, the interface signatures go here directly.]

### Dependencies

- **External**: [Third-party services or libraries this depends on, with versions if pinned]
- **Internal**: [Other components in this system this calls into]

## Internal design

### Structure

[C4 Component diagram or class structure for the inside of this component. Use D2 or Mermaid.]

### Key algorithms

[Pseudocode or flowcharts for any logic that isn't obvious from the code.]

### Data model

[Tables / entities owned by this component. Schema or pointer to migration files.]

## Error handling

| Error class | When it happens | Behavior |
|-------------|-----------------|----------|
| [Expected business error] | [Trigger condition] | [Returned to caller, logged, retried, ...] |
| [Unexpected system error] | [Trigger] | [Bubble up, retry with backoff, dead-letter, ...] |

## Performance considerations

- **Hot path**: [What's on the critical path and how fast it needs to be]
- **Bottlenecks**: [Known limitations and the conditions under which they bite]
- **Optimizations**: [Caching, indexing, batching strategies in use]

## Observability

- **Metrics emitted**: [List of metric names with what they track]
- **Logs**: [What gets logged, at what level]
- **Traces**: [Spans / annotations of interest]

## Testing strategy

- [Unit, integration, contract, load — what's covered and where]

## Open questions / known limitations

- [Things the design doesn't yet handle, or known sharp edges]

## Related

- ADRs: [Links to relevant ADRs]
- Upstream: [Components that call into this one]
- Downstream: [Components this calls into]
```

## Voice

- Audience-aware. State who the doc is for in the first lines and write to that audience's level.
- Decision-transparent. When a non-obvious choice was made, either inline a one-sentence rationale or link to an ADR.
- Honest about gaps. An "Open questions" section signals integrity; a doc that pretends everything is solved gets distrusted on first contact with reality.

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Code narration | The doc walks through every file in the repo | Capture structure and decisions; the code is the source of truth |
| Audience-blind | One doc trying to serve executives, architects, and devs | Multiple short docs, each with a stated audience |
| Frozen artifact | Doc is months out of date and nobody trusts it | Either update or delete; stale architecture docs cause wrong implementation |
| Hidden ADRs | Major decisions justified inline instead of in the ADR log | Pull rationale into ADRs, reference from here |

## When this is not the right artifact

- For end-user docs, use the `diataxis` skill (tutorials / how-tos / references / explanations)
- For an API contract specifically, use OpenAPI directly (`references/openapi.md`) — a system overview can link to the spec, not duplicate it
- For a single decision, write an ADR (`references/adr-template.md`) — system / component design docs are *broader* than a single decision
