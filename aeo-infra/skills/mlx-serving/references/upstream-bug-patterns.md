# Upstream Bug Patterns

When config tuning isn't enough — recurring patterns that indicate a
server-side bug rather than a configuration problem.

The principle: if a symptom reproduces across multiple unrelated config
combinations, suspect upstream. Chasing more flags wastes time when the
fix lives in the server's source.

---

## Pattern A: Architecture-specific cache shape mismatch under batched scheduling

**Shape**

A KV cache implementation tied to a specific model architecture
(e.g., `ChunkedKVCache` for chunked-attention architectures like the
Llama-4 family) is constructed with shape assumptions that hold only at
batch=1. When the server's scheduler invokes the model at batch>1
(coalescing concurrent requests, or running speculative decoding with a
batched draft path), the cache concatenation along the batch axis silently
corrupts state or raises a shape error.

**Recognize it by**

- Single requests work correctly
- Concurrent requests crash, hang, or produce cross-request corruption
- Issue is reproducible against the specific model architecture; other
  architectures on the same server work fine at batch>1
- Server log shows shape-related errors in MLX layers, or cache-related
  tracebacks
- Pinning `--max-concurrent-requests 1` makes the symptom disappear
  entirely

**Confirm**

```bash
# Sequential (should work)
for i in 1 2 3; do
  curl -s http://localhost:8000/v1/chat/completions \
    -d '{"model":"<arch-X>","messages":[{"role":"user","content":"hi"}]}'
done

# Parallel (reproduces if affected)
seq 3 | xargs -P3 -I{} curl -s http://localhost:8000/v1/chat/completions \
  -d '{"model":"<arch-X>","messages":[{"role":"user","content":"hi"}]}'
```

**Workaround (operator)**

Pin `--max-concurrent-requests 1` at server launch. Document the
constraint visibly so the next operator doesn't raise concurrency
without re-testing.

**Durable fix (server source)**

The cache constructor needs to accept a batch dimension or detect
batch>1 and construct per-sample cache state rather than sharing a single
buffer. The change is typically:

1. Add a `batch_size` parameter (or detect from the input shape) to the
   cache `__init__`
2. Allocate cache buffers with leading batch dimension
3. Index by batch position in the read/write paths
4. Add a batch>1 regression test for the affected architecture

When proposing this as a PR, include:

- Repro steps (sequential works, parallel fails)
- The specific architecture(s) affected
- A minimal test demonstrating the fix
- Note that `--max-concurrent-requests 1` is the operator workaround
  until merged

---

## Pattern B: Model tool-call format not parsed by server

**Shape**

A model emits tool calls in a JSON shape the server's parser doesn't
recognize. The structured `tool_calls` field in the response stays
empty/null while `content` contains the raw JSON of the call.

Common formats by model family:

| Family | Format in content |
|---|---|
| Llama-3 | `{"name": "<fn>", "parameters": {...}}` (often as the entire content) |
| Llama-4 | Similar to Llama-3 with subtle key differences and chat-template markers |
| Some Mistral variants | `[TOOL_CALLS]` prefix followed by JSON array |
| OpenAI-tuned | Usually emitted directly into `tool_calls` by the chat template |

A parser that recognizes only one shape (or only the chat template's
explicit markers) misses content emitted by other model families.

**Recognize it by**

- `tool_calls` is empty/null in responses
- `content` contains a JSON object with `name` and `parameters` (or the
  family's variant) keys
- The same prompt works against a different server (e.g., the model's
  HuggingFace inference endpoint produces a populated `tool_calls`)
- Issue is consistent across config changes — no flag toggle fixes it

**Confirm**

```bash
curl -s http://localhost:8000/v1/chat/completions -d '{
  "model": "<model>",
  "messages": [{"role":"user","content":"What is 2+2? Use the calc tool."}],
  "tools": [{"type":"function","function":{
    "name":"calc",
    "parameters":{"type":"object","properties":{"expr":{"type":"string"}}}
  }}]
}' | jq '.choices[0].message | {content, tool_calls}'
```

If `tool_calls` is null and `content` is JSON-shaped, the parser is
missing this format.

**Workaround (client)**

Post-process responses: when `tool_calls` is empty, attempt to parse
`content` as JSON. If it parses to an object with a `name` key (and
`parameters` or `arguments`), synthesize a `tool_calls` entry from it.
Document this in the client's serving adapter so it's removed once the
server gains native support.

**Durable fix (server source)**

The fix lives in the tool-call parser. Typical shape:

1. Identify where the server parses model output for tool calls (often
   `api/tool_calling.py` or similar)
2. Add a format detector that checks for the unrecognized shape (e.g.,
   "content parses as JSON object with `name` and `parameters` keys")
3. Convert the detected format into the server's internal tool-call
   representation
4. Add a unit test with a fixture covering each new format

When proposing this as a PR:

- Include a fixture of the actual model output for the new format
- Confirm existing format detectors are not broken (regression-test the
  formats already supported)
- Note which model families the new detector helps

---

## When NOT to suspect upstream

Several patterns look like upstream bugs but are usually config or
environment:

- **First request slow, rest fast** — cold prefix cache. Enable
  `specprefill` or warm the cache; this is expected behavior, not a bug.
- **Garbled output across all configs** — usually wrong chat template
  or wrong model variant, not a server bug. Verify the chat template
  matches the model card.
- **Memory grows unbounded** — usually KV cache without `turboquant_kv`
  or `dflash`, not a leak. Bound it with config before chasing leaks.
- **Wildly variable throughput** — usually thermal throttling on
  M-series under sustained load. Check `pmset -g thermlog` and let the
  chip cool.

---

## Reporting upstream

Good upstream bug reports for MLX-related servers share a shape:

1. **Environment block:** OS version, chip (M1/M2/M3/M4 variant), unified
   memory size, server version, model name and source (HuggingFace repo
   or local conversion path)
2. **Minimal repro:** the smallest curl/Python that triggers the issue;
   include the request payload verbatim
3. **Expected vs. actual:** what the response should look like, what it
   actually contains
4. **Scope:** which models/architectures are affected; which configs
   reproduce; which workarounds eliminate the symptom (this last one
   helps maintainers triage to subsystem)
5. **Patch sketch (optional but appreciated):** if the fix is small,
   include a code suggestion or a PR

Avoid: full server logs without grep filtering; complaints framed in
operational terms ("it's slow", "doesn't work") without the structured
data above.
