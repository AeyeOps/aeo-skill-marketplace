# Workflow Management Tools Guide

Complete guide for creating, updating, and managing n8n workflows.

---

## Tool Availability

**⚠️ Requires n8n API**: All tools in this guide need `N8N_API_URL` and `N8N_API_KEY` configured.

If unavailable, use template examples and validation-only workflows.

---

## n8n_create_workflow

**Reliability**: High | **Speed**: 100-500ms

**Use when**: Creating new workflows from scratch

**Syntax**:
```javascript
n8n_create_workflow({
  name: "Webhook to Slack",  // Required
  nodes: [...],              // Required: array of nodes
  connections: {...},        // Required: connections object
  settings: {...}            // Optional: workflow settings
})
```

**Returns**: Created workflow with ID

**Example**:
```javascript
n8n_create_workflow({
  name: "Webhook to Slack",
  nodes: [
    {
      id: "webhook-1",
      name: "Webhook",
      type: "n8n-nodes-base.webhook",  // Full prefix!
      typeVersion: 1,
      position: [250, 300],
      parameters: {
        path: "slack-notify",
        httpMethod: "POST"
      }
    },
    {
      id: "slack-1",
      name: "Slack",
      type: "n8n-nodes-base.slack",
      typeVersion: 1,
      position: [450, 300],
      parameters: {
        resource: "message",
        operation: "post",
        select: "channel",
        channelId: "C0123456789",
        text: "={{$json.body.message}}"
      }
    }
  ],
  connections: {
    "Webhook": {
      "main": [[{node: "Slack", type: "main", index: 0}]]
    }
  }
})
```

**Notes**:
- A created workflow is a **draft**: it exists, it is not running. Publishing is a separate step
- Auto-sanitization runs on creation
- Validate before creating for best results

---

## n8n_update_partial_workflow (MOST USED!)

**Reliability**: Very high | **Speed**: 50-200ms | **Most used tool!**

**Use when**: Making incremental changes to workflows

**Common pattern**: iterative building!

### 21 Operation Types

**Node Operations** (7 types):
1. `addNode` - Add new node
2. `removeNode` - Remove node by ID or name
3. `updateNode` - Update node properties
4. `patchNodeField` - Find-and-replace inside one field of one node
5. `moveNode` - Change position
6. `enableNode` - Enable disabled node
7. `disableNode` - Disable active node

**Connection Operations** (5 types):
8. `addConnection` - Connect nodes
9. `removeConnection` - Remove connection
10. `rewireConnection` - Change target
11. `cleanStaleConnections` - Auto-remove broken connections
12. `replaceConnections` - Replace entire connections object

**Metadata Operations** (5 types):
13. `updateSettings` - Workflow settings
14. `updateName` - Rename workflow
15. `setNodeGroups` - Assign nodes to groups
16. `addTag` - Add tag
17. `removeTag` - Remove tag

**Lifecycle Operations** (4 types):
18. `activateWorkflow` - Publish the workflow
19. `deactivateWorkflow` - Unpublish the workflow
20. `transferWorkflow` - Move to another project
21. `moveToFolder` - Move within a project

### patchNodeField: editing a Code node without resending it

`updateNode` replaces a node's parameters wholesale, which means a one-character fix inside a 200-line Code node
costs a full re-send of the script — and risks clobbering anything you did not carry over. `patchNodeField` takes
a `fieldPath` and a list of find/replace patches instead:

```javascript
{
  type: "patchNodeField",
  name: "Transform Data",
  fieldPath: "parameters.jsCode",   // or parameters.pythonCode
  patches: [
    {find: "$json.name", replace: "$json.body.name", replaceAll: true},
    {find: "const x = \\d+", replace: "const x = 42", regex: true}
  ]
}
```

Reach for it whenever the edit is a line inside a large field rather than a new value for the whole field.

### Smart Parameters (NEW!)

**IF nodes** - Use semantic branch names:
```javascript
{
  type: "addConnection",
  source: "IF",
  target: "True Handler",
  branch: "true"  // Instead of sourceIndex: 0
}

{
  type: "addConnection",
  source: "IF",
  target: "False Handler",
  branch: "false"  // Instead of sourceIndex: 1
}
```

**Switch nodes** - Use semantic case numbers:
```javascript
{
  type: "addConnection",
  source: "Switch",
  target: "Handler A",
  case: 0
}

{
  type: "addConnection",
  source: "Switch",
  target: "Handler B",
  case: 1
}
```

### AI Connection Types (12 types)

**Full support** for AI workflows:

```javascript
// Language Model
{
  type: "addConnection",
  source: "OpenAI Chat Model",
  target: "AI Agent",
  sourceOutput: "ai_languageModel"
}

// Tool
{
  type: "addConnection",
  source: "HTTP Request Tool",
  target: "AI Agent",
  sourceOutput: "ai_tool"
}

// Memory
{
  type: "addConnection",
  source: "Simple Memory",
  target: "AI Agent",
  sourceOutput: "ai_memory"
}

// All 12 non-main connection types:
// - ai_languageModel
// - ai_tool
// - ai_memory
// - ai_outputParser
// - ai_embedding
// - ai_vectorStore
// - ai_document
// - ai_textSplitter
// - ai_agent
// - ai_chain
// - ai_retriever
// - ai_reranker
```

### Example Usage

```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    // Add node
    {
      type: "addNode",
      node: {
        name: "Transform",
        type: "n8n-nodes-base.set",
        position: [400, 300],
        parameters: {}
      }
    },
    // Connect it (smart parameter)
    {
      type: "addConnection",
      source: "IF",
      target: "Transform",
      branch: "true"  // Clear and semantic!
    }
  ]
})
```

### Cleanup & Recovery

**cleanStaleConnections** - Remove broken connections:
```javascript
{
  type: "cleanStaleConnections"
}
```

**Best-effort mode** - Apply what works:
```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [...],
  continueOnError: true  // Don't fail if some operations fail
})
```

---

## n8n_validate_workflow (by ID)

**Reliability**: Very high | **Speed**: Network-dependent

**Use when**: Validating workflow stored in n8n

**Syntax**:
```javascript
n8n_validate_workflow({
  id: "workflow-id",
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true,
    profile: "runtime"
  }
})
```

**Returns**: Same as validate_workflow (from validation guide)

---

## Workflow Lifecycle

**Standard pattern**:
```
1. CREATE
   n8n_create_workflow({...})
   → Returns workflow ID

2. VALIDATE
   n8n_validate_workflow({id})
   → Check for errors

3. EDIT (iterative!)
   n8n_update_partial_workflow({id, operations: [...]})
   → Make changes

4. VALIDATE AGAIN
   n8n_validate_workflow({id})
   → Verify changes

5. PUBLISH (when ready)
   n8n_update_partial_workflow({id, operations: [{type: "activateWorkflow"}]})
   → The draft becomes the published graph and starts running

   Unpublish the same way with {type: "deactivateWorkflow"}.
   The CLI equivalents are `publish:workflow --id=<ID> [--versionId=...]` and `unpublish:workflow`.

6. MONITOR
   n8n_executions({action: "list", workflowId: id})
   n8n_executions({action: "get", id: execution_id})
```

### Draft and published are two different graphs

n8n 2.0 replaced activate/deactivate with a draft/publish model, and it changes what "saved" means. Saving a
workflow no longer changes what runs: you edit a **draft**, and the instance keeps executing the last
**published** version until you publish again. `n8n_get_workflow` exposes both — `mode: 'full'` returns the draft,
`mode: 'active'` returns the published graph — and when a user reports "I changed it but nothing happened", those
two calls are the diagnosis. Publishing is a normal MCP operation (`activateWorkflow`), not a trip to the UI.

---

## Common Patterns

### Pattern 1: Edit → Validate

```javascript
// Edit
n8n_update_partial_workflow({...})
// ↓ (decide what to validate)
// Validate
n8n_validate_workflow({id})
```

### Pattern 2: Validate → Fix

```javascript
// Validate
n8n_validate_workflow({id})
// ↓ (fix the errors)
// Fix
n8n_update_partial_workflow({...})
```

### Pattern 3: Iterative Building

```javascript
update → update → update → ...
```

**This shows**: Workflows are built **iteratively**, not in one shot!

---

## Retrieval Tools

### n8n_get_workflow

One tool, selected by `mode`:

```javascript
n8n_get_workflow({id: "workflow-id", mode: "full"})
// Returns: the complete DRAFT workflow JSON (the default view)

n8n_get_workflow({id: "workflow-id", mode: "active"})
// Returns: the PUBLISHED graph — compare against "full" to see unpublished edits

n8n_get_workflow({id: "workflow-id", mode: "structure"})
// Returns: Nodes + connections only (no parameters)

n8n_get_workflow({id: "workflow-id", mode: "minimal"})
// Returns: ID, name, active, tags only (fast!)
```

`mode` also takes `details` and `filtered`.

### n8n_executions
```javascript
n8n_executions({action: "list", workflowId: "workflow-id"})
n8n_executions({action: "get", id: "execution-id"})
n8n_executions({action: "delete", id: "execution-id"})
```

### n8n_list_workflows
```javascript
n8n_list_workflows({
  active: true,  // Optional: filter by status
  limit: 100,    // Optional: max results
  tags: ["production"]  // Optional: filter by tags
})
```

---

## Best Practices

### ✅ Do

- Build workflows **iteratively**
- Use **smart parameters** (branch, case) for clarity
- Validate **after** significant changes
- Use **atomic mode** (default) for critical updates
- Specify **sourceOutput** for AI connections
- Clean stale connections after node renames/deletions

### ❌ Don't

- Try to build workflows in one shot
- Use sourceIndex when branch/case available
- Skip validation before publishing
- Forget to test workflows after creation
- Ignore auto-sanitization behavior

---

## Summary

**Most Important**:
1. **n8n_update_partial_workflow** is the most-used tool
2. Workflows built **iteratively**
3. Use **smart parameters** (branch="true", case=0) for clarity
4. **AI connections** supported (12 non-main types, wired with sourceOutput)
5. **Auto-sanitization** runs on all operations
6. Validate frequently, then **publish** — a saved draft is not a running workflow

**Related**:
- [mcp-tools-search-guide.md](mcp-tools-search-guide.md) - Find nodes to add
- [mcp-tools-validation-guide.md](mcp-tools-validation-guide.md) - Validate workflows
