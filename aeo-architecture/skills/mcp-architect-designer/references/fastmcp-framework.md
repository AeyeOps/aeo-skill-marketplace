# FastMCP Framework Guide

## Overview

FastMCP is the official Python framework for building Model Context Protocol servers. It provides high-level abstractions that eliminate boilerplate while maintaining full protocol compliance.

## Core Concepts

### 1. Server Initialization

```python
from mcp.server.fastmcp import FastMCP

# Basic server
mcp = FastMCP("MyServer")

# Stateless server (no session persistence)
mcp = FastMCP("StatelessServer", stateless_http=True)

# JSON-only responses (no SSE)
mcp = FastMCP("JsonServer", stateless_http=True, json_response=True)

# Custom MCP endpoint path
mcp = FastMCP("CustomPath", streamable_http_path="/api/v1/mcp")
```

### 2. Tools

Tools are functions that LLMs can invoke.

#### Basic Tool

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

**Generated Schema:**
```json
{
  "name": "add",
  "description": "Add two numbers.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": {"type": "integer"},
      "b": {"type": "integer"}
    },
    "required": ["a", "b"]
  }
}
```

#### Async Tools

```python
@mcp.tool()
async def fetch_data(url: str) -> str:
    """Fetch data from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

#### Tools with Optional Parameters

```python
@mcp.tool()
def search(
    query: str,
    limit: int = 10,
    include_metadata: bool = False
) -> str:
    """
    Search documents.

    Args:
        query: Search query text
        limit: Maximum results to return (default: 10)
        include_metadata: Include document metadata (default: False)
    """
    # Implementation
    results = perform_search(query, limit)
    return json.dumps(results)
```

#### Tools with Context

```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

@mcp.tool()
async def long_task(
    task_name: str,
    ctx: Context[ServerSession, None]
) -> str:
    """Execute long-running task with progress updates."""

    # Log messages
    await ctx.info(f"Starting: {task_name}")
    await ctx.debug("Initializing...")

    # Report progress
    for i in range(5):
        progress = (i + 1) / 5
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"Step {i + 1}/5"
        )

    return f"Completed: {task_name}"
```

#### Structured Output Tools

```python
from pydantic import BaseModel, Field
from typing import TypedDict

# Using Pydantic model
class WeatherResult(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    conditions: str = Field(description="Weather conditions")
    humidity: int = Field(ge=0, le=100, description="Humidity percentage")

@mcp.tool()
def get_weather(city: str) -> WeatherResult:
    """Get weather for a city."""
    # Return Pydantic model - auto-validates
    return WeatherResult(
        temperature=22.5,
        conditions="Partly cloudy",
        humidity=65
    )

# Using TypedDict
class SearchResult(TypedDict):
    query: str
    count: int
    results: list[str]

@mcp.tool()
def search_docs(query: str) -> SearchResult:
    """Search documentation."""
    return {
        "query": query,
        "count": 3,
        "results": ["doc1", "doc2", "doc3"]
    }
```

### 3. Resources

Resources are data that can be read by LLMs.

#### Static Resources

```python
@mcp.resource("config://settings")
def get_settings() -> str:
    """Get application settings."""
    return json.dumps({
        "theme": "dark",
        "language": "en"
    })
```

#### Dynamic Resources with URI Templates

```python
@mcp.resource("file://documents/{doc_id}")
def read_document(doc_id: str) -> str:
    """Read document by ID."""
    # Extract parameter from URI
    content = load_document(doc_id)
    return content

# Multiple parameters
@mcp.resource("data://{category}/{item_id}")
def get_data(category: str, item_id: str) -> str:
    """Get data by category and item."""
    return f"Data for {category}/{item_id}"
```

#### Binary Resources

```python
@mcp.resource("image://photos/{photo_id}", mimeType="image/png")
def get_photo(photo_id: str) -> bytes:
    """Get photo as PNG."""
    return load_photo_bytes(photo_id)
```

#### Resource Subscriptions

```python
# Resources can notify clients of updates
# FastMCP handles subscription management automatically

@mcp.resource("live://metrics")
def get_metrics() -> str:
    """Get current metrics (supports subscriptions)."""
    return json.dumps(current_metrics())

# Notify subscribers when data changes
async def update_metrics():
    # Update metrics
    new_metrics = calculate_metrics()

    # FastMCP will notify all subscribers
    # (Framework handles notification automatically)
```

### 4. Prompts

Prompts are templates for LLM interactions.

```python
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate greeting prompt."""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting"
    }
    return f"{styles.get(style, styles['friendly'])} for {name}."

# Multi-message prompts
from mcp.types import TextContent, ImageContent

@mcp.prompt()
def analyze_with_context(topic: str, image_url: str) -> list:
    """Generate analysis prompt with image."""
    return [
        TextContent(
            type="text",
            text=f"Analyze the following image in context of: {topic}"
        ),
        ImageContent(
            type="image",
            url=image_url
        )
    ]
```

## Advanced Patterns

### 1. Lifespan Management

Manage resources across server lifecycle.

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

# Define application context
@dataclass
class AppContext:
    db: Database
    cache: Redis

# Lifespan handler
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle."""

    # Startup
    db = await Database.connect()
    cache = await Redis.connect()

    try:
        yield AppContext(db=db, cache=cache)
    finally:
        # Shutdown
        await db.disconnect()
        await cache.disconnect()

# Create server with lifespan
mcp = FastMCP("MyApp", lifespan=app_lifespan)

# Access lifespan context in tools
@mcp.tool()
def query_db(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> str:
    """Execute database query."""
    db = ctx.request_context.lifespan_context.db
    result = db.query(sql)
    return json.dumps(result)
```

### 2. Authentication

**IMPORTANT:** For production servers supporting multiple clients (OpenAI, Claude), refer to `dual-client-authentication.md` for comprehensive patterns. The examples below show basic OAuth 2.1 implementation.

#### OAuth 2.1 Resource Server (Basic Pattern)

```python
from pydantic import AnyHttpUrl
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
import jwt
from typing import Optional

class ProductionTokenVerifier(TokenVerifier):
    """
    Production-ready token verifier with OWASP security best practices.
    """

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        try:
            # 1. Fetch JWKS from authorization server
            jwks = await self.fetch_jwks("https://auth.example.com/jwks")

            # 2. Verify JWT signature and claims
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience="https://mcp.example.com",  # Validate audience
                issuer="https://auth.example.com"    # Validate issuer
            )

            # 3. Check required scopes (least privilege principle)
            required_scopes = {"user", "read"}
            token_scopes = set(claims.get("scope", "").split())
            if not required_scopes.issubset(token_scopes):
                return None

            # 4. Optional: Check token not blacklisted
            if await self.is_blacklisted(claims.get("jti")):
                return None

            return AccessToken(
                token=token,
                scopes=list(token_scopes),
                expires_at=claims.get("exp")
            )

        except jwt.InvalidTokenError:
            return None

    async def fetch_jwks(self, url: str):
        """Fetch and cache JWKS."""
        # Implementation with caching
        pass

    async def is_blacklisted(self, jti: str) -> bool:
        """Check token blacklist."""
        # Implementation with Redis/database
        pass

# Create protected server
mcp = FastMCP(
    "ProtectedServer",
    token_verifier=ProductionTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("https://mcp.example.com"),
        required_scopes=["user"]
    )
)

@mcp.tool()
def get_user_data() -> dict:
    """Get user data (requires authentication)."""
    # Tool automatically protected by auth settings
    return {"data": "sensitive information"}
```

#### Multi-Client Authentication (OpenAI + Claude)

For servers supporting both OpenAI and Claude, use separate endpoints:

```python
# Strict verifier for OpenAI (automatic OAuth)
class StrictOAuthVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        claims = jwt.decode(
            token,
            jwks,
            audience="https://mcp.example.com/openai",
            issuer="https://auth.example.com"
        )

        # Validate RFC 8707 resource parameter (MCP requirement)
        if claims.get("resource") != "https://mcp.example.com/openai":
            return None

        return AccessToken(token=token, scopes=claims["scope"].split())

# Flexible verifier for Claude (pre-obtained tokens)
class FlexibleTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        # Accept multiple audience values
        valid_audiences = [
            "https://mcp.example.com/claude",
            "https://api.example.com"
        ]

        claims = jwt.decode(
            token,
            jwks,
            audience=valid_audiences,  # Flexible audience
            issuer="https://auth.example.com"
        )

        return AccessToken(token=token, scopes=claims["scope"].split())

# Mount separate endpoints
from starlette.applications import Starlette
from starlette.routing import Mount

openai_mcp = FastMCP(
    "OpenAI_Server",
    token_verifier=StrictOAuthVerifier(),
    auth=AuthSettings(
        resource_server_url=AnyHttpUrl("https://mcp.example.com/openai")
    )
)

claude_mcp = FastMCP(
    "Claude_Server",
    token_verifier=FlexibleTokenVerifier(),
    auth=AuthSettings(
        resource_server_url=AnyHttpUrl("https://mcp.example.com/claude")
    )
)

app = Starlette(routes=[
    Mount("/openai", openai_mcp.streamable_http_app()),
    Mount("/claude", claude_mcp.streamable_http_app())
])
```

### 3. Error Handling

```python
@mcp.tool()
def risky_operation(file_path: str) -> str:
    """Perform risky file operation."""
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        # Return business logic error
        return json.dumps({
            "error": f"File not found: {file_path}",
            "suggestions": ["Check file path", "Verify permissions"],
            "isError": True
        })
    except PermissionError:
        return json.dumps({
            "error": "Permission denied",
            "isError": True
        })
    except Exception as e:
        # Let framework handle unexpected errors
        logging.error(f"Unexpected error: {e}")
        raise
```

### 4. Mounting to ASGI Applications

#### Basic Mounting

```python
from starlette.applications import Starlette
from starlette.routing import Mount

# Create MCP server
mcp = FastMCP("APIServer")

@mcp.tool()
def api_tool() -> str:
    return "result"

# Mount to Starlette app
app = Starlette(
    routes=[
        Mount("/api/mcp", app=mcp.streamable_http_app())
    ]
)

# Run with uvicorn
# uvicorn app:app --reload
```

#### Multiple Servers

```python
import contextlib

# Create multiple servers
echo_mcp = FastMCP("EchoServer", stateless_http=True)
math_mcp = FastMCP("MathServer", stateless_http=True)

@echo_mcp.tool()
def echo(msg: str) -> str:
    return f"Echo: {msg}"

@math_mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Combined lifespan
@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(echo_mcp.session_manager.run())
        await stack.enter_async_context(math_mcp.session_manager.run())
        yield

# Mount both servers
app = Starlette(
    routes=[
        Mount("/echo", echo_mcp.streamable_http_app()),
        Mount("/math", math_mcp.streamable_http_app())
    ],
    lifespan=lifespan
)
```

#### CORS Configuration

```python
from starlette.middleware.cors import CORSMiddleware

app = Starlette(routes=[...])

# Wrap with CORS middleware
app = CORSMiddleware(
    app,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"]  # Critical!
)
```

### 5. Custom Path Configuration

```python
# Configure MCP path during initialization
mcp = FastMCP("MyServer", streamable_http_path="/")

# Mount at /api - tools accessible at /api, not /api/mcp
app = Starlette(
    routes=[
        Mount("/api", app=mcp.streamable_http_app())
    ]
)
```

### 6. Host-based Routing

```python
from starlette.routing import Host

mcp = FastMCP("DomainServer")

@mcp.tool()
def domain_tool() -> str:
    return "domain-specific result"

# Only accessible from specific domain
app = Starlette(
    routes=[
        Host("mcp.example.com", app=mcp.streamable_http_app())
    ]
)
```

## Testing

### Unit Testing Tools

```python
import pytest
from mcp.server.fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("TestServer")

    @mcp.tool()
    def test_tool(value: str) -> str:
        return f"processed: {value}"

    return mcp

def test_tool_execution(mcp_server):
    # Test tool directly
    result = mcp_server.test_tool(value="test")
    assert result == "processed: test"
```

### Integration Testing

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_http_server():
    # Start server in background
    # (Use pytest-asyncio + uvicorn TestServer)

    async with httpx.AsyncClient() as client:
        # Test initialize
        response = await client.post(
            "http://localhost:8000/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "Test", "version": "1.0"}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data

        # Test tool call
        response = await client.post(
            "http://localhost:8000/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "test_tool",
                    "arguments": {"value": "test"}
                }
            }
        )
        assert response.status_code == 200
```

## Performance Optimization

### 1. Async I/O

```python
# Good: Non-blocking
@mcp.tool()
async def fetch_data(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

# Bad: Blocking (blocks entire server)
@mcp.tool()
def fetch_data_blocking(url: str) -> str:
    import requests
    response = requests.get(url)  # Blocks!
    return response.text
```

### 2. Connection Pooling

```python
# Reuse HTTP client
http_client = httpx.AsyncClient()

@mcp.tool()
async def api_call(endpoint: str) -> str:
    response = await http_client.get(endpoint)
    return response.text

# Cleanup in lifespan
@asynccontextmanager
async def lifespan(server):
    try:
        yield
    finally:
        await http_client.aclose()

mcp = FastMCP("Server", lifespan=lifespan)
```

### 3. Caching

```python
from functools import lru_cache
import asyncio

# Cache expensive computations
@lru_cache(maxsize=128)
def expensive_calculation(x: int) -> int:
    return x ** 2

@mcp.tool()
def cached_tool(value: int) -> int:
    """Tool with cached computation."""
    return expensive_calculation(value)

# Async cache
cache: dict = {}

@mcp.tool()
async def cached_async(key: str) -> str:
    """Async tool with manual cache."""
    if key in cache:
        return cache[key]

    # Expensive async operation
    result = await fetch_from_api(key)
    cache[key] = result
    return result
```

## Deployment

### Development

```bash
# Run with auto-reload
python server.py

# Or with uvicorn
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Production

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ProdServer")

# Define tools...

if __name__ == "__main__":
    # Production config
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",  # Localhost only (use reverse proxy)
        port=8000,
        log_level="INFO"
    )
```

```bash
# Run with Gunicorn + Uvicorn workers
gunicorn server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile - \
    --error-logfile -
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
```
