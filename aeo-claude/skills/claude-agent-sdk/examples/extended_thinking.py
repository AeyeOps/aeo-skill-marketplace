"""Extended thinking example - accessing Claude's reasoning process.

Demonstrates how to enable and access extended thinking (ThinkingBlock)
to observe Claude's step-by-step reasoning before the final response.

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
    TextBlock,
    ThinkingBlock,
)


async def main() -> None:
    """Run query with extended thinking enabled."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read"],
        permission_mode="default",
        max_thinking_tokens=5000,  # Enable extended thinking
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Analyze the trade-offs between using async vs sync code in Python. "
            "Think through the problem carefully before answering."
        )

        thinking_content: list[str] = []
        response_content: list[str] = []

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ThinkingBlock):
                        # Extended thinking - Claude's reasoning process
                        thinking_content.append(block.thinking)
                        # Show truncated thinking for demo
                        preview = block.thinking[:150].replace("\n", " ")
                        if len(block.thinking) > 150:
                            preview += "..."
                        print(f"[Thinking] {preview}")

                    elif isinstance(block, TextBlock):
                        # Final response to user
                        response_content.append(block.text)
                        print(f"\n[Response]\n{block.text}")

            elif isinstance(msg, ResultMessage):
                print(f"\n--- Summary ---")
                print(f"Session: {msg.session_id}")
                print(f"Thinking blocks: {len(thinking_content)}")
                print(f"Response blocks: {len(response_content)}")

                if thinking_content:
                    total_thinking = sum(len(t) for t in thinking_content)
                    print(f"Total thinking chars: {total_thinking}")

                if msg.total_cost_usd is not None:
                    print(f"Cost: ${msg.total_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
