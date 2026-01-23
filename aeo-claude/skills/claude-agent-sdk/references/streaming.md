# Claude Agent SDK - Streaming vs Single Mode

## Comparison

| Aspect | Streaming Mode | Single Message Mode |
|--------|---------------|---------------------|
| **Use Case** | Long-lived, interactive sessions | One-shot, serverless |
| **State** | Persistent across turns | Stateless (or manual resume) |
| **Feedback** | Real-time as generated | Final results only |
| **Interruption** | Supported | Not available |
| **Hooks** | Full support | Not available |
| **Image Attachments** | Supported | Not supported |
| **Complexity** | Higher initial setup | Minimal overhead |

---

## When to Use Each Mode

### Streaming Mode (Recommended for Most Cases)

Use when you need:

- Multi-turn conversations with context preservation
- Real-time feedback during long operations
- Ability to interrupt running tasks
- Dynamic message queueing with images
- Hook integration for tool monitoring

```python
from claude_agent_sdk import ClaudeSDKClient
import asyncio

async def streaming_example():
    async with ClaudeSDKClient() as client:
        await client.query("What's the weather like?")

        async for msg in client.receive_response():
            print(msg)

        # Follow-up with preserved context
        await client.query("Tell me more about that")

        async for msg in client.receive_response():
            print(msg)

asyncio.run(streaming_example())
```

### Single Message Mode

Use when you need:

- Simple request-response patterns
- Serverless environments (Lambda, Cloud Functions)
- Independent queries without multi-turn dialogue
- Minimal setup and complexity

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import asyncio

async def single_message_example():
    async for message in query(
        prompt="Explain the authentication flow",
        options=ClaudeAgentOptions(
            max_turns=1,
            allowed_tools=["Read", "Grep"]
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

asyncio.run(single_message_example())
```

---

## Streaming Input Patterns

### Dynamic Message Generation

Use async generators to stream messages incrementally:

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def message_stream():
    yield {"type": "text", "text": "Analyze the following data:"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "Temperature: 25C"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "Humidity: 60%"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "What patterns do you see?"}

async def main():
    async with ClaudeSDKClient() as client:
        await client.query(message_stream())

        async for message in client.receive_response():
            print(message)

        # Follow-up in same session
        await client.query("Should we be concerned about these readings?")

        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

---

## Real-Time Progress Monitoring

Monitor agent progress by inspecting message block types:

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    TextBlock
)
import asyncio

async def monitor_progress():
    options = ClaudeAgentOptions(
        allowed_tools=["Write", "Bash"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Create 5 Python files with different sorting algorithms"
        )

        files_created = []
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        if block.name == "Write":
                            file_path = block.input.get("file_path", "")
                            print(f"Creating: {file_path}")
                    elif isinstance(block, ToolResultBlock):
                        print("Completed tool execution")
                    elif isinstance(block, TextBlock):
                        print(f"Claude says: {block.text[:100]}...")

            if hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
                print("Task completed!")
                break

asyncio.run(monitor_progress())
```

---

## Concurrent Message Processing

Handle sending and receiving concurrently:

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        async def receive_messages():
            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Claude: {block.text}")

        receive_task = asyncio.create_task(receive_messages())

        questions = [
            "What is 2 + 2?",
            "What is the square root of 144?",
            "What is 10% of 80?"
        ]

        for question in questions:
            print(f"User: {question}")
            await client.query(question)
            await asyncio.sleep(3)

        await asyncio.sleep(2)
        receive_task.cancel()
        try:
            await receive_task
        except asyncio.CancelledError:
            pass

asyncio.run(main())
```

---

## Interrupt Handling

Stop long-running tasks gracefully:

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def interruptible_task():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Analyze all files in this large codebase")

        async def monitor_with_timeout():
            try:
                async for msg in client.receive_messages():
                    print(msg)
            except asyncio.CancelledError:
                await client.interrupt()
                print("Task interrupted by user")

        task = asyncio.create_task(monitor_with_timeout())

        # Interrupt after 5 seconds
        await asyncio.sleep(5)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

asyncio.run(interruptible_task())
```

---

## Session Continuation (Single Mode)

Continue conversations in single message mode:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import asyncio

async def continued_conversation():
    # First query
    async for message in query(
        prompt="Explain the authentication flow",
        options=ClaudeAgentOptions(
            max_turns=1,
            allowed_tools=["Read", "Grep"]
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

    # Continue with previous context
    async for message in query(
        prompt="Now explain the authorization process",
        options=ClaudeAgentOptions(
            continue_conversation=True,
            max_turns=1
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

asyncio.run(continued_conversation())
```

---

## Best Practices

### Streaming Mode

1. Always use async context manager for resource cleanup
2. Process messages incrementally for responsiveness
3. Handle `ResultMessage` to detect completion
4. Implement interrupt handlers for long operations
5. Use `receive_response()` for simple turn-based flows

### Single Message Mode

1. Set `max_turns=1` for true one-shot behavior
2. Use `continue_conversation=True` when resuming
3. Handle errors explicitly (no interrupt capability)
4. Prefer for Lambda/serverless deployments

### General

1. Match mode to your deployment environment
2. Use streaming for interactive applications
3. Use single mode for batch/background processing
4. Always handle `ResultMessage.is_error` appropriately
