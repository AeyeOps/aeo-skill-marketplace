---
name: mcp-architect-designer
description: Design and deploy Model Context Protocol servers with deep knowledge of the JSON-RPC 2.0 spec, transport mechanisms, and protocol lifecycle. Covers FastMCP framework patterns, production hardening, and diagnostic techniques for connectivity failures. Engage when architecting MCP integrations, building custom servers, or debugging protocol-level issues.
---

# MCP Architect Designer

## Overview

This skill provides expert guidance for Model Context Protocol (MCP) architecture, design, implementation, and troubleshooting. Combines deep knowledge of the MCP specification (JSON-RPC 2.0, protocol lifecycle, transport mechanisms) with practical expertise in building production-ready MCP servers using the FastMCP framework. Includes comprehensive troubleshooting capabilities for diagnosing and fixing MCP servers that won't start, can't connect, or fail during operation.

## When to Use This Skill

This skill applies to tasks involving:

- **Building New MCP Servers** - Creating MCP servers from scratch or using templates
- **Protocol Compliance** - Ensuring correct JSON-RPC 2.0 implementation and MCP specification adherence
- **Framework Selection** - Choosing between FastMCP, custom implementations, or evaluating MCP frameworks
- **Transport Configuration** - Setting up HTTP/SSE, stdio, or custom transport layers
- **Troubleshooting MCP Issues** - Diagnosing why servers won't start, connections fail, or protocol handshakes break
- **Authentication & Security** - Implementing OAuth 2.1, JWT validation, or custom authorization patterns
- **Multi-Client Support** - Building servers that work with both OpenAI and Claude (Anthropic) clients
- **OWASP Security Compliance** - Meeting security standards for OAuth 2.1 and MCP deployments
- **Performance Optimization** - Improving tool execution speed, resource management, and concurrent request handling
- **Production Deployment** - Deploying MCP servers with proper security, monitoring, Docker, and reverse proxy configuration
- **Architecture Design** - Designing dual REST+MCP interfaces or multi-server MCP architectures

## Quick Reference

**Create New Server:**
```bash
python scripts/init_mcp_server.py my-server
cd my-server
pip install -r requirements.txt
python server.py
```

**Test Connection:**
```bash
python scripts/test_mcp_connection.py http://localhost:8000/mcp
```

**Basic Server Pattern:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
def my_tool(param: str) -> str:
    return f"Result: {param}"

mcp.run(transport="streamable-http")
```

**Tool with Error Handling:**
```python
@mcp.tool()
def safe_operation(input: str) -> str:
    try:
        return process(input)
    except ValueError as e:
        return json.dumps({"error": str(e), "isError": True})
```

**Deep Dive References:**
- Protocol questions → [references/mcp-protocol-spec.md](references/mcp-protocol-spec.md)
- Transport issues → [references/transport-patterns.md](references/transport-patterns.md)
- Framework usage → [references/fastmcp-framework.md](references/fastmcp-framework.md)
- Debugging → [references/troubleshooting-guide.md](references/troubleshooting-guide.md)
- Multi-client auth → [references/dual-client-authentication.md](references/dual-client-authentication.md)
- Production deployment → [references/deployment-patterns.md](references/deployment-patterns.md)

## Core Capabilities

### 1. MCP Protocol Specification Expertise

Reference `references/mcp-protocol-spec.md` for complete protocol details.

**Key Protocol Concepts:**
- **JSON-RPC 2.0 Foundation** - All MCP communication uses JSON-RPC 2.0 message format
- **Message Types** - Requests (with `id`), Responses (matching `id`), Notifications (no `id`)
- **Connection Lifecycle** - Initialize → Initialized notification → Normal operation → Shutdown
- **Capabilities** - Tools, resources, prompts, subscriptions
- **Error Handling** - Standard codes (-32700 to -32603) and MCP-specific codes
- **Version Negotiation** - Protocol version compatibility between client and server

**Critical Requirements:**
```json
// Request MUST have unique id
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

// Response MUST match request id
{"jsonrpc": "2.0", "id": 1, "result": {...}}

// Notification MUST NOT have id
{"jsonrpc": "2.0", "method": "notifications/progress", "params": {...}}
```

### 2. Transport Pattern Implementation

Reference `references/transport-patterns.md` for transport-specific details.

**Transport Selection Guide:**
| Use Case | Transport | Reason |
|----------|-----------|--------|
| Web application | Streamable HTTP | Browser-compatible, SSE support |
| Local CLI tool | stdio | Simple process model |
| Cloud service | Streamable HTTP | Standard HTTP infrastructure |
| IDE plugin | stdio | Process isolation |

**Streamable HTTP Critical Points:**
- Single endpoint (`/mcp`) for both POST (client→server) and GET (SSE server→client)
- Include `Mcp-Session-Id` header for session management
- Expose `Mcp-Session-Id` in CORS `expose_headers`
- Validate `Origin` header for security
- Bind to localhost (127.0.0.1) for local servers

**stdio Critical Points:**
- Newline-delimited JSON-RPC messages
- Server reads from stdin, writes to stdout
- Logs go to stderr (never stdout)
- UTF-8 encoding required

### 3. FastMCP Framework Patterns

Reference `references/fastmcp-framework.md` for comprehensive implementation examples.

**Basic Server Pattern:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description shown to LLM."""
    return f"Result: {param}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**Key Framework Features:**
- **Automatic Schema Generation** - Python type hints → JSON Schema
- **Async Support** - Built on asyncio for non-blocking I/O
- **Progress Reporting** - `Context.report_progress()` for long-running tools
- **Structured Output** - Pydantic models for type-safe responses
- **Lifespan Management** - Initialize/cleanup database connections, caches
- **OAuth 2.1 Support** - Built-in token verification and protected endpoints
- **ASGI Integration** - Mount to Starlette/FastAPI applications

### 4. Troubleshooting Expertise

Reference `references/troubleshooting-guide.md` for systematic diagnostic procedures.

**Quick Triage Checklist:**
1. ✓ Is the server process running? (Check with `ps` or Task Manager)
2. ✓ Can you connect to the endpoint? (Test with `curl`)
3. ✓ Does initialize handshake complete? (Check server logs)
4. ✓ Are tools/resources discoverable? (Call `tools/list`)
5. ✓ Do tool calls execute successfully? (Call `tools/call`)

**Common Issue Patterns:**
- **Server Won't Start** → Check Python version (3.10+), missing dependencies, port conflicts
- **Connection Refused** → Verify firewall rules, binding address (0.0.0.0 vs 127.0.0.1)
- **Initialize Fails** → Protocol version mismatch, invalid parameters in initialize request
- **Tools Not Discovered** → Missing `@mcp.tool()` decorator, server capabilities not advertised
- **Tool Calls Fail** → Input schema mismatch, runtime errors, permission issues
- **SSE Not Working** → Missing `Accept: text/event-stream` header, CORS misconfiguration
- **Session Not Persisting** → `Mcp-Session-Id` not in CORS `expose_headers`

For systematic testing, run the diagnostic script:
```bash
python scripts/test_mcp_connection.py http://localhost:8000/mcp
```

## Development Workflow

### Starting a New MCP Server

**Option 1: Quick Start with Template**
```bash
# Create basic server project
python scripts/init_mcp_server.py my-server

# Create OAuth-protected server
python scripts/init_mcp_server.py my-server --template oauth

# Custom output directory
python scripts/init_mcp_server.py my-server --output /path/to/projects
```

Generates complete project structure:
- `server.py` - FastMCP server with example tools
- `requirements.txt` - Python dependencies
- `Dockerfile` and `docker-compose.yml` - Container deployment
- `README.md` - Documentation
- `tests/` - Unit test examples

**Option 2: Manual Setup**
1. Install dependencies: `pip install mcp httpx pydantic`
2. Create `server.py` with FastMCP initialization
3. Define tools using `@mcp.tool()` decorator
4. Add resources with `@mcp.resource()` decorator
5. Run with `mcp.run(transport="streamable-http")`

### Tool and Resource Design

For detailed tool and resource design patterns, see `references/fastmcp-framework.md` which covers:
- Type hints and automatic schema generation
- Pydantic models for complex inputs
- Error handling patterns (business logic vs framework errors)
- Static and dynamic resources
- URI template patterns
- Binary resources with MIME types

### Security Best Practices

**IMPORTANT:** For production servers supporting multiple clients (OpenAI, Claude), refer to `references/dual-client-authentication.md` for comprehensive guidance on authentication patterns, OWASP compliance, and recommended architectures.

**1. OAuth 2.1 Authentication:**
```python
from pydantic import AnyHttpUrl
from mcp.server.auth.provider import TokenVerifier, AccessToken
from mcp.server.auth.settings import AuthSettings

class ProductionTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        # Verify JWT signature with public key
        # Check expiration timestamp
        # Validate required scopes
        # Validate audience claim (prevents confused deputy attacks)
        if valid:
            return AccessToken(token=token, scopes=["user"], expires_at=None)
        return None

mcp = FastMCP(
    "SecureServer",
    token_verifier=ProductionTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("http://localhost:8000"),
        required_scopes=["user"]
    )
)
```

**2. Input Validation:** Use Pydantic models with validators to prevent injection attacks and path traversal.

**3. CORS Configuration:** Configure with specific allowed origins, expose `Mcp-Session-Id` header for session management.

## Production Deployment

For production deployment patterns, see `references/deployment-patterns.md` which covers:
- Docker and Kubernetes deployment
- Reverse proxy configuration (nginx, Caddy)
- Monitoring and observability (health checks, metrics, structured logging)
- Environment configuration
- Security hardening and TLS configuration
- Deployment checklists

## Architecture Patterns

### Dual-Interface (REST + MCP)

When building systems with both traditional REST API and MCP interface:

```python
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

# REST API
rest_api = FastAPI()

@rest_api.get("/api/data/{id}")
def get_data_rest(id: str):
    return get_data_from_db(id)  # Shared business logic

# MCP Interface
mcp = FastMCP("DualInterface")

@mcp.tool()
def get_data(id: str) -> str:
    """Get data by ID (MCP tool)."""
    data = get_data_from_db(id)  # Same business logic
    return json.dumps(data)

# Mount both
from starlette.applications import Starlette
from starlette.routing import Mount

app = Starlette(routes=[
    Mount("/api", rest_api),
    Mount("/mcp", mcp.streamable_http_app())
])
```

### Multi-Server Architecture

For complex systems with multiple specialized servers:

```python
# weather_server.py
weather = FastMCP("WeatherService")

@weather.tool()
def get_weather(city: str) -> dict:
    return {"city": city, "temp": 22}

# analytics_server.py
analytics = FastMCP("AnalyticsService")

@analytics.tool()
def get_metrics() -> dict:
    return {"users": 1000}

# Combined app
app = Starlette(routes=[
    Mount("/weather", weather.streamable_http_app()),
    Mount("/analytics", analytics.streamable_http_app())
])
```

### Multi-Client Architecture (OpenAI + Claude)

For servers supporting both OpenAI and Claude clients, use separate endpoints with shared backend logic due to:
- Different token audience validation requirements (MCP spec)
- RFC 8707 resource parameter handling differences
- Distinct discovery metadata needs
- OWASP security compliance requirements

See `references/dual-client-authentication.md` for:
- Complete authentication flow comparisons
- Production-ready implementation examples
- Token verifier patterns (strict vs flexible)
- OWASP security compliance details
- Why single endpoint approach doesn't work

## Bundled Resources

### scripts/

**`test_mcp_connection.py`** - Diagnostic tool for testing MCP server connectivity and protocol compliance.

Usage:
```bash
# Test HTTP MCP server
python scripts/test_mcp_connection.py http://localhost:8000/mcp

# Test with verbose output
python scripts/test_mcp_connection.py http://localhost:8000/mcp --verbose
```

Systematic checks:
1. Basic connectivity (server reachable)
2. Initialize handshake (protocol version negotiation)
3. Tools discovery (`tools/list`)
4. Session management (`Mcp-Session-Id` header)
5. SSE support (Server-Sent Events)

**`init_mcp_server.py`** - Project generator for new MCP servers.

Usage:
```bash
# Create basic FastMCP server
python scripts/init_mcp_server.py my-server

# Create OAuth-protected server
python scripts/init_mcp_server.py my-server --template oauth

# Custom output directory
python scripts/init_mcp_server.py my-server --output /path/to/projects
```

Generates complete project structure:
- `server.py` with FastMCP initialization and example tools
- `requirements.txt` with Python dependencies
- `Dockerfile` and `docker-compose.yml` for containerization
- `README.md` with documentation and usage instructions
- `tests/` directory with unit test examples
- `.gitignore` for Python projects

### references/

**`mcp-protocol-spec.md`** - Complete MCP protocol specification.

Contents:
- JSON-RPC 2.0 message formats (requests, responses, notifications)
- Connection lifecycle (initialize → initialized → normal operation)
- Core capabilities (tools, resources, prompts, subscriptions)
- Standard error codes and custom MCP codes
- Protocol version negotiation patterns
- Best practices for tool/resource design
- Testing checklist

**`transport-patterns.md`** - Comprehensive transport mechanism guide.

Contents:
- **Streamable HTTP** - Single endpoint, SSE support, session management
- **stdio** - Process-based IPC for local tools
- **HTTP with SSE (legacy)** - Separate endpoints pattern
- Security considerations (Origin validation, CORS, authentication)
- Transport selection guide by use case
- Debugging techniques for each transport
- Performance considerations

**`fastmcp-framework.md`** - In-depth FastMCP Python framework guide.

Contents:
- Server initialization patterns (stateful, stateless, custom paths)
- Tool design (sync, async, progress reporting, structured output)
- Resource patterns (static, dynamic, binary, subscriptions)
- Prompts and templates
- Authentication (OAuth 2.1, JWT, token verification)
- Lifespan management (startup/shutdown hooks)
- ASGI mounting (Starlette, FastAPI integration)
- CORS configuration
- Performance optimization
- Testing strategies
- Deployment patterns

**`troubleshooting-guide.md`** - Systematic troubleshooting procedures.

Contents:
- **Quick Triage Checklist** - 5-step diagnostic process
- **Common Issues** - Server won't start, connection refused, initialize fails, tools not discovered, tool calls fail, SSE issues, session problems, auth failures, performance issues
- **Diagnostic Tools** - Protocol validators, connection testers, log analysis
- **Emergency Fixes** - Quick resets, rollback procedures, minimal test servers
- **Detailed Solutions** - Step-by-step fixes for each issue category

**`dual-client-authentication.md`** - Multi-client authentication patterns.

Contents:
- **OpenAI vs Claude Authentication** - How each client handles OAuth 2.1 differently
- **Separate Endpoints Architecture** - Recommended pattern for production deployments
- **OWASP Security Compliance** - Complete security checklist and implementation
- **Token Validation Patterns** - Strict vs flexible token verifiers
- **Why Single Endpoint Doesn't Work** - Audience validation and resource parameter conflicts
- **Production Deployment** - Docker, nginx, monitoring, and testing strategies
- **Complete Code Examples** - Production-ready implementations with security best practices

**`deployment-patterns.md`** - Production deployment patterns.

Contents:
- **Docker Deployment** - Dockerfile, docker-compose, multi-stage builds
- **Kubernetes** - Deployment manifests, services, ingress configuration
- **Reverse Proxy** - nginx and Caddy configuration for SSE support
- **Monitoring** - Health checks, Prometheus metrics, structured logging
- **Environment Configuration** - Environment variables and YAML configuration
- **Security Hardening** - TLS configuration, rate limiting, deployment checklists

## Quick Reference

**Create New Server:**
```bash
python scripts/init_mcp_server.py my-server
cd my-server
pip install -r requirements.txt
python server.py
```

**Test Connection:**
```bash
python scripts/test_mcp_connection.py http://localhost:8000/mcp
```

**Basic Server Pattern:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
def my_tool(param: str) -> str:
    return f"Result: {param}"

mcp.run(transport="streamable-http")
```

**Tool with Error Handling:**
```python
@mcp.tool()
def safe_operation(input: str) -> str:
    try:
        return process(input)
    except ValueError as e:
        return json.dumps({"error": str(e), "isError": True})
```

**Reference Documentation:**
- Protocol questions → Read `references/mcp-protocol-spec.md`
- Transport issues → Read `references/transport-patterns.md`
- Framework usage → Read `references/fastmcp-framework.md`
- Debugging → Read `references/troubleshooting-guide.md`
- Multi-client authentication → Read `references/dual-client-authentication.md`
- Production deployment → Read `references/deployment-patterns.md`
