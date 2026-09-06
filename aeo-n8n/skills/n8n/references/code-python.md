# Python Code Node

Expert guidance for writing Python code in n8n Code nodes.

> **Removed in n8n 2.0**: the Pyodide helpers `_input`, `_json`, `_node`, `_now`,
> `_today`, `_jmespath` — plus dot access on item data. Every pattern that depended on them is gone from this file.

---

## The Python Runtime

Native Python is the only Python n8n runs. The Pyodide runtime — the mode that supplied the underscore helper
family and dot access — was deprecated in 1.113.2 and removed in n8n 2.0. Code node typeVersion 2 exposes two
languages, `javaScript` and `pythonNative`; the `python` value survives only so pre-existing nodes still load.
The native surface is deliberately tiny: `_items` in all-items mode, `_item` in per-item mode, bracket access
only, and no n8n helpers of any kind. Imports — standard library included — must be allowlisted on the runner,
and n8n Cloud allows none at all.

**Hard prerequisite**: Python Code nodes run only on task runners in **external mode**. The operator deploys the
`n8nio/runners` sidecar and sets `N8N_NATIVE_PYTHON_RUNNER=true`. Without that, the node does not execute at all,
and no amount of correct Python compensates. Confirm the deployment before writing Python for someone else's
instance.

---

## ⚠️ Important: JavaScript First

**Recommendation**: Use **JavaScript for most use cases**. n8n's own Code node builder hint says it plainly —
default to `javaScript`, the only language with library access and cross-node helpers; choose `pythonNative`
only when the user explicitly asks for Python.

**Why JavaScript is preferred:**
- Cross-node access: `$('Node Name')` exists only in JavaScript — Python has no node accessor at all
- The `helpers` surface (HTTP requests, binary data) is JavaScript-only
- Luxon `DateTime` is passed into the JavaScript sandbox; Python gets no n8n date or timezone helpers
- Libraries work without an operator editing runner configuration
- JavaScript runs on the default task runner; Python additionally requires external mode

**Use Python when:**
- The user explicitly asked for Python
- The logic genuinely reads better as Python and the modules it needs are already allowlisted on the runner

---

## Quick Start

```python
# Basic template for Python Code nodes (all-items mode)
processed = []

for item in _items:
    processed.append({
        "json": {
            **item["json"],
            "processed": True
        }
    })

return processed
```

### Essential Rules

1. **Consider JavaScript first** - Use Python only when asked or clearly warranted
2. **Access data**: `_items` (all-items mode) or `_item` (per-item mode) - nothing else exists
3. **Bracket access only**: `item["json"]["my_new_field"]`, never `item.json.myNewField`
4. **CRITICAL**: Must return `[{"json": {...}}]` format
5. **CRITICAL**: Webhook data is under `["body"]` (not at the top level of the item's `json`)
6. **Imports are allowlisted**: every module, standard library included, must be permitted by the runner
7. **No n8n helpers**: no node accessor, no HTTP helper, no date helpers, no static data, no secrets

---

## Mode Selection Guide

Same two modes as JavaScript - choose based on your use case.

### Run Once for All Items (Recommended - Default)

Parameter value: `runOnceForAllItems`

**Use this mode for:** most use cases

- **How it works**: Code executes **once** regardless of input count
- **Data access**: `_items` - a list of the input items
- **Best for**: Aggregation, filtering, batch processing, transformations
- **Performance**: Faster for multiple items (single execution)

```python
# Example: Calculate total from all items
total = sum(item["json"].get("amount", 0) for item in _items)

return [{
    "json": {
        "total": total,
        "count": len(_items),
        "average": total / len(_items) if _items else 0
    }
}]
```

### Run Once for Each Item

Parameter value: `runOnceForEachItem`

**Use this mode for:** Specialized cases only

- **How it works**: Code executes **separately** for each input item
- **Data access**: `_item` - the single input item
- **Best for**: Item-specific logic, independent operations, per-item validation
- **Performance**: Slower for large datasets (multiple executions)

```python
# Example: Flag each item independently
return [{
    "json": {
        **_item["json"],
        "processed": True
    }
}]
```

---

## Python Modes: Native Only

There is one Python runtime, `pythonNative`, and its entire n8n-facing surface is two variables.

| Available | Mode | What it is |
|-----------|------|------------|
| `_items` | Run Once for All Items | A list of the input items, each a dict with a `"json"` key |
| `_item` | Run Once for Each Item | The single input item, a dict with a `"json"` key |

Everything else that Pyodide offered is gone and raises `NameError`: the `_input`, `_json`,
`_node`, `_now`, `_today`, `_jmespath`, `_env`, `_vars`, `_execution`, `_getWorkflowStaticData`, `_prevNode`, `_runIndex`,
`secrets` and `workflow` names, and the `_("<node name>")` node accessor. Do not reach for a Python replacement -
none was shipped. Get the data into the node's input, or write the node in JavaScript.

Bracket access is mandatory. Pyodide accepted `item.json.myNewField`; native Python does not.

```python
# ✅ CORRECT - bracket access
value = item["json"]["my_new_field"]

# ❌ WRONG - dot access was a Pyodide affordance
value = item.json.myNewField  # AttributeError
```

---

## Data Access Patterns

### Pattern 1: _items - Most Common

**Use when**: Processing arrays, batch operations, aggregations (all-items mode)

```python
# Filter, then transform
valid = [item for item in _items if item["json"].get("status") == "active"]

return [
    {
        "json": {
            "id": item["json"]["id"],
            "name": item["json"]["name"]
        }
    }
    for item in valid
]
```

### Pattern 2: _items[0] - First Item

**Use when**: The previous node returns a single object, such as an API response

```python
# Guard the empty case yourself - there is no built-in "first" accessor
if not _items:
    return []

data = _items[0]["json"]

return [{
    "json": {
        "user_id": data.get("id"),
        "status": data.get("status")
    }
}]
```

### Pattern 3: _item - Each Item Mode Only

**Use when**: Mode is "Run Once for Each Item"

```python
return [{
    "json": {
        **_item["json"],
        "item_processed": True
    }
}]
```

`_item` does not exist in all-items mode, and `_items` does not exist in per-item mode. Referencing the wrong one
raises `NameError`.

### Pattern 4: Data From Another Node - JavaScript Only

Native Python has no node accessor. Reaching a named node is a JavaScript capability (`$('Node Name')`); see
[code-javascript.md](code-javascript.md). In Python, wire the other node's output into this node's input - a Merge
node, or simply placing the Code node downstream of the data you need - and read it from `_items`.

**See**: [code-python-data-access.md](code-python-data-access.md) for the comprehensive guide

---

## Critical: Webhook Data Structure

**MOST COMMON MISTAKE**: Webhook data is nested under `["body"]`

```python
# ❌ WRONG - Will raise KeyError
name = _items[0]["json"]["name"]
email = _items[0]["json"]["email"]

# ✅ CORRECT - Webhook data is under ["body"]
name = _items[0]["json"]["body"]["name"]
email = _items[0]["json"]["body"]["email"]

# ✅ SAFER - Use .get() for safe access
webhook_data = _items[0]["json"].get("body", {})
name = webhook_data.get("name")
```

**Why**: The Webhook node wraps all request data under `body`, alongside `headers`, `params` and `query`. This
includes POST data and JSON payloads.

**See**: [code-python-data-access.md](code-python-data-access.md) for full webhook structure details

---

## Return Format Requirements

**CRITICAL RULE**: Always return a list of dictionaries with a `"json"` key

### Correct Return Formats

```python
# ✅ Single result
return [{
    "json": {
        "field1": value1,
        "field2": value2
    }
}]

# ✅ Multiple results
return [
    {"json": {"id": 1, "data": "first"}},
    {"json": {"id": 2, "data": "second"}}
]

# ✅ List comprehension
transformed = [
    {"json": {"id": item["json"]["id"], "processed": True}}
    for item in _items
    if item["json"].get("valid")
]
return transformed

# ✅ Empty result (when no data to return)
return []

# ✅ Conditional return
if should_process:
    return [{"json": processed_data}]
else:
    return []
```

### Incorrect Return Formats

```python
# ❌ WRONG: Dictionary without list wrapper
return {
    "json": {"field": value}
}

# ❌ WRONG: List without json wrapper
return [{"field": value}]

# ❌ WRONG: Plain string
return "processed"

# ❌ WRONG: Incomplete structure
return [{"data": value}]  # Should be {"json": value}
```

**Why it matters**: Next nodes expect list format. Incorrect format causes workflow execution to fail.

**See**: [code-python-error-patterns.md](code-python-error-patterns.md) #2 for detailed error solutions

---

## Imports Are Allowlisted on the Runner

**MOST IMPORTANT PYTHON LIMITATION**: you do not get to decide what you can import - the operator does.

Native Python denies insecure built-ins by default. Both standard library and third-party modules are gated by
allowlists set on the Python task runner:

| Variable | Controls | Example value |
|----------|----------|---------------|
| `N8N_RUNNERS_STDLIB_ALLOW` | Which **standard library** modules may be imported | `json,datetime,re` |
| `N8N_RUNNERS_EXTERNAL_ALLOW` | Which **third-party** packages may be imported | `numpy,pandas` |

Both live in the Python runner's `env-overrides` block in `n8n-task-runners.json` as comma-separated lists.

**Self-hosted**: third-party packages are supported. Extend the `n8nio/runners` image (1.121.0 or later, matching
the `n8nio/n8n` image version), install the package, then allowlist it. `numpy` and `pandas` are ordinary examples
- not special cases.

**n8n Cloud**: the Python option allows **no imports at all**, standard library included. Code that starts with an
`import` line cannot run on Cloud.

### Consequences When Writing Code

```python
# Works only if "json" is in N8N_RUNNERS_STDLIB_ALLOW
import json

# Works only if the image ships numpy AND it is in N8N_RUNNERS_EXTERNAL_ALLOW
import numpy
```

Assume nothing. If you do not know the instance's allowlist, keep to plain built-ins (`sum`, `sorted`, `len`,
comprehensions, f-strings, `dict`/`list`/`set` methods) or ask what is permitted. Import failures surface at
execution time, not while editing.

### Workarounds

**Need HTTP requests?**
- ✅ Use the **HTTP Request node** before the Code node - the correct answer on every deployment
- ✅ Or switch to **JavaScript**, which reaches HTTP through the sandbox `helpers` surface

**Need data analysis (pandas/numpy)?**
- ✅ Self-hosted: have the operator add them to the runner image and the external allowlist
- ✅ Cloud, or no operator access: use built-ins and comprehensions, or switch to **JavaScript**

**Need web scraping?**
- ✅ Use **HTTP Request node** + **HTML Extract node**

**See**: [code-python-standard-library.md](code-python-standard-library.md) for the allowlist reference

---

## Common Patterns Overview

Based on production workflows, here are the most useful Python patterns:

### 1. Data Transformation
Transform all items with list comprehensions

```python
return [
    {
        "json": {
            "id": item["json"].get("id"),
            "name": item["json"].get("name", "Unknown").upper(),
            "processed": True
        }
    }
    for item in _items
]
```

### 2. Filtering & Aggregation
Sum, filter, count with built-in functions

```python
total = sum(item["json"].get("amount", 0) for item in _items)
valid_items = [item for item in _items if item["json"].get("amount", 0) > 0]

return [{
    "json": {
        "total": total,
        "count": len(valid_items)
    }
}]
```

### 3. String Processing with Regex
Extract patterns from text (requires `re` on the stdlib allowlist)

```python
import re

email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

all_emails = []
for item in _items:
    text = item["json"].get("text", "")
    all_emails.extend(re.findall(email_pattern, text))

unique_emails = sorted(set(all_emails))

return [{
    "json": {
        "emails": unique_emails,
        "count": len(unique_emails)
    }
}]
```

### 4. Data Validation
Validate and clean data - no imports needed

```python
validated = []

for item in _items:
    data = item["json"]
    errors = []

    if not data.get("email"):
        errors.append("Email required")
    if not data.get("name"):
        errors.append("Name required")

    validated.append({
        "json": {
            **data,
            "valid": len(errors) == 0,
            "errors": errors if errors else None
        }
    })

return validated
```

### 5. Statistical Analysis
Calculate statistics (requires `statistics` on the stdlib allowlist)

```python
from statistics import mean, median, stdev

values = [item["json"].get("value", 0) for item in _items if "value" in item["json"]]

if values:
    return [{
        "json": {
            "mean": mean(values),
            "median": median(values),
            "stdev": stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }
    }]
else:
    return [{"json": {"error": "No values found"}}]
```

**See**: [code-python-common-patterns.md](code-python-common-patterns.md) for 10 detailed Python patterns

---

## Error Prevention - Top 5 Mistakes

### #1: Assuming an Import Is Available (Python-Specific!)

```python
# ❌ WRONG: assuming the module is there
import requests  # never available; there is no HTTP client for Python here
import pandas    # ModuleNotFoundError unless the image ships it AND it is allowlisted

# ✅ CORRECT: use the HTTP Request node, or JavaScript, for network calls
# ✅ CORRECT: confirm the stdlib allowlist before importing json/datetime/re
```

### #2: Empty Code or Missing Return

```python
# ❌ WRONG: No return statement
processed = [item for item in _items if item["json"].get("active")]
# Forgot to return!

# ✅ CORRECT: Always return data
return [{"json": item["json"]} for item in _items]
```

### #3: Incorrect Return Format

```python
# ❌ WRONG: Returning dict instead of list
return {"json": {"result": "success"}}

# ✅ CORRECT: List wrapper required
return [{"json": {"result": "success"}}]
```

### #4: KeyError on Dictionary Access

```python
# ❌ WRONG: Direct access crashes if missing
name = _items[0]["json"]["user"]["name"]  # KeyError!

# ✅ CORRECT: Use .get() for safe access
name = _items[0]["json"].get("user", {}).get("name", "Unknown")
```

### #5: Webhook Body Nesting

```python
# ❌ WRONG: Direct access to webhook data
email = _items[0]["json"]["email"]  # KeyError!

# ✅ CORRECT: Webhook data under ["body"]
email = _items[0]["json"]["body"]["email"]

# ✅ BETTER: Safe access with .get()
email = _items[0]["json"].get("body", {}).get("email", "no-email")
```

**See**: [code-python-error-patterns.md](code-python-error-patterns.md) for comprehensive error guide

---

## Standard Library Reference

Each of these requires its module name in `N8N_RUNNERS_STDLIB_ALLOW`, and none of them work on n8n Cloud.

```python
# JSON operations
import json
data = json.loads(json_string)
json_output = json.dumps({"key": "value"})

# Date/time
from datetime import datetime, timedelta
now = datetime.now()
tomorrow = now + timedelta(days=1)
formatted = now.strftime("%Y-%m-%d")

# Regular expressions
import re
matches = re.findall(r'\d+', text)
cleaned = re.sub(r'[^\w\s]', '', text)

# Base64 encoding
import base64
encoded = base64.b64encode(data).decode()
decoded = base64.b64decode(encoded)

# Hashing
import hashlib
hash_value = hashlib.sha256(text.encode()).hexdigest()

# URL parsing
import urllib.parse
params = urllib.parse.urlencode({"key": "value"})
parsed = urllib.parse.urlparse(url)

# Statistics
from statistics import mean, median, stdev
average = mean([1, 2, 3, 4, 5])
```

**See**: [code-python-standard-library.md](code-python-standard-library.md) for complete reference

---

## Best Practices

### 1. Always Use .get() for Dictionary Access

```python
# ✅ SAFE: Won't crash if field missing
value = item["json"].get("field", "default")

# ❌ RISKY: Crashes if field doesn't exist
value = item["json"]["field"]
```

### 2. Handle None/Null Values Explicitly

```python
# ✅ GOOD: Default to 0 if None
amount = item["json"].get("amount") or 0

# ✅ GOOD: Check for None explicitly
text = item["json"].get("text")
if text is None:
    text = ""
```

### 3. Use List Comprehensions for Filtering

```python
# ✅ PYTHONIC: List comprehension
valid = [item for item in _items if item["json"].get("active")]

# ❌ VERBOSE: Manual loop
valid = []
for item in _items:
    if item["json"].get("active"):
        valid.append(item)
```

### 4. Return Consistent Structure

```python
# ✅ CONSISTENT: Always list with "json" key
return [{"json": result}]  # Single result
return results  # Multiple results (already formatted)
return []  # No results
```

### 5. Debug by Returning, Not by Printing

Where `print()` output from the native Python runner surfaces is not documented - do not build a debugging habit
on it. Put the value you want to inspect on the output item, where the execution view shows it reliably:

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

## When to Use Python vs JavaScript

### Use Python When:
- ✅ The user explicitly asked for Python
- ✅ Your logic maps well to list comprehensions and dict handling
- ✅ The standard library module you need is already allowlisted on the runner

### Use JavaScript When:
- ✅ You need HTTP requests from inside the Code node
- ✅ You need data from another node (`$('Node Name')`)
- ✅ You need advanced date/time (DateTime/Luxon)
- ✅ You need any library on n8n Cloud
- ✅ **For most use cases** (recommended)

### Consider Other Nodes When:
- ❌ Simple field mapping → Use **Set** node
- ❌ Basic filtering → Use **Filter** node
- ❌ Simple conditionals → Use **IF** or **Switch** node
- ❌ HTTP requests only → Use **HTTP Request** node

---

## Integration with Other Skills

### Works With:

**[n8n Expression Syntax](expressions.md)**:
- Expressions use `{{ }}` syntax in other nodes
- Code nodes use Python directly (no `{{ }}`)
- When to use expressions vs code

**[n8n MCP Tools Expert](mcp-tools.md)**:
- How to find Code node: `search_nodes({query: "code"})`
- Get configuration help: `get_node({nodeType: "nodes-base.code"})`
- Validate code: `validate_node({nodeType: "nodes-base.code", config, mode: "full"})`

**[n8n Node Configuration](node-configuration.md)**:
- Mode selection (All Items vs Each Item)
- Language selection (`pythonNative` vs `javaScript`)
- Understanding property dependencies

**[n8n Workflow Patterns](workflow-patterns.md)**:
- Code nodes in transformation step
- When to use Python vs JavaScript in patterns

**[n8n Validation Expert](validation.md)**:
- Validate Code node configuration
- Handle validation errors
- Auto-fix common issues

**[n8n Code JavaScript](code-javascript.md)**:
- When to use JavaScript instead
- Cross-node access, HTTP helpers, Luxon - all JavaScript-only
- Migration from Python to JavaScript

---

## Quick Reference Checklist

Before deploying Python Code nodes, verify:

- [ ] **Task runners in external mode** - `N8N_NATIVE_PYTHON_RUNNER=true`, `n8nio/runners` deployed
- [ ] **Considered JavaScript first** - Using Python only when asked or clearly warranted
- [ ] **Code is not empty** - Must have meaningful logic
- [ ] **Return statement exists** - Must return list of dictionaries
- [ ] **Proper return format** - Each item: `{"json": {...}}`
- [ ] **Data access correct** - `_items` in all-items mode, `_item` in per-item mode
- [ ] **Bracket access only** - `item["json"]["field"]`, never `item.json.field`
- [ ] **Imports allowlisted** - every module named in `N8N_RUNNERS_STDLIB_ALLOW` / `N8N_RUNNERS_EXTERNAL_ALLOW`
- [ ] **Not on Cloud with imports** - Cloud permits none
- [ ] **No n8n helpers assumed** - no node accessor, no HTTP helper, no date helpers
- [ ] **Safe dictionary access** - Using `.get()` to avoid KeyError
- [ ] **Webhook data** - Access via `["body"]` if from webhook
- [ ] **Mode selection** - "All Items" for most cases
- [ ] **Output consistent** - All code paths return same structure

---

## Additional Resources

### Related Files
- [code-python-data-access.md](code-python-data-access.md) - Comprehensive Python data access patterns
- [code-python-common-patterns.md](code-python-common-patterns.md) - 10 Python patterns for n8n
- [code-python-error-patterns.md](code-python-error-patterns.md) - Top 5 errors and solutions
- [code-python-standard-library.md](code-python-standard-library.md) - Import allowlist reference

### n8n Documentation
- Code Node Guide: https://docs.n8n.io/build/code-in-n8n/using-the-code-node/
- Task Runners (Python prerequisite): https://docs.n8n.io/deploy/host-n8n/configure-n8n/set-up-task-runners/

---

**Ready to write Python in n8n Code nodes - but consider JavaScript first!** Confirm the runner is in external mode,
keep to `_items` / `_item` and bracket access, check what the allowlist permits, and reference the error patterns
guide to avoid common mistakes.
