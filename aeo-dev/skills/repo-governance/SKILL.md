---
name: repo-governance
description: >
  Guide the user through repository documentation governance using the aeo-repo-* command
  family. Use when the user asks about AGENTS.md scaffolding, roadmap alignment reviews,
  doc curation, repo bootstrap, or wants to know which governance command to run next.
  Covers lifecycle sequencing: bootstrap a scaffold, iterate with alignment reviews and
  curation passes, sanitize before publishing.
---

# Repository Governance

## Purpose

Keep repository documentation honest. Code evolves faster than the docs that describe it —
roadmap items get implemented but never retired, architecture docs describe plans instead of
reality, and issue trackers accumulate resolved items. This command family closes that gap
by providing a repeatable lifecycle: establish structure, check alignment, curate what's
stale, and verify before sharing.

## Intent

Documentation governance is not about volume — it's about signal. A repository where
`docs/roadmap/` only contains active plans and `docs/architecture/` only contains implemented
designs is more useful than one with comprehensive but stale artifacts. These commands treat
documentation as a living system with an explicit lifecycle: planning docs are born in
`roadmap/`, mature into `architecture/` or `modules/` when implemented, and retire to
`_archive/` with provenance when they no longer reflect reality.

The governance scaffold uses `AGENTS.md` policy files because they give every directory a
contract — what belongs there, how content enters and exits, and what quality means in that
context. This helps both human contributors and AI agents make consistent decisions about
where to put things and when to move them.

## Command Family

| Command | Verb | Modifies files? |
|---------|------|-----------------|
| `/aeo-repo-bootstrap` | Establish the governance scaffold | Yes |
| `/aeo-repo-roadmap-alignment-review` | Diagnose implementation vs roadmap drift | No |
| `/aeo-repo-curate-docs` | Retire, trim, and archive stale docs | Yes |
| `/aeo-repo-sanitize` | Scan for secrets, PII, supply-chain risk | Yes (with approval) |

## Lifecycle

### 1. Bootstrap (once)

`/aeo-repo-bootstrap` creates the scaffold: `AGENTS.md` policy files at 10 locations,
`docs/` subdirectories by purpose, `tmp/` and `_archive/` utility directories, and
language-aware `.gitignore` additions. Idempotent — detects whether to initialize or
augment based on what already exists, and merges rather than overwrites.

Run this first. The other governance commands assume this structure.

### 2. Review → Curate (iterative)

Two commands form a feedback loop:

```
    /aeo-repo-roadmap-alignment-review
    (read-only: identifies drift, stale docs, gaps)
                    │
                    ▼
    /aeo-repo-curate-docs
    (acts: archives done, trims partial, updates issues)
                    │
                    ▼
              commit, repeat
```

**Alignment review** is safe to run anytime because it only reads. It compares implementation
evidence against roadmap intent, flags drift, and recommends three prioritized next steps.
Use it as a status pulse — after a sprint, before planning, or when docs feel stale.

**Curate docs** acts on what the review found. It classifies each roadmap artifact against
the codebase using evidence-first reasoning, then:
- Archives fully implemented items to `_archive/` with path provenance
- Trims partially implemented docs to remaining scope only
- Leaves unimplemented items in place (conservative default)
- Updates issue trackers in whatever format they already use

Typical cadence: review after each milestone, curate when review flags stale artifacts,
commit, review again to confirm docs match reality.

### 3. Sanitize (before sharing)

`/aeo-repo-sanitize` is independent of the governance scaffold — it works on any repository.
Run before making a repo public, pushing to a shared remote, or onboarding collaborators.

<reference>
Scaffold structure created by bootstrap:

repo/
├── AGENTS.md                     # Root governance policy
├── docs/
│   ├── AGENTS.md                 # Docs directory contract
│   ├── roadmap/   + AGENTS.md    # Active planning (→ architecture when done)
│   ├── adr/       + AGENTS.md    # Architecture decision records
│   ├── architecture/ + AGENTS.md # Implemented system design
│   ├── modules/   + AGENTS.md    # Per-module documentation
│   ├── issues/    + AGENTS.md    # Issue tracking (row or file based)
│   └── kb/        + AGENTS.md    # Knowledge base
├── tmp/           + AGENTS.md    # Ephemeral working files (gitignored)
└── _archive/      + AGENTS.md    # Retired artifacts with provenance (gitignored)

Document lifecycle flow:
  roadmap/ → (implemented) → architecture/ or modules/
  roadmap/ → (obsolete) → _archive/docs/roadmap/
  issues/  → (resolved) → _archive/docs/issues/
</reference>

## When to Suggest Each Command

| User signal | Suggest |
|-------------|---------|
| Setting up a new project, wants structure | `/aeo-repo-bootstrap` |
| Asks "are we on track?" or "what's drifted?" | `/aeo-repo-roadmap-alignment-review` |
| Finished a milestone, wants to clean up docs | `/aeo-repo-curate-docs` |
| Preparing to publish or share the repo | `/aeo-repo-sanitize` |
| Says "docs feel stale" or "roadmap is outdated" | Alignment review first, then curate |
| Asks which command to run next | Check if scaffold exists → if not, bootstrap; if yes, alignment review |

## Design Principles

These inform how the commands behave and why — useful context when the user asks "why did
it do X?" or wants to customize the approach.

- **Evidence over assumption**: Curate-docs inspects actual code paths before classifying a
  roadmap item, because surface-level directory matches mislead. Ambiguous cases default to
  keeping the item active rather than archiving prematurely.
- **Archive with provenance**: Retired docs move to `_archive/` mirroring their source path
  (`docs/roadmap/x.md` → `_archive/docs/roadmap/x.md`) because being able to trace where
  something came from matters more than saving directory depth.
- **Format-adaptive**: Curate-docs detects whether issues use row-based trackers (CSV/JSONL)
  or file-based docs and adapts its actions accordingly, because imposing a new schema on an
  existing tracker disrupts workflows.
- **Generic by default**: Bootstrap creates framework-agnostic policy content. Projects
  customize their AGENTS.md files over time — the scaffold provides structure, not opinions
  about the project's domain.
- **Read-only diagnostics are free**: Alignment review modifies nothing, so suggest it
  liberally. Curate-docs modifies files, so confirm the user's intent before running it.
