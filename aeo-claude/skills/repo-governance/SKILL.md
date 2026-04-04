---
name: repo-governance
description: >
  Guide for the aeo-repo-* command family that manages repository documentation governance.
  Use when the user asks about AGENTS.md scaffolding, roadmap alignment, doc curation,
  repo bootstrap, or wants to know which governance command to run next. Covers the
  lifecycle: bootstrap a scaffold, iterate with curation and alignment reviews, sanitize
  before publishing.
---

# Repository Governance Commands

Four commands that manage documentation governance as a lifecycle. They share an opinionated
structure: `AGENTS.md` policy files, `docs/` subdirectories by purpose, and `_archive/` for
retired artifacts.

## Command Family

| Command | Purpose | Modifies files? |
|---------|---------|-----------------|
| `/aeo-repo-bootstrap` | Create or augment the governance scaffold | Yes |
| `/aeo-repo-curate-docs` | Reconcile roadmap/issues docs against implementation | Yes |
| `/aeo-repo-roadmap-alignment-review` | Check implementation vs roadmap alignment | No (read-only) |
| `/aeo-repo-sanitize` | Security, PII, and supply-chain scan before push | Yes (with approval) |

## Lifecycle

### First use: Bootstrap

Run `/aeo-repo-bootstrap` to set up the scaffold. This creates:
- `AGENTS.md` policy files at root and in each `docs/` subdirectory
- Directory structure: `docs/roadmap/`, `docs/adr/`, `docs/architecture/`, `docs/modules/`, `docs/issues/`, `docs/kb/`
- Utility directories: `tmp/`, `_archive/`
- Language-aware `.gitignore` additions

The command is idempotent — it detects `init` (scaffold absent) vs `augment` (partially present)
and merges rather than overwrites.

### Ongoing: Review and Curate

Once the scaffold exists, two commands form an iteration loop:

```
                ┌──────────────────────────┐
                │  /aeo-repo-roadmap-      │
                │  alignment-review        │
                │  (read-only diagnostic)  │
                └────────────┬─────────────┘
                             │ identifies drift,
                             │ stale docs, gaps
                             ▼
                ┌──────────────────────────┐
                │  /aeo-repo-curate-docs   │
                │  (retire, trim, archive) │
                └────────────┬─────────────┘
                             │ acts on findings
                             │
                             ▼
                     commit changes,
                     loop back to review
```

**Alignment review** answers: "Are we building what the roadmap says? What's drifted?"
It produces a structured report with objective check, coverage table, top 3 recommendations,
and a user check-in. Run this when you want a status pulse.

**Curate docs** answers: "What roadmap items are done? What should be archived?"
It classifies each roadmap artifact (`implemented`, `partially_implemented`,
`still_applicable_unimplemented`, `not_applicable_or_superseded`), then archives completed
items and trims partially-done docs to remaining scope. Run this after a milestone or when
alignment review flags stale roadmap docs.

Typical iteration pattern:
1. Run alignment review to assess current state
2. If stale or completed roadmap docs are identified, run curate-docs
3. Commit the curation results
4. Run alignment review again to confirm the docs reflect reality

### Before publishing: Sanitize

Run `/aeo-repo-sanitize` before making a repo public or pushing to a shared remote.
This scans for secrets, PII, local environment leaks, and supply-chain risks.
It presents findings with severity ratings and grouped remediation options.

## When to Suggest Each Command

| User intent | Command |
|-------------|---------|
| "Set up docs structure" / "add AGENTS.md" / "bootstrap governance" | `/aeo-repo-bootstrap` |
| "What's the status of our roadmap?" / "are we on track?" / "alignment check" | `/aeo-repo-roadmap-alignment-review` |
| "Clean up roadmap docs" / "archive what's done" / "retire completed items" | `/aeo-repo-curate-docs` |
| "Check for secrets" / "prepare for public push" / "security scan" | `/aeo-repo-sanitize` |
| "I just finished a major feature" | Alignment review first, then curate-docs |
| "We haven't touched our docs in a while" | Alignment review to assess, curate-docs to act |

## The Scaffold Structure

The governance scaffold assumes this directory layout:

```
repo/
├── AGENTS.md                    # Root governance policy
├── docs/
│   ├── AGENTS.md                # Docs directory contract
│   ├── roadmap/                 # Active planning docs
│   │   └── AGENTS.md
│   ├── adr/                     # Architecture decision records
│   │   └── AGENTS.md
│   ├── architecture/            # Implemented system design
│   │   └── AGENTS.md
│   ├── modules/                 # Per-module documentation
│   │   └── AGENTS.md
│   ├── issues/                  # Issue tracking (row or file based)
│   │   └── AGENTS.md
│   └── kb/                      # Knowledge base
│       └── AGENTS.md
├── tmp/                         # Ephemeral working files (gitignored)
│   └── AGENTS.md
└── _archive/                    # Retired artifacts with provenance (gitignored)
    └── AGENTS.md
```

Each `AGENTS.md` file defines the policy for its directory — what belongs there, lifecycle
rules, and quality expectations. The bootstrap command creates these with generic, framework-
agnostic content. Projects customize them over time.

## Key Design Decisions

- **`docs/roadmap/`** holds active planning. Once implemented, content moves to `docs/architecture/` or `docs/modules/`.
- **`_archive/`** preserves provenance — path structure mirrors the source (`_archive/docs/roadmap/<file>`).
- **Curate-docs uses evidence-first reasoning** — it inspects actual code before classifying. Ambiguous cases default to `still_applicable_unimplemented` rather than premature archival.
- **Alignment review is read-only** — it diagnoses but does not modify, so it's safe to run anytime.
- **Sanitize is independent** — it doesn't require the governance scaffold. Works on any repo.
