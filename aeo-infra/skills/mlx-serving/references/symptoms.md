# Symptoms

Symptom-driven triage. Each entry: what the user observes, the likely
cause(s), how to confirm, and the fix.

---

## OOM during model load

**What you see**

The server process exits during startup, or `omlx` reports "out of
memory" before the first request. Logs show allocation failures around
weight loading.

**Likely causes**

1. Model file size + working set exceeds available unified memory
2. Other large processes (browser, IDE indexers) holding memory
3. Loading multiple models concurrently into the registry

**Confirm**

```bash
# Memory pressure right now
memory_pressure
vm_stat | head -10

# Model size on disk (approximate working set is 1.2-1.5x this for fp16,
# or close to disk size for already-quantized files)
du -sh ~/.omlx/models/<model-dir>

# Other large RSS users
ps -axo rss=,comm= | sort -nr | head -20
```

**Fix**

- Drop a smaller quant (4-bit instead of 8-bit; 2-bit if available and
  quality holds in bench)
- For oMLX: build an OptiQ proxy variant — uses lower-precision proxy
  weights to drive sensitivity-aware quantization without holding the
  full model
- Free other large processes
- For oMLX: configure the registry to load on demand, not eagerly
- Last resort: model is genuinely too large for this hardware; use a
  smaller model or upgrade RAM

---

## OOM during inference (long context)

**What you see**

Model loads fine, short prompts work, but a longer prompt (8k+ tokens) or
a long generation triggers OOM mid-stream. Output cuts off, server may
crash or stall.

**Likely cause**

KV cache growth. Each generated token adds to the KV cache; for large
contexts on large models, the cache itself can dwarf the model weights.

**Confirm**

- Issue a series of progressively longer prompts; OOM threshold tracks
  context length
- Server log shows allocation failures during generation, not load

**Fix**

- Enable `turboquant_kv` (oMLX): quantizes KV cache entries to fewer bits
  (typically 4-bit). Memory drops sharply with modest quality cost on
  most models.
- Enable spill-to-SSD on oMLX: launch with
  `omlx serve ... --paged-ssd-cache-dir <path>` (and optionally
  `--paged-ssd-cache-max-size`). The CLI flag is the operative control
  on current oMLX versions; per-model `dflash_*` keys in
  `model_settings.json` are version-dependent overrides — treat them as
  supplementary, not primary.
- Raise `--hot-cache-max-size` (oMLX) to keep recent KV state in RAM
  for prefix reuse before falling back to SSD
- Reduce `max_tokens` per request to bound generation length
- Reduce server concurrency — multiple in-flight requests each hold their
  own KV state

---

## Crash or hang at batch > 1

**What you see**

Single requests work fine. Concurrent requests cause crashes, hangs, or
garbled output. May manifest as the server becoming unresponsive after
the second simultaneous request, or producing tokens from one request in
another's stream.

**Likely cause**

Architecture-specific cache implementation built for batch=1 but invoked
at batch>1 by the scheduler. ChunkedKVCache (used by Llama-4 and similar
chunked-attention architectures) is a known instance: the cache shape is
constructed without a batch dimension, so concatenating across the batch
axis silently corrupts state.

**Confirm**

```bash
# Reproduce: send two parallel requests with curl
seq 2 | xargs -P2 -I{} curl -s http://localhost:8000/v1/chat/completions \
  -d '{"model":"<name>","messages":[{"role":"user","content":"hi"}]}'
```

If the same payload works sequentially but breaks in parallel, you have
a batch-shape bug.

**Fix**

- Immediate: launch oMLX with `--max-concurrent-requests 1`. The
  scheduler will queue requests, eliminating the batch>1 path.
- Durable: see [`upstream-bug-patterns.md`](upstream-bug-patterns.md) for
  the cache-shape pattern. The fix lives in the cache constructor, not
  in user config.
- For mlx-lm: this manifests less because mlx-lm's server doesn't batch
  requests internally, but raising the request rate beyond what one MLX
  graph can handle causes its own issues.

---

## Tool calls return as plaintext content

**What you see**

You prompt a tool-using model (Llama-3, Llama-4, function-calling Mistral)
with a tools list. The response's `choices[0].message.content` contains
JSON like `{"name": "get_weather", "parameters": {"city": "SF"}}` instead
of the structured `tool_calls` array. Client code that expects
`tool_calls` sees an empty list and treats the JSON-in-content as text.

**Likely cause**

The server's tool-call parser doesn't recognize the model's JSON shape.
Different model families emit different formats:

- OpenAI-style: separate `tool_calls` array (rare from open models)
- Llama-3 family: JSON object in content with `name` and `parameters` keys
- Some Mistral variants: `[TOOL_CALLS]` prefix, then JSON
- Llama-4: similar to Llama-3 but with subtle schema differences

If the parser only recognizes one shape, it passes other shapes through
unchanged.

**Confirm**

```bash
# Send a tool-using request
curl -s http://localhost:8000/v1/chat/completions -d '{
  "model": "<name>",
  "messages": [{"role":"user","content":"What is the weather in SF?"}],
  "tools": [{"type":"function","function":{
    "name":"get_weather",
    "parameters":{"type":"object","properties":{"city":{"type":"string"}}}
  }}]
}' | jq '.choices[0].message | {content, tool_calls}'
```

If `tool_calls` is empty/null and `content` looks like a JSON tool
invocation, the parser is missing this format.

**Fix**

- Verify the chat template applied at request time matches the model card
  (some templates include `<|tool_call|>` markers; the parser keys off
  these)
- For oMLX: see [`upstream-bug-patterns.md`](upstream-bug-patterns.md)
  for the parser-extension pattern
- Workaround: post-process responses on the client — if `tool_calls` is
  empty and `content` parses as a JSON object with `name` and `parameters`,
  treat it as a tool call

---

## Throughput regression after config change

**What you see**

You enabled a feature flag expecting a speedup. Tokens-per-second dropped
instead. Or you disabled something to "simplify" and lost throughput.

**Likely causes**

- Feature flags interact (e.g., `mtp_enabled` requires the model to
  support multi-token prediction; if it doesn't, you pay overhead with
  no win)
- `dflash` adds bookkeeping overhead that only pays off on long contexts;
  short prompts get slower
- `turboquant_kv` at very low bits adds dequant cost on every read

**Confirm**

Run a focused throughput bench before and after the change. Use the same
prompt length and generation budget for both runs; thermal state of the
M-series chip affects throughput, so allow a cooldown between runs.

```bash
# Simple throughput probe
time curl -s http://localhost:8000/v1/chat/completions -d '{
  "model":"<name>","max_tokens":256,
  "messages":[{"role":"user","content":"Write 256 tokens about apples."}]
}' | jq -r '.usage.completion_tokens'
```

**Fix**

- Bisect: revert the change, confirm baseline returns; re-apply one flag
  at a time
- Consult [`omlx-feature-flags.md`](omlx-feature-flags.md) for known
  interactions
- If a flag is documented as a speedup but isn't on this model, the model
  may lack a required capability (e.g., MTP heads). Disable and move on.

---

## Server log triage

**Where to look**

- oMLX: `~/.omlx/logs/server.log` (rotates daily). Tail it during
  reproduction.
- mlx-lm: process stderr — capture explicitly (`mlx_lm.server ... 2>log`)
- macOS unified log: `log show --predicate 'process == "omlx"' --last 5m`
  catches crashes that don't make it to the application log

**What to grep for**

```bash
# Errors and warnings
grep -E "ERROR|WARN|Traceback" ~/.omlx/logs/server.log | tail -30

# Memory-related
grep -iE "oom|memory|allocation" ~/.omlx/logs/server.log | tail -20

# Per-request timing
grep -E "completion|generation" ~/.omlx/logs/server.log | tail -50
```

**Reading patterns**

- Tracebacks ending in `mlx.core` or `mlx_lm` errors → MLX-level issue
  (often a cache or shape problem)
- Repeated "model not loaded" → registry / lifecycle issue, not a serving
  problem
- Slow first request, fast subsequent → cold prefix cache (enable
  `specprefill` or warm with a dummy request)
- Identical request times across very different prompt lengths →
  generation is fixed-cost-bound, not compute-bound; check disk I/O
