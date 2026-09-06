# n8n MCP Tools Expert

Master guide for using n8n-mcp MCP server tools to build workflows.

---

## Tool Categories

n8n-mcp provides **28 tools**: **7 core tools** that work with no n8n instance, and **21 n8n management
tools** that need an n8n API connection.

**The 7 core tools**: `tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `validate_workflow`,
`search_templates`, `get_template`.

They cover:

1. **Node Discovery** → [mcp-tools-search-guide.md](mcp-tools-search-guide.md)
2. **Configuration Validation** → [mcp-tools-validation-guide.md](mcp-tools-validation-guide.md)
3. **Workflow Management** → [mcp-tools-workflow-guide.md](mcp-tools-workflow-guide.md)
4. **Template Library** - Search and access thousands of real workflows
5. **Documentation** - Get tool and node documentation

### One tool per job, selected by a mode argument

n8n-mcp collapsed its single-purpose tools into a handful that take a mode argument, so a call written against an
earlier generation now fails immediately with "unknown tool". Five discovery tools became `get_node`, selected by
`detail` (`standard` by default, `full` for the complete schema) and `mode` (`docs`, `search_properties`). Two
validators became `validate_node`, selected by `mode` (`minimal`, `full`). Three template tools became
`search_templates`, selected by `searchMode` (`keyword`, `by_nodes`, `by_task`, `by_metadata`, `patterns`). Three
workflow getters became `n8n_get_workflow`, selected by `mode`. Two execution tools became `n8n_executions`,
selected by `action`. Node-property dependency inspection has no dedicated tool at all any more — read the raw
`displayOptions` out of `get_node({nodeType, detail: 'full'})` instead.

### Capability areas beyond node discovery

The 21 management tools reach further than workflow CRUD, and these are easy to miss:
`n8n_manage_credentials`, `n8n_manage_folders`, `n8n_manage_datatable`, `n8n_manage_agents`, `n8n_audit_instance`,
`n8n_workflow_versions` (local snapshots plus n8n-native history with rollback), `n8n_deploy_template`,
`n8n_evaluations`, `n8n_explore_node_resources`, `n8n_list_catalog`, `n8n_test_workflow`.

`n8n_explore_node_resources` is the one worth learning first: it resolves real resource identifiers — a Slack
channel ID, a Sheets tab — through a live credential, instead of leaving a placeholder in the configuration for
someone to discover at runtime. Several of these tools need a second secret, `N8N_MCP_ACCESS_TOKEN`, which is
distinct from `N8N_API_KEY`.

---

## Quick Reference

### Most Used Tools

| Tool | Use When | Reliability | Speed |
|------|----------|-------------|-------|
| `search_nodes` | Finding nodes by keyword | Very high | <20ms |
| `get_node` | Understanding node operations | High | <10ms |
| `validate_node` | Checking configurations | Varies | <100ms |
| `n8n_create_workflow` | Creating workflows | High | 100-500ms |
| `n8n_update_partial_workflow` | Editing workflows (MOST USED!) | Very high | 50-200ms |
| `validate_workflow` | Checking complete workflow | High | 100-500ms |

---

## Tool Selection Guide

### Finding the Right Node

**Workflow**:
```
1. search_nodes({query: "keyword"})
2. get_node({nodeType: "nodes-base.name"})
3. [Optional] get_node({nodeType: "nodes-base.name", mode: "docs"})
```

**Example**:
```javascript
// Step 1: Search
search_nodes({query: "slack"})
// Returns: nodes-base.slack

// Step 2: Get details
get_node({nodeType: "nodes-base.slack"})
// Returns: operations, properties, examples
```

**Common pattern**: search → get_node

### Validating Configuration

**Workflow**:
```
1. validate_node({nodeType, config: {}, mode: "minimal"}) - Check required fields
2. validate_node({nodeType, config, mode: "full", profile: "runtime"}) - Full validation
3. [Repeat] Fix errors, validate again
```

**Common pattern**: validate → fix → validate

### Managing Workflows

**Workflow**:
```
1. n8n_create_workflow({name, nodes, connections})
2. n8n_validate_workflow({id})
3. n8n_update_partial_workflow({id, operations: [...]})
4. n8n_validate_workflow({id}) again
```

**Common pattern**: iterative updates

---

## Critical: nodeType Formats

**Two different formats** for different tools!

### Format 1: Search/Validate Tools
```javascript
// Use SHORT prefix
"nodes-base.slack"
"nodes-base.httpRequest"
"nodes-base.webhook"
"nodes-langchain.agent"
```

**Tools that use this**:
- search_nodes (returns this format)
- get_node (every `detail` level and every `mode`)
- validate_node (every `mode`)

### Format 2: Workflow Tools
```javascript
// Use FULL prefix
"n8n-nodes-base.slack"
"n8n-nodes-base.httpRequest"
"n8n-nodes-base.webhook"
"@n8n/n8n-nodes-langchain.agent"
```

**Tools that use this**:
- n8n_create_workflow
- n8n_update_partial_workflow
- search_templates({searchMode: "by_nodes", nodeTypes: [...]})

### Conversion

```javascript
// search_nodes returns BOTH formats
{
  "nodeType": "nodes-base.slack",          // For search/validate tools
  "workflowNodeType": "n8n-nodes-base.slack"  // For workflow tools
}
```

---

## Common Mistakes

### ❌ Mistake 1: Wrong nodeType Format

**Problem**: "Node not found" error

```javascript
❌ get_node({nodeType: "slack"})  // Missing prefix
❌ get_node({nodeType: "n8n-nodes-base.slack"})  // Wrong prefix

✅ get_node({nodeType: "nodes-base.slack"})  // Correct!
```

### ❌ Mistake 2: Reaching for `detail: "full"` by default

**Problem**: frequent failures, slow response, huge payload

`get_node` has one `nodeType` and several depths. Picking the deepest one for a routine question buries the
answer in schema.

```javascript
❌ get_node({nodeType: "nodes-base.slack", detail: "full"})
// Returns: the complete property schema, ~3000-8000 tokens

✅ get_node({nodeType: "nodes-base.slack"})
// detail: "standard" is the default — ~1-2K tokens, operations and the properties that matter
```

**When `detail: "full"` earns its cost**:
- Debugging complex configuration issues
- Need the complete property schema, including raw `displayOptions`
- Exploring advanced features

**Cheaper depths first**:
1. `get_node({nodeType})` - operations list at the default `standard` detail
2. `get_node({nodeType, mode: "docs"})` - readable documentation
3. `get_node({nodeType, mode: "search_properties", propertyQuery: "auth"})` - one property, without the schema

### ❌ Mistake 3: Not Using Validation Profiles

**Problem**: Too many false positives OR missing real errors

**Profiles**:
- `minimal` - Only required fields (fast, permissive)
- `runtime` - Values + types (recommended for pre-deployment)
- `ai-friendly` - Reduce false positives (for AI configuration)
- `strict` - Maximum validation (for production)

```javascript
❌ validate_node({nodeType, config, mode: "full"})  // Uses default

✅ validate_node({nodeType, config, mode: "full", profile: "runtime"})  // Explicit
```

The defaults are not the same tool to tool: `validate_node` defaults to `ai-friendly`, while `validate_workflow`'s
`options.profile` defaults to `runtime`. Pre-deployment work wants `runtime` in both places, so say it.

### ❌ Mistake 4: Ignoring Auto-Sanitization

**What happens**: ALL nodes sanitized on ANY workflow update

**Auto-fixes**:
- Binary operators (equals, contains) → removes singleValue
- Unary operators (isEmpty, isNotEmpty) → adds singleValue: true
- IF/Switch nodes → adds missing metadata

**Cannot fix**:
- Broken connections
- Branch count mismatches
- Paradoxical corrupt states

```javascript
// After ANY update, auto-sanitization runs on ALL nodes
n8n_update_partial_workflow({id, operations: [...]})
// → Automatically fixes operator structures
```

### ❌ Mistake 5: Not Using Smart Parameters

**Problem**: Complex sourceIndex calculations for multi-output nodes

**Old way** (manual):
```javascript
// IF node connection
{
  type: "addConnection",
  source: "IF",
  target: "Handler",
  sourceIndex: 0  // Which output? Hard to remember!
}
```

**New way** (smart parameters):
```javascript
// IF node - semantic branch names
{
  type: "addConnection",
  source: "IF",
  target: "True Handler",
  branch: "true"  // Clear and readable!
}

{
  type: "addConnection",
  source: "IF",
  target: "False Handler",
  branch: "false"
}

// Switch node - semantic case numbers
{
  type: "addConnection",
  source: "Switch",
  target: "Handler A",
  case: 0
}
```

---

## Tool Usage Patterns

### Pattern 1: Node Discovery (Most Common)

**Common workflow**: search, then get details

```javascript
// Step 1: Search (fast!)
const results = await search_nodes({
  query: "slack",
  mode: "OR",  // Default: any word matches
  limit: 20
});
// → Returns: nodes-base.slack, nodes-base.slackTrigger

// Step 2: Get details (user reviewing results)
const details = await get_node({
  nodeType: "nodes-base.slack",
  includeExamples: true  // Get real template configs
});
// → Returns: operations, properties, metadata
```

### Pattern 2: Validation Loop

**Typical cycle**: check errors, then fix

```javascript
// Step 1: Validate
const result = await validate_node({
  mode: "full",
  nodeType: "nodes-base.slack",
  config: {
    resource: "channel",
    operation: "create"
  },
  profile: "runtime"
});

// Step 2: Check errors
if (!result.valid) {
  console.log(result.errors);  // "Missing required field: name"
}

// Step 3: Fix config
config.name = "general";

// Step 4: Validate again
await validate_node({..., mode: "full"});  // Repeat until clean
```

### Pattern 3: Workflow Editing

**Most used update tool**: highly reliable, used iteratively

```javascript
// Iterative workflow building (NOT one-shot!)
// Edit 1
await n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{type: "addNode", node: {...}}]
});

// later...

// Edit 2
await n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{type: "addConnection", source: "...", target: "..."}]
});

// later...

// Edit 3 (validation)
await n8n_validate_workflow({id: "workflow-id"});
```

---

## Detailed Guides

### Node Discovery Tools
See [mcp-tools-search-guide.md](mcp-tools-search-guide.md) for:
- search_nodes (highly reliable), including the `source` filter
- get_node and its `detail` levels
- get_node modes: `docs`, `search_properties`

### Validation Tools
See [mcp-tools-validation-guide.md](mcp-tools-validation-guide.md) for:
- Validation profiles explained
- validate_node modes: `minimal` vs `full`
- validate_workflow complete structure
- Auto-sanitization system
- Handling validation errors

### Workflow Management
See [mcp-tools-workflow-guide.md](mcp-tools-workflow-guide.md) for:
- n8n_create_workflow
- n8n_update_partial_workflow (21 operation types!)
- Smart parameters (branch, case)
- AI connection types (12 types)
- cleanStaleConnections recovery

---

## Template Usage

### Search Templates

```javascript
// Search by keyword (searchMode defaults to "keyword")
search_templates({
  query: "webhook slack",
  limit: 20
});
// → Searches a corpus of 2,352 templates, returning matches with metadata

// Search by the nodes a template uses (full-prefix node types here!)
search_templates({
  searchMode: "by_nodes",
  nodeTypes: ["n8n-nodes-base.webhook", "n8n-nodes-base.slack"]
});

// Search by task, from the tool's ten task values
search_templates({searchMode: "by_task", task: "webhook_processing"});

// Get template details
get_template({
  templateId: 2947,  // Weather to Slack
  mode: "structure"  // or "nodes_only", or "full" for complete JSON
});
```

`searchMode` also takes `by_metadata` and `patterns`. Alongside it the tool accepts `complexity`,
`minSetupMinutes`, `maxSetupMinutes`, `requiredService`, `targetAudience`, `fields` and `offset` — reach for those
before scrolling a keyword result set.

### Template Metadata

Templates include:
- Complexity (simple, medium, complex)
- Setup time estimate
- Required services
- Categories and use cases
- View counts (popularity)

---

## Self-Help Tools

### Get Tool Documentation

```javascript
// List all tools
tools_documentation()

// Specific tool details
tools_documentation({
  topic: "search_nodes",
  depth: "full"
})
```

### Health Check

```javascript
// Verify MCP server connectivity
n8n_health_check()
// → Returns: status, features, API availability, version
```

### Corpus size

There is no statistics tool any more. Per the n8n-mcp README the indexed corpus is **2,691 nodes** (832 core plus
1,859 community, of which 1,539 are verified), **267 AI tool variants**, **2,352 templates**, and 156 ranked
example configurations.

---

## Tool Availability

**Always Available** — the 7 core tools, no n8n API needed:
- tools_documentation ✅
- search_nodes ✅
- get_node ✅
- validate_node ✅
- validate_workflow ✅
- search_templates ✅
- get_template ✅

**Requires n8n API** (N8N_API_URL + N8N_API_KEY) — all 21 management tools, per the n8n-mcp README:
- Workflow management (10): n8n_create_workflow, n8n_get_workflow, n8n_update_full_workflow, n8n_update_partial_workflow,
  n8n_delete_workflow, n8n_list_workflows, n8n_validate_workflow (by ID), n8n_autofix_workflow, n8n_workflow_versions,
  n8n_deploy_template ⚠️
- Executions (3): n8n_test_workflow, n8n_executions, n8n_evaluations ⚠️
- Node resources (1): n8n_explore_node_resources ⚠️
- Folders, data tables, credentials, agents (4): n8n_manage_folders, n8n_manage_datatable, n8n_manage_credentials,
  n8n_manage_agents ⚠️
- Security and system (3): n8n_audit_instance, n8n_health_check, n8n_list_catalog ⚠️

**Requires a second secret** (`N8N_MCP_ACCESS_TOKEN`, on top of the API key): `n8n_manage_agents`,
`n8n_explore_node_resources`, `n8n_test_workflow` for any `method` other than `auto`, `n8n_workflow_versions` with
`source: 'native'`, and the datatable column operations.

If API tools unavailable, use templates and validation-only workflows.

---

## Performance Characteristics

| Tool | Response Time | Payload Size | Reliability |
|------|---------------|--------------|-------------|
| search_nodes | <20ms | Small | Very high |
| get_node (detail: "standard") | <10ms | ~5KB | High |
| get_node (detail: "full") | Varies | 100KB+ | Low ⚠️ |
| validate_node (mode: "minimal") | <100ms | Small | High |
| validate_node (mode: "full") | <100ms | Medium | Varies |
| validate_workflow | 100-500ms | Medium | High |
| n8n_create_workflow | 100-500ms | Medium | High |
| n8n_update_partial_workflow | 50-200ms | Small | Very high |

---

## Best Practices

### ✅ Do

- Stay at the default `detail: "standard"` on get_node until you need more
- Specify validation profile explicitly
- Use smart parameters (branch, case) for clarity
- Follow search → get_node → validate workflow
- Iterate workflows (make incremental edits)
- Validate after every significant change
- Use includeExamples: true for real configs

### ❌ Don't

- Use `detail: "full"` unless necessary (slow, huge, unreliable)
- Call a tool name from an earlier n8n-mcp generation — a mode argument on `get_node` or `validate_node` replaced it
- Forget nodeType prefix (nodes-base.*)
- Skip validation profiles (use "runtime")
- Try to build workflows in one shot (iterate!)
- Ignore auto-sanitization behavior
- Use full prefix (n8n-nodes-base.*) with search tools

---

## Summary

**Most Important**:
1. One discovery tool, **get_node**, with a `detail` level — stay on the default `standard` (5KB) rather than
   `full` (100KB+, far less reliable)
2. nodeType formats differ: `nodes-base.*` (search) vs `n8n-nodes-base.*` (workflows)
3. Specify **validation profiles** (runtime recommended)
4. Use **smart parameters** (branch="true", case=0)
5. **Auto-sanitization** runs on ALL nodes during updates
6. Workflows are built **iteratively** (incremental edits)

**Common Workflow**:
1. search_nodes → find node
2. get_node → understand config
3. validate_node (mode: "full") → check config
4. n8n_create_workflow → build
5. n8n_validate_workflow → verify
6. n8n_update_partial_workflow → iterate

For details, see:
- [mcp-tools-search-guide.md](mcp-tools-search-guide.md) - Node discovery
- [mcp-tools-validation-guide.md](mcp-tools-validation-guide.md) - Configuration validation
- [mcp-tools-workflow-guide.md](mcp-tools-workflow-guide.md) - Workflow management

---

**Related Skills**:
- [n8n Expression Syntax](expressions.md) - Write expressions in workflow fields
- [n8n Workflow Patterns](workflow-patterns.md) - Architectural patterns from templates
- [n8n Validation Expert](validation.md) - Interpret validation errors
- [n8n Node Configuration](node-configuration.md) - Operation-specific requirements
