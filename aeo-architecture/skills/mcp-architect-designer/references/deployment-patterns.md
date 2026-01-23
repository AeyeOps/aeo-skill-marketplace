# MCP Server Deployment Patterns

## Overview

Production deployment patterns for MCP servers covering containerization, reverse proxies, monitoring, and infrastructure configuration.

## Docker Deployment

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Run as non-root user (security best practice)
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "server.py"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
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

### Multi-Stage Build (Optimized)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY server.py .
COPY shared/ ./shared/

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "server.py"]
```

## Reverse Proxy Configuration

### nginx

```nginx
upstream mcp_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # Multiple instances for load balancing
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name mcp.example.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/mcp.example.com.crt;
    ssl_certificate_key /etc/ssl/private/mcp.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # MCP endpoint
    location /mcp {
        proxy_pass http://mcp_backend;
        proxy_http_version 1.1;

        # Critical for SSE (Server-Sent Events)
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;  # Long timeout for SSE

        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Pass through authentication headers
        proxy_pass_header Authorization;
    }

    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://mcp_backend;
        proxy_http_version 1.1;
        access_log off;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name mcp.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Caddy (Alternative)

```caddyfile
mcp.example.com {
    reverse_proxy /mcp/* localhost:8000 {
        # SSE support
        flush_interval -1

        # Headers
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }

    reverse_proxy /health localhost:8000

    # Automatic HTTPS
    tls your-email@example.com
}
```

## Monitoring and Observability

### Health Check Endpoint

```python
from starlette.responses import JSONResponse
from starlette.requests import Request
import asyncio

async def health_check(request: Request) -> JSONResponse:
    """
    Health check endpoint for load balancers and monitoring.
    Verifies all critical dependencies are operational.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database connectivity
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"

    # Check Redis/cache
    try:
        await redis.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"error: {str(e)}"

    # Check auth server reachability
    try:
        response = await httpx.get("https://auth.example.com/.well-known/jwks")
        if response.status_code == 200:
            health_status["checks"]["auth_server"] = "ok"
        else:
            health_status["checks"]["auth_server"] = f"status: {response.status_code}"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["auth_server"] = f"error: {str(e)}"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(health_status, status_code=status_code)
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging systems."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

# Usage in application
logger = logging.getLogger(__name__)

# Log with extra context
logger.info(
    "Tool invoked",
    extra={
        "user_id": user_id,
        "request_id": request_id,
        "tool_name": "search_database",
        "duration_ms": 150
    }
)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response

# Define metrics
auth_attempts_total = Counter(
    'mcp_auth_attempts_total',
    'Total authentication attempts',
    ['endpoint', 'result']
)

auth_duration_seconds = Histogram(
    'mcp_auth_duration_seconds',
    'Authentication duration in seconds',
    ['endpoint']
)

tool_calls_total = Counter(
    'mcp_tool_calls_total',
    'Total tool invocations',
    ['endpoint', 'tool_name', 'result']
)

tool_duration_seconds = Histogram(
    'mcp_tool_duration_seconds',
    'Tool execution duration in seconds',
    ['endpoint', 'tool_name']
)

active_connections = Gauge(
    'mcp_active_connections',
    'Number of active connections',
    ['endpoint']
)

# Metrics endpoint
async def metrics(request):
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type="text/plain; version=0.0.4"
    )

# Usage in application
@mcp.tool()
async def search_database(query: str) -> dict:
    start_time = time.time()

    try:
        result = await perform_search(query)
        tool_calls_total.labels(
            endpoint="claude",
            tool_name="search_database",
            result="success"
        ).inc()
        return result
    except Exception as e:
        tool_calls_total.labels(
            endpoint="claude",
            tool_name="search_database",
            result="error"
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        tool_duration_seconds.labels(
            endpoint="claude",
            tool_name="search_database"
        ).observe(duration)
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  labels:
    app: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: AUTH_SERVER_URL
          value: "https://auth.example.com"
        - name: LOG_LEVEL
          value: "INFO"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-server
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - mcp.example.com
    secretName: mcp-tls
  rules:
  - host: mcp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-server
            port:
              number: 80
```

## Environment Configuration

### Environment Variables

```bash
# Server configuration
MCP_SERVER_NAME=my-mcp-server
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
MCP_TRANSPORT=streamable-http

# Authentication
AUTH_SERVER_URL=https://auth.example.com
AUTH_ISSUER_URL=https://auth.example.com
RESOURCE_SERVER_URL=https://mcp.example.com
REQUIRED_SCOPES=user,read

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mcp
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
ALLOWED_ORIGINS=https://chatgpt.com,https://claude.ai
CORS_MAX_AGE=3600

# Monitoring
METRICS_ENABLED=true
METRICS_PORT=9090
```

### Configuration File (YAML)

```yaml
# config.yaml
server:
  name: my-mcp-server
  host: 0.0.0.0
  port: 8000
  transport: streamable-http

auth:
  issuer_url: https://auth.example.com
  resource_server_url: https://mcp.example.com
  required_scopes:
    - user
    - read
  token_cache_ttl: 300

database:
  url: postgresql://user:pass@localhost:5432/mcp
  pool_size: 20
  max_overflow: 10
  echo: false

redis:
  url: redis://localhost:6379/0
  max_connections: 50
  socket_timeout: 5

logging:
  level: INFO
  format: json
  handlers:
    - type: console
    - type: file
      filename: /var/log/mcp-server.log

cors:
  allowed_origins:
    - https://chatgpt.com
    - https://claude.ai
  allowed_methods:
    - GET
    - POST
  expose_headers:
    - Mcp-Session-Id
    - WWW-Authenticate
  max_age: 3600

metrics:
  enabled: true
  port: 9090
  path: /metrics
```

## Security Hardening

### TLS Configuration

```python
import ssl
import uvicorn

# Create SSL context with strong security
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", "key.pem")

# Disable weak protocols and ciphers
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")

# Run with TLS
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8443,
    ssl_context=ssl_context
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/mcp")
@limiter.limit("100/minute")
async def mcp_endpoint(request: Request):
    # Handle MCP requests with rate limiting
    pass
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] TLS certificates installed and valid
- [ ] Database migrations applied
- [ ] Redis/cache configured and accessible
- [ ] Health check endpoint responding
- [ ] Metrics endpoint configured
- [ ] Logging configured (structured JSON)
- [ ] CORS configured with allowed origins
- [ ] Rate limiting enabled
- [ ] Authentication server connectivity verified
- [ ] Firewall rules configured
- [ ] Load balancer health checks configured
- [ ] Monitoring and alerting set up
- [ ] Backup and disaster recovery plan in place
- [ ] Security headers configured
- [ ] Container running as non-root user
- [ ] Resource limits configured (CPU, memory)
- [ ] Auto-scaling policies configured (if applicable)
