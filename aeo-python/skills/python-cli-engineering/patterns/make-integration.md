# Make Integration for CLI Tools

Patterns for integrating Python CLI applications with Make in mono-repos, enabling convenient command execution from the repository root.

## Use Case

Mono-repos with multiple CLI applications benefit from centralized command access:

**Without Make integration:**
```bash
cd apps/my-cli-app && uv run my-cli-app sync --vendors-only
cd ../example-processor && uv run example-processor transform --format csv
cd ../example-client && uv run example-client fetch --limit 100
```

**With Make integration:**
```bash
make my-cli-app sync --vendors-only
make example-processor transform --format csv
make example-client fetch --limit 100
```

**Benefits:**
- Run from repo root (no cd required)
- Consistent interface across apps
- Shorter commands
- Easy to remember

---

## The Challenge: Flag Handling

Make interprets `--flags` as Make options, not CLI parameters.

### Problem Example

```makefile
# ❌ WRONG - Make consumes --vendors-only
my-cli-app:
    uv run my-cli-app $(MAKECMDGOALS)
```

```bash
make my-cli-app sync --vendors-only
# Error: make: invalid option -- 'v'
# Make tries to interpret --vendors-only as Make option!
```

---

## Solution: ARGS Variable Pattern

Use a Make variable to pass flags to the CLI command.

### Makefile Implementation

```makefile
# Makefile at repo root

.PHONY: my-cli-app

my-cli-app:
    @cd apps/my-cli-app && uv run my-cli-app $(ARGS) $(filter-out $@,$(MAKECMDGOALS))

# Catch-all rule to prevent Make treating args as targets
%:
    @:
```

**Explanation:**
- `@cd apps/my-cli-app` - Navigate to app directory
- `uv run my-cli-app` - Run CLI command
- `$(ARGS)` - Pass ARGS variable (for --flags)
- `$(filter-out $@,$(MAKECMDGOALS))` - Pass positional arguments
- `%: @:` - Catch-all to prevent errors on non-target arguments

### Usage

**With flags (using ARGS variable):**
```bash
make my-cli-app ARGS="sync --vendors-only"
make my-cli-app ARGS="analyze --top 25"
make my-cli-app ARGS="duplicates --threshold 0.90"
```

**Without flags (positional arguments only):**
```bash
make my-cli-app sync
make my-cli-app analyze
make my-cli-app help
```

**Combining both:**
```bash
make my-cli-app ARGS="--verbose" sync
```

---

## Complete Example

### Makefile (Repo Root)

```makefile
# Makefile (repository root)

.PHONY: my-cli-app example-processor example-client

# My CLI app
my-cli-app:
    @cd apps/my-cli-app && uv run my-cli-app $(ARGS) $(filter-out $@,$(MAKECMDGOALS))

# Data processor CLI
example-processor:
    @cd apps/example-processor && uv run example-processor $(ARGS) $(filter-out $@,$(MAKECMDGOALS))

# API client CLI
example-client:
    @cd apps/example-client && uv run example-client $(ARGS) $(filter-out $@,$(MAKECMDGOALS))

# Catch-all rule
%:
    @:
```

### App Structure

```
repo-root/
├── Makefile                          # Root Makefile
├── apps/
│   ├── my-cli-app/
│   │   ├── pyproject.toml
│   │   └── src/my_cli_app/
│   │       └── cli/main.py           # Typer CLI
│   ├── example-processor/
│   │   └── ...
│   └── example-client/
│       └── ...
```

---

## Advanced Patterns

### Help Target

```makefile
help:
    @echo "Available CLI tools:"
    @echo "  make my-cli-app [ARGS='flags'] [command]"
    @echo "  make example-processor [ARGS='flags'] [command]"
    @echo ""
    @echo "Examples:"
    @echo "  make my-cli-app sync"
    @echo "  make my-cli-app ARGS='--verbose' analyze"
    @echo "  make my-cli-app ARGS='sync --vendors-only'"
```

### All Apps Target

```makefile
all-sync:
    @make my-cli-app sync
    @make example-processor sync
    @make example-client sync
```

### Conditional Targets

```makefile
my-cli-sync-prod:
    @cd apps/my-cli-app && ENV=production uv run my-cli-app sync

my-cli-sync-dev:
    @cd apps/my-cli-app && ENV=development uv run my-cli-app sync
```

---

## Alternative: Shell Script Wrapper

For more complex logic, use shell scripts instead of Make:

```bash
#!/bin/bash
# bin/my-cli-app

cd "$(dirname "$0")/../apps/my-cli-app" || exit 1
uv run my-cli-app "$@"
```

```bash
# Usage (after chmod +x bin/my-cli-app)
bin/my-cli-app sync --vendors-only
```

**Benefits:**
- Simpler flag passing ($@)
- More readable for complex logic
- Easier debugging

**Downsides:**
- Requires chmod +x
- Not as familiar as Make
- Separate file per CLI

---

## Reference Implementation

```makefile
.PHONY: my-cli-app

my-cli-app:
    @cd apps/my-cli-app && uv run my-cli-app $(ARGS) $(filter-out $@,$(MAKECMDGOALS))

%:
    @:

# Usage examples in comments
# make my-cli-app sync
# make my-cli-app ARGS="sync --vendors-only"
# make my-cli-app ARGS="analyze --top 25"
```

---

## Related Patterns

**This Skill:**
- [../examples/](../examples/) - CLI application examples
- [../templates/Makefile](../templates/Makefile) - Makefile template

---

## Summary

**Key Points:**

1. **ARGS variable** - Pass flags through Make safely
2. **filter-out pattern** - Pass positional arguments
3. **Catch-all rule** (`%: @:`) - Prevent Make errors on arguments
4. **@cd pattern** - Navigate to app directory
5. **Easy usage** - `make app-name ARGS="--flags" command`

**This pattern solves Make's flag handling limitation, enabling convenient CLI access from mono-repo root.**
