---
name: agent-tui-expert
description: Construct rich terminal interfaces using Textual for multi-pane dashboards with CSS styling and Python Prompt Toolkit for interactive line editing with completions. Covers widget composition, key bindings, TUI testing strategies, and WSL2 layout quirks. Engage when building IDE-style interfaces, REPL shells, or dashboard applications.
---

# Agent TUI Expert

Expert guidance for building professional Terminal User Interfaces in Python.

## CRITICAL: WSL2 Users Read First

**If developing in WSL2, read [references/wsl2-platform-issues.md](references/wsl2-platform-issues.md) BEFORE starting.**

WSL2 has a critical bug (Microsoft/WSL#1001) where horizontal terminal resize does not propagate SIGWINCH signals. This breaks Textual resize handling and requires a specific workaround using `ioctl TIOCGWINSZ` polling. The reference file contains battle-tested solutions that took 12+ hours to discover.

## When to Use This Skill

- Building full-screen TUI applications with multiple panes
- Creating IDE-like layouts (file tree, editor, terminal)
- Adding command input with history and auto-completion
- Building interactive REPLs or shell interfaces
- Implementing keyboard navigation and shortcuts
- Testing TUI applications with automated interactions

## Decision Tree

```
Need multi-pane, full-screen UI?
├─ YES → Use Textual
│        (widgets, containers, CSS styling, message passing)
│
Need advanced line editing, history, completions?
├─ YES → Use Prompt Toolkit
│        (PromptSession, FileHistory, Completers, key bindings)
│
Need both?
└─ Use Textual with Suggester API for input completion
   Or embed prompt_toolkit patterns in custom widgets
```

## Quick Reference

### Textual Minimal App

```python
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer

class MyApp(App):
    CSS = """
    Screen { align: center middle; }
    #content { border: solid $primary; padding: 1 2; }
    """
    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Dark Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, Textual!", id="content")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

if __name__ == "__main__":
    MyApp().run()
```

### Prompt Toolkit Minimal Prompt

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

session = PromptSession(
    history=FileHistory(".history"),
    completer=WordCompleter(["help", "quit", "status", "run"]),
)

while True:
    text = session.prompt(">>> ")
    if text == "quit":
        break
    print(f"You entered: {text}")
```

## Contents Index

### References (Detailed Documentation)

| File | Purpose |
|------|---------|
| [references/wsl2-platform-issues.md](references/wsl2-platform-issues.md) | **READ FIRST** - WSL2 resize bugs, ioctl workarounds, layout gotchas |
| [references/textual-patterns.md](references/textual-patterns.md) | App lifecycle, containers, CSS styling, messages, widgets |
| [references/prompt-toolkit-patterns.md](references/prompt-toolkit-patterns.md) | Prompts, history, completions, key bindings, validation |
| [references/testing-guide.md](references/testing-guide.md) | Pilot API, snapshot testing, buffer/completer testing |
| [references/themes-and-colors.md](references/themes-and-colors.md) | Built-in themes, color variables, theme switching |
| [references/integration-patterns.md](references/integration-patterns.md) | MCP servers, sub-agents, CLAUDE.md patterns |
| [references/workflow-examples.md](references/workflow-examples.md) | Agent IDE, data dashboard, REPL workflows |

### Examples (Canonical Code)

| File | Purpose | Use As Reference For |
|------|---------|---------------------|
| [examples/minimal_textual_app.py](examples/minimal_textual_app.py) | Simplest working Textual app | Starting any Textual project |
| [examples/ide_layout.py](examples/ide_layout.py) | Multi-pane IDE layout | Building IDE-style applications |
| [examples/ptk_repl.py](examples/ptk_repl.py) | REPL with history and completions | Building interactive shells |

### Tests (Exemplar Patterns)

| File | Purpose |
|------|---------|
| [tests/test_textual_pilot.py](tests/test_textual_pilot.py) | Canonical Pilot API test patterns |

## Textual Key Concepts

### App Lifecycle
- `compose()` - Build widget tree (yields widgets)
- `on_mount()` - Called when app starts
- `on_ready()` - Called when app is ready for input

### Containers
- `Horizontal` - Left-to-right layout
- `Vertical` - Top-to-bottom layout
- `Container` - Generic wrapper
- `Grid` - Grid layout with `grid-size`, `grid-columns`

### CSS Styling
```css
Screen { background: $surface; }
#sidebar { dock: left; width: 25; }
.highlight { background: $accent; }
Widget:focus { border: thick $success; }
```

### Messages
```python
class MyWidget(Static):
    class Changed(Message):
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def update_value(self, value: str) -> None:
        self.post_message(self.Changed(value))

# In App:
def on_my_widget_changed(self, message: MyWidget.Changed) -> None:
    self.log(f"Changed to: {message.value}")
```

### Key Bindings
```python
BINDINGS = [
    ("q", "quit", "Quit"),
    ("ctrl+s", "save", "Save"),
    ("ctrl+p", "command_palette", "Commands"),
]

def action_save(self) -> None:
    # Handle save
    pass
```

### Themes
Use built-in themes for professional styling out of the box:
```python
class MyApp(App):
    theme = "textual-dark"  # or "nord", "gruvbox", "tokyo-night"
```

Theme variables: `$primary`, `$surface`, `$text`, `$accent`, `$warning`, `$error`, `$success`

Shade variations: `$primary-lighten-1`, `$primary-darken-2`, etc.

See [references/themes-and-colors.md](references/themes-and-colors.md) for full details.

## Prompt Toolkit Key Concepts

### History
```python
from prompt_toolkit.history import FileHistory, InMemoryHistory

# Persistent across sessions
history = FileHistory("~/.myapp_history")

# In-memory only
history = InMemoryHistory()
```

### Completions
```python
from prompt_toolkit.completion import WordCompleter, NestedCompleter

# Simple word list
completer = WordCompleter(["red", "green", "blue"])

# Nested commands
completer = NestedCompleter.from_nested_dict({
    "show": {"status": None, "config": None},
    "set": {"verbose": {"on": None, "off": None}},
})
```

### Key Bindings
```python
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

@bindings.add("c-x")
def exit_handler(event):
    event.app.exit()

session = PromptSession(key_bindings=bindings)
```

### Validation
```python
from prompt_toolkit.validation import Validator

validator = Validator.from_callable(
    lambda text: text.isdigit(),
    error_message="Must be a number",
)
text = prompt("Number: ", validator=validator)
```

## Testing Quick Reference

### Textual Pilot API
```python
import pytest
from my_app import MyApp

@pytest.mark.asyncio
async def test_button_click():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.click("#my-button")
        assert app.query_one("#result").renderable == "Clicked!"
```

### Snapshot Testing
```python
def test_app_snapshot(snap_compare):
    assert snap_compare("path/to/app.py", press=["tab", "enter"])
```

## Integration Quick Reference

### MCP Server Access
```python
class MyApp(App):
    def __init__(self, mcp_client: Any) -> None:
        super().__init__()
        self.mcp_client = mcp_client

    async def load_data(self) -> None:
        result = await self.mcp_client.call_tool(
            "database_query",
            {"query": "SELECT * FROM items"}
        )
        # Update widgets with result
```

### Sub-Agent Delegation
```python
async def on_input_submitted(self, event: Input.Submitted) -> None:
    async for chunk in self.agent_client.run_task(event.value):
        self.query_one("#output", RichLog).write(chunk.content)
```

See [references/integration-patterns.md](references/integration-patterns.md) and [references/workflow-examples.md](references/workflow-examples.md) for complete examples.

## Version Requirements

- Python >= 3.12
- Textual >= 1.0.0
- prompt-toolkit >= 3.0.52
- pytest >= 9.0.1
- pytest-asyncio >= 1.2.0
- pytest-textual-snapshot >= 1.1.0

## Resources

- [Textual Documentation](https://textual.textualize.io)
- [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [Textual Testing Guide](https://textual.textualize.io/guide/testing/)
- [Textual Design Guide](https://textual.textualize.io/guide/design/) - Themes and variables
- [Textual Color Reference](https://textual.textualize.io/css_types/color/) - Color formats
- [Prompt Toolkit Documentation](https://python-prompt-toolkit.readthedocs.io)
- [Prompt Toolkit GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit)
