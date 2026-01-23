#!/usr/bin/env python3
"""
MCP Connection Tester

Tests connectivity and protocol compliance of an MCP server.
Usage:
    python test_mcp_connection.py http://localhost:8000/mcp
    python test_mcp_connection.py --transport stdio --command "python server.py"
"""

import argparse
import asyncio
import json
import sys
from typing import Any

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


async def test_http_connection(url: str) -> dict[str, Any]:
    """Test HTTP MCP server connection"""
    results = {
        "connectivity": False,
        "initialize": False,
        "tools_list": False,
        "session_management": False,
        "errors": []
    }

    print_info(f"Testing connection to: {url}")

    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url.replace('/mcp', '/'))
            print_success(f"Server reachable (status: {response.status_code})")
            results["connectivity"] = True
    except httpx.ConnectError as e:
        print_error(f"Connection failed: {e}")
        results["errors"].append(f"Connection error: {e}")
        return results
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        results["errors"].append(f"Unexpected error: {e}")
        return results

    # Test 2: Initialize handshake
    print("\n2. Testing initialize handshake...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "MCP Connection Tester",
                        "version": "1.0.0"
                    }
                }
            }

            response = await client.post(
                url,
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

            if response.status_code != 200:
                print_error(f"Initialize failed with status {response.status_code}")
                results["errors"].append(f"Initialize HTTP {response.status_code}")
                return results

            data = response.json()

            if "error" in data:
                print_error(f"Initialize error: {data['error']['message']}")
                results["errors"].append(f"Initialize error: {data['error']}")
                return results

            if "result" not in data:
                print_error("Initialize response missing 'result' field")
                results["errors"].append("Invalid initialize response format")
                return results

            result = data["result"]
            print_success("Initialize handshake successful")
            print_info(f"  Server: {result.get('serverInfo', {}).get('name', 'Unknown')}")
            print_info(f"  Version: {result.get('protocolVersion', 'Unknown')}")

            capabilities = result.get("capabilities", {})
            if "tools" in capabilities:
                print_info("  Capabilities: tools ✓")
            if "resources" in capabilities:
                print_info("  Capabilities: resources ✓")

            results["initialize"] = True

            # Check for session ID
            session_id = response.headers.get("Mcp-Session-Id")
            if session_id:
                print_success(f"Session ID received: {session_id[:16]}...")
                results["session_management"] = True
            else:
                print_warning("No session ID in response (stateless mode?)")

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {e}")
        results["errors"].append(f"JSON decode error: {e}")
        return results
    except Exception as e:
        print_error(f"Initialize failed: {e}")
        results["errors"].append(f"Initialize exception: {e}")
        return results

    # Test 3: List tools
    print("\n3. Testing tools/list...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            if session_id:
                headers["Mcp-Session-Id"] = session_id

            response = await client.post(url, json=tools_request, headers=headers)

            if response.status_code != 200:
                print_warning(f"tools/list returned status {response.status_code}")
            else:
                data = response.json()
                if "error" in data:
                    print_warning(f"tools/list error: {data['error']['message']}")
                elif "result" in data:
                    tools = data["result"].get("tools", [])
                    print_success(f"Found {len(tools)} tool(s)")
                    for tool in tools[:5]:  # Show first 5
                        print_info(f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'no description')}")
                    if len(tools) > 5:
                        print_info(f"  ... and {len(tools) - 5} more")
                    results["tools_list"] = True

    except Exception as e:
        print_warning(f"tools/list failed: {e}")

    # Test 4: SSE support
    print("\n4. Testing SSE support...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                url,
                headers={"Accept": "text/event-stream"}
            )

            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    print_success("SSE supported")
                else:
                    print_warning(f"Unexpected content-type: {content_type}")
            elif response.status_code == 405:
                print_info("SSE not supported (stateless mode)")
            else:
                print_warning(f"SSE test returned status {response.status_code}")

    except Exception as e:
        print_info(f"SSE test inconclusive: {e}")

    return results


async def test_stdio_connection(command: str, args: list[str]) -> dict[str, Any]:
    """Test stdio MCP server connection"""
    results = {
        "connectivity": False,
        "initialize": False,
        "tools_list": False,
        "errors": []
    }

    print_info(f"Testing stdio connection: {command} {' '.join(args)}")
    print_error("stdio testing not yet implemented")
    results["errors"].append("stdio transport not implemented in tester")

    return results


async def main():
    parser = argparse.ArgumentParser(description="Test MCP server connectivity and protocol compliance")
    parser.add_argument("url", nargs="?", help="MCP server URL (e.g., http://localhost:8000/mcp)")
    parser.add_argument("--transport", choices=["http", "stdio"], default="http", help="Transport type")
    parser.add_argument("--command", help="Command for stdio transport")
    parser.add_argument("--args", nargs="*", help="Arguments for stdio command")

    args = parser.parse_args()

    if args.transport == "http":
        if not args.url:
            print_error("URL required for HTTP transport")
            parser.print_help()
            sys.exit(1)

        results = await test_http_connection(args.url)

    elif args.transport == "stdio":
        if not args.command:
            print_error("--command required for stdio transport")
            sys.exit(1)

        results = await test_stdio_connection(args.command, args.args or [])

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    checks = {
        "Connectivity": results.get("connectivity", False),
        "Initialize": results.get("initialize", False),
        "Tools List": results.get("tools_list", False),
        "Session Management": results.get("session_management", False)
    }

    for check, passed in checks.items():
        if passed:
            print_success(check)
        else:
            print_error(check)

    if results.get("errors"):
        print(f"\n{Colors.RED}Errors:{Colors.RESET}")
        for error in results["errors"]:
            print(f"  - {error}")

    all_passed = all(checks.values())
    if all_passed:
        print(f"\n{Colors.GREEN}All checks passed!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}Some checks failed{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
