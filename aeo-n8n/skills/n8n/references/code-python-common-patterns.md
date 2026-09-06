# Common Patterns - Python Code Node

Production-tested Python patterns for n8n Code nodes, written for the native Python runtime.

> **Removed in n8n 2.0**: the Pyodide helpers `_input`, `_json` — plus dot access on
> item data. The examples below use `_items` / `_item` and bracket access throughout.

---

## ⚠️ Important: JavaScript First

**Use JavaScript for most use cases.**

n8n's Code node builder hint is explicit: default to `javaScript`, the only language with library access and
cross-node helpers; choose `pythonNative` only when the user explicitly asks for Python. Python has no node
accessor, no HTTP helper, no Luxon, and its imports depend on an operator-managed allowlist.

Only use Python when:
- The user explicitly asked for Python
- Your logic maps cleanly to comprehensions and dict handling
- The standard library modules you need are already allowlisted on the runner

---

## Pattern Overview

These 10 patterns cover common n8n Code node scenarios using Python:

1. **Multi-Source Data Aggregation** - Normalise items arriving from different sources
2. **Regex-Based Filtering** - Filter items using pattern matching
3. **Markdown to Structured Data** - Parse markdown into structured format
4. **JSON Object Comparison** - Compare two JSON objects for changes
5. **CRM Data Transformation** - Transform CRM data to standard format
6. **Release Notes Processing** - Parse and categorize release notes
7. **Array Transformation** - Reshape arrays and extract fields
8. **Dictionary Lookup** - Create and use lookup dictionaries
9. **Top N Filtering** - Get top items by score/value
10. **String Aggregation** - Aggregate strings with formatting

All examples run in **Run Once for All Items** mode (`runOnceForAllItems`) unless noted, so `_items` is the input.

**Imports**: patterns 1-6 import `datetime` or `re`. Both are standard library, and native Python still requires
each module to be named in the runner's `N8N_RUNNERS_STDLIB_ALLOW`. On n8n Cloud no import works at all - patterns
7-10 need none and run anywhere. See [code-python-standard-library.md](code-python-standard-library.md).

---

## Pattern 1: Multi-Source Data Aggregation

**Use case**: Normalise differently-shaped payloads that arrive together on the input.

**Scenario**: Aggregate news articles collected by several upstream HTTP Request nodes and joined with a Merge node.

### Implementation

```python
from datetime import datetime

processed_articles = []

for item in _items:
    source_data = item["json"]
    source_name = source_data.get("name", "Unknown")

    # Process Hacker News shape
    if source_name == "Hacker News" and source_data.get("hits"):
        for hit in source_data["hits"]:
            processed_articles.append({
                "title": hit.get("title", "No title"),
                "url": hit.get("url", ""),
                "summary": hit.get("story_text") or "No summary",
                "source": "Hacker News",
                "score": hit.get("points", 0),
                "fetched_at": datetime.now().isoformat()
            })

    # Process Reddit shape
    elif source_name == "Reddit" and source_data.get("data"):
        for post in source_data["data"].get("children", []):
            post_data = post.get("data", {})
            processed_articles.append({
                "title": post_data.get("title", "No title"),
                "url": post_data.get("url", ""),
                "summary": post_data.get("selftext", "")[:200],
                "source": "Reddit",
                "score": post_data.get("score", 0),
                "fetched_at": datetime.now().isoformat()
            })

# Sort by score descending
processed_articles.sort(key=lambda x: x["score"], reverse=True)

# Return as n8n items
return [{"json": article} for article in processed_articles]
```

### Key Techniques

- Normalise different data structures in one loop
- Discriminate on a field in the item, not on the originating node
- Sort by criteria
- Return properly formatted items

**Note**: Python cannot reach a named node. Bring every source onto this node's input with a **Merge** node, or
write the node in JavaScript and use `$('Node Name')` - see [code-javascript.md](code-javascript.md).

---

## Pattern 2: Regex-Based Filtering

**Use case**: Filter items based on pattern matching in text fields.

**Scenario**: Filter support tickets by priority keywords.

### Implementation

```python
import re

priority_tickets = []

# High priority keywords pattern
high_priority_pattern = re.compile(
    r'\b(urgent|critical|emergency|asap|down|outage|broken)\b',
    re.IGNORECASE
)

for item in _items:
    ticket = item["json"]

    # Check subject and description
    subject = ticket.get("subject", "")
    description = ticket.get("description", "")
    combined_text = f"{subject} {description}"

    # Find matches
    matches = high_priority_pattern.findall(combined_text)

    if matches:
        priority_tickets.append({
            "json": {
                **ticket,
                "priority": "high",
                "matched_keywords": sorted(set(matches)),
                "keyword_count": len(matches)
            }
        })
    else:
        priority_tickets.append({
            "json": {
                **ticket,
                "priority": "normal",
                "matched_keywords": [],
                "keyword_count": 0
            }
        })

# Sort by keyword count (most urgent first)
priority_tickets.sort(key=lambda x: x["json"]["keyword_count"], reverse=True)

return priority_tickets
```

### Key Techniques

- Use re.compile() for reusable patterns
- re.IGNORECASE for case-insensitive matching
- Combine multiple text fields for searching
- Extract and deduplicate matches
- Sort by priority indicators

---

## Pattern 3: Markdown to Structured Data

**Use case**: Parse markdown text into structured data.

**Scenario**: Extract tasks from a markdown checklist posted to a webhook.

### Implementation

```python
import re

if not _items:
    return []

# Webhook payload lives under ["body"]
markdown_text = _items[0]["json"].get("body", {}).get("markdown", "")

# Parse markdown checklist
tasks = []
lines = markdown_text.split("\n")

for line in lines:
    # Match: - [ ] Task or - [x] Task
    match = re.match(r'^\s*-\s*\[([ x])\]\s*(.+)$', line, re.IGNORECASE)

    if match:
        checked = match.group(1).lower() == 'x'
        task_text = match.group(2).strip()

        # Extract priority if present (e.g. [P1], [HIGH])
        priority_match = re.search(r'\[(P\d|HIGH|MEDIUM|LOW)\]', task_text, re.IGNORECASE)
        priority = priority_match.group(1).upper() if priority_match else "NORMAL"

        # Remove priority tag from text
        clean_text = re.sub(r'\[(P\d|HIGH|MEDIUM|LOW)\]', '', task_text, flags=re.IGNORECASE).strip()

        tasks.append({
            "text": clean_text,
            "completed": checked,
            "priority": priority,
            "original_line": line.strip()
        })

return [{
    "json": {
        "tasks": tasks,
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t["completed"]),
        "pending": sum(1 for t in tasks if not t["completed"])
    }
}]
```

### Key Techniques

- Line-by-line parsing
- Multiple regex patterns for extraction
- Extract metadata from text
- Calculate summary statistics
- Return structured data

---

## Pattern 4: JSON Object Comparison

**Use case**: Compare two JSON objects to find differences.

**Scenario**: Compare old and new user profile data arriving as two items.

### Implementation

```python
# Assume first item is old data, second is new data
old_data = _items[0]["json"] if len(_items) > 0 else {}
new_data = _items[1]["json"] if len(_items) > 1 else {}

changes = {
    "added": {},
    "removed": {},
    "modified": {},
    "unchanged": {}
}

# Find all unique keys
all_keys = set(old_data.keys()) | set(new_data.keys())

for key in all_keys:
    old_value = old_data.get(key)
    new_value = new_data.get(key)

    if key not in old_data:
        changes["added"][key] = new_value
    elif key not in new_data:
        changes["removed"][key] = old_value
    elif old_value != new_value:
        changes["modified"][key] = {
            "old": old_value,
            "new": new_value
        }
    else:
        changes["unchanged"][key] = old_value

return [{
    "json": {
        "changes": changes,
        "summary": {
            "added_count": len(changes["added"]),
            "removed_count": len(changes["removed"]),
            "modified_count": len(changes["modified"]),
            "unchanged_count": len(changes["unchanged"]),
            "has_changes": bool(changes["added"] or changes["removed"] or changes["modified"])
        }
    }
}]
```

### Key Techniques

- Set operations for key comparison
- Dictionary .get() for safe access
- Categorize changes by type
- No imports required - runs on Cloud

---

## Pattern 5: CRM Data Transformation

**Use case**: Transform CRM data to standard format.

**Scenario**: Normalize data from different CRM systems.

### Implementation

```python
from datetime import datetime
import re

normalized_contacts = []

for item in _items:
    raw_contact = item["json"]
    source = raw_contact.get("source", "unknown")

    # Normalize email
    email = raw_contact.get("email", "").lower().strip()

    # Normalize phone (remove non-digits)
    phone = re.sub(r'\D', '', raw_contact.get("phone", ""))

    # Parse name
    if "full_name" in raw_contact:
        name_parts = raw_contact["full_name"].split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
    else:
        first_name = raw_contact.get("first_name", "")
        last_name = raw_contact.get("last_name", "")

    # Normalize status
    status_raw = raw_contact.get("status", "").lower()
    status = "active" if status_raw in ["active", "enabled", "true", "1"] else "inactive"

    normalized_contacts.append({
        "json": {
            "id": raw_contact.get("id", ""),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "full_name": f"{first_name} {last_name}".strip(),
            "email": email,
            "phone": phone,
            "status": status,
            "source": source,
            "normalized_at": datetime.now().isoformat(),
            "original_data": raw_contact
        }
    })

return normalized_contacts
```

### Key Techniques

- Multiple field name variations handling
- String cleaning and normalization
- Regex for phone number cleaning
- Name parsing logic
- Preserve original data

---

## Pattern 6: Release Notes Processing

**Use case**: Parse release notes and categorize changes.

**Scenario**: Extract features, fixes, and breaking changes from release notes posted to a webhook.

### Implementation

```python
import re

if not _items:
    return []

release_notes = _items[0]["json"].get("body", {}).get("notes", "")

categories = {
    "features": [],
    "fixes": [],
    "breaking": [],
    "other": []
}

for line in release_notes.split("\n"):
    line = line.strip()

    # Skip empty lines and headers
    if not line or line.startswith("#"):
        continue

    # Remove bullet points
    clean_line = re.sub(r'^[\*\-\+]\s*', '', line)

    # Categorize
    if re.search(r'\b(feature|add|new)\b', clean_line, re.IGNORECASE):
        categories["features"].append(clean_line)
    elif re.search(r'\b(fix|bug|patch|resolve)\b', clean_line, re.IGNORECASE):
        categories["fixes"].append(clean_line)
    elif re.search(r'\b(breaking|deprecated|remove)\b', clean_line, re.IGNORECASE):
        categories["breaking"].append(clean_line)
    else:
        categories["other"].append(clean_line)

return [{
    "json": {
        "categories": categories,
        "summary": {
            "features": len(categories["features"]),
            "fixes": len(categories["fixes"]),
            "breaking": len(categories["breaking"]),
            "other": len(categories["other"]),
            "total": sum(len(v) for v in categories.values())
        }
    }
}]
```

### Key Techniques

- Line-by-line parsing
- Pattern-based categorization
- Bullet point removal
- Skip headers and empty lines
- Summary statistics

---

## Pattern 7: Array Transformation

**Use case**: Reshape arrays and extract specific fields.

**Scenario**: Transform user data to extract specific fields.

### Implementation

```python
transformed = []

for item in _items:
    user = item["json"]

    # Extract nested fields
    profile = user.get("profile", {})
    settings = user.get("settings", {})

    transformed.append({
        "json": {
            "user_id": user.get("id"),
            "email": user.get("email"),
            "name": profile.get("name", "Unknown"),
            "avatar": profile.get("avatar_url"),
            "bio": profile.get("bio", "")[:100],  # Truncate to 100 chars
            "notifications_enabled": settings.get("notifications", True),
            "theme": settings.get("theme", "light"),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login_at")
        }
    })

return transformed
```

### Key Techniques

- Field extraction from nested objects
- Default values with .get()
- String truncation
- Flattening nested structures
- No imports required - runs on Cloud

---

## Pattern 8: Dictionary Lookup

**Use case**: Create lookup dictionary for fast data access.

**Scenario**: Look up user details by ID.

### Implementation

```python
# Build lookup dictionary
users_by_id = {}

for item in _items:
    user = item["json"]
    user_id = user.get("id")

    if user_id:
        users_by_id[user_id] = {
            "name": user.get("name"),
            "email": user.get("email"),
            "status": user.get("status")
        }

# Example: Look up specific users
lookup_ids = [1, 3, 5]
looked_up = []

for user_id in lookup_ids:
    if user_id in users_by_id:
        looked_up.append({
            "json": {
                "id": user_id,
                **users_by_id[user_id],
                "found": True
            }
        })
    else:
        looked_up.append({
            "json": {
                "id": user_id,
                "found": False
            }
        })

return looked_up
```

### Key Techniques

- O(1) lookup time
- Handle missing keys gracefully
- Preserve lookup order
- No imports required - runs on Cloud

---

## Pattern 9: Top N Filtering

**Use case**: Get top items by score or value.

**Scenario**: Get top 10 products by sales.

### Implementation

```python
products = []

for item in _items:
    product = item["json"]
    products.append({
        "id": product.get("id"),
        "name": product.get("name"),
        "sales": product.get("sales", 0),
        "revenue": product.get("revenue", 0.0),
        "category": product.get("category")
    })

# Sort by sales descending, then take the top 10
products.sort(key=lambda p: p["sales"], reverse=True)
top_10 = products[:10]

return [
    {
        "json": {
            **product,
            "rank": index + 1
        }
    }
    for index, product in enumerate(top_10)
]
```

### Key Techniques

- List sorting with custom key
- Slicing for top N (never raises IndexError)
- Add ranking information
- No imports required - runs on Cloud

---

## Pattern 10: String Aggregation

**Use case**: Aggregate strings with formatting.

**Scenario**: Create summary text from multiple items.

### Implementation

```python
messages = []

for item in _items:
    data = item["json"]

    user = data.get("user", "Unknown")
    message = data.get("message", "")
    timestamp = data.get("timestamp", "")

    messages.append(f"[{timestamp}] {user}: {message}")

summary = "\n".join(messages)

total_length = sum(len(msg) for msg in messages)
average_length = total_length / len(messages) if messages else 0

return [{
    "json": {
        "summary": summary,
        "message_count": len(messages),
        "total_characters": total_length,
        "average_length": round(average_length, 2)
    }
}]
```

### Key Techniques

- String formatting with f-strings
- Join lists with separator
- Handle empty lists
- No imports required - runs on Cloud

---

## Pattern Comparison: Python vs JavaScript

### Data Access

```python
# Python (native)
all_items = _items                       # all-items mode
first_item = _items[0] if _items else None
current = _item                          # per-item mode
webhook_data = _items[0]["json"]["body"]
# other node: not available in Python
```

```javascript
// JavaScript
const allItems = $input.all();
const firstItem = $input.first();
const current = $input.item;
const webhookData = $json.body;
const otherNode = $('HTTP Request').first().json;   // no Python equivalent
```

### Dictionary/Object Access

```python
# Python - bracket access only
name = user["name"]           # May raise KeyError
name = user.get("name", "?")  # Safe with default
```

```javascript
// JavaScript - dot or bracket
const name = user.name;              // May be undefined
const name = user.name || "?";       // Safe with default
```

### Array Operations

```python
# Python - list comprehension
filtered = [item for item in _items if item["json"]["active"]]
```

```javascript
// JavaScript - array methods
const filtered = $input.all().filter(item => item.json.active);
```

### Sorting

```python
# Python
items.sort(key=lambda x: x["json"]["score"], reverse=True)
```

```javascript
// JavaScript
items.sort((a, b) => b.json.score - a.json.score);
```

---

## Best Practices

### 1. Use .get() for Safe Access

```python
# ✅ SAFE: Use .get() with defaults
name = user.get("name", "Unknown")
email = user.get("email", "no-email@example.com")

# ❌ RISKY: Direct key access
name = user["name"]  # KeyError if missing!
```

### 2. Handle Empty Lists

```python
# ✅ SAFE: Check before processing
if not _items:
    return [{"json": {"error": "No items"}}]

first = _items[0]

# ❌ RISKY: Assume items exist
first = _items[0]  # IndexError if empty!
```

### 3. Use List Comprehensions

```python
# ✅ PYTHONIC: List comprehension
active = [item for item in _items if item["json"].get("active")]

# ❌ VERBOSE: Traditional loop
active = []
for item in _items:
    if item["json"].get("active"):
        active.append(item)
```

### 4. Return Proper Format

```python
# ✅ CORRECT: List of dicts with "json" key
return [{"json": {"field": "value"}}]

# ❌ WRONG: Just the data
return {"field": "value"}

# ❌ WRONG: List without "json" wrapper
return [{"field": "value"}]
```

### 5. Know What You May Import

```python
# ✅ ALWAYS SAFE: built-ins and comprehensions need no allowlist
average = sum(numbers) / len(numbers) if numbers else 0

# ⚠️ CONDITIONAL: standard library needs N8N_RUNNERS_STDLIB_ALLOW, and fails on Cloud
import statistics
average = statistics.mean(numbers)

# ⚠️ SELF-HOSTED ONLY: needs the module in the runners image AND N8N_RUNNERS_EXTERNAL_ALLOW
import numpy
```

---

## When to Use Each Pattern

| Pattern | When to Use |
|---------|-------------|
| Multi-Source Aggregation | Normalising differently-shaped items on one input |
| Regex Filtering | Text pattern matching, validation, extraction |
| Markdown Parsing | Processing formatted text into structured data |
| JSON Comparison | Detecting changes between objects |
| CRM Transformation | Normalizing data from different systems |
| Release Notes | Categorizing text by keywords |
| Array Transformation | Reshaping data, extracting fields |
| Dictionary Lookup | Fast ID-based lookups |
| Top N Filtering | Getting best/worst items by criteria |
| String Aggregation | Creating formatted text summaries |

---

## Summary

**Key Takeaways**:
- `_items` in all-items mode, `_item` in per-item mode - that is the whole surface
- Bracket access only: `item["json"]["field"]`
- Use `.get()` for safe dictionary access
- Handle empty lists before indexing
- Return proper n8n format: `[{"json": {...}}]`

**Remember**:
- JavaScript is recommended for most use cases
- Every import depends on the runner allowlist; n8n Cloud permits none
- Cross-node data is JavaScript-only - merge it into the input instead
- Code node is for data transformation, not API calls

**See Also**:
- [code-python.md](code-python.md) - Python Code overview
- [code-python-data-access.md](code-python-data-access.md) - Data access patterns
- [code-python-standard-library.md](code-python-standard-library.md) - Import allowlists
- [code-python-error-patterns.md](code-python-error-patterns.md) - Avoid common mistakes
