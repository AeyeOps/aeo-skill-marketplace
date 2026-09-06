# Data Access Patterns - Python Code Node

Complete guide to accessing data in n8n Code nodes using native Python.

> **Removed in n8n 2.0**: the Pyodide helpers `_input`, `_json`, `_node` — plus dot
> access on item data. Patterns built on them, including every cross-node example, are gone from this file.

---

## Overview

Native Python exposes exactly two variables, and which one exists depends on the node's mode:

**Data Access Priority** (by common usage):
1. **`_items`** - all-items mode - the list of input items; covers batch work, aggregation, filtering
2. **`_items[0]`** - all-items mode - the first item, for single-object payloads
3. **`_item`** - per-item mode only - the single input item

There is no third option. There is no node accessor, no `first()`/`all()` method, and no direct "current json"
variable. Access is **bracket only**: `item["json"]["my_new_field"]`, never `item.json.myNewField`.

**Python vs JavaScript**:
| JavaScript | Python (native) |
|------------|-----------------|
| `$input.all()` | `_items` |
| `$input.first()` | `_items[0]` (guard the empty list yourself) |
| `$input.item` | `_item` |
| `$json` | `_item["json"]` (per-item) or `_items[0]["json"]` (all-items) |
| `$('Name')` | Not available - JavaScript only, see [code-javascript.md](code-javascript.md) |

Every `import` below - `datetime` included - must be named in the runner's `N8N_RUNNERS_STDLIB_ALLOW`, and none
work on n8n Cloud. See [code-python-standard-library.md](code-python-standard-library.md).

---

## Pattern 1: _items - Process All Items

**Usage**: Most common pattern for batch processing

**When to use:**
- Processing multiple records
- Aggregating data (sum, count, average)
- Filtering lists
- Transforming datasets

### Basic Usage

```python
# _items is a list of dictionaries like:
# [
#   {"json": {"id": 1, "name": "Alice"}},
#   {"json": {"id": 2, "name": "Bob"}}
# ]

return _items
```

### Example 1: Filter Active Items

```python
active_items = [
    item for item in _items
    if item["json"].get("status") == "active"
]

return active_items
```

### Example 2: Transform All Items

```python
transformed = []
for item in _items:
    transformed.append({
        "json": {
            "id": item["json"].get("id"),
            "full_name": f"{item['json'].get('first_name', '')} {item['json'].get('last_name', '')}".strip(),
            "email": item["json"].get("email")
        }
    })

return transformed
```

### Example 3: Aggregate Data

```python
total = sum(item["json"].get("amount", 0) for item in _items)

return [{
    "json": {
        "total": total,
        "count": len(_items),
        "average": total / len(_items) if _items else 0
    }
}]
```

### Example 4: Sort and Limit

```python
sorted_items = sorted(
    _items,
    key=lambda item: item["json"].get("score", 0),
    reverse=True
)
top_five = sorted_items[:5]

return [{"json": item["json"]} for item in top_five]
```

### Example 5: Group By Category

```python
grouped = {}
for item in _items:
    category = item["json"].get("category", "Uncategorized")

    if category not in grouped:
        grouped[category] = []

    grouped[category].append(item["json"])

return [
    {
        "json": {
            "category": category,
            "items": items,
            "count": len(items)
        }
    }
    for category, items in grouped.items()
]
```

### Example 6: Deduplicate by ID

```python
seen = set()
unique = []

for item in _items:
    item_id = item["json"].get("id")

    if item_id and item_id not in seen:
        seen.add(item_id)
        unique.append(item)

return unique
```

---

## Pattern 2: _items[0] - Get First Item

**Usage**: Very common for single-item operations

**When to use:**
- Previous node returns single object
- Working with API responses
- Getting initial/first data point

**IMPORTANT**: there is no built-in "first item" accessor with empty-list safety. Guard it yourself; `_items[0]`
on an empty list raises `IndexError`.

### Basic Usage

```python
if not _items:
    return []

data = _items[0]["json"]

return [{"json": data}]
```

### Example 1: Process Single API Response

```python
if not _items:
    return []

response = _items[0]["json"]

return [{
    "json": {
        "user_id": response.get("data", {}).get("user", {}).get("id"),
        "user_name": response.get("data", {}).get("user", {}).get("name"),
        "status": response.get("status")
    }
}]
```

### Example 2: Transform Single Object

```python
if not _items:
    return []

data = _items[0]["json"]

return [{
    "json": {
        "id": data.get("id"),
        "contact": {
            "email": data.get("email"),
            "phone": data.get("phone")
        },
        "address": {
            "street": data.get("street"),
            "city": data.get("city"),
            "zip": data.get("zip")
        }
    }
}]
```

### Example 3: Validate Single Item

```python
if not _items:
    return []

item = _items[0]["json"]

is_valid = bool(item.get("email") and "@" in item.get("email", ""))

return [{
    "json": {
        **item,
        "valid": is_valid
    }
}]
```

### Example 4: Extract Nested Data

```python
if not _items:
    return []

response = _items[0]["json"]
users = response.get("data", {}).get("users", [])

return [
    {
        "json": {
            "id": user.get("id"),
            "name": user.get("profile", {}).get("name", "Unknown"),
            "email": user.get("contact", {}).get("email", "no-email")
        }
    }
    for user in users
]
```

---

## Pattern 3: _item - Current Item (Each Item Mode)

**Usage**: Common in "Run Once for Each Item" mode (`runOnceForEachItem`)

**When to use:**
- Mode is set to "Run Once for Each Item"
- Need to process items independently
- Per-item validation

**IMPORTANT**: `_item` exists only in per-item mode and `_items` only in all-items mode. Referencing the wrong one
raises `NameError` - it is not `None`, it is undefined.

### Basic Usage

```python
data = _item["json"]

return [{
    "json": {
        **data,
        "processed": True
    }
}]
```

### Example 1: Add Processing Metadata

```python
return [{
    "json": {
        **_item["json"],
        "processed": True,
        "source": "code-node"
    }
}]
```

### Example 2: Per-Item Validation

```python
data = _item["json"]

errors = []

if not data.get("email"):
    errors.append("Email required")
if not data.get("name"):
    errors.append("Name required")
if data.get("age") and data["age"] < 18:
    errors.append("Must be 18+")

return [{
    "json": {
        **data,
        "valid": len(errors) == 0,
        "errors": errors if errors else None
    }
}]
```

### Example 3: Conditional Processing

```python
data = _item["json"]

if data.get("type") == "premium":
    return [{
        "json": {
            **data,
            "discount": 0.20,
            "tier": "premium"
        }
    }]
else:
    return [{
        "json": {
            **data,
            "discount": 0.05,
            "tier": "standard"
        }
    }]
```

---

## Pattern 4: Data From Another Node - JavaScript Only

Native Python has **no node accessor**. Nothing in the Python surface reaches a named node, and no replacement was
shipped - this is a JavaScript-only capability.

**If you need another node's output, pick one:**

1. **Write the node in JavaScript** and use `$('Node Name')`, which also gives you `.all()`, `.first()`,
   `.itemMatching()` and `.isExecuted`. See [code-javascript.md](code-javascript.md).
2. **Wire the data into this node's input.** Put the Code node downstream of the data you need, or merge the two
   branches with a **Merge** node first, then read everything from `_items`.

### Combining Two Sources Through the Input

```python
# Upstream: a Merge node joins the webhook branch and the API branch,
# tagging each item with a "source" field via a Set node.
by_source = {}
for item in _items:
    source = item["json"].get("source", "unknown")
    by_source.setdefault(source, []).append(item["json"])

return [{
    "json": {
        "webhook": by_source.get("webhook", []),
        "api": by_source.get("api", []),
        "source_count": len(by_source)
    }
}]
```

### Comparing Two Datasets Through the Input

```python
# Upstream: a Merge node in "append" mode puts the old set first, the new set second,
# each tagged with a "dataset" field.
old_data = [i["json"] for i in _items if i["json"].get("dataset") == "old"]
new_data = [i["json"] for i in _items if i["json"].get("dataset") == "new"]

old_ids = {o.get("id") for o in old_data}
new_ids = {n.get("id") for n in new_data}

return [{
    "json": {
        "added": [n for n in new_data if n.get("id") not in old_ids],
        "removed": [o for o in old_data if o.get("id") not in new_ids],
        "summary": {
            "added": len(new_ids - old_ids),
            "removed": len(old_ids - new_ids)
        }
    }
}]
```

---

## Critical: Webhook Data Structure

**MOST COMMON MISTAKE**: Forgetting webhook data is nested under `["body"]`

### The Problem

Webhook node wraps all incoming data under a `"body"` property.

### Structure

```python
# Webhook node output structure:
{
    "headers": {
        "content-type": "application/json",
        "user-agent": "..."
    },
    "params": {},
    "query": {},
    "body": {
        # ← YOUR DATA IS HERE
        "name": "Alice",
        "email": "alice@example.com",
        "message": "Hello!"
    }
}
```

### Wrong vs Right

```python
webhook = _items[0]["json"]

# ❌ WRONG: Trying to access directly
name = webhook["name"]  # KeyError!
email = webhook["email"]  # KeyError!

# ✅ CORRECT: Access via ["body"]
name = webhook["body"]["name"]  # "Alice"
email = webhook["body"]["email"]  # "alice@example.com"

# ✅ SAFER: Use .get() for safe access
body = webhook.get("body", {})
name = body.get("name")  # None if missing
email = body.get("email", "no-email")  # Default value
```

### Example: Full Webhook Processing

```python
if not _items:
    return []

webhook_output = _items[0]["json"]

# Access the actual payload
payload = webhook_output.get("body", {})

# Access headers if needed
content_type = webhook_output.get("headers", {}).get("content-type")

# Access query parameters if needed
api_key = webhook_output.get("query", {}).get("api_key")

return [{
    "json": {
        # Data from webhook body
        "user_name": payload.get("name"),
        "user_email": payload.get("email"),
        "message": payload.get("message"),

        # Metadata
        "content_type": content_type,
        "authenticated": bool(api_key)
    }
}]
```

### POST Data, Query Params, and Headers

```python
webhook = _items[0]["json"]

return [{
    "json": {
        # POST body data
        "form_data": webhook.get("body", {}),

        # Query parameters (?key=value)
        "query_params": webhook.get("query", {}),

        # Route parameters (/path/:variable)
        "route_params": webhook.get("params", {}),

        # HTTP headers
        "user_agent": webhook.get("headers", {}).get("user-agent"),
        "content_type": webhook.get("headers", {}).get("content-type")
    }
}]
```

---

## Choosing the Right Pattern

### Decision Tree

```
Which mode is the node in?
├─ Run Once for Each Item → Use _item (only _item exists)
│
└─ Run Once for All Items → Use _items
    ├─ Need every record?      → iterate _items
    ├─ Need one object?        → guard "if not _items", then _items[0]
    └─ Need another node's data?
        └─ Not possible in Python → JavaScript $('Node Name'),
           or wire the data into this node's input
```

### Quick Reference Table

| Scenario | Use This | Example |
|----------|----------|---------|
| Sum all amounts | `_items` | `sum(i["json"].get("amount", 0) for i in _items)` |
| Get API response | `_items[0]` | `_items[0]["json"].get("data")` |
| Process each independently | `_item` | `_item["json"]` (Each Item mode) |
| Combine two nodes | node input | Merge upstream, then read `_items` |
| Filter list | `_items` | `[i for i in _items if i["json"].get("active")]` |
| Transform single object | `_items[0]` | `{**_items[0]["json"], "new": True}` |
| Webhook data | `_items[0]` | `_items[0]["json"]["body"]` |

---

## Common Mistakes

### Mistake 1: Using the Wrong Mode Variable

```python
# ❌ WRONG: _item does not exist in all-items mode
data = _item["json"]  # NameError!

# ✅ CORRECT: all-items mode gives you _items
data = _items[0]["json"]
```

### Mistake 2: Forgetting ["json"] Property

```python
# ❌ WRONG: Trying to access fields on the item dictionary
names = [item["name"] for item in _items]  # KeyError!

# ✅ CORRECT: Access via ["json"]
names = [item["json"]["name"] for item in _items]
```

### Mistake 3: Dot Access

```python
# ❌ WRONG: dot access was a Pyodide affordance
value = _items[0].json.my_new_field  # AttributeError!

# ✅ CORRECT: bracket access only
value = _items[0]["json"]["my_new_field"]
```

### Mistake 4: Not Handling Empty Lists

```python
# ❌ WRONG: Crashes if no items
first = _items[0]["json"]  # IndexError!

# ✅ CORRECT: Check length first
if not _items:
    return []
first = _items[0]["json"]
```

### Mistake 5: Direct Dictionary Access (KeyError)

```python
# ❌ RISKY: Crashes if key missing
value = item["json"]["field"]  # KeyError!

# ✅ SAFE: Use .get()
value = item["json"].get("field", "default")
```

---

## Advanced Patterns

### Pattern: Safe Nested Access

```python
value = (
    _items[0]["json"]
    .get("level1", {})
    .get("level2", {})
    .get("level3", "default")
) if _items else "default"
```

### Pattern: List Comprehension with Filtering

```python
# Filter and transform in one step
return [
    {
        "json": {
            "id": item["json"]["id"],
            "name": item["json"]["name"].upper()
        }
    }
    for item in _items
    if item["json"].get("active") and item["json"].get("verified")
]
```

### Pattern: Dictionary Comprehension

```python
# Create lookup dictionary
lookup = {
    item["json"]["id"]: item["json"]
    for item in _items
    if "id" in item["json"]
}

return [{"json": lookup}]
```

---

## Summary

**Most Common Patterns**:
1. `_items` - process multiple items, batch operations (all-items mode)
2. `_items[0]` - single item, API responses (guard the empty list)
3. `_item` - per-item mode processing

**Critical Rules**:
- Webhook data is under the `["body"]` property
- Bracket access only; dot access raises `AttributeError`
- Cross-node access does not exist in Python - use JavaScript or the node's input

**Best Practice**:
- Use `.get()` for dictionary access to avoid KeyError
- Always check for empty lists before indexing
- Match the variable to the mode: `_items` for all-items, `_item` for each-item

**See Also**:
- [code-python.md](code-python.md) - Overview and quick start
- [code-python-common-patterns.md](code-python-common-patterns.md) - Python-specific patterns
- [code-python-error-patterns.md](code-python-error-patterns.md) - Avoid common mistakes
- [code-javascript.md](code-javascript.md) - Cross-node access and helpers
