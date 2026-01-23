"""Stateful client with hooks and multi-turn conversation.

Demonstrates production patterns with ClaudeSDKClient including:
- Multi-turn conversations with preserved context
- PreCompact hook for context limit warnings
- PreToolUse hook for command validation
- Session management

Based on patterns from aeo-axis libs/costblitz_extension/agent.py.

Requirements:
    - claude-agent-sdk>=0.1.20
    - Claude Code CLI installed
"""

import asyncio
import logging
from typing import Any
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def precompact_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Called before context compaction.

    PreCompact fires when the conversation is approaching context limits
    and the SDK needs to compact/summarize the conversation history.

    Args:
        input_data: Contains conversation state info
        tool_use_id: Not used for PreCompact
        context: Hook context (signal field for future abort support)

    Returns:
        Empty dict (acknowledgment)
    """
    logger.warning("PreCompact triggered - context limit approaching")
    # Could persist state, notify user, or trigger summary
    return {}


async def pretool_validator(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Validate tool calls before execution.

    PreToolUse hook runs before each tool invocation. Return a deny
    decision to block dangerous operations.

    Args:
        input_data: Contains 'tool_name' and 'tool_input'
        tool_use_id: Unique ID for this tool invocation
        context: Hook context

    Returns:
        Empty dict to allow, or hookSpecificOutput with deny to block
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Block dangerous commands
        dangerous_patterns = ["rm -rf", "mkfs.", "> /dev/", "dd if="]
        for pattern in dangerous_patterns:
            if pattern in command:
                logger.warning(f"Blocked dangerous command: {command[:50]}...")
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Dangerous pattern '{pattern}' blocked",
                    }
                }

        # Log all bash commands
        logger.info(f"Allowing Bash command: {command[:80]}...")

    return {}


async def main() -> None:
    """Run multi-turn conversation with hooks."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Bash"],
        permission_mode="acceptEdits",
        max_turns=10,
        hooks={
            "PreCompact": [HookMatcher(hooks=[precompact_hook])],
            "PreToolUse": [HookMatcher(matcher="Bash", hooks=[pretool_validator])],
        },
    )

    session_id: str | None = None

    async with ClaudeSDKClient(options=options) as client:
        # First turn
        print("--- Turn 1: Directory listing ---")
        await client.query("What files are in the current directory?")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        # Truncate long responses
                        text = block.text
                        if len(text) > 300:
                            text = text[:300] + "..."
                        print(f"Claude: {text}")

            elif isinstance(msg, ResultMessage):
                session_id = msg.session_id
                print(f"\nSession: {session_id}")

        # Second turn - context preserved
        print("\n--- Turn 2: Follow-up question ---")
        await client.query("How many Python files are there?")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd is not None:
                    print(f"\nTotal cost: ${msg.total_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
