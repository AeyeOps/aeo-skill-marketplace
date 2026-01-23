"""Basic query() example - one-shot task execution.

Demonstrates the simplest way to use the Claude Agent SDK for stateless,
one-shot tasks. Uses the query() async iterator pattern.

Requirements:
    - claude-agent-sdk>=0.1.20
    - Claude Code CLI installed (claude command available)
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    CLINotFoundError,
    ProcessError,
)


async def main() -> None:
    """Execute a simple one-shot query."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        permission_mode="default",
        max_turns=5,
    )

    try:
        async for message in query(
            prompt="List Python files in current directory",
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

            elif isinstance(message, ResultMessage):
                if message.total_cost_usd is not None:
                    print(f"\nCost: ${message.total_cost_usd:.4f}")
                if message.is_error:
                    print(f"Error: {message.result}")

    except CLINotFoundError:
        print("Error: Claude Code CLI not installed")
        print("Install with: npm install -g @anthropic-ai/claude-code")

    except ProcessError as e:
        print(f"Process error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
