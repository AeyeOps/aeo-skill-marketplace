# MCP Transport Patterns

## Overview

MCP supports multiple transport mechanisms for client-server communication. All transports must preserve JSON-RPC 2.0 message format and lifecycle requirements.

## Supported Transports

1. **Streamable HTTP** - HTTP POST/GET with optional SSE (recommended for web)
2. **stdio** - Standard input/output (recommended for local processes)
3. **HTTP with SSE** - Separate SSE and POST endpoints (legacy pattern)
4. **Custom** - Any bidirectional transport preserving JSON-RPC

## 1. Streamable HTTP Transport (Recommended)

### Overview

Single HTTP endpoint supporting both POST (client→server) and GET (server→client via SSE).

**Advantages:**
- Single endpoint simplifies configuration
- Built-in session management via `Mcp-Session-Id` header
- Optional SSE for server-initiated messages
- Works with standard HTTP infrastructure

**Endpoint:** `/mcp` (customizable)

### Request Flow

#### Client Sends Message (POST)

```http
POST /mcp HTTP/1.1
Host: example.com
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

#### Server Response Options

**Option A: Immediate JSON Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"tools": [...]}
}
```

**Option B: SSE Stream for Multiple Messages**
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408

event: message
data: {"jsonrpc": "2.0", "id": 1, "result": {...}}

event: message
data: {"jsonrpc": "2.0", "method": "notifications/progress", "params": {...}}
```

#### Client Listens for Server Messages (GET)

```http
GET /mcp HTTP/1.1
Host: example.com
Accept: text/event-stream
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408
```

**Server SSE Stream:**
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

event: message
data: {"jsonrpc": "2.0", "method": "server/notification", "params": {...}}
```

### Session Management

**Initial Request:**
Server may create session and return header:
```http
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408
```

**Subsequent Requests:**
Client includes session ID:
```http
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408
```

**Session Recovery:**
Client can resume interrupted SSE stream using `Last-Event-ID`:
```http
GET /mcp HTTP/1.1
Last-Event-ID: 42
Mcp-Session-Id: 1868a90c-11e7-4e32-a870-055188d83408
```

### Python FastMCP Implementation

```python
from mcp.server.fastmcp import FastMCP

# Stateful server (maintains sessions)
mcp = FastMCP("ServerName")

@mcp.tool()
def get_data() -> str:
    return "data"

# Run with streamable-http
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # Serves at http://localhost:8000/mcp
```

**Stateless Mode:**
```python
# No session persistence, faster for simple use cases
mcp = FastMCP("StatelessServer", stateless_http=True)
```

**JSON-Only Mode (No SSE):**
```python
# Always return JSON, never SSE stream
mcp = FastMCP("JsonServer", stateless_http=True, json_response=True)
```

### Mounting to Existing App

```python
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

# Mount MCP to existing ASGI app
app = Starlette(
    routes=[
        Mount("/api/mcp", app=mcp.streamable_http_app()),
    ]
)

# Add CORS for browser clients
app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    expose_headers=["Mcp-Session-Id"],  # Critical for session management
)
```

### Security Considerations

1. **Origin Validation:**
```python
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = Starlette(
    middleware=[
        Middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "*.example.com"])
    ]
)
```

2. **Localhost Binding:**
```python
# For local development only
mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

3. **Authentication:**
```python
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings

mcp = FastMCP(
    "SecureServer",
    token_verifier=MyTokenVerifier(),
    auth=AuthSettings(
        issuer_url="https://auth.example.com",
        resource_server_url="http://localhost:8000"
    )
)
```

## 2. stdio Transport

### Overview

Process-based communication via standard input/output. Client launches server as subprocess.

**Advantages:**
- Simple local IPC
- No network configuration
- Natural process isolation
- Built-in lifecycle management

**Use Cases:**
- Local tools and utilities
- IDE integrations
- CLI applications

### Message Format

Messages are newline-delimited JSON-RPC:
```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}\n
{"jsonrpc":"2.0","id":1,"result":{...}}\n
```

### Python FastMCP Implementation

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LocalServer")

@mcp.tool()
def local_tool() -> str:
    return "result"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client Usage

```python
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    # Launch server as subprocess
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("local_tool", {})
            print(result)

asyncio.run(main())
```

### Requirements

1. **Server MUST:**
   - Read from stdin
   - Write to stdout
   - Write logs to stderr (not stdout)
   - Parse newline-delimited JSON

2. **Client MUST:**
   - Write to server's stdin
   - Read from server's stdout
   - Handle stderr separately for logs

3. **Messages MUST:**
   - Be valid JSON-RPC 2.0
   - End with newline character
   - Be UTF-8 encoded

### Error Handling

**Logging (stderr):**
```python
import sys
sys.stderr.write("Debug: Processing request\n")
```

**Protocol Errors (stdout):**
```json
{"jsonrpc":"2.0","id":1,"error":{"code":-32600,"message":"Invalid Request"}}\n
```

## 3. HTTP with SSE Transport (Legacy)

### Overview

Separate endpoints for client→server (POST) and server→client (SSE).

**Architecture:**
- SSE Endpoint: `GET /` for server messages
- POST Endpoint: Dynamic, provided via SSE `endpoint` event

### Connection Flow

1. **Client connects to SSE endpoint:**
```http
GET / HTTP/1.1
Accept: text/event-stream
```

2. **Server sends endpoint URI:**
```
event: endpoint
data: http://localhost:8080/message

```

3. **Client sends messages to POST endpoint:**
```http
POST /message HTTP/1.1
Content-Type: application/json

{"jsonrpc":"2.0","method":"tools/list","id":1}
```

4. **Server responds via SSE:**
```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{...}}

```

### Why Legacy?

- More complex (two endpoints)
- No built-in session management
- Harder to deploy behind proxies
- **Prefer Streamable HTTP** for new implementations

## 4. Custom Transports

### Requirements

Custom transports MUST:
1. Preserve JSON-RPC 2.0 message format
2. Support bidirectional communication
3. Maintain connection lifecycle (initialize → normal → shutdown)
4. Document connection establishment patterns

### Examples

**WebSocket:**
```javascript
const ws = new WebSocket('ws://localhost:8000/mcp');
ws.onopen = () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {...}
  }));
};
```

**gRPC:**
```protobuf
service MCP {
  rpc Call(stream JsonRpcMessage) returns (stream JsonRpcMessage);
}
```

## Transport Selection Guide

| Use Case | Recommended Transport | Reason |
|----------|----------------------|--------|
| Web application | Streamable HTTP | Browser-compatible, SSE support |
| Local CLI tool | stdio | Simple process model |
| Desktop IDE plugin | stdio | Process isolation |
| Cloud service | Streamable HTTP | HTTP infrastructure |
| Real-time dashboard | Streamable HTTP (SSE) | Server-push notifications |
| Embedded device | Custom (MQTT/CoAP) | Resource constraints |

## Performance Considerations

### Streamable HTTP

**Advantages:**
- Connection pooling
- HTTP/2 multiplexing
- CDN compatibility

**Considerations:**
- SSE keeps connection open (use for active sessions only)
- Consider timeouts for idle sessions

### stdio

**Advantages:**
- Zero network overhead
- No port conflicts

**Considerations:**
- One client per process
- Process startup overhead

## Debugging Transport Issues

### Common Problems

**1. SSE Not Working:**
```bash
# Check Accept header
curl -H "Accept: text/event-stream" http://localhost:8000/mcp

# Verify Content-Type in response
```

**2. Session Not Persisting:**
```bash
# Check for Mcp-Session-Id header
curl -v http://localhost:8000/mcp

# Verify expose_headers in CORS
```

**3. stdio Messages Corrupted:**
```python
# Ensure newline-delimited JSON
import json
message = json.dumps({"jsonrpc": "2.0", ...}) + "\n"
sys.stdout.write(message)
sys.stdout.flush()  # Critical!
```

**4. CORS Errors:**
```python
# Must expose Mcp-Session-Id
CORSMiddleware(
    app,
    expose_headers=["Mcp-Session-Id"]
)
```

## Testing Transport Implementation

### Streamable HTTP

```python
import httpx

# Test POST
response = httpx.post(
    "http://localhost:8000/mcp",
    json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    headers={"Accept": "application/json"}
)
assert response.status_code == 200

# Test SSE
async with httpx.AsyncClient() as client:
    async with client.stream(
        "GET",
        "http://localhost:8000/mcp",
        headers={"Accept": "text/event-stream"}
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                message = json.loads(line[6:])
```

### stdio

```python
import subprocess
import json

proc = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Send initialize
request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {...}}) + "\n"
proc.stdin.write(request.encode())
proc.stdin.flush()

# Read response
response = proc.stdout.readline().decode()
result = json.loads(response)
assert result["jsonrpc"] == "2.0"
```
