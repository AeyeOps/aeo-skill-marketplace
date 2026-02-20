<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## aeo-nous Lens System — Deep Code Review

I've read every meaningful file in `aeo-nous`: `nous.py`, all four files in `lenses/`, `hooks.json`, `nous-stop-guard.sh`, `setup.md`, and the README. Here's what the per-project lens system actually does, and where it's strong, where it's thin, and where the real opportunities are.

***

### What the Lens System Actually Is

The `ExtractionLens` dataclass is the core abstraction. Each lens defines:

- **A prompt** — what to look for in a session transcript
- **An inbox path** — where raw fire-and-forget `claude --print` subprocess output lands as uniquely-named fragment files
- **An encoded path** — where reviewed/flushed entries graduate to (the durable store)
- **A Pydantic schema** — for validation of extracted entries

Today there are exactly **two lenses**:

1. **Learnings** (`engram.jsonl`) — behavioral deltas: errors, workarounds, corrections, user-stated rules. The core question is "what should future sessions do differently?"
2. **Knowledge** (`cortex.jsonl`) — project facts: architecture, patterns, dependencies, gotchas. The core question is "what facts should future sessions know?"

The lifecycle works like this:

- **SessionStart** → `nous.py` reads the last 10 entries from `engram.jsonl` and `cortex.jsonl` and prints them to stdout (injected into Claude's context)
- **Stop** → Based on `context_window.used_percentage` from the statusline activity log:
    - **<10%**: skip entirely
    - **10–60%**: flush inbox fragments + fire two `claude --print` extraction subprocesses (one per lens), then advance the extraction cursor
    - **60–65%**: flush inbox only (no extraction)
    - **>65%**: `nous-stop-guard.sh` (sync) blocks with a `/clear` recommendation

The extraction subprocess reads the actual transcript file using `jq` to window by timestamp, then outputs JSONL to a unique fragment file. `flush_inbox()` later globs those fragments, parses, validates, appends to the encoded file with `fcntl` locking, and deletes the fragment.

***

### Strengths

**1. The lens abstraction is genuinely well-designed.** The `ExtractionLens` dataclass is clean — prompt, inbox, encoded, schema. Adding a new lens is trivial: define a prompt, pick paths, define a Pydantic model. The framework doesn't know or care about what it's extracting, only how to route it. This is a solid foundation for extensibility.

**2. Fire-and-forget with fragment files is production-aware.** Rather than blocking the main session or requiring a database, extraction subprocesses write to uniquely-named fragments (`inbox.jsonl.{timestamp}_{pid}_{random}`), and `flush_inbox()` processes them idempotently. This avoids race conditions without complex locking — each fragment is processed exactly once. The `FRAGMENT_MIN_AGE_SECONDS = 2` guard prevents reading partially-written files. This is pragmatic engineering.

**3. The threshold-based extraction is context-budget-conscious.** The tiered approach (skip at <10%, extract at 10–60%, flush-only above 60%, block at 65%) shows real operational awareness. You don't waste API calls extracting from trivial sessions, and you don't fire expensive `claude --print` subprocesses when the context window is already stressed.

**4. Deduplication by feeding existing entries back to the extraction prompt.** `read_existing_encoded()` grabs the last 20 entries and passes them as `existing_entries` in `build_extraction_prompt()`, telling the extraction agent to skip duplicates. This is a simple but effective anti-accumulation mechanism.

**5. The sync/async split is well-engineered.** The `nous-stop-guard.sh` runs synchronously (fast, bash, jq only) to make the blocking decision, while `nous.py` runs async for the heavy extraction work. This keeps Claude Code's UX responsive while doing substantial background work.

**6. Per-project scoping.** Everything lives under `.claude/nous/` within the project directory. The extraction cursor, inbox fragments, and encoded files are all project-local. This means different projects accumulate independent memory — correct behavior.

***

### Weaknesses

**1. The engram/cortex stores are append-only JSONL with no compaction, deduplication, or decay.** `flush_inbox()` appends to `engram.jsonl` and `cortex.jsonl` forever. Over weeks/months of active development, these files will grow unbounded. The deduplication in the extraction prompt helps prevent new duplicates, but it only checks the last 20 entries — earlier duplicates or near-duplicates accumulate. There's no mechanism to:

- Merge similar entries
- Decay stale entries (a learning about a now-deleted module)
- Compact/summarize when the file gets too large
- Score entries by how often they were actually useful

**2. Injection is naive: last-N with no relevance filtering.** `handle_session_start()` injects the last 10 learnings and last 10 knowledge entries. If you've been working on module A for 3 sessions and now switch to module B, you get module A's learnings injected. There's no semantic relevance, no task-awareness, no category filtering. The `KnowledgeSignal` has a `category` field but it's never used for retrieval — it's written but never queried.

**3. No relationship/graph between entries.** Learnings and knowledge are flat, independent JSONL lines. A learning about "always use `--no-cache` with Docker builds in this repo" has no link to the knowledge entry about "CI uses multi-stage Docker builds." There's no way to traverse from one insight to related insights. Each entry is an island.

**4. `suggested_target` is written but never acted on.** Both `LearningSignal` and `KnowledgeSignal` include `suggested_target` (e.g., "put this in `commands/docker-build.md`"). But nothing in the system ever reads that field to actually promote content into those targets. The promotion path from "observation" to "durable skill/command/CLAUDE.md content" doesn't exist — it's a schema placeholder with no actuator.

**5. No cross-project memory.** If you discover something in project A that's universally true (e.g., a Claude Code behavioral pattern), it stays in project A's `.claude/nous/`. There's no global/user-level memory tier. The `~/.claude/` path is used only for logs and the statusline, never for shared knowledge.

**6. The extraction window can miss content.** The cursor advances to `current.meta_ts` after spawning extraction subprocesses — but those subprocesses are fire-and-forget. If a subprocess fails or times out (300s limit), the cursor has already advanced past that window. The content in that window is permanently skipped. There's no retry or dead-letter mechanism.

**7. No feedback loop on extraction quality.** Entries go from inbox → encoded and get injected forever. There's no signal back about whether an injected learning was actually helpful. No thumbs-up/down, no usage tracking, no relevance scoring. Over time the signal-to-noise ratio in engram/cortex can only degrade.

***

### Opportunities

**1. Add a Consolidation Lens (or "Compactor Agent").** Create a third lens that runs periodically (or when encoded files exceed a size threshold) and:

- Merges near-duplicate entries
- Summarizes clusters of related learnings into higher-order principles
- Removes entries about deleted files/modules (detectable via `git diff` or file existence checks)
- Scores entries by age, recency of injection, and session outcome

This is the "promotion" layer you've been describing — observations graduate to principles, principles graduate to skill/command content.

**2. Add relevance-based injection instead of last-N.** At SessionStart, instead of the last 10 entries, use the current working directory, recent `git log`, or the user's first prompt to select entries that are semantically relevant. Even a simple heuristic — filter by `category` (knowledge) or by file paths mentioned in `content` — would be a massive improvement over chronological-last-N. A lightweight embedding step (even via `claude --print` with a focused prompt) could rank entries by relevance to the current task.

**3. Act on `suggested_target`.** Build a promotion command (e.g., `/nous:promote`) or a background agent that:

- Reads entries with `suggested_target` set
- Groups them by target file
- Drafts a PR or appends to the target file
- Marks entries as "promoted" so they're no longer injected raw

This closes the loop from "observation" → "durable project knowledge in the right place."

**4. Add a relationship/graph layer.** Each entry has `project`, `session`, `category`, `content`, and `suggested_target`. You can build a lightweight graph by:

- Linking entries that share `session` (co-discovered in the same session)
- Linking entries whose `content` mentions the same files/modules
- Linking learnings to knowledge entries about the same `category`
- Using `suggested_target` as a clustering key

This doesn't require Neo4j — even a simple adjacency list in a `.claude/nous/graph.jsonl` would enable multi-hop traversal at injection time ("you're working on module X, here are all learnings and knowledge connected to X").

**5. Add a global/user-level memory tier.** Some learnings are project-specific ("this repo uses pnpm, not npm") and some are universal ("Claude Code's Read tool doesn't handle binary files well"). Add a `~/.claude/nous/global/` tier with its own engram/cortex that captures cross-project patterns. The extraction prompt can be extended to classify: "Is this learning specific to this project, or universal?" and route accordingly.

**6. Add extraction retry / dead-letter.** When the cursor advances past a window, record the window in a retry queue. On next Stop event, if there are unprocessed windows, retry them before advancing further. This prevents permanent content loss from subprocess failures.

**7. Add a feedback signal.** When learnings are injected at SessionStart, tag them. If the session completes without errors/corrections related to that topic, that's a positive signal. If the user corrects something that a learning should have prevented, that's a negative signal. Over time, use these signals to weight entries for injection priority and compaction decisions.

**8. Make lenses truly pluggable and independent of the marketplace.** Right now the lens framework is embedded in `aeo-nous/hooks/lenses/`. If aeo-nous is going to be the memory orchestration layer, the `ExtractionLens` base class, `flush_inbox`, and `build_extraction_prompt` should be a standalone, installable module (even just a pip-installable micro-package). Other plugins or external tools could then define their own lenses (e.g., a "decisions" lens, a "risks" lens, a "dependencies" lens) and register them with aeo-nous without modifying its code.

***

### Summary Assessment

The lens system is a clean, production-aware extraction framework with solid engineering fundamentals (fragment files, fcntl locking, threshold-based firing, sync/async split). What it lacks is everything *after* extraction: compaction, relevance-based retrieval, relationship modeling, promotion to durable knowledge, feedback loops, and cross-project memory. The `ExtractionLens` abstraction is the right foundation — the opportunity is to build the memory lifecycle on top of it rather than treating extraction as the end state.

