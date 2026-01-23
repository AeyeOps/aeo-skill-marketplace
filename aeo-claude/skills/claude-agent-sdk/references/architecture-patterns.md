# Claude Agent SDK - Architecture Patterns

## The Agent Loop (GTVR)

The foundational pattern for all Claude agents:

```
        +-----------------------+
        |   GATHER CONTEXT      |
        | (fetch files, search) |
        +-----------+-----------+
                    |
        +-----------v-----------+
        |   TAKE ACTION         |
        | (tools, code, bash)   |
        +-----------+-----------+
                    |
        +-----------v-----------+
        |   VERIFY WORK         |
        | (check, self-correct) |
        +-----------+-----------+
                    |
        +-----------v-----------+
        |   Done?               |
        |  (goal reached)       |
        +-----------+-----------+
              yes |  | no
                  |  +---------> REPEAT
                  v
              COMPLETE
```

---

## 1. Gather Context

### Agentic Search (vs RAG)

Don't pre-index. Use grep, find, glob on demand:

```python
# Agent searches dynamically
options = ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob"])

async with ClaudeSDKClient(options=options) as client:
    await client.query("Find all SQL queries in src/")
    # Agent uses: grep -r "SELECT" src/ | head -20
    # Then reads relevant files
```

### Subagents for Scale

Large tasks require delegation to isolated subagents:

```
Orchestrator Agent (main task)
    +-- Subagent 1 (extract diagrams)
    +-- Subagent 2 (generate images)
    +-- Subagent 3 (compile Word doc)
    +-- Subagent 4 (create PDF)
```

Benefits:
- No context pollution between subagents
- Parallel execution possible
- Clear responsibility boundaries

---

## 2. Take Action

### Tool Hierarchy (by frequency)

1. **Custom tools** - Most frequent, high-signal actions
2. **File I/O** - read, write, grep, glob
3. **Bash** - Shell scripts, git commands
4. **Code execution** - Complex logic
5. **MCP tools** - External integrations

### Code Generation Pattern

Claude generates code scripts for precision:

```python
# Agent creates script for complex operation
script = """
import pandas as pd
df = pd.read_csv('data.csv')
df_filtered = df[df['status'] == 'active']
df_filtered.to_csv('output.csv', index=False)
"""
# Execute via Bash or code execution tool
```

---

## 3. Verify Work

### Self-Correction Pattern

```python
from claude_agent_sdk import ClaudeSDKClient, ResultMessage

async def run_with_verification():
    async with ClaudeSDKClient() as client:
        # Take action
        await client.query("Create a Python function to parse JSON")

        result = None
        async for msg in client.receive_response():
            if isinstance(msg, ResultMessage):
                result = msg
                break

        if result and result.is_error:
            # Retry with feedback
            await client.query("The previous attempt failed. Please fix the issues.")
            async for msg in client.receive_response():
                pass
```

### Error Handling Pattern

```python
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    ProcessError
)

async def robust_agent():
    max_retries = 3
    backoff = 2

    for attempt in range(max_retries):
        try:
            async for msg in query(prompt="..."):
                process(msg)
            return  # Success
        except ProcessError as e:
            if attempt == max_retries - 1:
                raise
            wait = backoff ** attempt
            await asyncio.sleep(wait)
```

---

## 4. Repeat Control

### Max Turns Pattern

Prevent infinite loops:

```python
options = ClaudeAgentOptions(
    max_turns=10,           # Limit iterations
    max_budget_usd=5.0,     # Cost limit
    max_thinking_tokens=10000  # Thinking limit
)
```

---

## Component Architecture

### Skills vs Subagents vs MCP vs Projects

| Component | Purpose | Use Case |
|-----------|---------|----------|
| **Skills** | Reusable expertise, workflows | Domain knowledge, instructions |
| **Subagents** | Isolated agents with specific roles | Parallel execution, context isolation |
| **MCP** | Dynamic tool integration | Database, email, vector search, APIs |
| **Projects** | Workspace combining all components | Persistent context, settings scope |

### How They Compose

```
Skills + Subagents + MCP + Projects = Full agentic ecosystem

Skills teach *what* and *how*
Subagents execute *where* and *when*
MCP provides *external capabilities*
Projects organize and persist *everything*
```

---

## Multi-Agent Orchestration

### Orchestrator Pattern

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from dataclasses import dataclass
from typing import Any

@dataclass
class Subagent:
    name: str
    system_prompt: str
    allowed_tools: list[str]

    async def execute(self, task: str) -> dict[str, Any]:
        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            allowed_tools=self.allowed_tools
        )
        async with ClaudeSDKClient(options=options) as client:
            await client.query(task)
            results = []
            async for msg in client.receive_response():
                results.append(msg)
            return {"agent": self.name, "results": results}

class Orchestrator:
    def __init__(self):
        self.subagents = {
            "sql_expert": Subagent(
                name="SQL Expert",
                system_prompt="You are an SQL optimization expert.",
                allowed_tools=["Read", "Grep"]
            ),
            "security": Subagent(
                name="Security Analyst",
                system_prompt="You analyze code for security vulnerabilities.",
                allowed_tools=["Read", "Grep", "Bash"]
            ),
            "performance": Subagent(
                name="Performance Tuner",
                system_prompt="You optimize code and infrastructure.",
                allowed_tools=["Read", "Bash"]
            )
        }

    async def orchestrate(self, task: str) -> dict[str, Any]:
        import asyncio
        tasks = [
            agent.execute(task)
            for agent in self.subagents.values()
        ]
        results = await asyncio.gather(*tasks)
        return {r["agent"]: r["results"] for r in results}
```

---

## Context Management

### CLAUDE.md: Persistent Project Context

Location: `.claude/CLAUDE.md` in project root

```markdown
# Project: Email Analytics Platform

## Architecture
- Backend: Python FastAPI
- DB: PostgreSQL
- Queue: Redis
- Frontend: React + TypeScript

## Conventions
- Function names: snake_case
- Constants: UPPER_SNAKE_CASE
- Commits: "feat: " / "fix: " / "docs: " prefixes

## Active Constraints
- Python 3.10+ only
- All DB writes use async
- Email processing must be idempotent

## Current Sprint
- [ ] Add email threading
- [ ] Implement spam filter
- [ ] Performance optimization
```

### Context Compaction

The SDK automatically handles context limits:

1. Agent accumulates messages & tool outputs
2. When approaching limit, summarization kicks in
3. Old conversations become compressed summaries
4. Agent continues with fresh context

### Memory Sizing Guidelines

| Component | Token Estimate |
|-----------|----------------|
| Skill + references | 3,000-5,000 tokens |
| Project context (CLAUDE.md) | 500-1,000 tokens |
| Agent messages | 1,000-3,000 per turn |
| Available context | 200K (Sonnet) to 1M (Opus) |

---

## Production Patterns

### Deployment Checklist

- [ ] Permission model defined (manual/acceptEdits/acceptAll)
- [ ] Allowlist vs denylist strategy chosen
- [ ] Error handling with graceful failures
- [ ] Timeouts: max_turns, per-tool timeout
- [ ] Logging: All actions logged (sanitized)
- [ ] Monitoring: Health checks, metrics
- [ ] Secrets: API keys in env vars
- [ ] Rate limiting on external API calls
- [ ] Audit trail for mutations

### Permission Modes by Environment

| Mode | Environment | Use Case |
|------|-------------|----------|
| `manual` | Development | Full visibility |
| `acceptEdits` | Staging | Faster iteration, still safe |
| `acceptAll` | Production | Trusted background jobs |

### Logging and Observability

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, HookContext
import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def log_tool_use(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get('tool_name', 'unknown')
    logger.info(f"Tool: {tool_name} | Args: {input_data.get('tool_input', {})}")
    return {}

async def log_tool_result(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    logger.info(f"Result: {input_data}")
    if input_data.get("error"):
        logger.error(f"Tool failed: {input_data['error']}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [HookMatcher(hooks=[log_tool_use])],
        'PostToolUse': [HookMatcher(hooks=[log_tool_result])]
    }
)
```

### Rate Limiting Pattern

```python
from asyncio import Semaphore
from claude_agent_sdk import tool
from typing import Any

rate_limiter = Semaphore(10)  # Max 10 concurrent API calls

@tool("rate_limited_api", "Call external API with rate limiting", {"query": str})
async def rate_limited_api(args: dict[str, Any]) -> dict[str, Any]:
    async with rate_limiter:
        result = await expensive_api_call(args["query"])
        return {"content": [{"type": "text", "text": str(result)}]}
```

---

## Example Agent Architectures

### Email Agent

```
email-agent/
+-- SKILL.md              # Email agent workflow
+-- references/
|   +-- email-filtering.md
|   +-- draft-strategies.md
|   +-- threading-model.md
+-- scripts/
|   +-- setup_gmail_oauth.py
+-- templates/
|   +-- email-reply-template.txt
+-- examples/
    +-- draft_response.py
```

### Code Review Agent

```
code-review-agent/
+-- SKILL.md
+-- references/
|   +-- security-checklist.md
|   +-- code-metrics.md
|   +-- best-practices.md
+-- scripts/
|   +-- lint_python.py
|   +-- scan_vulnerabilities.sh
|   +-- analyze_ast.py
+-- examples/
    +-- review_pr.py
```

### Research Agent

```
research-agent/
+-- SKILL.md
+-- references/
|   +-- research-methodology.md
|   +-- source-evaluation.md
|   +-- synthesis-patterns.md
+-- scripts/
|   +-- web_search.py
+-- examples/
    +-- research_topic.py
```
