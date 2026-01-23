# Textual Patterns

Detailed patterns for building Textual applications.

## App Lifecycle and Structure

### Basic App Structure

```python
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer

class MyApp(App):
    """Application docstring."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header()
        yield Static("Content")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted (before display)."""
        self.log("App mounted")

    def on_ready(self) -> None:
        """Called when app is ready for user input."""
        self.log("App ready")

if __name__ == "__main__":
    app = MyApp()
    app.run()
```

### Lifecycle Hooks

| Hook | When Called | Use For |
|------|-------------|---------|
| `compose()` | Building UI | Yielding widgets |
| `on_mount()` | After compose, before display | Initial setup, data loading |
| `on_ready()` | After display, ready for input | Focus management, timers |
| `on_unmount()` | App shutting down | Cleanup |

## Widget Tree and Containers

### Container Types

```python
from textual.containers import Horizontal, Vertical, Container, Grid
from textual.widgets import Static

class LayoutApp(App):
    def compose(self) -> ComposeResult:
        # Horizontal: left to right
        with Horizontal():
            yield Static("Left")
            yield Static("Right")

        # Vertical: top to bottom
        with Vertical():
            yield Static("Top")
            yield Static("Bottom")

        # Nested containers
        with Horizontal():
            yield Static("Sidebar", id="sidebar")
            with Vertical():
                yield Static("Main", id="main")
                yield Static("Footer", id="footer")
```

### Grid Layout

```python
from textual.containers import Grid

class GridApp(App):
    CSS = """
    Grid {
        grid-size: 3 2;  /* 3 columns, 2 rows */
        grid-columns: 1fr 2fr 1fr;
        grid-rows: auto 1fr;
        grid-gutter: 1;
    }
    #wide {
        column-span: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            yield Static("Cell 1")
            yield Static("Cell 2", id="wide")  # Spans 2 columns
            yield Static("Cell 3")
            yield Static("Cell 4")
            yield Static("Cell 5")
```

### Scrollable Containers

```python
from textual.containers import ScrollableContainer, VerticalScroll

class ScrollApp(App):
    CSS = """
    ScrollableContainer {
        height: 10;
        border: solid $primary;
    }
    """

    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            for i in range(50):
                yield Static(f"Line {i}")
```

## CSS and Styling

### CSS Syntax

```css
/* Type selector */
Static {
    color: $text;
}

/* ID selector */
#sidebar {
    width: 25;
    dock: left;
}

/* Class selector */
.highlight {
    background: $accent;
}

/* Pseudo-classes */
Button:hover {
    background: $primary-lighten-1;
}

Button:focus {
    border: thick $success;
}

Input:focus {
    border: tall $accent;
}
```

### Layout Properties

```css
/* Sizing */
#panel {
    width: 50%;        /* Percentage */
    width: 30;         /* Fixed cells */
    width: 1fr;        /* Fractional */
    width: auto;       /* Content-based */
    min-width: 20;
    max-width: 100;
}

/* Docking */
#sidebar {
    dock: left;        /* left, right, top, bottom */
}

/* Alignment */
Container {
    align: center middle;  /* horizontal vertical */
}

/* Margin and padding */
Static {
    margin: 1 2;       /* vertical horizontal */
    padding: 1;        /* all sides */
}
```

### Color Variables

```css
/* Built-in color variables */
Screen {
    background: $surface;
    color: $text;
}

.primary { color: $primary; }
.secondary { color: $secondary; }
.accent { color: $accent; }
.success { color: $success; }
.warning { color: $warning; }
.error { color: $error; }

/* Lighten/darken */
Button {
    background: $primary-lighten-2;
}
Button:hover {
    background: $primary-darken-1;
}
```

### Dynamic Styling

```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    widget = self.query_one("#target")

    # Modify styles programmatically
    widget.styles.background = "red"
    widget.styles.border = ("solid", "green")

    # Add/remove CSS classes
    widget.add_class("highlight")
    widget.remove_class("dimmed")
    widget.toggle_class("active")
```

## Messages and Event Handling

### Custom Messages

```python
from textual.message import Message
from textual.widgets import Static

class Counter(Static):
    """A counter widget that emits messages."""

    class Incremented(Message):
        """Sent when counter increments."""
        def __init__(self, value: int) -> None:
            self.value = value
            super().__init__()

    class Decremented(Message):
        """Sent when counter decrements."""
        def __init__(self, value: int) -> None:
            self.value = value
            super().__init__()

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def increment(self) -> None:
        self.count += 1
        self.update(str(self.count))
        self.post_message(self.Incremented(self.count))

    def decrement(self) -> None:
        self.count -= 1
        self.update(str(self.count))
        self.post_message(self.Decremented(self.count))
```

### Message Handlers

```python
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Counter(id="counter")
        yield Button("Increment", id="inc")

    # Handler naming: on_<widget_class>_<message_class>
    def on_counter_incremented(self, message: Counter.Incremented) -> None:
        self.log(f"Counter is now: {message.value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "inc":
            self.query_one(Counter).increment()
```

### Preventing Message Propagation

```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    # Handle the event
    self.do_something()
    # Stop propagation to parent widgets
    event.stop()
```

## Key Bindings and Actions

### Defining Bindings

```python
class MyApp(App):
    BINDINGS = [
        # (key, action, description)
        ("q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
        ("ctrl+shift+s", "save_as", "Save As"),
        ("f1", "help", "Help"),
        ("escape", "cancel", "Cancel"),

        # Binding without footer display
        Binding("ctrl+c", "copy", show=False),
    ]

    def action_save(self) -> None:
        """Handle save action."""
        self.notify("Saved!")

    def action_save_as(self) -> None:
        """Handle save as action."""
        # Show dialog, etc.
        pass
```

### Actions with Parameters

```python
BINDINGS = [
    ("1", "set_theme('dark')", "Dark Theme"),
    ("2", "set_theme('light')", "Light Theme"),
]

def action_set_theme(self, theme: str) -> None:
    self.theme = theme
```

### Widget-Level Bindings

```python
class MyInput(Input):
    BINDINGS = [
        ("ctrl+a", "select_all", "Select All"),
    ]

    def action_select_all(self) -> None:
        self.selection = (0, len(self.value))
```

## Essential Widgets

### Input Widget

```python
from textual.widgets import Input
from textual.suggester import SuggestFromList

class InputApp(App):
    def compose(self) -> ComposeResult:
        # Basic input
        yield Input(placeholder="Enter text...")

        # With validation
        yield Input(
            placeholder="Enter number",
            validators=[Number()],
        )

        # With suggestions
        yield Input(
            placeholder="Enter color",
            suggester=SuggestFromList(["red", "green", "blue"]),
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.log(f"Submitted: {event.value}")
        event.input.clear()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.log(f"Changed: {event.value}")
```

### TextArea Widget

```python
from textual.widgets import TextArea

class EditorApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea(
            text="Initial content",
            language="python",  # Syntax highlighting
            show_line_numbers=True,
        )

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.log(f"Content changed")
```

### Tree Widget

```python
from textual.widgets import Tree

class FileTreeApp(App):
    def compose(self) -> ComposeResult:
        tree = Tree("Project", id="file-tree")
        tree.root.expand()

        # Add nodes
        src = tree.root.add("src", expand=True)
        src.add_leaf("main.py")
        src.add_leaf("utils.py")

        tests = tree.root.add("tests")
        tests.add_leaf("test_main.py")

        yield tree

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        self.log(f"Selected: {event.node.label}")
```

### DataTable Widget

```python
from textual.widgets import DataTable

class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable(id="table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        # Add columns
        table.add_columns("Name", "Age", "City")

        # Add rows
        table.add_rows([
            ("Alice", 30, "NYC"),
            ("Bob", 25, "LA"),
            ("Charlie", 35, "Chicago"),
        ])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.log(f"Selected row: {event.row_key}")
```

### RichLog Widget

```python
from textual.widgets import RichLog

class LogApp(App):
    def compose(self) -> ComposeResult:
        yield RichLog(id="log", highlight=True, markup=True)

    def on_mount(self) -> None:
        log = self.query_one(RichLog)

        # Write text
        log.write("Plain text")

        # Write with markup
        log.write("[bold green]Success![/]")

        # Write code with highlighting
        log.write("def hello(): pass", highlight=True)
```

## Advanced Patterns

### Reactive Properties

```python
from textual.reactive import reactive

class StatusWidget(Static):
    status = reactive("idle")

    def watch_status(self, value: str) -> None:
        """Called when status changes."""
        self.update(f"Status: {value}")
        if value == "error":
            self.add_class("error")
        else:
            self.remove_class("error")
```

### Workers for Background Tasks

```python
from textual.worker import Worker, get_current_worker

class MyApp(App):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.run_worker(self.fetch_data())

    @work(exclusive=True)
    async def fetch_data(self) -> None:
        """Background task."""
        worker = get_current_worker()

        for i in range(10):
            if worker.is_cancelled:
                return
            await asyncio.sleep(0.1)
            self.call_from_thread(self.update_progress, i)

    def update_progress(self, value: int) -> None:
        self.query_one("#progress").update(str(value))
```

### Screens

```python
from textual.screen import Screen

class SettingsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Static("Settings")
        yield Button("Save", id="save")

class MyApp(App):
    SCREENS = {"settings": SettingsScreen}

    def action_open_settings(self) -> None:
        self.push_screen("settings")
```
