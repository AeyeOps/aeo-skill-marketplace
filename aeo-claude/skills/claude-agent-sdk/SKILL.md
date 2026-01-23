---
name: Claude Agent SDK Reference
description: |
  Build autonomous AI agents in Python using the Claude Agent SDK. Covers the GTVR execution pattern
  (gather, take action, verify, repeat), stateless query() and stateful ClaudeSDKClient APIs, streaming
  versus batch modes, custom tool creation with @tool decorator, MCP server integration, hook-based
  execution control, permission boundaries, API key and OAuth token management, multi-agent coordination,
  and production deployment strategies. Suited for programmatic agents, tool chains, and multi-agent
  systems. Not designed for basic chat interfaces.
---

# Claude Agent SDK - Python Expert

Build production-ready AI agents using Anthropic's Claude Agent SDK.

## Quick Start

```python
from claude_agent_sdk import query, ClaudeAgentOptions
import asyncio

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits"
    )
    async for message in query(prompt="Create hello.py", options=options):
        print(message)

asyncio.run(main())
```

## The Agent Loop (GTVR)

All Claude agents follow this pattern:

1. **Gather Context** - Search files, read docs, query APIs
2. **Take Action** - Execute tools, write code, run commands
3. **Verify Work** - Check outputs, self-correct errors
4. **Repeat** - Iterate until task complete

For detailed patterns: See [architecture-patterns.md](references/architecture-patterns.md)

## Core APIs

### Two Interaction Patterns

| Pattern | Use Case | State |
|---------|----------|-------|
| `query()` | One-shot tasks, serverless | Stateless |
| `ClaudeSDKClient` | Multi-turn conversations | Stateful |

### query() - Stateless Operations

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for message in query(
    prompt="Analyze this codebase",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Grep"],
        max_turns=5
    )
):
    if isinstance(message, ResultMessage):
        print(f"Cost: ${message.total_cost_usd:.4f}")
```

### ClaudeSDKClient - Stateful Sessions

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient() as client:
    await client.query("What's in this repo?")
    async for msg in client.receive_response():
        print(msg)

    # Follow-up with preserved context
    await client.query("Show me the main entry point")
    async for msg in client.receive_response():
        print(msg)
```

For complete API reference: See [python-sdk.md](references/python-sdk.md)

## Streaming vs Single Mode

| Aspect | Streaming | Single |
|--------|-----------|--------|
| **Use Case** | Interactive sessions | Serverless, one-shot |
| **Feedback** | Real-time | Final only |
| **Interruption** | Supported | Not available |
| **Hooks** | Full support | Not available |

For patterns and examples: See [streaming.md](references/streaming.md)

## Custom Tools

### @tool Decorator

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": f"Hello, {args['name']}!"}]
    }

server = create_sdk_mcp_server(name="tools", tools=[greet])
options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)
```

For tool design and MCP integration: See [tools-mcp.md](references/tools-mcp.md)

## Hooks System

Intercept tool execution for validation, logging, or blocking:

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, HookContext
from typing import Any

async def validate_bash(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command blocked"
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[validate_bash])]}
)
```

Hook events: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`

## Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Prompt for each action |
| `acceptEdits` | Auto-approve file edits |
| `bypassPermissions` | Fully autonomous |

## Authentication

Two authentication methods are supported:

| Method | Billing | Use Case |
|--------|---------|----------|
| API Key | Per-token | Serverless, CI/CD, production |
| Subscription | Flat rate | Development, interactive sessions |

### API Key

```python
options = ClaudeAgentOptions(
    env={"ANTHROPIC_API_KEY": "sk-ant-api..."},
)
```

### Subscription (OAuth)

First authenticate via CLI: `claude setup-token`

Then force OAuth by clearing any inherited API key:

```python
options = ClaudeAgentOptions(
    env={"ANTHROPIC_API_KEY": ""},  # Empty string forces OAuth
)
```

The SDK spawns a persistent Claude CLI subprocess that:
- Reads credentials from `~/.claude/.credentials.json` once at startup
- Handles token refresh internally using the refreshToken
- Your application does not manage token refresh

For complete auth patterns and token lifecycle: See [authentication.md](references/authentication.md)

## ClaudeAgentOptions

Key configuration fields:

```python
ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],
    permission_mode="acceptEdits",
    system_prompt="You are a coding assistant.",
    max_turns=10,
    max_budget_usd=5.0,
    cwd="/path/to/project",
    mcp_servers={"tools": server},
    hooks={"PreToolUse": [...]},
    setting_sources=["project"]  # Load CLAUDE.md
)
```

## Built-in Tools

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Write file contents |
| `Edit` | Edit existing files |
| `Bash` | Execute shell commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch URL content |
| `Task` | Spawn subagents |

## Message Types

```python
from claude_agent_sdk import (
    AssistantMessage,  # Claude's response
    UserMessage,       # User input
    SystemMessage,     # System events
    ResultMessage,     # Completion with cost
    TextBlock,         # Text content
    ToolUseBlock,      # Tool invocation
    ToolResultBlock    # Tool output
)
```

## Error Handling

```python
from claude_agent_sdk import (
    ClaudeSDKError,     # Base exception
    CLINotFoundError,   # SDK not installed
    ProcessError,       # Process failure
    CLIJSONDecodeError  # Parse error
)
```

## Production Patterns

- Use allowlists, not denylists for tools
- Implement PreToolUse hooks for validation
- Add PostToolUse hooks for logging
- Set `max_turns` and `max_budget_usd` limits
- Use `permission_mode="acceptEdits"` for development
- Mask secrets in logs

For deployment checklist: See [architecture-patterns.md](references/architecture-patterns.md)

## Reference Files

- **[python-sdk.md](references/python-sdk.md)** - Complete Python API reference
- **[streaming.md](references/streaming.md)** - Streaming vs single mode patterns
- **[tools-mcp.md](references/tools-mcp.md)** - Tool design and MCP integration
- **[authentication.md](references/authentication.md)** - API key vs subscription, token lifecycle
- **[architecture-patterns.md](references/architecture-patterns.md)** - GTVR, orchestration, production

## Examples

Complete, runnable scripts demonstrating SDK patterns:

| Example | Purpose | Key Patterns |
|---------|---------|--------------|
| [basic_query.py](examples/basic_query.py) | Simplest working agent | `query()`, message handling, error handling |
| [custom_tools.py](examples/custom_tools.py) | Custom MCP tools | `@tool` decorator, `create_sdk_mcp_server` |
| [stateful_client.py](examples/stateful_client.py) | Production patterns | `ClaudeSDKClient`, hooks, multi-turn |
| [extended_thinking.py](examples/extended_thinking.py) | Extended thinking | `ThinkingBlock`, `max_thinking_tokens` |
| [streaming_events.py](examples/streaming_events.py) | Real-time streaming | `StreamEvent`, `include_partial_messages` |

All examples require `claude-agent-sdk>=0.1.20` and the Claude Code CLI.

## External Resources

- **Context7**: Use `mcp__context7__get-library-docs` with `/anthropics/claude-agent-sdk-python`
- **Archon RAG**: Search `rag_search_knowledge_base(query="Claude Agent SDK")`
- **Platform Docs**: https://platform.claude.com/docs/en/agent-sdk/python

## When to Use This Skill

Use for:
- Building custom agents with Claude Agent SDK
- Designing effective tools and MCP servers
- Implementing permission models and guardrails
- Configuring authentication (API key or subscription)
- Managing token lifecycle and environment variables
- Creating multi-agent orchestration systems
- Deploying agents to production

Not for:
- Basic chat completion (use Messages API)
- Simple API calls (use direct HTTP)
- Non-agentic workflows (use prompts)
