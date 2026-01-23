# MCP Server Troubleshooting Guide

## Quick Triage Checklist

When an MCP server is not working, systematically check:

1. **Is the server process running?**
2. **Can you connect to the endpoint?**
3. **Does initialize handshake complete?**
4. **Are tools/resources discoverable?**
5. **Do tool calls execute successfully?**

## Common Issues and Solutions

### 1. Server Won't Start

#### Symptom: Process exits immediately or won't launch

**Check 1: Python Environment**
```bash
# Verify Python version (3.10+ required for FastMCP)
python --version

# Check if mcp package installed
python -c "import mcp; print(mcp.__version__)"

# Install if missing
pip install mcp
# or with uv:
uv add mcp
```

**Check 2: Import Errors**
```bash
# Run server with verbose errors
python -v server.py

# Common missing dependencies:
pip install fastapi starlette uvicorn  # For HTTP transport
pip install pydantic  # For schema validation
```

**Check 3: Port Already in Use**
```bash
# Check if port 8000 is occupied
lsof -i :8000

# Kill process or use different port
mcp.run(transport="streamable-http", port=8001)
```

**Check 4: Syntax Errors**
```bash
# Validate Python syntax
python -m py_compile server.py

# Check for common errors:
# - Missing colons after function definitions
# - Incorrect indentation
# - Unclosed brackets/parentheses
```

### 2. Connection Refused / Can't Reach Server

#### Symptom: Client cannot connect to HTTP endpoint

**Check 1: Server is Listening**
```bash
# Verify server is running
ps aux | grep python

# Check which port server is listening on
lsof -i -P | grep python

# Test with curl
curl http://localhost:8000/mcp
```

**Check 2: Firewall Rules**
```bash
# Check if port is blocked
sudo iptables -L -n | grep 8000

# For macOS:
sudo pfctl -s rules | grep 8000

# Temporarily allow port
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
```

**Check 3: Binding Address**
```python
# Server might be bound to 127.0.0.1 (localhost only)
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)

# For production, use reverse proxy instead
# and bind to localhost for security
```

**Check 4: Network Routing**
```bash
# If server is on different machine
ping server-hostname

# Check route
traceroute server-hostname

# Test port connectivity
telnet server-hostname 8000
nc -zv server-hostname 8000
```

### 3. Initialize Handshake Fails

#### Symptom: Connection works but initialize fails

**Check 1: Protocol Version Mismatch**
```bash
# Server logs should show version error
# Look for: "Unsupported protocol version"

# Fix: Update client to match server version
{
  "protocolVersion": "2025-03-26"  # Match server version
}
```

**Check 2: Invalid Initialize Parameters**
```json
// Common mistakes:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},  // CORRECT
    "clientInfo": {
      "name": "MyClient",
      "version": "1.0.0"
    }
  }
}

// Wrong: capabilities as array
"capabilities": []  // ERROR

// Wrong: missing clientInfo
```

**Check 3: Server Error During Initialize**
```python
# Add logging to server init
import logging
logging.basicConfig(level=logging.DEBUG)

# Check for errors in:
# - Database connections
# - Configuration loading
# - Resource initialization
```

**Check 4: Timeout**
```python
# Increase client timeout
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)
```

### 4. Tools Not Discovered

#### Symptom: tools/list returns empty or fails

**Check 1: Tools Actually Defined**
```python
# Verify decorator syntax
@mcp.tool()  # Correct
def my_tool() -> str:
    return "result"

# Common mistakes:
@mcp.tool  # Missing ()
@tool()    # Wrong decorator name
```

**Check 2: Server Capabilities**
```json
// Server must advertise tools capability
{
  "capabilities": {
    "tools": {
      "listChanged": true  // Optional
    }
  }
}
```

**Check 3: Tool Registration**
```python
# Ensure tools defined before run()
@mcp.tool()
def tool1() -> str:
    return "a"

@mcp.tool()
def tool2() -> str:
    return "b"

# THEN run server
mcp.run(transport="streamable-http")
```

**Check 4: Request Format**
```bash
# Test tools/list directly
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

### 5. Tool Calls Fail

#### Symptom: tools/call returns errors or wrong results

**Check 1: Input Schema Validation**
```python
# Tool expects certain parameters
@mcp.tool()
def search(query: str, limit: int = 10) -> str:
    pass

# Call with correct types
{
  "name": "search",
  "arguments": {
    "query": "test",     # String ✓
    "limit": 5           # Int ✓
  }
}

# Common errors:
{
  "arguments": {
    "query": 123,        # Wrong type
    "limit": "5"         # Should be int, not string
  }
}
```

**Check 2: Runtime Errors**
```python
# Add error handling in tools
@mcp.tool()
def risky_operation(file_path: str) -> str:
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        # Return error via isError flag
        return json.dumps({
            "error": f"File not found: {file_path}",
            "isError": True
        })
    except Exception as e:
        logging.error(f"Tool error: {e}")
        raise  # Let framework handle
```

**Check 3: Timeout**
```python
# For long-running tools
from mcp.server.fastmcp import Context
import asyncio

@mcp.tool()
async def slow_tool(ctx: Context) -> str:
    await ctx.report_progress(0.0, message="Starting...")

    await asyncio.sleep(5)  # Long operation

    await ctx.report_progress(1.0, message="Done")
    return "result"
```

**Check 4: Permissions**
```python
# Tool might lack permissions
@mcp.tool()
def read_system_file() -> str:
    # Check permissions before operation
    import os
    if not os.access('/etc/passwd', os.R_OK):
        return json.dumps({
            "error": "Permission denied",
            "isError": True
        })
```

### 6. SSE Stream Issues

#### Symptom: Server-Sent Events not working

**Check 1: Client Accept Header**
```bash
# Client MUST include text/event-stream
curl -H "Accept: text/event-stream" \
     http://localhost:8000/mcp
```

**Check 2: Server Content-Type**
```python
# Verify server sends correct header
# FastMCP handles this automatically

# For custom implementation:
from starlette.responses import StreamingResponse

async def event_stream():
    yield "event: message\ndata: {...}\n\n"

return StreamingResponse(
    event_stream(),
    media_type="text/event-stream"
)
```

**Check 3: Buffering**
```python
# Disable buffering for SSE
async def event_stream():
    yield "event: message\n"
    yield f"data: {json.dumps(message)}\n\n"

    # Flush immediately (framework-dependent)
    # FastMCP handles this
```

**Check 4: Proxy Buffering**
```nginx
# nginx config for SSE
location /mcp {
    proxy_pass http://localhost:8000;
    proxy_buffering off;  # Critical for SSE
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
}
```

### 7. Session Management Problems

#### Symptom: Session not persisting across requests

**Check 1: Mcp-Session-Id Header**
```bash
# Verify server sends session ID
curl -v http://localhost:8000/mcp

# Look for:
< Mcp-Session-Id: uuid-here

# Client must echo it back:
curl -H "Mcp-Session-Id: uuid-here" \
     http://localhost:8000/mcp
```

**Check 2: CORS Configuration**
```python
# Must expose Mcp-Session-Id
from starlette.middleware.cors import CORSMiddleware

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    expose_headers=["Mcp-Session-Id"],  # Critical!
)
```

**Check 3: Stateless Mode**
```python
# Check if server is in stateless mode
mcp = FastMCP("Server", stateless_http=True)
# In stateless mode, no session persistence

# Use stateful mode for sessions:
mcp = FastMCP("Server", stateless_http=False)
```

**Check 4: Session Storage**
```python
# For production, configure session backend
# (FastMCP uses in-memory by default)

# For distributed systems, use Redis/database
# (Implementation depends on framework)
```

### 8. Authentication Failures

#### Symptom: 401/403 errors

**Check 1: Token Format**
```bash
# Verify Bearer token format
curl -H "Authorization: Bearer your-token-here" \
     http://localhost:8000/mcp
```

**Check 2: Token Verification**
```python
# Add logging to verifier
class MyTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        logging.debug(f"Verifying token: {token[:10]}...")

        # Your verification logic
        if valid:
            return AccessToken(...)

        logging.warning("Token verification failed")
        return None
```

**Check 3: Required Scopes**
```python
# Check auth settings
mcp = FastMCP(
    "Server",
    token_verifier=verifier,
    auth=AuthSettings(
        required_scopes=["user", "read"]  # Client must have these
    )
)
```

**Check 4: Token Expiration**
```python
# Check if token expired
from datetime import datetime

access_token = AccessToken(
    token=token,
    scopes=scopes,
    expires_at=datetime(2024, 12, 31)  # Check this
)
```

### 9. Performance Issues

#### Symptom: Slow responses or timeouts

**Check 1: Tool Performance**
```python
# Add timing to tools
import time

@mcp.tool()
def slow_tool() -> str:
    start = time.time()

    # Operation
    result = expensive_operation()

    duration = time.time() - start
    logging.info(f"Tool took {duration:.2f}s")

    return result
```

**Check 2: Database Queries**
```python
# Use connection pooling
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://...",
    pool_size=10,
    max_overflow=20
)

# Add query timeouts
session.execute(
    text("SELECT ..."),
    timeout=5.0
)
```

**Check 3: Concurrent Requests**
```python
# FastMCP uses asyncio - check for blocking calls
@mcp.tool()
async def good_tool() -> str:
    # Use async I/O
    async with httpx.AsyncClient() as client:
        response = await client.get(...)
    return response.text

@mcp.tool()
def bad_tool() -> str:
    # Blocking I/O blocks entire server!
    import requests
    response = requests.get(...)  # BAD
    return response.text
```

**Check 4: Payload Size**
```python
# Paginate large results
@mcp.tool()
def get_data(limit: int = 100, offset: int = 0) -> str:
    # Return chunks instead of all data
    items = query_db().limit(limit).offset(offset)
    return json.dumps(items)
```

## Diagnostic Tools

### 1. MCP Protocol Validator

```python
# scripts/validate_mcp_protocol.py
import json

def validate_message(message: str):
    """Validate JSON-RPC message"""
    try:
        msg = json.loads(message)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    # Check required fields
    if msg.get("jsonrpc") != "2.0":
        return "Missing or invalid jsonrpc field"

    # Check message type
    has_id = "id" in msg
    has_method = "method" in msg
    has_result = "result" in msg
    has_error = "error" in msg

    if has_method and has_id:
        return "Valid Request"
    elif has_method and not has_id:
        return "Valid Notification"
    elif has_id and (has_result or has_error):
        return "Valid Response"
    else:
        return "Invalid message structure"
```

### 2. Connection Tester

```bash
# Test basic connectivity
curl -v -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"ping"}'

# Test SSE
curl -v -N -H "Accept: text/event-stream" \
  http://localhost:8000/mcp
```

### 3. Log Analysis

```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
python server.py

# Common patterns to grep for:
grep "ERROR" server.log
grep "tool/call" server.log
grep "initialize" server.log
```

## Emergency Fixes

### Quick Reset

```bash
# Kill all MCP servers
pkill -f "mcp"

# Clear session state (if using file-based storage)
rm -rf /tmp/mcp-sessions/*

# Restart with clean state
python server.py
```

### Rollback Protocol Version

```python
# If new version broken, use previous
{
  "protocolVersion": "2024-11-05"  # Instead of 2025-03-26
}
```

### Minimal Test Server

```python
# Simplest possible MCP server for testing
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TestServer")

@mcp.tool()
def ping() -> str:
    return "pong"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## Getting Help

1. **Check server logs** - Most issues show up in logs
2. **Test with curl** - Isolate client vs server issues
3. **Minimal reproduction** - Simplify to smallest failing case
4. **Protocol validation** - Ensure JSON-RPC compliance
5. **Compare working example** - Use FastMCP examples as reference
