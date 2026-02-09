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

### 5. ultraplan

Coordinator-delegated planning that breaks complex tasks into subtasks and delegates all implementation to Opus subagents:

- Task breakdown with acceptance criteria and dependencies
- Parallel subagent delegation
- Progress monitoring and output verification

### 6. ultraplan-teams

Team-coordinated planning that creates an agent team for parallel implementation using Claude Code's teams feature:

- Plan-then-execute workflow with user approval gate
- Bidirectional agent communication via shared task list
- File ownership boundaries to prevent edit conflicts
- Embedded engineering standards for teammate quality

### 7. ultrareview

Deep validation protocol that examines preceding context for errors, unvalidated assumptions, alignment issues, and gaps:

- Machine-parseable findings summary
- Prioritized issue categorization
- Use before proceeding with plans or code changes

### 8. ultrareview-fix

Systematically addresses all findings from a preceding ultrareview:

- Works through errors, alignment issues, gaps by priority
- Applies fixes directly to plans or code

### 9. ultrareview-loop

Automated review-fix cycle that iterates until no actionable findings remain:

- Continuous ultrareview → ultrareview-fix iterations
- Stops when validation passes clean

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
- Planning complex multi-step projects (ultraplan, ultraplan-teams)
- Validating plans, code changes, or configurations (ultrareview)
- Fixing review findings automatically (ultrareview-fix, ultrareview-loop)

## License

MIT
