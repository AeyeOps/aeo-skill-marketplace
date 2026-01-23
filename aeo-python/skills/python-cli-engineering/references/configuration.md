# Configuration Patterns

Dual configuration using YAML defaults + .env overrides with pydantic-settings.

## Dual Configuration Strategy

### Why YAML + .env?

**YAML (config.yaml):**
- Default values that are safe to commit
- Common across all environments
- Team-wide shared configuration
- Nested structures, lists, complex data

**.env (not committed):**
- Secrets and credentials
- Environment-specific overrides
- Developer/deployment-specific values
- Simple key=value format

**pydantic-settings:**
- Type validation
- Automatic merging
- Fail-fast on missing required values
- Environment variable overrides

---

## Basic Pattern

### config.yaml (committed)
```yaml
app:
  name: my-cli
  version: 1.0.0

database:
  host: localhost
  port: 5432
  name: mydb

api:
  base_url: https://api.example.com
  timeout: 30
  retry_attempts: 3

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### .env (NOT committed)
```bash
# Database credentials
DB_USER=my_user
DB_PASSWORD=secret123

# API keys
API_KEY=abc123def456

# Environment override
DB_HOST=prod-db.example.com
LOGGING_LEVEL=DEBUG
```

### .env.example (committed template)
```bash
# Database credentials
DB_USER=
DB_PASSWORD=

# API keys
API_KEY=

# Optional overrides
# DB_HOST=localhost
# LOGGING_LEVEL=INFO
```

---

## Implementation with pydantic-settings

### Basic Settings Class

```python
# core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with YAML defaults and .env overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # DB__HOST -> db.host
        case_sensitive=False,       # DB_HOST or db_host both work
    )

    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "mydb"
    db_user: str  # Required - must be in .env
    db_password: str  # Required - must be in .env

    # API settings
    api_base_url: str = "https://api.example.com"
    api_timeout: int = 30
    api_key: str  # Required - must be in .env

    # Logging
    logging_level: str = "INFO"
    logging_format: str = "%(asctime)s - %(levelname)s - %(message)s"

# Create singleton instance
settings = Settings()
```

### Loading YAML First

```python
# core/config.py
from pathlib import Path
import yaml
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    db_host: str = "localhost"
    db_password: str  # Must be in .env

    @classmethod
    def from_yaml(cls, yaml_path: Path = Path("config.yaml")) -> "Settings":
        """Load YAML defaults, then override with .env."""
        if yaml_path.exists():
            with open(yaml_path) as f:
                yaml_data = yaml.safe_load(f)
            # Flatten nested YAML
            flat_data = _flatten_dict(yaml_data)
            return cls(**flat_data)
        return cls()

def _flatten_dict(d: dict, parent_key: str = "") -> dict:
    """Flatten nested dict: {'db': {'host': 'x'}} -> {'db_host': 'x'}"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

settings = Settings.from_yaml()
```

---

## Advanced Patterns

### Nested Configuration

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    password: str

class APIConfig(BaseModel):
    base_url: str
    api_key: str
    timeout: int = 30

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    database: DatabaseConfig
    api: APIConfig

# In .env:
# DATABASE__HOST=localhost
# DATABASE__USER=admin
# DATABASE__PASSWORD=secret
# API__BASE_URL=https://api.example.com
# API__API_KEY=abc123
```

### Validation and Computed Fields

```python
from pydantic import field_validator, computed_field

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @field_validator("db_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be 1-65535")
        return v

    @computed_field
    @property
    def db_url(self) -> str:
        """Construct database URL from components."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
```

### Multiple Environments

```python
from enum import Enum

class Environment(str, Enum):
    DEV = "development"
    STAGING = "staging"
    PROD = "production"

class Settings(BaseSettings):
    environment: Environment = Environment.DEV

    # Different API URLs per environment
    @computed_field
    @property
    def api_base_url(self) -> str:
        urls = {
            Environment.DEV: "https://dev-api.example.com",
            Environment.STAGING: "https://staging-api.example.com",
            Environment.PROD: "https://api.example.com",
        }
        return urls[self.environment]

# In .env:
# ENVIRONMENT=production
```

---

## CLI Integration

### Loading Config in Commands

```python
# cli/commands.py
import typer
from pathlib import Path
from my_cli.core.config import Settings
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def sync(
    config: Path = typer.Option(
        "config.yaml",
        "--config",
        "-c",
        help="Config file path"
    ),
) -> None:
    """Sync data using configured settings."""
    try:
        settings = Settings.from_yaml(config)
    except Exception as e:
        console.print(f"[red]Config error: {e}[/red]")
        raise typer.Exit(1) from e

    console.print(f"[green]Connecting to {settings.db_host}[/green]")
    # Use settings...
```

### Config Validation Command

```python
@app.command()
def check_config() -> None:
    """Validate configuration."""
    try:
        settings = Settings()
        console.print("[green]✓ Configuration valid[/green]")
        console.print(f"  DB: {settings.db_host}:{settings.db_port}")
        console.print(f"  API: {settings.api_base_url}")
    except Exception as e:
        console.print(f"[red]✗ Configuration invalid: {e}[/red]")
        raise typer.Exit(1) from e
```

---

## Error Handling

### Missing Required Values

```python
from my_cli.core.exceptions import ConfigurationError

class Settings(BaseSettings):
    api_key: str  # Required

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
        except Exception as e:
            if "api_key" in str(e):
                raise ConfigurationError(
                    "API_KEY not found in .env file. "
                    "Copy .env.example to .env and set API_KEY."
                ) from e
            raise
```

### Type Validation Errors

```python
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    for error in e.errors():
        field = error["loc"][0]
        message = error["msg"]
        console.print(f"[red]Config error in {field}: {message}[/red]")
    raise typer.Exit(1) from e
```

---

## Best Practices

### 1. Never Commit Secrets
```bash
# Add to .gitignore
.env
*.local
*.secret
```

### 2. Provide .env.example
```bash
# Complete template with all required variables
cp .env.example .env
# Fill in actual values
```

### 3. Fail Fast on Missing Config
```python
# Don't use defaults for secrets
api_key: str  # No default = required

# Not this:
api_key: str = "changeme"  # Security risk!
```

### 4. Document All Settings
```python
from pydantic import Field

class Settings(BaseSettings):
    api_key: str = Field(
        ...,
        description="API key for external service (get from dashboard)"
    )
    db_password: str = Field(
        ...,
        description="Database password (set in .env)"
    )
```

### 5. Use Type Hints Strictly
```python
# ✅ Good - explicit types
db_port: int = 5432
retry_attempts: int = 3

# ❌ Bad - unclear types
port = 5432  # type unknown to pydantic
```

---

## Testing with Config

### Override Settings in Tests

```python
# tests/conftest.py
import pytest
from my_cli.core.config import Settings

@pytest.fixture
def test_settings():
    """Provide test configuration."""
    return Settings(
        db_host="localhost",
        db_port=5432,
        db_user="test_user",
        db_password="test_pass",
        api_key="test_key",
    )

# tests/test_cli.py
def test_sync_command(test_settings):
    # Use test_settings instead of real settings
    pass
```

### Temporary .env for Tests

```python
# tests/test_config.py
from pathlib import Path
import tempfile

def test_env_loading():
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("API_KEY=test123\nDB_PASSWORD=secret\n")

        settings = Settings(_env_file=str(env_file))
        assert settings.api_key == "test123"
```

---

## Example: Complete Setup

### config.yaml
```yaml
database:
  host: localhost
  port: 5432
  name: myapp

api:
  base_url: https://api.example.com
  timeout: 30

logging:
  level: INFO
```

### .env (create from .env.example)
```bash
DB_USER=myapp_user
DB_PASSWORD=supersecret
API_KEY=abc123def456ghi789
```

### core/config.py
```python
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Database (YAML defaults + .env secrets)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "myapp"
    db_user: str  # From .env
    db_password: str  # From .env

    # API (YAML defaults + .env secrets)
    api_base_url: str = "https://api.example.com"
    api_timeout: int = 30
    api_key: str  # From .env

    # Logging (YAML defaults)
    logging_level: str = "INFO"

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
```

### Usage in CLI
```python
from my_cli.core.config import settings

@app.command()
def sync() -> None:
    """Sync data."""
    console.print(f"Connecting to {settings.db_host}")
    console.print(f"API: {settings.api_base_url}")
```

This completes the dual configuration pattern implementation.
