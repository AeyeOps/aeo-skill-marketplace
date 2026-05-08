---
name: diataxis
description: |
  Author user-facing technical documentation following the Diataxis framework — tutorials, how-to guides, reference material, and conceptual explanations. Picks the right of the four documentation modes for the request, applies that mode's structural template, and avoids cross-mode bleed (no comprehensive API listings inside a tutorial, no learning exercises inside reference docs, no step-by-step procedures inside an explanation). Use whenever someone asks to document something for users, write a getting-started guide, generate an API or config or CLI reference, write a deployment / migration / troubleshooting guide, explain a design decision, or produce any docs that will live in `docs/`. Trigger phrases include "write a tutorial", "create a how-to", "document the API", "explain why we chose", "generate config docs", "build a reference", "write user docs for X", and any open-ended request to produce user-facing documentation. Not for: README content, code comments, architecture / C4 / ADR / OpenAPI work (use `architecture-docs` instead), or internal design docs that aren't user-facing.
---

# Diataxis — User-Facing Documentation

The [Diataxis framework](https://diataxis.fr) splits user-facing documentation into four modes that serve different reader needs. Most "bad documentation" comes from mixing modes — a tutorial that gets reference-dumpy, a reference that wanders into design rationale, a how-to that pauses to teach concepts. **Pick the mode first; the template flows from that.**

## The four modes

| Mode | Reader is | Reader wants | Output is |
|------|-----------|--------------|-----------|
| **Tutorial** | a beginner | to learn by doing | a guided practice exercise |
| **How-to guide** | competent | to solve a specific problem | a goal-oriented procedure |
| **Reference** | already knows what they need | to look up exact specifications | comprehensive, scannable lookup |
| **Explanation** | experienced | to understand *why* | a conceptual narrative |

The reader's state and intent decide the mode, not the topic. The same feature can have all four — a tutorial that walks a beginner through using it, a how-to that solves a specific problem with it, a reference that lists every option, and an explanation of why it works the way it does.

## Picking the mode

Two questions resolve the choice:

1. **Is the reader trying to learn, or trying to do something specific?** Learning → tutorial or explanation. Doing → how-to or reference.
2. **Is the reader hands-on, or after concepts?** Hands-on → tutorial (learning) or how-to (doing). Conceptual → explanation (learning) or reference (doing).

```
                  hands-on            conceptual
                ┌───────────────────┬──────────────────┐
   learning     │     Tutorial      │   Explanation    │
                ├───────────────────┼──────────────────┤
   doing        │     How-to        │   Reference      │
                └───────────────────┴──────────────────┘
```

When a request fits multiple modes, write multiple short docs rather than one cross-mode doc. A "guide to X" that's three modes glued together helps no one.

## Mode summaries — read the matching reference for the full template

### Tutorial — "build your first X"

Beginner-safe, hands-on, single linear path, every step verified. The reader follows along; the doc holds their hand. Goal is confidence and basic familiarity, not comprehensive knowledge.

→ Output: `docs/tutorials/`. Read `references/tutorial.md` for the section template, anti-patterns, and quality checklist.

### How-to guide — "how to X in Y"

Goal-oriented procedure for someone who already knows the basics. Imperative voice ("Set", "Configure", "Run"), real-world conditions, troubleshooting included. Shortest reasonable path from problem to solution.

→ Output: `docs/how-to/`. Read `references/howto.md` for the section template.

### Reference — "the X API / config / CLI"

Comprehensive, factual, scannable. Reader knows what they need; the doc tells them exactly. No tutorials, no opinions, no design rationale — those live elsewhere and get linked.

→ Output: `docs/reference/`. Read `references/reference.md` for the API, config, CLI, schema, and error-code templates (different reference *types* have different shapes).

### Explanation — "why X works this way"

Builds mental models. Discusses trade-offs, alternatives, history, and design rationale. The reader should come away thinking differently about the system, not knowing how to do something new.

→ Output: `docs/explanation/`. Read `references/explanation.md` for the section template.

## Output conventions across all four modes

### File paths

```
docs/
├── tutorials/      # Tutorial mode
├── how-to/         # How-to mode
├── reference/      # Reference mode
└── explanation/    # Explanation mode
```

If the project doesn't have a `docs/` tree yet, create the relevant subdirectory the first time you write into it. Don't create empty siblings preemptively — they accrete cruft.

### File naming

Kebab-case, lead with the verb or topic noun:

| Mode | Examples |
|------|----------|
| Tutorial | `getting-started-[tool].md`, `build-[thing].md`, `learn-[concept].md`, `connect-[a]-to-[b].md` |
| How-to | `configure-[feature].md`, `integrate-[system].md`, `troubleshoot-[problem].md`, `migrate-[from]-to-[to].md`, `deploy-[target].md` |
| Reference | `[component]-api.md`, `[feature]-config.md`, `[tool]-cli.md`, `[data]-schema.md`, `error-codes.md` |
| Explanation | `[concept]-design.md`, `[system]-architecture.md`, `understanding-[topic].md`, `[pattern]-explained.md` |

### Cross-linking

Each mode links *out* to the other three when the reader's next question would be better served there. The four-way footer is a good default at the end of any doc:

```markdown
## See also

- **Want to follow along?** → `../tutorials/<topic>.md`
- **Solving a specific problem?** → `../how-to/<task>.md`
- **Looking up specs?** → `../reference/<component>.md`
- **Want to understand why?** → `../explanation/<concept>.md`
```

Drop bullets that don't have a corresponding doc on the other end — broken-link rot is worse than a shorter footer.

## Cross-mode anti-patterns — fingerprints of mode bleed

These are the patterns that mean you've drifted out of mode. If you catch yourself writing one, stop and ask whether the content belongs in a different doc.

| Drift | Fingerprint | Fix |
|-------|-------------|-----|
| Tutorial → reference | Listing every option of a thing the reader is just trying to use once | Pick one good default, link to the reference for the rest |
| How-to → tutorial | Pausing to teach basics the audience should already know | State the prereqs, link to a tutorial |
| Reference → explanation | Design rationale interleaved with specs | Keep the reference factual, push rationale into an explanation doc |
| Explanation → how-to | Step-by-step instructions creeping into the conceptual narrative | Link to a how-to for the procedure |

## When the request is ambiguous

Common cases and how to resolve them:

- **"Document X"** with no other context — if X is an API / config / CLI, default to a reference. Otherwise ask whether the audience is learning or already using it. When unclear, a how-to plus a reference covers most needs without writing a tutorial nobody asked for.
- **"Write docs for the new feature"** — almost always means at least a how-to (for users who'll adopt it) plus a reference (for the spec). A tutorial only if the feature is a new entry point users learn from scratch.
- **"Explain how X works"** is ambiguous between how-to and explanation. *"How does it work"* (mechanism) → explanation. *"How do I use it"* (procedure) → how-to. Ask if you can't tell from context.
- **"Add a section to existing docs"** — match the mode of the existing doc; don't introduce a different mode mid-page.

## Diagrams in docs

For diagrams inside any of the four modes:

- **Mermaid** (flowcharts, sequence diagrams, class diagrams, gantt) → `markdown-mermaid` skill in this plugin. Renders natively on GitHub and most MD viewers.
- **D2** (architecture, sequence_diagram, sql_table, class, grid, c4 — the full Terrastruct DSL) → `d2` skill in this plugin. More powerful, requires the `d2` CLI to render to SVG/PNG.

For C4 architecture / ADR / OpenAPI work, that's a different kind of documentation entirely — use the `architecture-docs` skill in this plugin, not Diataxis.

## Why this skill exists

The four-mode separation is the substance. The voice differences (encouraging in tutorials, terse in how-tos, factual in references, thoughtful in explanations) fall out of the mode choice — once you've picked the right mode, the right register comes with it. Writing in mode is more about what *not* to include than what to add.
