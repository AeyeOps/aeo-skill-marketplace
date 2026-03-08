# claude -p Subprocess Patterns for Skill Scripts

Last verified: 2026-03-06 against code.claude.com/docs/en/headless and code.claude.com/docs/en/cli-reference

## Why This Exists

The official `skill-creator` plugin uses `anthropic.Anthropic()` SDK calls which require an API key
(paid subscription). This KB documents how to replace those calls with `claude -p` subprocess
invocations that use whatever auth the CLI already has — no SDK dependency, no subscription gate.

## Parity Mapping: SDK vs claude -p

| Original SDK | `claude -p` Equivalent | Notes |
|---|---|---|
| `model=model` | `--model model` | Exact match |
| `thinking: {"type": "enabled", "budget_tokens": 10000}` | `--effort high` | Enables deep thinking. Not documented on website but present in `claude --help` |
| `max_tokens=16000` | Managed by CLI internally | No direct flag |
| Single-turn `messages=[{"role":"user","content":prompt}]` | `claude -p "prompt"` | Exact match |
| Multi-turn `messages=[{user},{assistant},{user}]` | First call captures `session_id`, second call uses `--resume $session_id` | Session preserves full conversation history |
| `response.content` with separate `thinking`/`text` blocks | `--output-format stream-json --verbose --include-partial-messages` then parse `thinking_delta`/`text_delta` events | Full parity — accumulate deltas to reconstruct both blocks |
| `response.content` text only (no thinking needed) | `--output-format json` → `data["result"]` | Simpler but no thinking separation |
| No tools (pure text generation) | Default behavior — `claude -p` without `--allowedTools` prompts for tools. Use `--max-turns 1` or constrain with `--tools ""` if needed | SDK `messages.create()` has no tools by default |

## Output Format: --output-format json

Returns a single JSON object with (at minimum):
- `result` — the text response (thinking folded in, not separated)
- `session_id` — UUID for `--resume` continuation

Docs say: "structured JSON with result, session ID, and metadata"

To extract:
```bash
claude -p "prompt" --output-format json | jq -r '.result'
session_id=$(claude -p "prompt" --output-format json | jq -r '.session_id')
```

## Output Format: --output-format stream-json

Newline-delimited JSON objects. Requires `--verbose` to get stream events. Add `--include-partial-messages`
for token-by-token content block events.

### Event Types (from run_eval.py observation + docs)

```
content_block_start  → {type: "stream_event", event: {type: "content_block_start", content_block: {type: "thinking"|"text"|"tool_use", ...}}}
content_block_delta  → {type: "stream_event", event: {type: "content_block_delta", delta: {type: "thinking_delta"|"text_delta"|"input_json_delta", ...}}}
content_block_stop   → {type: "stream_event", event: {type: "content_block_stop"}}
message_stop         → {type: "stream_event", event: {type: "message_stop"}}
```

Full assistant message (after completion):
```
{type: "assistant", message: {content: [{type: "text", text: "..."}, {type: "tool_use", ...}]}}
```

Final result:
```
{type: "result", session_id: "...", ...}
```

### Capturing Thinking from stream-json

Filter for thinking blocks:
```bash
claude -p "prompt" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "thinking_delta") | .event.delta.thinking'
```

Filter for text (non-thinking):
```bash
claude -p "prompt" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

## Session Continuation (--resume)

```bash
# First call — capture session_id
session_id=$(claude -p "first prompt" --output-format json | jq -r '.session_id')

# Second call — resumes conversation (model sees full prior context)
claude -p "follow-up prompt" --resume "$session_id"
```

This replicates the SDK multi-turn pattern:
```python
messages=[
    {"role": "user", "content": prompt},          # turn 1 — first claude -p call
    {"role": "assistant", "content": text},        # turn 2 — stored in session
    {"role": "user", "content": shorten_prompt},   # turn 3 — --resume call
]
```

## CLAUDECODE Env Var Stripping

When running `claude -p` from inside an active Claude Code session, strip the `CLAUDECODE`
env var to prevent the "already running" guard:

```python
env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
subprocess.run(cmd, env=env, ...)
```

Both `run_eval.py` and `improve_description.py` use this pattern.

## Key CLI Flags Reference

From `claude --help` and code.claude.com/docs/en/cli-reference (March 2026):

| Flag | Description |
|---|---|
| `-p, --print` | Non-interactive mode — print response and exit |
| `--output-format json\|text\|stream-json` | Response format |
| `--model <model>` | Model alias (`sonnet`, `opus`) or full name |
| `--effort <level>` | `low`, `medium`, `high` — controls thinking depth |
| `--max-turns <n>` | Limit agentic turns (print mode only) |
| `--max-budget-usd <amount>` | Spending cap (print mode only) |
| `--resume, -r <session_id>` | Resume specific conversation |
| `--continue, -c` | Resume most recent conversation |
| `--verbose` | Full turn-by-turn output; required for stream-json events |
| `--include-partial-messages` | Token-level streaming (requires stream-json + verbose) |
| `--allowedTools <tools>` | Auto-approve specific tools without prompting |
| `--tools <tools>` | Restrict available tools (`""` disables all) |
| `--append-system-prompt <text>` | Add to default system prompt |
| `--system-prompt <text>` | Replace entire system prompt |
| `--json-schema <schema>` | Structured output validation (response in `structured_output` field) |
| `--no-session-persistence` | Don't save session to disk |
| `--dangerously-skip-permissions` | Skip all permission prompts |
| `--fallback-model <model>` | Auto-fallback when primary overloaded |

## Existing Patterns in skill-creator Scripts

### run_eval.py — Triggering Detection
Uses `stream-json` with `Popen` for early detection of skill triggering:
```python
cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
if model:
    cmd.extend(["--model", model])
env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=project_root, env=env)
```
Parses `content_block_start` for `tool_use` type, accumulates `input_json_delta`, checks for skill name match.

### improve_description.py — Text Generation with Thinking (patched)
Uses `--output-format stream-json --verbose --include-partial-messages --effort high` to
capture thinking blocks separately, matching the original SDK's `thinking.type=enabled` behavior:
```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "stream-json",
    "--verbose",
    "--include-partial-messages",
    "--effort", "high",
]
if model:
    cmd.extend(["--model", model])
if session_id:
    cmd.extend(["--resume", session_id])
env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
result = subprocess.run(cmd, capture_output=True, text=True, env=env)
# Parse stream to separate thinking_text, text, session_id
```
Returns `(thinking_text, text, session_id)` — full parity with SDK's content blocks.
The shorten flow uses `--resume session_id` for multi-turn conversation context.

### run_loop.py — Orchestration
Calls `improve_description()` and `run_eval()` in a loop. No direct subprocess usage — delegates to the above.

## Resolved: Thinking in Transcript Logs

The SDK version captured `thinking_text` separately and logged it to transcript JSON files.
With `--output-format json`, thinking is folded into processing but not exposed in `result`.

**Solution**: Use `--output-format stream-json --verbose --include-partial-messages` and parse
the stream to accumulate `thinking_delta` and `text_delta` events separately. This achieves
full parity with the SDK's separate `thinking`/`text` content blocks.

### --include-partial-messages Flag

From official docs (code.claude.com/docs/en/headless, March 2026):
> "Include partial streaming events in output (requires `--print` and `--output-format=stream-json`)"

This flag enables token-level content block events in the stream. Without it, you only get
the final `assistant` message and `result` event. With it, you get:
- `content_block_start` — signals a new block (thinking, text, tool_use)
- `content_block_delta` — incremental content (thinking_delta, text_delta, input_json_delta)
- `content_block_stop` — block complete
- `message_stop` — message complete

### Python Pattern for Separating Thinking from Text

```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "stream-json",
    "--verbose",
    "--include-partial-messages",
    "--effort", "high",
]
if model:
    cmd.extend(["--model", model])
if session_id:
    cmd.extend(["--resume", session_id])

env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
result = subprocess.run(cmd, capture_output=True, text=True, env=env)

thinking_text = ""
text = ""
sid = ""

for line in result.stdout.split("\n"):
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue

    if event.get("type") == "stream_event":
        se = event.get("event", {})
        se_type = se.get("type", "")

        if se_type == "content_block_delta":
            delta = se.get("delta", {})
            delta_type = delta.get("type", "")
            if delta_type == "thinking_delta":
                thinking_text += delta.get("thinking", "")
            elif delta_type == "text_delta":
                text += delta.get("text", "")

    elif event.get("type") == "result":
        sid = event.get("session_id", "")
```

This mirrors the SDK pattern:
```python
for block in response.content:
    if block.type == "thinking":
        thinking_text = block.thinking
    elif block.type == "text":
        text = block.text
```

### Session ID from stream-json

The `session_id` comes from the final `result` event (not from content blocks):
```json
{"type": "result", "session_id": "abc-123-...", ...}
```

This is the same `session_id` that `--output-format json` returns in its top-level object,
just delivered at the end of the stream instead.
