---
name: n8n
description: |
  Use when building, debugging, or reviewing n8n 2.x workflow automation: writing {{ }} expressions over $json, $node
  and $input; scripting a Code node in JavaScript or Python; node configuration and missing or unknown parameters;
  validation errors, warnings and false positives; driving the n8n-mcp MCP tools for node search, configuration
  validation and workflow creation; or choosing a workflow pattern for webhook processing, REST API integration,
  a database pipeline, an AI agent, or scheduled and cron automation. Covers the n8n workflow layer end to end —
  expression syntax, Code node APIs, node parameters, validation, MCP tooling and architectural workflow patterns —
  not self-hosted n8n installation, upgrades or infrastructure.
license: MIT
metadata:
  author: AeyeOps
  version: "0.4.1"
  summary: Router and cross-cutting rules for n8n workflow automation, with deep-dive references for expressions, Code nodes, node configuration, validation, n8n-mcp tools and workflow patterns.
---

# n8n

Expert guidance for building n8n workflows: expressions, Code nodes, node configuration, validation, the n8n-mcp
tool surface, and the five production workflow patterns.

Read this file for the rules that apply everywhere, then open the one reference that matches the task.

---

## Which reference to read

| Task | Reference | Purpose |
|------|-----------|---------|
| Write or debug `{{ }}` expressions, map data between nodes | [references/expressions.md](references/expressions.md) | n8n's double-curly-brace expression language: `$json`, `$('Node Name')`, `$input` access patterns, evaluation failures, webhook payloads |
| Write JavaScript in a Code node | [references/code-javascript.md](references/code-javascript.md) | JavaScript logic with the `$input`, `$json`, `$('Node Name')` and `this.helpers` APIs, HTTP requests, Luxon DateTime, error debugging, mode selection |
| Write Python in a Code node | [references/code-python.md](references/code-python.md) | Native Python logic with the `_items` / `_item` accessors, the runner import allowlists, execution constraints, and why JavaScript is the default |
| Configure a node, chase a missing parameter | [references/node-configuration.md](references/node-configuration.md) | Operation-specific configuration and property dependencies: required versus optional fields, progressive disclosure with `get_node`, patterns by node type |
| Fix validation failures and false positives | [references/validation.md](references/validation.md) | Validation profiles, the iterative fix cycle, error categorisation, and which warnings are safe to ignore |
| Drive the n8n-mcp server's tools | [references/mcp-tools.md](references/mcp-tools.md) | The 7 core plus 21 management n8n-mcp tools for node discovery, configuration validation, template access and workflow management, plus tool-selection strategy and parameter formats |
| Pick an architecture for a new workflow | [references/workflow-patterns.md](references/workflow-patterns.md) | Blueprints from production deployments: webhook handlers, REST API integrations, database pipelines, AI agent orchestration, scheduled automation |

### Deep dives

Each topic above has companion references, opened from the topic file or directly:

- Expressions: [references/expressions-examples.md](references/expressions-examples.md) (real workflow examples),
  [references/expressions-common-mistakes.md](references/expressions-common-mistakes.md) (complete error catalogue)
- JavaScript Code node: [references/code-javascript-data-access.md](references/code-javascript-data-access.md),
  [references/code-javascript-common-patterns.md](references/code-javascript-common-patterns.md),
  [references/code-javascript-error-patterns.md](references/code-javascript-error-patterns.md),
  [references/code-javascript-builtin-functions.md](references/code-javascript-builtin-functions.md)
- Python Code node: [references/code-python-data-access.md](references/code-python-data-access.md),
  [references/code-python-common-patterns.md](references/code-python-common-patterns.md),
  [references/code-python-error-patterns.md](references/code-python-error-patterns.md),
  [references/code-python-standard-library.md](references/code-python-standard-library.md)
- Node configuration: [references/node-configuration-dependencies.md](references/node-configuration-dependencies.md),
  [references/node-configuration-operation-patterns.md](references/node-configuration-operation-patterns.md)
- Validation: [references/validation-error-catalog.md](references/validation-error-catalog.md),
  [references/validation-false-positives.md](references/validation-false-positives.md)
- n8n-mcp tools: [references/mcp-tools-search-guide.md](references/mcp-tools-search-guide.md),
  [references/mcp-tools-validation-guide.md](references/mcp-tools-validation-guide.md),
  [references/mcp-tools-workflow-guide.md](references/mcp-tools-workflow-guide.md)
- Workflow patterns: [references/workflow-patterns-webhook-processing.md](references/workflow-patterns-webhook-processing.md),
  [references/workflow-patterns-http-api-integration.md](references/workflow-patterns-http-api-integration.md),
  [references/workflow-patterns-database-operations.md](references/workflow-patterns-database-operations.md),
  [references/workflow-patterns-ai-agent-workflow.md](references/workflow-patterns-ai-agent-workflow.md),
  [references/workflow-patterns-scheduled-tasks.md](references/workflow-patterns-scheduled-tasks.md)

---

## Cross-cutting rules

These four rules decide most n8n bugs. They apply across expressions, Code nodes, node parameters and patterns, so
they are stated once here; the details stay in the references.

### 1. Webhook data lives under `.body`

The Webhook node wraps the incoming request so headers, params and query survive alongside the payload:

```javascript
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // user data is HERE
    "name": "John",
    "email": "john@example.com"
  }
}
```

Reaching for the field at the root is the single most common n8n mistake, in every language:

```javascript
// Expression field
❌ {{$json.name}}          ✅ {{$json.body.name}}

// JavaScript Code node
❌ const name = $json.name;            ✅ const name = $json.body.name;

# Python Code node (per-item mode)
❌ name = _item["json"]["name"]        ✅ name = _item["json"]["body"]["name"]
```

Details: [references/expressions.md](references/expressions.md),
[references/workflow-patterns-webhook-processing.md](references/workflow-patterns-webhook-processing.md).

### 2. Expressions and Code nodes are different languages

`{{ }}` is for **node parameter fields**. Code nodes run JavaScript or Python **directly** and never use `{{ }}`.

| Context | Access | Example |
|---------|--------|---------|
| Node parameter field | Expression, wrapped in `{{ }}` | `{{$json.body.email}}` |
| Node parameter field, other node | Quoted, exact node name | `{{$('HTTP Request').json.data}}` |
| JavaScript Code node | Direct variable | `const email = $json.body.email;` |
| Python Code node | Direct variable | `email = _item["json"]["body"]["email"]` |

Expressions do **not** evaluate in a webhook path — that route is registered once, so use a route parameter
(`user/:userId`, read back as `$json.params.userId`) when the path must vary. Credential fields are the
opposite case: they *do* take expressions, and they are the only place `$secrets` resolves at all. Node names
inside `$('Node Name')` are case-sensitive, must be quoted, and `{{ }}` never nests.

Reach for a Code node when the logic is a multi-step transformation, a custom calculation, recursion, complex
response parsing or cross-item aggregation. Reach for **Set**, **Filter**, **IF**/**Switch** or **HTTP Request**
when it is field mapping, basic filtering, a simple conditional or a plain request.

Details: [references/expressions.md](references/expressions.md),
[references/code-javascript.md](references/code-javascript.md), [references/code-python.md](references/code-python.md).

### 3. Choose the Code node mode, then return the right shape

Code nodes offer two execution modes. **Run Once for All Items** is the default and the right answer for most
work — the code runs once with the whole batch, so aggregation, sorting, deduplication and top-N are possible.
**Run Once for Each Item** runs the code per item and only exposes `$input.item` (JavaScript) or `_item`
(Python); use it when each item is genuinely independent and the per-item code is simple. Python's whole surface
is `_items` in all-items mode and `_item` per item, with bracket access only.

Whichever mode, the return value must be an array (JavaScript) or list (Python) of objects each carrying a `json`
key:

```javascript
// JavaScript
return [{json: {result: "value"}}];              // ✅
return {result: "value"};                        // ❌ not wrapped
return [{result: "value"}];                      // ❌ missing json key

// Python
return [{"json": {"result": "value"}}]           # ✅
return {"result": "value"}                       # ❌ dict without list wrapper
```

Python imports are allowlisted on the task runner, not free: the standard library needs
`N8N_RUNNERS_STDLIB_ALLOW` and third-party packages need `N8N_RUNNERS_EXTERNAL_ALLOW` plus an extended
`n8nio/runners` image — and n8n Cloud permits no imports at all. Native Python also requires task runners in
external mode. When an import is blocked, use an HTTP Request node, or switch to JavaScript and
`this.helpers.httpRequest()`, which is the default language for a reason.

Details: [references/code-javascript.md](references/code-javascript.md),
[references/code-python.md](references/code-python.md),
[references/code-python-standard-library.md](references/code-python-standard-library.md).

### 4. Validate before you deploy, and iterate

Configuration is not finished when it looks right; it is finished when validation passes. The loop that works:

```
1. Configure node
   ↓
2. validate_node({nodeType, config, mode: "full", profile: "runtime"})
   ↓
3. Read the error messages carefully
   ↓
4. Fix errors
   ↓
5. validate_node again
   ↓
6. Repeat until valid (usually 2-3 iterations)
```

Then validate the assembled workflow with `validate_workflow` before you create it.

A validated workflow is still a **draft**. n8n 2.0 replaced activate/deactivate with a draft/publish model:
saving changes nothing about what runs until you publish, so finish with the `activateWorkflow` operation on
`n8n_update_partial_workflow` (or `publish:workflow --id=<ID>` on the CLI). "I saved it and nothing happened" is
almost always an unpublished draft.

Pick the profile that matches the stage:

| Profile | Use when | Trade-off |
|---------|----------|-----------|
| `minimal` | Quick checks while editing | Fastest, may miss issues |
| `runtime` | Pre-deployment (**recommended**) | Balanced, catches real errors |
| `ai-friendly` | AI-generated configurations | Fewer false positives, tolerates minor issues |
| `strict` | Production and critical workflows | Maximum safety, many warnings |

Name the profile explicitly: `validate_node` defaults to `ai-friendly`, `validate_workflow` defaults to
`runtime`. Errors must be fixed. Warnings should be fixed. Suggestions are optional. Some warnings are known
false positives — check before chasing them.

Details: [references/validation.md](references/validation.md),
[references/validation-false-positives.md](references/validation-false-positives.md),
[references/mcp-tools-validation-guide.md](references/mcp-tools-validation-guide.md).

---

## Working with n8n-mcp

When the n8n-mcp server is available, the usual sequence is discover → configure → validate → build:

1. `search_nodes({query: "..."})` to find the node
2. `get_node({nodeType: "nodes-base.<node>"})` for the fields that matter — `detail` defaults to `standard`, and
   `detail: "full"` returns the entire schema, which is rarely what you want
3. `validate_node({nodeType, config, mode: "full", profile: "runtime"})` on the configuration, iterating as above
4. `n8n_create_workflow` / `n8n_update_partial_workflow` to build and edit
5. `validate_workflow` on the finished structure
6. `n8n_update_partial_workflow({id, operations: [{type: "activateWorkflow"}]})` to publish it

There are 28 tools: 7 core ones that need no n8n instance (`tools_documentation`, `search_nodes`, `get_node`,
`validate_node`, `validate_workflow`, `search_templates`, `get_template`) and 21 management tools behind
`N8N_API_URL` + `N8N_API_KEY`. Each core tool absorbed several older single-purpose tools behind a `detail`,
`mode` or `searchMode` argument, so a call written against an earlier generation fails with "unknown tool".

Node type strings come in two formats and mixing them is a frequent failure: search and validation tools take the
short form (`nodes-base.slack`), workflow tools take the full form (`n8n-nodes-base.slack`).

Details: [references/mcp-tools.md](references/mcp-tools.md),
[references/mcp-tools-search-guide.md](references/mcp-tools-search-guide.md),
[references/mcp-tools-workflow-guide.md](references/mcp-tools-workflow-guide.md).

---

## The five workflow patterns

Start from the pattern that matches the trigger and the destination, then fill in the nodes:

| Pattern | Shape | Reference |
|---------|-------|-----------|
| Webhook processing (most common) | Webhook → Validate → Transform → Respond/Notify | [references/workflow-patterns-webhook-processing.md](references/workflow-patterns-webhook-processing.md) |
| HTTP API integration | Trigger → HTTP Request → Transform → Action → Error Handler | [references/workflow-patterns-http-api-integration.md](references/workflow-patterns-http-api-integration.md) |
| Database operations | Schedule → Query → Transform → Write → Verify | [references/workflow-patterns-database-operations.md](references/workflow-patterns-database-operations.md) |
| AI agent workflow | Trigger → AI Agent (model + tools + memory) → Output | [references/workflow-patterns-ai-agent-workflow.md](references/workflow-patterns-ai-agent-workflow.md) |
| Scheduled tasks | Schedule → Fetch → Process → Deliver → Log | [references/workflow-patterns-scheduled-tasks.md](references/workflow-patterns-scheduled-tasks.md) |

Selection guidance, the shared components of every pattern, and the full worked examples live in
[references/workflow-patterns.md](references/workflow-patterns.md).

---

## Attribution

Conceived as the n8n-mcp project by Romuald Czlonkowski (aiadvisors.pl), adapted and maintained by AeyeOps — see
NOTICE.md at the plugin root.
