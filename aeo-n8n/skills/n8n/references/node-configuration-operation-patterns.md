# Operation Patterns Guide

Common node configuration patterns organized by node type and operation.

---

## Overview

**Purpose**: Quick reference for common node configurations

**Coverage**: Top 20 most-used nodes from 525 available

**Pattern format**:
- Minimal valid configuration
- Common options
- Real-world examples
- Gotchas and tips

---

## HTTP & API Nodes

### HTTP Request (nodes-base.httpRequest)

Most versatile node for HTTP operations

#### GET Request

**Minimal**:
```javascript
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "authentication": "none"
}
```

**With query parameters**:
```javascript
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "sendQuery": true,
  "queryParameters": {
    "parameters": [
      {
        "name": "limit",
        "value": "100"
      },
      {
        "name": "offset",
        "value": "={{$json.offset}}"
      }
    ]
  }
}
```

**With authentication**:
```javascript
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth"
}
```

#### POST with JSON

**Minimal**:
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify({ name: 'John Doe', email: 'john@example.com' }) }}"
}
```

**With name/value pairs instead of raw JSON**:
```javascript
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "keypair",
  "bodyParameters": {
    "parameters": [
      {
        "name": "name",
        "value": "={{$json.name}}"
      },
      {
        "name": "email",
        "value": "={{$json.email}}"
      }
    ]
  }
}
```

**Gotcha**: `sendBody` is optional and defaults to `false` - a POST with no body is valid. Set it when
you want a body, then `contentType` and `specifyBody` decide which field carries it.

#### PUT/PATCH Request

**Pattern**: Same as POST, but method changes
```javascript
{
  "method": "PUT",  // or "PATCH"
  "url": "https://api.example.com/users/123",
  "authentication": "none",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify({ name: 'Updated Name' }) }}"
}
```

#### DELETE Request

**Minimal** (no body):
```javascript
{
  "method": "DELETE",
  "url": "https://api.example.com/users/123",
  "authentication": "none"
}
```

**With body** (some APIs allow):
```javascript
{
  "method": "DELETE",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify({ ids: ['123', '456'] }) }}"
}
```

---

### Webhook (nodes-base.webhook)

Most common trigger - 813 searches!

#### Basic Webhook

**Minimal**:
```javascript
{
  "path": "my-webhook",
  "httpMethod": "POST",
  "responseMode": "onReceived"
}
```

**Gotcha**: Webhook data is under `$json.body`, not `$json`!

```javascript
// ❌ Wrong
{
  "text": "={{$json.email}}"
}

// ✅ Correct
{
  "text": "={{$json.body.email}}"
}
```

#### Webhook with Authentication

**Header auth**:
```javascript
{
  "path": "secure-webhook",
  "httpMethod": "POST",
  "responseMode": "onReceived",
  "authentication": "headerAuth",
  "options": {
    "responseCode": 200,
    "responseData": "{\n  \"success\": true\n}"
  }
}
```

#### Webhook Returning Data

**Custom response**:
```javascript
{
  "path": "my-webhook",
  "httpMethod": "POST",
  "responseMode": "lastNode",  // Return data from last node
  "options": {
    "responseCode": 201,
    "responseHeaders": {
      "entries": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    }
  }
}
```

---

## Communication Nodes

### Slack (nodes-base.slack)

Popular choice for AI agent workflows

#### Post Message

**Minimal**:
```javascript
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "C123",
  "text": "Hello from n8n!"
}
```

**With dynamic content**:
```javascript
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "={{$json.channelId}}",
  "text": "New user: {{$json.name}} ({{$json.email}})"
}
```

**With attachments**:
```javascript
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "C123",
  "text": "Error Alert",
  "attachments": [
    {
      "color": "#ff0000",
      "fields": [
        {
          "title": "Error Type",
          "value": "={{$json.errorType}}"
        },
        {
          "title": "Timestamp",
          "value": "={{$now.toLocaleString()}}"
        }
      ]
    }
  ]
}
```

**Gotcha**: `select` decides the target - `'channel'` takes `channelId` (a resource locator), `'user'`
takes `user`. There is no `channel` parameter.

#### Update Message

**Minimal**:
```javascript
{
  "resource": "message",
  "operation": "update",
  "select": "channel",
  "channelId": "C123",
  "ts": "1234567890.123456",  // From previous message post
  "text": "Updated message content"
}
```

**Note**: `ts` is the message identifier, not an id field

#### Create Channel

**Minimal**:
```javascript
{
  "resource": "channel",
  "operation": "create",
  "name": "new-project-channel",  // Lowercase, no spaces
  "isPrivate": false
}
```

**Gotcha**: Channel name must be lowercase, no spaces, 1-80 chars!

---

### Gmail (nodes-base.gmail)

Popular for email automation

#### Send Email

**Minimal**:
```javascript
{
  "resource": "message",
  "operation": "send",
  "to": "user@example.com",
  "subject": "Hello from n8n",
  "message": "This is the email body"
}
```

**With dynamic content**:
```javascript
{
  "resource": "message",
  "operation": "send",
  "to": "={{$json.email}}",
  "subject": "Order Confirmation #{{$json.orderId}}",
  "message": "Dear {{$json.name}},\n\nYour order has been confirmed.\n\nThank you!",
  "options": {
    "ccList": "admin@example.com",
    "replyTo": "support@example.com"
  }
}
```

#### Get Email

**Minimal**:
```javascript
{
  "resource": "message",
  "operation": "getAll",
  "returnAll": false,
  "limit": 10
}
```

**With filters**:
```javascript
{
  "resource": "message",
  "operation": "getAll",
  "returnAll": false,
  "limit": 50,
  "filters": {
    "q": "is:unread from:important@example.com",
    "labelIds": ["INBOX"]
  }
}
```

---

## Database Nodes

### Postgres (nodes-base.postgres)

Database operations - 456 templates

#### Execute Query

**Minimal** (SELECT):
```javascript
{
  "operation": "executeQuery",
  "query": "SELECT * FROM users WHERE active = true LIMIT 100"
}
```

**With parameters** (SQL injection prevention):
```javascript
{
  "operation": "executeQuery",
  "query": "SELECT * FROM users WHERE email = $1 AND active = $2",
  "additionalFields": {
    "mode": "list",
    "queryParameters": "user@example.com,true"
  }
}
```

**Gotcha**: ALWAYS use parameterized queries for user input!

```javascript
// ❌ BAD - SQL injection risk!
{
  "query": "SELECT * FROM users WHERE email = '{{$json.email}}'"
}

// ✅ GOOD - Parameterized
{
  "query": "SELECT * FROM users WHERE email = $1",
  "additionalFields": {
    "mode": "list",
    "queryParameters": "={{$json.email}}"
  }
}
```

#### Insert

**Minimal**:
```javascript
{
  "operation": "insert",
  "table": "users",
  "columns": "name,email,created_at",
  "additionalFields": {
    "mode": "list",
    "queryParameters": "John Doe,john@example.com,NOW()"
  }
}
```

**With expressions**:
```javascript
{
  "operation": "insert",
  "table": "users",
  "columns": "name,email,metadata",
  "additionalFields": {
    "mode": "list",
    "queryParameters": "={{$json.name}},={{$json.email}},{{JSON.stringify($json)}}"
  }
}
```

#### Update

**Minimal**:
```javascript
{
  "operation": "update",
  "table": "users",
  "updateKey": "id",
  "columns": "name,email",
  "additionalFields": {
    "mode": "list",
    "queryParameters": "={{$json.id}},Updated Name,newemail@example.com"
  }
}
```

---

## Data Transformation Nodes

### Set (nodes-base.set)

Most used transformation!

#### Set Fixed Values

**Minimal**:
```javascript
{
  "mode": "manual",
  "duplicateItem": false,
  "assignments": {
    "assignments": [
      {
        "name": "status",
        "value": "active",
        "type": "string"
      },
      {
        "name": "count",
        "value": 100,
        "type": "number"
      }
    ]
  }
}
```

#### Set from Input Data

**Mapping data**:
```javascript
{
  "mode": "manual",
  "duplicateItem": false,
  "assignments": {
    "assignments": [
      {
        "name": "fullName",
        "value": "={{$json.firstName}} {{$json.lastName}}",
        "type": "string"
      },
      {
        "name": "email",
        "value": "={{$json.email.toLowerCase()}}",
        "type": "string"
      },
      {
        "name": "timestamp",
        "value": "={{$now.toISO()}}",
        "type": "string"
      }
    ]
  }
}
```

**Gotcha**: Use correct `type` for each field!

```javascript
// ❌ Wrong type
{
  "name": "age",
  "value": "25",      // String
  "type": "string"    // Will be string "25"
}

// ✅ Correct type
{
  "name": "age",
  "value": 25,        // Number
  "type": "number"    // Will be number 25
}
```

---

### Code (nodes-base.code)

JavaScript execution

#### Simple Transformation

**Minimal**:
```javascript
{
  "mode": "runOnceForAllItems",
  "jsCode": "return $input.all().map(item => ({\n  json: {\n    name: item.json.name.toUpperCase(),\n    email: item.json.email\n  }\n}));"
}
```

**Per-item processing**:
```javascript
{
  "mode": "runOnceForEachItem",
  "jsCode": "// Process each item\nconst data = $input.item.json;\n\nreturn {\n  json: {\n    fullName: `${data.firstName} ${data.lastName}`,\n    email: data.email.toLowerCase(),\n    timestamp: new Date().toISOString()\n  }\n};"
}
```

**Gotcha**: In Code nodes, use `$input.item.json` or `$input.all()`, NOT `{{...}}`!

```javascript
// ❌ Wrong - expressions don't work in Code nodes
{
  "jsCode": "const name = '={{$json.name}}';"
}

// ✅ Correct - direct access
{
  "jsCode": "const name = $input.item.json.name;"
}
```

---

## Conditional Nodes

### IF (nodes-base.if)

Conditional logic

#### String Comparison

**Equals** (binary):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.status}}",
        "rightValue": "active",
        "operator": { "type": "string", "operation": "equals" }
      }
    ]
  }
}
```

**Contains** (binary):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.email}}",
        "rightValue": "@example.com",
        "operator": { "type": "string", "operation": "contains" }
      }
    ]
  }
}
```

**isEmpty** (unary):
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.email}}",
        // No rightValue - unary operator
        "operator": { "type": "string", "operation": "isEmpty" }
        // operator.singleValue: true added by auto-sanitization
      }
    ]
  }
}
```

**Gotcha**: Unary operators (isEmpty, isNotEmpty) don't need rightValue, and `singleValue` lives on the
`operator` object!

#### Number Comparison

**Greater than**:
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.age}}",
        "rightValue": 18,
        "operator": { "type": "number", "operation": "larger" }
      }
    ]
  }
}
```

#### Boolean Comparison

**Is true**:
```javascript
{
  "conditions": {
    "combinator": "and",
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.isActive}}",
        "operator": { "type": "boolean", "operation": "true", "singleValue": true }
        // Unary - no rightValue
      }
    ]
  }
}
```

#### Multiple Conditions (AND)

**All must match**:
```javascript
{
  "conditions": {
    "combinator": "and",  // AND logic
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.status}}",
        "rightValue": "active",
        "operator": { "type": "string", "operation": "equals" }
      },
      {
        "leftValue": "={{$json.age}}",
        "rightValue": 18,
        "operator": { "type": "number", "operation": "larger" }
      }
    ]
  }
}
```

#### Multiple Conditions (OR)

**Any can match**:
```javascript
{
  "conditions": {
    "combinator": "or",  // OR logic
    "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{$json.status}}",
        "rightValue": "active",
        "operator": { "type": "string", "operation": "equals" }
      },
      {
        "leftValue": "={{$json.status}}",
        "rightValue": "pending",
        "operator": { "type": "string", "operation": "equals" }
      }
    ]
  }
}
```

---

### Switch (nodes-base.switch)

Multi-way routing

#### Basic Switch

**Minimal** (Switch typeVersion 3.4):
```javascript
{
  "mode": "rules",
  "rules": {
    "values": [
      {
        "outputKey": "active",
        "conditions": {
          "combinator": "and",
          "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
          "conditions": [
            {
              "leftValue": "={{$json.status}}",
              "rightValue": "active",
              "operator": { "type": "string", "operation": "equals" }
            }
          ]
        }
      },
      {
        "outputKey": "pending",
        "conditions": {
          "combinator": "and",
          "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
          "conditions": [
            {
              "leftValue": "={{$json.status}}",
              "rightValue": "pending",
              "operator": { "type": "string", "operation": "equals" }
            }
          ]
        }
      }
    ]
  },
  "fallbackOutput": "extra"  // Catch-all for non-matching
}
```

**Gotcha**: Rules live under `rules.values`, not `rules.rules`, and each entry needs an `outputKey`. The
number of rules must match the number of outputs!

---

## AI Nodes

### OpenAI (nodes-langchain.openAi)

AI operations - 234 templates

#### Chat Completion

**Minimal**:
```javascript
{
  "resource": "chat",
  "operation": "complete",
  "messages": {
    "values": [
      {
        "role": "user",
        "content": "={{$json.prompt}}"
      }
    ]
  }
}
```

**With system prompt**:
```javascript
{
  "resource": "chat",
  "operation": "complete",
  "messages": {
    "values": [
      {
        "role": "system",
        "content": "You are a helpful assistant specialized in customer support."
      },
      {
        "role": "user",
        "content": "={{$json.userMessage}}"
      }
    ]
  },
  "options": {
    "temperature": 0.7,
    "maxTokens": 500
  }
}
```

---

## Schedule Nodes

### Schedule Trigger (nodes-base.scheduleTrigger)

Time-based workflows

#### Daily at Specific Time

**Minimal**:
```javascript
{
  "rule": {
    "interval": [
      {
        "field": "hours",
        "hoursInterval": 24
      }
    ],
    "hour": 9,
    "minute": 0,
    "timezone": "America/New_York"
  }
}
```

**Gotcha**: Always set timezone explicitly!

```javascript
// ❌ Bad - uses server timezone
{
  "rule": {
    "interval": [...]
  }
}

// ✅ Good - explicit timezone
{
  "rule": {
    "interval": [...],
    "timezone": "America/New_York"
  }
}
```

#### Every N Minutes

**Minimal**:
```javascript
{
  "rule": {
    "interval": [
      {
        "field": "minutes",
        "minutesInterval": 15
      }
    ]
  }
}
```

#### Cron Expression

**Advanced scheduling**:
```javascript
{
  "mode": "cron",
  "cronExpression": "0 */2 * * *",  // Every 2 hours
  "timezone": "America/New_York"
}
```

---

## Summary

**Key Patterns by Category**:

| Category | Most Common | Key Gotcha |
|---|---|---|
| HTTP/API | GET, POST JSON | sendBody is optional - set it to opt in to a body |
| Webhooks | POST receiver | Data under $json.body |
| Communication | Slack post | select + channelId, never `channel` |
| Database | SELECT with params | Use parameterized queries |
| Transform | Set assignments | Correct type per field |
| Conditional | IF string equals | Unary vs binary operators, singleValue on `operator` |
| AI | OpenAI chat | System + user messages |
| Schedule | Daily at time | Set timezone explicitly |

**Configuration Approach**:
1. Use patterns as starting point
2. Adapt to your use case
3. Validate configuration
4. Iterate based on errors
5. Deploy when valid

**Related Files**:
- **[node-configuration.md](node-configuration.md)** - Configuration workflow and philosophy
- **[node-configuration-dependencies.md](node-configuration-dependencies.md)** - Property dependency rules
