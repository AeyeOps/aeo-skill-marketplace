"""Minimal Textual Application.

This is the canonical example of the simplest working Textual app.
Use as a starting point for any Textual project.

Run: python minimal_textual_app.py
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer


class MinimalApp(App):
    """A minimal Textual application."""

    CSS = """
    Screen {
        align: center middle;
    }
    #content {
        width: 50;
        height: 5;
        border: solid $primary;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),  # Built-in action
    ]

    def compose(self) -> ComposeResult:
        """Build the UI."""
        yield Header()
        yield Static("Hello, Textual!", id="content")
        yield Footer()


if __name__ == "__main__":
    app = MinimalApp()
    app.run()
