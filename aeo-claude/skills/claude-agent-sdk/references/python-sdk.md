# Claude Agent SDK - Python Reference

## Installation

```bash
pip install claude-agent-sdk
```

## Core APIs

The SDK provides two primary interaction patterns:

| Pattern | Use Case | State |
|---------|----------|-------|
| `query()` | One-shot tasks, serverless | Stateless |
| `ClaudeSDKClient` | Multi-turn conversations | Stateful |

---

## query() Function

Creates fresh sessions for independent tasks without conversation memory.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None
) -> AsyncIterator[Message]
```

### Basic Usage

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

### With Options

```python
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
        system_prompt="You are a helpful coding assistant.",
        max_turns=5,
        cwd="/path/to/project"
    )

    async for message in query(
        prompt="Create a hello.py file that prints 'Hello, World!'",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Cost: ${message.total_cost_usd:.4f}")

anyio.run(main)
```

---

## ClaudeSDKClient Class

Maintains persistent conversation sessions with context preserved across exchanges.

### Methods

| Method | Purpose |
|--------|---------|
| `connect(prompt?)` | Establish session, optionally with initial message |
| `query(prompt, session_id)` | Send streaming request within session |
| `receive_messages()` | Iterate all messages from Claude |
| `receive_response()` | Iterate until ResultMessage |
| `interrupt()` | Stop current execution |
| `disconnect()` | Terminate session |

### Context Manager Pattern

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(options) as client:
    await client.query("prompt")
    async for msg in client.receive_response():
        process(msg)
```

### Multi-Turn Conversation

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    ToolUseBlock
)
import asyncio

async def main():
    async with ClaudeSDKClient() as client:
        # First turn
        await client.query("What's the capital of France?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up with preserved context
        await client.query("What's the population of that city?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(main())
```

### Conversation Session Class

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
import asyncio

class ConversationSession:
    def __init__(self, options: ClaudeAgentOptions = None):
        self.client = ClaudeSDKClient(options)
        self.turn_count = 0

    async def start(self):
        await self.client.connect()
        print("Session started. Commands: 'exit', 'interrupt', 'new'")

        while True:
            user_input = input(f"\n[Turn {self.turn_count + 1}] You: ")

            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'interrupt':
                await self.client.interrupt()
                print("Task interrupted!")
                continue
            elif user_input.lower() == 'new':
                await self.client.disconnect()
                await self.client.connect()
                self.turn_count = 0
                print("New session started")
                continue

            await self.client.query(user_input)
            self.turn_count += 1

            print(f"[Turn {self.turn_count}] Claude: ", end="")
            async for message in self.client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="")
            print()

        await self.client.disconnect()
        print(f"Ended after {self.turn_count} turns.")

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits"
    )
    session = ConversationSession(options)
    await session.start()

asyncio.run(main())
```

---

## ClaudeAgentOptions

Configuration for customizing agent behavior.

```python
@dataclass
class ClaudeAgentOptions:
    allowed_tools: list[str] = []
    disallowed_tools: list[str] = []
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = {}
    permission_mode: PermissionMode | None = None
    cwd: str | Path | None = None
    model: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    max_thinking_tokens: int | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    can_use_tool: CanUseTool | None = None
    setting_sources: list[SettingSource] | None = None
    env: dict[str, str] | None = None
```

### Permission Modes

| Mode | Behavior |
|------|----------|
| `"default"` | Standard permission prompts |
| `"acceptEdits"` | Auto-accept file edits |
| `"plan"` | Planning mode |
| `"bypassPermissions"` | Skip all permission checks |

### Setting Sources

| Value | Loads From |
|-------|------------|
| `"user"` | User-level config |
| `"project"` | CLAUDE.md files |
| `"local"` | Local workspace config |

---

## Message Types

All messages inherit from base `Message` union.

### UserMessage

```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
```

### AssistantMessage

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
```

### SystemMessage

```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

### ResultMessage

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    is_error: bool
    session_id: str
    total_cost_usd: float | None = None
```

---

## Content Blocks

### TextBlock

```python
@dataclass
class TextBlock:
    text: str
```

### ThinkingBlock

```python
@dataclass
class ThinkingBlock:
    thinking: str
    signature: str
```

### ToolUseBlock

```python
@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
```

### ToolResultBlock

```python
@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

---

## Error Handling

```python
from claude_agent_sdk import (
    CLINotFoundError,      # SDK not installed
    ProcessError,          # Process execution failure
    CLIJSONDecodeError,    # Response parsing issue
    ClaudeSDKError         # Base exception
)

try:
    async for message in query(prompt="..."):
        pass
except CLINotFoundError:
    print("Claude CLI not installed")
except ProcessError as e:
    print(f"Process failed: {e}")
except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

---

## Built-in Tools

Available tool names for `allowed_tools`:

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
| `NotebookEdit` | Edit Jupyter notebooks |
| `TodoWrite` | Manage task lists |
| `BashOutput` | Get background shell output |
| `KillBash` | Kill background shell |

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API authentication |
| `CLAUDE_CODE_USE_BEDROCK` | Use AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI |
| `ANTHROPIC_MODEL` | Override default model |
