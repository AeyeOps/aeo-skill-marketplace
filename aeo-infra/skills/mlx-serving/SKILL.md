---
name: mlx-serving
version: 1.0.0
description: >-
  This skill should be used when the user asks about "MLX serving",
  "mlx_lm.server", "oMLX", "Apple Silicon LLM serving", or "local LLM on
  Mac" — and when troubleshooting symptoms like model fails to load, OOM
  during load or inference, server hangs or crashes at batch>1, tool calls
  returning as plaintext content, throughput regression, or choosing between
  mlx-lm and oMLX. Also applies to oMLX feature-flag tuning ("turboquant_kv",
  "dflash", "MTP", "specprefill", "thinking_budget",
  "max-concurrent-requests", "force_sampling"), OptiQ proxy for models
  exceeding RAM, Llama-4 ChunkedKVCache batch handling, Llama-3 tool-call
  JSON format ("name"/"parameters"), and bench-driven validation of serving
  configs. For Apple Silicon (M-series) only — not for cloud LLM hosting
  (Bedrock, OpenAI API, Anthropic API), not for non-MLX backends
  (llama.cpp, Ollama, vLLM), not for model training.
---

# Apple Silicon LLM Serving (MLX / oMLX)

Operational guidance for running and tuning local LLM inference on Apple
Silicon (M-series). Covers two common backends: Apple's `mlx-lm` and the
oMLX server built on top of MLX.

Both expose OpenAI-compatible HTTP APIs, so client code is portable. The
differences are in features, packaging, and the failure modes you hit when
pushing models near the limits of unified memory.

---

## Pre-Flight: Verify Environment

Before debugging any serving issue, confirm the basics:

```bash
# Hardware: confirm Apple Silicon and unified-memory size
system_profiler SPHardwareDataType | grep -E "Model|Chip|Memory"

# Activate the venv where mlx-lm is installed before the next two probes,
# otherwise they hit system Python and may report nothing useful.
python -c "import mlx.core as mx; print(mx.__version__, mx.default_device())"
python -c "import mlx_lm; print(mlx_lm.__version__)"

# oMLX (DMG install): inspect available subcommands and run health checks
omlx --help
omlx diagnose menubar   # checks Tahoe ControlCenter visibility (oMLX-specific)

# Confirm a process is actually listening
lsof -nP -iTCP -sTCP:LISTEN | grep -E "omlx|mlx_lm"
```

Verify which backend is bound before debugging: both can serve OpenAI-
compatible endpoints on user-chosen ports, and a client request hitting the
wrong backend silently produces correct-looking but unrelated output.

---

## Backend Decision: mlx-lm vs oMLX

| Concern | mlx-lm | oMLX |
|---|---|---|
| Install | `pip install mlx-lm` | DMG (macOS app bundle) |
| Process model | One model per `mlx_lm.server` process | Built-in registry; multi-model |
| Config surface | Minimal CLI flags | Rich per-model JSON (`model_settings.json`) |
| Feature flags | `--temp`, `--top-p`, basic | turboquant_kv, dflash, MTP, specprefill, thinking budget |
| Tool calling | Format depends on chat template | Per-model parser (configurable) |
| Models > RAM | Not supported (OOM on load) | OptiQ proxy build (sensitivity-driven quant) |
| GUI | None | Native macOS app + menu bar |
| Default port | 8080 | 8000 |
| Best for | Library-first scripts, embedding in Python | Long-running daemon, multiple models, GUI ops |

> **Skill bias:** the depth here leans oMLX — feature flags, cache controls,
> upstream bug patterns. mlx-lm coverage is lighter and focuses on the
> shared substrate.

Pick **mlx-lm** when: you control the Python process, you want minimal
surface area, you serve one model at a time, and the model fits comfortably
in RAM.

Pick **oMLX** when: you need a daemon that survives terminal sessions, you
serve multiple models behind one endpoint, you want feature flags
(turboquant, dflash, MTP) without writing them yourself, or your model
exceeds RAM and you need OptiQ proxy.

Both backends share the same fundamental constraints (unified memory,
KV cache pressure, model architecture quirks), so most troubleshooting in
this skill applies to either.

---

## Symptom → Cause Triage

| Symptom | Likely cause | First move |
|---|---|---|
| OOM during model load | Model + KV scratch > available RAM | Smaller quant; OptiQ proxy (oMLX); free other apps |
| OOM during long-context inference | KV cache growth | Enable `turboquant_kv`; set `--paged-ssd-cache-dir` for spill-to-SSD (CLI flag is the operative control; `dflash_*` keys are version-dependent overrides) |
| Crash / hang at batch > 1 | Architecture cache shape mismatch | Pin `--max-concurrent-requests 1` (oMLX); see upstream-bug-patterns |
| Tool calls return as plaintext content | Parser doesn't recognize the model's tool-call JSON shape | See upstream-bug-patterns; check `tool_calls` field in response |
| Throughput regression after config change | Feature flag interaction | Bisect via bench, one flag at a time |
| Server hangs on startup | Large checkpoint loading from cold disk | Wait; tail `server.log`; check disk I/O via `iostat` |
| Wrong / garbled outputs | Quantization too aggressive, or wrong chat template | Reduce `turboquant_kv_bits` or disable; verify chat template matches model card |
| First request slow, rest fast | Cold prefix cache | Enable `specprefill`; warm cache with a dummy request |
| Output cut off mid-sentence | `max_tokens` too low; thinking budget exhausted | Raise `max_tokens`; check `thinking_budget_enabled` |

For deeper triage on each symptom: `references/symptoms.md`.

---

## Core Principles

1. **Lower `--max-concurrent-requests` to 1 for batch-fragile architectures.**
   oMLX defaults to `--max-concurrent-requests 8`. Higher concurrency
   exposes architecture-specific batch handling bugs (notably in cache
   implementations like ChunkedKVCache used by Llama-4). For affected
   architectures, pin concurrency to 1 at launch and bench upward only
   after confirming clean output at batch>1.

2. **One flag at a time.** Feature flags interact (e.g., `dflash` +
   `turboquant_kv` both touch the KV cache path). Changing two flags
   simultaneously and observing a regression makes attribution impossible.
   Bench between each change.

3. **Bench, don't guess.** "It feels faster" is not a tuning signal.
   Maintain a small bench suite (chat / coding / tool-calling correctness +
   throughput) and re-run it after every config change. See
   `references/bench-methodology.md`.

4. **Match chat templates to model cards.** Tool-calling and reasoning
   behavior depend on the chat template applied at request time. The
   model's HuggingFace card is authoritative.

5. **Quantization is a curve, not a switch.** `turboquant_kv_bits=4.0`
   keeps most quality; lower bits trade quality for memory. Always include
   a quality cell in the bench suite — a config that passes throughput
   but fails coding can be worse than slower-but-correct.

6. **OptiQ proxy is for the "model > RAM" case only.** It builds a
   sensitivity-driven proxy of the model so per-layer quant decisions can
   be made without holding the full model in memory. It's not a general
   speedup; for in-RAM models it adds startup cost without runtime benefit.

7. **Server-side bugs masquerade as config problems.** When a symptom
   reproduces across multiple config combinations, suspect upstream rather
   than chasing more flags. See `references/upstream-bug-patterns.md`.

---

## References

- [`references/symptoms.md`](references/symptoms.md) — symptom triage with
  diagnostics and fixes (OOM, batch>1 crashes, tool-call-as-text,
  throughput regression, log triage)
- [`references/omlx-feature-flags.md`](references/omlx-feature-flags.md) —
  per-flag reference (turboquant_kv, dflash, MTP, specprefill, thinking
  budget, max-concurrent-requests, force_sampling) with interactions
- [`references/bench-methodology.md`](references/bench-methodology.md) —
  bench-it-don't-guess: suite design, backend-agnostic harness shape,
  scoring, change attribution
- [`references/upstream-bug-patterns.md`](references/upstream-bug-patterns.md)
  — when to suspect upstream vs config; two recurring bug patterns
  (cache-shape mismatch under batched scheduling; model tool-call format
  not parsed) with diagnostics and reporting guidance

---

## What This Skill Does Not Cover

- Cloud LLM hosting (Bedrock, OpenAI API, Anthropic API) — different
  surface entirely
- Non-MLX local backends (llama.cpp, Ollama, vLLM) — overlapping problem
  space but different tooling
- Model training, fine-tuning, or LoRA — see MLX training tutorials
- General Python / HTTP debugging unrelated to MLX
- Model card creation or HuggingFace upload workflows
