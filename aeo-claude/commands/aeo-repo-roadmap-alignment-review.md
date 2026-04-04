---
name: aeo-repo-roadmap-alignment-review
version: 0.1.0
description: Read-only alignment check — compare current implementation against roadmap docs, flag objective drift, and recommend prioritized next steps
argument-hint: "[focus area or roadmap doc]"
allowed-tools: Read, Glob, Grep, Bash, Agent
---

# Roadmap Alignment Review

Optional focus area (used as prioritization context only):
$ARGUMENTS

If no focus is provided, review the overall roadmap and implementation state.

This is an analysis-only roadmap review. Do not run tests, linters, builds, or modify files. Do not produce validation evidence or validation summaries.

## Step 1: Discover Roadmap and Governance Docs

Read AGENTS.md files at root, `docs/`, and `docs/roadmap/` for governance context. Glob `docs/roadmap/*.md` for roadmap artifacts — do not hardcode specific filenames because different repos have different roadmap documents. If a focus area is specified, prioritize matching docs; otherwise review all discovered roadmap files.

## Step 2: Inspect Implementation Evidence

Spawn Explore agents for parallel inspection of these areas: `src/`, `tests/`, `docs/architecture/`, `docs/adr/`, `docs/modules/`, `schemas/`, and top-level config files. Look at actual implementation footprint, not just scaffolded directories. Use `git status` only if it helps separate active work from untouched plans — do not let uncommitted state dominate the assessment.

## Step 3: Assess Alignment

<principles>
Distinguish between roadmap intent that is merely scaffolded and work that is substantively implemented because surface-level directory structure can mislead. Check for sequencing drift (implementation order diverged from roadmap phasing) and architectural drift (implementation choices differ from roadmap assumptions). Identify docs that belong in implemented-state records (docs/architecture/, docs/adr/) rather than active roadmap. Base all claims on repository inspection, not assumptions.
</principles>

For each roadmap document:
- Classify as `fully implemented`, `partially implemented`, or `not yet implemented`.
- Cite specific evidence from the repository.
- Recommend exactly one next action: retire from active roadmap, promote to `docs/adr/` or `docs/architecture/`, or keep active with remaining scope named.

Read roadmap sources before drawing implementation conclusions because assumptions without evidence lead to incorrect alignment assessments. If coverage is partial, inspect at least one additional relevant file before concluding.

## Step 4: Output Report

Use this structure exactly:

```
## Objective Check
- Restated objective: (plain language from roadmap, not assumption)
- Current evidence:
- Objective drift risk: low | medium | high

## Alignment Status
- Overall: aligned | partially aligned | off-track
- Why: (one sentence)
- Major gaps or sequencing concerns:

## Roadmap Coverage
For each fully or partially implemented doc:
- [doc path] — fully/partially implemented
- Evidence:
- Recommended action:

For not-yet-implemented docs that materially affect the assessment:
- [doc path] — not yet implemented
- Why it matters now:

## Next 3 Recommendations
1. ...
2. ...
3. ...

## User Check-In
(Short paragraph: is the project aligned and on track? Ask whether these objectives and priorities are still the intended target.)
```

## Constraints

- Operate on `.` only because targeting other paths risks reviewing unrelated repositories.
- Analysis-only — do not modify files, run tests, or produce validation evidence.
- Sequence the review so objective understanding comes before gap analysis and recommendations.
- If user guidance is provided, use it as focus context only.
