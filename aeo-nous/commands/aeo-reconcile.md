 ---
description: Reconcile nous stores — prune stale, resolve conflicts, deduplicate, fix lens bleed
argument-hint: [max-entries-per-lens]
disable-model-invocation: true
model: opus
---

# Nous Reconciliation

Curate the project's nous stores by pruning entries that have gone stale, conflict with each other, or say the same thing. What remains after reconciliation is the durable memory — the injection window gets higher signal as noise is removed.

## Resolve plugin path

Read `~/.claude/plugins/installed_plugins.json` and extract the `installPath` for `aeo-nous@aeo-skill-marketplace`:
```
jq -r '.plugins["aeo-nous@aeo-skill-marketplace"][0].installPath' ~/.claude/plugins/installed_plugins.json
```
All subsequent references to `$NOUS_PLUGIN` mean this resolved path.

## Flush pending inbox fragments

Before reconciling, flush any inbox fragments so the encoded files contain all extracted entries. This prevents reconciliation from missing entries that were extracted but not yet flushed.

Run `$NOUS_PLUGIN/scripts/flush_inbox.sh`, passing the project root as the argument.

## Discover lenses

Grep for `ExtractionLens(` in `$NOUS_PLUGIN/hooks/lenses/` to find all lens definition files. Collect the file paths for handoff to agents.

## Parallel reconciliation

Each agent processes at most **$ARGUMENTS** entries from its JSONL file (default: 50 if no argument provided), starting after its reconciliation cursor. The cursor file lives in the same directory as the JSONL store (e.g., `.claude/nous/knowledge/cortex.reconcile_cursor.json` alongside `cortex.jsonl`). This bounds context usage per agent and allows incremental reconciliation across multiple invocations.

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
Every entry you scan gets a weight `w` (0.0–1.0). Read `WEIGHT_RUBRIC` from `$NOUS_PLUGIN/hooks/nous.py` — it defines weight bands, promotion/demotion signals, and assignment rules. Use it to ground every weight decision.

The rubric has a **verification gate**: bands at w >= 0.45 (moderate, solid, foundational) require tool-verified confirmation. Each band has a `verification` field — read it. If you cannot verify an entry's claims with a Read/Grep/Glob call, cap its weight at 0.35 (narrow band ceiling).

**w_at rules**: Only update `w_at` (ISO 8601 datetime, e.g. `2026-03-04T14:30:00.000Z`) on entries you individually verified with a tool call. Unverified entries keep their existing `w_at` — a fresh timestamp signals fresh verification and affects injection priority via decay math. Pruned entries (w = 0.0) always get a current `w_at`.

After scanning, set `w` (and `w_at` where applicable) on each entry. For consolidations, mark originals `w = 0.0` and append a new merged entry with an appropriate weight. Entry content is immutable — only `w` and `w_at` change. The coordinator's Python code sweeps entries at `w <= 0.15` to the discard file after you finish.
</weight-rubric>

<detection-criteria>
- **Stale** — overtaken by project changes, completed work, or moved paths/versions. Includes self-contradictory entries and orphaned SUPERSEDES references. Verify against actual project state before flagging.
- **Misdirecting** — entry would cause a future agent to use the wrong path, flag, value, or assumption when injected into session context. Evaluate each entry as a prompt fragment: what will an agent DO if it reads this?
- **Conflicting** — two entries stating opposite things; verify which is currently true. When guidance conflicts with implementation, keep the entry matching actual code and flag the gap separately.
- **Duplicated** — same insight restated across sessions; keep the most complete version
- **Lens bleed** — entry belongs in a different lens based on the domain boundaries. Flag which lens it should move to.
- **CLAUDE.md correction** — entry exists to compensate for a wrong claim in a CLAUDE.md file. Verify the claim against actual project state. Flag for the coordinator with the file path and what needs fixing.
- **Off-project** — entry describes facts or guidance about systems, tools, or files outside the project scope. Check `suggested_target` paths against the project root — targets outside the project tree are strong signals. These waste injection budget and dilute project-specific context.

If a lens has no actionable findings, report that cleanly — don't force findings where none exist.
</detection-criteria>

<applying>
Set `w` on each scanned entry in the JSONL store. Only update `w_at` on entries you verified with a tool call or pruned to w = 0.0. Do not touch the discard file — the coordinator's Python code handles that after you finish.

The JSONL stores are `jq`-native. Here are some ways to work with them efficiently:
- Cross-cursor dedup: `jq -c 'select(.content | test("keyword"))' $STORE`
- Stale high-weight: `jq -c 'select(.w >= 0.45 and .w_at < "DATE")' $STORE`
- Weight distribution: `jq '[.w // 0] | group_by(. * 10 | floor / 10) | map({w: .[0], n: length})' $STORE -s`
- Surgical update: `jq -c 'if input_line_number == N then .w = W | .w_at = "TS" else . end' $STORE`
- Count beyond cursor: `jq -c 'select(.ts > "CURSOR_TS")' $STORE | wc -l`

Prune means set `w = 0.0` and `w_at` to the current timestamp on the entry.

**Prune tagging** — when pruning, set `_prune` to categorize the reason. The sweep routes entries to separate files based on this field:
- `"off_project"` → `<stem>.nonproject.jsonl` — valid content that belongs to a different project
- `"lens_bleed"` → `<stem>.misclassified.jsonl` — valid content that doesn't belong in this lens
- No `_prune` field → `<stem>.discarded.jsonl` — generic low-value (stale, duplicate, misdirecting, etc.)

Off-project and lens-bleed entries are routed out regardless of their weight — they may be high-value content that simply doesn't belong in this store. Keep their existing `w` intact so downstream processes can assess their value.

For consolidations, set `w = 0.0` on the originals and append one clean merged entry at the end of the JSONL file with an appropriate weight. The consolidated entry should read as if it were always a single observation — no lineage commentary, no process notes, no SUPERSEDES references. If you identify a consolidation candidate, execute it — do not defer to natural decay.

For lens bleed: if the entry is also stale or pruneable, set `w = 0.0` and `_prune = "lens_bleed"`. If it's still valid, lift-and-shift it — set `_prune = "lens_bleed"` on the source entry (keep its existing `w`) and append the entry as-is to the target lens's JSONL store. Do NOT rewrite content, reassign weight, or change `w_at` — copy `content`, `context`, `suggested_target`, `w`, and `w_at` verbatim. Only adapt the schema envelope: add a `category` field (1-2 words) when moving to knowledge; drop `category` when moving to learnings. This is a zero-friction move — if the entry is valid and fits another lens, move it. No rationalization threshold, no cost-benefit analysis, no "it'll decay anyway." Report moves in your summary so the coordinator can verify.
</applying>

<workflow>
1. Ground yourself on the JSONL store contents and project CLAUDE.md files needed for verification. The weight rubric, cursor value, and lens definitions are already provided in this prompt — do not re-read them. Start scanning within 3 turns.
2. Read the reconciliation cursor from the same directory as your JSONL store. The cursor filename is `{store_stem}.reconcile_cursor.json` (e.g., `.claude/nous/knowledge/cortex.reconcile_cursor.json`). Schema: `{"reviewed_through_ts": "<ISO 8601>"}`. If it exists, resume scanning after its `reviewed_through_ts` value. If it doesn't exist, start from the oldest entry.
3. Scan up to max-entries from the cursor position, using exploration results as ground truth. When an entry references something the exploration didn't cover, verify with a targeted Read or Glob before making a staleness call. When you encounter an entry covering a common topic, grep the full JSONL file for the key claim or unique phrase — cross-cursor duplicates are a real risk since entries earlier in the file may already cover the same ground at a higher weight.
4. Set `w` on each scanned entry. Update `w_at` only on entries you verified with a tool call or pruned (see w_at rules in weight-rubric). For consolidations, also append the merged entry. Record: entry content, assigned weight, issue type.
5. After scanning, write the cursor file (in the same directory as your JSONL store) with `{"reviewed_through_ts": "<ts of last scanned entry>"}`. If no entries remain beyond the scan window, delete the cursor file — previously-clean entries can go stale as the project evolves, so the cycle resets.
6. Return a summary that includes:
   - Changes applied, cursor state (advanced / reset), lens bleed and CLAUDE.md findings for the coordinator.
   - **Verification ledger**: for each entry scored w >= 0.45, state which tool call verified it (e.g., "L442: Read account_name_mapping.yaml — confirmed canonical source claim"). Entries scored below 0.45 do not need verification citations. The coordinator will spot-check the ledger against the transcript.
</workflow>

</agent-prompt>

<coordinator>

Agents assign weights on entries. The coordinator collects summaries, handles cross-cutting follow-ups, then runs the deterministic sweep.

## Summary

Present each agent's summary grouped by lens. Show entry counts: scanned, weighted, consolidated, flagged.

## Cross-store lens bleed

Agents lift-and-shift lens bleed entries themselves (zero source, append verbatim copy to target store). Verify reported moves: confirm the source entry is `w = 0.0`, the target entry exists with correct schema (`category` present for knowledge, absent for learnings), and the content/context/w/w_at were preserved verbatim (no rewrite, no reweigh). Fix any moves that changed content.

## CLAUDE.md mismatches

When agents flag a CLAUDE.md claim contradicted by verified ground truth (e.g., wrong hardware specs, stale paths, incorrect counts), fix the CLAUDE.md and set `w = 0.0` on the correction entry.

## Post-agent sweep

After all agents finish and cross-cutting work is done, run `$NOUS_PLUGIN/scripts/reconcile_nous_entries.sh`, passing the project root as the argument. This sweeps all entries with `w <= 0.15` to the discard files and reports counts.

</coordinator>
