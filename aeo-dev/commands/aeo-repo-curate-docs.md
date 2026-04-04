---
name: aeo-repo-curate-docs
version: 0.1.0
description: Reconcile roadmap and issue docs against implemented code — retire completed items to archive, trim partial implementations, update issue trackers
argument-hint: "[optional guidance]"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Agent
---

# Roadmap & Issues Curation

Optional freeform guidance (used as prioritization context only):
$ARGUMENTS

## Step 1: Discovery & Preflight

Read governance context: `AGENTS.md`, `docs/AGENTS.md`, `docs/roadmap/AGENTS.md`, `docs/issues/AGENTS.md`, `_archive/AGENTS.md`.

Build candidate sets:
- Roadmap candidates: `docs/roadmap/**/*` excluding any `AGENTS.md` files.
- Issues candidates: `docs/issues/**/*` excluding any `AGENTS.md` files.

Detect issues storage mode from existing artifacts:
- `row_based`: structured tracker files (CSV/TSV/JSONL) with issue rows.
- `file_based`: individual issue documents.
- `none_detected`: no issue artifacts exist.

If no roadmap and no issue candidates exist, return a no-op report with evidence and stop.

## Step 2: Fast-Path Idempotency Check

Before deep analysis, check each artifact for prior reconciliation:
- Source file starts with a reconciliation note.
- Matching destination already exists for the source slug/title.
- Evidence signals are unchanged relative to the current repo snapshot.

If all three hold, classify as `unchanged` for this run and skip deep analysis.

## Step 3: Evidence Collection

For large candidate sets, spawn focused Agent threads for parallel inspection. Prefer targeted checks in `docs/`, `src/`, and `tests/` over broad recursive scans — keep search scope tight.

Per roadmap artifact, collect:
- Implementation signals: matching code paths, test coverage, config entries, runtime docs.
- Unresolved-gap signals: missing acceptance criteria coverage, deferred work markers, TODO/FIXME annotations referencing the roadmap item.
- Superseded signals: newer implementation or docs that replace the original concern.
- Existing destination matches in `docs/architecture/`, `docs/modules/`, `docs/issues/`.

Apply evidence-first reasoning — when uncertain, do not archive.

## Step 4: Classify

Assign each artifact exactly one classification.

<reference name="classification-decision-tree">
Decision rules:
- `implemented`: strong implementation signals, no material unresolved gaps.
- `partially_implemented`: some implementation signals AND material gaps remain.
- `still_applicable_unimplemented`: no implementation signals, concern still applicable.
- `not_applicable_or_superseded`: concern clearly obsolete or replaced.

Coverage rule for roadmap items with explicit deliverables:
- All deliverables have concrete implementation signals -> `implemented`.
- At least one does and at least one does not -> `partially_implemented`.
- None have signals and concern is still applicable -> `still_applicable_unimplemented`.

Conservative fallback on ambiguity: `still_applicable_unimplemented`.
</reference>

## Step 5: Execute Actions

Roadmap actions by classification:
- `implemented`: migrate concise essence to destination docs, move source to archive.
- `partially_implemented`: migrate implemented portion to destination docs, rewrite source to remaining scope only. Prepend: `> Note: implemented portions were reconciled out; remaining scope below.` Archive if no applicable remainder survives the rewrite.
- `still_applicable_unimplemented`: keep in roadmap, optionally normalize for clarity.
- `not_applicable_or_superseded`: move source to archive.

Issues actions (format-adaptive):
- `row_based`: update rows in place for status transitions (resolved, not_applicable).
- `file_based`: update active files or move resolved ones to archive.
- `none_detected`: keep unresolved scope in roadmap remainder because inventing a new schema disrupts existing workflows.

Destination routing for implemented content:
- `docs/architecture/` for cross-cutting or system-level concerns.
- `docs/modules/` for module-specific behavior.
- `docs/issues/` for deferred gaps that remain unresolved.

Destination file matching order:
1. Exact filename stem match in the target directory.
2. Exact title heading match inside existing files.
3. Create new file: `reconciled-<source-slug>.md` in the selected directory.

When updating existing files, append or update a concise section keyed by source slug. Avoid duplicating equivalent content. Keep entries implementation-specific — no speculative roadmap prose.

<workflow name="archive-mechanics">
Path formulas:
- `docs/roadmap/<R>` -> `_archive/docs/roadmap/<R>`
- `docs/issues/<I>` -> `_archive/docs/issues/<I>`

Rules:
- Preserve the relative path structure under `_archive/` so provenance is self-documenting.
- Avoid duplicating `docs/roadmap` or `docs/issues` segments in the archive destination.
- If archive destination already exists, append a deterministic suffix: `.reconciled.NNN` (001, 002, ...).
- Create intermediate directories as needed.
- Avoid restoring from archive automatically because reconciliation is a one-way operation.
</workflow>

## Step 6: Validate & Report

After reconciliation, verify all mutations and produce a structured report:

```
- Mode: roadmap_only | issues_only | roadmap_and_issues | no_op
- Per-artifact classification table with evidence summary
- Action ledger: updated | moved_to_archive | created | unchanged
- Archive provenance check: every moved item has correct normalized path
- Governance integrity: no AGENTS.md files were modified as reconciliation artifacts
- Idempotency: running again produces no additional mutations
- Follow-up recommendations (only if gaps remain)
```

<principles>
Genericity — all reconciled content should remain repository-agnostic. Reject and rewrite output that introduces client identifiers, domain jargon not present in the codebase, or hardcoded environment assumptions.
</principles>

## Constraints

- Operate on `.` only because targeting other paths risks modifying unrelated repositories.
- Reconcile from `docs/roadmap/` and `docs/issues/` only, excluding AGENTS.md policy files.
- Avoid deleting reconciled source artifacts directly — use archive moves with provenance.
- Do not force a new issue schema when one already exists because it disrupts existing workflows.
- Keep outputs concise, operational, and implementation-grounded.
- If user guidance is provided, use it as prioritization context only — do not relax safety constraints.
