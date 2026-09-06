# n8n Node Configuration

Expert guidance for operation-aware node configuration with property dependencies.

---

## Configuration Philosophy

**Progressive disclosure**: Start minimal, add complexity as needed

Configuration best practices:
- get_node at its default `standard` detail is the most used discovery pattern
- Configuration proceeds iteratively, one edit at a time
- Standard-detail configuration succeeds for most nodes

**Key insight**: Most configurations need only standard detail, not the full schema!

---

## Core Concepts

### 1. Operation-Aware Configuration

**Not all fields are always required** - it depends on operation!

**Example**: Slack node
```javascript
// For operation='post'
{
  "resource": "message",
  "operation": "post",
  "select": "channel",        // Required: 'channel' or 'user'
  "channelId": "C123",        // Required for post (resource locator)
  "text": "Hello!"            // Required for post
}

// For operation='update'
{
  "resource": "message",
  "operation": "update",
  "select": "channel",
  "channelId": "C123",
  "ts": "1234567890.123456",  // Required for update (different!)
  "text": "Updated!"          // Required for update
}
```

**Key**: Resource + operation determine which fields are required!

### 2. Property Dependencies

**Fields appear/disappear based on other field values**

**Example**: HTTP Request node
```javascript
// Body fields hidden (sendBody defaults to false)
{
  "method": "POST",
  "url": "https://api.example.com"
  // Valid - a POST with no body is a legal configuration
}

// Body fields visible
{
  "method": "POST",
  "url": "https://api.example.com",
  "sendBody": true,        // Optional boolean, default false
  "contentType": "json",   // Shown when sendBody=true
  "specifyBody": "json",   // Shown when contentType='json'
  "jsonBody": "={{ JSON.stringify($json) }}"  // Shown when specifyBody='json'
}
```

**Mechanism**: displayOptions control field visibility

### 3. Progressive Discovery

**Use the right tool for the right job**:

1. **get_node({nodeType})** - default `detail: 'standard'`, ~1-2K tokens
   - Quick overview
   - Required fields
   - Common options
   - **Use first** - covers most needs

2. **get_node({nodeType, mode: 'search_properties', propertyQuery: 'auth'})**
   - Finds one named field inside a large node
   - Cheaper than pulling the whole schema
   - Cap the result set with `maxPropertyResults`

3. **get_node({nodeType, detail: 'full'})** - full schema, ~3000-8000 tokens
   - Every property, complete documentation
   - Raw `displayOptions` - the dependency rules themselves
   - Use when standard detail is insufficient

---

## Configuration Workflow

### Standard Process

```
1. Identify node type and operation
   ↓
2. Use get_node (standard detail)
   ↓
3. Configure required fields
   ↓
4. Validate configuration
   ↓
5. If dependencies unclear → get_node({detail: 'full'}), read displayOptions
   ↓
6. Add optional fields as needed
   ↓
7. Validate again
   ↓
8. Deploy
```

### Example: Configuring HTTP Request

**Step 1**: Identify what you need
```javascript
// Goal: POST JSON to API
```

**Step 2**: Get the standard view
```javascript
const info = get_node({
  nodeType: "nodes-base.httpRequest"
});

// Returns: method, url, authentication, sendBody, contentType, specifyBody, jsonBody
```

**Step 3**: Minimal config
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/create",
  "authentication": "none"
}
```

**Step 4**: Validate
```javascript
validate_node({
  mode: "full",
  nodeType: "nodes-base.httpRequest",
  config,
  profile: "runtime"
});
// → Valid - a POST with no body is a legal configuration
```

**Step 5**: Opt in to a body
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/create",
  "authentication": "none",
  "sendBody": true
}
```

**Step 6**: Validate again
```javascript
validate_node({..., mode: "full"});
// → sendBody=true reveals contentType and specifyBody
```

**Step 7**: Complete configuration
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/create",
  "authentication": "none",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify({ name: $json.name, email: $json.email }) }}"
}
```

**Step 8**: Final validation
```javascript
validate_node({..., mode: "full"});
// → Valid! ✅
```

---

## Choosing a get_node Detail Level

### Use detail: 'standard' (the default) When:

**✅ Starting configuration** (reliable for most nodes)
```javascript
get_node({
  nodeType: "nodes-base.slack"
});
```

**Returns**:
- Required fields
- Common options
- Basic examples
- Operation list

**Fast**: ~1-2K tokens

### Use detail: 'full' When:

**✅ Standard detail insufficient**
```javascript
get_node({
  detail: "full",
  nodeType: "nodes-base.slack"
});
```

**Returns**:
- Full schema
- All properties
- Raw `displayOptions` on every property
- Advanced options

**Slower**: ~3000-8000 tokens

### Decision Tree

```
┌─────────────────────────────────┐
│ Starting new node config?       │
├─────────────────────────────────┤
│ YES → get_node (standard)       │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Standard has what you need?     │
├─────────────────────────────────┤
│ YES → Configure with standard   │
│ NO  → Continue                  │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Looking for one named field?    │
├─────────────────────────────────┤
│ YES → mode: 'search_properties' │
│ NO  → Continue                  │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Need the dependency rules?      │
├─────────────────────────────────┤
│ YES → detail: 'full', then read │
│       displayOptions            │
└─────────────────────────────────┘
```

---

## Property Dependencies Deep Dive

### displayOptions Mechanism

**Fields have visibility rules**:

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

**Translation**: "jsonBody" field shows when:
- sendBody = true AND
- contentType = json AND
- specifyBody = json

### Common Dependency Patterns

#### Pattern 1: Boolean Toggle

**Example**: HTTP Request sendBody
```javascript
// sendBody controls the visibility of the body section
{
  "sendBody": true   // → contentType and specifyBody appear
}
```

#### Pattern 2: Operation Switch

**Example**: Slack resource/operation
```javascript
// Different operations → different fields
{
  "resource": "message",
  "operation": "post"
  // → Shows: select, channelId or user, text, attachments, etc.
}

{
  "resource": "message",
  "operation": "update"
  // → Shows: select, channelId, ts, text (different fields!)
}
```

#### Pattern 3: Type Selection

**Example**: IF node condition operators
```javascript
{
  "operator": { "type": "string", "operation": "contains" }
  // → Shows: leftValue, rightValue
}

{
  "operator": { "type": "boolean", "operation": "true", "singleValue": true }
  // → Shows: leftValue only
}
```

### Reading Dependencies off the Full Schema

There is no dedicated dependency tool. `detail: 'full'` returns every property with its raw
`displayOptions`, and you read the rules from there.

**Example**:
```javascript
const node = get_node({
  nodeType: "nodes-base.httpRequest",
  detail: "full"
});

// Each property carries its own visibility rule
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

**Use this when**: Validation fails and you don't understand why field is missing/required

---

## Common Node Patterns

### Pattern 1: Resource/Operation Nodes

**Examples**: Slack, Google Sheets, Airtable

**Structure**:
```javascript
{
  "resource": "<entity>",      // What type of thing
  "operation": "<action>",     // What to do with it
  // ... operation-specific fields
}
```

**How to configure**:
1. Choose resource
2. Choose operation
3. Use get_node to see operation-specific requirements
4. Configure required fields

### Pattern 2: HTTP-Based Nodes

**Examples**: HTTP Request, Webhook

**Structure**:
```javascript
{
  "method": "<HTTP_METHOD>",
  "url": "<endpoint>",
  "authentication": "<type>",
  // ... method-specific fields
}
```

**Dependencies**:
- sendBody is an optional boolean defaulting to false, and is not gated by method
- sendBody=true → contentType and specifyBody appear
- specifyBody="json" → jsonBody appears; specifyBody="keypair" → bodyParameters appears
- authentication != "none" → credentials required

### Pattern 3: Database Nodes

**Examples**: Postgres, MySQL, MongoDB

**Structure**:
```javascript
{
  "operation": "<query|insert|update|delete>",
  // ... operation-specific fields
}
```

**Dependencies**:
- operation="executeQuery" → query required
- operation="insert" → table + values required
- operation="update" → table + values + where required

### Pattern 4: Conditional Logic Nodes

**Examples**: IF, Switch, Merge

**Structure** (IF typeVersion 2.3, Switch typeVersion 3.4):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict",
      "version": 2
    },
    "conditions": [
      {
        "leftValue": "...",
        "rightValue": "...",   // Omitted for unary operators
        "operator": {
          "type": "<string|number|boolean|array|object|dateTime>",
          "operation": "<operator>"
        }
      }
    ]
  }
}
```

**Dependencies**:
- Binary operators (equals, contains, etc.) → leftValue + rightValue
- Unary operators (isEmpty, isNotEmpty) → leftValue only, plus `singleValue: true` on the `operator` object
- Switch wraps the same condition object per output under `rules.values[]`, each entry carrying an `outputKey`

---

## Operation-Specific Configuration

### Slack Node Examples

#### Post Message
```javascript
{
  "resource": "message",
  "operation": "post",
  "select": "channel",        // Required: 'channel' or 'user'
  "channelId": "C123",        // Required (resource locator)
  "text": "Hello!",           // Required
  "attachments": [],          // Optional
  "blocks": []                // Optional
}
```

#### Update Message
```javascript
{
  "resource": "message",
  "operation": "update",
  "select": "channel",
  "channelId": "C123",
  "ts": "1234567890.123456",  // Required (different from post!)
  "text": "Updated!"          // Required
}
```

#### Create Channel
```javascript
{
  "resource": "channel",
  "operation": "create",
  "name": "new-channel",      // Required
  "isPrivate": false          // Optional
  // Note: text NOT required for this operation
}
```

### HTTP Request Node Examples

#### GET Request
```javascript
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "sendQuery": true,                    // Optional
  "queryParameters": {                  // Shows when sendQuery=true
    "parameters": [
      {
        "name": "limit",
        "value": "100"
      }
    ]
  }
}
```

#### POST with JSON
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "sendBody": true,                     // Optional - opt in to a body
  "contentType": "json",                // Shown when sendBody=true
  "specifyBody": "json",                // Shown when contentType='json'
  "jsonBody": "={{ JSON.stringify({ name: 'John Doe', email: 'john@example.com' }) }}"
}
```

### IF Node Examples

#### String Comparison (Binary)
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.status}}",
        "rightValue": "active",         // Binary: needs rightValue
        "operator": { "type": "string", "operation": "equals" }
      }
    ]
  }
}
```

#### Empty Check (Unary)
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.email}}",
        // No rightValue - unary operator
        "operator": {
          "type": "string",
          "operation": "isEmpty",
          "singleValue": true           // Auto-added by sanitization
        }
      }
    ]
  }
}
```

---

## Handling Conditional Requirements

### Example: HTTP Request Body

**Scenario**: the body fields appear only sometimes

**Rule**:
```
sendBody is optional and defaults to false - a request with no body is valid.
What sendBody gates:
  - sendBody = true         → contentType, specifyBody appear
  - specifyBody = 'json'    → jsonBody appears
  - specifyBody = 'keypair' → bodyParameters appears
```

**How to discover**:
```javascript
// Option 1: Read validation error
validate_node({..., mode: "full"});

// Option 2: Read the rules off the full schema
get_node({
  nodeType: "nodes-base.httpRequest",
  detail: "full"
});
// jsonBody → displayOptions.show: sendBody=[true], contentType=['json'], specifyBody=['json']

// Option 3: Try minimal config and iterate
// Start without a body, add sendBody only when you need one
```

### Example: IF Node singleValue

**Scenario**: singleValue appears on the `operator` object for unary operators

**Rule**:
```
operator.singleValue should be true when:
  - operation IN (isEmpty, isNotEmpty, true, false)
```

**Good news**: Auto-sanitization fixes this!

**Manual check**:
```javascript
get_node({
  nodeType: "nodes-base.if",
  detail: "full"
});
// Read displayOptions on the condition properties for operator-specific rules
```

---

## Configuration Anti-Patterns

### ❌ Don't: Over-configure Upfront

**Bad**:
```javascript
// Adding every possible field
{
  "method": "GET",
  "url": "...",
  "sendQuery": false,
  "sendHeaders": false,
  "sendBody": false,
  "timeout": 10000,
  "ignoreResponseCode": false,
  // ... 20 more optional fields
}
```

**Good**:
```javascript
// Start minimal
{
  "method": "GET",
  "url": "...",
  "authentication": "none"
}
// Add fields only when needed
```

### ❌ Don't: Skip Validation

**Bad**:
```javascript
// Configure and deploy without validating
const config = {...};
n8n_update_partial_workflow({...});  // YOLO
```

**Good**:
```javascript
// Validate before deploying
const config = {...};
const result = validate_node({..., mode: "full"});
if (result.valid) {
  n8n_update_partial_workflow({...});
}
```

### ❌ Don't: Ignore Operation Context

**Bad**:
```javascript
// Same config for all Slack operations
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "C123",
  "text": "..."
}

// Then switching operation without updating config
{
  "resource": "message",
  "operation": "update",  // Changed
  "select": "channel",
  "channelId": "C123",
  "text": "..."
  // Missing ts - update targets one message, not a channel
}
```

**Good**:
```javascript
// Check requirements when changing operation
get_node({
  nodeType: "nodes-base.slack"
});
// See what the update operation needs (ts, not just channelId)
```

---

## Best Practices

### ✅ Do

1. **Start with get_node at standard detail**
   - Reliable for most nodes
   - Far cheaper than detail: 'full'
   - Sufficient for most needs

2. **Validate iteratively**
   - Configure → Validate → Fix → Repeat
   - Average 2-3 iterations is normal
   - Read validation errors carefully

3. **Use property dependencies when stuck**
   - If field seems missing, check dependencies
   - Understand what controls field visibility
   - get_node({detail: 'full'}) exposes the displayOptions rules

4. **Respect operation context**
   - Different operations = different requirements
   - Always re-read the node when changing operation
   - Don't assume configs are transferable

5. **Trust auto-sanitization**
   - Operator structure fixed automatically
   - Don't manually add/remove singleValue
   - IF/Switch metadata added on save

### ❌ Don't

1. **Jump to detail: 'full' immediately**
   - Try standard detail first
   - Only escalate if needed
   - Full schema is overwhelming

2. **Configure blindly**
   - Always validate before deploying
   - Understand why fields are required
   - Check dependencies for conditional fields

3. **Copy configs without understanding**
   - Different operations need different fields
   - Validate after copying
   - Adjust for new context

4. **Manually fix auto-sanitization issues**
   - Let auto-sanitization handle operator structure
   - Focus on business logic
   - Save and let system fix structure

---

## Detailed References

For comprehensive guides on specific topics:

- **[node-configuration-dependencies.md](node-configuration-dependencies.md)** - Deep dive into property dependencies and displayOptions
- **[node-configuration-operation-patterns.md](node-configuration-operation-patterns.md)** - Common configuration patterns by node type

---

## Summary

**Configuration Strategy**:
1. Start with get_node at standard detail (reliable for most nodes)
2. Configure required fields for operation
3. Validate configuration
4. Check dependencies if stuck
5. Iterate until valid (avg 2-3 cycles)
6. Deploy with confidence

**Key Principles**:
- **Operation-aware**: Different operations = different requirements
- **Progressive disclosure**: Start minimal, add as needed
- **Dependency-aware**: Understand field visibility rules
- **Validation-driven**: Let validation guide configuration

**Related Skills**:
- **[n8n MCP Tools Expert](mcp-tools.md)** - How to use discovery tools correctly
- **[n8n Validation Expert](validation.md)** - Interpret validation errors
- **[n8n Expression Syntax](expressions.md)** - Configure expression fields
- **[n8n Workflow Patterns](workflow-patterns.md)** - Apply patterns with proper configuration
