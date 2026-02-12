# Nous Architecture Review & Roadmap

**Date**: February 2026
**Version**: 0.1.4 (current)
**Authors**: AeyeOps research team (5 parallel agents: hooks, compaction, memory, extraction, architecture)

---

## Executive Summary

Nous is a self-improving context system for Claude Code that solves one of the most painful problems in AI-assisted development: **compaction-induced memory loss**. When Claude Code sessions approach context limits, the standard response is `/compact` (lossy summarization) or `/clear` (total wipe). Both destroy nuanced understanding built over a session.

Nous takes a fundamentally different approach: **extract before you lose**. By monitoring context window usage via a statusline hook, Nous identifies the right moment to spawn extraction workers that analyze the session transcript and distill structured learnings (behavioral deltas) and knowledge (factual discoveries) into persistent JSONL stores. On next session start, these are injected back, creating a continuous improvement loop.

**The innovation**: Rather than trying to compress everything (like compaction) or remember nothing (like /clear), Nous selectively preserves *what matters* across sessions. This is not summarization — it is *observation through lenses*, each tuned to extract a specific type of insight.

**Current state**: The system works. Extraction happens, learnings accumulate, injection populates new sessions. But architectural analysis reveals 10 critical/high-severity gaps that, if closed, would transform Nous from a working prototype into a production-grade memory system.

---

## Architecture Deep-Dive

### System Overview

```
                          Claude Code Session
                                 |
                    +------------+------------+
                    |                         |
              SessionStart                   Stop
              (hook fires)              (hook fires)
                    |                         |
                    v                         v
            +---------------+      +-------------------+
            | Inject recent |      | Read statusline   |
            | learnings &   |      | activity log      |
            | knowledge     |      | (context %)       |
            | from JSONL    |      +-------------------+
            +---------------+              |
                    |              +-------+--------+
                    v              |       |        |
              stdout → Claude    <15%   15-59%    >=60%
              context injection   skip   extract   block+
                                         + flush   /clear
                                           |
                                    +------+------+
                                    |             |
                              Learnings      Knowledge
                              Worker         Worker
                              (claude        (claude
                               --print)       --print)
                                    |             |
                                    v             v
                              inbox.jsonl.*  inbox.jsonl.*
                              (fragments)    (fragments)
                                    |             |
                                    v             v
                              flush_inbox    flush_inbox
                                    |             |
                                    v             v
                              engram.jsonl   cortex.jsonl
                              (consolidated) (consolidated)
                                    |             |
                                    +------+------+
                                           |
                                     Next Session
                                     SessionStart
                                     injects last 10
```

### Data Flow Detail

```
Per-Project Storage (.claude/nous/):
  extraction_cursor.json      ← tracks last extracted timestamp
  learnings/
    inbox.jsonl.*             ← raw extraction fragments (temporary)
    engram.jsonl              ← consolidated learnings (injected at start)
  knowledge/
    inbox.jsonl.*             ← raw extraction fragments (temporary)
    cortex.jsonl              ← consolidated knowledge (injected at start)

Global Storage (~/.claude/):
  statusline-activity.jsonl   ← enriched status log (context %, tokens, etc.)
  nous.log                    ← operational log (async, non-blocking)
  nous-statusline.sh          ← wrapper script (tees to logger + visual)
```

### Component Roles

| Component | File | Role |
|-----------|------|------|
| **Main Hook** | `hooks/nous.py` | Entry point for SessionStart + Stop events |
| **Lens Framework** | `hooks/lenses/base.py` | ExtractionLens dataclass, flush_inbox, prompt builder |
| **Learnings Lens** | `hooks/lenses/learnings.py` | Behavioral delta extraction prompt |
| **Knowledge Lens** | `hooks/lenses/knowledge.py` | Factual discovery extraction prompt |
| **Models** | `hooks/lenses/models.py` | Pydantic models for statusline, signals |
| **Activity Logger** | `hooks/nous-logger.sh` | Silent JSONL append (statusline tee) |
| **Visual Statusline** | `hooks/statusline-example.sh` | Optional terminal status bar |
| **Setup Command** | `commands/setup.md` | Generates wrapper script |

### Threshold Behavior (Current)

| Context % | Action | Rationale |
|-----------|--------|-----------|
| **<15%** | Skip entirely | Session too short for useful extraction |
| **15-59%** | Flush inboxes + fire extraction workers | Prime extraction window |
| **60-65%** | Flush inboxes only | Too risky to spawn workers |
| **>65%** | Flush + block with /clear recommendation | Context nearly exhausted |

---

## How Nous Addresses Compaction Memory Loss

### The Problem

Claude Code's `/compact` is fundamentally lossy (research findings, Feb 2026):

1. **Compaction is summarization**, not selective preservation. Nuance dies first.
2. **Post-compaction quality degrades**: Claude forgets which files it was working with, repeats corrected mistakes, loses edge-case understanding.
3. **Compaction frequently fails**: GitHub issues #23751, #18211, #21853 report failures at 48-82% context, state corruption, hangs.
4. **Same model bottleneck**: Compaction uses the same Opus model (no cheaper alternative), consuming expensive tokens for lossy output.
5. **Auto-compaction is disruptive**: Triggers mid-task at 75-95% capacity, with no user control over what's preserved.

### The Nous Solution

Nous sidesteps compaction entirely by implementing a **parallel memory pipeline**:

1. **Extract before context fills**: At 15% context, Nous already begins extracting. By the time compaction would trigger (75%+), valuable insights are safely persisted to disk.
2. **Structured extraction over summarization**: Instead of compressing everything, two focused lenses extract *specific* types of insight — behavioral learnings and factual knowledge. This is higher signal-to-noise than generic summarization.
3. **Recommend /clear over /compact**: At >65%, Nous blocks and recommends `/clear` instead of `/compact`. The rationale: if learnings are already extracted, a clean start with injection is better than a lossy summary.
4. **Fire-and-forget architecture**: Extraction workers run as detached subprocesses. The main hook returns in milliseconds. No blocking, no performance penalty.
5. **Continuous injection**: Every new session starts with the last 10 learnings and knowledge entries pre-loaded. Cross-session continuity without compaction.

### What Compaction Loses vs. What Nous Preserves

| Lost in Compaction | Preserved by Nous |
|--------------------|-------------------|
| Detailed error messages & workarounds | Captured as learnings |
| Specific file paths & architecture facts | Captured as knowledge |
| User corrections & preferences | Captured as learnings with context |
| Tool failure patterns | Captured as behavioral deltas |
| Edge cases & gotchas | Captured as knowledge with category |

### What Nous Does NOT Preserve

- Mid-task state (what Claude was actively doing)
- Exact code snippets under review
- Full conversation flow/reasoning chains
- Temporary debugging context

These are the domain of continuation prompts (user-crafted) and session resume, not automated extraction.

---

## Current Gaps & Limitations (Prioritized)

### Critical Severity

#### G1. Cursor Advances Before Extraction Completes
**Location**: `nous.py:565`
**Impact**: If an extraction subprocess fails (OOM, timeout, API error), the window [start_ts, end_ts] is permanently lost. The cursor has already advanced past it.

**Current code**:
```python
# Fire subprocess
_fire_extraction_subprocess(LEARNINGS_LENS, ...)
_fire_extraction_subprocess(KNOWLEDGE_LENS, ...)
# Cursor advances immediately
write_extraction_cursor(project_dir, current.meta_ts)  # Line 565
```

**Proposed fix**: Two-phase cursor with pending state:
1. Write `extraction_cursor.pending.json` on spawn
2. Promote to `extraction_cursor.json` only after `flush_inbox` validates output
3. On next run, if pending exists and is stale (>WORKER_TIMEOUT), retry that window

#### G2. Unbounded Storage Growth
**Location**: `base.py:182-188`
**Impact**: `engram.jsonl` and `cortex.jsonl` grow forever. Only last 10 entries are injected (INJECT_RECENT_COUNT=10), but files never rotate. After months of use: slow I/O on injection (reads entire file to take last 10), wasted disk, no aging out of stale entries.

**Proposed fix**: Rotate during flush:
```python
def rotate_encoded(file, max_entries=500, keep_entries=200):
    entries = read_all_jsonl(file)
    if len(entries) > max_entries:
        atomic_write(file, entries[-keep_entries:])
```

### High Severity

#### G3. Naive Last-N Injection (No Relevance)
**Location**: `nous.py:425-434`
**Impact**: A frontend CSS session gets injected with backend database learnings just because they're most recent. No relevance ranking, no domain filtering.

**Proposed fix (phased)**:
- **Phase 1**: Tag entries with domain hints during extraction (e.g., "frontend", "backend/db")
- **Phase 2**: At injection, infer current domain from recent file activity, prioritize matching entries
- **Phase 3**: Embedding-based similarity ranking (requires vector store)

#### G4. No JSONL Output Validation
**Location**: `base.py:168-179`
**Impact**: Extraction workers may produce markdown-wrapped JSON, partial output, or complete garbage. `parse_jsonl` silently skips invalid lines. No schema validation against LearningSignal/KnowledgeSignal models.

**Proposed fix**: Validate in flush_inbox:
```python
for entry in entries:
    try:
        validated = lens.schema.model_validate(entry)
        if len(validated.content) > 10:  # Non-trivial content
            append_to_encoded(validated)
    except ValidationError:
        log_to_review_queue(entry, reason="schema_mismatch")
```

#### G5. No Retry on Extraction Failure
**Location**: `base.py:158-166`
**Impact**: Empty fragments (failed extractions) are deleted with no retry. Combined with G1, failed windows are permanently lost.

**Proposed fix**: Track failures in `.claude/nous/failed_extractions.jsonl` with window timestamps. Background retry (max 3 attempts, exponential backoff).

#### G6. suggested_target Field is Unused
**Location**: `models.py:114,125`, extraction prompts
**Impact**: Every extraction entry includes a `suggested_target` field pointing to where the learning should live (CLAUDE.md, commands/*.md, skills/*.md, etc.). Nothing acts on this. Major missed opportunity for auto-applying learnings to project memory files.

**Proposed fix (phased)**:
- **Phase 1**: Queue pending updates in `.claude/nous/pending_updates/{target}.jsonl`
- **Phase 2**: Slash command `/nous:review` shows pending updates for human approval
- **Phase 3**: Auto-apply with confidence scoring (high-confidence entries applied automatically)

#### G7. Unbounded Extraction Cost
**Location**: `nous.py:91, 496-508`
**Impact**: Each Stop hook spawns 2 Opus workers. At ~$15/M input tokens: 10 sessions/day x 2 workers x 50k tokens = ~$15/day with no budget control.

**Proposed fix**:
1. **Immediate**: Switch `EXTRACTION_MODEL` from "opus" to "sonnet" (10x cheaper, likely sufficient for extraction)
2. **Short-term**: Track costs in `.claude/nous/cost_log.jsonl`, add daily budget cap
3. **Medium-term**: Batch API integration (50% discount, async processing)

#### G8. Fragment Processing Race Condition
**Location**: `base.py:134-198`
**Impact**: Two concurrent `flush_inbox` calls (different sessions, same project) can race on fragment read/delete. Current code handles FileNotFoundError but silently drops fragments.

**Proposed fix**: File-level locking with LOCK_NB (non-blocking, skip if locked):
```python
with open(fragment, 'r') as f:
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        continue  # Another process is handling this fragment
```

#### G9. Cross-Project Knowledge Isolation
**Location**: `nous.py:419-420`
**Impact**: Each project maintains separate engram/cortex. General insights ("use Ruff for linting", "prefer pnpm") are re-learned per project.

**Proposed fix**: Global knowledge layer:
1. During extraction, classify learnings as project-specific vs. general
2. Append general learnings to `~/.claude/nous/global_learnings.jsonl`
3. Inject global learnings (last 5) alongside project-specific ones

#### G10. No Self-Healing or Error Recovery
**Location**: `nous.py:584-591, 694-696`
**Impact**: Worker subprocess errors are logged but not recovered. Main hook swallows all exceptions. Systemic failures (e.g., broken pydantic) repeat silently every session.

**Proposed fix**: Failed extraction queue + error rate monitoring. Alert after threshold.

### Medium Severity

#### G11. Weak Deduplication
Only last 20 entries used for dedup context in extraction prompts. Semantic duplicates with different wording accumulate over time. Needs embedding-based similarity checking.

#### G12. Fixed Threshold Percentages
Hard-coded skip/extract/block thresholds may not be optimal for all session types. Short but valuable sessions (<15%) never get extracted. Needs configurable thresholds and manual extraction trigger.

#### G13. Observability Gaps
Good logging but no metrics aggregation. Can't answer: extraction success rate? entries/day? cost/week? Needs structured metrics + reporting command.

#### G14. jq-Based Transcript Filtering
Extraction prompts instruct workers to use `jq` for transcript filtering. Should use Read tool instead (safer, no shell injection risk, works with locked files).

---

## Claude Code Platform Opportunities

Research uncovered several platform features that could significantly enhance Nous:

### PreCompact Hook (Available Now, Not Used)
**What**: Fires before compaction begins. Receives `trigger` (manual/auto) and `custom_instructions`.
**Opportunity**: Last-chance extraction before lossy summarization. Add PreCompact handler to `hooks.json` that forces extraction regardless of context %.

### Async Hooks (New in Jan 2026)
**What**: Set `"async": true` on command hooks. Runs in background without blocking (10-min timeout).
**Opportunity**: Could replace the fire-and-forget multiprocessing pattern with native async hooks, simplifying the architecture.

### Context Editing API (Beta)
**What**: `clear_tool_uses_20250919` and `clear_thinking_20251015` selectively remove old tool results/thinking without full compaction.
**Opportunity**: If Claude Code exposes context editing, Nous could surgically remove stale context instead of recommending /clear.

### TaskCompleted / TeammateIdle Hooks (New Feb 2026)
**What**: Fire when team tasks complete or teammates go idle.
**Opportunity**: Could trigger extraction after significant team milestones.

### Batch API (50% Discount)
**What**: Anthropic's batch API processes requests asynchronously at 50% token cost. Combinable with prompt caching for up to 90% savings.
**Opportunity**: Queue extraction requests as batch jobs instead of real-time `claude --print`. Acceptable for non-urgent extraction.

### MEMORY.md Auto-Memory (Built-in, 200 Lines)
**What**: Claude Code's native auto-memory at `~/.claude/projects/<project>/memory/MEMORY.md`. First 200 lines injected per session.
**Opportunity**: Nous could write high-confidence learnings directly to MEMORY.md, leveraging built-in injection. However, 200-line limit and unstructured format are constraints.

---

## Competing & Complementary Approaches

| Approach | How It Works | Strengths | Weaknesses | Relationship to Nous |
|----------|-------------|-----------|------------|---------------------|
| **MEMORY.md** (built-in) | Auto-writes memories, 200-line injection | Zero setup, native | Unstructured, small limit, no semantic filtering | Complementary — Nous could feed high-confidence entries to MEMORY.md |
| **CLAUDE.md** (built-in) | User-curated project instructions | Persistent, always loaded | Manual maintenance, no auto-update | Nous `suggested_target` could auto-update CLAUDE.md |
| **claude-mem** (community) | Token-based memory with 95% reduction | Efficient compression | External dependency, less structured | Different approach — compression vs. extraction |
| **MCP Memory Servers** | Vector DB + semantic retrieval | Semantic relevance, scalable | Complex setup, external infra | Could be Nous's injection backend for Phase 3 |
| **Manual /compact** | User-triggered summarization | User controls timing | Lossy, expensive, frequently fails | Nous replaces need for this entirely |

**Key insight**: Nous is the only approach that combines *automated extraction* with *structured storage* and *session-start injection*. Others either require manual curation (CLAUDE.md), have limited capacity (MEMORY.md), or require external infrastructure (MCP).

---

## Proposed Roadmap

### Phase 1: Hardening (Quick Wins)

Focus: Fix critical reliability issues with minimal effort.

| Item | Gap | Effort | Impact |
|------|-----|--------|--------|
| Switch extraction to Sonnet | G7 | 1 line | 10x cost reduction |
| Fragment file locking | G8 | 1 day | Eliminates silent data loss |
| Concurrent extraction prevention | G3 (race) | 1 day | No duplicate extractions |
| Use Read tool over jq in prompts | G14 | 2 hours | Safer transcript access |
| Add stale fragment cleanup | G2 (partial) | 2 hours | Prevents orphaned files |

### Phase 2: Reliability (Critical Foundations)

Focus: Ensure no data loss under any failure mode.

| Item | Gap | Effort | Impact |
|------|-----|--------|--------|
| Two-phase cursor (pending/confirmed) | G1 | 3 days | No lost extraction windows |
| Storage rotation strategy | G2 | 5 days | Bounded storage growth |
| JSONL output validation | G4 | 3 days | No garbage in encoded files |
| Basic cost tracking | G7 | 2 days | Cost visibility |
| Add PreCompact hook handler | Platform | 3 days | Last-chance extraction before compaction |

### Phase 3: Intelligence (Quality Improvements)

Focus: Make injection and extraction smarter.

| Item | Gap | Effort | Impact |
|------|-----|--------|--------|
| Domain-tagged extraction | G3 | 1 week | Relevance-aware injection |
| Retry queue for failed extractions | G5 | 1 week | No permanently lost windows |
| Review queue for suggested_target | G6 | 2 weeks | Learnings auto-update files |
| Manual extraction trigger (/extract) | G12 | 2 days | Short sessions extractable |
| Error rate monitoring + alerting | G10 | 3 days | Self-healing awareness |

### Phase 4: Scale (Cross-Project & Cost)

Focus: Global knowledge and cost optimization.

| Item | Gap | Effort | Impact |
|------|-----|--------|--------|
| Global knowledge layer | G9 | 1 week | Cross-project learning |
| Batch API for extraction | G7 | 2 weeks | 50%+ cost reduction |
| Embedding-based dedup | G11 | 2 weeks | No semantic duplicates |
| Metrics aggregation + /nous:metrics | G13 | 1 week | Full observability |

### Phase 5: Integration (Platform Leverage)

Focus: Leverage Claude Code platform evolution.

| Item | Gap | Effort | Impact |
|------|-----|--------|--------|
| Async hook migration | Platform | 1 week | Simpler architecture |
| MEMORY.md integration | Platform | 1 week | Native injection path |
| Context editing integration | Platform | 2 weeks | Surgical context management |
| Embedding-based injection (MCP) | G3 | 3 weeks | Semantic relevance at scale |

---

## Research Sources

### Claude Code Hooks
- Official Claude Code Docs: hooks system, 14 hook event types
- GitHub releases v2.1.33: TeammateIdle, TaskCompleted, async hooks
- GitHub issues: #10814, #10367, #14281, #2814

### Compaction Mechanics
- Claude API Docs: context compaction, context editing beta
- GitHub issues: #23751, #18211, #21853, #18482, #19888, #19567, #20696
- Community reports: Dev Genius, ClaudeLog, hyperdev.matsuoka.com

### Memory & Persistence
- Claude Code Docs: MEMORY.md auto-memory, CLAUDE.md @import syntax
- MCP ecosystem: Memory-Keeper, Memory-MCP, claude-mem
- GitHub discussions: cross-session persistence requests

### Extraction & CLI
- Claude Code CLI Reference: --print mode, --model, --permission-mode flags
- Anthropic API: Batch API (50% discount), pricing by model
- GitHub issues: #949, #581, #2734, #19060, #10964, #7263
- Known limitation: --print returns empty output with stdin >7000 chars

### Architecture Analysis
- Direct code review of nous.py (704 lines), lenses/ framework (4 files)
- Line-by-line analysis of file I/O patterns, locking, error handling
- Severity/effort ratings based on blast radius and code complexity

---

## Conclusion

Nous represents a genuinely novel approach to the context persistence problem. Rather than fighting compaction's limitations, it builds a parallel memory pipeline that makes compaction irrelevant. The core insight — **extract structured observations before context fills, inject them into fresh sessions** — is sound and validated by working code.

The path from working prototype to production-grade system requires closing 10 critical/high-severity gaps, most addressable in Phase 1-2 with moderate effort. The highest-leverage improvements are:

1. **Cursor reliability** (G1) — without this, the system silently loses data
2. **Cost management** (G7) — switching to Sonnet is a one-line change with 10x savings
3. **PreCompact hook** — the missing safety net before compaction
4. **suggested_target activation** (G6) — transforms passive storage into active memory management

The long-term vision is a system where Claude Code sessions genuinely learn from each other, with semantic retrieval, cross-project knowledge sharing, and automatic codebase documentation updates — all without ever needing to compact.
