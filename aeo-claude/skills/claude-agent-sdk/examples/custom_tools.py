"""Custom MCP tools with @tool decorator.

Demonstrates how to create custom tools using the @tool decorator and
expose them via MCP server. Based on patterns from aeo-axis libs/sme/tools/factory.py.

Requirements:
    - claude-agent-sdk>=0.1.20
    - Claude Code CLI installed
"""

import asyncio
from typing import Any
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    AssistantMessage,
    TextBlock,
)


@tool("calculate", "Perform arithmetic calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Safe arithmetic evaluation with error handling.

    Args:
        args: Dict with 'expression' key containing math expression

    Returns:
        Tool response dict with content or error
    """
    try:
        # Safe eval with restricted builtins (no access to __import__, etc.)
        result = eval(args["expression"], {"__builtins__": {}}, {})
        return {
            "content": [{"type": "text", "text": f"Result: {result}"}]
        }
    except Exception as e:
        # Return error in tool response format
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True,
        }


@tool("greet", "Greet a user by name", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    """Simple greeting tool.

    Args:
        args: Dict with 'name' key

    Returns:
        Tool response dict with greeting text
    """
    name = args.get("name", "World")
    return {
        "content": [{"type": "text", "text": f"Hello, {name}!"}]
    }


@tool(
    "lookup_user",
    "Look up user information by ID",
    {"user_id": int, "include_email": bool},
)
async def lookup_user(args: dict[str, Any]) -> dict[str, Any]:
    """Example tool with multiple typed parameters.

    Args:
        args: Dict with 'user_id' (int) and 'include_email' (bool)

    Returns:
        Tool response dict with user info
    """
    user_id = args.get("user_id", 0)
    include_email = args.get("include_email", False)

    # Simulate user lookup
    user_info = f"User #{user_id}: John Doe"
    if include_email:
        user_info += f" (john.doe.{user_id}@example.com)"

    return {
        "content": [{"type": "text", "text": user_info}]
    }


async def main() -> None:
    """Run agent with custom MCP tools."""
    # Create MCP server with our custom tools
    server = create_sdk_mcp_server(
        name="demo",
        version="1.0.0",
        tools=[calculate, greet, lookup_user],
    )

    options = ClaudeAgentOptions(
        mcp_servers={"demo": server},
        allowed_tools=[
            "mcp__demo__calculate",
            "mcp__demo__greet",
            "mcp__demo__lookup_user",
        ],
        permission_mode="acceptEdits",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Calculate 2 + 2, then greet Alice, then look up user 42 with email")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

            elif isinstance(msg, ResultMessage):
                cost = f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "N/A"
                print(f"\nDone. Cost: {cost}")


if __name__ == "__main__":
    asyncio.run(main())
