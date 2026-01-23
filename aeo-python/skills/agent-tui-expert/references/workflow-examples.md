# Workflow Examples

Complete workflow examples combining Textual TUI with the Claude ecosystem.

## Agent IDE Workflow

A Claude-powered IDE with file tree, editor, chat, and command panes.

### Architecture

```
+------------------+-------------------------+
|   File Tree      |        Editor           |
|   (Tree widget)  |    (TextArea widget)    |
|                  |                         |
+------------------+-------------------------+
|   Chat Pane      |     Output/Terminal     |
| (RichLog+Input)  |    (RichLog widget)     |
+------------------+-------------------------+
```

### Implementation

```python
from textual.app import App, ComposeResult
from textual.widgets import (
    Tree, TextArea, RichLog, Input, Header, Footer, Static, TabbedContent, TabPane
)
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from pathlib import Path
from typing import Any

class AgentIDE(App):
    """Claude-powered IDE with integrated agent chat."""

    CSS = """
    #file-tree { width: 25; dock: left; border-right: solid $surface; }
    #editor-pane { width: 1fr; }
    #bottom-pane { height: 12; dock: bottom; border-top: solid $surface; }
    #chat-pane { width: 50%; }
    #output-pane { width: 50%; }
    #chat-input { dock: bottom; }
    #file-path { dock: top; height: 1; background: $surface; padding: 0 1; }
    """

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
        Binding("ctrl+p", "command_palette", "Commands"),
        Binding("ctrl+`", "toggle_terminal", "Terminal"),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, agent_client: Any, mcp_client: Any, root_path: str = ".") -> None:
        super().__init__()
        self.agent_client = agent_client
        self.mcp_client = mcp_client
        self.root_path = Path(root_path)
        self.current_file: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree(str(self.root_path), id="file-tree")
            with Vertical(id="editor-pane"):
                yield Static("No file open", id="file-path")
                yield TextArea(id="editor", language="python")
        with Horizontal(id="bottom-pane"):
            with Vertical(id="chat-pane"):
                yield RichLog(id="chat-log", highlight=True, markup=True)
                yield Input(placeholder="Ask Claude...", id="chat-input")
            yield RichLog(id="output-pane", highlight=True)
        yield Footer()

    async def on_mount(self) -> None:
        await self.populate_file_tree()

    async def populate_file_tree(self) -> None:
        """Load file tree from filesystem via MCP."""
        tree = self.query_one("#file-tree", Tree)
        tree.root.expand()
        await self._add_directory_contents(tree.root, self.root_path)

    async def _add_directory_contents(self, node: Any, path: Path) -> None:
        """Recursively add directory contents to tree."""
        result = await self.mcp_client.call_tool(
            "list_directory",
            {"path": str(path)}
        )

        for entry in sorted(result.entries, key=lambda e: (not e.is_dir, e.name)):
            child = node.add(entry.name, data={"path": path / entry.name, "is_dir": entry.is_dir})
            if entry.is_dir:
                child.add("...")  # Lazy loading placeholder

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Lazy load directory when expanded."""
        node = event.node
        if node.data and node.data.get("is_dir"):
            node.remove_children()
            await self._add_directory_contents(node, node.data["path"])

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Open file in editor when selected."""
        node = event.node
        if node.data and not node.data.get("is_dir"):
            await self.open_file(node.data["path"])

    async def open_file(self, path: Path) -> None:
        """Load file content into editor."""
        result = await self.mcp_client.call_tool(
            "read_file",
            {"path": str(path)}
        )

        editor = self.query_one("#editor", TextArea)
        file_path = self.query_one("#file-path", Static)

        editor.load_text(result.content)
        file_path.update(str(path))
        self.current_file = path

        # Set language based on extension
        suffix = path.suffix.lower()
        lang_map = {".py": "python", ".js": "javascript", ".ts": "typescript", ".md": "markdown"}
        editor.language = lang_map.get(suffix, "text")

    async def action_save(self) -> None:
        """Save current file."""
        if not self.current_file:
            return

        editor = self.query_one("#editor", TextArea)
        output = self.query_one("#output-pane", RichLog)

        await self.mcp_client.call_tool(
            "write_file",
            {"path": str(self.current_file), "content": editor.text}
        )

        output.write(f"[green]Saved {self.current_file}[/green]\n")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle chat input - send to Claude agent."""
        if event.input.id != "chat-input":
            return

        chat_input = self.query_one("#chat-input", Input)
        chat_log = self.query_one("#chat-log", RichLog)
        editor = self.query_one("#editor", TextArea)

        message = chat_input.value.strip()
        if not message:
            return

        chat_input.value = ""
        chat_log.write(f"[bold blue]You:[/bold blue] {message}\n")

        # Include current file context if available
        context = ""
        if self.current_file:
            context = f"Current file: {self.current_file}\n```\n{editor.text[:2000]}\n```\n"

        chat_log.write("[bold green]Claude:[/bold green] ")

        async for chunk in self.agent_client.chat(f"{context}\n{message}"):
            if chunk.type == "text":
                chat_log.write(chunk.content)
            elif chunk.type == "tool_use":
                chat_log.write(f"\n[dim]Using: {chunk.tool_name}[/dim]\n")
            elif chunk.type == "code":
                # Offer to apply code changes
                chat_log.write(f"\n[yellow]Suggested code change available[/yellow]\n")

        chat_log.write("\n")

    def action_toggle_sidebar(self) -> None:
        """Toggle file tree visibility."""
        tree = self.query_one("#file-tree")
        tree.display = not tree.display

    def action_toggle_terminal(self) -> None:
        """Toggle bottom pane visibility."""
        bottom = self.query_one("#bottom-pane")
        bottom.display = not bottom.display
```

### Key Features

- **File tree** with lazy loading via MCP file tools
- **Syntax-highlighted editor** with language detection
- **Chat pane** connected to Claude agent with file context
- **Output pane** for command results and logs
- **Keyboard shortcuts** for common IDE operations

## Data Dashboard Workflow

Live dashboard with MCP database queries and real-time updates.

### Architecture

```
+------------------------------------------+
|              Header + Controls           |
+----------+----------+----------+---------+
|  Metric  |  Metric  |  Metric  | Metric  |
+----------+----------+----------+---------+
|          Data Table (scrollable)         |
+------------------------------------------+
|              Status Bar                  |
+------------------------------------------+
```

### Implementation

```python
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DataTable, Button, Select, Input
)
from textual.containers import Horizontal, Vertical, Grid
from textual.timer import Timer
from datetime import datetime
from typing import Any

class MetricCard(Static):
    """A card displaying a single metric."""

    DEFAULT_CSS = """
    MetricCard {
        border: solid $primary;
        padding: 1;
        height: 5;
    }
    MetricCard .label { color: $text-muted; }
    MetricCard .value { text-style: bold; color: $accent; }
    MetricCard .change { color: $success; }
    MetricCard .change.negative { color: $error; }
    """

    def __init__(self, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = label
        self._value = "-"
        self._change = 0.0

    def compose(self) -> ComposeResult:
        yield Static(self.label, classes="label")
        yield Static(self._value, classes="value", id="value")
        yield Static("", classes="change", id="change")

    def update_metric(self, value: str, change: float = 0.0) -> None:
        self._value = value
        self._change = change
        self.query_one("#value").update(value)

        change_widget = self.query_one("#change")
        if change > 0:
            change_widget.update(f"+{change:.1f}%")
            change_widget.remove_class("negative")
        elif change < 0:
            change_widget.update(f"{change:.1f}%")
            change_widget.add_class("negative")
        else:
            change_widget.update("")


class DataDashboard(App):
    """Live data dashboard with MCP queries."""

    CSS = """
    #controls { height: 3; dock: top; }
    #metrics { height: 7; }
    #data-table { height: 1fr; }
    #status { height: 1; dock: bottom; background: $surface; }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("a", "auto_refresh", "Auto Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client
        self.auto_refresh_timer: Timer | None = None
        self.refresh_interval = 30  # seconds

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="controls"):
            yield Select(
                [("Last 24 Hours", "24h"), ("Last 7 Days", "7d"), ("Last 30 Days", "30d")],
                value="24h",
                id="time-range"
            )
            yield Button("Refresh", id="refresh-btn")
            yield Static("Auto: Off", id="auto-status")
        with Grid(id="metrics"):
            yield MetricCard("Total Revenue", id="revenue")
            yield MetricCard("Orders", id="orders")
            yield MetricCard("Customers", id="customers")
            yield MetricCard("Avg Order Value", id="aov")
        yield DataTable(id="data-table")
        yield Static("Ready", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#data-table", DataTable)
        table.add_columns("ID", "Customer", "Amount", "Status", "Date")
        await self.refresh_dashboard()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            await self.refresh_dashboard()

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "time-range":
            await self.refresh_dashboard()

    async def refresh_dashboard(self) -> None:
        """Refresh all dashboard data from MCP."""
        status = self.query_one("#status", Static)
        time_range = self.query_one("#time-range", Select).value

        status.update("Loading...")

        # Fetch metrics
        metrics = await self.mcp_client.call_tool(
            "database_query",
            {"query": f"""
                SELECT
                    SUM(amount) as revenue,
                    COUNT(*) as orders,
                    COUNT(DISTINCT customer_id) as customers,
                    AVG(amount) as aov
                FROM orders
                WHERE created_at > NOW() - INTERVAL '{time_range}'
            """}
        )

        if metrics.rows:
            row = metrics.rows[0]
            self.query_one("#revenue", MetricCard).update_metric(f"${row[0]:,.2f}", 5.2)
            self.query_one("#orders", MetricCard).update_metric(f"{row[1]:,}", 12.3)
            self.query_one("#customers", MetricCard).update_metric(f"{row[2]:,}", -2.1)
            self.query_one("#aov", MetricCard).update_metric(f"${row[3]:,.2f}", 3.8)

        # Fetch recent orders
        orders = await self.mcp_client.call_tool(
            "database_query",
            {"query": f"""
                SELECT o.id, c.name, o.amount, o.status, o.created_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.created_at > NOW() - INTERVAL '{time_range}'
                ORDER BY o.created_at DESC
                LIMIT 100
            """}
        )

        table = self.query_one("#data-table", DataTable)
        table.clear()
        for row in orders.rows:
            table.add_row(str(row[0]), row[1], f"${row[2]:,.2f}", row[3], str(row[4]))

        status.update(f"Updated at {datetime.now().strftime('%H:%M:%S')}")

    def action_refresh(self) -> None:
        self.run_worker(self.refresh_dashboard())

    def action_auto_refresh(self) -> None:
        """Toggle auto-refresh."""
        auto_status = self.query_one("#auto-status", Static)

        if self.auto_refresh_timer:
            self.auto_refresh_timer.stop()
            self.auto_refresh_timer = None
            auto_status.update("Auto: Off")
        else:
            self.auto_refresh_timer = self.set_interval(
                self.refresh_interval,
                lambda: self.run_worker(self.refresh_dashboard())
            )
            auto_status.update(f"Auto: {self.refresh_interval}s")
```

### Key Features

- **Metric cards** with value and trend indicators
- **Time range selection** for filtering data
- **Auto-refresh** with configurable interval
- **Scrollable data table** with recent records
- **Status bar** showing last update time

## Interactive REPL Workflow

REPL with MCP tool access and command completion.

### Architecture

```
+------------------------------------------+
|              Command History             |
|              (RichLog widget)            |
+------------------------------------------+
|  >>> command_input_with_completions      |
+------------------------------------------+
|              Status/Help Bar             |
+------------------------------------------+
```

### Implementation

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input, Static
from textual.containers import Vertical
from textual.suggester import Suggester
from typing import Any
import shlex

class ToolCompleter(Suggester):
    """Suggester that completes MCP tool names."""

    def __init__(self, tools: list[str]) -> None:
        super().__init__(use_cache=False)
        self.tools = tools

    async def get_suggestion(self, value: str) -> str | None:
        for tool in self.tools:
            if tool.startswith(value) and tool != value:
                return tool
        return None


class CommandREPL(App):
    """Interactive REPL with MCP tool access."""

    CSS = """
    #history {
        height: 1fr;
        border: solid $surface;
        padding: 0 1;
    }
    #prompt {
        height: 3;
    }
    #status {
        height: 1;
        background: $surface;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear", "Clear"),
        ("ctrl+h", "help", "Help"),
    ]

    # Built-in commands
    BUILTIN_COMMANDS = {
        "help": "Show available commands",
        "clear": "Clear history",
        "tools": "List available MCP tools",
        "history": "Show command history",
        "quit": "Exit the REPL",
    }

    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client
        self.command_history: list[str] = []
        self.history_index = -1
        self.available_tools: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="history", highlight=True, markup=True)
        yield Input(placeholder="Enter command...", id="prompt")
        yield Static("Type 'help' for commands | Tab to complete", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        # Fetch available MCP tools
        result = await self.mcp_client.list_tools()
        self.available_tools = [t.name for t in result.tools]

        # Set up tool completion
        prompt = self.query_one("#prompt", Input)
        all_commands = list(self.BUILTIN_COMMANDS.keys()) + self.available_tools
        prompt.suggester = ToolCompleter(all_commands)

        # Welcome message
        history = self.query_one("#history", RichLog)
        history.write("[bold]MCP Tool REPL[/bold]")
        history.write(f"[dim]{len(self.available_tools)} tools available[/dim]\n")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = self.query_one("#prompt", Input)
        history = self.query_one("#history", RichLog)

        command = prompt.value.strip()
        if not command:
            return

        prompt.value = ""
        self.command_history.append(command)
        self.history_index = -1

        history.write(f"[bold green]>>>[/bold green] {command}")

        # Parse and execute command
        try:
            await self.execute_command(command)
        except Exception as e:
            history.write(f"[red]Error: {e}[/red]")

        history.write("")  # Blank line

    async def execute_command(self, command: str) -> None:
        """Execute a command (builtin or MCP tool)."""
        history = self.query_one("#history", RichLog)
        parts = shlex.split(command)
        cmd = parts[0]
        args = parts[1:]

        # Check for builtin commands
        if cmd == "help":
            await self.show_help()
        elif cmd == "clear":
            history.clear()
        elif cmd == "tools":
            await self.list_tools()
        elif cmd == "history":
            self.show_history()
        elif cmd == "quit":
            self.exit()
        elif cmd in self.available_tools:
            await self.call_tool(cmd, args)
        else:
            history.write(f"[yellow]Unknown command: {cmd}[/yellow]")
            history.write("[dim]Type 'help' for available commands[/dim]")

    async def show_help(self) -> None:
        """Display help information."""
        history = self.query_one("#history", RichLog)
        history.write("[bold]Built-in Commands:[/bold]")
        for cmd, desc in self.BUILTIN_COMMANDS.items():
            history.write(f"  [cyan]{cmd}[/cyan] - {desc}")
        history.write("\n[bold]MCP Tools:[/bold]")
        history.write(f"  [dim]{len(self.available_tools)} tools available. Type 'tools' to list.[/dim]")

    async def list_tools(self) -> None:
        """List available MCP tools."""
        history = self.query_one("#history", RichLog)
        result = await self.mcp_client.list_tools()

        history.write("[bold]Available MCP Tools:[/bold]")
        for tool in result.tools:
            history.write(f"  [cyan]{tool.name}[/cyan]")
            if tool.description:
                history.write(f"    [dim]{tool.description[:60]}...[/dim]")

    def show_history(self) -> None:
        """Show command history."""
        history = self.query_one("#history", RichLog)
        history.write("[bold]Command History:[/bold]")
        for i, cmd in enumerate(self.command_history[-20:], 1):
            history.write(f"  {i}. {cmd}")

    async def call_tool(self, tool_name: str, args: list[str]) -> None:
        """Call an MCP tool with arguments."""
        history = self.query_one("#history", RichLog)
        status = self.query_one("#status", Static)

        # Parse args as key=value pairs
        params = {}
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                params[key] = value
            else:
                # Positional arg - use as 'query' or first param
                params["query"] = arg

        status.update(f"Running {tool_name}...")

        try:
            result = await self.mcp_client.call_tool(tool_name, params)

            # Format output based on result type
            if hasattr(result, "rows"):
                # Table result
                history.write(f"[dim]({len(result.rows)} rows)[/dim]")
                for row in result.rows[:20]:
                    history.write(f"  {row}")
                if len(result.rows) > 20:
                    history.write(f"  [dim]... and {len(result.rows) - 20} more[/dim]")
            elif hasattr(result, "content"):
                # Text content
                lines = result.content.split("\n")[:30]
                for line in lines:
                    history.write(f"  {line}")
            else:
                # Generic result
                history.write(f"  {result}")

        except Exception as e:
            history.write(f"[red]Tool error: {e}[/red]")

        status.update("Ready")

    def action_clear(self) -> None:
        self.query_one("#history", RichLog).clear()

    async def action_help(self) -> None:
        await self.show_help()

    def on_key(self, event) -> None:
        """Handle up/down for history navigation."""
        if event.key == "up" and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                prompt = self.query_one("#prompt", Input)
                prompt.value = self.command_history[-(self.history_index + 1)]
        elif event.key == "down":
            if self.history_index > 0:
                self.history_index -= 1
                prompt = self.query_one("#prompt", Input)
                prompt.value = self.command_history[-(self.history_index + 1)]
            elif self.history_index == 0:
                self.history_index = -1
                self.query_one("#prompt", Input).value = ""
```

### Key Features

- **Tab completion** for MCP tool names
- **Command history** with up/down navigation
- **Built-in commands** (help, clear, tools, history)
- **MCP tool execution** with argument parsing
- **Formatted output** for different result types

## Common Patterns Across Workflows

### Async Data Loading

Always load data asynchronously to keep the UI responsive:

```python
async def on_mount(self) -> None:
    await self.load_data()

async def load_data(self) -> None:
    # Show loading state
    self.query_one("#status").update("Loading...")

    # Fetch data
    result = await self.mcp_client.call_tool("query", {...})

    # Update UI
    self.update_display(result)

    # Clear loading state
    self.query_one("#status").update("Ready")
```

### Error Handling

Wrap MCP calls with error handling:

```python
async def safe_tool_call(self, tool: str, params: dict) -> Any:
    try:
        return await self.mcp_client.call_tool(tool, params)
    except Exception as e:
        self.query_one("#status").update(f"Error: {e}")
        self.log.error(f"Tool call failed: {tool}", exc_info=True)
        return None
```

### Background Workers

Use workers for long-running operations:

```python
def action_heavy_operation(self) -> None:
    self.run_worker(self.perform_heavy_operation())

async def perform_heavy_operation(self) -> None:
    # Long-running async work
    ...
```
