"""IDE-Like Multi-Pane Layout.

This is the canonical example of a multi-pane IDE layout with:
- Left sidebar (file tree)
- Main editor area
- Bottom terminal/output pane
- Header and footer

Use as reference for building IDE-style applications.

Run: python ide_layout.py
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    Input,
    RichLog,
    Static,
    Tree,
)


class IDELayout(App):
    """An IDE-like multi-pane layout."""

    CSS = """
    #sidebar {
        width: 25;
        dock: left;
        background: $surface;
        border-right: solid $primary;
    }
    #main {
        width: 1fr;
    }
    #editor {
        height: 2fr;
        border: solid $secondary;
        padding: 1;
    }
    #output {
        height: 1fr;
        border: solid $secondary;
    }
    #command-input {
        dock: bottom;
        height: 3;
    }
    Tree {
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+p", "command_palette", "Commands"),
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
    ]

    def compose(self) -> ComposeResult:
        """Build the IDE layout."""
        yield Header()

        # Sidebar with file tree
        with Vertical(id="sidebar"):
            tree: Tree[str] = Tree("Project", id="file-tree")
            tree.root.expand()
            tree.root.add_leaf("README.md")
            src = tree.root.add("src")
            src.add_leaf("main.py")
            src.add_leaf("utils.py")
            tests = tree.root.add("tests")
            tests.add_leaf("test_main.py")
            yield tree

        # Main area
        with Vertical(id="main"):
            yield Static("Editor content here...", id="editor")
            yield RichLog(id="output", highlight=True, markup=True)

        yield Input(placeholder="Enter command...", id="command-input")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        log = self.query_one("#output", RichLog)
        log.write("[bold cyan]Output pane ready[/]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input."""
        log = self.query_one("#output", RichLog)
        log.write(f"[bold green]>[/] {event.value}")
        event.input.clear()

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        """Handle file selection."""
        log = self.query_one("#output", RichLog)
        log.write(f"[dim]Selected: {event.node.label}[/]")

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display


if __name__ == "__main__":
    app = IDELayout()
    app.run()
