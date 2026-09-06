# n8n Expression Syntax

Expert guide for writing correct n8n expressions in workflows.

---

## Expression Format

All dynamic content in n8n uses **double curly braces**:

```
{{expression}}
```

**Examples**:
```
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$('HTTP Request').json.data}}
❌ $json.email  (no braces - treated as literal text)
❌ {$json.email}  (single braces - invalid)
```

---

## Core Variables

### $json - Current Node Output

Access data from the current node:

```javascript
{{$json.fieldName}}
{{$json['field with spaces']}}
{{$json.nested.property}}
{{$json.items[0].name}}
```

### $() - Reference Other Nodes

`$('Node Name')` is the accessor for another node's data:

```javascript
{{$('Node Name').json.fieldName}}
{{$('HTTP Request').json.data}}
{{$('Webhook').json.body.email}}
```

**Important**:
- Node names **must** be in quotes
- Node names are **case-sensitive**
- Must match exact node name from workflow

The returned proxy carries more than `.json`:

| Accessor | Returns |
|----------|---------|
| `$('X').json` | The linked item's JSON, following item linking back through the run |
| `$('X').all()` | Every item that node output |
| `$('X').first()` / `$('X').last()` | The first or last output item |
| `$('X').item` | The item on this branch that produced the current item |
| `$('X').itemMatching(i)` | The output item paired with input item `i` |
| `$('X').isExecuted` | Whether that node ran in this execution — the clean guard for optional branches |
| `$('X').params` | That node's own parameter values |

The older `{{$node["X"].json}}` form still resolves at runtime, so existing workflows keep working, but it has
been removed from the n8n documentation and the expression editor does not offer it in autocomplete. Write new
expressions with `$('X')`, and read `$node[...]` as a sign the workflow predates the current syntax.

### $now - Current Timestamp

Access current date/time:

```javascript
{{$now}}
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.toFormat('HH:mm:ss')}}
{{$now.plus({days: 7})}}
```

### $env - Environment Variables

Access environment variables:

```javascript
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
```

### The rest of the root set

`$json`, `$()`, `$now` and `$env` cover most expressions, but the documented root namespace is wider, and reaching
for the right one beats reconstructing it by hand:

`$()`, `$binary`, `$env`, `$execution`, `$fromAI()`, `$if()`, `$ifEmpty()`, `$input`, `$itemIndex`, `$jmespath()`,
`$json`, `$max()`, `$min()`, `$nodeVersion`, `$now`, `$pageCount`, `$parameter`, `$prevNode`, `$request`,
`$response`, `$runIndex`, `$secrets`, `$today`, `$vars`, `$workflow`.

Two of these have context restrictions worth knowing before you use them: `$secrets` resolves **only** in
credential fields, and the transformation helpers (`$if()`, `$ifEmpty()`, `$jmespath()`, `$min()`, `$max()`) exist
in the expression editor but **not** inside a Code node.

---

## 🚨 CRITICAL: Webhook Data Structure

**Most Common Mistake**: Webhook data is **NOT** at the root!

### Webhook Node Output Structure

```javascript
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // ⚠️ USER DATA IS HERE!
    "name": "John",
    "email": "john@example.com",
    "message": "Hello"
  }
}
```

### Correct Webhook Data Access

```javascript
❌ WRONG: {{$json.name}}
❌ WRONG: {{$json.email}}

✅ CORRECT: {{$json.body.name}}
✅ CORRECT: {{$json.body.email}}
✅ CORRECT: {{$json.body.message}}
```

**Why**: Webhook node wraps incoming data under `.body` property to preserve headers, params, and query parameters.

---

## Common Patterns

### Access Nested Fields

```javascript
// Simple nesting
{{$json.user.email}}

// Array access
{{$json.data[0].name}}
{{$json.items[0].id}}

// Bracket notation for spaces
{{$json['field name']}}
{{$json['user data']['first name']}}
```

### Reference Other Nodes

```javascript
// Node without spaces
{{$('Set').json.value}}

// Node with spaces (common!)
{{$('HTTP Request').json.data}}
{{$('Respond to Webhook').json.message}}

// Webhook node
{{$('Webhook').json.body.email}}
```

### Combine Variables

```javascript
// Concatenation (automatic)
Hello {{$json.body.name}}!

// In URLs
https://api.example.com/users/{{$json.body.user_id}}

// In object properties
{
  "name": "={{$json.body.name}}",
  "email": "={{$json.body.email}}"
}
```

---

## When NOT to Use Expressions

### ❌ Code Nodes

Code nodes use **direct JavaScript access**, NOT expressions!

```javascript
// ❌ WRONG in Code node
const email = '={{$json.email}}';
const name = '{{$json.body.name}}';

// ✅ CORRECT in Code node
const email = $json.email;
const name = $json.body.name;

// Or using Code node API
const email = $input.item.json.email;
const allItems = $input.all();
```

### ❌ Webhook Paths

A webhook path is resolved when the route is registered, not per execution, so a runtime expression in it never
evaluates:

```javascript
// ❌ WRONG - nothing evaluates this at request time
path: "{{$json.user_id}}/webhook"

// ✅ CORRECT
path: "user-webhook"
```

The Path field is not limited to a fixed string, though. It accepts **route parameters**, which is usually what
someone reaching for an expression actually wanted:

```javascript
path: "user/:userId"              // matches /user/42
path: ":tenant/webhook"           // leading parameter
path: ":tenant/order/:orderId"    // several parameters
```

Matched values arrive at runtime under `$json.params`, so `/user/42` gives you `{{$json.params.userId}}`.

### ⚠️ Credential Fields — expressions work, but use them for secrets

Credential fields **do** accept expressions. They are in fact the only place `$secrets` resolves at all: a value
pulled from an external secret store is unavailable in every other field that supports expressions.

```javascript
// ✅ The intended use — select "Expression" on the credential field
apiKey: "={{ $secrets.vaultName.apiKeyName }}"

// ⚠️ Works, but you are now managing a credential by hand in an env var
apiKey: "={{$env.API_KEY}}"

// ✅ Simplest and safest when there is no external store
Store the key in an n8n credential and select it on the node
```

The rule is about where the secret lives, not about expression syntax: prefer an n8n credential, use
`$secrets.<store>.<name>` when an external secret store is configured, and treat `$env` in a credential field as a
fallback you have chosen deliberately.

---

## Validation Rules

### 1. Always Use {{}}

Expressions **must** be wrapped in double curly braces.

```javascript
❌ $json.field
✅ {{$json.field}}
```

### 2. Use Quotes for Spaces

Field or node names with spaces require **bracket notation**:

```javascript
❌ {{$json.field name}}
✅ {{$json['field name']}}

❌ {{$(HTTP Request).json}}
✅ {{$('HTTP Request').json}}
```

### 3. Match Exact Node Names

Node references are **case-sensitive**:

```javascript
❌ {{$('http request').json}}  // lowercase
❌ {{$('Http Request').json}}  // wrong case
✅ {{$('HTTP Request').json}}  // exact match
```

### 4. No Nested {{}}

Don't double-wrap expressions:

```javascript
❌ {{{$json.field}}}
✅ {{$json.field}}
```

---

## Common Mistakes

For complete error catalog with fixes, see [expressions-common-mistakes.md](expressions-common-mistakes.md)

### Quick Fixes

| Mistake | Fix |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$(HTTP Request)}}` | `{{$('HTTP Request')}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `'={{$json.email}}'` (Code node) | `$json.email` |

---

## Working Examples

For real workflow examples, see [expressions-examples.md](expressions-examples.md)

### Example 1: Webhook to Slack

**Webhook receives**:
```json
{
  "body": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  }
}
```

**In Slack node text field**:
```
New form submission!

Name: {{$json.body.name}}
Email: {{$json.body.email}}
Message: {{$json.body.message}}
```

### Example 2: HTTP Request to Email

**HTTP Request returns**:
```json
{
  "data": {
    "items": [
      {"name": "Product 1", "price": 29.99}
    ]
  }
}
```

**In Email node** (reference HTTP Request):
```
Product: {{$('HTTP Request').json.data.items[0].name}}
Price: ${{$('HTTP Request').json.data.items[0].price}}
```

### Example 3: Format Timestamp

```javascript
// Current date
{{$now.toFormat('yyyy-MM-dd')}}
// Result: 2025-10-20

// Time
{{$now.toFormat('HH:mm:ss')}}
// Result: 14:30:45

// Full datetime
{{$now.toFormat('yyyy-MM-dd HH:mm')}}
// Result: 2025-10-20 14:30
```

---

## Data Type Handling

### Arrays

```javascript
// First item
{{$json.users[0].email}}

// Array length
{{$json.users.length}}

// Last item
{{$json.users[$json.users.length - 1].name}}
```

### Objects

```javascript
// Dot notation (no spaces)
{{$json.user.email}}

// Bracket notation (with spaces or dynamic)
{{$json['user data'].email}}
```

### Strings

```javascript
// Concatenation (automatic)
Hello {{$json.name}}!

// String methods
{{$json.email.toLowerCase()}}
{{$json.name.toUpperCase()}}
```

### Numbers

```javascript
// Direct use
{{$json.price}}

// Math operations
{{$json.price * 1.1}}  // Add 10%
{{$json.quantity + 5}}
```

---

## Advanced Patterns

### Conditional Content

```javascript
// Ternary operator
{{$json.status === 'active' ? 'Active User' : 'Inactive User'}}

// Default values
{{$json.email || 'no-email@example.com'}}
```

### Date Manipulation

```javascript
// Add days
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}

// Subtract hours
{{$now.minus({hours: 24}).toISO()}}

// Set specific date
{{DateTime.fromISO('2025-12-25').toFormat('MMMM dd, yyyy')}}
```

### String Manipulation

```javascript
// Substring
{{$json.email.substring(0, 5)}}

// Replace
{{$json.message.replace('old', 'new')}}

// Split and join
{{$json.tags.split(',').join(', ')}}
```

---

## Debugging Expressions

### Test in Expression Editor

1. Click field with expression
2. Open expression editor (click "fx" icon)
3. See live preview of result
4. Check for errors highlighted in red

### Common Error Messages

**"Cannot read property 'X' of undefined"**
→ Parent object doesn't exist
→ Check your data path

**"X is not a function"**
→ Trying to call method on non-function
→ Check variable type

**Expression shows as literal text**
→ Missing {{ }}
→ Add curly braces

---

## Expression Helpers

### Available Methods

**String**:
- `.toLowerCase()`, `.toUpperCase()`
- `.trim()`, `.replace()`, `.substring()`
- `.split()`, `.includes()`

**Array**:
- `.length`, `.map()`, `.filter()`
- `.find()`, `.join()`, `.slice()`

**DateTime** (Luxon):
- `.toFormat()`, `.toISO()`, `.toLocal()`
- `.plus()`, `.minus()`, `.set()`

**Number**:
- `.toFixed()`, `.toString()`
- Math operations: `+`, `-`, `*`, `/`, `%`

---

## Best Practices

### ✅ Do

- Always use {{ }} for dynamic content
- Use bracket notation for field names with spaces
- Reference webhook data from `.body`
- Use `$('Node Name')` for data from other nodes
- Test expressions in expression editor

### ❌ Don't

- Don't use expressions in Code nodes
- Don't forget quotes around node names with spaces
- Don't double-wrap with extra {{ }}
- Don't assume webhook data is at root (it's under .body!)
- Don't use expressions in webhook paths or credentials

---

## Related Skills

- **[n8n MCP Tools Expert](mcp-tools.md)**: Learn how to validate expressions using MCP tools
- **[n8n Workflow Patterns](workflow-patterns.md)**: See expressions in real workflow examples
- **[n8n Node Configuration](node-configuration.md)**: Understand when expressions are needed

---

## Summary

**Essential Rules**:
1. Wrap expressions in {{ }}
2. Webhook data is under `.body`
3. No {{ }} in Code nodes
4. Quote node names with spaces
5. Node names are case-sensitive

**Most Common Mistakes**:
- Missing {{ }} → Add braces
- `{{$json.name}}` in webhooks → Use `{{$json.body.name}}`
- `{{$json.email}}` in Code → Use `$json.email`
- Legacy node reference from an older workflow → Use `{{$('HTTP Request')}}`

For more details, see:
- [expressions-common-mistakes.md](expressions-common-mistakes.md) - Complete error catalog
- [expressions-examples.md](expressions-examples.md) - Real workflow examples

---

**Need Help?** Reference the n8n expression documentation or use n8n-mcp validation tools to check your expressions.
