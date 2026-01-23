# Claude Agent SDK - Tools and MCP Integration

## Overview

The Claude Agent SDK extends Claude's capabilities through:

1. **Built-in Tools** - File operations, search, web access
2. **Custom Tools** - User-defined tools via `@tool` decorator
3. **MCP Servers** - Model Context Protocol servers for external integrations
4. **Hooks** - Intercept and modify tool behavior

---

## @tool Decorator

Define custom MCP tools with type safety.

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any]
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique tool identifier |
| `description` | `str` | Human-readable description |
| `input_schema` | `type | dict` | Input parameter schema |

### Basic Tool Definition

```python
from claude_agent_sdk import tool
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {args['name']}!"
        }]
    }
```

### Input Schema Options

**Simple type mapping (recommended):**

```python
{"text": str, "count": int, "enabled": bool}
```

**JSON Schema format (for complex validation):**

```python
{
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "count": {"type": "integer", "minimum": 0}
    },
    "required": ["text"]
}
```

### Tool Return Format

All tools must return this structure:

```python
{
    "content": [{
        "type": "text",
        "text": "response content"
    }]
}
```

---

## Stateful Tools with Data Store

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient
from typing import Any

class DataStore:
    def __init__(self):
        self.items: list[str] = []
        self.counter: int = 0

store = DataStore()

@tool("add_item", "Add an item to the store", {"item": str})
async def add_item(args: dict[str, Any]) -> dict[str, Any]:
    store.items.append(args["item"])
    store.counter += 1
    return {
        "content": [{
            "type": "text",
            "text": f"Added '{args['item']}'. Total items: {store.counter}"
        }]
    }

@tool("list_items", "List all items in the store", {})
async def list_items(args: dict[str, Any]) -> dict[str, Any]:
    if not store.items:
        return {"content": [{"type": "text", "text": "Store is empty"}]}
    items_text = "\n".join(f"- {item}" for item in store.items)
    return {
        "content": [{"type": "text", "text": f"Items:\n{items_text}"}]
    }
```

---

## create_sdk_mcp_server()

Create in-process MCP servers from tool definitions.

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

### Basic Server Creation

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Greet Alice")
    async for msg in client.receive_response():
        print(msg)
```

### Multi-Tool Server

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query
from typing import Any

@tool("calculate", "Perform calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    result = eval(args["expression"])
    return {"content": [{"type": "text", "text": f"Result: {result}"}]}

@tool("translate", "Translate text", {"text": str, "target_lang": str})
async def translate(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Translated: {args['text']}"}]}

@tool("search_web", "Search the web", {"query": str})
async def search_web(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Search results for: {args['query']}"}]}

multi_tool_server = create_sdk_mcp_server(
    name="utilities",
    version="1.0.0",
    tools=[calculate, translate, search_web]
)

# Selective tool allowance
options = ClaudeAgentOptions(
    mcp_servers={"utilities": multi_tool_server},
    allowed_tools=[
        "mcp__utilities__calculate",
        "mcp__utilities__translate",
        # search_web is NOT allowed
    ]
)
```

---

## Tool Naming Convention

Tools become available with the pattern: `mcp__{server_name}__{tool_name}`

| Server Name | Tool Name | Full Reference |
|-------------|-----------|----------------|
| `tools` | `greet` | `mcp__tools__greet` |
| `utilities` | `calculate` | `mcp__utilities__calculate` |
| `store` | `add_item` | `mcp__store__add_item` |

---

## Hooks System

Intercept and modify behavior at key points.

### Hook Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| `PreToolUse` | Before tool execution | Validate/block tools |
| `PostToolUse` | After tool execution | Log/audit results |
| `UserPromptSubmit` | Before processing user input | Modify prompts |
| `Stop` | Agent stopping | Cleanup actions |
| `SubagentStop` | Subagent stopping | Subagent cleanup |
| `PreCompact` | Before context compaction | Save important context |

### Hook Signature

```python
async def hook_function(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]
```

### PreToolUse Hook Example

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher, HookContext
from typing import Any

async def check_bash_command(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    if tool_name != "Bash":
        return {}

    command = tool_input.get("command", "")
    block_patterns = ["rm -rf /", "foo.sh"]

    for pattern in block_patterns:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Command contains invalid pattern: {pattern}",
                }
            }
    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command]),
        ],
    }
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Run the bash command: ./foo.sh --help")
    async for msg in client.receive_response():
        print(msg)
```

### Logging Hooks

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext
)
from typing import Any

async def pre_tool_logger(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get('tool_name', 'unknown')
    print(f"[PRE-TOOL] About to use: {tool_name}")

    if tool_name == "Bash" and "rm -rf" in str(input_data.get('tool_input', {})):
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Dangerous command blocked'
            }
        }
    return {}

async def post_tool_logger(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get('tool_name', 'unknown')
    print(f"[POST-TOOL] Completed: {tool_name}")
    return {}
```

### Multiple Hooks Configuration

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher
import asyncio

async def main():
    options = ClaudeAgentOptions(
        hooks={
            'PreToolUse': [
                HookMatcher(hooks=[pre_tool_logger]),
                HookMatcher(matcher='Bash', hooks=[pre_tool_logger])
            ],
            'PostToolUse': [
                HookMatcher(hooks=[post_tool_logger])
            ],
            'UserPromptSubmit': [
                HookMatcher(hooks=[user_prompt_modifier])
            ]
        },
        allowed_tools=["Read", "Write", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List files in current directory")
        async for message in client.receive_response():
            pass

asyncio.run(main())
```

---

## Hook Return Values

### Allow (default)

```python
return {}
```

### Deny with Reason

```python
return {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': 'Reason for denial'
    }
}
```

### Modify Input

```python
return {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'modifiedInput': {
            'command': 'modified command'
        }
    }
}
```

---

## Custom Transport

Extend the SDK with custom communication layers:

```python
from claude_agent_sdk import Transport, query
from typing import AsyncIterator

class CustomTransport(Transport):
    async def connect(self) -> None:
        pass

    async def write(self, data: str) -> None:
        pass

    def read_messages(self) -> AsyncIterator[dict]:
        async def _read():
            while True:
                yield {}
        return _read()

    async def close(self) -> None:
        pass

    def is_ready(self) -> bool:
        return True

    async def end_input(self) -> None:
        pass

async def main():
    transport = CustomTransport()
    async for message in query(prompt="Hello", transport=transport):
        print(message)

import anyio
anyio.run(main)
```

---

## Best Practices

### Tool Design

1. Keep tool functions focused and single-purpose
2. Use descriptive names and descriptions
3. Validate inputs before processing
4. Return structured error messages on failure
5. Use type hints for all parameters

### Hook Design

1. Keep hooks lightweight and fast
2. Avoid side effects in PreToolUse hooks
3. Use PostToolUse for logging and auditing
4. Return early when hook doesn't apply
5. Document blocking patterns clearly

### Security

1. Never use `eval()` without sanitization
2. Block dangerous command patterns in hooks
3. Use `allowed_tools` to limit tool access
4. Audit all tool executions with PostToolUse
5. Validate external inputs thoroughly
