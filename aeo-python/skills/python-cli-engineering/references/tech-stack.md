# Technology Stack Details

Complete guides for the modern Python CLI toolchain.

## UV Package Manager

### Why UV?
- **Speed**: 10-100x faster than pip, poetry
- **Written in Rust**: Compiled performance
- **Standards-compliant**: Uses pyproject.toml, compatible with PEP standards
- **Integrated**: Handles venvs, dependencies, builds in one tool

### Installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Complete Command Reference
```bash
# Project lifecycle
uv init my-project                  # Create new project
uv add package==1.2.3               # Add specific version
uv add --dev pytest                 # Add development dependency
uv remove package                   # Remove dependency
uv sync                             # Install all dependencies from lock file
uv lock                             # Update lock file without installing

# Running code
uv run script.py                    # Run in project venv
uv run python -m my_cli             # Run module
uv run pytest                       # Run dev dependency

# Building
uv build                            # Create wheel + sdist
uv publish                          # Publish to PyPI

# Environment management
uv venv                             # Create virtual environment
uv pip install package              # Pip-compatible interface
```

---

## Ruff Linter & Formatter

### Why Ruff?
- **Replaces multiple tools**: flake8, black, isort, pyupgrade, autoflake, pydocstyle
- **10-100x faster**: Written in Rust
- **Auto-fix**: Automatically fixes many issues
- **Drop-in replacement**: Compatible with existing configs

### Configuration Options
```toml
[tool.ruff]
line-length = 100              # Match black default or customize
target-version = "py312"        # Python version for code modernization

[tool.ruff.lint]
# Rule categories
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "W",      # pycodestyle warnings
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "RUF",    # Ruff-specific rules
]

# Common patterns to ignore
ignore = [
    "E501",   # Line too long (formatter handles this)
    "B008",   # Do not perform function call in argument defaults
]

[tool.ruff.format]
quote-style = "double"          # Use "double" quotes
indent-style = "space"          # Use spaces, not tabs
skip-magic-trailing-comma = false
```

### CLI Usage
```bash
ruff check .                   # Check all files
ruff check --fix .             # Auto-fix issues
ruff format .                  # Format code
ruff check --watch .           # Watch mode for development
```

---

## Pyright Type Checker

### Why Pyright over mypy?
- **Faster**: 3-5x faster, written in TypeScript
- **Stricter defaults**: Catches more issues out of the box
- **IDE integration**: Powers VS Code Pylance
- **Better errors**: More readable error messages

### Strict Mode Configuration
```toml
[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"

# Strict checks
reportMissingTypeStubs = true           # Warn about missing type stubs
reportUnknownMemberType = true          # Catch unknown attribute types
reportUnknownArgumentType = true        # Catch untyped function arguments
reportUnknownVariableType = true        # Catch untyped variables
reportUnknownParameterType = true       # Catch untyped parameters

# Strict inference
strictListInference = true              # Infer list types strictly
strictDictionaryInference = true        # Infer dict types strictly
strictSetInference = true               # Infer set types strictly

# Paths
include = ["src"]
exclude = ["**/__pycache__", ".venv"]
```

### Common Type Patterns
```python
from typing import Any, TypeGuard
from collections.abc import Sequence, Mapping

# Use Sequence instead of list for parameters (more flexible)
def process(items: Sequence[str]) -> list[str]:
    return [item.upper() for item in items]

# Use Mapping for readonly dict parameters
def configure(options: Mapping[str, Any]) -> None:
    pass

# Type guards for runtime checks
def is_str_list(val: list[Any]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)
```

---

## Typer CLI Framework

### Core Features
- Type hints automatically become CLI arguments
- Auto-generated help text from docstrings
- Built on Click (mature, battle-tested)
- Rich integration for beautiful output

### Complete Typer Patterns

**Basic Command:**
```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str) -> None:
    """Greet someone."""
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
```

**With Options and Arguments:**
```python
from pathlib import Path

@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Input file path"),
    output_dir: Path = typer.Option("./output", "--output", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    format: str = typer.Option("json", help="Output format"),
) -> None:
    """Process input file and save to output directory."""
    if verbose:
        typer.echo(f"Processing {input_file}")
```

**Sub-commands:**
```python
app = typer.Typer()
db_app = typer.Typer()
app.add_typer(db_app, name="db", help="Database commands")

@db_app.command("migrate")
def db_migrate() -> None:
    """Run database migrations."""
    pass

@db_app.command("seed")
def db_seed() -> None:
    """Seed database with test data."""
    pass
```

**Progress and Confirmation:**
```python
@app.command()
def delete(
    confirm: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete all data."""
    if not confirm:
        typer.confirm("Are you sure?", abort=True)

    with typer.progressbar(items, label="Deleting") as progress:
        for item in progress:
            delete_item(item)
```

---

## Rich Console Output

### Core Capabilities
- Colored text with markup
- Tables, trees, panels
- Progress bars
- Syntax highlighting
- Markdown rendering

### Rich Patterns

**Console with Colors:**
```python
from rich.console import Console

console = Console()

console.print("[green]Success![/green]")
console.print("[red]Error:[/red] Something went wrong")
console.print("[yellow]Warning:[/yellow] Check configuration")
```

**Tables:**
```python
from rich.table import Table

table = Table(title="Results")
table.add_column("Name", style="cyan")
table.add_column("Status", style="magenta")
table.add_column("Count", justify="right", style="green")

table.add_row("Item 1", "Active", "42")
table.add_row("Item 2", "Pending", "17")

console.print(table)
```

**Progress Bars:**
```python
from rich.progress import track

for item in track(items, description="Processing..."):
    process(item)

# Or with more control
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("[green]Downloading...", total=100)
    while not progress.finished:
        progress.update(task, advance=1)
```

**Panels and Groups:**
```python
from rich.panel import Panel

console.print(Panel("Important message", title="Alert", border_style="red"))
```

**Logging Integration:**
```python
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("my_app")
log.info("Application started")
```

---

## Integration Example

Complete example showing all tools working together:

```python
# src/my_cli/__main__.py
import typer
from rich.console import Console
from rich.table import Table
from pydantic_settings import BaseSettings

app = typer.Typer()
console = Console()

class Settings(BaseSettings):
    api_key: str
    model_config = {"env_file": ".env"}

@app.command()
def status(verbose: bool = typer.Option(False, "-v")) -> None:
    """Check system status."""
    settings = Settings()  # Fails fast if API_KEY missing

    if verbose:
        console.print("[yellow]Checking status...[/yellow]")

    table = Table(title="System Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("API", "✓ Connected")
    table.add_row("Database", "✓ Ready")

    console.print(table)

if __name__ == "__main__":
    app()
```

**Running:**
```bash
uv run python -m my_cli status --verbose
```

**Output:**
```
Checking status...
┌─────────────┬────────────┐
│ Service     │ Status     │
├─────────────┼────────────┤
│ API         │ ✓ Connected│
│ Database    │ ✓ Ready    │
└─────────────┴────────────┘
```
