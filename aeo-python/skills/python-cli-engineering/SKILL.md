---
name: python-cli-engineering
description: Engineer production-grade Python CLI tools with UV for package management, Ruff for linting, Pyright for strict typing, Typer for commands, and Rich for polished output. Addresses fail-fast patterns, pydantic-settings configuration, modular code organization, and professional UX conventions. Apply when creating admin utilities, data processors, or developer tooling.
allowed-tools: Read, Write, Edit, Bash
---

# Python CLI Engineering

Modern patterns for building production-grade Python command-line applications.

## When to Use This Skill

Use when building:
- Command-line tools and utilities
- Data processing applications
- Admin/operations tooling
- Developer utilities
- ETL/sync scripts with user interaction
- Analysis tools with formatted output
- Database management CLIs

---

## Technology Stack Overview

### Core Tools
- **UV** - Package manager (10-100x faster than pip/poetry)
- **Ruff** - Linting + formatting (Rust-based, replaces 6+ tools)
- **Pyright** - Type checking in strict mode (3-5x faster than mypy)
- **Typer** - CLI framework with type hints + auto-help
- **Rich** - Console output with colors, tables, progress bars

**Installation:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install UV
uv init my-cli          # Initialize project
uv add typer rich       # Add dependencies
```

**For complete tool guides, configuration examples, and advanced patterns:**
See [references/tech-stack.md](references/tech-stack.md)

---

## Fail-Fast Discipline

### Core Principles

1. **No default values** (except in explicit config files)
2. **No try/catch swallowing** (let exceptions propagate)
3. **No fallback mechanisms** (fail immediately on errors)
4. **Explicit configuration** (missing config = app stops)
5. **Type everything** (strict Pyright mode)

### Exception Handling Pattern

```python
# Custom exceptions (core/exceptions.py)
class AppError(Exception):
    """Base exception - let it bubble up."""
    pass

# CLI main entry (cli/main.py)
def main() -> None:
    """Main entry point - ONLY catch at top level."""
    try:
        app()
    except AppError as e:
        console.print(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(code=1) from e
```

**Key Rules:**
- ❌ **Never**: `except Exception: pass` or `except: return None`
- ✅ **Always**: Let exceptions bubble to main entry point
- ✅ **Always**: Use specific exception types for different failure modes
- ✅ **Always**: Exit with non-zero code on failure

---

## Modular Architecture

### Module Size Constraints

**CRITICAL RULE: 500 lines maximum per module**

When module approaches 500 lines:
1. Extract related functions to new module
2. Split by domain/responsibility
3. Create subpackage if >3 related modules

### Project Structure

```
my_cli/
├── pyproject.toml          # UV project config
├── .env.example            # Template for .env
├── config.yaml            # Application defaults
├── Makefile               # Development tasks
└── src/
    └── my_cli/
        ├── __init__.py
        ├── __main__.py         # Entry point
        ├── cli/                # CLI commands
        │   ├── __init__.py
        │   └── commands.py     # Typer app
        ├── core/               # Business logic
        │   ├── __init__.py
        │   ├── config.py       # pydantic-settings
        │   └── exceptions.py
        ├── db/                 # Database layer
        │   ├── __init__.py
        │   ├── models.py       # SQLAlchemy models
        │   └── connection.py
        └── services/           # External integrations
            └── __init__.py
```

**For complete architecture patterns, module organization, and size management:**
See [references/architecture.md](references/architecture.md)

---

## Configuration Pattern

### Dual Configuration (YAML + .env)

**Pattern:** Merge YAML defaults with .env overrides using pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str  # Must be in .env

    # API
    api_key: str
    api_url: str = "https://api.example.com"

settings = Settings()  # Fails if db_password or api_key missing
```

**config.yaml** (defaults):
```yaml
db_host: localhost
db_port: 5432
api_url: https://api.example.com
```

**.env** (secrets):
```bash
DB_PASSWORD=secret
API_KEY=abc123
```

**For complete configuration patterns, validation, and advanced examples:**
See [references/configuration.md](references/configuration.md)

---

## Quick Start

### 1. Initialize Project

```bash
uv init my-cli
cd my-cli
uv add typer rich pydantic-settings pyyaml
uv add --dev ruff pyright pytest
```

### 2. Create Entry Point

```python
# src/my_cli/__main__.py
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def hello(name: str) -> None:
    """Say hello."""
    console.print(f"[green]Hello {name}![/green]")

if __name__ == "__main__":
    app()
```

### 3. Configure Tools

Copy configuration templates:
- [templates/pyproject.toml](templates/pyproject.toml) - UV + Ruff + Pyright config
- [templates/Makefile](templates/Makefile) - Development tasks

### 4. Run

```bash
uv run python -m my_cli hello World
```

---

## Development Workflow

### Standard Tasks (via Makefile)

```bash
make lint       # Run ruff check + format
make type       # Run pyright
make test       # Run pytest
make check      # lint + type + test
make clean      # Remove build artifacts
```

### Pre-commit Checks

**Always run before committing:**
```bash
make check
```

**Why:** Catches type errors, style issues, and test failures early

---

## Common Patterns

### Advanced Pattern References

**Build integration**: See [patterns/make-integration.md](patterns/make-integration.md) - Integrate CLI with Makefiles
**Multi-method authentication**: See [patterns/multi-method-auth.md](patterns/multi-method-auth.md) - Support OAuth, TBA, API keys
**PostgreSQL JSONB**: See [patterns/postgresql-jsonb.md](patterns/postgresql-jsonb.md) - Flexible schema with JSONB columns
**Pydantic flexibility**: See [patterns/pydantic-flexible.md](patterns/pydantic-flexible.md) - Handle dynamic/unknown fields
**Schema resilience**: See [patterns/schema-resilience.md](patterns/schema-resilience.md) - Robust API schema handling
**Database migrations**: See [reference/database-migrations.md](reference/database-migrations.md) - Alembic migration patterns

### CLI Command with Config

```python
@app.command()
def sync(
    config_file: Path = typer.Option("config.yaml"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Sync data from source."""
    settings = Settings(_env_file=".env")
    if verbose:
        console.print(f"[yellow]Connecting to {settings.db_host}[/yellow]")
    # Implementation
```

### Database Connection with SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine(f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}")
Session = sessionmaker(bind=engine)
```

### Rich Progress Bar

```python
from rich.progress import track

for item in track(items, description="Processing..."):
    process(item)
```

---

## Error Handling

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base for all app exceptions."""
    pass

class ConfigurationError(AppError):
    """Config missing/invalid."""
    pass

class DatabaseError(AppError):
    """DB operation failed."""
    pass

class ExternalServiceError(AppError):
    """External API failed."""
    pass
```

### Usage in Commands

```python
@app.command()
def process() -> None:
    """Process data."""
    if not settings.api_key:
        raise ConfigurationError("API_KEY not set in .env")

    try:
        response = api.fetch_data()
    except Exception as e:
        raise ExternalServiceError(f"API fetch failed: {e}") from e

    # Process response (let exceptions bubble)
```

---

## Type Checking Best Practices

### Strict Mode Configuration

```toml
[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
reportMissingTypeStubs = true
reportUnknownMemberType = true
```

### Common Type Patterns

```python
from typing import Any
from collections.abc import Sequence

# Function signatures
def process_items(items: Sequence[dict[str, Any]]) -> list[str]:
    return [item["name"] for item in items]

# Optional values
from typing import Optional
def get_value(key: str) -> Optional[str]:
    return cache.get(key)  # Returns str | None

# Type guards
from typing import TypeGuard
def is_string_list(val: list[Any]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)
```

---

## Testing

### Pytest Structure

```
tests/
├── conftest.py           # Fixtures
├── test_cli.py          # CLI command tests
├── test_config.py       # Config loading tests
└── test_services.py     # Service integration tests
```

### Testing CLI Commands

```python
from typer.testing import CliRunner

runner = CliRunner()

def test_hello_command():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World" in result.stdout
```

---

## Deployment

### Building Distribution

```bash
uv build                 # Creates wheel + sdist
ls dist/                 # my_cli-0.1.0-py3-none-any.whl
```

### Installing

```bash
uv pip install dist/my_cli-0.1.0-py3-none-any.whl
my-cli hello World       # Now available as command
```

---

## Key Principles Summary

1. **Fail Fast** - No silent errors, no defaults for critical config
2. **Type Everything** - Strict Pyright mode catches issues early
3. **Modular** - 500-line max per module, clear separation of concerns
4. **Explicit Config** - YAML defaults + .env secrets, no magic
5. **Rich Output** - Professional CLI UX with colors and progress
6. **UV for Speed** - 10-100x faster than traditional tools
7. **Test Early** - pytest + type checking before commit

---

**For detailed guides:** See [references/](references/) directory
**For project templates:** See [templates/](templates/) directory

**End of Skill**
