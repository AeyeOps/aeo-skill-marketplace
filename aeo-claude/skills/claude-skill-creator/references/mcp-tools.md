# MCP Tool References in Skills

This document explains how to correctly reference MCP (Model Context Protocol) tools in skills.

## Fully Qualified Tool Names

Always use fully qualified tool names to avoid "tool not found" errors.

### Format

```
ServerName:tool_name
```

### Examples

```markdown
Use the `BigQuery:bigquery_schema` tool to retrieve table schemas.
Use the `GitHub:create_issue` tool to create issues.
Use the `Salesforce:query` tool to run SOQL queries.
Use the `Slack:post_message` tool to send messages.
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| **ServerName** | MCP server name from configuration | `BigQuery`, `GitHub`, `Salesforce` |
| **tool_name** | Specific tool provided by server | `bigquery_schema`, `create_issue`, `query` |

---

## Why Fully Qualified Names Matter

**Problem:** Tool names can conflict across MCP servers.

**Example conflict:**
- `Salesforce` server has a `query` tool
- `BigQuery` server has a `query` tool
- Just saying "use the `query` tool" is ambiguous

**Solution:** Always specify `Salesforce:query` or `BigQuery:query`.

---

## Common MCP Servers and Tools

### Salesforce

```markdown
`Salesforce:query` - Execute SOQL queries
`Salesforce:create` - Create records
`Salesforce:update` - Update records
`Salesforce:delete` - Delete records
`Salesforce:describeSObject` - Get object metadata
```

### Context7

```markdown
`mcp__context7__resolve-library-id` - Find library ID
`mcp__context7__get-library-docs` - Fetch documentation
```

### Database (mssql)

```markdown
`mcp__mssql__query` - Execute SQL queries
`mcp__mssql__manage_session` - Manage connections
```

### GitHub

```markdown
`GitHub:create_issue` - Create issues
`GitHub:create_pull_request` - Create pull requests
`GitHub:get_file_contents` - Read repository files
```

---

## Documenting Available Tools

In your skill, list available tools with their purposes:

```markdown
## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `Salesforce:query` | Run SOQL queries |
| `Salesforce:create` | Create new records |
| `Salesforce:update` | Update existing records |
| `Salesforce:describeSObject` | Get field metadata |
```

---

## Error Handling

Include guidance for common MCP errors:

```markdown
## Troubleshooting MCP Tools

### "Tool not found" Error
- Verify the MCP server is configured and running
- Check spelling of server name and tool name
- Use fully qualified format: `ServerName:tool_name`

### Connection Errors
- Check network connectivity
- Verify authentication credentials
- Review MCP server logs for details
```

---

## Example: MCP Tool Usage in SKILL.md

```markdown
## Querying Salesforce Data

To query records:

1. Use `Salesforce:query` with SOQL:
   ```
   SELECT Id, Name FROM Account WHERE CreatedDate = TODAY
   ```

2. For record counts, use `Salesforce:query`:
   ```
   SELECT COUNT() FROM Case WHERE Status != 'Closed'
   ```

**Tool Reference:**
- [MCP Tools Guide](references/mcp-tools.md) - Complete tool documentation
```

---

*Reference: See main [SKILL.md](../SKILL.md) for complete skill creation guidance.*
