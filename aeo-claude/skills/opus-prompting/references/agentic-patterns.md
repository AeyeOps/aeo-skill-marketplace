# Agentic Patterns for Opus 4.6

Best practices for building agents, agent teams, MCPs, and long-horizon workflows with Opus 4.6.

## Table of Contents

1. [Context Management](#1-context-management)
2. [Agent Teams](#2-agent-teams)
3. [Sub-Agent Delegation](#3-sub-agent-delegation)
4. [Tool Design](#4-tool-design)
5. [State Tracking](#5-state-tracking)
6. [Long-Horizon Workflows](#6-long-horizon-workflows)
7. [Parallel Execution](#7-parallel-execution)
8. [Error Handling](#8-error-handling)
9. [Adaptive Thinking](#9-adaptive-thinking)

---

## 1. Context Management

Opus 4.6 has a standard 200K context window with 1M available in beta. Server-side compaction is now available, reducing client-side context management burden.

### Key Patterns

**Progress Summaries at 20% Remaining**
```
When approaching context limits (~20% remaining), create a progress summary:
- What has been accomplished
- Current state of the task
- Next steps to continue

Then clear context and resume with the summary.
```

**Server-Side Compaction (4.6 Beta)**
```
Opus 4.6 supports server-side context summarization via the Compaction API.
Older messages are automatically summarized when approaching limits—no
additional API calls required. This enables effectively infinite conversations.
```

**Fresh Starts vs Compaction**
```
Consider starting with a fresh context window rather than compaction.
Opus 4.6 effectively discovers state from local filesystems.

On fresh start:
1. Call pwd to establish location
2. Review progress.txt or similar state file
3. Check git logs for recent changes
4. Resume from documented checkpoint
```

---

## 2. Agent Teams

Opus 4.6 introduces agent teams—parallel agents coordinating on complex projects.

### When to Use Teams

- Frontend, backend, and testing can run simultaneously
- Large refactors across independent modules
- Research + implementation in parallel
- Any task where components are independent but need coordination

### Team Pattern

```
Create teams of agents that collaborate in parallel:

- Coordinator: Breaks down task, assigns to specialists
- Specialists: Work on independent components simultaneously
- Reviewer: Validates integration across components

Agents share state via filesystem (progress files, git branches).
```

### Teams vs Sub-Agents

| | Sub-Agents | Agent Teams |
|---|---|---|
| **Execution** | Sequential | Parallel |
| **Context** | Each gets fresh window | Each gets fresh window |
| **Coordination** | Parent manages | Coordinator + shared state |
| **Use when** | Research, investigation | Implementation, multi-component work |

---

## 3. Sub-Agent Delegation

Delegate research-heavy tasks to sub-agents to preserve main context.

### When to Delegate

- Searching large codebases for patterns
- Exploring documentation
- Running multiple investigation paths
- Tasks that consume significant context

### Delegation Pattern

```
For research-intensive subtasks, delegate to a sub-agent:

Task: [specific subtask description]
Return: [what information to bring back]

The sub-agent will consume its own context budget, preserving yours.
```

### Conservative Delegation

```
Only delegate to subagents when the task clearly benefits from
a separate agent with a new context window.
```

---

## 4. Tool Design

Opus 4.5+ responds strongly to tool descriptions. Design carefully.

### Tool Description Pattern

```json
{
  "name": "search_codebase",
  "description": "Search for patterns in the codebase. Use when exploring code structure or finding implementations. Returns matching files and line numbers."
}
```

### Avoid Over-Triggering

```
# Too aggressive (causes over-triggering)
"description": "CRITICAL: You MUST use this tool whenever code is mentioned."

# Better
"description": "Search for code patterns. Use when looking for implementations or exploring structure."
```

### Tool Invocation in System Prompts

```
# Before
If you need to search, you MUST ALWAYS use the search tool.

# After
Use the search tool to find relevant code or documentation.
```

---

## 5. State Tracking

Maintain state effectively across context windows.

### Structured Formats

```
Use structured formats (JSON) for organized data:
- Test results
- Task checklists
- Configuration state

Use unstructured text for:
- Progress notes
- Reasoning traces
- Exploration logs
```

### Git for State

```
Leverage Git for state tracking across sessions:
- Commits preserve work state
- Branches isolate experiments
- Logs provide history

On session start, check git status and recent commits.
```

### State File Pattern

```json
// progress.json
{
  "current_task": "Implement authentication",
  "completed": ["Setup database", "Create user model"],
  "blocked": [],
  "next_steps": ["Add JWT tokens", "Create login endpoint"],
  "context_notes": "Using bcrypt for passwords, JWT for tokens"
}
```

---

## 6. Long-Horizon Workflows

Opus 4.6 excels at sustained reasoning across extended tasks, now with up to 128K output tokens.

### Incremental Progress

```
Focus on incremental progress:
- Make steady advances on a few things at a time
- Don't attempt everything at once
- Complete components before moving on
```

### Prescriptive Starts

```
On session start, be prescriptive:

1. Call pwd; you can only read and write files in this directory
2. Review progress.txt, tests.json, and the git logs
3. Run fundamental integration tests before implementing new features
```

### Test-First Pattern

```
Create tests before starting work:
- Keep track in structured format (tests.json)
- Run tests frequently
- Never remove or edit tests (could miss bugs)
```

### Quality of Life Scripts

```
Create setup scripts early:
- init.sh: Start servers, set up environment
- test.sh: Run test suite
- lint.sh: Check code quality

These reduce cognitive load across sessions.
```

---

## 7. Parallel Execution

Opus 4.6 excels at parallel tool execution.

### Encourage Parallelism

```
If you intend to call multiple tools and there are no dependencies
between the calls, make all independent calls in parallel.
```

### Reduce Parallelism (When Needed)

```
Execute operations sequentially with brief pauses between each step
to ensure stability.
```

### Dependency Awareness

```
# Parallel (no dependencies)
- Read file A
- Read file B
- Search for pattern X

# Sequential (dependencies)
- Read config.json
- Use config values to connect to database
- Query database
```

---

## 8. Error Handling

Design for robustness in agentic workflows.

### Fail Fast

```
If you encounter an error you cannot resolve:
1. Document the error clearly
2. Save current state to progress file
3. Report the blocker
4. Do not attempt workarounds that mask the issue
```

### Prompt Injection Resistance

Opus 4.6 has improved prompt injection resistance, but:

```
- Still vulnerable (~33% success rate with 10 attempts)
- Defensive application design remains essential
- Validate untrusted inputs
- Sandbox tool execution
```

### Non-Determinism

```
Model outputs vary across identical prompts.
- Run multiple attempts for critical operations
- Don't expect consistent results from single tries
- Use verification steps after generation
```

---

## System Prompt Template for Agents

```
# Agent System Prompt

You are an autonomous coding agent.

## Context Awareness
Your context window will be compacted when approaching limits.
Save progress to files before context runs low.

## Tool Usage
Use available tools when they help. Don't force tool use unnecessarily.

## State Management
- Check progress.json on startup
- Update progress after completing tasks
- Commit work frequently

## Long-Horizon Tasks
- Focus on incremental progress
- Complete one component before starting another
- Run tests frequently
- Document decisions and blockers

## Delegation
Delegate research tasks to sub-agents when beneficial.
Keep your context focused on the current implementation.
```

---

## 9. Adaptive Thinking

Opus 4.6 replaces extended thinking with adaptive thinking—4 effort levels that dynamically adjust reasoning depth.

### Effort Levels

| Level | Use Case | Reasoning Behavior |
|-------|----------|-------------------|
| `low` | Simple edits, quick lookups | Skips deliberation |
| `medium` | Standard implementation | Moderate reasoning |
| `high` | Complex reasoning, architecture (default) | Full deliberation |
| `max` | Hardest problems, novel research | Peak reasoning capability |

### Migration from Extended Thinking

```
# Before (Opus 4.5)
"thinking": {"type": "enabled", "budget_tokens": 10000}

# After (Opus 4.6)
"thinking": {"type": "enabled", "effort": "high"}
```

The `budget_tokens` parameter is deprecated. Opus 4.6 auto-calibrates reasoning depth within each effort level.

### Prompting Implications

- The "think" word sensitivity from 4.5 is reduced since adaptive thinking handles reasoning calibration
- Avoid explicitly requesting reasoning depth ("think harder")—instead, set the effort level via API
- For Claude Code skills: the model selects effort automatically; no need to specify in skill prompts

### Breaking Change: Prefilling Disabled

Opus 4.6 returns a 400 error for assistant message prefilling. Migrate to:
- `output_config.format` for JSON output structure
- `json_schema` parameter for structured output validation
- System prompt instructions for output formatting
