# Reference mode — full reference

Reference is **scannable, factual, exhaustive lookup** for a reader who already knows what they need. Different *types* of reference have different shapes — pick the matching template below.

## Reference types

| Type | Path / filename | When to use |
|------|----------------|-------------|
| API | `[component]-api.md` | Methods, classes, functions, return types, exceptions |
| Configuration | `[feature]-config.md` | Config file options, env vars, valid values, defaults |
| CLI | `[tool]-cli.md` | Commands, subcommands, flags, exit codes |
| Data schema | `[data]-schema.md` | Event/message/record formats, field constraints |
| Error codes | `error-codes.md` | Error codes/messages, causes, related troubleshooting |

## API reference template

```markdown
# [Class/Module/Service] API Reference

## Overview

[Brief factual description of purpose and scope. One short paragraph.]

## Class: [ClassName]

[Brief description of what this class represents.]

### Constructor

```python
ClassName(
    param1: Type,
    param2: Type = default_value,
    **kwargs
)
```

**Parameters**:

- `param1` (Type): [Description]
- `param2` (Type, optional): [Description]. Default: `default_value`
- `**kwargs`: Additional options (see Options)

**Returns**: ClassName instance

**Raises**:

- `ValueError`: [When raised]
- `TypeError`: [When raised]

**Example**:

```python
>>> obj = ClassName("value", param2=True)
>>> obj.param1
'value'
```

### Methods

#### `method_name()`

```python
method_name(arg1: Type, arg2: Optional[Type] = None) -> ReturnType
```

**Purpose**: [One-line description]

**Parameters**, **Returns**, **Raises**, **Example** — same shape as constructor.

### Properties

#### `property_name`

- **Type**: Type
- **Access**: Read / Write / Read-only
- **Description**: [What this property represents]

### Related classes

- `RelatedClass`: [Brief description of relationship]
```

## Configuration reference template

```markdown
# Configuration Reference

## File format

[Supported formats: YAML, JSON, TOML, etc.]

## Configuration structure

```yaml
# Complete configuration example
setting_group:
  option1: value
  option2: value
  nested_group:
    nested_option: value
```

## Options

For nested / dotted keys, use the dotted form as the heading and group siblings under their shared parent — e.g. `### mesh` with `#### mesh.endpoint`, `#### mesh.auth_token_path` underneath. This keeps the table of contents readable and matches how readers reference the option in config files.

### `setting_group`

Configuration for [specific functionality].

#### `option1`

- **Type**: string
- **Required**: yes
- **Description**: [What this option controls]
- **Valid values**: `value1`, `value2`, `value3`
- **Default**: no default

**Example**:

```yaml
setting_group:
  option1: "value1"
```

#### `option2`

- **Type**: integer
- **Required**: no
- **Range**: 1–100
- **Default**: `10`

[Continue per option.]

## Environment variables

If the project supports a uniform env-var scheme (e.g. prefix + dot-to-underscore + uppercase), state the rule once instead of repeating it per row:

> All options can be set via env vars by prefixing with `APP_` and replacing dots with underscores. Example: `setting_group.option1` → `APP_SETTING_GROUP_OPTION1`.

Only list a table when overrides are *not* uniform (e.g., some env vars use legacy names). The table maps env var to config option — descriptions live with the option above, don't repeat them here:

| Env var | Config option | Type |
|---------|---------------|------|
| `APP_LEGACY_NAME` | `setting_group.option1` | string |

## Validation

[How config is validated and how errors surface.]
```

## CLI reference template

```markdown
# CLI Command Reference

## Synopsis

```bash
command [GLOBAL_OPTIONS] <subcommand> [SUBCOMMAND_OPTIONS] [ARGUMENTS]
```

## Global options

### `--help`, `-h`
Show help and exit.

### `--version`, `-v`
Show version and exit.

### `--config PATH`

- **Type**: file path
- **Default**: `~/.config/app/config.yaml`

### `--verbose`, `-V`

- **Type**: flag (repeatable for higher verbosity)

## Subcommands

### `init`

Initialize a new project or configuration.

**Synopsis**:
```bash
command init [OPTIONS] [DIRECTORY]
```

**Arguments**:
- `DIRECTORY` (optional): Target directory. Default: current directory

**Options**:

#### `--template TEMPLATE`
- **Type**: string
- **Valid values**: `basic`, `advanced`, `custom`
- **Default**: `basic`

#### `--force`, `-f`
- **Type**: flag — overwrite existing files

**Examples**:
```bash
command init                          # Initialize in current directory
command init --template advanced      # Use advanced template
command init --force /path/to/dir     # Force overwrite in specific directory
```

[Repeat per subcommand.]

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Network error |
```

## Quality checklist

- [ ] **Complete coverage** — all public APIs / options / commands documented
- [ ] **Consistent format** — same shape for similar items (every method has the same Parameters/Returns/Raises sections)
- [ ] **Accurate specs** — types, defaults, ranges have been verified
- [ ] **Brief examples** — every non-trivial item has a working example, but examples stay short
- [ ] **Cross-references** — related items link to each other
- [ ] **Searchable structure** — predictable headings, alphabetical or logical ordering inside each section
- [ ] **Version info** included where relevant
- [ ] **Deprecation notices** present for retired surfaces

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Tutorial creep | Step-by-step instructions in a reference | Brief examples only; link to a tutorial |
| Opinion injection | "We recommend using X because..." in the spec | Stick to facts; link to an explanation doc |
| Incomplete coverage | Missing parameters, methods, or edge cases | Systematic audit against the source |
| Inconsistent format | Different shapes for similar items | Use the templates above; deviate only when justified |
| Example novel | 30-line example that obscures the spec | Keep examples 3–8 lines; show usage, not a tutorial |

## Voice and register

- Dry, factual, third-person. No "we", no "you should". State what something *is* and what it *does*.
- Every option/parameter gets the same fields in the same order — predictability is the whole point.
- No design rationale. If a parameter exists for non-obvious reasons, link to an explanation doc; don't inline the reasoning.

## Output

- **Path**: `docs/reference/`
- **Filenames**: `[component]-api.md`, `[feature]-config.md`, `[tool]-cli.md`, `[data]-schema.md`, `error-codes.md`, `[system]-reference.md`

## Information architecture

- **Hierarchical** by default for APIs (Module → Class → Method/Property)
- **Alphabetical** when there's no logical grouping (e.g. config option lists with no obvious group)
- **Functional** when grouping by user workflow makes the reference more findable

## Success and failure indicators

**Success**: Readers can find specific information quickly, all public surfaces are covered, the format is consistent enough that scanning is fast, cross-references go where the reader expects.

**Failure**: Information is missing, inaccurate, or inconsistently formatted. Examples don't work or are misleading. Cross-references are dead ends.
