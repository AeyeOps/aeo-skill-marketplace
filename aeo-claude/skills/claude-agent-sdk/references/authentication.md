# Authentication Guide

The Claude Agent SDK supports two authentication methods: API Key and Subscription (OAuth).

## Contents

- Authentication Methods Overview
- API Key Authentication
- Subscription Authentication
- Token Lifecycle
- Environment Variable Handling
- SDK Subprocess Architecture
- Code Examples
- Best Practices

## Authentication Methods Overview

| Method | Billing | Token Location | Use Case |
|--------|---------|----------------|----------|
| API Key | Per-token usage | Environment variable | Serverless, CI/CD, production |
| Subscription | Flat rate (Pro/Max/Team) | Credentials file | Development, interactive sessions |

The SDK spawns a Claude CLI subprocess that handles authentication. Your application configures which method to use via environment variables passed to `ClaudeAgentOptions`.

## API Key Authentication

Direct authentication using an Anthropic API key.

### Setup

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    env={"ANTHROPIC_API_KEY": "sk-ant-api..."},
    allowed_tools=["Read", "Write"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Hello")
```

### Characteristics

- Billed per input/output token
- Key never expires (until revoked)
- No browser-based login required
- Suitable for automated pipelines

### Security

- Never hardcode API keys in source code
- Load from environment or secrets manager
- Use separate keys for dev/staging/production
- Rotate keys periodically

## Subscription Authentication

OAuth-based authentication using a Claude subscription (Pro, Max, Team, Enterprise).

### Initial Setup

Users authenticate once via the Claude CLI:

```bash
claude setup-token
```

This opens a browser for OAuth and stores credentials at `~/.claude/.credentials.json`.

### Credentials Structure

```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1764298419175,
    "scopes": ["user:inference", "user:profile"],
    "subscriptionType": "max",
    "rateLimitTier": "default_claude_max_20x"
  }
}
```

| Field | Description |
|-------|-------------|
| accessToken | Short-lived token, expires in approximately 1 hour |
| refreshToken | Long-lived token for obtaining new access tokens |
| expiresAt | Unix timestamp in milliseconds |
| subscriptionType | pro, max, team, or enterprise |
| rateLimitTier | Rate limit configuration for the subscription |

### Using Subscription Auth in SDK

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

# Empty string forces OAuth, prevents API key inheritance
options = ClaudeAgentOptions(
    env={"ANTHROPIC_API_KEY": ""},
    allowed_tools=["Read", "Write"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Hello")
```

## Token Lifecycle

### Access Token Refresh

The Claude CLI subprocess handles token refresh automatically:

1. CLI reads credentials file at subprocess startup
2. Before each API call, CLI checks if accessToken is expired
3. If expired, CLI uses refreshToken to obtain new accessToken
4. CLI updates the credentials file with new tokens
5. API call proceeds with fresh accessToken

Your application does not manage token refresh. The CLI subprocess handles this internally.

### Token Expiry Timeline

| Token | Lifespan | Refresh Mechanism |
|-------|----------|-------------------|
| accessToken | Approximately 1 hour | Automatic via refreshToken |
| refreshToken | Weeks to months | Re-run `claude setup-token` |

### Handling Refresh Token Expiry

If the refreshToken expires during a long-running application:

```python
from claude_agent_sdk import ProcessError

try:
    async for msg in client.receive_response():
        print(msg)
except ProcessError as e:
    if e.exit_code != 0:
        # Token refresh may have failed
        # Prompt user to re-authenticate
        print("Session expired. Please run: claude setup-token")
```

## Environment Variable Handling

### The Inheritance Problem

The SDK spawns the Claude CLI as a subprocess. Environment variables are inherited:

```python
# SDK internal behavior (subprocess_cli.py)
process_env = {
    **os.environ,           # Parent process environment
    **options.env,          # Your overrides
    "CLAUDE_CODE_ENTRYPOINT": "sdk-py",
}
```

If `ANTHROPIC_API_KEY` exists in the parent environment (common in development), the CLI will use API billing even when you want subscription auth.

### Forcing Subscription Auth

Override with an empty string to force OAuth:

```python
options = ClaudeAgentOptions(
    env={"ANTHROPIC_API_KEY": ""},  # Empty string, not omitted
)
```

The empty string overwrites any inherited key. The CLI sees an empty value and falls back to OAuth credentials.

### Auth Manager Pattern

Encapsulate auth logic in a manager class:

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json


class AuthMethod(Enum):
    NONE = "none"
    API_KEY = "api-key"
    SUBSCRIPTION = "subscription"


@dataclass
class AuthStatus:
    method: AuthMethod
    description: str | None = None


class AuthManager:
    CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"

    def __init__(self) -> None:
        self._api_key: str | None = None

    def get_status(self) -> AuthStatus:
        """Detect current authentication state."""
        # Check for stored API key preference
        if self._api_key:
            return AuthStatus(AuthMethod.API_KEY, "API Key")

        # Check for subscription credentials
        if self.CREDENTIALS_PATH.exists():
            try:
                creds = json.loads(self.CREDENTIALS_PATH.read_text())
                oauth = creds.get("claudeAiOauth", {})
                if oauth.get("accessToken"):
                    sub_type = oauth.get("subscriptionType", "unknown")
                    return AuthStatus(
                        AuthMethod.SUBSCRIPTION,
                        f"Claude {sub_type.title()}"
                    )
            except (json.JSONDecodeError, KeyError):
                pass

        return AuthStatus(AuthMethod.NONE)

    def set_api_key(self, key: str) -> None:
        """Configure API key authentication."""
        self._api_key = key

    def get_env(self) -> dict[str, str]:
        """Get environment variables for ClaudeAgentOptions."""
        status = self.get_status()

        if status.method == AuthMethod.API_KEY and self._api_key:
            return {"ANTHROPIC_API_KEY": self._api_key}

        # Force OAuth by clearing any inherited API key
        return {"ANTHROPIC_API_KEY": ""}
```

### Using the Auth Manager

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

auth = AuthManager()

# Check status before creating client
status = auth.get_status()
if status.method == AuthMethod.NONE:
    print("Not authenticated. Run: claude setup-token")
    return

# Create client with appropriate auth
options = ClaudeAgentOptions(
    env=auth.get_env(),
    allowed_tools=["Read", "Write"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Hello")
```

## SDK Subprocess Architecture

Understanding how the SDK uses authentication:

```
Your Application
    |
    v
ClaudeAgentOptions(env={...})
    |
    v
ClaudeSDKClient
    |
    v
SubprocessCLITransport
    |
    +---> anyio.open_process(["claude", ...], env=process_env)
              |
              v
         Claude CLI (subprocess)
              |
              +---> Reads ~/.claude/.credentials.json (once at startup)
              |
              +---> Handles token refresh internally
              |
              +---> Makes API calls to Anthropic
```

### Key Points

1. **Single subprocess**: SDK spawns one persistent CLI subprocess per client
2. **Credentials read once**: CLI reads credentials at startup, not per-query
3. **Refresh is internal**: CLI handles accessToken refresh using refreshToken
4. **Environment merge**: SDK merges os.environ with options.env before spawning

### Subprocess Lifecycle

```python
# Subprocess created on connect
client = ClaudeSDKClient(options=options)
await client.connect()  # Spawns subprocess, reads credentials

# Subprocess stays alive for all queries
await client.query("First query")
await client.query("Second query")  # Same subprocess

# Subprocess terminated on disconnect
await client.disconnect()  # Kills subprocess
```

## Code Examples

### Example 1: API Key from Environment

```python
import os
from claude_agent_sdk import ClaudeAgentOptions, query

async def run_with_api_key():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    options = ClaudeAgentOptions(
        env={"ANTHROPIC_API_KEY": api_key},
        max_turns=5,
    )

    async for msg in query("Summarize this file", options=options):
        print(msg)
```

### Example 2: Subscription with Fallback

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from pathlib import Path
import json


def has_valid_subscription() -> bool:
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if not creds_path.exists():
        return False
    try:
        creds = json.loads(creds_path.read_text())
        return bool(creds.get("claudeAiOauth", {}).get("accessToken"))
    except Exception:
        return False


async def run_with_subscription():
    if not has_valid_subscription():
        print("No subscription found. Run: claude setup-token")
        return

    options = ClaudeAgentOptions(
        env={"ANTHROPIC_API_KEY": ""},  # Force OAuth
        max_turns=10,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Hello")
        async for msg in client.receive_response():
            print(msg)
```

### Example 3: Dual-Mode Auth Manager

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
import subprocess


class DualAuthManager:
    """Support both API key and subscription authentication."""

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._use_subscription: bool = False

    def configure_api_key(self, key: str) -> None:
        self._api_key = key
        self._use_subscription = False

    def configure_subscription(self) -> bool:
        """Trigger subscription login flow."""
        result = subprocess.run(
            ["claude", "setup-token"],
            capture_output=False,
        )
        if result.returncode == 0:
            self._use_subscription = True
            self._api_key = None
            return True
        return False

    def get_options_env(self) -> dict[str, str]:
        if self._api_key:
            return {"ANTHROPIC_API_KEY": self._api_key}
        # Empty string forces OAuth
        return {"ANTHROPIC_API_KEY": ""}

    def logout(self) -> None:
        self._api_key = None
        self._use_subscription = False
        # Optionally remove credentials file
        creds = Path.home() / ".claude" / ".credentials.json"
        if creds.exists():
            creds.unlink()
```

### Example 4: Production Service with API Key

```python
from claude_agent_sdk import ClaudeAgentOptions, query
import os


async def production_handler(prompt: str) -> str:
    """Serverless handler using API key auth."""
    api_key = os.environ["ANTHROPIC_API_KEY"]

    options = ClaudeAgentOptions(
        env={"ANTHROPIC_API_KEY": api_key},
        allowed_tools=["Read"],
        max_turns=3,
        max_budget_usd=0.50,
        permission_mode="bypassPermissions",
    )

    result = ""
    async for msg in query(prompt, options=options):
        if hasattr(msg, "content"):
            result = msg.content

    return result
```

## Best Practices

### Authentication Selection

| Scenario | Recommended Method |
|----------|-------------------|
| CI/CD pipelines | API Key |
| Serverless functions | API Key |
| Local development | Subscription |
| Interactive CLI tools | Subscription |
| Team shared environments | API Key (shared service account) |
| Cost-sensitive production | API Key (granular tracking) |

### Security Checklist

1. Never commit API keys to source control
2. Use environment variables or secrets managers
3. Implement key rotation for production
4. Log authentication method, not credentials
5. Handle auth failures gracefully with user guidance

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| API billing when expecting subscription | Set `env={"ANTHROPIC_API_KEY": ""}` explicitly |
| Credentials file not found | Guide user to run `claude setup-token` |
| Token refresh fails silently | Catch ProcessError and check exit codes |
| Hardcoded API keys | Load from environment or config |
| Missing auth status feedback | Check and display auth method at startup |

### Logging Authentication

```python
import logging

logger = logging.getLogger(__name__)

def log_auth_status(auth: AuthManager) -> None:
    status = auth.get_status()
    logger.info(
        "Authentication configured",
        extra={
            "method": status.method.value,
            "description": status.description,
            # Never log actual tokens or keys
        }
    )
```
