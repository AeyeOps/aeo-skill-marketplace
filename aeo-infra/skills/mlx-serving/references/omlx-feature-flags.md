# oMLX Feature Flags

Two surfaces:

1. **Server-level flags** passed to `omlx serve`. Authoritative source:
   `omlx serve --help` for your installed version.
2. **Per-model `model_settings.json` keys** stored under `~/.omlx/`. Schema
   is observed in field installs and may shift between oMLX versions —
   verify against your version before relying on a specific key.

Each flag below: what it does, when to enable, when to leave off, and
known interactions.

`model_settings.json` shape (observed; verify against your install):

```json
{
  "version": 1,
  "models": {
    "<model-name>": {
      "force_sampling": false,
      "enable_thinking": false,
      "thinking_budget_enabled": false,
      "turboquant_kv_enabled": false,
      "turboquant_kv_bits": 4.0,
      "turboquant_skip_last": true,
      "specprefill_enabled": false,
      "dflash_enabled": false,
      "dflash_in_memory_cache": true,
      "dflash_in_memory_cache_max_bytes": 8589934592,
      "dflash_ssd_cache": false,
      "mtp_enabled": false
    }
  }
}
```

---

## Server-level flags (`omlx serve`)

### `--max-concurrent-requests N`

Caps the number of in-flight requests the scheduler will accept
simultaneously. Excess requests queue.

**Default: `8`.** This works on architectures whose cache implementations
handle batch>1 cleanly.

**Lower to `1`** for architecture-specific cache implementations that
assume batch=1 (ChunkedKVCache for Llama-4 family, others for chunked-
attention architectures). Concurrency >1 against these exposes cross-
request corruption, crashes, or hangs.

**When to raise back up:** only after benching the specific model at
batch=2, batch=4 and confirming clean output. Do this per model — a
setting that works for one architecture may fail for another.

**Trade-off:** at concurrency=1, multiple clients see latency stack up.
Suitable for a small number of clients or single-user developer setups.
For multi-tenant serving, fix the underlying batch handling first.

---

### `--port`, `--host`

Default: `--host 127.0.0.1 --port 8000`. Bind to `0.0.0.0` for LAN
access; bind to a non-default port to coexist with mlx-lm (default 8080)
on the same machine.

---

### `--model-dir`

Default: `~/.omlx/models`. Each subdirectory containing `config.json` and
`*.safetensors` becomes a discoverable model. Move or symlink models
into here rather than passing absolute paths per request.

---

### `--max-model-memory`, `--max-process-memory`

`--max-model-memory` defaults to 80% of system RAM — caps total memory
across loaded models for LRU-driven eviction. Lower this if other
processes need headroom.

`--max-process-memory` defaults to `auto` (RAM minus 8 GB) — hard ceiling
on the entire server process. Pass `disabled` to remove the ceiling
(risky on memory-tight systems).

---

### Cache controls (`--paged-ssd-cache-*`, `--hot-cache-max-size`, `--no-cache`, `--initial-cache-blocks`)

oMLX maintains a paged KV cache that can spill to SSD. These flags
control its sizing and storage:

- `--paged-ssd-cache-dir <path>` — enable SSD-backed cache by setting a
  directory. Required to actually use the SSD path; without it, only the
  in-memory hot cache applies.
- `--paged-ssd-cache-max-size <e.g. 100GB>` — cap on SSD cache size.
  Default 100GB.
- `--hot-cache-max-size <e.g. 8GB>` — in-memory hot cache size.
  Default `0` (disabled). Raise to keep recent KV state in RAM for prefix
  reuse.
- `--initial-cache-blocks N` — pre-allocate N cache blocks at startup.
  Default 256. Raise for large-context workloads to reduce dynamic
  allocation overhead.
- `--no-cache` — disable oMLX's paged cache entirely; mlx-lm
  BatchGenerator still manages KV state internally per request.

The relationship between these CLI flags and the per-model `dflash_*`
keys (below) varies by oMLX version — when in doubt, prefer the CLI
flags as the canonical control surface and treat `dflash_*` keys as
overrides where supported.

---

## KV cache: `turboquant_kv_*`

Quantizes the KV cache to fewer bits, reducing memory at modest quality
cost. The single highest-leverage flag for long-context serving.

### `turboquant_kv_enabled` (bool)

Master switch. Defaults off.

### `turboquant_kv_bits` (float)

Bit-width target. Common values: `4.0` (mild, near-lossless on most
models), `2.0` (aggressive, quality-sensitive). Lower bits = more memory
saved, more dequant overhead per token.

**Pick `4.0` first.** Bench. Drop to `2.0` only if memory is still tight
and the bench's quality cells still pass.

### `turboquant_skip_last` (bool)

When true, leaves the final transformer block's KV cache un-quantized.
The last block has outsized impact on output quality, so keeping it full-
precision is a small memory cost for noticeable quality preservation.

**Recommended:** `true` whenever `turboquant_kv_enabled` is true.

### Interactions

- `turboquant_kv` + `dflash`: both touch KV cache pathways. Enable one,
  bench, then add the other and bench again. Do not enable both
  simultaneously on first try.
- `turboquant_kv` + `mtp`: MTP generates speculative tokens against a
  shared KV state. Aggressive quantization can hurt MTP acceptance rates.

---

## Disk-flash KV: `dflash_*`

Persists prefix KV cache to memory and optionally SSD, enabling reuse
across requests sharing a prefix and spill-to-SSD when memory is tight.

### `dflash_enabled` (bool)

Master switch.

### `dflash_in_memory_cache` (bool) + `dflash_in_memory_cache_max_bytes` (int)

When true, holds recently used prefix caches in RAM up to the byte limit.
Default `8589934592` (8 GiB). Tune relative to total unified memory and
expected prefix reuse — a 36 GiB Mac running a 20 GiB model has limited
headroom for an 8 GiB cache.

### `dflash_ssd_cache` (bool)

When true, spills cache entries beyond the in-memory limit to disk.
Slower retrieval but prevents OOM and preserves cache continuity across
restarts.

**When to enable:** workloads with strong prefix reuse (system prompts,
long fixed contexts, RAG with repeated documents). Idle benefit is small
for one-off prompts.

**When to leave off:** short, varied prompts. The bookkeeping overhead
slightly slows the no-cache-hit path.

### Interactions

- `dflash` + `turboquant_kv`: see above
- `dflash` + `specprefill`: complementary — `specprefill` accelerates
  cache miss path, `dflash` accelerates cache hit path

---

## Multi-token prediction: `mtp_enabled`

Predicts and verifies multiple tokens per forward pass when the model has
MTP heads. On supported models, increases throughput substantially.

**Requires model support.** Not every checkpoint ships MTP heads. If the
model doesn't have them, enabling MTP costs overhead with no benefit.
Check the model card; if uncertain, bench with the flag on and off and
observe whether throughput actually improves.

**Bench requirement:** measure with and without on representative
workload. MTP acceptance rates vary by prompt — high acceptance on
predictable text, low acceptance on creative or domain-specific output.

---

## Speculative prefill: `specprefill_enabled`

Overlaps prompt processing with generation startup. Reduces time-to-first-
token, especially on long prompts.

**When to enable:** interactive workloads (chat, REPL) where time-to-
first-token dominates user perception.

**When to leave off:** batch / offline jobs where total throughput
matters and TTFT is irrelevant.

**Interaction:** with `dflash` enabled and a cache hit, prefill is
already cheap; specprefill's marginal benefit shrinks.

---

## Thinking mode: `enable_thinking` + `thinking_budget_enabled`

For models that support extended-reasoning ("thinking") modes (some
recent Llama, Gemma, Mistral, and reasoning-tuned variants).

### `enable_thinking` (bool)

Activates the model's thinking pathway when the chat template supports
it. The model produces internal reasoning tokens before its visible
answer.

### `thinking_budget_enabled` (bool)

Caps the number of reasoning tokens. Without a budget, models can run
on for thousands of tokens of internal monologue, blowing latency
budgets.

**Pair them:** if `enable_thinking` is true, `thinking_budget_enabled`
should generally also be true with a sensible per-request budget.

**When to disable:** the model doesn't support thinking mode; the use
case demands minimum latency; the chat template at request time will
override the flag anyway.

---

## Sampling: `force_sampling`

Forces non-greedy sampling regardless of `temperature=0` requests from
clients.

**Default off.** Enable only when you specifically want sampling
diversity for evaluation runs or when a client incorrectly hardcodes
`temperature=0` for use cases that benefit from variation.

---

## OptiQ proxy (model build)

Not a runtime flag — a model-build mode. When a model exceeds available
memory, OptiQ builds a sensitivity-aware quantized variant by using
lower-precision proxy weights to measure per-layer importance, then
applies aggressive quantization to insensitive layers and gentler
quantization to sensitive ones.

**When to use:** model + scratch > unified memory.

**When NOT to use:** the model fits in RAM. Build cost is real (often
30+ minutes); for in-RAM models the runtime is identical to a
conventionally-quantized variant.

**Storage location:** OptiQ-built models live alongside the source under
`~/.omlx/models/`. The proxy build itself takes meaningful disk space
during construction; ensure free space before invoking.

---

## Quick-start matrix

For a new model on a memory-comfortable machine, start here:

| Flag | Value | Reason |
|---|---|---|
| `--max-concurrent-requests` | `1` for batch-fragile arches; otherwise leave default `8` | Lower for ChunkedKVCache-using models (Llama-4); raise back after benching cleanly at higher batch |
| `turboquant_kv_enabled` | `false` | Add only if memory pressure observed |
| `dflash_enabled` | `false` | Add only if prefix reuse pattern observed |
| `mtp_enabled` | `false` | Enable only if model has MTP heads |
| `specprefill_enabled` | `false` | Enable only if TTFT matters |
| `enable_thinking` | per model | Match model's intended use |
| `force_sampling` | `false` | Leave default |

For a memory-constrained machine (model + working set near or above
unified memory):

| Flag | Value | Reason |
|---|---|---|
| `turboquant_kv_enabled` | `true` | Cuts KV memory significantly |
| `turboquant_kv_bits` | `4.0` | Start mild; bench |
| `turboquant_skip_last` | `true` | Quality preservation, low cost |
| `dflash_enabled` | `true` | Spill to SSD if RAM exhausted |
| `dflash_ssd_cache` | `true` | Same |

Then bench. Adjust one knob at a time.
