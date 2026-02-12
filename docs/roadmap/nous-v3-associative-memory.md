# Nous v3: Associative Memory Architecture

**Date**: February 2026
**Version**: 0.3.0 (proposed)
**Predecessors**:
- [nous-v2-associative-memory.md](nous-v2-associative-memory.md)
- [nous-architecture-review.md](nous-architecture-review.md) (v1 whitepaper)

---

## Executive Summary

Nous v1 solved compaction-induced memory loss with a parallel extraction pipeline: structured learnings and knowledge extracted from sessions, persisted as JSONL, injected on next start. It works. But it stores memories as a flat, time-ordered log and retrieves by recency alone. This is **episodic memory** — it remembers *what happened recently*, not *what's relevant to what I'm doing now*.

This document proposes the evolution to **Associative Memory**: retrieval by content, context, and connection rather than by timestamp. The architecture replaces JSONL with SQLite, adds concept-tagged semantic search, introduces a lightweight knowledge graph via edge tables, implements reinforcement scoring so memories that prove useful rise to the top, and introduces a **bi-temporal event-sourced model** that tracks both when facts were true and when the system learned about them — enabling historical session ingestion, cross-session contradiction detection, and retroactive corrections.

The key insights from current research (MAGMA, Graphiti, HybridRAG, Helland): the industry is converging on **multi-dimensional hybrid retrieval** — combining keyword search, vector similarity, graph traversal, temporal weighting, and bi-temporal validity. Independent agent sessions are temporal islands that produce knowledge asynchronously; reconciliation through immutable, timestamped events is the path to coherent long-term memory. We adapt these patterns for an embedded, serverless context with zero mandatory external dependencies.

**Naming**: We call this pattern **Associative Memory** rather than "GraphRAG" because:
- It is not RAG (no external document retrieval — it retrieves from its own extracted memories)
- The neuroscience parallel is exact: the transition from episodic memory (time-ordered events) to semantic/associative memory (content-addressed knowledge with relational links)
- The brain's associative cortex links different types of memory — precisely what the edge table does

### v3 Operating Decisions

This v3 update keeps the full v2 architecture and applies the latest integration constraints:

1. **Advanced reconciliation is v1-required** and remains in the core path.
2. **Event history is retained indefinitely**; only projections/read models are pruned/rebuilt.
3. **Out-of-band ingestion is primary**: filesystem watch + reconcile scan over Claude session artifacts.
4. **Inline hooks are thin and deterministic**:
   - `SessionStart`: required, read-only context resolve.
   - `UserPromptSubmit`: deferred for v1, gated by feature flag (`NOUS_ENABLE_USERPROMPTSUBMIT=false` by default).
   - `Stop`: optional fire-and-forget wake signal only (no extraction dependency).
5. **Precompute + cache is a non-functional requirement** for low-latency runtime injection.
6. **Artifact scope for v1 is fixed**: transcript ingestion includes `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl` and subagent transcripts; debug/history/statusline remain optional enrichment.
7. **Local-first deployment is the default** with containerized portability and a clean service interface.

---

## The Scaling Challenge

### Why Flat JSONL Hits a Ceiling

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph Current["Nous v1: Episodic Memory"]
        E1[Session ends] --> E2[Extract to JSONL]
        E2 --> E3[Append to engram.jsonl]
        E3 --> E4["tail -10 at next start"]
        E4 --> E5[Inject regardless of relevance]
    end
    subgraph Problem["Scaling Problems"]
        P1["1 dimension: recency only"]
        P2["No semantic search"]
        P3["No relationships between memories"]
        P4["No usage feedback loop"]
        P5["O(n) full file scan for last 10"]
    end
    Current --> Problem
```

Nous v1 has **one retrieval dimension**: time. A frontend CSS session gets injected with backend database learnings simply because they are newest. There is no way to ask "what do I know about React hooks?" or "what's connected to this API pattern I'm using?".

At small scale (~50 entries), recency is a reasonable proxy for relevance. At hundreds of entries across diverse work, it breaks down.

### What the Industry Learned (Feb 2026)

Research converged on seven principles for agent memory:

| Principle | Source | Implication for Nous |
|-----------|--------|---------------------|
| **Multi-graph retrieval** | MAGMA (Jan 2026) — semantic, temporal, causal, entity graphs. 45.5% higher reasoning accuracy | Memories need multiple relationship types, not just timestamps |
| **Bi-temporal data** | Graphiti/Zep — tracks both "when fact was true" and "when we learned it" ([Fowler](https://martinfowler.com/articles/bitemporal-history.html)) | Extraction timestamps alone are insufficient; validity windows drive retrieval and enable historical backfill |
| **Event sourcing** | [Fowler](https://martinfowler.com/eaaDev/EventSourcing.html), [Datomic](https://blog.datomic.com/2014/08/stuff-happens-fixing-bad-data-in-datomic.html) — immutable event log with projections | Mutations as events, not CRUD; enables retroactive corrections and full audit trail |
| **Temporal reconciliation** | [Helland](https://queue.acm.org/detail.cfm?id=3415014) — independent services generate facts in their own temporal domains | Sessions are temporal islands; reconciliation via CRDTs and NLI contradiction detection at injection time |
| **Hybrid search** | HybridRAG (NVIDIA/BlackRock) — vector + graph outperforms either alone | No single retrieval method is sufficient; fuse keyword + vector + graph + temporal |
| **Incremental construction** | LightRAG, Fast GraphRAG — upsert-based, no full recomputation | Graph must grow with each extraction, not be rebuilt |
| **Process mining** | [van der Aalst](https://link.springer.com/book/10.1007/978-3-662-49851-4) — discover operational patterns from event logs | Re-learning detection signals injection failures vs naturally important knowledge |

---

## Architecture Overview

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph Session["Claude Code Session"]
        S1[SessionStart hook]
        S2["UserPromptSubmit hook (optional)"]
        S3["Stop hook (optional notify)"]
    end

    subgraph Runtime["Runtime Resolver (Inline Path)"]
        R1[Build context fingerprint]
        R2[Resolve precomputed context and interventions]
        R3["Inject via stdout/additionalContext"]
    end

    subgraph Ingestion["Out-of-Band Ingestion Pipeline"]
        X1["Watch ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl"]
        X2["Reconcile scan (startup + periodic)"]
        X3["Incremental parser + per-file cursor"]
        X4["Extract memories + concepts + edges + temporal bounds"]
        X5[Validate schema]
        X6[Write to event log]
    end

    subgraph Intelligence["Background Intelligence"]
        N1[Project read models]
        N2["Reconcile full path (NLI uncached pairs)"]
        N3["Observer pipelines -> intervention candidates"]
        N4[Precompute injection cache]
    end

    subgraph Backfill["Historical Backfill (CLI)"]
        B1["Read ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl"]
        B2[Batch extract with same prompt]
        B3[Write to event log via same ingest contracts]
    end

    subgraph Storage["cortex.db (SQLite)"]
        DB6[(learning_events)]
        DB1[(memories — projected)]
        DB2[(concepts)]
        DB3[(edges)]
        DB4[(access_log)]
        DB5[(vectors)]
        DB7[(injection_cache)]
        DB8[(nli_results)]
    end

    S1 --> R1 --> R2 --> R3
    S2 --> R1
    S3 -.->|optional poke| X2
    X1 --> X3 --> X4 --> X5 --> X6
    X2 --> X3
    X6 --> DB6
    B1 --> B2 --> B3 --> DB6
    DB6 -.->|projection| DB1
    DB6 -.->|projection| DB2 & DB3
    DB6 -.->|checkpointed projection| N1
    N1 --> DB1 & DB2 & DB3
    DB5 -.-> N1
    N1 --> N2 --> N3 --> N4 --> DB7
    N2 --> DB8
    DB8 -.-> R2
    R2 --> DB7
    R2 -.->|log access| DB4
```

### Storage Schema

```mermaid
%%{init: {'theme': 'dark'}}%%
erDiagram
    MEMORIES {
        int id PK
        text content "The extracted learning or knowledge"
        text type "learning | knowledge"
        text domain "inferred domain tag"
        text scope "project | global"
        text source_session "session ID that produced this"
        real reinforcement_score "usage-weighted relevance"
        datetime created_at
        datetime accessed_at
        datetime valid_from "when fact became true"
        datetime valid_until "when fact was invalidated"
        text temporal_confidence "low | medium | high"
    }
    CONCEPTS {
        int id PK
        int memory_id FK
        text concept "normalized lowercase concept phrase"
    }
    EDGES {
        int id PK
        int source_id FK
        int target_id FK
        text rel_type "relates_to | supersedes | contradicts | depends_on"
        real weight "strength of relationship"
        datetime created_at
    }
    ACCESS_LOG {
        int id PK
        int memory_id FK
        text session_id
        int was_useful "1 if session succeeded 0 if corrected"
        datetime accessed_at
    }
    VECTORS {
        int memory_id FK
        blob embedding "float32 or int8 vector via sqlite-vec"
    }
    NLI_RESULTS {
        int id PK
        int memory_id_a FK
        int memory_id_b FK
        text nli_label "entailment | neutral | contradiction"
        real confidence
        text model_version
        datetime updated_at
    }

    MEMORIES ||--o{ CONCEPTS : "tagged with"
    MEMORIES ||--o{ EDGES : "source"
    MEMORIES ||--o{ EDGES : "target"
    MEMORIES ||--o{ ACCESS_LOG : "tracked by"
    MEMORIES ||--o| VECTORS : "embedded as"
    MEMORIES ||--o{ NLI_RESULTS : "memory_a"
    MEMORIES ||--o{ NLI_RESULTS : "memory_b"
```

### Bi-Temporal Model

The schema includes `valid_from` and `valid_until` on the memories table, but these fields require an explicit **population strategy** and **scoring integration** to be architecturally meaningful. The bi-temporal model tracks two independent time axes per fact:

| Axis | Column(s) | Meaning | Set By |
|------|----------|---------|--------|
| **Transaction time** | `created_at` | When the system learned this fact | Automatic (extraction timestamp) |
| **Valid time** | `valid_from` / `valid_until` | When this fact was true in the real world | Extraction prompt (estimated) + `temporal_confidence` |

**Population Strategy**: The extraction prompt asks Claude to estimate temporal bounds for each learning:

```
For each extracted learning, also output:
- valid_from: when did this fact become true? (ISO 8601 or "unknown")
- valid_until: is this still true? (ISO 8601 if expired, "current" if still valid, "unknown" if uncertain)
- temporal_confidence: low | medium | high
```

Most learnings will output `valid_from = session_date, valid_until = "current", confidence = medium`. Version-specific facts (e.g., "React 18 uses createRoot") receive bounded validity windows. The extraction worker normalizes "unknown" to NULL and "current" to NULL (open-ended validity). `temporal_confidence` is persisted on the projected `MEMORIES` row so temporal scoring remains stable across restart/replay. Cost: ~30-50 additional output tokens per learning on the already-running extraction worker.

**Query Patterns** ([Fowler, "Bitemporal History"](https://martinfowler.com/articles/bitemporal-history.html)):

- **"As of" (transaction time)**: What did the system know at time T? `WHERE created_at <= T` — useful for debugging extraction quality and replaying knowledge state.
- **"As at" (valid time)**: What is true at time T? `WHERE valid_from <= T AND (valid_until IS NULL OR valid_until > T)` — useful for filtering stale knowledge at injection time.
- **Bitemporal intersection**: What did the system know at time T1 that was true at time T2? Combines both axes — useful for historical analysis and the backfill pipeline.

**Scoring Integration**: Valid-time overlap with the current project state adds a sixth scoring dimension. Expired memories receive a staleness penalty; fresh knowledge post-dating the project's last activity is boosted:

```python
def s_temporal(memory, project_context):
    """Temporal relevance score [0, 1]."""
    now = datetime.utcnow()
    if memory.valid_until and memory.valid_until < now:
        return 0.2  # Expired — still potentially relevant as context
    if memory.valid_from and memory.valid_from > project_context.last_activity:
        return 1.0  # Fresh knowledge, post-dates last project activity
    if memory.temporal_confidence == "low":
        return 0.5  # Uncertain temporal bounds — neutral score
    return 0.8  # Valid and within bounds
```

This replaces the five-dimension scoring function with seven dimensions:

```python
return (
    0.15 * s_text          # FTS5 keyword match
  + 0.15 * s_concept       # Concept Jaccard overlap
  + 0.15 * s_vector        # Cosine similarity via sqlite-vec (0.0 if no embeddings)
  + 0.15 * s_graph         # Edge distance to active memories
  + 0.15 * s_reinforce     # Proven useful (access_log)
  + 0.15 * s_temporal      # Bi-temporal validity relevance
  + 0.10 * s_recency       # Freshness decay
)
```

### Immutable Event Log

Direct mutation of the `memories` table (CRUD) loses history. If a memory is updated, there is no record of what it previously said or why it changed. **Event sourcing** solves this: all state changes are recorded as immutable events in a `learning_events` table, and the `memories` table becomes a **materialized projection** rebuilt from events ([Fowler, "Event Sourcing"](https://martinfowler.com/eaaDev/EventSourcing.html)).

```mermaid
%%{init: {'theme': 'dark'}}%%
erDiagram
    LEARNING_EVENTS {
        int event_id PK "auto-increment"
        text event_uuid UK "globally unique ID for cross-database references"
        text learning_id "UUID stable across events for same learning"
        text event_type "LearningExtracted | LearningValidated | LearningReinforced | LearningWeakened | LearningContradicted | LearningSuperseded | LearningArchived"
        text idempotency_key UK "unique dedup key for at-least-once ingestion"
        int schema_version "event schema version for forward compatibility"
        datetime transaction_time "when the system recorded this event"
        datetime valid_from "estimated start of fact validity (nullable)"
        datetime valid_until "estimated end of fact validity (nullable)"
        text vector_clock_json "causal clock map by session_id for conflict detection"
        text payload_json "JSON full learning content plus metadata"
        int parent_event_id FK "causality chain to prior event (nullable)"
        text session_id "session that triggered this event"
        text project_id "project context"
        text source "fs_watch | fs_reconcile | historical_backfill | user_review"
    }

    LEARNING_EVENTS ||--o| LEARNING_EVENTS : "parent_event_id"
    LEARNING_EVENTS }o--|| MEMORIES : "projects to"
```

Canonical DDL contract:

```sql
CREATE TABLE learning_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_uuid TEXT NOT NULL UNIQUE,
    learning_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'LearningExtracted', 'LearningValidated', 'LearningReinforced',
            'LearningWeakened', 'LearningContradicted', 'LearningSuperseded',
            'LearningArchived'
        )
    ),
    idempotency_key TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL,
    transaction_time TEXT NOT NULL,
    valid_from TEXT,
    valid_until TEXT,
    vector_clock_json TEXT,
    payload_json TEXT NOT NULL,
    parent_event_id INTEGER REFERENCES learning_events(event_id),
    session_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK (
        source IN ('fs_watch', 'fs_reconcile', 'historical_backfill', 'user_review')
    )
);
```

### Learning Lifecycle

Each learning progresses through a state machine driven by events. The current state is **derived**, not stored — it emerges from replaying the event stream ([Event-Driven.io, "Projections and Read Models"](https://event-driven.io/en/projections_and_read_models_in_event_driven_architecture/)).

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> LearningExtracted: Watch/reconcile/backfill extraction fires
    LearningExtracted --> LearningValidated: Schema check plus dedup passes
    LearningValidated --> Active: Injected into at least one session
    Active --> LearningReinforced: Session succeeded after injection plus 0.1
    Active --> LearningWeakened: User corrected something minus 0.2
    Active --> LearningContradicted: NLI detects conflict with newer learning
    Active --> LearningSuperseded: Newer learning explicitly replaces this one
    LearningReinforced --> Active: Continue normal lifecycle
    LearningWeakened --> Active: Continue unless score drops below threshold
    LearningWeakened --> LearningArchived: Score decays below 0.1
    LearningContradicted --> Active: Continue with reduced confidence
    LearningSuperseded --> Active: Retained for history; validity window closed
    LearningArchived --> [*]
```

**Projection Function**: The `memories` table is materialized by replaying events in `event_id` order (monotonic auto-increment — never by `transaction_time`, which can have ties):

```python
def project_memories(events: list[LearningEvent]) -> dict[str, Memory]:
    """Replay events to derive current memory state."""
    state = {}
    for event in sorted(events, key=lambda e: e.event_id):
        lid = event.learning_id
        if event.event_type == "LearningExtracted":
            state[lid] = Memory.from_event(event)
        elif event.event_type == "LearningReinforced":
            state[lid].reinforcement_score += event.payload["reinforcement_delta"]
        elif event.event_type == "LearningWeakened":
            state[lid].reinforcement_score += event.payload["reinforcement_delta"]  # negative
        elif event.event_type == "LearningContradicted":
            state[lid].reinforcement_score *= event.payload.get(
                "contradiction_multiplier", 0.7
            )
        elif event.event_type == "LearningSuperseded":
            state[lid].reinforcement_score *= 0.5
            state[lid].valid_until = event.transaction_time
        elif event.event_type == "LearningArchived":
            del state[lid]  # Remove from active set
    return state
```

`LearningSuperseded` does not auto-delete the row from projection state. It closes the fact's validity window (`valid_until`), and runtime retrieval excludes it for "current truth" queries via valid-time filtering. `LearningArchived` remains an explicit lifecycle event for removal from the active projected set.

In practice, the projection runs **incrementally**: on startup, replay only events with `event_id > last_projected_event_id`. Full replay is reserved for consistency checks and migration.

**Correction Patterns** ([Fowler, "Retroactive Event"](https://martinfowler.com/eaaDev/RetroactiveEvent.html); [Datomic, "Stuff Happens"](https://blog.datomic.com/2014/08/stuff-happens-fixing-bad-data-in-datomic.html)):

| Pattern | Mechanism | Nous Use Case |
|---------|-----------|---------------|
| **Compensating event** | New event negates a previous one | "Python 3.12 removed distutils" corrects "use distutils for setup" |
| **Retroactive event** | Event with `valid_from` backdated | Historical backfill discovers a learning that was true since last month |
| **Tombstone** | `Archived` event with explicit reason | User manually invalidates a learning via `/nous:review` |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Storage engine** | SQLite (stdlib `sqlite3`) | Zero deps, single file, ACID transactions, FTS5 built-in |
| **Temporal model** | Bi-temporal (valid time + transaction time) | Distinguishes "when true" from "when learned"; enables as-of/as-at queries and historical backfill |
| **Mutation strategy** | Event-sourced with materialized projection | Full audit trail, retroactive corrections, enables dual-path ingestion (live + historical) |
| **Graph representation** | Adjacency table (`edges`) | Lightweight, queryable with standard SQL, no graph DB needed |
| **Concept extraction** | Claude via `--print` at extraction time | Already running extraction workers; marginal token cost |
| **Edge extraction** | Claude via `--print` at extraction time | Same worker, same cost; outputs relationship tuples |
| **Vector storage** | `sqlite-vec` (2MB pure C extension) | cosine/L2/hamming distance, works with stdlib sqlite3, `pip install sqlite-vec` |
| **Primary search** | SQLite FTS5 over concepts + content | Zero deps, built into SQLite, good enough for <10k memories |
| **Reinforcement** | `access_log` table + decay function | Tracks which memories actually help; decays unused ones |

---

## Embedding Strategy

The core question: how do we get semantic similarity without external infrastructure?

### Concept Tags (Always Active, Zero Dependencies)

The extraction worker already calls `claude --print`. Add to the prompt:

```
Also output a "concepts" field: a list of 5-10 normalized lowercase
concept phrases that capture the semantic content. Example:
["sqlite", "connection pooling", "python async", "error handling"]

And an "edges" field: relationships to existing memories (provided as context).
Example: [{"target_id": 42, "rel_type": "supersedes", "weight": 0.9}]
```

Similarity becomes **Jaccard over concept sets** + FTS5 keyword matching. Two memories sharing 4/6 concepts are clearly related. Cost: ~50-100 extra output tokens per extraction on an already-running Sonnet worker. Concept tags are always extracted regardless of which embedding alternative is chosen below.

### Architectural Alternatives for Dense Embeddings

When the corpus grows past ~500 memories and concept overlap alone becomes insufficient, dense vector embeddings stored in `sqlite-vec` provide cosine similarity search. Choose **one** of the following alternatives.

#### Alternative A: Local Embeddings

Run embedding inference on the local machine. Zero cost, fully offline, data never leaves the device.

| Model | Size | Dimensions | Dependencies | Latency | Quality |
|-------|------|-----------|--------------|---------|---------|
| **Model2Vec** (potion-base-8M) | ~8MB | 256 | numpy only | <50ms | ~92% of MiniLM |
| **FastEmbed** (bge-small-en-v1.5) | ~33MB | 384 | onnxruntime | ~200ms | MiniLM-class |

**Recommended default**: Model2Vec for its extraordinary lightness (8MB, numpy-only, 500x faster than sentence-transformers). FastEmbed as the quality upgrade when the ~33MB model + onnxruntime dependency is acceptable.

```python
# Model2Vec example
from model2vec import StaticModel

model = StaticModel.from_pretrained("minishlab/potion-base-8M")
embedding = model.encode(memory.content)  # numpy array, 256d

# Store in sqlite-vec virtual table
db.execute(
    "INSERT INTO vectors(memory_id, embedding) VALUES (?, ?)",
    [memory.id, serialize_float32(embedding)]
)
```

| Advantage | Disadvantage |
|-----------|--------------|
| Zero ongoing cost | Lower quality than cloud models |
| Works offline / air-gapped | Model2Vec 256d limits fine-grained similarity |
| Data never leaves device | FastEmbed adds ~33MB + onnxruntime dep |
| Sub-50ms latency (Model2Vec) | No matryoshka dimension reduction |
| No API keys to manage | CPU-bound on large batch re-embeds |

#### Alternative B: OpenAI Embeddings

Use OpenAI's embedding API. Higher quality vectors, matryoshka dimension reduction, requires network + API key.

| Model | Max Dimensions | Price/M tokens | Batch (50% off) | Use Case |
|-------|---------------|----------------|-----------------|----------|
| **text-embedding-3-small** | 1536 (shortable) | $0.02 | $0.01 | Default for nous — best cost/quality |
| **text-embedding-3-large** | 3072 (shortable) | $0.13 | $0.065 | Maximum quality when cost is secondary |

Both models support **matryoshka dimension reduction** — you can request fewer dimensions (e.g., 256 or 512) and the leading dimensions remain meaningful. This lets you tune the storage/quality tradeoff without re-embedding.

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY env var
response = client.embeddings.create(
    input=[memory.content],
    model="text-embedding-3-small",
    dimensions=512  # Matryoshka: use fewer dims to save storage
)
embedding = response.data[0].embedding

# Store in sqlite-vec virtual table
db.execute(
    "INSERT INTO vectors(memory_id, embedding) VALUES (?, ?)",
    [memory.id, serialize_float32(embedding)]
)
```

**Batch API** available for bulk re-embedding: 50% discount, 24h window. Ideal for initial migration of existing memories.

| Advantage | Disadvantage |
|-----------|--------------|
| Highest embedding quality available | Requires network connectivity |
| Matryoshka dimension reduction (tune storage vs quality) | API key management |
| 50% batch discount for bulk operations | Per-token cost (low but non-zero) |
| No local model to download or update | Data sent to OpenAI servers |
| Consistent results across machines | Latency depends on network (~100-300ms) |

### Choosing an Alternative

| Criterion | Local (Alt A) | OpenAI (Alt B) |
|-----------|--------------|----------------|
| **Cost** | Free | $0.02/M tokens (small) |
| **Privacy** | Data stays local | Data sent to OpenAI |
| **Offline use** | Full support | Requires network |
| **Quality** | Good (92% MiniLM) | Best available |
| **Dimension flexibility** | Fixed (256 or 384) | Matryoshka (any ≤ 1536/3072) |
| **Setup complexity** | `pip install model2vec` | API key + `pip install openai` |
| **Batch re-embed** | CPU-bound, free | 50% discount, 24h window |

Either alternative integrates identically with `sqlite-vec` and the hybrid retrieval pipeline — the only difference is how the embedding vector is produced. Both can be swapped at any time by re-embedding the corpus.

---

## Hybrid Retrieval Pipeline

### The Scoring Function

```python
def score_memory(memory, context, active_memories):
    """Seven-dimensional relevance scoring with bi-temporal awareness."""
    s_text = fts5_rank(context.fingerprint, memory)        # Keyword match
    s_concept = jaccard(context.concepts, memory.concepts)  # Concept overlap
    s_vector = vector_similarity(context.embedding, memory) # Cosine via sqlite-vec (0.0 if unavailable)
    s_graph = graph_proximity(active_memories, memory)      # Edge distance
    s_reinforce = memory.reinforcement_score                # Proven useful
    s_temporal = temporal_relevance(memory, context)         # Bi-temporal validity
    s_recency = decay(memory.accessed_at, half_life=30)     # Freshness

    return (
        0.15 * s_text
      + 0.15 * s_concept
      + 0.15 * s_vector       # Dense embedding similarity
      + 0.15 * s_graph
      + 0.15 * s_reinforce
      + 0.15 * s_temporal
      + 0.10 * s_recency
    )
```

### Context Fingerprint

At injection time, build a fingerprint from available signals:

```python
def build_fingerprint(project_dir):
    """Infer what the user is likely working on."""
    signals = []
    # Recent file activity from git
    signals += recent_files_from_git(project_dir, n=20)
    # Current branch name
    signals += [current_branch(project_dir)]
    # Language/framework hints from file extensions
    signals += detect_tech_stack(project_dir)
    return " ".join(signals)
```

### Graph Traversal

```sql
-- Find memories connected to already-selected memories
-- within 2 hops, weighted by edge strength
WITH RECURSIVE connected AS (
    SELECT target_id AS memory_id, weight, 1 AS depth
    FROM edges
    WHERE source_id IN (SELECT id FROM active_memories)
    UNION ALL
    SELECT e.target_id, e.weight * 0.5, c.depth + 1
    FROM edges e
    JOIN connected c ON e.source_id = c.memory_id
    WHERE c.depth < 2
)
SELECT memory_id, MAX(weight) as proximity
FROM connected
GROUP BY memory_id;
```

### Reinforcement Loop

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    A[Inject memories at session start] --> B[Log access in access_log]
    B --> C{Session outcome}
    C -->|Successful completion| D[Increment reinforcement +0.1]
    C -->|User corrected something| E[Decrement reinforcement -0.2]
    C -->|Memory not referenced| F[No change]
    D & E & F --> G[Apply time decay every 30 days]
    G --> H[Low scoring memories archived]
```

### Re-Learning Detection

When the same insight is extracted from multiple sessions, it signals either reinforcement (the learning is genuinely important) or injection failure (the learning was extracted but never successfully surfaced). Distinguishing these requires tracking re-extraction patterns and correlating with access history.

**Three-Tier Detection Pipeline**:

| Tier | Method | Threshold | Cost | Catches |
|------|--------|-----------|------|---------|
| 1 | Jaccard over tokenized content | >= 0.75 | Zero (in-process) | Near-duplicates, copy-paste variations |
| 2 | TF-IDF cosine / embedding cosine | >= 0.85 | Embedding lookup | Paraphrases, reworded learnings |
| 3 | LLM judgment via `claude --print` | Ambiguous cases only | ~100 tokens/pair | Semantic equivalence across different framing |

At extraction time, Tier 1 runs against existing memories. Matches above threshold skip extraction (current behavior enhanced). Near-misses (0.65-0.74) are logged as **re-learning events** for later analysis.

**Decision Matrix** — when a learning is re-extracted for the Nth time:

| Recurrence | Reinforcement Score | Injection History | Action |
|-----------|-------------------|-------------------|--------|
| High (3+ sessions) | High (>0.7) | Successfully injected | Merge: consolidate into canonical version, boost `reinforcement_score` +0.3 |
| High (3+ sessions) | Low (<0.3) | Never injected or ignored | Flag: injection failure — route to `/nous:review` for investigation |
| High (3+ sessions) | Medium | Injected but ignored | Rewrite: memory text may need clearer phrasing, auto-queue for refinement |
| Low (2 sessions) | Any | Any | Merge silently, increment reinforcement +0.1 |

**Process Mining Metrics** (computed from `learning_events` + `access_log`):

- **Recurrence rate**: `count(re-extractions) / count(sessions)` per learning — flag if >15%
- **Injection effectiveness**: `count(injected_and_session_succeeded) / count(injected)` per learning
- **Burst index**: re-extraction concentrated in short time window (7-day density vs 30-day average) — indicates active struggle with a topic

**Scoring integration**: Recurrence feeds into the scoring function as a modifier on `s_reinforce`. High recurrence + high injection effectiveness = boost (+0.15). High recurrence + low injection effectiveness = penalty (-0.15) — the memory text likely needs rewriting, not more injection.

### Temporal Reconciliation

Claude Code sessions are **temporal islands** ([Helland, "Data on the Outside vs Data on the Inside"](https://queue.acm.org/detail.cfm?id=3415014)): each session operates independently, may run concurrently, and produces learnings without awareness of what other sessions learned. When two sessions extract contradictory facts about the same concept, the system must detect and resolve the conflict.

**Conflict Detection** (two complementary mechanisms):

1. **Causality via vector clocks**: Each session maintains a logical clock incremented per extraction. When session B reads memories produced by session A, B's clock subsumes A's. Two learnings with incomparable clocks are **concurrent** (potential conflict); comparable clocks indicate **sequential** derivation (no conflict). Implementation: store canonicalized `vector_clock_json` on each `LearningEvent`; compare at injection time.

2. **Contradiction via NLI**: For concurrent learnings sharing concept overlap (Jaccard >= 0.5), run a Natural Language Inference check. A cross-encoder fine-tuned on NLI (e.g., `cross-encoder/nli-deberta-v3-small`, ~90% accuracy on short text per [Stanford SNLI](https://nlp.stanford.edu/projects/snli/)) classifies the pair as `entailment`, `neutral`, or `contradiction`. Short learning entries (1-3 sentences) are ideal for NLI — [research shows](https://arxiv.org/html/2405.01259v1) accuracy is higher on short evidence (61.8%) than long evidence (53.4%).

**Resolution Strategies** (CRDT-inspired, per [Shapiro et al.](https://crdt.tech/)):

| Data Type | Strategy | Example |
|-----------|----------|---------|
| **Single-valued facts** | Last-Writer-Wins (LWW) by `valid_from` | "Default branch is main" vs "Default branch is develop" — latest `valid_from` wins |
| **Concept tags** | OR-Set (add-wins union) | Session A tags `[react, hooks]`, Session B tags `[react, state]` → merged `[react, hooks, state]` |
| **Contradictions** | Emit paired `LearningContradicted` events, keep both with reduced scores | "Use class components" vs "Use functional components" — both retained, both penalized (×0.7) |
| **Sequential supersession** | Emit `LearningSuperseded` event on older learning | Session B explicitly updates a fact from Session A |

**Reconciliation Flow** (two-tier, respecting the hook latency budget):

Reconciliation runs in two tiers to stay within the SessionStart hook's latency budget (see [Hook Latency Policy](#hook-latency-policy)). The **fast path** (vector clock + cached NLI) runs inline during injection. The **full path** (NLI classification for uncached pairs) runs asynchronously after injection.

```python
def reconcile(candidate_memories, context):
    """Detect and resolve conflicts before injection (fast path only)."""
    clusters = cluster_by_concept_overlap(candidate_memories, threshold=0.5)
    deferred_pairs = []
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        for a, b in pairwise(cluster):
            if vector_clocks_comparable(a.vector_clock, b.vector_clock):
                continue  # Sequential — no conflict possible
            cached = nli_cache_lookup(a.id, b.id)
            if cached is not None:
                label, confidence = cached
                if label == "contradiction" and confidence >= 0.7:
                    a.score *= 0.7
                    b.score *= 0.7
            else:
                deferred_pairs.append((a, b))  # Queue for async NLI
    if deferred_pairs:
        schedule_async_reconciliation(deferred_pairs)
    return sorted(candidate_memories, key=lambda m: m.score, reverse=True)


def async_reconcile(pairs):
    """Full NLI classification — runs after injection completes."""
    for a, b in pairs:
        nli_label, confidence = nli_classify(a.content, b.content)
        nli_cache_store(a.id, b.id, nli_label, confidence)
        if nli_label == "contradiction" and confidence >= 0.7:
            # Paired events: keep both learnings active but penalize confidence symmetrically
            emit_event(
                "LearningContradicted",
                learning_id=a.id,
                payload={
                    "contradicted_with": b.id,
                    "contradiction_multiplier": 0.7,
                },
            )
            emit_event(
                "LearningContradicted",
                learning_id=b.id,
                payload={
                    "contradicted_with": a.id,
                    "contradiction_multiplier": 0.7,
                },
            )
        # Low confidence: defer action, do not mutate truth state
```

**Why two tiers**: Extraction is per-session and has no visibility into concurrent sessions. Injection is the natural reconciliation boundary ([Helland](https://queue.acm.org/detail.cfm?id=3415014)), but per-pair NLI classification (~50-200ms per pair) can exceed the hook latency budget for large candidate sets. The fast path uses vector clocks (pure comparison, <1ms) and a persistent NLI cache (`nli_results` table keyed by `(memory_id_a, memory_id_b)`) to handle known pairs inline. Unknown pairs are deferred to an async worker that runs after injection completes — results are cached for the next session's fast path. This means first-encounter contradictions are surfaced one session late, which is acceptable: the alternative (blocking injection for NLI) would violate the latency SLO.

**`nli_results` canonical key/index contract**:

```sql
CREATE TABLE nli_results (
    id INTEGER PRIMARY KEY,
    memory_id_a INTEGER NOT NULL,
    memory_id_b INTEGER NOT NULL,
    CHECK (memory_id_a < memory_id_b),
    nli_label TEXT NOT NULL CHECK (nli_label IN ('entailment', 'neutral', 'contradiction')),
    confidence REAL NOT NULL,
    model_version TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(memory_id_a, memory_id_b)
);

CREATE INDEX idx_nli_results_updated_at ON nli_results(updated_at);
```

Pair ordering must be canonicalized before lookup/write (`memory_id_a = min(id1,id2)`, `memory_id_b = max(id1,id2)`) so `(A,B)` and `(B,A)` resolve to the same cache record.

---

## Cherry-Picked Must-Haves from v1

These gaps from the v1 whitepaper are **independent of the storage migration** and must be addressed regardless:

### Extraction Reliability (Critical)

| Gap | Fix | Effort | Status |
|-----|-----|--------|--------|
| **G1**: Cursor advances before extraction completes | Two-phase cursor: `pending.json` on spawn, promote on success | 3 days | Prerequisite for migration |
| **G5**: No retry on extraction failure | Failed extraction queue with 3-attempt backoff | 1 week | Can parallel with migration |
| **G7**: Unbounded extraction cost | Switch `EXTRACTION_MODEL` to Sonnet. One-line change. | 1 hour | **Do immediately** |
| **G10**: No self-healing | Error rate tracking + alert after threshold | 3 days | Post-migration |

### Prompt Safety (Quick Win)

| Gap | Fix | Effort | Status |
|-----|-----|--------|--------|
| **G14**: jq in extraction prompts | Replace with Read tool instructions | 2 hours | **Do immediately** |

### Feature (Post-Migration)

| Gap | Fix | Effort | Status |
|-----|-----|--------|--------|
| **G6**: suggested_target unused | Queue pending updates; `/nous:review` command | 2 weeks | Intelligence layer |
| **G12**: Fixed thresholds | Make configurable via `.claude/nous/config.json` | 1 day | Anytime |
| **G13**: Observability | Structured metrics in cortex.db + `/nous:metrics` | 1 week | Post-migration |

### Gaps Absorbed by Migration

These v1 gaps are **solved by the architecture change** and need no separate fix:

| Gap | How Migration Solves It |
|-----|------------------------|
| **G2**: Unbounded storage | SQLite rotation: `DELETE FROM memories WHERE id NOT IN (SELECT id FROM memories ORDER BY reinforcement_score DESC LIMIT 2000)` |
| **G3**: Naive last-N injection | Replaced by hybrid scoring pipeline |
| **G8**: Fragment race condition | SQLite transactions replace file-level locking |
| **G9**: Cross-project isolation | Global memories table: `scope TEXT CHECK(scope IN ('project', 'global'))` column |
| **G11**: Weak deduplication | Concept similarity + embedding distance at insert time |

---

## Migration Path

### JSONL to SQLite Migration

Legacy source naming varies by plugin version. Migration discovery should include:

1. Legacy memory logs (`engram.jsonl`, `cortex.jsonl`) when present.
2. Session transcripts under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl`.
3. Subagent transcripts under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/subagents/*.jsonl`.

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> ReadJSONL
    ReadJSONL: Read existing engram.jsonl and cortex.jsonl
    ReadJSONL: Parse all entries

    ReadJSONL --> CreateDB
    CreateDB: Create cortex.db with schema
    CreateDB: Enable WAL mode and FTS5

    CreateDB --> AppendEvents
    AppendEvents: Append each legacy entry as LearningExtracted event
    AppendEvents: idempotency_key includes project_id and extractor_version

    AppendEvents --> ProjectMemories
    ProjectMemories: Build memories table via projection replay

    ProjectMemories --> BackfillConcepts
    BackfillConcepts: Run concept extraction on existing entries
    BackfillConcepts: Batch via claude print

    BackfillConcepts --> BackfillEdges
    BackfillEdges: Identify relationships between entries
    BackfillEdges: Batch via claude print

    BackfillEdges --> SwitchOver
    SwitchOver: Update nous.py to read from cortex.db
    SwitchOver: Keep JSONL as backup for 30 days

    SwitchOver --> [*]
```

Migration must preserve event sourcing invariants: legacy JSONL content is imported into `learning_events` as `LearningExtracted` records, and `memories` is rebuilt from projection replay. Direct writes into `memories` are not a valid migration path.

Legacy normalization rules for imported records:

1. If extractor metadata is missing, set `payload.extractor_version = "legacy-v1"` and `schema_version = 1`.
2. If concepts/edges are missing, allow empty arrays in schema v1 and populate them during `BackfillConcepts`/`BackfillEdges`.
3. Assign deterministic migration scope (`project_id = "legacy-migration"` when original project is unknown) before computing idempotency.

### Backwards Compatibility

- First 30 days: write to both JSONL and SQLite
- Old nous versions see JSONL as usual
- New nous reads from SQLite, falls back to JSONL if cortex.db missing
- After 30 days: JSONL write path removed

---

## Historical Session Ingestion

The bi-temporal architecture and event-sourced log create a separation that enables a critical capability: **retroactive learning from historical sessions**. In v3, live extraction and historical extraction share one ingestion contract: watch/reconcile/backfill all converge to the same immutable `LearningEvent` stream.

### Unified Capture Architecture (Watch + Reconcile + Backfill)

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph Online["Online Capture"]
        L1[Filesystem watch event] --> L2[Read appended bytes from cursor]
        L2 --> L3[Parse complete JSON lines]
        L3 --> L4["Emit ingest events<br/>source = fs_watch"]
    end

    subgraph Recovery["Recovery Capture"]
        R1[Startup reconcile scan] --> R2[Periodic deep scan]
        R2 --> R3["Detect missed, rotated,<br/>or truncated files"]
        R3 --> R4["Emit ingest events<br/>source = fs_reconcile"]
    end

    subgraph Historical["Historical Path (CLI / Cron)"]
        H1["Read ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl"] --> H2[Batch extract with same prompt]
        H2 --> H3["Emit ingest events<br/>source = historical_backfill"]
    end

    subgraph Shared["Shared Processing and Storage"]
        S0[(ingest_events)]
        S1[Extractor workers]
        S2[(learning_events)]
        S3[Projection function]
        S4[(memories — materialized view)]
        S5[(concepts + edges + access_log)]
    end

    L4 --> S0
    R4 --> S0
    H3 --> S0
    S0 --> S1 --> S2
    S2 --> S3 --> S4
    S3 --> S5
```

All three paths use the same extraction prompt, schema validation, idempotency envelope, and event types. The only differences:

| Property | Watch Path | Reconcile Path | Historical Backfill |
|----------|------------|----------------|--------------------|
| **Trigger** | Filesystem change notifications | Startup + periodic scan | `nous backfill --since 90d` CLI |
| **Latency target** | Near-real-time | Eventual consistency safety net | Bulk/offline |
| **Transaction time** | Now (ingest moment) | Now (scan ingest moment) | Now (batch ingest moment) |
| **Valid time** | Estimated from session context | Estimated from session context | Session timestamp / inferred window |
| **Idempotency** | `idempotency_key = sha256(project_id + session_id + learning_index + extractor_version)` + per-file cursor | Same key + scan dedup | Same key + batch dedup |
| **Primary purpose** | Freshness | Correctness (no missed data) | Cold start + retroactive learning |

### Ingest Queue Durability Contract

`ingest_events` is a durable queue, not an in-memory buffer. Restart safety and retry semantics are required to preserve effectively-once ingestion.

```sql
CREATE TABLE ingest_events (
    ingest_id INTEGER PRIMARY KEY,
    source TEXT NOT NULL CHECK (source IN ('fs_watch', 'fs_reconcile', 'historical_backfill')),
    project_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    transcript_path TEXT NOT NULL,
    file_inode TEXT,
    file_offset INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'dead_letter')),
    retry_count INTEGER NOT NULL DEFAULT 0,
    claimed_by TEXT,
    claimed_at TEXT,
    lease_expires_at TEXT,
    next_attempt_at TEXT,
    last_error TEXT,
    idempotency_key TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(idempotency_key)
);

CREATE INDEX idx_ingest_events_status_next ON ingest_events(status, next_attempt_at);
CREATE INDEX idx_ingest_events_lease ON ingest_events(status, lease_expires_at);

CREATE TABLE ingest_cursors (
    cursor_id INTEGER PRIMARY KEY,
    transcript_path TEXT NOT NULL,
    file_inode TEXT,
    last_offset INTEGER NOT NULL,
    last_mtime TEXT,
    updated_at TEXT NOT NULL,
    UNIQUE(transcript_path, file_inode)
);

CREATE TABLE processed_extractions (
    project_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    learning_index INTEGER NOT NULL,
    latest_event_id INTEGER NOT NULL,
    latest_extractor_version TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (project_id, session_id, learning_index)
);
```

Processing rules:

1. Transitions: `pending -> processing -> completed|failed`; `failed` retries with backoff; terminal `dead_letter` after max attempts.
2. Cursor promotion occurs only after `completed`; failed events do not advance cursor.
3. Reconcile scans may re-enqueue observed artifacts; queue-level `idempotency_key` uniqueness prevents duplicate processing.
4. Claim protocol: worker sets `claimed_by`, `claimed_at`, `lease_expires_at` when moving to `processing`; heartbeat extends lease while work is active.
5. Recovery protocol (deterministic): a sweeper finds stale `processing` rows (`lease_expires_at < now()`), increments `retry_count`, sets `last_error='lease_expired'`, sets `status='pending'`, and computes `next_attempt_at` using standard retry backoff.

### Extractor Version Replay Policy

The idempotency key includes `project_id`, `session_id`, and `extractor_version`, but extractor upgrades must not silently duplicate history.

Default mode (`NOUS_REEXTRACT_ON_VERSION_CHANGE=false`):

1. Watch/reconcile process only new appended transcript data from cursors.
2. Backfill skips already-processed `(project_id, session_id, learning_index)` tuples using `processed_extractions`, regardless of extractor version.
3. Upgrade applies only to newly observed artifacts.

Optional re-extract mode (`NOUS_REEXTRACT_ON_VERSION_CHANGE=true`):

1. Run explicit reprocess command (`nous reextract --since ... --from-version ... --to-version ...`).
2. Reprocessed learnings emit compensating lifecycle events (`LearningSuperseded` and/or `LearningWeakened`) instead of silently creating parallel active duplicates.
3. Replay/audit preserves both old and new extractor outputs with explicit lineage.

### Backfill Processor Design

The historical processor reads session JSONL transcripts, applies the same extraction prompt used by live extraction, and writes events with backdated `valid_from` timestamps. Corrections are mined from the transcript itself: when a user explicitly corrected Claude's behavior, this produces retroactive `LearningWeakened` events.

```python
# External workflow — out-of-band pipeline (never inline in hooks)
# Run as: python -m nous.backfill [--project PATH] [--since DATE]
import os
from pathlib import Path
from uuid import uuid4

CLAUDE_CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))
EVENT_SCHEMA_VERSION = 2

for session_file in glob(f"{CLAUDE_CONFIG_DIR}/projects/**/*.jsonl", recursive=True):
    if not is_session_transcript(session_file):
        continue
    transcript = parse_session(session_file)
    transcript.project_id = transcript.project_id or "unknown-project"
    learnings = extract_learnings(transcript, existing_memories)
    reextract_mode = os.environ.get("NOUS_REEXTRACT_ON_VERSION_CHANGE", "false").lower() == "true"

    for learning_index, entry in enumerate(learnings):
        if not reextract_mode and already_processed_tuple(
            transcript.project_id, transcript.session_id, learning_index
        ):
            continue  # Default mode: tuple-level dedup regardless of extractor version

        idempotency_key = sha256(
            f"{transcript.project_id}:{transcript.session_id}:{learning_index}:{EXTRACTOR_VERSION}"
        )

        if reextract_mode and already_processed_tuple(
            transcript.project_id, transcript.session_id, learning_index
        ):
            emit_compensating_events_for_reextract(transcript, learning_index, entry)

        write_event(LearningEvent(
            event_type="LearningExtracted",
            event_uuid=str(uuid4()),
            idempotency_key=idempotency_key,
            schema_version=EVENT_SCHEMA_VERSION,
            transaction_time=now(),
            valid_from=transcript.start_time,
            valid_until=estimate_validity(entry, transcript.project),
            source="historical_backfill",
            payload=entry
        ))
        mark_processed_extraction(
            project_id=transcript.project_id,
            session_id=transcript.session_id,
            learning_index=learning_index,
            extractor_version=EXTRACTOR_VERSION,
        )

    # Mine user corrections → retroactive negative reinforcement
    for correction in detect_user_corrections(transcript):
        related = find_related_memory(correction.context)
        if related:
            write_event(LearningEvent(
                event_type="LearningWeakened",
                learning_id=related.id,
                transaction_time=now(),
                valid_from=transcript.start_time,
                payload={"reinforcement_delta": -0.1, "reason": "user_correction_historical"}
            ))
```

### Process Mining Unlocked

With a complete event history (live + backfilled), process mining across the full session corpus becomes tractable:

| Metric | Definition | Value |
|--------|-----------|-------|
| **Recurrence rate** | How often the same learning is re-extracted across sessions | Measures injection effectiveness — high recurrence = injection failure |
| **Learning velocity** | Rate of new unique learnings per session over time | Measures knowledge acquisition rate; declining velocity = maturing codebase |
| **Correction density** | Ratio of `LearningContradicted`/`LearningSuperseded` events to `Active` | Measures knowledge stability; high density = volatile domain |
| **Knowledge decay** | Time between last access and current date for active memories | Identifies stale knowledge candidates for archival |
| **Complexity hotspots** | Domains with highest recurrence + correction density | Targets for skill/CLAUDE.md investment |

### Solving the Bootstrap Problem

New installations face a cold-start problem: no memories, no reinforcement data, no graph. Historical ingestion solves this. A developer who has used Claude Code for months has hundreds of sessions containing extractable knowledge. The backfill command (`nous backfill --since 90d`) processes these sessions and populates cortex.db with a rich initial corpus, complete with temporal metadata and cross-session relationships. The bi-temporal model ensures these backdated learnings are distinguished from live-extracted ones — `transaction_time` reflects when the batch ran, while `valid_from` reflects when the session actually happened.

---

## Implementation

The architecture described above is the target end-state, built as a single coordinated effort. Dependencies dictate sequence — not artificial phases. With Claude as the implementation engine, a single pass is equivalent to weeks of phased team work.

### Dependency Order

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    P[Prerequisites] --> S[Schema +<br/>Event Sourcing]
    S --> C[Capture +<br/>Ingestion Pipeline]
    C --> X[Extraction<br/>Workers]
    S --> V[Embedding<br/>Integration]
    X --> R[Retrieval<br/>Pipeline]
    V --> R
    S --> H[Historical<br/>Ingestion]
    R --> I[Intelligence<br/>Layer]
    H --> I
```

**Prerequisites** — unblock everything:
1. Define runtime contracts (`ResolveContext`, `IngestArtifact`, `Feedback`, `Backfill`) with identity/idempotency envelopes and v1 hook policy (`SessionStart` enabled, `UserPromptSubmit` feature-flagged off by default, `Stop` optional notify-only).
2. Standardize `.env` defaults and path overrides (`CLAUDE_CONFIG_DIR`, data dir, socket/HTTP bind, archive dir).
3. Ship a Docker Compose starter profile for local-first deployment and lightweight client integration.
4. Switch `EXTRACTION_MODEL` to Sonnet.
5. Replace jq usage with Claude-native tools in extraction prompts.

**Schema + Event Sourcing** — the foundation:
6. Create `cortex.db` with all tables: `learning_events`, `memories`, `concepts`, `edges`, `access_log`, `vectors`, `nli_results`, `projection_checkpoints`, `injection_cache`, `ingest_events`, `ingest_cursors`, `processed_extractions`, `intervention_candidates`, `active_interventions`.
7. Enable WAL mode, FTS5, foreign keys.
8. Implement projection function: `learning_events` -> materialized `memories` table.
9. Write JSONL-to-SQLite migration script (import existing entries as `LearningExtracted` events).
10. Add event source taxonomy (`fs_watch`, `fs_reconcile`, `historical_backfill`, `user_review`) and enforce schema validation.
11. Preserve replay guarantees: append-only events retained indefinitely, hot/cold archive support.

**Capture + Ingestion Pipeline** — out-of-band by default:
12. Implement filesystem watch using `NOUS_PROJECT_GLOB` (default `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl`) plus subagent transcripts.
13. Implement startup reconcile scan and periodic deep scan (missed event recovery).
14. Build per-file cursor tracking (inode/path/offset) with truncate/rotate handling.
15. Parse complete JSONL records incrementally; defer partial lines until complete.
16. Add ingest queue with retries/backoff and dead-letter handling.
17. Canonicalize session artifacts into ingest events (`project_id`, `session_id`, `cwd`, `client_id`, `event_source`).
18. Deduplicate with `idempotency_key = sha256(project_id + session_id + learning_index + extractor_version)`.
19. Keep Stop hook optional and non-blocking (`wake` signal only).

**Extraction Workers** — enrich what we capture:
20. Modify extraction prompts: `concepts`, `edges`, `valid_from`/`valid_until`, `temporal_confidence`.
21. Implement strict schema validation on extraction output.
22. Add retry queue for failed extractions with bounded exponential backoff.
23. Emit compensating events for parser/extractor corrections rather than mutating records.

**Embedding Integration** — dense vector similarity (parallelizable with extraction):
24. Integrate `sqlite-vec` as dependency.
25. Implement embedding provider interface (Local or OpenAI — see Embedding Strategy).
26. Embed at extraction time; batch-embed existing corpus on migration.
27. Add vector similarity as a first-class scoring dimension.

**Retrieval Pipeline** — seven-dimension hybrid scoring:
28. Context fingerprint builder (recent files, branch, tech stack).
29. FTS5 + concept Jaccard + graph traversal + reinforcement + temporal + recency scoring.
30. Access log tracking and reinforcement feedback loop.
31. Time decay function (30-day half-life).
32. Re-learning detection: three-tier pipeline (Jaccard -> TF-IDF/embedding -> LLM judgment).
33. Temporal reconciliation: vector clocks for causality, NLI for contradiction, LWW/OR-Set merge.
34. Precompute runtime injection cache for low-latency `SessionStart` and optional `UserPromptSubmit`.

**Historical Ingestion** — retroactive learning (parallelizable with retrieval):
35. Session reader using `NOUS_PROJECT_GLOB` (default `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl`) with transcript-type filtering.
36. Unified-path architecture: watch + reconcile + backfill -> shared event store.
37. Backfill processor: same extraction prompt, idempotent via `sha256(project_id + session_id + learning_index + extractor_version)`.
38. Mine correction signals from historical transcripts -> retroactive `LearningWeakened` events.
39. Bootstrap mode: `nous backfill --since 90d` populates cortex.db from session history.

**Intelligence Layer** — leverage the full architecture:
40. Add observer pipelines for proactive/corrective intervention candidates.
41. Materialize intervention read model with TTL, cooldown, and dedupe policy.
42. Activate `suggested_target` automation for CLAUDE.md/skills updates.
43. Community detection over memory graph (Leiden-inspired clustering).
44. Cross-project global knowledge layer.
45. Process mining: recurrence rate, learning velocity, correction density, knowledge decay, complexity hotspots.
46. Commands: `/nous:review`, `/nous:status`, `/nous:metrics`.
47. Configurable thresholds via `.claude/nous/config.json`.

---

## Operational Policies

### Hook Latency Policy

Claude Code hooks must return quickly to avoid blocking the session. All Nous hooks operate under explicit latency SLOs:

| Hook | SLO | Budget Allocation | Timeout Behavior |
|------|-----|-------------------|------------------|
| **SessionStart** (required injection) | **< 250ms** total | Fingerprint 10ms, resolver lookup 40ms, cached payload assembly 40ms, stdout 10ms | Hard timeout at 500ms; fail-open to empty/minimal context |
| **UserPromptSubmit** (feature-flagged, v1 default off) | **< 150ms** total when enabled | Staleness check 10ms, resolver lookup 30ms, cached payload assembly 30ms | Disabled by default (`NOUS_ENABLE_USERPROMPTSUBMIT=false`); if enabled, skip injection on timeout and continue prompt |
| **Stop** (optional notify) | **< 20ms** total | Fire-and-forget wake signal only | Drop signal on timeout; reconcile scanner will recover |
| **PreCompact** | **< 50ms** | Metadata snapshot only | Skip on timeout — next session retries |

**Inline determinism rule**: Hooks may only execute deterministic read-path operations (fingerprint, cache lookup, payload formatting). Extraction, embeddings, NLI, reconciliation full path, and archive work are strictly out-of-band.

**Async fallback rule**: Any operation that cannot guarantee completion within the hook's SLO must be deferred to async workers driven by watch/reconcile/backfill ingestion and background job queues.

**Timeout semantics**: Hard timeouts are fail-open — the session proceeds with degraded but functional results (less context, no intervention). Failures are logged for observability and recovered by the out-of-band pipeline.

### Hook Latency Validation Plan

SLO claims above are not considered complete until benchmarked and recorded. v1 acceptance requires:

1. Run hook benchmarks on representative datasets (cold cache and warm cache) for at least 200 session starts per profile.
2. Capture p50/p95/p99 for each hook path (`SessionStart`, optional `UserPromptSubmit`, `Stop`) and include timeout/fail-open rate.
3. Pass criteria: `SessionStart p95 <= 250ms`, `UserPromptSubmit p95 <= 150ms` (when enabled), `Stop p95 <= 20ms`.
4. Archive benchmark artifacts (`benchmark.json`, config snapshot, hardware profile) with release notes for regression comparison.

### Event Type Validation

All event types must be validated against the canonical enum at write time. Unknown event types are rejected at ingestion — they indicate a bug in the producer, not new behavior:

```python
VALID_EVENT_TYPES = {
    "LearningExtracted", "LearningValidated", "LearningReinforced",
    "LearningWeakened", "LearningContradicted", "LearningSuperseded",
    "LearningArchived",
}

def validate_event(event: LearningEvent) -> None:
    if event.event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event.event_type}")
```

### Event Payload Validation

Event type checks are necessary but insufficient. Writers must validate payload shape/required keys per event type before append:

```python
REQUIRED_PAYLOAD_KEYS = {
    # concepts/edges are required for modern extraction (schema >= 2)
    # but optional for legacy migration records (schema == 1)
    "LearningExtracted": {"content", "extractor_version"},
    "LearningValidated": set(),
    "LearningReinforced": {"reinforcement_delta"},
    "LearningWeakened": {"reinforcement_delta"},
    "LearningContradicted": {"contradicted_with", "contradiction_multiplier"},
    "LearningSuperseded": {"superseded_by"},
    "LearningArchived": {"reason"},
}

def validate_event_payload(event: LearningEvent) -> None:
    required = REQUIRED_PAYLOAD_KEYS[event.event_type]
    missing = required - set(event.payload.keys())
    if missing:
        raise ValueError(f"Missing payload keys for {event.event_type}: {sorted(missing)}")
    if event.event_type == "LearningExtracted" and event.schema_version >= 2:
        for k in ("concepts", "edges"):
            if k not in event.payload:
                raise ValueError(f"Missing payload key for {event.event_type} schema>=2: {k}")
```

`schema_version` gates payload evolution: new keys may be added in a new schema version, but required keys for an existing version are immutable.

### Vector Clock Contract

`vector_clock_json` uses a canonical JSON object: `{ "<session_id>": <counter_int>, ... }`.

1. Keys are session IDs; values are positive integers.
2. Serialization is canonicalized by lexicographically sorted keys with no duplicate keys.
3. Missing/NULL clock is treated as `{}`.
4. Merge uses component-wise max; local extraction increments only the current session key by 1.
5. To control growth, retain the current session key plus up to 63 most-recently-observed peer keys (max 64 keys total), preserving canonical sort in persisted JSON.

### Retention Policy

`learning_events` is append-only and retained indefinitely. The immutable event log is the system's source of truth and must never be pruned or truncated. Projection/read-model tables (`memories`, `concepts`, `edges`, `access_log`) may be pruned, compacted, or fully rebuilt from event history at any time. Any storage-management job must preserve replayability and auditability of the complete event stream.

**Archival mechanics**: As the event log grows, a hot/cold tiering strategy keeps query performance stable:

| Tier | Scope | Storage | Access Pattern |
|------|-------|---------|----------------|
| **Hot** | Events from last 90 days | `cortex.db` main file | Incremental projection, real-time queries |
| **Cold** | Events older than 90 days | `cortex-archive-{YYYY}.db` segmented by year | Full replay, historical analysis, audit |

- **Segmentation**: A background job (`nous archive --before 90d`) moves events older than the retention window into year-segmented archive files. Each archive is a standalone SQLite database with the same `learning_events` schema.
- **Compression**: Archive files are compressed with zstd after write (`cortex-archive-{YYYY}.db.zst`). Typical compression ratio for JSON event payloads: 5-8x.
- **Replay/restore**: Full replay reads hot + cold tiers in `event_id` order. The `replay` command accepts `--include-archives` to span all tiers. Restoring an archive to hot tier: `nous restore --archive cortex-archive-2025.db.zst`.
- **Integrity**: Each archive records a `min_event_id`/`max_event_id` range and a SHA-256 checksum over the event stream. Restore verifies checksum before merging.
- **Projection independence**: Projections are always rebuildable from the complete event stream (hot + cold). Archive segmentation never affects projection correctness — only replay speed when cold tiers are excluded.

Archive manifest contract (cataloged in hot storage):

```sql
CREATE TABLE archive_segments (
    segment_id TEXT PRIMARY KEY,
    archive_path TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL CHECK (tier IN ('cold')),
    min_event_id INTEGER NOT NULL,
    max_event_id INTEGER NOT NULL,
    event_count INTEGER NOT NULL,
    stream_checksum_sha256 TEXT NOT NULL,
    compressed_bytes INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    restored_at TEXT
);

CREATE INDEX idx_archive_segments_event_range ON archive_segments(min_event_id, max_event_id);
```

Every archive/restore operation must update `archive_segments` transactionally with event movement.

### Projection Checkpoints

For efficiency at scale, projectors track their progress via a checkpoint table rather than replaying the full event stream on every rebuild:

```sql
CREATE TABLE projection_checkpoints (
    projector_name TEXT PRIMARY KEY,
    last_event_id INTEGER NOT NULL,
    updated_at TEXT NOT NULL
);
```

Incremental projection processes only events after `last_event_id`. Full replay (from `event_id = 0`) remains available for correctness verification or schema migration.

### Observer and Intervention Model (Out-of-Band)

Associative memory and proactive intervention are distinct concerns sharing one substrate. v3 treats intervention as a downstream consumer of event/projection state:

1. **Observers** consume `learning_events` plus read models and detect conditions (e.g., repeated corrections, stalled progress, high contradiction density, user frustration signals).
2. **Candidates** are emitted as immutable `InterventionCandidate` records (append-only).
3. **Policy reducer** applies thresholds, cooldowns, and dedupe to materialize `active_interventions`.
4. **Precompute cache** builds per-session/per-project injection packets consumed by `ResolveContext`.

This keeps heavy interpretation outside hook lifecycles while preserving explainability and audit.

| Field | Purpose |
|-------|---------|
| `intervention_id` | Stable ID for audit and dedupe |
| `scope` (`session|project|global`) | Routing boundary for injection |
| `reason_codes[]` | Human/metric-readable trigger rationale |
| `confidence` | Policy threshold input |
| `priority` | Tie-break ordering |
| `ttl_seconds` | Automatic expiry window |
| `cooldown_seconds` | Anti-spam guardrail |
| `payload_text` | Injected guidance text |
| `state` (`candidate|approved|suppressed|delivered|expired`) | Lifecycle state |

Canonical persistence contract:

```sql
CREATE TABLE intervention_candidates (
    candidate_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL CHECK (scope IN ('session', 'project', 'global')),
    target_session_id TEXT,
    target_project_id TEXT,
    reason_codes_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    ttl_seconds INTEGER NOT NULL,
    cooldown_seconds INTEGER NOT NULL,
    payload_text TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('candidate', 'approved', 'suppressed', 'delivered', 'expired')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE active_interventions (
    intervention_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL CHECK (scope IN ('session', 'project', 'global')),
    target_session_id TEXT,
    target_project_id TEXT,
    payload_text TEXT NOT NULL,
    priority INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    cooldown_until TEXT,
    dedupe_key TEXT NOT NULL UNIQUE,
    source_candidate_id TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_active_interventions_scope ON active_interventions(scope, target_session_id, target_project_id, expires_at);
```

### Agent-Service Interface

The system is designed to run locally but expose a clean service boundary so containerized infrastructure can serve multiple clients and mediums (terminal, VS Code, machine A, machine B). v3 separates the interface into a thin runtime plane and a background processing plane:

| API | Plane | Direction | Contract |
|-----|-------|-----------|----------|
| **ResolveContext** | Runtime (hook path) | Read | Accept fingerprint + identity envelope; return precomputed `additional_context` and optional intervention payload |
| **IngestArtifact** | Background | Write | Accept parsed transcript artifacts with file cursor metadata; dedup and enqueue extraction |
| **AppendEvent** | Background | Write | Append a `LearningEvent` with `idempotency_key`; reject duplicates |
| **Feedback** | Runtime/Background | Write | Accept `memory_id` + signal (`useful`, `corrected`, `ignored`) + `session_outcome` |
| **Backfill** | Background | Write | Batch ingest from historical transcripts; same idempotency guarantees as `AppendEvent` |
| **Replay/Archive** | Ops | Read/Write | Rebuild projections, archive cold events, restore historical segments |

Every request carries an identity envelope (`project_id`, `session_id`, `client_id`, `event_source`, `tenant_id?`). Every write carries an idempotency envelope (`idempotency_key`, `schema_version`). Runtime endpoints are deterministic and read-only; heavy tasks are background-only.

Transport is pluggable: embedded in-process for local-only, Unix domain socket or localhost HTTP for local container sidecar, mTLS or signed token auth for shared multi-client infrastructure.

#### Backend Provider Contracts

The service implementation is decoupled from specific storage engines via provider interfaces. This allows the default SQLite implementation to be swapped for alternative backends without changing the service API:

| Provider | Interface | Default Implementation | Alternative |
|----------|-----------|----------------------|-------------|
| **EventStore** | `append(event)`, `replay(from_id)`, `get(id)` | SQLite `learning_events` table | PostgreSQL, append-only log |
| **ProjectionStore** | `upsert(memory)`, `delete(id)`, `query(fingerprint, top_k)` | SQLite `memories` + FTS5 | PostgreSQL + pg_trgm |
| **VectorStore** | `insert(id, embedding)`, `search(embedding, top_k)` | `sqlite-vec` virtual table | pgvector, in-memory numpy |
| **GraphStore** | `add_edge(src, tgt, rel, weight)`, `traverse(ids, depth)` | SQLite `edges` adjacency table | Neo4j, NetworkX in-memory |
| **CacheStore** | `get(context_key)`, `put(packet, ttl)`, `invalidate(keys)` | SQLite `injection_cache` table | Redis, in-memory LRU |
| **IngestQueueStore** | `enqueue(artifact)`, `claim(batch)`, `ack(id)`, `fail(id,error)` | SQLite `ingest_events` + `ingest_cursors` | Redis streams, Kafka |
| **InterventionStore** | `append_candidate(c)`, `upsert_active(i)`, `resolve(scope,target)` | SQLite `intervention_candidates` + `active_interventions` | PostgreSQL, Redis |

The default deployment bundles all listed providers over a single `cortex.db` file. Provider interfaces are Python protocols (structural subtyping) — no base class inheritance required. Swapping a provider is a configuration change, not a code change.

#### Deployment Modes

| Mode | Description | Transport | Storage |
|------|-------------|-----------|---------|
| **Embedded local** | Service runs in-process with Claude hook adapter | Direct function call | Single `cortex.db` file |
| **Local Docker Compose (default)** | One local service stack per machine; shared by terminal + VS Code clients | Unix domain socket or localhost HTTP | Container-mounted SQLite (`cortex.db`) |
| **Shared infrastructure (future)** | Centralized service with tenant/workspace isolation for multiple clients in parallel | mTLS or signed token auth | PostgreSQL + pgvector (or sharded SQLite) |

#### Multi-Client Correctness Rules

1. At-least-once delivery assumed from all clients.
2. Service guarantees effectively-once mutation through `idempotency_key` unique constraint.
3. Projection ordering uses `event_id` only — never client-provided timestamps.
4. Conflicts are resolved by the reconciliation engine, not by client-side mutation.
5. Cross-device session events remain auditable by `client_id` and `event_source`.

#### Docker Compose Local Profile (v3 Default)

v3 should ship with a ready-to-run Compose profile where client integrations remain lightweight (hooks call local resolver endpoint only):

```yaml
services:
  nous-api:
    image: ghcr.io/aeyeops/nous-memory:${NOUS_IMAGE_TAG:-latest}
    command: ["nous", "serve"]
    env_file: [".env"]
    environment:
      - CLAUDE_CONFIG_DIR=/claude
      - NOUS_DB_PATH=/data/cortex.db
      - NOUS_ARCHIVE_DIR=/data/archive
      - NOUS_SOCKET_PATH=/run/nous/nous.sock
      - NOUS_HTTP_BIND=0.0.0.0:4317
    volumes:
      - ${CLAUDE_CONFIG_DIR:-$HOME/.claude}:/claude:ro
      - ${NOUS_DATA_DIR:-./.nous-data}:/data
      - nous-run:/run/nous
    ports:
      - "${NOUS_HTTP_PORT:-4317}:4317"

  nous-worker:
    image: ghcr.io/aeyeops/nous-memory:${NOUS_IMAGE_TAG:-latest}
    command: ["nous", "worker"]
    env_file: [".env"]
    environment:
      - CLAUDE_CONFIG_DIR=/claude
      - NOUS_DB_PATH=/data/cortex.db
      - NOUS_ARCHIVE_DIR=/data/archive
    volumes:
      - ${CLAUDE_CONFIG_DIR:-$HOME/.claude}:/claude:ro
      - ${NOUS_DATA_DIR:-./.nous-data}:/data
    depends_on: [nous-api]

  nous-watcher:
    image: ghcr.io/aeyeops/nous-memory:${NOUS_IMAGE_TAG:-latest}
    command: ["nous", "watch"]
    env_file: [".env"]
    environment:
      - CLAUDE_CONFIG_DIR=/claude
      - NOUS_DB_PATH=/data/cortex.db
      - NOUS_PROJECT_GLOB=/claude/projects/**/*.jsonl
    volumes:
      - ${CLAUDE_CONFIG_DIR:-$HOME/.claude}:/claude:ro
      - ${NOUS_DATA_DIR:-./.nous-data}:/data
    depends_on: [nous-api]

volumes:
  nous-run: {}
```

#### `.env` Defaults (Expandability Required)

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_CONFIG_DIR` | `$HOME/.claude` | Host Claude config root to mount/read (must be overridable) |
| `NOUS_DATA_DIR` | `./.nous-data` | Persistent local Nous data (`cortex.db`, archives, checkpoints) |
| `NOUS_DB_PATH` | `/data/cortex.db` | Primary event store + projections |
| `NOUS_ARCHIVE_DIR` | `/data/archive` | Cold archive tier location |
| `NOUS_PROJECT_GLOB` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/**/*.jsonl` | Session artifact discovery pattern |
| `NOUS_HTTP_BIND` | `0.0.0.0:4317` | API bind address (container/service runtime) |
| `NOUS_HTTP_PORT` | `4317` | Local HTTP resolver port |
| `NOUS_SOCKET_PATH` | `/run/nous/nous.sock` | Unix socket path for low-latency local resolver |
| `NOUS_IMAGE_TAG` | `latest` | Container image release pin |
| `NOUS_ENABLE_USERPROMPTSUBMIT` | `false` | Enables prompt-time refresh hook path after v1 validation |

`CLAUDE_CONFIG_DIR` must never be hardcoded to `~/.claude`; all code paths and Compose mounts should resolve the canonical fallback form `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`. In practice the environment variable is often unset and Claude Code uses the fallback root.

---

## Technology Stack and Comparison

### v3 Stack Recommendation (Local-First, Compose-Ready)

| Layer | v3 Default | Why This Fits Current Constraints | Cloud-Ready Upgrade Path |
|-------|------------|-----------------------------------|--------------------------|
| **Runtime resolver API** | Python 3.12 + FastAPI/Uvicorn (or UDS server) | Lightweight, easy local integration from hooks, deterministic read path | Keep contract, move behind gateway/load balancer |
| **Ingestion** | `watchfiles` (or inotify wrapper) + periodic reconcile scanner | Removes Stop-hook extraction dependency; robust against missed FS events | Replace scanner source with object-store/Kafka consumer |
| **Work queue** | SQLite-backed job tables + retry metadata | Zero extra infra for local, durable retries | Swap to Redis/Kafka/SQS without API change |
| **Primary state store** | SQLite (`cortex.db`) + WAL + FTS5 | Embedded, portable, low ops, fast enough for local corpora | PostgreSQL + partitioning for shared multi-tenant workloads |
| **Vector search** | `sqlite-vec` | No external DB required, simple packaging | pgvector or dedicated vector store |
| **Graph relationships** | SQLite adjacency tables (`edges`) | Adequate for current traversal depth and scale | Neo4j/Falkor/graph service via `GraphStore` interface |
| **Cache/read models** | SQLite `injection_cache` + projection tables | Precompute path for low-latency hooks, no external cache required | Redis + materialized views |
| **Containerization** | Docker Compose (`nous-api`, `nous-worker`, `nous-watcher`) | Fast startup for new users, same stack for terminal/VS Code clients | Helm/Terraform + tenant-aware deployment profiles |
| **Config** | `.env` with explicit path overrides (`CLAUDE_CONFIG_DIR`) | Avoid path assumptions, portable across machines/OS layouts | Secret manager + centralized config service |

### Embedding Providers (Feb 2026)

| Provider | Best Model | Dims | Price/M tokens | Batch | Offline |
|----------|-----------|------|----------------|-------|---------|
| **OpenAI** | text-embedding-3-small | 1536 (shortable) | $0.02 | 50% off | No |
| **OpenAI** | text-embedding-3-large | 3072 (shortable) | $0.13 | 50% off | No |
| **Model2Vec** | potion-base-8M | 256 | Free | N/A | Yes |
| **FastEmbed** | bge-small-en-v1.5 | 384 | Free | N/A | Yes |

### sqlite-vec Technical Profile

| Property | Value |
|----------|-------|
| **Language** | Pure C, no dependencies |
| **Install** | `pip install sqlite-vec` |
| **Binary size** | ~2MB |
| **Vector types** | float32, int8, bit |
| **Distance metrics** | L2, cosine, hamming (bit) |
| **Search** | Brute-force O(n) — ANN planned for v1.0 |
| **Scale sweet spot** | Thousands to hundreds of thousands of vectors |
| **Quantization** | Binary (32x reduction), int8 scalar |
| **Performance** | <4ms on 100k vectors with binary quantization |
| **Maturity** | v0.1.6 (Nov 2024). v1.0 targeting 2026. Community forks active. |

### Compared Architectures

| System | Approach | Server? | Deps | Relevance |
|--------|----------|---------|------|-----------|
| **MAGMA** | Multi-graph (semantic/temporal/causal/entity) | Research paper | Heavy | Pattern inspiration: multi-view retrieval |
| **Graphiti/Zep** | Temporal knowledge graph + Neo4j | Yes (Neo4j) | Heavy | Pattern inspiration: bi-temporal model, edge invalidation |
| **LightRAG** | Dual-level graph + vector | Configurable | Moderate | Pattern inspiration: low/high level retrieval |
| **FalkorDBLite** | Embedded graph DB | No (subprocess) | Moderate | Alternative to SQLite adjacency tables |
| **Nous v3** | SQLite + FTS5 + adjacency + sqlite-vec + event sourcing + precomputed injection cache | No | Light | Current target architecture |

---

## Open Questions (To Resolve Before Freeze)

1. **Intervention policy**: What are the initial thresholds for `confidence`, `ttl`, and `cooldown` to avoid over-injection?
2. **Context packet budget**: What max token/char budget is enforced for resolved context/intervention payloads per hook call?
3. **Watcher portability**: Which cross-platform file watch backend is canonical for Linux/macOS/WSL, and what is the tested overflow behavior?
4. **Parser finalization**: What is the exact rule for considering a JSONL line complete and safe to parse under concurrent appends?
5. **Privacy boundaries**: Which fields are excluded/redacted before persistence in `learning_events.payload_json`?
6. **Archive cadence**: What is the initial hot/cold split window (90d default?) and when do we auto-run archive jobs?
7. **Tenant envelope**: For future shared deployment, what are required tenant identifiers and isolation guarantees at API and DB layers?
8. **Promotion criteria**: What objective SLO/quality thresholds trigger promotion from local Compose default to shared infrastructure mode?

---

## Appendix A: ALT — LLM Ranking at Injection Time

### Concept

Instead of building a retrieval index, send all candidate memories to Claude and let it rank them. This inverts the model: **no write-time indexing, all intelligence at read time**.

### How It Works

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    A[Session starts] --> B[Build context fingerprint]
    B --> C[Load ALL memories from cortex.db]
    C --> D{Memory count}
    D -->|Under 100| E[Send all to Claude with ranking prompt]
    D -->|100 to 500| F[Pre filter by domain tag then send to Claude]
    D -->|Over 500| G[Pre filter by FTS5 then send top 50 to Claude]
    E & F & G --> H[Claude returns ranked top 10]
    H --> I[Inject ranked memories]
```

### The Prompt

```
Given the following project context:
- Recent files: {fingerprint}
- Tech stack: {stack}
- Branch: {branch}

And these candidate memories:
{numbered list of memories with IDs}

Rank the 10 most relevant memories for this session.
Return only the IDs in order of relevance.
```

### Trade-offs

| Advantage | Disadvantage |
|-----------|-------------|
| Perfect semantic understanding | ~$0.01-0.05 per session start (Sonnet) |
| No embedding infrastructure needed | Adds 2-5 seconds to session startup |
| Handles nuance keyword search cannot | Scales poorly past ~500 memories |
| Works immediately, no migration | Non-deterministic (different rankings each time) |
| Can explain *why* it chose each memory | Cannot be used offline |

### When This Makes Sense

- **Small corpus** (<200 memories): LLM ranking is fast, cheap, and maximally intelligent
- **Transitional period**: While building the full retrieval pipeline, LLM ranking works immediately
- **Validation**: Use LLM ranking as ground truth to tune the scoring function weights

### When This Breaks Down

- **Large corpus** (>500 memories): Pre-filtering becomes necessary, defeating the purpose
- **Latency-sensitive**: 2-5 seconds at startup may be unacceptable
- **Cost at scale**: 10 sessions/day x $0.03 = ~$9/month just for injection ranking
- **Offline**: Requires API access

### Recommendation

Use LLM ranking as a **calibration tool**, not as the primary retrieval mechanism. Run it in parallel with the scoring function and measure agreement. When agreement exceeds 85%, the scoring function is well-tuned and LLM ranking can be retired.

---

## Appendix B: Research Sources

### Embedding Models & Providers
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) — text-embedding-3 family, Matryoshka dimension reduction
- [OpenAI API Pricing](https://platform.openai.com/docs/pricing) — embedding model pricing and batch discounts
- [New Embedding Models and API Updates (Jan 2024)](https://openai.com/index/new-embedding-models-and-api-updates/) — text-embedding-3-small/large announcement
- [Embeddings — Claude Docs](https://docs.claude.com/en/docs/build-with-claude/embeddings)
- [13 Best Embedding Models 2026](https://elephas.app/blog/best-embedding-models)

### sqlite-vec
- [sqlite-vec GitHub](https://github.com/asg017/sqlite-vec)
- [sqlite-vec v0.1.0 Release](https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html)
- [sqlite-vec API Reference](https://alexgarcia.xyz/sqlite-vec/api-reference.html)
- [Binary Quantization Guide](https://alexgarcia.xyz/sqlite-vec/guides/binary-quant.html)
- [Comparison to Other Approaches](https://github.com/asg017/sqlite-vec/issues/94)

### Lightweight Local Embeddings
- [Model2Vec GitHub](https://github.com/MinishLab/model2vec) — 8-30MB, numpy-only, 500x faster
- [FastEmbed by Qdrant](https://github.com/qdrant/fastembed) — ONNX runtime, no PyTorch
- [EmbeddingGemma-300M](https://huggingface.co/google/embeddinggemma-300m) — <200MB quantized
- [EmbeddingGemma ONNX](https://huggingface.co/onnx-community/embeddinggemma-300m-ONNX)

### Agent Memory Architectures
- [MAGMA: Multi-Graph Agentic Memory](https://arxiv.org/abs/2601.03236) — Jan 2026
- [Graphiti: Temporal Knowledge Graphs](https://github.com/getzep/graphiti)
- [Zep: Temporal KG Architecture for Agent Memory](https://arxiv.org/abs/2501.13956)
- [LightRAG: Dual-Level Retrieval](https://lightrag.github.io/)
- [HybridRAG: KG + Vector Retrieval](https://arxiv.org/abs/2408.04948)
- [Graph Memory for AI Agents (Jan 2026)](https://mem0.ai/blog/graph-memory-solutions-ai-agents)
- [FalkorDBLite: Embedded Graph DB](https://www.falkordb.com/blog/falkordblite-embedded-python-graph-database/)

### Retrieval Patterns
- [Hybrid RAG in the Real World](https://community.netapp.com/t5/Tech-ONTAP-Blogs/Hybrid-RAG-in-the-Real-World-Graphs-BM25-and-the-End-of-Black-Box-Retrieval/ba-p/464834)
- [Incremental Updates in RAG Systems](https://dasroot.net/posts/2026/01/incremental-updates-rag-dynamic-documents/)
- [GraphRAG Complete Guide 2026](https://www.meilisearch.com/blog/graph-rag)
- [Efficient Maintenance of Leiden Communities](https://arxiv.org/abs/2601.08554) — Jan 2026

### CLI Agent Memory Patterns
- [Letta Code: Memory-First Coding Agent](https://www.letta.com/blog/letta-code)
- [Deep Agent CLI: Persistent Memory](https://www.flowhunt.io/blog/deep-agent-cli-intelligent-coding-assistants-persistent-memory/)
- [CLAUDE.md as Agent Memory](https://evoleinik.com/posts/claude-md-as-agent-memory/)
- [Agent Design Patterns 2026](https://rlancemartin.github.io/2026/01/09/agent_design/)

### Bi-Temporal Data Modeling
- [Martin Fowler — Bitemporal History](https://martinfowler.com/articles/bitemporal-history.html) — canonical walkthrough of valid time vs record time
- [XTDB — Bitemporality](https://v1-docs.xtdb.com/concepts/bitemporality/) — bitemporality as a first-class database primitive
- [Bi-Temporal Event Sourcing Experience Report](https://www.planetgeek.ch/2023/12/04/our-experience-with-bi-temporal-event-sourcing/) — combining event sourcing with bi-temporal timestamps in production
- [Bi-Temporal Data Modeling Overview](https://contact-rajeshvinayagam.medium.com/bi-temporal-data-modeling-an-overview-cbba335d1947) — "as at" vs "as of" query patterns
- [SQL:2011 Temporal Features](https://en.wikipedia.org/wiki/Temporal_database) — standard language constructs for temporal queries
- [Graphiti Bi-Temporal Architecture](https://github.com/getzep/graphiti) — valid_at vs recorded_at in temporal knowledge graphs

### Event Sourcing & CQRS
- [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) — foundational pattern definition
- [Martin Fowler — Retroactive Event](https://martinfowler.com/eaaDev/RetroactiveEvent.html) — handling corrections after the fact
- [Datomic — Stuff Happens: Fixing Bad Data](https://blog.datomic.com/2014/08/stuff-happens-fixing-bad-data-in-datomic.html) — immutable retraction model
- [Pat Helland — Immutability Changes Everything](https://www.cidrdb.org/cidr2015/Papers/CIDR15_Paper16.pdf) — append-only data architecture
- [Event-Driven.io — Projections and Read Models](https://event-driven.io/en/projections_and_read_models_in_event_driven_architecture/) — materializing current state from event streams
- [CodeOpinion — Projections in Event Sourcing](https://codeopinion.com/projections-in-event-sourcing-build-any-model-you-want/) — building any view from events
- [Confluent — Event-Driven vs State-Based](https://developer.confluent.io/courses/event-sourcing/event-driven-vs-state-based/) — architectural comparison
- [Event Sourcing with Bitemporal Data (DDD/CQRS)](https://groups.google.com/g/dddcqrs/c/3gPU6rSZf8M) — community discussion on combining the two patterns

### Distributed Systems & Temporal Reconciliation
- [Pat Helland — Data on the Outside vs Data on the Inside](https://queue.acm.org/detail.cfm?id=3415014) — independent temporal domains and immutable external facts
- [Pat Helland — Data on the Outside (CIDR 2005 Original)](https://www.cidrdb.org/cidr2005/papers/P12.pdf) — the foundational paper
- [CRDT.tech — Conflict-Free Replicated Data Types](https://crdt.tech/) — convergence without coordination
- [Vector Clocks — Kevin Sookocheff](https://sookocheff.com/post/time/vector-clocks/) — detecting causality vs concurrency
- [Lamport — Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) — logical time foundations
- [Clocks and Causality — Ordering Events in Distributed Systems](https://www.exhypothesi.com/clocks-and-causality-ordering-events-in-distributed-systems/) — practical vector clock tutorial
- [Stanford SNLI Corpus — Natural Language Inference](https://nlp.stanford.edu/projects/snli/) — 570k labeled entailment/contradiction pairs
- [Identification of Entailment and Contradiction Relations](https://arxiv.org/html/2405.01259v1) — NLI techniques for short text
- [Contradiction Detection in RAG Systems](https://arxiv.org/html/2504.00180v1) — detecting conflicting facts across documents

### Process Mining & Duplicate Detection
- [SAP Signavio — Process Mining](https://www.signavio.com/wiki/process-discovery/process-mining/) — discovering operational patterns from event logs
- [van der Aalst — Process Mining: Data Science in Action](https://link.springer.com/book/10.1007/978-3-662-49851-4) — foundational academic reference
- [SemHash — Semantic Deduplication](https://github.com/MinishLab/semhash) — three-stage dedup pipeline for short text
- [FSRS — Free Spaced Repetition Scheduler](https://github.com/open-spaced-repetition/fsrs4anki) — per-item difficulty and retrievability curves
- [Mem0 — Production AI Agent Memory](https://arxiv.org/pdf/2504.19413) — memory survey covering deduplication, reinforcement, and decay
- [Agentic Memory — Unified Long/Short-Term Memory](https://arxiv.org/html/2601.01885v1) — learning vs retrieval in agent memory systems
