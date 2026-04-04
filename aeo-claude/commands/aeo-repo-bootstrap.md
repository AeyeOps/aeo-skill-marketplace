---
name: aeo-repo-bootstrap
version: 0.1.0
description: Bootstrap or augment a repository with governance scaffold — AGENTS.md tree, docs layout, gitignore additions. Idempotent init or augment mode.
argument-hint: "[optional guidance]"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Repository Governance Bootstrap

Optional freeform guidance (used as prioritization context only):
$ARGUMENTS

## Step 1: Detect Mode and Read State

Glob for `**/AGENTS.md` and `docs/*/` directories. Check for `.git/` and `.gitignore`. Classify as `init` if most required AGENTS.md files are missing, `augment` if some exist. Read every existing AGENTS.md file because merge behavior in Step 2 requires comparing section headings.

## Step 2: Create or Merge Scaffold

Required directories: `docs/roadmap/`, `docs/adr/`, `docs/architecture/`, `docs/modules/`, `docs/issues/`, `docs/kb/`, `tmp/`, `_archive/`

Required AGENTS.md files: `AGENTS.md`, `docs/AGENTS.md`, `docs/roadmap/AGENTS.md`, `docs/adr/AGENTS.md`, `docs/architecture/AGENTS.md`, `docs/modules/AGENTS.md`, `docs/issues/AGENTS.md`, `docs/kb/AGENTS.md`, `tmp/AGENTS.md`, `_archive/AGENTS.md`

For each AGENTS.md:
- If absent, create with canonical generic content from the `<reference>` block.
- If present, section-aware merge by Markdown heading — preserve project-specific sections, add missing canonical ones.
- Normalize both sides before comparison (trim whitespace, collapse blank lines, compare non-empty line sets per heading).
- `additive` = one side is a subset of the other. `material_conflict` = both sides have unique lines.
- On material conflict, back up first: `<original>.bak.aeo.NNN` (zero-padded, e.g., `001`). No backups when no conflict.
- Do not create sample artifacts, demo content, or `docs/issues/issues_backlog.csv`.

## Step 3: Update .gitignore

Ensure `.gitignore` exists and includes `tmp/` and `_archive/`. Do not duplicate existing entries or remove user entries. Detect project language from file signals and add appropriate entries:

| Signal | Ignore entries |
|--------|---------------|
| pyproject.toml, .py files | `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/` |
| package.json, .ts/.js files | `node_modules/`, `dist/`, `build/`, `coverage/` |
| go.mod, .go files | `bin/`, `*.test`, `coverage.out` |
| Cargo.toml, .rs files | `target/` |
| (always) | `.DS_Store`, `.idea/`, `.vscode/`, `*.swp` |

## Step 4: Git Init (if needed)

If `.git` is missing, initialize with `git init -b main`. If that flag is unavailable, run `git init` then set the default branch to `main`.

## Step 5: Validate

After all edits, verify:
1. All 10 required AGENTS.md files exist.
2. All 8 required directories exist.
3. `.gitignore` includes `tmp/` and `_archive/`.
4. No `docs/issues/issues_backlog.csv` was created.
5. If git was initialized this run, current branch is `main`.
6. Idempotency: run the same logic again and confirm no new changes or backups are produced.

## Step 6: Output Report

```
- Mode: init | augment (with rationale)
- Files: created | merged | backed_up | unchanged (grouped)
- Validation: pass/fail per check
- Idempotency: pass/fail
- Chat-only reorg proposal:
  - Current gaps relative to the scaffold
  - Target organization
  - Prioritized move/cleanup sequence
  - Key risks and rollback notes
```

The reorg proposal is advisory only — do not execute it.

<reference>
Canonical AGENTS.md section headings per file. Use concise, operational wording — machine-readable structure over narrative.

Root AGENTS.md:
- Agent-First Repository Assumption
- Completion and Validation Discipline
- Instrumentation Discipline
- Audience
- Instruction Precedence
- Project Definition of Done
- Project Interaction Guardrails
- Doc Discipline
- Documentation Noise Policy
- Docs Directory Contract
- Archive Contract
- Interim Files

docs/AGENTS.md: Purpose, Subdirectory Contracts (roadmap, adr, architecture, modules, issues, kb), Lifecycle Rules, Quality Rules

docs/roadmap/AGENTS.md: Scope, Role in Lifecycle, Content Contract, Exit Criteria

docs/adr/AGENTS.md:
- Scope
- Numbering and Naming
- ADR Content Contract
- Mutation Rules
- Decision Hygiene

docs/architecture/AGENTS.md: Scope, ADR Relationship, Content Rules, Boundaries

docs/modules/AGENTS.md: Scope, Placement Rules, Lifecycle, Quality Rules

docs/issues/AGENTS.md: Scope, Storage Model, Lifecycle, Field Hygiene — keep intentionally lightweight

docs/kb/AGENTS.md:
- Scope
- Freshness and Date Discipline
- Research Method
- Storage Model
- Minimum Metadata for Topic Files
- Tracking Policy

tmp/AGENTS.md: Purpose, Usage Rules, Cleanup Expectations

_archive/AGENTS.md:
- Purpose
- Tracking Policy
- Model Usage Policy
- Provenance Rule
- Mutation Rules
</reference>

<principles>
Genericity — all canonical content should be framework-generic and repository-agnostic. Reject and rewrite if it includes domain-specific business nouns, org identifiers, pipeline artifact names, project-specific env vars, or year-specific identifiers. User guidance is prioritization context only.
</principles>

## Constraints

- Operate on `.` only because targeting other paths risks modifying unrelated repositories.
- Auto-detect init vs augment from repo state.
- Avoid overwriting destructively — use merge behavior for existing files.
- Do not create sample artifacts or demo content because they become stale noise.
- Keep all generated policy text generic.
- Finish with a chat-only reorganization proposal (do not execute it).
