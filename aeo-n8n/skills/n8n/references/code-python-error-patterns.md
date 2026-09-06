# Error Patterns - Python Code Node

Common Python Code node errors and how to fix them, for the native Python runtime.

> **Removed in n8n 2.0**: the Pyodide helpers `_input`, `_json` — plus dot access on
> item data. Error patterns that only occurred with those helpers are gone from this file.

---

## Error Overview

**Top 5 Python Code Node Errors**:

1. **ModuleNotFoundError / ImportError** - Importing a module the runner does not allow (Python-specific)
2. **Empty Code / Missing Return** - No code or return statement
3. **KeyError** - Dictionary access without .get()
4. **IndexError** - List access without bounds checking
5. **Incorrect Return Format** - Wrong data structure returned

These 5 errors cover the majority of Python Code node failures.

**Before any of them**: if the node never runs at all, the instance is missing the prerequisite. From n8n 2.0
Python Code nodes execute only on task runners in **external mode** (`n8nio/runners` sidecar,
`N8N_NATIVE_PYTHON_RUNNER=true`). That is an operator fix, not a code fix.

---

## Error #1: ModuleNotFoundError (MOST CRITICAL)

**Frequency**: Very common in Python Code nodes

**What it is**: Importing a module that the runner image does not contain, or that the runner's allowlist does not
permit. Native Python denies insecure built-ins by default, and **every** import is gated - including the standard
library.

### The Problem

```python
# ❌ Never available - there is no HTTP client for Python in the Code node
import requests   # ModuleNotFoundError: No module named 'requests'

# ❌ Fails unless the runners image ships it AND N8N_RUNNERS_EXTERNAL_ALLOW lists it
import pandas
import numpy

# ❌ Fails on n8n Cloud, and self-hosted unless N8N_RUNNERS_STDLIB_ALLOW lists it
import json
import datetime
```

### The Two Allowlists

| Variable | Controls | Example value |
|----------|----------|---------------|
| `N8N_RUNNERS_STDLIB_ALLOW` | Standard library modules | `json,datetime,re` |
| `N8N_RUNNERS_EXTERNAL_ALLOW` | Third-party packages | `numpy,pandas` |

Both are comma-separated lists in the Python runner's `env-overrides` block of `n8n-task-runners.json`. On **n8n
Cloud** the Python option allows **no imports at all**, standard library included.

### The Solution

**Option 1: Use no imports** (works everywhere, including Cloud)

```python
# ✅ Built-ins need no allowlist
total = sum(item["json"].get("amount", 0) for item in _items)
ranked = sorted(_items, key=lambda i: i["json"].get("score", 0), reverse=True)
joined = ", ".join(str(i["json"].get("id")) for i in _items)

return [{"json": {"total": total, "top_id": ranked[0]["json"].get("id") if ranked else None}}]
```

**Option 2: Get the data from a node instead** (correct answer for anything network-shaped)

```python
# ✅ Add an HTTP Request node BEFORE the Python Code node,
# then read its response from the input
if not _items:
    return []

response = _items[0]["json"]

return [{
    "json": {
        "status": response.get("status"),
        "data": response.get("body"),
        "processed": True
    }
}]
```

**Option 3: Switch to JavaScript**

JavaScript has library access, HTTP through the sandbox helper surface, and Luxon, with no operator-managed
allowlist in the way. See [code-javascript.md](code-javascript.md).

**Option 4: Have the operator allowlist what you need** (self-hosted only)

Extend the `n8nio/runners` image (1.121.0 or later, matching the `n8nio/n8n` version), install the package, then
add it to the appropriate allowlist. This is a deployment change, not something you can do from the workflow.

### Common Library Replacements

| Need | ❌ Not available by default | ✅ Alternative |
|------|---------------------------|----------------|
| HTTP requests | `requests` | HTTP Request node, or JavaScript |
| Data analysis | `pandas` | Built-in comprehensions, or allowlist it self-hosted |
| Database | `psycopg2`, `pymongo` | n8n database nodes |
| Web scraping | `beautifulsoup4` | HTTP Request node + HTML Extract node |
| Excel | `openpyxl` | Extract from File / Convert to File nodes |
| Image processing | `pillow` | External API or a dedicated node |

---

## Error #2: Empty Code / Missing Return

**Frequency**: Common across all Code nodes

**What it is**: Code node has no code or no return statement.

### The Problem

```python
# ❌ WRONG: Empty code
# (nothing here)

# ❌ WRONG: Code but no return
processed = [item for item in _items if item["json"].get("active")]
# Forgot to return!

# ❌ WRONG: Return only on one branch
if _items:
    return [{"json": {"result": "success"}}]
# Falls off the end when _items is empty
```

### The Solution

```python
# ✅ CORRECT: Every path returns
if not _items:
    return [{"json": {"error": "No items"}}]

processed = [item for item in _items if item["json"].get("active")]

return processed if processed else [{"json": {"message": "No active items"}}]
```

### Best Practice

```python
# ✅ GOOD: Single unconditional return at the end
def process_items(items):
    if not items:
        return [{"json": {"error": "Empty input"}}]

    return [{"json": item["json"]} for item in items]

return process_items(_items)
```

---

## Error #3: KeyError

**Frequency**: Very common in Python Code nodes

**What it is**: Accessing dictionary key that doesn't exist. Bracket access is the only access native Python
offers, so this is the error you will meet most.

### The Problem

```python
# ❌ WRONG: Direct key access
item = _items[0]["json"]

name = item["name"]        # KeyError if "name" doesn't exist!
email = item["email"]      # KeyError if "email" doesn't exist!
age = item["age"]          # KeyError if "age" doesn't exist!

return [{"json": {"name": name, "email": email, "age": age}}]
```

### Error Message

```
KeyError: 'name'
```

### The Solution

```python
# ✅ CORRECT: Use .get() with defaults
item = _items[0]["json"] if _items else {}

return [{
    "json": {
        "name": item.get("name", "Unknown"),
        "email": item.get("email", "no-email@example.com"),
        "age": item.get("age", 0)
    }
}]
```

### Nested Dictionary Access

```python
# ❌ WRONG: Nested key access
webhook = _items[0]["json"]
name = webhook["body"]["user"]["name"]  # Multiple KeyErrors possible!

# ✅ CORRECT: Chained .get()
name = (
    webhook
    .get("body", {})
    .get("user", {})
    .get("name", "Unknown")
)

return [{"json": {"name": name}}]
```

### Webhook Body Access (Critical!)

```python
# ❌ WRONG: Forgetting webhook data is under "body"
webhook = _items[0]["json"]
name = webhook["name"]        # KeyError!
email = webhook["email"]      # KeyError!

# ✅ CORRECT: Access via ["body"]
body = _items[0]["json"].get("body", {})

return [{
    "json": {
        "name": body.get("name", "Unknown"),
        "email": body.get("email", "no-email")
    }
}]
```

---

## Error #4: IndexError

**Frequency**: Common when processing lists

**What it is**: Accessing a list index that doesn't exist. Native Python has no safe "first item" accessor, so
`_items[0]` is on you to guard.

### The Problem

```python
# ❌ WRONG: Assuming items exist
first_item = _items[0]        # IndexError if the input is empty!
second_item = _items[1]       # IndexError if only 1 item!

return [{
    "json": {
        "first": first_item["json"],
        "second": second_item["json"]
    }
}]
```

### Error Message

```
IndexError: list index out of range
```

### The Solution

```python
# ✅ CORRECT: Check length first
if len(_items) >= 2:
    return [{
        "json": {
            "first": _items[0]["json"],
            "second": _items[1]["json"]
        }
    }]

return [{
    "json": {
        "error": f"Expected 2+ items, got {len(_items)}"
    }
}]
```

### Safe First Item Access

```python
# ✅ CORRECT: Guard, then index
if not _items:
    return []

return [{"json": _items[0]["json"]}]

# ✅ ALSO CORRECT: Conditional expression
first_item = _items[0]["json"] if _items else {}

return [{"json": first_item}]
```

### Slice Instead of Index

```python
# ✅ CORRECT: Slicing never raises IndexError
first_five = _items[:5]   # fine with fewer than 5
rest = _items[1:]         # fine with an empty list

return [{"json": item["json"]} for item in first_five]
```

---

## Error #5: Incorrect Return Format

**Frequency**: Common for new users

**What it is**: Returning data in wrong format (n8n expects a list of objects with a `"json"` key).

### The Problem

```python
# ❌ WRONG: Returning plain dictionary
return {"name": "Alice", "age": 30}

# ❌ WRONG: Returning list without "json" wrapper
return [{"name": "Alice"}, {"name": "Bob"}]

# ❌ WRONG: Returning None
return None

# ❌ WRONG: Returning string
return "success"

# ❌ WRONG: Returning single item (not a list)
return {"json": {"name": "Alice"}}
```

### The Solution

```python
# ✅ CORRECT: List of objects with "json" key
return [{"json": {"name": "Alice", "age": 30}}]

# ✅ CORRECT: Multiple items
return [
    {"json": {"name": "Alice"}},
    {"json": {"name": "Bob"}}
]

# ✅ CORRECT: Transform items
return [{"json": item["json"]} for item in _items]

# ✅ CORRECT: Empty list (valid)
return []

# ✅ CORRECT: Single item still needs the list wrapper
return [{"json": {"result": "success"}}]
```

### Common Scenarios

**Scenario 1: Aggregation (Return Single Result)**

```python
total = sum(item["json"].get("amount", 0) for item in _items)

# ✅ CORRECT: Wrap in a list with "json"
return [{
    "json": {
        "total": total,
        "count": len(_items)
    }
}]
```

**Scenario 2: Filtering (Return Multiple Results)**

```python
active = [item for item in _items if item["json"].get("active")]

# ✅ CORRECT: Already in correct format
return active

# ✅ ALSO CORRECT: If transforming
return [
    {"json": {**item["json"], "filtered": True}}
    for item in active
]
```

**Scenario 3: No Results**

```python
# ✅ CORRECT: Return empty list
return []

# ✅ ALSO CORRECT: Return error message
return [{"json": {"error": "No results found"}}]
```

---

## Bonus Errors: NameError and AttributeError

### NameError - Wrong Mode Variable

Native Python defines `_items` in all-items mode and `_item` in per-item mode. The other name is not `None` - it
does not exist.

```python
# ❌ WRONG: _item in "Run Once for All Items" mode
data = _item["json"]   # NameError: name '_item' is not defined

# ❌ WRONG: _items in "Run Once for Each Item" mode
data = _items[0]["json"]   # NameError: name '_items' is not defined
```

```python
# ✅ CORRECT: match the variable to the mode
# runOnceForAllItems:
return [{"json": item["json"]} for item in _items]

# runOnceForEachItem:
return [{"json": _item["json"]}]
```

`NameError` is also what you get for any Pyodide helper: the `_input`, `_json`, `_node`, `_now`,
`_today` and `_jmespath` names were removed in n8n 2.0 and have no Python replacement.

### AttributeError - Dot Access

```python
# ❌ WRONG: dot access was a Pyodide affordance
value = _items[0].json.my_new_field   # AttributeError

# ✅ CORRECT: bracket access only
value = _items[0]["json"]["my_new_field"]
```

---

## Error Prevention Checklist

Before running your Python Code node, verify:

- [ ] **Runner prerequisite met**: task runners in external mode, `N8N_NATIVE_PYTHON_RUNNER=true`
- [ ] **Imports allowlisted**: every module in `N8N_RUNNERS_STDLIB_ALLOW` / `N8N_RUNNERS_EXTERNAL_ALLOW`; none on Cloud
- [ ] **Right variable for the mode**: `_items` for all-items, `_item` for each-item
- [ ] **Bracket access only**: `item["json"]["field"]`, never `item.json.field`
- [ ] **Code returns data**: Every code path ends with `return`
- [ ] **Correct format**: Returns `[{"json": {...}}]`
- [ ] **Safe dictionary access**: Uses `.get()` instead of `[]` where a key may be missing
- [ ] **Safe list access**: Checks length before indexing, or uses slicing
- [ ] **Webhook body access**: Reads webhook data via `["body"]`
- [ ] **No None returns**: Returns empty list `[]` instead of `None`
- [ ] **No n8n helpers assumed**: no node accessor, no HTTP helper, no date helpers

---

## Quick Fix Reference

| Error | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError` | Drop the import, use an upstream node, or have the operator allowlist it |
| `NameError: '_item' is not defined` | You are in all-items mode - use `_items` |
| `NameError: '_items' is not defined` | You are in per-item mode - use `_item` |
| `AttributeError` on item data | Replace dot access with bracket access |
| `KeyError: 'field'` | Change `data["field"]` to `data.get("field", default)` |
| `IndexError: list index out of range` | Guard with `if not _items: return []` before `_items[0]` |
| Empty output | Add `return [{"json": {...}}]` at the end |
| Wrong format error | Wrap result: `return [{"json": result}]` |
| Webhook KeyError | Access via `.get("body", {})` |
| Node never executes | Task runners not in external mode - operator fix |

---

## Testing Your Code

### Test Pattern 1: Handle Empty Input

```python
# ✅ Always test with empty input
if not _items:
    return [{"json": {"message": "No items to process"}}]

# Continue with processing
```

### Test Pattern 2: Test with Missing Fields

```python
# ✅ Use .get() with defaults
item = _items[0]["json"] if _items else {}

return [{
    "json": {
        "name": item.get("name", "Unknown"),
        "email": item.get("email", "no-email"),
        "age": item.get("age", 0)
    }
}]
```

### Test Pattern 3: Write for One Mode

There is no mode-agnostic code. `_items` and `_item` are mutually exclusive, and probing for one with `try`/`except`
hides real errors rather than adapting to the mode. Decide the mode first, then write against its variable.

```python
# ✅ runOnceForAllItems - the default, and the right choice for most work
return [
    {"json": {**item["json"], "checked": True}}
    for item in _items
]
```

### Test Pattern 4: Inspect Values by Returning Them

Where `print()` output from the native Python runner surfaces is not documented. Put what you want to see on the
output item instead, where the execution view shows it reliably.

```python
return [{
    "json": {
        "debug_item_count": len(_items),
        "debug_first_keys": sorted(_items[0]["json"].keys()) if _items else [],
        "result": result
    }
}]
```

---

## Summary

**Top 5 Errors to Avoid**:
1. **ModuleNotFoundError** - every import is allowlisted; Cloud permits none
2. **Missing return** - always end with `return [{"json": {...}}]`
3. **KeyError** - use `.get()` for dictionary access
4. **IndexError** - guard the empty list before `_items[0]`
5. **Wrong format** - return `[{"json": {...}}]`, not plain objects

**Golden Rules**:
- `_items` in all-items mode, `_item` in per-item mode - nothing else exists
- BRACKET access only
- ALWAYS use `.get()` where a key may be missing
- ALWAYS return `[{"json": {...}}]` format
- CHECK lengths before list access
- ACCESS webhook data via `["body"]`

**Remember**:
- JavaScript is recommended for most use cases
- Python needs task runners in external mode before any of this matters
- Cross-node data is JavaScript-only - merge it into the input instead
- Use n8n nodes for HTTP, databases, and file parsing

**See Also**:
- [code-python.md](code-python.md) - Python Code overview
- [code-python-data-access.md](code-python-data-access.md) - Data access patterns
- [code-python-standard-library.md](code-python-standard-library.md) - Import allowlists
- [code-python-common-patterns.md](code-python-common-patterns.md) - Production patterns
