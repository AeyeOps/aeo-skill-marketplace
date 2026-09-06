# Worked example: add per-client rate limiting to an HTTP API

The request, the coordinator's plan, the subagent briefs, and the verification, end to end.

## Request

> Add per-client rate limiting to the public API. 100 requests per minute per API key,
> 429 with a Retry-After header when exceeded, configurable per environment.

## 0. Plan mode

The coordinator calls `EnterPlanMode` before any other tool call. Nothing below runs until
the user approves the breakdown.

## 1. Understand

- `Grep` for the request pipeline: `middleware/` holds auth and logging middleware in order.
- `Read` `middleware/auth.py` to learn how the API key reaches the handler (`request.state.api_key`).
- `Glob` `config/*.yaml` to find per-environment settings and the existing config loader.
- `Read` `tests/middleware/test_auth.py` to see the test harness the new tests should reuse.

## 2. Task breakdown (`TaskCreate`)

| # | subject | description (abridged) | activeForm |
|---|---|---|---|
| T1 | Add rate-limit settings to config | `rate_limit.requests_per_minute` (int, default 100) and `rate_limit.enabled` (bool) in `config/schema.py` and every `config/*.yaml`; loader validates types. Acceptance: existing config tests pass, new fields load in all three environments | Adding rate-limit settings |
| T2 | Implement sliding-window limiter | `middleware/rate_limit.py`: sliding window keyed by `request.state.api_key`, in-process store behind an interface so a Redis store can replace it later. Acceptance: unit tests for allow, deny, window reset, disabled flag | Implementing rate limiter |
| T3 | Wire middleware and 429 response | Register after auth, before logging; on deny return 429 with `Retry-After` seconds until the window frees. Acceptance: integration test hits the limit and reads the header | Wiring middleware |
| T4 | Document the limit | Public API docs: limit, headers, 429 body; changelog entry | Documenting rate limit |

## 3. Dependencies (`TaskUpdate` with `addBlockedBy`)

- T2 blocked by T1 (needs the settings shape).
- T3 blocked by T2.
- T4 blocked by T3 (documents the final behavior).

T1 starts alone; nothing else is independent here, so the run is sequential. A breakdown
with independent tasks would dispatch them in the same turn.

## 4. Delegation (`Task`, `subagent_type: "general-purpose"`, `model: "opus"`)

Brief for T2, showing the shape every brief follows:

```
Implement middleware/rate_limit.py.

Context: API keys arrive as request.state.api_key (set by middleware/auth.py). Settings are
loaded by config/loader.py; the new fields are rate_limit.requests_per_minute and
rate_limit.enabled (added in T1, already merged).

Deliver: a sliding-window limiter keyed by API key, with an in-process store behind a small
interface (get_window, record) so a Redis-backed store can replace it without touching the
middleware. Unit tests in tests/middleware/test_rate_limit.py covering allow, deny at the
limit, reset after the window, and enabled=false passing everything through.

Acceptance: pytest tests/middleware passes; no changes outside middleware/ and tests/.

You have full implementation authority. If you discover additional work needed, create new
tasks using TaskCreate.
```

## 5. Monitor and verify

After each subagent reports back:

- `TaskList` to see what is unblocked.
- `Read` the files it named in its report. For T2: `middleware/rate_limit.py` and the test
  file; check the store interface exists and the disabled path is tested.
- Mark the task completed only after the read-back matches the acceptance line.

## 6. Final check

- Every task shows completed.
- `Read` `middleware/__init__.py` (or the app factory) to confirm the registration order
  auth, rate limit, logging.
- The integration test from T3 exists and asserts on `Retry-After`.
- Report to the user: what shipped, the default limit, how to change it per environment.
