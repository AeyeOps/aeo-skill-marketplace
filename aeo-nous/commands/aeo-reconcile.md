 ---
description: Reconcile nous stores — prune stale, resolve conflicts, deduplicate, fix lens bleed
argument-hint: [max-entries-per-lens]
disable-model-invocation: true
model: opus
---

# Nous Reconciliation

Curate the project's nous stores by pruning entries that have gone stale, conflict with each other, or say the same thing. What remains after reconciliation is the durable memory — the injection window gets higher signal as noise is removed.

## Flush pending inbox fragments

Before reconciling, flush any inbox fragments so the encoded files contain all extracted entries. This prevents reconciliation from missing entries that were extracted but not yet flushed.

Run `flush_inbox.sh` from the plugin's `scripts/` directory, passing the project root as the argument.

## Discover lenses

Grep for `ExtractionLens(` in the plugin's `hooks/lenses/` directory to find all lens definition files. Collect the file paths for handoff to agents.

## Parallel reconciliation

Each agent processes at most **$ARGUMENTS** entries from its JSONL file (default: 50 if no argument provided), starting after its reconciliation cursor. This bounds context usage per agent and allows incremental reconciliation across multiple invocations.

Launch one opus agent per lens, all in parallel. Each agent's prompt should contain:

<agent-prompt>

Curate a nous JSONL store by scanning its oldest entries against current project state. Nous entries are injected into future sessions as context. Stale or misleading entries waste injection budget and can misdirect future agents. Your job: identify entries to prune or consolidate by assigning weights. Do not flag entries for content edits that don't reduce the total count — the goal is compaction, not copy-editing.

<lens-files>
File paths to all lens definition files — needed for detecting lens bleed across stores.
</lens-files>

<assigned-lens>
The file path to THIS agent's lens definition file — identifies which JSONL store to reconcile.
</assigned-lens>

<max-entries>
The number of entries to scan from the oldest end of the JSONL file.
</max-entries>

<weight-rubric>
Every entry you scan gets a weight `w` (0.0–1.0) and `w_at` (current ISO 8601 timestamp). Read `WEIGHT_RUBRIC` from `nous.py` in the plugin's hooks directory — it defines weight bands, promotion/demotion signals, and assignment rules. Use it to ground every weight decision.

After scanning, set `w` and `w_at` on each entry. For entries you'd prune, set `w = 0.0`. For consolidations, mark originals `w = 0.0` and append a new merged entry with an appropriate weight. Entry content is immutable — only `w` and `w_at` change. The coordinator's Python code sweeps entries at `w <= 0.15` to the discard file after you finish.
</weight-rubric>

<detection-criteria>
- **Stale** — overtaken by project changes, completed work, or moved paths/versions. Includes self-contradictory entries and orphaned SUPERSEDES references. Verify against actual project state before flagging.
- **Misdirecting** — entry would cause a future agent to use the wrong path, flag, value, or assumption when injected into session context. Evaluate each entry as a prompt fragment: what will an agent DO if it reads this?
- **Conflicting** — two entries stating opposite things; verify which is currently true. When guidance conflicts with implementation, keep the entry matching actual code and flag the gap separately.
- **Duplicated** — same insight restated across sessions; keep the most complete version
- **Lens bleed** — entry belongs in a different lens based on the domain boundaries. Flag which lens it should move to.
- **CLAUDE.md correction** — entry exists to compensate for a wrong claim in a CLAUDE.md file. Verify the claim against actual project state. Flag for the coordinator with the file path and what needs fixing.

If a lens has no actionable findings, report that cleanly — don't force findings where none exist.
</detection-criteria>

<applying>
Set `w` and `w_at` on each scanned entry in the JSONL store. Do not touch the discard file — the coordinator's Python code handles that after you finish.

Prune means set `w = 0.0` and `w_at` to the current timestamp on the entry.

For consolidations, set `w = 0.0` on the originals and append one clean merged entry at the end of the JSONL file with an appropriate weight. The consolidated entry should read as if it were always a single observation — no lineage commentary, no process notes, no SUPERSEDES references.

For lens bleed, if the entry is also stale, misdirecting, or otherwise pruneable — just set `w = 0.0`. Only flag lens bleed entries that are still valid; leave them in place for the coordinator to decide disposition.
</applying>

<workflow>
1. Ground yourself: understand the project, both lens domains (from the lens source files), how entries are injected (from `nous.py` in the same plugin directory), and the JSONL store contents. Parallelize exploration and source reading.
2. Read the reconciliation cursor from `.claude/nous/`. The cursor filename is `{store_stem}.reconcile_cursor.json` where `{store_stem}` matches the stem of the lens's `encoded_path` JSONL file. Schema: `{"reviewed_through_ts": "<ISO 8601>"}`. If it exists, resume scanning after its `reviewed_through_ts` value. If it doesn't exist, start from the oldest entry.
3. Scan up to max-entries from the cursor position, using exploration results as ground truth. When an entry references something the exploration didn't cover, verify with a targeted Read or Glob before making a staleness call.
4. Set `w` and `w_at` on each scanned entry (add the fields if they don't exist). For consolidations, also append the merged entry. Record: entry content, assigned weight, issue type.
5. After scanning, write the cursor file with `{"reviewed_through_ts": "<ts of last scanned entry>"}`. If no entries remain beyond the scan window, delete the cursor file — previously-clean entries can go stale as the project evolves, so the cycle resets.
6. Return a summary of changes applied, cursor state (advanced / reset), and any lens bleed or CLAUDE.md findings for the coordinator.
</workflow>

</agent-prompt>

<coordinator>

Agents assign weights on entries. The coordinator collects summaries, handles cross-cutting follow-ups, then runs the deterministic sweep.

## Summary

Present each agent's summary grouped by lens. Show entry counts: scanned, weighted, consolidated, flagged.

## Cross-store lens bleed

For every entry agents flagged as lens bleed: if a better-suited lens exists, move it there — adapt the schema to the target lens's format and rewrite the content to match its voice. If no lens is a good fit, discard it (`w = 0.0`). Either way, set `w = 0.0` on the original in the source store.

## CLAUDE.md mismatches

When agents flag a CLAUDE.md claim contradicted by verified ground truth (e.g., wrong hardware specs, stale paths, incorrect counts), fix the CLAUDE.md and set `w = 0.0` on the correction entry.

## Post-agent sweep

After all agents finish and cross-cutting work is done, run `reconcile_nous_entries.sh` from the plugin's `scripts/` directory, passing the project root as the argument. This sweeps all entries with `w <= 0.15` to the discard files and reports counts.

</coordinator>
