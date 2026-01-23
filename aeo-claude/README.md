# AEO Claude Plugin

Claude development skills: Agent SDK reference, skill creation, slash command creation, and Opus prompting techniques.

## Installation

```bash
# If marketplace is already added
/plugin install aeo-claude@aeo-skill-marketplace

# Or load directly
claude --plugin-dir ./aeo-claude
```

## Skills Included

### 1. claude-agent-sdk

Comprehensive guidance for building autonomous AI agents:

- **Agent Loop Patterns** - GTVR: gather context, take action, verify, repeat
- **Core APIs** - `ClaudeSDKClient` and `query()` usage
- **Streaming** - Real-time vs single-mode execution
- **Custom Tools** - `@tool` decorator and MCP server integration
- **Hooks** - Runtime control and validation
- **Permissions** - Security models and guardrails
- **Authentication** - API key vs subscription OAuth, token lifecycle
- **Production** - Deployment patterns and best practices

### 2. claude-skill-creator

Guidance for creating Claude Code skills:

- Skill file structure and frontmatter
- Progressive disclosure patterns
- MCP tool references
- Testing and validation

### 3. slash-command-creator

Guidance for creating slash commands:

- Command frontmatter and structure
- Argument handling patterns
- Best practices and examples

### 4. opus-prompting

Prompting techniques optimized for Claude Opus:

- Agentic patterns
- Extended thinking prompts
- Complex reasoning strategies

## Reference Documentation

| File | Topic |
|------|-------|
| `skills/claude-agent-sdk/references/python-sdk.md` | Complete Python API reference |
| `skills/claude-agent-sdk/references/streaming.md` | Streaming vs single mode patterns |
| `skills/claude-agent-sdk/references/tools-mcp.md` | Tool design and MCP integration |
| `skills/claude-agent-sdk/references/authentication.md` | Auth patterns and token lifecycle |
| `skills/claude-agent-sdk/references/architecture-patterns.md` | GTVR, orchestration, production |

## Trigger Phrases

The skills activate when you ask about:

- Building custom agents with Claude Agent SDK
- Creating skills or slash commands for Claude Code
- Prompting techniques for Opus
- Designing effective tools and MCP servers
- Implementing permission models and guardrails

## License

MIT
