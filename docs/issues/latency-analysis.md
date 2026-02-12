# Latency Gap Analysis: stop_hook_summary → turn_duration

**Date**: 2026-02-12
**Session IDs analyzed**: 9e53f3d5, 2a75c748, d65beede (marketplace), 6e184e8d, 27092acc, 4b96fcf7, 19890723 (sbd), aa418830 (stuffbydemi-web)
**Data sources**: hook-profile.log, nous.log, session JSONL transcripts

## Executive Summary

A consistent **5-7 second latency gap** exists between `stop_hook_summary` and `turn_duration` entries in Claude Code session transcripts. This gap is **internal to Claude Code** and is NOT caused by hooks or plugins. All Stop hooks execute in under 50ms total. The gap occurs in a dead zone with zero transcript entries, across all projects, and does not correlate with turn duration or hook count.

## Raw Timeline Data

### Session 9e53f3d5 (aeo-skill-marketplace) — 10 turn-ending pairs

| stop_hook_summary (UTC) | turn_duration (UTC) | GAP (s) | turnMs |
|---|---|---|---|
| 21:55:44.421 | 21:55:50.212 | **5.791** | 63,309 |
| 21:58:06.931 | 21:58:12.556 | **5.625** | 83,941 |
| 22:00:53.338 | 22:01:00.143 | **6.805** | 37,110 |
| 22:02:53.815 | 22:02:59.145 | **5.330** | 84,217 |
| 22:05:07.685 | 22:05:13.064 | **5.379** | 42,234 |
| 22:10:00.850 | 22:10:06.985 | **6.135** | 85,125 |
| 22:10:40.339 | 22:10:46.010 | **5.671** | 37,844 |
| 22:12:23.537 | 22:12:29.025 | **5.488** | 69,666 |
| 22:18:31.031 | 22:18:36.455 | **5.424** | 326,379 |
| 22:34:08.938 | 22:34:14.617 | **5.679** | 106,512 |

**Mean: 5.73s | Min: 5.33s | Max: 6.81s**

### Session 2a75c748 (aeo-skill-marketplace) — 2 pairs

| stop_hook_summary | turn_duration | GAP (s) | turnMs |
|---|---|---|---|
| 22:18:36.652 | 22:18:43.503 | **6.851** | 107,106 |
| 22:39:36.595 | 22:39:42.018 | **5.423** | 47,869 |

### Session d65beede (aeo-skill-marketplace) — 1 pair

| stop_hook_summary | turn_duration | GAP (s) | turnMs |
|---|---|---|---|
| 22:59:16.134 | 22:59:21.348 | **5.214** | 39,209 |

### Cross-project sessions (sbd) — 4 pairs

| Session | GAP (s) | hookCount | hasOutput |
|---|---|---|---|
| 6e184e8d | **5.35** | 4 | True |
| 27092acc | **5.28** | 4 | True |
| 4b96fcf7 | **7.77** | 4 | True |
| 19890723 | **9.29** | 4 | True |

### Session aa418830 (stuffbydemi-web) — 1 pair

| stop_hook_summary | turn_duration | GAP (s) | turnMs |
|---|---|---|---|
| 01:23:28.076 | 01:23:32.688 | **4.61** | 63,842 |

## Hook Execution Timing (Proof Hooks Are Not the Cause)

### hook-profile.log: PROFILE_ENTER → PROFILE_EXIT

Every hook invocation completes in **2-4 milliseconds**:

```
260212011621.357 PROFILE_ENTER event=Stop
260212011621.360 PROFILE_EXIT  event=Stop       ← 3ms
260212011626.536 PROFILE_ENTER event=SubagentStop
260212011626.538 PROFILE_EXIT  event=SubagentStop ← 2ms
260212033927.361 PROFILE_ENTER event=Stop
260212033927.363 PROFILE_EXIT  event=Stop       ← 2ms
```

### nous.log: STOP → END (full nous.py handler)

```
260211235544.3742 STOP ctx=22%
260211235544.3762 END 6ms      ← 6ms including dispatch
260212005916.0917 STOP ctx=16%
260212005916.0936 END 6ms
260212034720.1817 STOP ctx=27%
260212034720.1895 END 28ms     ← worst case: 28ms
```

### Total hook chain (all hooks combined)

From nous.py STOP timestamp to stop_hook_summary timestamp in JSONL: **~50ms** total. This includes Claude Code's overhead for launching hook processes, piping JSON, and collecting results for 2 hooks (loop-hook.sh + nous.py).

## Where the Gap Occurs

```
[Model finishes generating response]
    ↓
[Claude Code fires Stop hooks]
    ↓  ← ~50ms (2 hooks execute and complete)
[Claude Code writes stop_hook_summary to JSONL]
    ↓
    ↓  ← ██████████ 5-7 SECONDS — ZERO transcript entries ██████████
    ↓
[Claude Code writes turn_duration to JSONL]
    ↓
[Turn complete, user sees prompt]
```

**Between stop_hook_summary and turn_duration there are ZERO entries in the transcript.** This was verified by iterating through every line of the JSONL between each pair. The gap is a black box inside Claude Code's turn finalization logic.

## Key Observations

### 1. Gap does NOT correlate with turn duration
- 37s turns and 326s turns show the same 5-7s gap
- Pearson correlation ≈ 0 between turnMs and gap

### 2. Gap does NOT correlate with hook count
- hookCount=2 (marketplace): 5-7s
- hookCount=3 (stuffbydemi): 4.6s
- hookCount=4 (sbd): 5-9s

### 3. Gap is cross-project
- aeo-skill-marketplace: 5.2-6.9s
- sbd: 5.3-9.3s
- stuffbydemi-web: 4.6s

### 4. Occasional spikes to 8-11s
- sbd/19890723: 9.29s
- sbd/4b96fcf7: 7.77s
- marketplace/2a75c748: 6.85s (one instance with intermediate assistant/progress entries at 11.4s which was actually TWO stops within the same turn)

### 5. The stop_hook_summary `hasOutput` field
- All marketplace hooks have `hasOutput: true` (hooks return statusline data)
- One sbd session had `hasOutput: false` but the stop wasn't paired with a turn_duration

### 6. Timezone correlation
- hook-profile.log and nous.log use **local time** (UTC+2)
- Session JSONL transcripts use **UTC**
- Confirmed offset: local 23:55:44 = UTC 21:55:44

## Hypothesis: Claude Code Internal Post-Turn Processing

The 5-7s gap is caused by a **synchronous operation inside Claude Code** that runs after hooks complete but before the turn is marked done. The consistency of the timing (always 5-7s, not variable) points to one of:

### Primary hypothesis: Synchronous network call
- **Usage reporting / telemetry** to Anthropic's API
- **Session sync** to cloud storage
- **Token count validation** against API limits

Evidence: ~5s is consistent with a network round-trip including TLS handshake, server processing, and response on a non-cached endpoint. The variability (5-9s) matches network jitter.

### Secondary hypothesis: JSONL serialization + fsync
- Claude Code may be serializing the full conversation and doing a synchronous `fsync()`
- On WSL2 (Linux 6.6.87.2-microsoft-standard-WSL2), file I/O can have variable latency
- However, the gap doesn't scale with conversation size, making this less likely

### Tertiary hypothesis: Internal await/polling loop
- Claude Code may have a fixed 5s `setTimeout` or polling interval in its turn finalization
- This would explain the consistent floor of ~5s

## Root Cause: IDENTIFIED

**The 5-7s gap is caused by OTEL gRPC exports to a dead `localhost:4317` endpoint.**

### Evidence Chain

1. `ss -tnp` showed `SYN-SENT` state on `127.0.0.1:4317` (gRPC OTEL port) during every turn
2. `~/.zshrc_claude` exported these env vars into every Claude session:
   ```bash
   export CLAUDE_CODE_ENABLE_TELEMETRY=1
   export OTEL_METRICS_EXPORTER=otlp
   export OTEL_LOGS_EXPORTER=otlp
   export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
   export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
   ```
3. No OTEL collector was running on localhost:4317
4. Claude Code's OTEL `BatchSpanProcessor` uses `scheduledDelayMillis=5000` (5 seconds)
5. At end-of-turn, span.end() triggers a flush attempt → gRPC connect to dead endpoint → TCP SYN timeout (~5-7s)

### Why `DISABLE_TELEMETRY=1` Did Not Help

`DISABLE_TELEMETRY` (set via `~/.claude/settings.json` env block) only controls Claude Code's **custom event telemetry** (`iP()` function). It does NOT control the OTEL SDK traces/metrics/logs exporters, which are configured by the standard `OTEL_*` env vars from the shell profile.

### Fix Applied

1. Commented out all OTEL env vars in `~/.zshrc_claude` (lines 7-11)
2. Set `OTEL_TRACES_EXPORTER=none` in `~/.claude/settings.json` as belt-and-suspenders
3. Removed ineffective `DISABLE_TELEMETRY=1` from settings.json

### Expected Result

Gap should drop from ~5.7s mean to <0.5s. Requires session restart to pick up the env var changes.

### To Re-enable OTEL Telemetry

Start an OTEL collector first, then uncomment the env vars in `~/.zshrc_claude`:
```bash
docker run -p 4317:4317 otel/opentelemetry-collector:latest
```

## Appendix: Data Collection Methodology

- **hook-profile.log**: Bash hook writing PROFILE_ENTER/PROFILE_EXIT with `date '+%y%m%d%H%M%S.%3N'` for each hook event
- **nous.log**: Python logging from nous.py with timestamps for STOP handler entry, dispatch, and completion
- **Session JSONL**: Claude Code's native session transcript format with entries for all events including stop_hook_summary and turn_duration
- **Analysis**: Python scripts correlating timestamps across all three sources, with timezone normalization (local UTC+2 → UTC)
