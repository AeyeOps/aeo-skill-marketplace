# Standard Library Reference - Python Code Node

Complete guide to importing Python modules in n8n Code nodes: what the two runner allowlists control, and how the
common standard library modules are used once they are permitted.

> **Removed in n8n 2.0**: the Pyodide helpers `_input`, `_json` — plus dot access on
> item data. Every example below reads its input from `_items` with bracket access.

---

## ⚠️ Critical Limitation

**IMPORTS ARE ALLOWLISTED - YOU DO NOT DECIDE WHAT YOU CAN IMPORT**

Native Python denies insecure built-ins by default. Nothing is importable until the operator permits it, and this
applies to the **standard library** as much as to third-party packages.

| Variable | Controls | Example value |
|----------|----------|---------------|
| `N8N_RUNNERS_STDLIB_ALLOW` | Which **standard library** modules may be imported | `json,datetime,re` |
| `N8N_RUNNERS_EXTERNAL_ALLOW` | Which **third-party** packages may be imported | `numpy,pandas` |

Both are comma-separated lists in the Python runner's `env-overrides` block of `n8n-task-runners.json`:

```json
{
  "task-runners": [{
    "runner-type": "python",
    "env-overrides": {
      "N8N_RUNNERS_STDLIB_ALLOW": "json,datetime,re,base64,hashlib",
      "N8N_RUNNERS_EXTERNAL_ALLOW": "numpy,pandas"
    }
  }]
}
```

### Self-Hosted: Third-Party Packages Are Supported

`numpy` and `pandas` are ordinary cases, not exceptions. Extend the `n8nio/runners` image (1.121.0 or later, and
matching your `n8nio/n8n` image version), install the package with the image's package manager, then add it to
`N8N_RUNNERS_EXTERNAL_ALLOW`. The old "no pip packages, ever" rule is not how native Python works.

### n8n Cloud: No Imports At All

On n8n Cloud the Python option allows **no imports** - standard library included. Cloud Python code must run on
built-ins alone: comprehensions, f-strings, `sum`/`sorted`/`len`/`min`/`max`, and `dict`/`list`/`set`/`str` methods.

### Writing Code Without Knowing the Allowlist

```python
# ✅ ALWAYS SAFE - built-ins need no allowlist and work on Cloud
total = sum(item["json"].get("amount", 0) for item in _items)
ranked = sorted(_items, key=lambda i: i["json"].get("score", 0), reverse=True)
unique = {item["json"].get("id") for item in _items}

# ⚠️ CONDITIONAL - needs the module in N8N_RUNNERS_STDLIB_ALLOW, fails on Cloud
import json

# ⚠️ SELF-HOSTED ONLY - needs the module in the image AND N8N_RUNNERS_EXTERNAL_ALLOW
import pandas
```

Import failures surface at execution time, not while editing. If you do not know the instance's allowlist, stay on
built-ins or ask what is permitted.

**Recommendation**: Use **JavaScript** for most use cases. Its libraries need no operator configuration.

---

## Available Modules

"Available" means **allowlisted on this instance**. The modules below are the ones most worth requesting; each
section states the allowlist entry it needs.

### Priority 1: Most Useful (Request These First)

1. **json** - JSON parsing and generation
2. **datetime** - Date and time operations
3. **re** - Regular expressions
4. **base64** - Base64 encoding/decoding
5. **hashlib** - Hashing (MD5, SHA256, etc.)
6. **urllib.parse** - URL parsing and encoding

### Priority 2: Moderately Useful

7. **math** - Mathematical functions
8. **random** - Random number generation
9. **statistics** - Statistical functions
10. **collections** - Specialized data structures

### Priority 3: Occasionally Useful

11. **itertools** - Iterator tools
12. **functools** - Higher-order functions
13. **operator** - Standard operators as functions
14. **string** - String constants and templates
15. **textwrap** - Text wrapping utilities

---

## Module 1: json - JSON Operations

**Allowlist entry**: `json` in `N8N_RUNNERS_STDLIB_ALLOW`

Parse and generate JSON data. Note that item data is already a Python dict - you need `json` only for strings that
carry JSON inside them.

### Parse JSON String

```python
import json

json_string = '{"name": "Alice", "age": 30}'
data = json.loads(json_string)

return [{
    "json": {
        "name": data["name"],
        "age": data["age"],
        "parsed": True
    }
}]
```

### Generate JSON String

```python
import json

data = {
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "total": 2
}

json_string = json.dumps(data, indent=2)

return [{
    "json": {
        "json_output": json_string,
        "length": len(json_string)
    }
}]
```

### Handle JSON Errors

```python
import json

if not _items:
    return []

json_string = _items[0]["json"].get("body", {}).get("data", "")

try:
    parsed = json.loads(json_string)
    status = "valid"
    error = None
except json.JSONDecodeError as exc:
    parsed = None
    status = "invalid"
    error = str(exc)

return [{
    "json": {
        "status": status,
        "data": parsed,
        "error": error
    }
}]
```

### Pretty Print JSON

```python
import json

data = _items[0]["json"] if _items else {}

return [{
    "json": {
        "formatted": json.dumps(data, indent=2, sort_keys=True)
    }
}]
```

---

## Module 2: datetime - Date and Time

**Allowlist entry**: `datetime` in `N8N_RUNNERS_STDLIB_ALLOW`

Python has no n8n date helpers - Luxon and the workflow timezone are JavaScript-side only, so `datetime` is the
whole toolkit here.

### Current Date and Time

```python
from datetime import datetime

now = datetime.now()

return [{
    "json": {
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "formatted": now.strftime("%B %d, %Y at %I:%M %p")
    }
}]
```

### Parse Date String

```python
from datetime import datetime

date_string = "2025-01-15T14:30:00"
dt = datetime.fromisoformat(date_string)

return [{
    "json": {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "weekday": dt.strftime("%A")
    }
}]
```

### Date Calculations

```python
from datetime import datetime, timedelta

now = datetime.now()

return [{
    "json": {
        "now": now.isoformat(),
        "tomorrow": (now + timedelta(days=1)).isoformat(),
        "yesterday": (now - timedelta(days=1)).isoformat(),
        "next_week": (now + timedelta(weeks=1)).isoformat(),
        "one_hour_ago": (now - timedelta(hours=1)).isoformat()
    }
}]
```

### Compare Dates

```python
from datetime import datetime

date1 = datetime(2025, 1, 15)
date2 = datetime(2025, 1, 20)

diff = date2 - date1

return [{
    "json": {
        "days_difference": diff.days,
        "seconds_difference": diff.total_seconds(),
        "date1_is_earlier": date1 < date2,
        "date2_is_later": date2 > date1
    }
}]
```

### Format Dates

```python
from datetime import datetime

dt = datetime.now()

return [{
    "json": {
        "iso": dt.isoformat(),
        "us_format": dt.strftime("%m/%d/%Y"),
        "eu_format": dt.strftime("%d/%m/%Y"),
        "long_format": dt.strftime("%A, %B %d, %Y"),
        "time_12h": dt.strftime("%I:%M %p"),
        "time_24h": dt.strftime("%H:%M:%S")
    }
}]
```

---

## Module 3: re - Regular Expressions

**Allowlist entry**: `re` in `N8N_RUNNERS_STDLIB_ALLOW`

Pattern matching, text extraction, validation.

### Pattern Matching

```python
import re

text = "Email: alice@example.com, Phone: 555-1234"

email_match = re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
phone_match = re.search(r'\d{3}-\d{4}', text)

return [{
    "json": {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None
    }
}]
```

### Extract All Matches

```python
import re

text = "Tags: #python #automation #workflow #n8n"

hashtags = re.findall(r'#(\w+)', text)

return [{
    "json": {
        "tags": hashtags,
        "count": len(hashtags)
    }
}]
```

### Replace Patterns

```python
import re

text = "Price: $99.99, Discount: $10.00"

cleaned = re.sub(r'\$', '', text)
normalized = re.sub(r'\s+', ' ', cleaned)

return [{
    "json": {
        "original": text,
        "cleaned": cleaned,
        "normalized": normalized
    }
}]
```

### Validate Format

```python
import re

email = _items[0]["json"].get("body", {}).get("email", "") if _items else ""

is_valid = bool(re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email))

return [{
    "json": {
        "email": email,
        "valid": is_valid
    }
}]
```

### Split on Pattern

```python
import re

text = "apple,banana;orange|grape"

items = [item.strip() for item in re.split(r'[,;|]', text)]

return [{
    "json": {
        "items": items,
        "count": len(items)
    }
}]
```

---

## Module 4: base64 - Encoding/Decoding

**Allowlist entry**: `base64` in `N8N_RUNNERS_STDLIB_ALLOW`

Encode text payloads, build auth headers.

### Encode String to Base64

```python
import base64

text = "Hello, World!"

encoded_string = base64.b64encode(text.encode('utf-8')).decode('utf-8')

return [{
    "json": {
        "original": text,
        "encoded": encoded_string
    }
}]
```

### Decode Base64 to String

```python
import base64

encoded = "SGVsbG8sIFdvcmxkIQ=="

decoded_string = base64.b64decode(encoded).decode('utf-8')

return [{
    "json": {
        "encoded": encoded,
        "decoded": decoded_string
    }
}]
```

### Basic Auth Header

```python
import base64

# Read credentials from the input, never hardcode them -
# the Code node has no access to n8n credentials or secrets
data = _items[0]["json"] if _items else {}
credentials = f"{data.get('username', '')}:{data.get('password', '')}"

encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

return [{
    "json": {
        "authorization": f"Basic {encoded}"
    }
}]
```

---

## Module 5: hashlib - Hashing

**Allowlist entry**: `hashlib` in `N8N_RUNNERS_STDLIB_ALLOW`

Generate checksums, hash values, create stable IDs.

### MD5 Hash

```python
import hashlib

text = "Hello, World!"

return [{
    "json": {
        "original": text,
        "md5": hashlib.md5(text.encode('utf-8')).hexdigest()
    }
}]
```

### SHA256 Hash

```python
import hashlib

value = _items[0]["json"].get("body", {}).get("token", "") if _items else ""

return [{
    "json": {
        "hashed": hashlib.sha256(value.encode('utf-8')).hexdigest()
    }
}]
```

### Generate Stable ID

```python
import hashlib

results = []

for item in _items:
    data = item["json"]
    seed = f"{data.get('user_id', 'unknown')}-{data.get('created_at', '')}"

    results.append({
        "json": {
            **data,
            "id": hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]
        }
    })

return results
```

---

## Module 6: urllib.parse - URL Operations

**Allowlist entry**: `urllib` in `N8N_RUNNERS_STDLIB_ALLOW`

Parse URLs, encode parameters. Note this is `urllib.parse` only - the Code node is not the place to open network
connections; use the HTTP Request node.

### Parse URL

```python
from urllib.parse import urlparse

url = "https://example.com/path?key=value&foo=bar#section"

parsed = urlparse(url)

return [{
    "json": {
        "scheme": parsed.scheme,      # "https"
        "netloc": parsed.netloc,      # "example.com"
        "path": parsed.path,          # "/path"
        "query": parsed.query,        # "key=value&foo=bar"
        "fragment": parsed.fragment   # "section"
    }
}]
```

### URL Encode Parameters

```python
from urllib.parse import urlencode

params = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "message": "Hello, World!"
}

encoded = urlencode(params)

return [{
    "json": {
        "query_string": encoded,
        "full_url": f"https://api.example.com/submit?{encoded}"
    }
}]
```

### Parse Query String

```python
from urllib.parse import parse_qs

query_string = "name=Alice&age=30&tags=python&tags=n8n"

params = parse_qs(query_string)

return [{
    "json": {
        "name": params.get("name", [""])[0],
        "age": int(params.get("age", ["0"])[0]),
        "tags": params.get("tags", [])
    }
}]
```

### URL Encode/Decode Strings

```python
from urllib.parse import quote, unquote

text = "Hello, World! 你好"

encoded = quote(text)
decoded = unquote(encoded)

return [{
    "json": {
        "original": text,
        "encoded": encoded,
        "decoded": decoded
    }
}]
```

---

## Module 7: math - Mathematical Operations

**Allowlist entry**: `math` in `N8N_RUNNERS_STDLIB_ALLOW`

Advanced math functions. `round`, `abs`, `min`, `max`, `sum` and `**` are built-ins and need no allowlist.

### Basic Math Functions

```python
import math

number = 16.7

return [{
    "json": {
        "ceiling": math.ceil(number),      # 17
        "floor": math.floor(number),       # 16
        "rounded": round(number),          # 17 (built-in)
        "square_root": math.sqrt(16),      # 4.0
        "power": math.pow(2, 3),           # 8.0
        "absolute": math.fabs(-5.5)        # 5.5
    }
}]
```

### Trigonometry

```python
import math

angle_radians = math.radians(45)

return [{
    "json": {
        "sine": math.sin(angle_radians),
        "cosine": math.cos(angle_radians),
        "tangent": math.tan(angle_radians),
        "pi": math.pi,
        "e": math.e
    }
}]
```

### Logarithms

```python
import math

number = 100

return [{
    "json": {
        "log10": math.log10(number),     # 2.0
        "natural_log": math.log(number), # 4.605...
        "log2": math.log2(number)        # 6.644...
    }
}]
```

---

## Module 8: random - Random Numbers

**Allowlist entry**: `random` in `N8N_RUNNERS_STDLIB_ALLOW`

Generate random data, sampling.

### Random Numbers

```python
import random

return [{
    "json": {
        "random_float": random.random(),            # 0.0 to 1.0
        "random_int": random.randint(1, 100),       # 1 to 100
        "random_range": random.randrange(0, 100, 5) # 0, 5, 10, ..., 95
    }
}]
```

### Random Choice

```python
import random

colors = ["red", "green", "blue", "yellow"]

return [{
    "json": {
        "random_color": random.choice(colors),
        "random_item": random.choice(_items)["json"] if _items else None
    }
}]
```

### Shuffle List

```python
import random

shuffled = list(_items)
random.shuffle(shuffled)

return shuffled
```

### Random Sample

```python
import random

sample_size = min(10, len(_items))
sample = random.sample(_items, sample_size)

return [{"json": item["json"]} for item in sample]
```

---

## Module 9: statistics - Statistical Functions

**Allowlist entry**: `statistics` in `N8N_RUNNERS_STDLIB_ALLOW`

Calculate stats from data. `sum`, `min`, `max` and `len` cover a surprising amount without it.

### Basic Statistics

```python
import statistics

numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

return [{
    "json": {
        "mean": statistics.mean(numbers),          # 55.0
        "median": statistics.median(numbers),      # 55.0
        "mode": statistics.mode([1, 2, 2, 3]),     # 2
        "stdev": statistics.stdev(numbers),        # 30.28...
        "variance": statistics.variance(numbers)   # 916.67...
    }
}]
```

### Aggregate from Items

```python
import statistics

amounts = [item["json"].get("amount", 0) for item in _items]

if not amounts:
    return [{"json": {"error": "No data"}}]

return [{
    "json": {
        "count": len(amounts),
        "total": sum(amounts),
        "average": statistics.mean(amounts),
        "median": statistics.median(amounts),
        "min": min(amounts),
        "max": max(amounts),
        "range": max(amounts) - min(amounts)
    }
}]
```

---

## Workarounds for Missing Libraries

### HTTP Requests

There is no HTTP client for the Python Code node - `requests` is not a candidate for any allowlist, and opening
sockets is not what this runtime is for.

```python
# ✅ Add an HTTP Request node BEFORE the Code node, then read its response
if not _items:
    return []

response_data = _items[0]["json"]

return [{
    "json": {
        "status": response_data.get("status"),
        "data": response_data.get("body"),
        "processed": True
    }
}]
```

### Data Processing Without pandas

Self-hosted, `pandas` is allowlistable. Everywhere else, built-ins cover the common cases:

```python
# ✅ Filter
active_items = [
    item for item in _items
    if item["json"].get("status") == "active"
]

# ✅ Group by (no imports needed)
grouped = {}
for item in _items:
    category = item["json"].get("category", "other")
    grouped.setdefault(category, []).append(item["json"])

# ✅ Aggregate (no imports needed)
amounts = [item["json"].get("amount", 0) for item in _items]
total = sum(amounts)
average = total / len(amounts) if amounts else 0

return [{
    "json": {
        "active_count": len(active_items),
        "grouped": grouped,
        "total": total,
        "average": average
    }
}]
```

### Database Operations

Database drivers are not part of the Code node's job.

```python
# ✅ Add a Postgres/MySQL/MongoDB node BEFORE the Code node,
# then process its result rows from the input
return [{
    "json": {
        "record_count": len(_items),
        "processed": True
    }
}]
```

---

## Complete Standard Library List

The list below is **candidates, not guarantees**. Each still needs its name in `N8N_RUNNERS_STDLIB_ALLOW`, and none
of them work on n8n Cloud.

**Commonly requested**:
- json
- datetime, time
- re
- base64
- hashlib
- urllib.parse
- math
- random
- statistics
- collections (defaultdict, Counter, namedtuple)
- itertools
- functools
- operator
- string
- textwrap

**Less common but reasonable to request**:
- copy
- typing
- enum
- decimal
- fractions
- uuid

**Do not expect these to be allowlisted**: native Python denies insecure built-ins by default, so anything that
touches the filesystem, processes, or the network - `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`,
`urllib.request` - is the kind of module an operator has good reason to refuse. Design around them.

**Third-party packages** (self-hosted only, via an extended `n8nio/runners` image plus
`N8N_RUNNERS_EXTERNAL_ALLOW`): numpy, pandas and similar data libraries are supported this way. HTTP clients,
browser drivers, database drivers and web frameworks are the wrong tool here even when installable - n8n has nodes
for all of them.

---

## Best Practices

### 1. Prefer Built-Ins Over Imports

```python
# ✅ GOOD: no allowlist dependency, runs on Cloud
totals = {}
for item in _items:
    key = item["json"].get("category", "other")
    totals[key] = totals.get(key, 0) + item["json"].get("amount", 0)

return [{"json": totals}]
```

### 2. Fall Back to n8n Nodes

```python
# For anything needing a network call, a database, or file parsing,
# use the node - HTTP Request, Postgres/MySQL, Extract from File -
# and let the Code node handle only the transformation.
result = _items[0]["json"] if _items else {}
return [{"json": {"processed": result}}]
```

### 3. Combine Multiple Modules

```python
import json
import base64
import hashlib

# Requires json, base64 and hashlib all in N8N_RUNNERS_STDLIB_ALLOW
if not _items:
    return []

data = _items[0]["json"].get("body", {})

return [{
    "json": {
        "user_id": hashlib.sha256(data.get("email", "").encode()).hexdigest()[:16],
        "encoded_data": base64.b64encode(json.dumps(data).encode()).decode()
    }
}]
```

### 4. Fail Loudly on a Missing Module

Do not wrap imports in `try`/`except ImportError` to keep a workflow limping. A missing module means the runner is
not configured for this code; a swallowed import turns that into silently wrong output. Let it raise, and fix the
allowlist or the approach.

---

## Summary

**The rule that replaces "standard library only"**:
- `N8N_RUNNERS_STDLIB_ALLOW` gates standard library imports
- `N8N_RUNNERS_EXTERNAL_ALLOW` gates third-party imports (self-hosted, extended `n8nio/runners` image)
- n8n Cloud allows **no imports at all**

**Most Useful Modules to Request**:
1. json - parse/generate JSON strings
2. datetime - date operations (Python has no n8n date helpers)
3. re - regular expressions
4. base64 - encoding
5. hashlib - hashing
6. urllib.parse - URL operations

**Recommended Approach**:
- Write on built-ins where you can - they need no allowlist and run on Cloud
- Use **JavaScript** for most use cases; its libraries need no operator configuration
- Use n8n nodes for HTTP, databases, and file parsing

**See Also**:
- [code-python.md](code-python.md) - Python Code overview
- [code-python-data-access.md](code-python-data-access.md) - Data access patterns
- [code-python-common-patterns.md](code-python-common-patterns.md) - Production patterns
- [code-python-error-patterns.md](code-python-error-patterns.md) - Avoid common mistakes
