# Integration Patterns

Patterns for integrating Textual TUI applications with the Claude ecosystem.

## MCP Server Integration

TUI applications can consume data from MCP servers. The TUI handles display and interaction while MCP servers provide data access.

### Database Access Pattern

Query databases through MCP database tools and render results in Textual widgets.

```python
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Static
from textual.containers import Vertical
import asyncio
from typing import Any

class DatabaseBrowser(App):
    """TUI for browsing database data via MCP."""

    CSS = """
    #status { dock: bottom; height: 1; background: $surface; }
    #results { height: 1fr; }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="results")
        yield Static("Ready", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        await self.load_data()

    async def load_data(self) -> None:
        """Load data from MCP database tool."""
        status = self.query_one("#status", Static)
        table = self.query_one("#results", DataTable)

        status.update("Loading...")

        # Call MCP tool - actual implementation depends on your MCP client
        result = await self.mcp_client.call_tool(
            "database_query",
            {"query": "SELECT id, name, status FROM items LIMIT 100"}
        )

        table.clear(columns=True)
        if result.rows:
            table.add_columns(*result.columns)
            for row in result.rows:
                table.add_row(*row)

        status.update(f"Loaded {len(result.rows)} rows")

    async def action_refresh(self) -> None:
        await self.load_data()
```

### File Browser Pattern

Navigate file systems using MCP file tools with a Tree widget.

```python
from textual.app import App, ComposeResult
from textual.widgets import Tree, Header, Footer, Static
from textual.containers import Horizontal
from typing import Any

class FileBrowser(App):
    """TUI file browser using MCP file tools."""

    CSS = """
    #tree { width: 40; dock: left; }
    #preview { width: 1fr; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree("Files", id="tree")
            yield Static("Select a file", id="preview")
        yield Footer()

    async def on_mount(self) -> None:
        tree = self.query_one("#tree", Tree)
        await self.populate_tree(tree.root, "/")
        tree.root.expand()

    async def populate_tree(self, node: Any, path: str) -> None:
        """Populate tree node with directory contents from MCP."""
        result = await self.mcp_client.call_tool(
            "list_directory",
            {"path": path}
        )

        for entry in result.entries:
            child = node.add(entry.name, data={"path": entry.path, "is_dir": entry.is_dir})
            if entry.is_dir:
                child.add("...")  # Placeholder for lazy loading

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Lazy load directory contents when expanded."""
        node = event.node
        if node.data and node.data.get("is_dir"):
            # Remove placeholder and load actual contents
            node.remove_children()
            await self.populate_tree(node, node.data["path"])

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Preview file contents when selected."""
        node = event.node
        if node.data and not node.data.get("is_dir"):
            preview = self.query_one("#preview", Static)
            result = await self.mcp_client.call_tool(
                "read_file",
                {"path": node.data["path"]}
            )
            preview.update(result.content[:2000])  # Truncate for preview
```

### External API Pattern

Display external API data with automatic refresh.

```python
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer
from textual.containers import Grid
from typing import Any

class APIDashboard(App):
    """Dashboard displaying external API data via MCP."""

    CSS = """
    Grid { grid-size: 2 2; }
    .metric { border: solid $primary; padding: 1; }
    .metric-value { text-style: bold; color: $accent; }
    """

    BINDINGS = [("r", "refresh", "Refresh"), ("q", "quit", "Quit")]

    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client

    def compose(self) -> ComposeResult:
        yield Header()
        with Grid():
            yield Static("Users: -", id="users", classes="metric")
            yield Static("Revenue: -", id="revenue", classes="metric")
            yield Static("Orders: -", id="orders", classes="metric")
            yield Static("Status: -", id="status", classes="metric")
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_metrics()
        # Auto-refresh every 30 seconds
        self.set_interval(30, self.refresh_metrics)

    async def refresh_metrics(self) -> None:
        """Fetch metrics from external API via MCP."""
        metrics = await self.mcp_client.call_tool(
            "api_request",
            {"url": "https://api.example.com/metrics", "method": "GET"}
        )

        self.query_one("#users").update(f"Users: {metrics.data['users']}")
        self.query_one("#revenue").update(f"Revenue: ${metrics.data['revenue']:,.2f}")
        self.query_one("#orders").update(f"Orders: {metrics.data['orders']}")
        self.query_one("#status").update(f"Status: {metrics.data['status']}")

    async def action_refresh(self) -> None:
        await self.refresh_metrics()
```

## Sub-Agent Integration

TUI applications can delegate specialized tasks to sub-agents and display results.

### Task Delegation Pattern

UI for submitting tasks to specialized agents.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, RichLog, Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.message import Message
from typing import Any

class AgentTaskUI(App):
    """TUI for delegating tasks to sub-agents."""

    CSS = """
    #task-input { width: 1fr; }
    #output { height: 1fr; border: solid $primary; }
    #status { dock: bottom; height: 1; }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, agent_client: Any) -> None:
        super().__init__()
        self.agent_client = agent_client

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Input(placeholder="Enter task...", id="task-input")
            yield Button("Submit", id="submit")
        yield RichLog(id="output", highlight=True, markup=True)
        yield Static("Ready", id="status")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            await self.submit_task()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self.submit_task()

    async def submit_task(self) -> None:
        """Submit task to sub-agent and stream results."""
        task_input = self.query_one("#task-input", Input)
        output = self.query_one("#output", RichLog)
        status = self.query_one("#status", Static)

        task = task_input.value.strip()
        if not task:
            return

        task_input.value = ""
        status.update("Processing...")
        output.write(f"[bold]Task:[/bold] {task}\n")

        # Stream results from sub-agent
        async for chunk in self.agent_client.run_task(task):
            if chunk.type == "text":
                output.write(chunk.content)
            elif chunk.type == "tool_use":
                output.write(f"[dim]Using tool: {chunk.tool_name}[/dim]\n")
            elif chunk.type == "result":
                output.write(f"\n[green]Result:[/green] {chunk.content}\n")

        status.update("Ready")
```

### Multi-Agent Chat Pattern

Route messages to specialized agents based on content.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Header, Footer, Select, Static
from textual.containers import Vertical, Horizontal
from dataclasses import dataclass
from typing import Any

@dataclass
class Agent:
    name: str
    description: str
    client: Any

class MultiAgentChat(App):
    """Chat interface with multiple specialized agents."""

    CSS = """
    #agent-select { width: 20; }
    #chat-input { width: 1fr; }
    #chat-log { height: 1fr; border: solid $surface; }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, agents: list[Agent]) -> None:
        super().__init__()
        self.agents = {a.name: a for a in agents}
        self.current_agent = agents[0].name

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="chat-log", highlight=True, markup=True)
        with Horizontal():
            yield Select(
                [(a.name, a.name) for a in self.agents.values()],
                value=self.current_agent,
                id="agent-select"
            )
            yield Input(placeholder="Message...", id="chat-input")
        yield Footer()

    async def on_select_changed(self, event: Select.Changed) -> None:
        self.current_agent = event.value
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[dim]Switched to {self.current_agent}[/dim]\n")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        chat_input = self.query_one("#chat-input", Input)
        log = self.query_one("#chat-log", RichLog)

        message = chat_input.value.strip()
        if not message:
            return

        chat_input.value = ""
        log.write(f"[bold blue]You:[/bold blue] {message}\n")

        agent = self.agents[self.current_agent]
        log.write(f"[bold green]{agent.name}:[/bold green] ")

        async for chunk in agent.client.chat(message):
            log.write(chunk)

        log.write("\n")
```

### Auto-Routing Pattern

Automatically route queries to the appropriate agent.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Header, Footer, Static
from typing import Any

class AutoRoutingChat(App):
    """Chat that auto-routes to specialized agents."""

    CSS = """
    #chat-log { height: 1fr; }
    #routing-indicator { dock: bottom; height: 1; background: $surface; }
    """

    # Agent routing keywords
    AGENT_ROUTES = {
        "code": ["code", "function", "bug", "error", "implement"],
        "data": ["query", "database", "sql", "table", "report"],
        "docs": ["document", "explain", "how to", "guide", "help"],
    }

    def __init__(self, agents: dict[str, Any]) -> None:
        super().__init__()
        self.agents = agents

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="chat-log", highlight=True, markup=True)
        yield Input(placeholder="Ask anything...", id="chat-input")
        yield Static("Auto-routing enabled", id="routing-indicator")
        yield Footer()

    def route_message(self, message: str) -> str:
        """Determine which agent should handle the message."""
        message_lower = message.lower()
        for agent_name, keywords in self.AGENT_ROUTES.items():
            if any(kw in message_lower for kw in keywords):
                return agent_name
        return "general"  # Default agent

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        chat_input = self.query_one("#chat-input", Input)
        log = self.query_one("#chat-log", RichLog)
        indicator = self.query_one("#routing-indicator", Static)

        message = chat_input.value.strip()
        if not message:
            return

        chat_input.value = ""
        agent_name = self.route_message(message)

        indicator.update(f"Routed to: {agent_name}")
        log.write(f"[bold blue]You:[/bold blue] {message}\n")
        log.write(f"[dim]({agent_name} agent)[/dim] ")

        agent = self.agents.get(agent_name, self.agents["general"])
        async for chunk in agent.chat(message):
            log.write(chunk)

        log.write("\n")
```

## CLAUDE.md Patterns for TUI Projects

Project configuration that helps Claude understand TUI applications.

### Recommended CLAUDE.md Structure

```markdown
# CLAUDE.md

## Project Overview

TUI application built with Textual for [purpose].

## Architecture

- `src/app.py` - Main application entry point
- `src/screens/` - Application screens
- `src/widgets/` - Custom widgets
- `src/services/` - Backend services and MCP integration
- `styles/` - TCSS stylesheets

## Running the Application

```bash
uv run python -m myapp
```

## Testing

```bash
uv run pytest tests/ -v
```

## Key Patterns

### Widget Communication
Widgets communicate via Textual messages. See `src/widgets/` for examples.

### Data Loading
All data loading is async. Use `self.call_later()` for background updates.

### Styling
App uses theme variables ($primary, $surface, etc.) for consistent theming.
External TCSS files in `styles/` for complex styling.

## MCP Integration

This app integrates with MCP servers for:
- Database access: Uses `mcp__database__query` tool
- File operations: Uses `mcp__filesystem__*` tools

See `src/services/mcp_client.py` for integration patterns.
```

### TUI-Specific Instructions

```markdown
## TUI Development Guidelines

### Do
- Use CSS variables for colors ($primary, $surface, $text)
- Keep widgets focused and composable
- Use async for all I/O operations
- Test with Pilot API

### Don't
- Block the event loop
- Use print() for output (use RichLog or Static widgets)
- Hardcode colors (use theme variables)
- Create monolithic widgets
```

## Progressive Loading

Skills use progressive disclosure to manage context efficiently.

### How It Works

1. **SKILL.md loads first** - Lightweight index with tables referencing other files
2. **Reference files load on demand** - Claude reads specific files when needed
3. **Examples provide canonical code** - Source of truth for implementations

### File Size Guidelines

| File Type | Target Lines | Purpose |
|-----------|--------------|---------|
| SKILL.md | < 500 | Index and quick reference |
| Reference | 300-600 | Detailed documentation |
| Example | 50-150 | Canonical implementation |
| Test | 100-200 | Exemplar test patterns |

### Why This Matters

- Reduces initial context consumption
- Allows Claude to fetch relevant details as needed
- Keeps skill responsive across different query types
- Examples serve as trusted code templates
