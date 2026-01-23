# Multi-Method Authentication Abstraction

Factory pattern for supporting multiple authentication methods in a single Python application, enabling gradual migration and environment-specific auth.

## When to Use

Implement multi-method authentication when:
- **Migrating between auth methods** (e.g., OAuth 1.0 → OAuth 2.0)
- **Different environments use different auth** (sandbox vs production)
- **User/deployment choice** of authentication method
- **Backward compatibility required** during transition

**Example:** NetSuite deprecates TBA (OAuth 1.0) in February 2025, requiring migration to OAuth 2.0.

---

## Factory Pattern

### Abstract Base Class

Define common interface for all authentication methods:

```python
from abc import ABC, abstractmethod

class AuthProvider(ABC):
    """Abstract base class for authentication providers"""

    @abstractmethod
    def get_auth_headers(self, url: str, method: str) -> dict[str, str]:
        """Generate authentication headers for a request

        Args:
            url: Full request URL (may be needed for signature generation)
            method: HTTP method (GET, POST, etc.)

        Returns:
            Dictionary of headers to add to request
        """
        pass
```

**Design note:** Interface accepts `url` parameter because some auth methods (OAuth 1.0) need the complete URL for signature generation. Implementations that don't need it can ignore the parameter.

### Concrete Implementations

```python
# oauth1_provider.py
import hmac
import hashlib
import base64
import time
import secrets
from urllib.parse import urlparse, parse_qsl, quote

class OAuth1Provider(AuthProvider):
    """OAuth 1.0 authentication provider"""

    def __init__(self, consumer_key, consumer_secret, token_id, token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret

    def get_auth_headers(self, url: str, method: str) -> dict[str, str]:
        """Generate OAuth 1.0 signature and build Authorization header

        URL and method required for signature calculation
        """
        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_token": self.token_id,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_version": "1.0",
        }

        signature = self._generate_signature(url, method, oauth_params)
        oauth_params["oauth_signature"] = signature

        auth_header = "OAuth " + ", ".join(
            f'{quote(k, safe="")}="{quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        return {"Authorization": auth_header}

    def _generate_signature(self, url, method, oauth_params):
        """Generate HMAC-SHA256 signature (includes query params from URL)"""
        # Implementation details...
        # See OAuth 1.0a RFC 5849 for complete signature generation algorithm
        pass

# oauth2_provider.py
import httpx
import base64
from datetime import datetime, timedelta

class OAuth2Provider(AuthProvider):
    """OAuth 2.0 Client Credentials provider"""

    def __init__(self, token_url, consumer_key, consumer_secret):
        self.token_url = token_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = None
        self.token_expiry = None

    def get_auth_headers(self, url: str, method: str) -> dict[str, str]:
        """Generate bearer token header

        URL and method not needed (OAuth 2.0 doesn't sign URLs)
        """
        token = self._get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _get_valid_token(self):
        """Get valid access token (cached or refresh)"""
        # Check cache
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry - timedelta(minutes=5):
                return self.access_token

        # Request new token
        self.access_token = self._request_token()
        self.token_expiry = datetime.now() + timedelta(hours=1)

        return self.access_token

    def _request_token(self):
        """Request new OAuth 2.0 access token"""
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = httpx.post(
            self.token_url,
            headers=headers,
            data={"grant_type": "client_credentials"}
        )
        response.raise_for_status()

        return response.json()["access_token"]
```

### Factory Function

```python
# auth_factory.py
from typing import Literal

AuthMethod = Literal["oauth1", "oauth2"]

def create_auth_provider(
    auth_method: AuthMethod,
    settings: dict
) -> AuthProvider:
    """Create appropriate auth provider based on configuration

    Args:
        auth_method: Authentication method to use
        settings: Configuration dict with credentials

    Returns:
        Configured authentication provider

    Raises:
        ValueError: If auth_method is unknown
    """
    if auth_method == "oauth1":
        return OAuth1Provider(
            consumer_key=settings["consumer_key"],
            consumer_secret=settings["consumer_secret"],
            token_id=settings["token_id"],
            token_secret=settings["token_secret"]
        )
    elif auth_method == "oauth2":
        return OAuth2Provider(
            token_url=settings["token_url"],
            consumer_key=settings["consumer_key"],
            consumer_secret=settings["consumer_secret"]
        )
    else:
        raise ValueError(
            f"Unknown authentication method: {auth_method}. "
            f"Valid options: 'oauth1', 'oauth2'"
        )
```

---

## Configuration

### YAML Configuration

```yaml
# config.yaml
application:
  auth_method: oauth2  # or "oauth1"
```

### Environment Variables

```bash
# .env
# OAuth 1.0 credentials (4 required)
CONSUMER_KEY=...
CONSUMER_SECRET=...
TOKEN_ID=...
TOKEN_SECRET=...

# OAuth 2.0 credentials (subset - only 2 needed)
# CONSUMER_KEY=...
# CONSUMER_SECRET=...
```

### Settings Model

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Account/API settings
    account_id: str
    base_url: str
    token_url: str

    # Credentials (all optional - depends on auth method)
    consumer_key: str
    consumer_secret: str
    token_id: str | None = None
    token_secret: str | None = None

    # Configuration
    class Config:
        env_file = ".env"
        case_sensitive = False  # CONSUMER_KEY = consumer_key

class YAMLConfig(BaseSettings):
    auth_method: str = "oauth2"

    class Config:
        yaml_file = "config.yaml"
```

---

## Client Integration

### HTTP Client with Pluggable Auth

```python
import httpx

class APIClient:
    """HTTP client with multi-method authentication"""

    def __init__(self, settings):
        self.base_url = settings.base_url
        # Factory creates appropriate provider
        self.auth = create_auth_provider(
            settings.yaml_config.auth_method,
            settings
        )
        self.http_client = httpx.Client(timeout=30.0)

    def request(self, method: str, endpoint: str, params=None, json=None):
        """Make authenticated HTTP request

        Auth headers generated automatically based on configured method
        """
        # Build full URL
        url = f"{self.base_url}/{endpoint}"
        if params:
            from urllib.parse import urlencode
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        # Get auth headers (method-specific)
        headers = self.auth.get_auth_headers(url=url, method=method)
        headers["Accept"] = "application/json"

        # Make request
        response = self.http_client.request(
            method=method,
            url=url,
            headers=headers,
            json=json
        )

        response.raise_for_status()
        return response.json()

    def get(self, endpoint, params=None):
        """HTTP GET"""
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint, json=None):
        """HTTP POST"""
        return self.request("POST", endpoint, json=json)
```

**Usage:**
```python
# Initialize client (auth method from config)
client = APIClient(settings)

# Use client (auth handled automatically)
vendors = client.get('vendors', params={"limit": 100})
# Auth method determined by config, not hardcoded!
```

---

## Migration Benefits

### Easy Configuration Toggle

Switch authentication methods without code changes:

```yaml
# Test OAuth 2.0
auth_method: oauth2

# Rollback to OAuth 1.0 if issues
auth_method: oauth1
```

### Gradual Migration

1. **Implement both providers**
2. **Deploy with OAuth 1.0** (existing method)
3. **Test OAuth 2.0** in staging
4. **Switch config** to OAuth 2.0
5. **Monitor production**
6. **Remove OAuth 1.0** code after successful migration

### Environment-Specific Auth

```yaml
# production.yaml
auth_method: oauth2

# sandbox.yaml
auth_method: oauth1  # Still testing OAuth 2.0
```

---

## Related Patterns

**This Skill:**
- [../reference/configuration.md](../reference/configuration.md) - Environment-specific config patterns
- [make-integration.md](make-integration.md) - CLI structure with Make integration

**Common Examples:**
- **GitHub API** - Personal access tokens + GitHub Apps (OAuth)
- **AWS Services** - IAM credentials + STS temporary tokens + SSO
- **Stripe API** - Test keys + live keys with different auth scopes
- **Salesforce** - Username/password + OAuth 2.0 + JWT bearer flow

**Standards:**
- OAuth 1.0a: RFC 5849
- OAuth 2.0: RFC 6749
- HTTP Authentication: RFC 7235

---

## Summary

**Key Points:**

1. **Abstract base class** - Common interface for all auth methods
2. **Factory pattern** - Create provider based on configuration
3. **Configuration-driven** - Switch methods via config, not code
4. **Interface flexibility** - Accept url parameter for signature-based auth
5. **Easy migration** - Test new method without removing old
6. **Environment-specific** - Different auth per environment if needed

**This pattern enables gradual, low-risk migration between authentication methods without code changes in the client layer.**
