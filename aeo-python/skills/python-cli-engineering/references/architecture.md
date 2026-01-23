# Modular Architecture Patterns

Guidelines for organizing Python CLI applications with strict module size constraints.

## Module Size Constraints

**CRITICAL RULE: 500 lines maximum per module**

### Why 500 Lines?
- Easier to understand and maintain
- Faster type checking and linting
- Clearer separation of concerns
- Forces good architectural decisions
- Reduces merge conflicts

### What Counts Toward 500 Lines?
- All code lines (imports, functions, classes, comments)
- Docstrings
- Blank lines for readability

**Does NOT count:**
- File header comments (license, copyright)
- Module-level docstrings (first docstring)

### When Module Approaches 500 Lines

**Step 1: Identify cohesive groups**
- Related functions/classes
- Domain boundaries
- Responsibility clusters

**Step 2: Extract to new module**
```python
# Before (models.py - 600 lines)
class User: pass
class UserRepository: pass
class Product: pass
class ProductRepository: pass

# After - Split by domain
# models/user.py (250 lines)
class User: pass
class UserRepository: pass

# models/product.py (250 lines)
class Product: pass
class ProductRepository: pass

# models/__init__.py
from .user import User, UserRepository
from .product import Product, ProductRepository
```

**Step 3: Create subpackage if needed**
When you have >3 related modules, group into subpackage:
```
services/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── client.py
│   ├── auth.py
│   └── endpoints.py
└── database/
    ├── __init__.py
    ├── connection.py
    └── queries.py
```

---

## Standard Project Structure

### Small CLI (Single Module)
```
my_cli/
├── pyproject.toml
├── .env.example
├── Makefile
├── README.md
└── src/
    └── my_cli/
        ├── __init__.py
        └── __main__.py     # All code here (<500 lines)
```

### Medium CLI (Multi-Module)
```
my_cli/
├── pyproject.toml
├── .env.example
├── config.yaml
├── Makefile
├── README.md
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   └── test_services.py
└── src/
    └── my_cli/
        ├── __init__.py
        ├── __main__.py         # Entry point only
        ├── cli/
        │   ├── __init__.py
        │   └── commands.py     # Typer commands
        ├── core/
        │   ├── __init__.py
        │   ├── config.py       # Settings
        │   └── exceptions.py   # Custom exceptions
        └── services/
            ├── __init__.py
            └── api.py          # External API client
```

### Large CLI (Subpackages)
```
my_cli/
├── pyproject.toml
├── .env.example
├── config.yaml
├── Makefile
├── README.md
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_db.py
│   └── test_services.py
└── src/
    └── my_cli/
        ├── __init__.py
        ├── __main__.py
        ├── cli/
        │   ├── __init__.py
        │   ├── app.py          # Main Typer app
        │   ├── sync.py         # Sync commands
        │   └── admin.py        # Admin commands
        ├── core/
        │   ├── __init__.py
        │   ├── config.py
        │   ├── exceptions.py
        │   └── logging.py
        ├── db/
        │   ├── __init__.py
        │   ├── models.py       # SQLAlchemy models
        │   ├── connection.py
        │   └── migrations/
        └── services/
            ├── __init__.py
            ├── api/
            │   ├── __init__.py
            │   ├── client.py
            │   └── auth.py
            └── processors/
                ├── __init__.py
                └── data.py
```

---

## Layer Separation

### CLI Layer
**Responsibility:** User interaction only
- Parse arguments/options
- Display output
- Handle user errors (validation, missing args)
- Call core layer

**Rules:**
- No business logic
- No database access
- No external API calls
- Only import from core/services layers

```python
# cli/commands.py
from my_cli.core.config import settings
from my_cli.services.api import fetch_data
from rich.console import Console

@app.command()
def sync() -> None:
    """Sync data from API."""
    try:
        data = fetch_data(settings.api_url)
        console.print(f"[green]Synced {len(data)} items[/green]")
    except AppError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e
```

### Core Layer
**Responsibility:** Business logic and configuration
- Application settings
- Custom exceptions
- Domain models
- Pure business logic (no I/O)

**Rules:**
- No CLI code (no typer, no rich)
- No direct database/API access
- Can be used by CLI and services

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_url: str
    api_key: str
    db_url: str

    model_config = {"env_file": ".env"}

settings = Settings()
```

### Services Layer
**Responsibility:** External interactions
- Database access
- API clients
- File I/O
- Message queues

**Rules:**
- Use core.config for settings
- Raise custom exceptions from core
- No CLI code
- No cross-service dependencies

```python
# services/api.py
from my_cli.core.config import settings
from my_cli.core.exceptions import APIError
import requests

def fetch_data(endpoint: str) -> list[dict]:
    """Fetch data from API."""
    response = requests.get(
        f"{settings.api_url}/{endpoint}",
        headers={"Authorization": f"Bearer {settings.api_key}"}
    )
    if not response.ok:
        raise APIError(f"API returned {response.status_code}")
    return response.json()
```

### Database Layer (if needed)
**Responsibility:** Database operations only
- SQLAlchemy models
- Database connection
- Queries and transactions
- Migrations

```python
# db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
```

---

## Import Rules

### Allowed Import Directions
```
CLI Layer → Core Layer
CLI Layer → Services Layer
CLI Layer → DB Layer

Services Layer → Core Layer
DB Layer → Core Layer

Core Layer → (no other layers)
```

### Anti-Pattern: Circular Imports
```python
# ❌ BAD: Circular dependency
# services/api.py
from my_cli.cli.commands import console  # NO!

# ✅ GOOD: Services don't know about CLI
# services/api.py
import logging
logger = logging.getLogger(__name__)
```

---

## Module Organization Patterns

### Pattern 1: Feature-Based
Organize by feature/domain:
```
my_cli/
└── features/
    ├── users/
    │   ├── commands.py    # CLI commands
    │   ├── models.py      # Domain models
    │   └── service.py     # Business logic
    └── products/
        ├── commands.py
        ├── models.py
        └── service.py
```

**Use when:**
- Features are independent
- Each feature has its own data model
- Team organized by feature

### Pattern 2: Layer-Based (Recommended)
Organize by technical layer:
```
my_cli/
├── cli/          # All CLI commands
├── core/         # All business logic
├── services/     # All external services
└── db/           # All database code
```

**Use when:**
- Cross-cutting concerns
- Shared infrastructure
- Traditional separation of concerns

### Pattern 3: Hybrid
Combine both approaches:
```
my_cli/
├── cli/
│   ├── users.py      # User commands
│   └── products.py   # Product commands
├── domain/
│   ├── users/
│   │   ├── models.py
│   │   └── service.py
│   └── products/
│       ├── models.py
│       └── service.py
└── infrastructure/
    ├── db/
    └── api/
```

**Use when:**
- Large applications
- Clear domain boundaries
- Multiple teams

---

## Dependency Injection Pattern

Instead of global singletons, use dependency injection:

```python
# services/api.py
class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def fetch(self, endpoint: str) -> list[dict]:
        # Implementation
        pass

# cli/commands.py
from my_cli.core.config import settings
from my_cli.services.api import APIClient

@app.command()
def sync() -> None:
    client = APIClient(settings.api_url, settings.api_key)
    data = client.fetch("users")
```

**Benefits:**
- Easier testing (inject mocks)
- No hidden global state
- Clear dependencies
- Better type checking

---

## Testing Structure

Match your source structure:
```
tests/
├── conftest.py              # Shared fixtures
├── cli/
│   └── test_commands.py     # CLI tests
├── core/
│   └── test_config.py       # Config tests
└── services/
    └── test_api.py          # Service tests
```

**Module size applies to tests too!**
- Keep test files under 500 lines
- Split by test category if needed
- Use fixtures to reduce duplication
