# Property Dependencies Guide

Deep dive into n8n property dependencies and displayOptions mechanism.

---

## What Are Property Dependencies?

**Definition**: Rules that control when fields are visible or required based on other field values.

**Mechanism**: `displayOptions` in node schema

**Purpose**:
- Show relevant fields only
- Hide irrelevant fields
- Simplify configuration UX
- Prevent invalid configurations

---

## displayOptions Structure

### Basic Format

```javascript
{
  "name": "fieldName",
  "type": "string",
  "displayOptions": {
    "show": {
      "otherField": ["value1", "value2"]
    }
  }
}
```

**Translation**: Show `fieldName` when `otherField` equals "value1" OR "value2"

### Show vs Hide

#### show (Most Common)

**Show field when condition matches**:
```javascript
{
  "name": "contentType",
  "displayOptions": {
    "show": {
      "sendBody": [true]
    }
  }
}
```

**Meaning**: Show `contentType` when `sendBody = true`

#### hide (Less Common)

**Hide field when condition matches**:
```javascript
{
  "name": "advanced",
  "displayOptions": {
    "hide": {
      "simpleMode": [true]
    }
  }
}
```

**Meaning**: Hide `advanced` when `simpleMode = true`

### Multiple Conditions (AND Logic)

```javascript
{
  "name": "jsonBody",
  "displayOptions": {
    "show": {
      "sendBody": [true],
      "contentType": ["json"],
      "specifyBody": ["json"]
    }
  }
}
```

**Meaning**: Show `jsonBody` when:
- `sendBody = true` AND
- `contentType = json` AND
- `specifyBody = json`

**All conditions must match** (AND logic)

### Multiple Values (OR Logic)

```javascript
{
  "name": "someField",
  "displayOptions": {
    "show": {
      "method": ["POST", "PUT", "PATCH"]
    }
  }
}
```

**Meaning**: Show `someField` when:
- `method = POST` OR
- `method = PUT` OR
- `method = PATCH`

**Any value matches** (OR logic)

---

## Common Dependency Patterns

### Pattern 1: Boolean Toggle

**Use case**: Optional feature flag

**Example**: HTTP Request sendBody
```javascript
// Field: sendBody (boolean)
{
  "name": "sendBody",
  "type": "boolean",
  "default": false
}

// Field: contentType (depends on sendBody)
{
  "name": "contentType",
  "displayOptions": {
    "show": {
      "sendBody": [true]
    }
  }
}
```

**Flow**:
1. User sees sendBody checkbox
2. When checked → contentType, and the body fields beneath it, appear
3. When unchecked → they hide

### Pattern 2: Resource/Operation Cascade

**Use case**: Different operations show different fields

**Example**: Slack message operations
```javascript
// Operation: post
{
  "name": "channelId",
  "displayOptions": {
    "show": {
      "resource": ["message"],
      "operation": ["post"],
      "select": ["channel"]
    }
  }
}

// Operation: update
{
  "name": "ts",
  "displayOptions": {
    "show": {
      "resource": ["message"],
      "operation": ["update"]
    }
  }
}
```

**Flow**:
1. User selects resource="message"
2. User selects operation="post" and select="channel" → sees channelId
3. User changes to operation="update" → ts appears as the message identifier

### Pattern 3: Type-Specific Configuration

**Use case**: Different types need different fields

**Example**: IF node conditions (typeVersion 2.3)
```javascript
// Binary operations show rightValue
{
  "name": "rightValue",
  "displayOptions": {
    "show": {
      "operator.operation": ["equals", "notEquals", "contains"]
    }
  }
}

// Unary operations (isEmpty) hide rightValue
{
  "name": "rightValue",
  "displayOptions": {
    "hide": {
      "operator.operation": ["isEmpty", "isNotEmpty"]
    }
  }
}
```

### Pattern 4: Method-Specific Fields

**Use case**: HTTP Request opts in to each section separately

**Example**: HTTP Request
```javascript
// Query parameters
{
  "name": "queryParameters",
  "displayOptions": {
    "show": {
      "sendQuery": [true]
    }
  }
}

// Body content - gated by sendBody and specifyBody, not by method
{
  "name": "jsonBody",
  "displayOptions": {
    "show": {
      "sendBody": [true],
      "contentType": ["json"],
      "specifyBody": ["json"]
    }
  }
}
```

---

## Reading Dependencies with get_node

### Basic Usage

```javascript
const node = get_node({
  nodeType: "nodes-base.httpRequest",
  detail: "full"
});
```

No tool returns a pre-chewed dependency tree. `detail: 'full'` returns every property with its raw
`displayOptions`, and the dependency rules are those objects.

### Example Response

```javascript
{
  "nodeType": "nodes-base.httpRequest",
  "properties": [
    {
      "name": "sendBody",
      "type": "boolean",
      "default": false
    },
    {
      "name": "jsonBody",
      "displayOptions": {
        "show": {
          "sendBody": [true],
          "contentType": ["json"],
          "specifyBody": ["json"]
        }
      }
    },
    {
      "name": "queryParameters",
      "displayOptions": {
        "show": {
          "sendQuery": [true]
        }
      }
    },
    {
      "name": "headerParameters",
      "displayOptions": {
        "show": {
          "sendHeaders": [true]
        }
      }
    }
  ]
}
```

### When to Use

**✅ Use when**:
- Validation fails with "missing field" but you don't see that field
- A field appears/disappears unexpectedly
- You need to understand what controls field visibility
- Building dynamic configuration tools

**❌ Don't use when**:
- Simple configuration (standard detail is enough)
- Just starting configuration
- Field requirements are obvious

---

## Complex Dependency Examples

### Example 1: HTTP Request Complete Flow

**Scenario**: Configuring POST with JSON body

**Step 1**: Set method and url
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users"
  // Already valid - sendBody defaults to false
}
```

**Step 2**: Enable body
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "sendBody": true
  // → contentType and specifyBody become visible
}
```

**Step 3**: Choose how the body is specified
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json"
  // → jsonBody becomes visible
}
```

**Step 4**: Add content
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify({ name: 'John', email: 'john@example.com' }) }}"
}
// ✅ Valid!
```

**Dependency chain**:
```
sendBody=true
  → contentType visible
    → contentType=json
      → specifyBody visible
        → specifyBody=json
          → jsonBody visible
```

### Example 2: IF Node Operator Dependencies

**Scenario**: String comparison with different operators (IF typeVersion 2.3)

**Binary operator** (equals):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "operator": { "type": "string", "operation": "equals" }
        // → leftValue required
        // → rightValue required
        // → operator.singleValue should NOT be set
      }
    ]
  }
}
```

**Unary operator** (isEmpty):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "operator": { "type": "string", "operation": "isEmpty" }
        // → leftValue required
        // → rightValue should NOT be set
        // → operator.singleValue should be true (auto-added)
      }
    ]
  }
}
```

**Dependency table**:

| Operator | leftValue | rightValue | operator.singleValue |
|---|---|---|---|
| equals | Required | Required | false |
| notEquals | Required | Required | false |
| contains | Required | Required | false |
| isEmpty | Required | Hidden | true |
| isNotEmpty | Required | Hidden | true |

### Example 3: Slack Operation Matrix

**Scenario**: Different Slack operations show different fields

```javascript
// post message
{
  "resource": "message",
  "operation": "post"
  // Shows: select (required), channelId or user (required), text (required), attachments, blocks
}

// update message
{
  "resource": "message",
  "operation": "update"
  // Shows: select, channelId (required), ts (required), text (required)
}

// delete message
{
  "resource": "message",
  "operation": "delete"
  // Shows: select, channelId (required), ts (required)
  // Hides: text, attachments, blocks
}

// get message
{
  "resource": "message",
  "operation": "get"
  // Shows: select, channelId (required), ts (required)
  // Hides: text, attachments, blocks
}
```

**Field visibility matrix**:

| Field | post | update | delete | get |
|---|---|---|---|---|
| channelId | Required | Required | Required | Required |
| text | Required | Required | Hidden | Hidden |
| ts | Hidden | Required | Required | Required |
| attachments | Optional | Optional | Hidden | Hidden |
| blocks | Optional | Optional | Hidden | Hidden |

---

## Nested Dependencies

### What Are They?

**Definition**: Dependencies within object properties

**Example**: HTTP Request `specifyBody` controls which body field appears

```javascript
{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  // → jsonBody expects a JSON string
  "jsonBody": "={{ JSON.stringify({ key: 'value' }) }}"
}

{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "keypair",
  // → bodyParameters expects name/value entries
  "bodyParameters": {
    "parameters": [
      {
        "name": "field1",
        "value": "value1"
      }
    ]
  }
}
```

### How to Handle

**Strategy**: Configure parent first, then children

```javascript
// Step 1: Parents
{
  "sendBody": true,
  "contentType": "json"   // Set parents first
}

// Step 2: Children (structure determined by parents)
{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",  // JSON string format
  "jsonBody": "={{ JSON.stringify({ key: 'value' }) }}"
}
```

---

## Auto-Sanitization and Dependencies

### What Auto-Sanitization Fixes

**Operator structure issues** (IF/Switch nodes):

**Example**: singleValue property
```javascript
// You configure (missing singleValue)
{
  "type": "boolean",
  "operation": "isEmpty"
  // Missing singleValue
}

// Auto-sanitization adds it
{
  "type": "boolean",
  "operation": "isEmpty",
  "singleValue": true  // ✅ Added automatically
}
```

### What It Doesn't Fix

**Missing required fields**:
```javascript
// You configure (missing the message target)
{
  "resource": "message",
  "operation": "post",
  "text": "Hello"
  // Missing required fields: select, channelId
}

// Auto-sanitization does NOT add
// You must add them yourself
{
  "resource": "message",
  "operation": "post",
  "select": "channel",    // ← You must add
  "channelId": "C123",    // ← You must add
  "text": "Hello"
}
```

---

## Troubleshooting Dependencies

### Problem 1: "Field X is required but not visible"

**Error**:
```json
{
  "type": "missing_required",
  "property": "jsonBody",
  "message": "jsonBody is required"
}
```

**But you don't see the jsonBody field in configuration!**

**Solution**:
```javascript
// Read the rules off the full schema
const node = get_node({
  nodeType: "nodes-base.httpRequest",
  detail: "full"
});

// Find that jsonBody shows when sendBody=true, contentType=json, specifyBody=json
{
  "method": "POST",
  "sendBody": true,       // ← Now the body fields appear
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify($json) }}"
}
```

### Problem 2: "Field disappears when I change operation"

**Scenario**:
```javascript
// Working configuration
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "C123",
  "text": "Hello"
}

// Change operation
{
  "resource": "message",
  "operation": "update",  // Changed
  "select": "channel",    // Still here
  "channelId": "C123",    // Still here
  "text": "Updated"       // Still here
  // Missing: ts (required for update!)
}
```

**Validation error**: "ts is required"

**Why**: Different operation = different required fields

**Solution**:
```javascript
// Re-read the node for the new operation
get_node({
  nodeType: "nodes-base.slack"
});

// Configure for update operation
{
  "resource": "message",
  "operation": "update",
  "select": "channel",
  "channelId": "C123",
  "ts": "1234567890.123456",  // Required for update
  "text": "Updated"
}
```

### Problem 3: "Validation passes but field doesn't save"

**Scenario**: Field hidden by dependencies after validation

**Example**:
```javascript
// Configure
{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "keypair",  // keypair mode
  "jsonBody": "{...}"        // Hidden in keypair mode - never applies
}

// What actually runs
{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "keypair"
  // jsonBody ignored because specifyBody is not 'json'
}
```

**Solution**: Respect dependencies from the start

```javascript
// Correct approach
get_node({
  nodeType: "nodes-base.httpRequest",
  detail: "full"
});

// See that jsonBody only shows when specifyBody='json'
{
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify($json) }}"
}
```

---

## Advanced Patterns

### Pattern 1: Conditional Required with Fallback

**Example**: Channel ID can be a literal OR an expression

```javascript
// Option 1: Literal
{
  "select": "channel",
  "channelId": "C123"
}

// Option 2: Expression
{
  "select": "channel",
  "channelId": "={{$json.channelId}}"
}

// Validation accepts both
```

### Pattern 2: Mutually Exclusive Fields

**Example**: Slack message target - a channel or a user, never both

```javascript
// Post to a channel
{
  "select": "channel",
  "channelId": "C123"
  // user not shown
}

// OR post to a user
{
  "select": "user",
  "user": "U456"
  // channelId not shown
}

// displayOptions on select ensure only one is required
```

### Pattern 3: Progressive Complexity

**Example**: Simple mode vs advanced mode

```javascript
// Simple mode
{
  "mode": "simple",
  "text": "{{$json.message}}"
  // Advanced fields hidden
}

// Advanced mode
{
  "mode": "advanced",
  "attachments": [...],
  "blocks": [...],
  "metadata": {...}
  // Simple field hidden, advanced fields shown
}
```

---

## Best Practices

### ✅ Do

1. **Check dependencies when stuck**
   ```javascript
   get_node({nodeType: "...", detail: "full"});  // then read displayOptions
   ```

2. **Configure parent properties first**
   ```javascript
   // First: method, resource, operation
   // Then: dependent fields
   ```

3. **Validate after changing operation**
   ```javascript
   // Operation changed → requirements changed
   validate_node({..., mode: "full"});
   ```

4. **Read validation errors for dependency hints**
   ```
   Error: "jsonBody is required"
   → Hint: jsonBody shows when sendBody=true, contentType=json, specifyBody=json
   ```

### ❌ Don't

1. **Don't ignore dependency errors**
   ```javascript
   // Error: "jsonBody not visible" → Check displayOptions
   ```

2. **Don't hardcode all possible fields**
   ```javascript
   // Bad: Adding fields that will be hidden
   ```

3. **Don't assume operations are identical**
   ```javascript
   // Each operation has unique requirements
   ```

---

## Summary

**Key Concepts**:
- `displayOptions` control field visibility
- `show` = field appears when conditions match
- `hide` = field disappears when conditions match
- Multiple conditions = AND logic
- Multiple values = OR logic

**Common Patterns**:
1. Boolean toggle (sendBody → contentType → specifyBody → jsonBody)
2. Resource/operation cascade (different operations → different fields)
3. Type-specific config (string vs boolean operators)
4. Opt-in sections (sendQuery → queryParameters, sendHeaders → headerParameters)

**Troubleshooting**:
- Field required but not visible → Check dependencies
- Field disappears after change → Operation changed requirements
- Field doesn't save → Hidden by dependencies

**Tools**:
- `get_node({nodeType, detail: 'full'})` - Raw displayOptions, which are the dependency rules
- `get_node({nodeType})` - Standard detail: operation requirements
- Validation errors - Hints about dependencies

**Related Files**:
- **[node-configuration.md](node-configuration.md)** - Main configuration guide
- **[node-configuration-operation-patterns.md](node-configuration-operation-patterns.md)** - Common patterns by node type
