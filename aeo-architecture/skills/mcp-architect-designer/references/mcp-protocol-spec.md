# Model Context Protocol (MCP) Specification Reference

## Overview

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It uses JSON-RPC 2.0 for all communication and supports multiple transport mechanisms.

## Core Protocol: JSON-RPC 2.0

All MCP communication uses JSON-RPC 2.0 message format.

### Message Types

#### 1. Request Message
```json
{
  "jsonrpc": "2.0",
  "id": "string | number",
  "method": "string",
  "params": {
    // Optional structured parameters
  }
}
```

**Requirements:**
- `id` MUST be unique within the session
- `id` MUST NOT be null
- `id` MUST NOT be reused

#### 2. Response Message
```json
{
  "jsonrpc": "2.0",
  "id": "string | number",
  "result": {
    // Success result
  }
}
```

**Or error response:**
```json
{
  "jsonrpc": "2.0",
  "id": "string | number",
  "error": {
    "code": -32000,
    "message": "Error description",
    "data": {}  // Optional additional data
  }
}
```

**Requirements:**
- Response MUST include same `id` as request
- Response MUST include either `result` OR `error`, not both

#### 3. Notification Message
```json
{
  "jsonrpc": "2.0",
  "method": "string",
  "params": {
    // Optional parameters
  }
}
```

**Requirements:**
- Notifications MUST NOT include an `id`
- Notifications do not expect a response

## Standard Error Codes

| Code | Meaning | Usage |
|------|---------|-------|
| -32700 | Parse error | Invalid JSON received |
| -32600 | Invalid Request | JSON-RPC structure invalid |
| -32601 | Method not found | Method doesn't exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal server error |
| -32002 | Resource not found | MCP-specific: resource not found |

## Connection Lifecycle

### 1. Initialize Phase

**Client → Server:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ClientName",
      "version": "1.0.0"
    }
  }
}
```

**Server → Client:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "subscribe": true }
    },
    "serverInfo": {
      "name": "ServerName",
      "version": "1.0.0"
    }
  }
}
```

### 2. Initialized Notification

**Client → Server:**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

**Critical:** Server MUST NOT respond to this notification.

### 3. Normal Operation

After initialization, clients and servers exchange:
- Tool calls (`tools/call`)
- Resource reads (`resources/read`)
- Prompt requests (`prompts/get`)
- Notifications (various)

### 4. Shutdown

Graceful shutdown via connection close. No special protocol required.

## Core Capabilities

### Tools

Tools are functions that LLMs can invoke.

**List Tools:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {
    "cursor": "optional-pagination-cursor"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "tool_name",
        "description": "What this tool does",
        "inputSchema": {
          "type": "object",
          "properties": {
            "param1": { "type": "string" }
          },
          "required": ["param1"]
        }
      }
    ],
    "nextCursor": null
  }
}
```

**Call Tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value"
    }
  }
}
```

**Tool Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool result as text"
      }
    ],
    "isError": false
  }
}
```

### Resources

Resources are data that can be read by LLMs.

**List Resources:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {
    "cursor": null
  }
}
```

**Read Resource:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///path/to/resource"
  }
}
```

**Subscribe to Resource Updates:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "resources/subscribe",
  "params": {
    "uri": "file:///path/to/resource"
  }
}
```

**Update Notification (Server → Client):**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "uri": "file:///path/to/resource"
  }
}
```

### Prompts

Prompts are templates for LLM interactions.

**List Prompts:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/list"
}
```

**Get Prompt:**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "prompts/get",
  "params": {
    "name": "prompt_name",
    "arguments": {
      "arg1": "value"
    }
  }
}
```

## Protocol Versions

Current versions:
- `2025-06-18` (latest)
- `2025-03-26`
- `2024-11-05`

**Version Negotiation:**
- Client specifies supported version in `initialize`
- Server responds with supported version
- If versions incompatible, return error -32602

**Version Mismatch Error:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2025-03-26"],
      "requested": "1.0.0"
    }
  }
}
```

## Best Practices

### Tool Design

1. **Granularity:** Design tools at the right level
   - Too coarse: `do_everything()`
   - Too fine: `add_character_at_position()`
   - Just right: `search_documents(query)`

2. **Input Schema:** Always provide JSON Schema
   ```json
   {
     "type": "object",
     "properties": {
       "query": {
         "type": "string",
         "description": "Search query text"
       },
       "limit": {
         "type": "integer",
         "description": "Max results",
         "default": 10
       }
     },
     "required": ["query"]
   }
   ```

3. **Error Handling:** Use `isError: true` for business logic errors
   ```json
   {
     "result": {
       "content": [{"type": "text", "text": "Not found"}],
       "isError": true
     }
   }
   ```

4. **Descriptions:** Write clear, actionable descriptions
   - Bad: "Gets data"
   - Good: "Search documents by text query, returns top N matches with similarity scores"

### Resource Design

1. **URI Templates:** Use for dynamic resources
   ```
   file://documents/{doc_id}
   data://{category}/{item_id}
   ```

2. **MIME Types:** Always specify for binary content
   ```json
   {
     "uri": "image://photo/123",
     "mimeType": "image/png"
   }
   ```

3. **Subscriptions:** Enable for frequently changing resources

### Error Handling

1. **Protocol Errors:** Use standard JSON-RPC codes
2. **Business Logic Errors:** Use `isError: true` in result
3. **Detailed Messages:** Include actionable error information
4. **Data Field:** Add context for debugging

```json
{
  "error": {
    "code": -32002,
    "message": "Resource not found",
    "data": {
      "uri": "file:///missing.txt",
      "available": ["file:///doc1.txt", "file:///doc2.txt"]
    }
  }
}
```

## Security Considerations

1. **Authentication:** Implement at transport layer (OAuth 2.1, JWT)
2. **Authorization:** Check permissions before executing tools
3. **Input Validation:** Validate all tool arguments
4. **Origin Validation:** For HTTP transports, validate Origin header
5. **Rate Limiting:** Implement per-client rate limits
6. **Audit Logging:** Log all tool calls with user context

## Testing Checklist

- [ ] Initialize handshake completes successfully
- [ ] Protocol version negotiation works
- [ ] Tool discovery returns all tools with schemas
- [ ] Tool calls execute and return proper results
- [ ] Tool errors return `isError: true`
- [ ] Invalid methods return -32601
- [ ] Invalid params return -32602
- [ ] Resource subscription sends update notifications
- [ ] Concurrent requests handled correctly
- [ ] Large payloads handled without truncation
- [ ] Connection interruption recovery works (if supported)
