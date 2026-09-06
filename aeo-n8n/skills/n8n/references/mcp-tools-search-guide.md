# Node Discovery Tools Guide

Complete guide for finding and understanding n8n nodes.

---

## search_nodes (START HERE!)

**Reliability**: Very high | **Speed**: <20ms

**Use when**: You know what you're looking for (keyword, service, use case)

**Syntax**:
```javascript
search_nodes({
  query: "slack",      // Required: search keywords
  mode: "OR",          // Optional: OR (default), AND, FUZZY
  limit: 20,          // Optional: max results (default 20, max 100)
  source: "all",      // Optional: all (default), core, community, verified
  includeExamples: true,   // Optional: real configs pulled from templates
  includeOperations: true  // Optional: operations list per result
})
```

**Returns**:
```javascript
{
  "query": "slack",
  "results": [
    {
      "nodeType": "nodes-base.slack",                    // For search/validate tools
      "workflowNodeType": "n8n-nodes-base.slack",       // For workflow tools
      "displayName": "Slack",
      "description": "Consume Slack API",
      "category": "output",
      "relevance": "high"
    }
  ]
}
```

**Tips**:
- Common searches: webhook, http, database, email, slack, google, ai
- OR mode (default): matches any word
- AND mode: requires all words
- FUZZY mode: typo-tolerant (finds "slak" → Slack)
- `source` is the only corpus filter there is: 832 core nodes, 1,859 community nodes, 1,539 of them verified.
  There is no category or package filter — narrow with the query text instead.

---

## get_node, detail: "standard" (RECOMMENDED!)

**Reliability**: High | **Speed**: <10ms | **Size**: ~5KB

**Use when**: You've found the node and need configuration details. `standard` is the default detail level, so
you get it by naming no detail at all.

**Syntax**:
```javascript
get_node({
  nodeType: "nodes-base.slack",      // Required: SHORT prefix format
  includeExamples: true              // Optional: get real template configs
})
```

**Returns**:
- Available operations and resources
- Essential properties (10-20 most common)
- Metadata (isAITool, isTrigger, hasCredentials)
- Real examples from templates (if includeExamples: true)

**Why use this**:
- 5KB vs 100KB+ (`detail: "full"`)
- Far more reliable than `detail: "full"`
- <10ms vs slower
- Focused data (no information overload)

---

## get_node, detail: "full" (USE SPARINGLY!)

**Reliability**: Low ⚠️ | **Size**: 100KB+

**Use when**:
- Debugging complex configuration
- Need complete property schema
- Exploring advanced features

**Syntax**:
```javascript
get_node({
  detail: "full",
  nodeType: "nodes-base.httpRequest"
})
```

**Warning**: Prone to failure! Stay on the default `standard` detail for most cases.

**Cheaper depths on the same tool**:
1. `get_node({nodeType})` - operations list at the default `standard` detail
2. `get_node({nodeType, mode: "docs"})` - readable docs
3. `get_node({nodeType, mode: "search_properties", propertyQuery: "auth"})` - one specific property

It is also the only way left to inspect property dependencies: `detail: "full"` returns each property's raw
`displayOptions`, and those `show` / `hide` rules are the dependency tree.

---

## search_nodes, source filter (BROWSE A CORPUS SLICE)

**Reliability**: Very high | **Speed**: <20ms

**Use when**: Exploring what exists rather than chasing one known node

**Syntax**:
```javascript
search_nodes({
  query: "trigger",     // Required: there is no listing without a query
  source: "core",       // Optional: all (default), core, community, verified
  limit: 200            // Optional: default 20, max 100 per page
})
```

**Sources**:
- `core` - the nodes that ship with n8n (832)
- `community` - installed community nodes (1,859, of which 1,539 verified)
- `verified` - the verified subset only
- `all` - the default, everything indexed

There is no category or package filter. Category words still work as query text — searching `trigger`,
`transform` or `ai` gets you most of the way, and each result carries its own `category` field.

---

## get_node, mode: "search_properties" (FIND SPECIFIC FIELDS)

**Use when**: Looking for specific property in a node

**Syntax**:
```javascript
get_node({
  nodeType: "nodes-base.httpRequest",
  mode: "search_properties",
  propertyQuery: "auth",      // Find authentication properties
  maxPropertyResults: 20      // Optional: cap the matches returned
})
```

**Returns**: Property paths and descriptions matching query

**Common searches**: auth, header, body, json, url, method

---

## get_node, mode: "docs" (READABLE DOCS)

**Coverage**: Most nodes

**Use when**: Need human-readable documentation with examples

**Syntax**:
```javascript
get_node({
  mode: "docs",
  nodeType: "nodes-base.slack"
})
```

**Returns**: Formatted docs with:
- Usage examples
- Authentication guide
- Common patterns
- Best practices

**Note**: Better than raw schema for learning!

---

## Common Workflow: Finding & Configuring

```
Step 1: Search
search_nodes({query: "slack"})
→ Returns: nodes-base.slack

Step 2: Get Operations
get_node({
  nodeType: "nodes-base.slack",
  includeExamples: true
})
→ Returns: operations list + example configs

Step 3: Validate Config
validate_node({
  mode: "full",
  nodeType: "nodes-base.slack",
  config: {resource: "channel", operation: "create"},
  profile: "runtime"
})
→ Returns: validation result

Step 4: Use in Workflow
(Configuration ready!)
```

**Most common pattern**: search → get_node → validate_node

---

## Quick Comparison

| Tool | When to Use | Reliability | Speed | Size |
|------|-------------|-------------|-------|------|
| search_nodes | Find by keyword | Very high | <20ms | Small |
| search_nodes (source filter) | Browse a corpus slice | Very high | <20ms | Small |
| get_node (detail: "standard") | Get config | High | <10ms | 5KB |
| get_node (detail: "full") | Full schema | Low ⚠️ | Slow | 100KB+ |
| get_node (mode: "docs") | Learn usage | N/A | Fast | Medium |

**Best Practice**: search → get_node → validate

---

## nodeType Format (CRITICAL!)

**Search/Validate Tools** (SHORT prefix):
```javascript
"nodes-base.slack"
"nodes-base.httpRequest"
"nodes-langchain.agent"
```

**Workflow Tools** (FULL prefix):
```javascript
"n8n-nodes-base.slack"
"n8n-nodes-base.httpRequest"
"@n8n/n8n-nodes-langchain.agent"
```

**Conversion**: search_nodes returns BOTH formats:
```javascript
{
  "nodeType": "nodes-base.slack",          // Use with get_node / validate_node
  "workflowNodeType": "n8n-nodes-base.slack"  // Use with create_workflow
}
```

---

## Related

- [mcp-tools-validation-guide.md](mcp-tools-validation-guide.md) - Validate node configs
- [mcp-tools-workflow-guide.md](mcp-tools-workflow-guide.md) - Use nodes in workflows
