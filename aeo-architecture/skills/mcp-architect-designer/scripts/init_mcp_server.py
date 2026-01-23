#!/usr/bin/env python3
"""
MCP Server Project Initializer

Creates a new MCP server project with best-practice structure.
Usage:
    python init_mcp_server.py my-server
    python init_mcp_server.py my-server --template oauth
    python init_mcp_server.py my-server --output /path/to/dir
"""

import argparse
import os
import sys
from pathlib import Path


TEMPLATES = {
    "basic": {
        "name": "Basic FastMCP Server",
        "description": "Simple MCP server with tools and resources",
    },
    "oauth": {
        "name": "OAuth-Protected Server",
        "description": "MCP server with OAuth 2.1 authentication",
    },
    "dual-interface": {
        "name": "Dual REST + MCP Interface",
        "description": "Server exposing both REST API and MCP tools",
    }
}


def create_basic_template(project_path: Path, project_name: str):
    """Create basic FastMCP server template"""

    # server.py
    server_py = '''"""
{name} - MCP Server

A Model Context Protocol server built with FastMCP.
"""

import logging
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("{name}")


@mcp.tool()
def greet(name: str = "World") -> str:
    """
    Greet someone by name.

    Args:
        name: Name of person to greet

    Returns:
        Greeting message
    """
    logger.info(f"Greeting: {{name}}")
    return f"Hello, {{name}}!"


@mcp.tool()
async def long_task(
    task_name: str,
    steps: int = 5,
    ctx: Context[ServerSession, None] = None
) -> str:
    """
    Execute a long-running task with progress updates.

    Args:
        task_name: Name of the task
        steps: Number of steps to execute
        ctx: MCP context for progress reporting

    Returns:
        Completion message
    """
    await ctx.info(f"Starting task: {{task_name}}")

    for i in range(steps):
        progress = (i + 1) / steps
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"Step {{i + 1}}/{{steps}}"
        )

    await ctx.info(f"Completed: {{task_name}}")
    return f"Task '{{task_name}}' completed successfully"


@mcp.resource("config://settings")
def get_settings() -> str:
    """Get server configuration settings."""
    import json
    return json.dumps({{
        "server_name": "{name}",
        "version": "1.0.0"
    }})


@mcp.resource("data://item/{{item_id}}")
def get_item(item_id: str) -> str:
    """
    Get item by ID.

    Args:
        item_id: ID of item to retrieve

    Returns:
        Item data as JSON string
    """
    import json
    # Replace with actual data source
    return json.dumps({{
        "id": item_id,
        "name": f"Item {{item_id}}"
    }})


if __name__ == "__main__":
    logger.info("Starting {name} MCP server...")
    mcp.run(transport="streamable-http")
'''.format(name=project_name)

    (project_path / "server.py").write_text(server_py)

    # requirements.txt
    requirements = '''mcp>=1.0.0
httpx>=0.27.0
pydantic>=2.0.0
'''
    (project_path / "requirements.txt").write_text(requirements)

    # README.md
    readme = f'''# {project_name}

A Model Context Protocol server built with FastMCP.

## Installation

```bash
# Using pip
pip install -r requirements.txt

# Using uv
uv sync
```

## Running the Server

```bash
# Development mode
python server.py

# Or with uvicorn
uvicorn server:app --reload
```

The server will start on `http://localhost:8000/mcp`

## Testing

```bash
# Test connectivity
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/list"}}'
```

## Available Tools

- `greet(name)` - Greet someone by name
- `long_task(task_name, steps)` - Execute long-running task with progress

## Available Resources

- `config://settings` - Server configuration
- `data://item/{{item_id}}` - Get item by ID

## Development

```bash
# Run with auto-reload
python server.py

# Run tests
pytest

# Type checking
mypy server.py
```

## Deployment

See `docker-compose.yml` for containerized deployment.

## License

MIT
'''
    (project_path / "README.md").write_text(readme)

    # .gitignore
    gitignore = '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.env
.venv
env/
venv/
'''
    (project_path / ".gitignore").write_text(gitignore)

    # docker-compose.yml
    docker_compose = f'''version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
'''
    (project_path / "docker-compose.yml").write_text(docker_compose)

    # Dockerfile
    dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
'''
    (project_path / "Dockerfile").write_text(dockerfile)

    # tests/
    tests_dir = project_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")

    test_server = '''"""Tests for MCP server"""
import pytest
from server import mcp


def test_greet_tool():
    """Test greet tool"""
    result = mcp.greet(name="Test")
    assert result == "Hello, Test!"


def test_greet_default():
    """Test greet with default parameter"""
    result = mcp.greet()
    assert result == "Hello, World!"
'''
    (tests_dir / "test_server.py").write_text(test_server)


def create_oauth_template(project_path: Path, project_name: str):
    """Create OAuth-protected server template"""
    create_basic_template(project_path, project_name)

    # Update server.py with OAuth
    server_py = '''"""
{name} - OAuth-Protected MCP Server
"""

import logging
from pydantic import AnyHttpUrl
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleTokenVerifier(TokenVerifier):
    """Simple token verifier for demonstration"""

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify access token.

        In production, verify with your authorization server:
        - Check token signature
        - Validate expiration
        - Verify scopes
        """
        # Demo: accept any token starting with "valid-"
        if token.startswith("valid-"):
            return AccessToken(
                token=token,
                scopes=["user", "read"],
                expires_at=None
            )

        logger.warning(f"Token verification failed for: {{token[:10]}}...")
        return None


# Create protected MCP server
mcp = FastMCP(
    "{name}",
    token_verifier=SimpleTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("http://localhost:8000"),
        required_scopes=["user"]
    )
)


@mcp.tool()
def get_protected_data() -> dict:
    """
    Get protected data (requires authentication).

    Returns:
        Protected data
    """
    return {{
        "data": "This is sensitive information",
        "access_level": "protected"
    }}


@mcp.tool()
def public_info() -> str:
    """
    Get public information (no auth required if you modify auth settings).

    Returns:
        Public information
    """
    return "This is public information"


if __name__ == "__main__":
    logger.info("Starting OAuth-protected MCP server...")
    logger.warning("Using demo token verifier - replace with real OAuth in production!")
    mcp.run(transport="streamable-http")
'''.format(name=project_name)

    (project_path / "server.py").write_text(server_py)

    # Add OAuth note to README
    readme_addition = f'''

## OAuth Authentication

This server requires OAuth 2.1 authentication.

### Testing with Authentication

```bash
# Call with Bearer token
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer valid-test-token" \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{"name":"get_protected_data","arguments":{{}}}}}}'
```

### Production Deployment

Replace `SimpleTokenVerifier` with real OAuth token verification:

```python
class ProductionTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        # Verify with your OAuth server
        # Check JWT signature, expiration, scopes
        pass
```
'''
    readme = (project_path / "README.md").read_text()
    (project_path / "README.md").write_text(readme + readme_addition)


def main():
    parser = argparse.ArgumentParser(description="Initialize a new MCP server project")
    parser.add_argument("name", help="Project name (e.g., my-server)")
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default="basic",
        help="Project template to use"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    project_name = args.name
    project_path = args.output / project_name

    # Check if directory exists
    if project_path.exists():
        print(f"Error: Directory already exists: {project_path}")
        sys.exit(1)

    # Create project directory
    project_path.mkdir(parents=True)
    print(f"Creating MCP server project: {project_name}")
    print(f"Template: {TEMPLATES[args.template]['name']}")
    print(f"Location: {project_path}")

    # Create template
    if args.template == "basic":
        create_basic_template(project_path, project_name)
    elif args.template == "oauth":
        create_oauth_template(project_path, project_name)
    elif args.template == "dual-interface":
        print("Error: dual-interface template not yet implemented")
        sys.exit(1)

    print("\n✓ Project created successfully!")
    print("\nNext steps:")
    print(f"  cd {project_name}")
    print("  pip install -r requirements.txt")
    print("  python server.py")
    print(f"\nServer will be available at: http://localhost:8000/mcp")


if __name__ == "__main__":
    main()
