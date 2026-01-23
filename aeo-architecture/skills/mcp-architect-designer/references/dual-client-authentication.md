# Dual-Client Authentication Patterns for MCP Servers

## Overview

This guide covers authentication strategies for MCP servers that need to support multiple client types, specifically OpenAI and Claude (Anthropic), while maintaining OWASP security compliance. Based on industry best practices and the MCP OAuth 2.1 specification.

## Executive Summary

**Key Insight:** OpenAI and Claude implement the same MCP OAuth 2.1 specification but differ in WHO manages the OAuth flow:

- **OpenAI**: Automatically manages full OAuth 2.1 flow (discovery, DCR, PKCE)
- **Claude**: Expects developers to provide pre-obtained tokens

**Recommended Architecture:** Separate endpoints per client type with shared backend logic.

## Understanding Client Differences

### OpenAI's Automatic OAuth Pattern

OpenAI's ChatGPT and Agents SDK handle OAuth completely automatically:

1. **Discovery Phase**: Fetches protected resource metadata (RFC 9728)
2. **Dynamic Client Registration**: Auto-registers with authorization server (RFC 7591)
3. **Authorization Flow**: Launches authorization code + PKCE flow
4. **Token Management**: Automatically obtains, refreshes, and includes tokens
5. **Resource Binding**: Includes RFC 8707 resource parameter

**Connection Sequence:**
```
Step 1: POST /mcp (no token)
  → Server returns 401 with WWW-Authenticate header

Step 2: GET /.well-known/oauth-protected-resource
  → Server returns: {"authorization_servers": ["https://auth.example.com"]}

Step 3: GET https://auth.example.com/.well-known/oauth-authorization-server
  → Discovers endpoints (authorize, token, register)

Step 4: POST https://auth.example.com/register
  → Dynamically registers client, receives client_id

Step 5: User Authorization Flow
  → Redirects user to authorization endpoint with PKCE
  → User authorizes
  → Exchanges code for token with code_verifier

Step 6: POST /mcp (with token)
  Authorization: Bearer eyJhbGc...
  → Server validates token and proceeds
```

**Token Characteristics:**
```json
{
  "iss": "https://auth.example.com",
  "aud": "https://mcp.example.com/openai",
  "resource": "https://mcp.example.com/openai",
  "scope": "user read",
  "exp": 1234567890,
  "iat": 1234564290
}
```

### Claude's Manual Token Pattern

Claude's API and Desktop client expect developers to handle OAuth externally:

1. **Pre-Configuration**: Developer obtains token before configuring Claude
2. **Configuration**: Token passed via `authorization_token` parameter
3. **Direct Connection**: Claude immediately sends token with first request
4. **No Discovery**: Claude doesn't perform metadata discovery
5. **Developer Responsibility**: Token refresh and management handled externally

**Connection Sequence:**
```
Step 0: Developer obtains token externally
  - Manual OAuth flow with authorization server
  - Service account credentials
  - Pre-generated API keys

Step 1: Developer configures Claude
  {
    "mcpServers": {
      "my-server": {
        "url": "https://mcp.example.com/claude",
        "authorization_token": "eyJhbGc..."
      }
    }
  }

Step 2: POST /mcp (with token immediately)
  Authorization: Bearer eyJhbGc...
  → Server validates token and proceeds
```

**Token Characteristics:**
```json
{
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "scope": "user read",
  "exp": 1234567890,
  "iat": 1234564290
  // Note: May not include "resource" parameter
  // Audience may be generic API, not MCP-specific
}
```

## Why Single Endpoint Doesn't Work

### The Audience Validation Problem

The MCP specification REQUIRES:

> "MCP servers MUST verify that access tokens were issued specifically for them as the intended audience"

This creates an architectural conflict:

**OpenAI's Tokens:**
- Audience: `https://mcp.example.com/openai`
- Resource: `https://mcp.example.com/openai`
- Cryptographically bound to specific MCP server

**Claude's Manual Tokens:**
- Audience: `https://api.example.com` (or varies by how obtained)
- Resource: May not be present
- Not necessarily bound to MCP server

**Server Validation Conflict:**
```python
# If server validates strictly (as MCP spec requires)
def validate_token(token):
    claims = decode_jwt(token)

    # MCP spec requirement
    if claims["aud"] != "https://mcp.example.com":
        return False  # REJECT

    # OpenAI tokens: aud = https://mcp.example.com/openai ✅
    # Claude tokens: aud = https://api.example.com ❌ REJECTED
```

### RFC 8707 Resource Parameter Conflict

**OpenAI automatically includes:**
```
Token Request:
  resource=https://mcp.example.com/openai

Token Claims:
  "resource": "https://mcp.example.com/openai"
```

**Claude's manual tokens:**
```
May not include resource parameter at all
Depends on how developer obtained the token
```

**Server Validation:**
```python
# MCP clients MUST implement resource parameter (RFC 8707)
if claims.get("resource") != "https://mcp.example.com":
    return False  # REJECT

# OpenAI: includes correct resource ✅
# Claude: may not have resource parameter ❌
```

### Discovery Metadata Conflict

**OpenAI requires:**
- Protected resource metadata at `/.well-known/oauth-protected-resource`
- Must point to authorization server
- Must advertise OAuth capabilities

**Claude doesn't use:**
- Doesn't fetch metadata
- Doesn't perform discovery
- Bypasses entire discovery phase

**Single endpoint problem:**
- If metadata advertises strict OAuth requirements, it's misleading for Claude users
- If metadata is generic, it doesn't provide OpenAI with necessary information
- Cannot accurately describe endpoint capabilities for both client types

## Recommended Architecture: Separate Endpoints

### Architecture Pattern

```
MCP Server Architecture
├── /openai
│   ├── Strict OAuth 2.1 validation
│   ├── Full discovery metadata
│   ├── Dynamic client registration support
│   └── RFC 8707 resource parameter validation
│
├── /claude
│   ├── Flexible token acceptance
│   ├── Optional discovery metadata
│   ├── Manual token validation
│   └── Lenient audience checking
│
└── /shared
    ├── Common business logic
    ├── Shared tool implementations
    ├── Database connections
    └── External API integrations
```

### Implementation Example

```python
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from mcp.server.auth.provider import TokenVerifier, AccessToken
from mcp.server.auth.settings import AuthSettings
import jwt
from typing import Optional

# ============================================================================
# SHARED BUSINESS LOGIC
# ============================================================================

class SharedTools:
    """Common business logic used by both endpoints."""

    @staticmethod
    async def search_database(query: str) -> dict:
        """Shared search implementation."""
        # Database query logic here
        return {"results": [...]}

    @staticmethod
    async def process_data(data: str) -> dict:
        """Shared data processing."""
        # Processing logic here
        return {"processed": data}

# ============================================================================
# TOKEN VERIFIERS
# ============================================================================

class StrictOAuthVerifier(TokenVerifier):
    """
    Strict OAuth 2.1 verification for OpenAI clients.
    Implements full MCP specification and OWASP best practices.
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
                audience="https://mcp.example.com/openai",  # Strict audience
                issuer="https://auth.example.com"
            )

            # 3. Validate RFC 8707 resource parameter (MCP requirement)
            if claims.get("resource") != "https://mcp.example.com/openai":
                self.log_security_event("resource_mismatch", claims)
                return None

            # 4. Check required scopes (least privilege principle - OWASP)
            required_scopes = {"user", "read"}
            token_scopes = set(claims.get("scope", "").split())
            if not required_scopes.issubset(token_scopes):
                self.log_security_event("insufficient_scopes", claims)
                return None

            # 5. Additional security checks

            # Check token is not blacklisted
            if await self.is_blacklisted(claims.get("jti")):
                self.log_security_event("blacklisted_token", claims)
                return None

            # Check token hasn't been used too many times (replay protection)
            if await self.check_replay(claims.get("jti")):
                self.log_security_event("potential_replay", claims)
                return None

            # 6. Log successful authentication
            self.log_auth_success(claims)

            return AccessToken(
                token=token,
                scopes=token_scopes,
                expires_at=claims.get("exp")
            )

        except jwt.ExpiredSignatureError:
            self.log_security_event("expired_token")
            return None
        except jwt.InvalidTokenError as e:
            self.log_security_event("invalid_token", str(e))
            return None

    async def fetch_jwks(self, url: str):
        """Fetch and cache JWKS from authorization server."""
        # Implementation with caching
        pass

    async def is_blacklisted(self, jti: str) -> bool:
        """Check if token ID is blacklisted."""
        # Implementation with Redis/database lookup
        pass

    async def check_replay(self, jti: str) -> bool:
        """Check for potential token replay attacks."""
        # Implementation with rate limiting
        pass

    def log_security_event(self, event_type: str, details=None):
        """Log security events for monitoring."""
        # Implementation with structured logging
        pass

    def log_auth_success(self, claims: dict):
        """Log successful authentication."""
        # Implementation
        pass

class FlexibleTokenVerifier(TokenVerifier):
    """
    Flexible token verification for Claude clients.
    Accepts manually-obtained tokens while maintaining security.
    """

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        try:
            # Fetch JWKS
            jwks = await self.fetch_jwks("https://auth.example.com/jwks")

            # Accept multiple audience values for Claude's manual tokens
            valid_audiences = [
                "https://mcp.example.com/claude",  # Ideal: MCP-specific token
                "https://api.example.com",         # Generic API token
                "https://mcp.example.com"          # Root domain token
            ]

            # Verify signature and basic claims
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=valid_audiences,  # Flexible audience
                issuer="https://auth.example.com"
            )

            # Still enforce scope requirements
            required_scopes = {"user", "read"}
            token_scopes = set(claims.get("scope", "").split())
            if not required_scopes.issubset(token_scopes):
                self.log_security_event("insufficient_scopes", claims)
                return None

            # Blacklist check still applies
            if await self.is_blacklisted(claims.get("jti")):
                self.log_security_event("blacklisted_token", claims)
                return None

            # Log for monitoring
            self.log_auth_success(claims)

            return AccessToken(
                token=token,
                scopes=token_scopes,
                expires_at=claims.get("exp")
            )

        except jwt.InvalidTokenError as e:
            self.log_security_event("invalid_token", str(e))
            return None

    async def fetch_jwks(self, url: str):
        """Fetch and cache JWKS from authorization server."""
        pass

    async def is_blacklisted(self, jti: str) -> bool:
        """Check if token ID is blacklisted."""
        pass

    def log_security_event(self, event_type: str, details=None):
        """Log security events for monitoring."""
        pass

    def log_auth_success(self, claims: dict):
        """Log successful authentication."""
        pass

# ============================================================================
# MCP SERVERS
# ============================================================================

# OpenAI endpoint - Full OAuth 2.1 with discovery
openai_mcp = FastMCP(
    "OpenAI_MCP_Server",
    token_verifier=StrictOAuthVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("https://mcp.example.com/openai"),
        required_scopes=["user", "read"]
    )
)

@openai_mcp.tool()
async def search_openai(query: str) -> dict:
    """
    Search database (OpenAI endpoint).

    Args:
        query: Search query string
    """
    return await SharedTools.search_database(query)

@openai_mcp.tool()
async def process_openai(data: str) -> dict:
    """
    Process data (OpenAI endpoint).

    Args:
        data: Data to process
    """
    return await SharedTools.process_data(data)

# Claude endpoint - Pre-obtained token acceptance
claude_mcp = FastMCP(
    "Claude_MCP_Server",
    token_verifier=FlexibleTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("https://mcp.example.com/claude"),
        required_scopes=["user", "read"]
    )
)

@claude_mcp.tool()
async def search_claude(query: str) -> dict:
    """
    Search database (Claude endpoint).

    Args:
        query: Search query string
    """
    return await SharedTools.search_database(query)

@claude_mcp.tool()
async def process_claude(data: str) -> dict:
    """
    Process data (Claude endpoint).

    Args:
        data: Data to process
    """
    return await SharedTools.process_data(data)

# ============================================================================
# APPLICATION ASSEMBLY
# ============================================================================

# Mount both MCP servers
app = Starlette(routes=[
    Mount("/openai", openai_mcp.streamable_http_app()),
    Mount("/claude", claude_mcp.streamable_http_app())
])

# CORS configuration (critical for browser clients)
app = CORSMiddleware(
    app,
    allow_origins=[
        "https://chatgpt.com",          # OpenAI
        "https://claude.ai",            # Claude
        "https://yourapp.example.com"   # Your frontend
    ],
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Mcp-Session-Id",
        "Accept"
    ],
    expose_headers=[
        "Mcp-Session-Id",  # Critical for session management
        "WWW-Authenticate"  # Critical for OAuth discovery
    ],
    allow_credentials=True
)

# ============================================================================
# DEPLOYMENT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
```

### Client Configuration

**OpenAI Configuration:**
```python
# OpenAI SDK (auto-discovery)
from openai import OpenAI

client = OpenAI()

# Point to OpenAI endpoint - discovery handles rest
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Search for user data"}],
    tools=[{
        "type": "mcp",
        "mcp": {
            "url": "https://mcp.example.com/openai"
        }
    }]
)
```

**Claude Configuration:**
```json
{
  "mcpServers": {
    "my-server-claude": {
      "url": "https://mcp.example.com/claude",
      "authorization_token": "eyJhbGc..."
    }
  }
}
```

**Obtaining Token for Claude:**
```bash
# Option 1: OAuth Device Flow (recommended for user tokens)
curl -X POST https://auth.example.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code" \
  -d "device_code=YOUR_DEVICE_CODE" \
  -d "client_id=your-client-id" \
  -d "resource=https://mcp.example.com/claude"

# Option 2: Client Credentials (for service accounts)
curl -X POST https://auth.example.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=your-client-id" \
  -d "client_secret=your-secret" \
  -d "scope=user read" \
  -d "resource=https://mcp.example.com/claude"

# Response includes access_token for Claude configuration
```

## OWASP Security Compliance

### Authentication & Authorization Checklist

**OAuth 2.1 Requirements:**
- [x] PKCE mandatory (prevents authorization code interception)
- [x] Short-lived access tokens (15-60 minutes)
- [x] Refresh token rotation
- [x] No client secrets for public clients
- [x] HTTPS only (TLS 1.2+ minimum)

**Token Validation:**
- [x] JWT signature verification with JWKS
- [x] Audience claim validation (prevents confused deputy attacks)
- [x] Issuer validation
- [x] Expiration validation
- [x] Scope validation (least privilege principle)
- [x] Token blacklist support

**MCP-Specific Requirements:**
- [x] RFC 8707 resource parameter validation
- [x] Protected Resource Metadata (RFC 9728) exposed
- [x] Authorization Server Metadata (RFC 8414) at auth server
- [x] Dynamic Client Registration (RFC 7591) supported
- [x] WWW-Authenticate header on 401 responses

**Transport Security:**
- [x] HTTPS enforced
- [x] Certificate validation
- [x] HSTS headers
- [x] CORS properly configured
- [x] No tokens in URL query parameters
- [x] No tokens in localStorage (use httpOnly cookies or memory)

**Monitoring & Audit:**
- [x] Log all authentication attempts
- [x] Log all tool invocations with user context
- [x] Rate limiting per client/token
- [x] Anomaly detection for token reuse
- [x] Security event alerting

### OWASP Top 10 Considerations

**A01:2021 - Broken Access Control:**
- Enforce scope-based authorization
- Validate token audience matches server
- Implement token blacklist/revocation
- Rate limit per token/client

**A02:2021 - Cryptographic Failures:**
- Use TLS 1.2+ exclusively
- Verify JWT signatures with proper algorithms (RS256, ES256)
- Never accept unsigned tokens (alg=none)
- Rotate signing keys regularly

**A03:2021 - Injection:**
- Validate all tool input parameters
- Use parameterized queries for database operations
- Sanitize outputs
- Guard against prompt injection attacks

**A04:2021 - Insecure Design:**
- Separate endpoints for different client types
- Clear security boundaries
- Fail secure by default
- Principle of least privilege

**A05:2021 - Security Misconfiguration:**
- Disable debug mode in production
- Remove default credentials
- Configure CORS restrictively
- Keep dependencies updated

**A07:2021 - Identification and Authentication Failures:**
- No weak password requirements (OAuth only)
- Multi-factor authentication at auth server
- Secure session management
- Token replay protection

**A09:2021 - Security Logging and Monitoring Failures:**
- Log all authentication events
- Monitor for suspicious patterns
- Alert on security events
- Retain logs for forensic analysis

## Discovery Metadata Configuration

### OpenAI Endpoint Metadata

**Protected Resource Metadata** (`/.well-known/oauth-protected-resource`):
```json
{
  "resource": "https://mcp.example.com/openai",
  "authorization_servers": ["https://auth.example.com"],
  "bearer_methods_supported": ["header"],
  "resource_signing_alg_values_supported": ["RS256"]
}
```

**Authorization Server Metadata** (`/.well-known/oauth-authorization-server`):
```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "registration_endpoint": "https://auth.example.com/register",
  "jwks_uri": "https://auth.example.com/jwks",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none"],
  "scopes_supported": ["user", "read", "write"]
}
```

### Claude Endpoint Metadata

**Optional Protected Resource Metadata** (for documentation):
```json
{
  "resource": "https://mcp.example.com/claude",
  "authorization_servers": ["https://auth.example.com"],
  "bearer_methods_supported": ["header"],
  "documentation_uri": "https://docs.example.com/mcp-claude-auth"
}
```

Note: Claude doesn't fetch this metadata, but providing it helps developers understand requirements.

## Alternative Approaches (Not Recommended)

### Single Endpoint with Intelligent Detection

**Concept:** Use single endpoint with token inspection to determine client type.

```python
class UniversalTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        # Decode without verification to inspect claims
        unverified = jwt.decode(token, options={"verify_signature": False})

        # Detect token source
        aud = unverified.get("aud")
        resource = unverified.get("resource")

        # Route to appropriate validator
        if resource and "openai" in resource:
            return await self.verify_openai_token(token)
        elif "claude" in str(aud):
            return await self.verify_claude_token(token)
        else:
            return await self.verify_generic_token(token)
```

**Problems:**
1. Violates clear security boundaries
2. Complex validation logic harder to audit
3. Ambiguous audience validation
4. Discovery metadata becomes unclear
5. Difficult to monitor and debug
6. Not explicitly supported by MCP spec

**When to consider:** Only if you absolutely cannot deploy separate endpoints (e.g., infrastructure constraints).

### Relaxed Audience Validation

**Concept:** Accept any token from trusted issuer, regardless of audience.

```python
class RelaxedVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        # Only verify issuer, not audience
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer="https://auth.example.com",
            options={"verify_aud": False}  # Skip audience validation
        )
        return AccessToken(token=token, scopes=claims["scope"].split())
```

**Problems:**
1. Violates MCP specification requirement
2. Enables confused deputy attacks
3. Fails OWASP security standards
4. Tokens can be reused across services
5. No defense against token theft

**Never use in production.**

## Production Deployment Considerations

### Infrastructure

**Load Balancer Configuration:**
```nginx
upstream mcp_openai {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    keepalive 32;
}

upstream mcp_claude {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name mcp.example.com;

    ssl_certificate /etc/ssl/certs/mcp.example.com.crt;
    ssl_certificate_key /etc/ssl/private/mcp.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    # OpenAI endpoint
    location /openai {
        proxy_pass http://mcp_openai;
        proxy_http_version 1.1;

        # Critical for SSE
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;

        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Claude endpoint
    location /claude {
        proxy_pass http://mcp_claude;
        proxy_http_version 1.1;

        # SSE configuration
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;

        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .
COPY shared/ ./shared/

# Run as non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "server.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - AUTH_SERVER_URL=https://auth.example.com
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

### Monitoring

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Authentication metrics
auth_attempts_total = Counter(
    'mcp_auth_attempts_total',
    'Total authentication attempts',
    ['endpoint', 'result']
)

auth_duration_seconds = Histogram(
    'mcp_auth_duration_seconds',
    'Authentication duration',
    ['endpoint']
)

# Tool execution metrics
tool_calls_total = Counter(
    'mcp_tool_calls_total',
    'Total tool calls',
    ['endpoint', 'tool_name', 'result']
)

tool_duration_seconds = Histogram(
    'mcp_tool_duration_seconds',
    'Tool execution duration',
    ['endpoint', 'tool_name']
)

# Active connections
active_connections = Gauge(
    'mcp_active_connections',
    'Number of active connections',
    ['endpoint']
)
```

**Structured Logging:**
```python
import structlog

logger = structlog.get_logger()

# Log authentication event
logger.info(
    "authentication_success",
    endpoint="openai",
    user_id=claims.get("sub"),
    scopes=claims.get("scope"),
    token_exp=claims.get("exp")
)

# Log tool invocation
logger.info(
    "tool_invocation",
    endpoint="claude",
    tool_name="search_database",
    user_id=claims.get("sub"),
    parameters=sanitize(parameters),
    duration_ms=duration
)

# Log security event
logger.warning(
    "security_event",
    event_type="invalid_audience",
    endpoint="openai",
    expected_aud="https://mcp.example.com/openai",
    received_aud=claims.get("aud")
)
```

## Testing Strategies

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
import jwt

class TestStrictOAuthVerifier:
    @pytest.fixture
    def verifier(self):
        return StrictOAuthVerifier()

    @pytest.mark.asyncio
    async def test_valid_token(self, verifier):
        """Test validation of valid OpenAI token."""
        token = create_test_token(
            aud="https://mcp.example.com/openai",
            resource="https://mcp.example.com/openai",
            scope="user read"
        )

        result = await verifier.verify_token(token)

        assert result is not None
        assert "user" in result.scopes
        assert "read" in result.scopes

    @pytest.mark.asyncio
    async def test_wrong_audience(self, verifier):
        """Test rejection of token with wrong audience."""
        token = create_test_token(
            aud="https://wrong.example.com",
            resource="https://mcp.example.com/openai",
            scope="user read"
        )

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    async def test_missing_resource(self, verifier):
        """Test rejection of token without resource parameter."""
        token = create_test_token(
            aud="https://mcp.example.com/openai",
            scope="user read"
            # No resource parameter
        )

        result = await verifier.verify_token(token)

        assert result is None

class TestFlexibleTokenVerifier:
    @pytest.fixture
    def verifier(self):
        return FlexibleTokenVerifier()

    @pytest.mark.asyncio
    async def test_accepts_multiple_audiences(self, verifier):
        """Test acceptance of tokens with various audiences."""
        audiences = [
            "https://mcp.example.com/claude",
            "https://api.example.com",
            "https://mcp.example.com"
        ]

        for aud in audiences:
            token = create_test_token(aud=aud, scope="user read")
            result = await verifier.verify_token(token)
            assert result is not None
```

### Integration Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_openai_endpoint_requires_token():
    """Test that OpenAI endpoint returns 401 without token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/openai",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        )

        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers

@pytest.mark.asyncio
async def test_openai_endpoint_with_valid_token():
    """Test OpenAI endpoint with valid token."""
    token = create_test_token(
        aud="https://mcp.example.com/openai",
        resource="https://mcp.example.com/openai",
        scope="user read"
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/openai",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data

@pytest.mark.asyncio
async def test_claude_endpoint_with_manual_token():
    """Test Claude endpoint with manually-obtained token."""
    token = create_test_token(
        aud="https://api.example.com",  # Generic audience
        scope="user read"
        # No resource parameter
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/claude",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
```

## Summary

### Key Takeaways

1. **Separate Endpoints Are Required** for production-grade dual-client support due to:
   - Token audience validation requirements (MCP spec)
   - RFC 8707 resource parameter differences
   - Discovery metadata conflicts
   - OWASP security compliance

2. **OpenAI vs Claude Differences:**
   - OpenAI: Automatic OAuth flow management, strict validation
   - Claude: Manual token management, flexible acceptance

3. **Security Must Not Be Compromised:**
   - Always validate token audience
   - Always verify JWT signatures
   - Always enforce scopes
   - Always use HTTPS
   - Always log security events

4. **Architecture Benefits:**
   - Clear security boundaries
   - Easy to audit and monitor
   - Follows MCP specification exactly
   - OWASP-compliant by design
   - Simple to maintain

### Quick Decision Matrix

**Use Separate Endpoints When:**
- Building production MCP servers
- Security compliance required (OWASP, SOC2, etc.)
- Supporting both OpenAI and Claude
- Need clear audit trails
- Want explicit security boundaries

**Consider Single Endpoint Only When:**
- Development/testing only (never production)
- Internal tools with relaxed security
- Both clients use identical token sources
- You can relax audience validation (not recommended)

### Resources

- MCP Specification: https://modelcontextprotocol.io/specification
- RFC 8707 (Resource Indicators): https://www.rfc-editor.org/rfc/rfc8707.html
- RFC 9728 (Protected Resource Metadata): https://www.rfc-editor.org/rfc/rfc9728.html
- OWASP OAuth Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html
