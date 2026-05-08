---
name: architecture-docs
description: |
  Produce architecture documentation for technical audiences using established frameworks — the C4 model for system structure (Context / Container / Component / Code), Architectural Decision Records (ADRs) for capturing the why behind significant design choices, OpenAPI for HTTP API specifications, and system / component design documents for engineers who need to build against or reason about the architecture. Use when someone asks to document system architecture, write an ADR, capture an architectural decision, generate C4 diagrams (context / container / component), produce an OpenAPI spec, draft a component design doc, or document how services integrate. Trigger phrases include "create a C4 diagram", "write an ADR for X", "document the architecture", "specify the API", "OpenAPI spec for", "system design doc", "decision record", "architecture overview". Not for: end-user-facing docs (use the `diataxis` skill instead — tutorials, how-tos, references, explanations live there), README content, or code-level inline documentation.
---

# Architecture Documentation

Architecture documentation serves a different audience and purpose than user-facing documentation. The reader is a developer, architect, or technical stakeholder who needs to *implement against*, *integrate with*, or *reason about* the system. The output is structural and decision-oriented, not learning-oriented.

If the request is to write user-facing docs (tutorials, how-tos, references, explanations that live in `docs/`), use the `diataxis` skill instead. This skill covers the architectural-artifact side: structure diagrams, decision records, API specs, system / component design.

## The four artifact types

| Artifact | What it captures | Audience | Path |
|----------|-----------------|----------|------|
| **C4 diagrams** | System structure at four zoom levels | Everyone (Context) → Architects (Code) | `docs/architecture/` |
| **ADR** | A single significant architectural decision and its context | Future engineers, current team | `docs/decisions/` |
| **OpenAPI spec** | HTTP API contract | API consumers, integrators | `docs/api/` |
| **System / component design** | Detailed structural design for a system or one component | Engineers building or extending the thing | `docs/architecture/` |

Most architecture-doc requests resolve to one of these four. Pick the one that matches what the user is actually asking to capture.

## Picking the artifact

- **"Document our architecture"** → start with a C4 Context + Container diagram, plus a short System Overview. Drill into Component / Code only when an audience specifically needs that depth.
- **"Why did we choose X over Y?"** or **"capture this decision"** → write an ADR. One decision per ADR; multiple decisions = multiple ADRs.
- **"Document the API"** → OpenAPI spec for HTTP APIs. (For internal Python / TypeScript / etc. APIs that aren't HTTP, that's a *user-facing reference* — use the `diataxis` skill's reference mode instead.)
- **"Document this service / component"** → component design doc, possibly with an embedded C4 Component diagram and links to the relevant ADRs.

## C4 Model — what each level captures

C4 is a four-level zoom into a system. Each level has its own audience and purpose; you don't need all four for every system. **Read `references/c4-model.md` for the diagrams and templates.**

| Level | Audience | What's shown |
|-------|----------|--------------|
| 1. System Context | Everyone | The system as a single box, the people and external systems it interacts with |
| 2. Container | Technical stakeholders | High-level technology choices (apps, databases, services) |
| 3. Component | Architects, senior developers | Major building blocks inside a container |
| 4. Code | Developers | Class / module structure inside a component (often skipped in favor of code itself) |

Most projects need Context + Container always. Component when the system is non-trivial. Code level rarely earns its keep — the source of truth is the source.

## Architectural Decision Records (ADRs)

An ADR captures **one** significant architectural decision: the context that motivated it, the options considered, the choice made, and the consequences. ADRs are *immutable* once accepted — superseding decisions get a new ADR that links back to the previous one.

**Read `references/adr-template.md` for the template, naming conventions, and the full "when to write / when not to write" criteria.** Quick gut check: write one when a future engineer will ask "why did we do it this way?" and the answer isn't obvious from the code; skip it for trivially-correct choices and implementation details.

## OpenAPI specifications

OpenAPI 3.x is the standard for HTTP API contracts. The spec serves as both human-readable reference and machine-readable input to client generators, mock servers, validation, and gateways.

**Read `references/openapi.md` for the structure template, common patterns (auth, pagination, error schemas), and the trade-offs between handwritten YAML, code-generated specs, and OpenAPI-first development.**

## System and component design documents

These are prose-with-diagrams design docs that capture the structure and behavior of a system or one component within it. Use when:

- Onboarding new engineers to a non-trivial subsystem
- Proposing a new component before implementation
- Documenting an existing component whose design isn't self-evident from the code

**Read `references/system-and-component-design.md` for the templates.**

## Diagrams

C4, sequence, deployment, and data-flow diagrams are core to architecture docs. Two skill options in this plugin:

- **D2** (`d2` skill) — declarative, full-featured, especially good for C4 (`shape: c4-person`), sequence diagrams, ER diagrams, and grid layouts. Renders to SVG / PNG / PDF / PPTX. Requires the `d2` CLI.
- **Mermaid** (`markdown-mermaid` skill) — renders natively on GitHub and most MD viewers; good enough for sequence, flowchart, gantt, class. No CLI needed but less expressive than D2.

For C4 specifically, D2's `c4-person` shape and explicit container boundaries produce cleaner output than mermaid's generic graph syntax. For sequence diagrams either works.

## Voice and register

- Audience-aware. The same system gets a different doc for the executive sponsor than for the engineer implementing it. State the audience near the top.
- Decision-transparent. Document the *why*, not just the *what*. The code is the *what*.
- Living, not archival. Architecture docs that aren't kept synchronized with reality become liabilities. If a doc is fossilized, mark it as historical or delete it.
- Standard formats. C4 is a real framework; ADRs have well-known conventions; OpenAPI has a spec. Use them rather than inventing local variants — readers have built-in expectations.

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Implementation tour | Documentation that just narrates the code structure file by file | Capture decisions and structure that *aren't* obvious from the code |
| Audience-blind | One doc trying to serve executives, architects, and devs | Multiple short docs, each with a stated audience |
| Frozen artifact | Doc is months out of date, nobody trusts it, but it persists | Either keep it current or delete it; stale architecture docs cause wrong implementation |
| ADR as proposal | Using ADRs to propose decisions instead of recording accepted ones | Use a regular design doc for proposals; the ADR captures the *outcome* |
| C4 Code level for everything | Generating Code-level diagrams that immediately go stale | Skip the Code level unless an audience specifically needs it |

## Output paths summary

```
docs/
├── architecture/      # C4 diagrams, system overviews, component design
├── decisions/         # ADRs (numbered: 0001-*.md, 0002-*.md, ...)
└── api/               # OpenAPI specs and supporting API docs
```
