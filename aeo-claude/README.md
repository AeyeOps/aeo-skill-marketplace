# AEO Claude Plugin

Claude development skills: Agent SDK reference, skill creation, slash command creation, Opus prompting techniques, session retrospectives, and Cowork session migration/export utilities.

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

### 10. cowork-migrate

Claude Cowork session migration guidance for Windows-to-Windows moves under the same Cowork account:

- Full transcript restoration, including compact_boundary stitching
- Host path and VM working-directory rewrites
- Sidecar restore handling after Cowork's first-load folder pruning
- Shared Cowork storage-layout documentation and bundle utilities under `shared/cowork/`

## Reference Documentation

| File | Topic |
|------|-------|
| `skills/claude-agent-sdk/references/python-sdk.md` | Complete Python API reference |
| `skills/claude-agent-sdk/references/streaming.md` | Streaming vs single mode patterns |
| `skills/claude-agent-sdk/references/tools-mcp.md` | Tool design and MCP integration |
| `skills/claude-agent-sdk/references/authentication.md` | Auth patterns and token lifecycle |
| `skills/claude-agent-sdk/references/architecture-patterns.md` | GTVR, orchestration, production |
| `shared/cowork/storage-layout.md` | Cowork profile/session/space storage layout |
| `shared/cowork/session-enum.py` | Enumerate Cowork projects and sessions from local profile data |
| `shared/cowork/bundle-pack.py` | Pack a Cowork project into a portable bundle directory |
| `shared/cowork/bundle-manifest.schema.json` | Manifest contract for Cowork bundle import/export |

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
- Running session retrospectives to extract and persist learnings (aeo-retro)
- Migrating or exporting Claude Cowork sessions/projects between machines

## Commands

### /aeo-create-claude-prompt

Create well-crafted prompts for Claude agentic execution:

- Derives context from arguments and conversation, asks only for low-confidence gaps
- Supports file templates, slash commands, console, and embedded string delivery
- Enforces intent-over-procedure and files-over-content principles
- Validates token replacement contracts and output format strictness
- Self-reviews against opus-prompting anti-patterns before presenting

### /aeo-review-claude-prompt

Review and improve existing Claude prompts:

- Evaluates through 7 anti-pattern lenses (content embedding, procedural prescription, exhaustive enums, aggressive language, output clarity, context boundaries, self-defeating instructions)
- Produces a summary verdict, specific issues with quoted passages, and a full revised prompt
- Complementary to create — catches over-specification in prompts written without the creation workflow

### /aeo-retro

Session retrospective that extracts improvements and reconciles stale guidance in CLAUDE.md files and project skills:

- Analyzes session transcript for durable insights (corrections, discoveries, process improvements)
- Reconciles current knowledge against saved CLAUDE.md/SKILL.md content and nous entries
- Routes findings to the appropriate destination (project CLAUDE.md, user CLAUDE.md, project skill, nous)
- Presents proposals with diff format for user approval before applying

## License

MIT
