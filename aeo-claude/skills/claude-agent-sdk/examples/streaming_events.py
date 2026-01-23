"""Streaming events example - real-time partial message updates.

Demonstrates how to enable and process StreamEvent for real-time
token-by-token streaming. Useful for interactive UIs where you want
to show Claude's response as it generates.

Requirements:
    - claude-agent-sdk>=0.1.20
    - Claude Code CLI installed
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    TextBlock,
)


async def main() -> None:
    """Run query with streaming events enabled."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        permission_mode="acceptEdits",
        include_partial_messages=True,  # Enable StreamEvent
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Write a haiku about programming")

        block_count = 0

        async for msg in client.receive_response():
            if isinstance(msg, StreamEvent):
                # Raw Anthropic API stream event
                event_type = msg.event.get("type", "")

                if event_type == "content_block_start":
                    block = msg.event.get("content_block", {})
                    block_type = block.get("type", "")
                    block_count += 1
                    print(f"[Stream] Block {block_count} started: {block_type}")

                elif event_type == "content_block_delta":
                    delta = msg.event.get("delta", {})
                    delta_type = delta.get("type", "")

                    if delta_type == "text_delta":
                        # Print text as it streams in
                        text = delta.get("text", "")
                        print(text, end="", flush=True)

                    elif delta_type == "thinking_delta":
                        # Extended thinking streaming (if enabled)
                        thinking = delta.get("thinking", "")
                        print(f"[think]{thinking}", end="", flush=True)

                elif event_type == "content_block_stop":
                    print()  # Newline after block completes

                elif event_type == "message_stop":
                    print("[Stream] Message complete")

            elif isinstance(msg, AssistantMessage):
                # Full message after streaming completes
                # This contains all blocks accumulated from the stream
                text_blocks = [b for b in msg.content if isinstance(b, TextBlock)]
                print(f"\n[Full Message] {len(msg.content)} blocks, {len(text_blocks)} text")

            elif isinstance(msg, ResultMessage):
                print(f"\n--- Result ---")
                print(f"Session: {msg.session_id}")
                if msg.total_cost_usd is not None:
                    print(f"Cost: ${msg.total_cost_usd:.4f}")
                if msg.is_error:
                    print(f"Error: {msg.result}")


if __name__ == "__main__":
    asyncio.run(main())
