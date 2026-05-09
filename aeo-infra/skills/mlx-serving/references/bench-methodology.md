# Bench Methodology

Tuning MLX serving without a bench is guessing. The hardware is fast
enough that intuitions about throughput are usually wrong — thermal
state, cache temperature, KV pressure, and feature-flag interactions
all create non-obvious effects.

This is a methodology, not a tool spec. The harness is small enough to
write in an afternoon; what matters is the discipline.

---

## Suite shape

A useful bench has at least these cells per model:

| Cell | What it measures | Pass criteria |
|---|---|---|
| `chat` | Coherent multi-turn conversation | Output is on-topic, no repetition loops, completes within token budget |
| `coding` | Generation of working code | Code parses; for languages with simple checks, runs and produces expected output |
| `tool_call` | Structured tool invocation | Response includes a populated `tool_calls` field with valid JSON arguments |
| `tok/s` | Steady-state throughput | Tokens-per-second over a fixed-length generation; report median across N runs |

Optional cells worth adding once basic four pass:

| Cell | Measures |
|---|---|
| `long_context` | Performance and correctness at 16k+ token prompts |
| `concurrency` | Throughput and correctness under N parallel requests |
| `memory_peak` | Max RSS observed during a long-generation run |
| `quality` | Output similarity to a reference set (BLEU/ROUGE or model-as-judge) |

A model that passes all four core cells is "fleet-ready"; one that fails
any cell needs config attention before being added to the production
roster.

---

## Backend-agnostic harness shape

The harness should not care whether it's hitting `mlx_lm.server` or
`omlx serve`. Both expose OpenAI-compatible `/v1/chat/completions` and
`/v1/completions` endpoints.

Minimum harness contract:

```
bench --base-url http://localhost:<port> \
      --model <name> \
      --suite chat,coding,tool_call,tokps \
      --runs 3 \
      --output results.json
```

Output schema:

```json
{
  "model": "<name>",
  "backend_url": "http://localhost:8000",
  "ts": "<iso8601>",
  "config_hash": "<sha256 of relevant config>",
  "cells": {
    "chat": {"pass": true, "elapsed_s": 4.2},
    "coding": {"pass": true, "elapsed_s": 8.1},
    "tool_call": {"pass": false, "reason": "tool_calls empty; content has JSON"},
    "tokps": {"median": 39.6, "p25": 38.1, "p75": 41.0}
  }
}
```

Including a `config_hash` (a stable hash of `model_settings.json` for
this model + relevant server flags) lets you correlate bench results
with config changes after the fact.

---

## Change attribution

When a bench result changes, you need to know what changed. Two rules:

1. **One config change per bench run.** If you change two flags between
   bench runs and a regression appears, you've lost attribution. Either
   accept ambiguity or revert and bisect.

2. **Same physical conditions.** Bench results vary 5-15% based on
   thermal state of the chip, background processes, and recent disk
   activity. Run consecutive benches with no other heavy work, allow a
   minute of cooldown between runs, and report median across N.

---

## Bench-driven release gate

Adopting a "model can serve in production iff bench passes all core
cells at chosen config" gate prevents the slow-creep failure mode where
a half-broken config becomes the daily driver because nobody re-tests
after the original tuning session.

A practical gate:

- Run bench after every model addition
- Run bench after every config change
- Run bench after every oMLX/mlx-lm version bump
- Archive results with the config hash; track regressions over time

---

## Detecting regressions

A simple regression check, given a baseline `results.json`:

```python
def regression_check(baseline, current, tokps_tolerance=0.10):
    fails = []
    for cell, b in baseline["cells"].items():
        c = current["cells"][cell]
        if "pass" in b and b["pass"] and not c["pass"]:
            fails.append(f"{cell}: passed in baseline, fails now")
        if cell == "tokps":
            if c["median"] < b["median"] * (1 - tokps_tolerance):
                fails.append(
                    f"tokps: {c['median']:.1f} < {b['median']:.1f} "
                    f"(>{int(tokps_tolerance*100)}% drop)"
                )
    return fails
```

A 10% throughput tolerance accounts for normal thermal variance; tighten
to 5% only with multiple runs and controlled conditions.

---

## What not to bench

Resist the urge to bench everything:

- **Cold-load time.** It varies wildly with disk cache state and is rarely
  what users care about. If startup matters, measure it once and move on.
- **Single-token latency.** Almost meaningless on M-series — the chip is
  fast enough that microbenchmarks are dominated by HTTP and JSON
  serialization overhead.
- **Synthetic stress at maximum context.** Useful to know the ceiling
  but not representative of typical workload. Bench the workloads you
  actually serve.

---

## Pass/fail vs. score

Some teams prefer numeric scores ("model X scored 87/100"). For LLM
serving config tuning, pass/fail per cell is more actionable: a config
either supports tool calling or it doesn't; either generates working
code or it doesn't. Numeric quality scores are useful for comparing
models, not for tuning a single model's config.
