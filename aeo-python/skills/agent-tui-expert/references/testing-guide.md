# Testing Guide

Patterns for testing TUI applications.

## Textual Pilot API

### Basic Test Structure

```python
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Click Me", id="btn")
        yield Static("", id="result")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one("#result", Static).update("Clicked!")

@pytest.mark.asyncio
async def test_button_click():
    """Test that clicking button updates result."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Click the button
        await pilot.click("#btn")

        # Verify result
        result = app.query_one("#result", Static)
        assert result.content == "Clicked!"
```

### pytest Configuration

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

Or use decorator on each test:

```python
@pytest.mark.asyncio
async def test_something():
    ...
```

### run_test() Options

```python
async with app.run_test(size=(100, 50)) as pilot:
    # Test with specific terminal size
    pass

async with app.run_test(size=None) as pilot:
    # Use default 80x24
    pass
```

## Pilot API Methods

### Pressing Keys

```python
@pytest.mark.asyncio
async def test_keyboard_input():
    app = MyApp()
    async with app.run_test() as pilot:
        # Single key
        await pilot.press("a")

        # Multiple keys in sequence
        await pilot.press("h", "e", "l", "l", "o")

        # Special keys
        await pilot.press("enter")
        await pilot.press("tab")
        await pilot.press("escape")
        await pilot.press("backspace")
        await pilot.press("delete")

        # Arrow keys
        await pilot.press("up")
        await pilot.press("down")
        await pilot.press("left")
        await pilot.press("right")

        # Modifier combinations
        await pilot.press("ctrl+c")
        await pilot.press("ctrl+s")
        await pilot.press("ctrl+shift+s")
        await pilot.press("alt+f")

        # Function keys
        await pilot.press("f1")
        await pilot.press("f12")
```

### Clicking Widgets

```python
@pytest.mark.asyncio
async def test_clicking():
    app = MyApp()
    async with app.run_test() as pilot:
        # Click by CSS selector
        await pilot.click("#my-button")
        await pilot.click(".submit-btn")
        await pilot.click("Button")

        # Click with offset from widget center
        await pilot.click("#widget", offset=(5, 2))

        # Double-click
        await pilot.click("#item", times=2)

        # Click with modifiers
        await pilot.click("#item", control=True)
        await pilot.click("#item", shift=True)
        await pilot.click("#item", alt=True)
```

### Hovering

```python
@pytest.mark.asyncio
async def test_hover():
    app = MyApp()
    async with app.run_test() as pilot:
        # Hover over widget
        await pilot.hover("#tooltip-trigger")

        # Check tooltip appeared
        tooltip = app.query_one("#tooltip")
        assert tooltip.display is True
```

### Pausing

```python
@pytest.mark.asyncio
async def test_with_pause():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.click("#start")

        # Wait for animations/messages to process
        await pilot.pause()

        # Or with specific delay
        await pilot.pause(delay=0.5)
```

## Querying Widgets

### query_one()

```python
@pytest.mark.asyncio
async def test_query_one():
    app = MyApp()
    async with app.run_test() as pilot:
        # Query by ID
        widget = app.query_one("#my-widget")

        # Query by ID with type
        button = app.query_one("#submit", Button)

        # Query by type
        static = app.query_one(Static)

        # Query by CSS class
        widget = app.query_one(".highlight")
```

### query()

```python
@pytest.mark.asyncio
async def test_query_multiple():
    app = MyApp()
    async with app.run_test() as pilot:
        # Get all buttons
        buttons = app.query("Button")
        assert len(buttons) == 3

        # Get all with class
        items = app.query(".item")

        # Iterate
        for button in app.query(Button):
            assert button.disabled is False
```

## Assertions

### Widget State

```python
@pytest.mark.asyncio
async def test_widget_state():
    app = MyApp()
    async with app.run_test() as pilot:
        widget = app.query_one("#target")

        # Content
        assert widget.content == "Expected Text"

        # Visibility
        assert widget.display is True
        assert widget.visible is True

        # Focus
        assert widget.has_focus is True

        # CSS classes
        assert widget.has_class("active")
        assert not widget.has_class("disabled")

        # Styles
        assert widget.styles.background == Color.parse("red")
```

### Input Widget

```python
@pytest.mark.asyncio
async def test_input():
    app = MyApp()
    async with app.run_test() as pilot:
        input_widget = app.query_one(Input)

        # Type into input
        await pilot.click(Input)
        await pilot.press("h", "e", "l", "l", "o")

        # Check value
        assert input_widget.value == "hello"

        # Submit
        await pilot.press("enter")
```

### App State

```python
@pytest.mark.asyncio
async def test_app_state():
    app = MyApp()
    async with app.run_test() as pilot:
        # Check screen
        assert app.screen.id == "main"

        # Check theme (toggle_dark switches between light/dark themes)
        initial_theme = app.theme
        await pilot.press("d")  # Toggle dark (built-in action)
        assert app.theme != initial_theme

        # Check custom app attributes
        assert app.counter == 0
        await pilot.click("#increment")
        assert app.counter == 1
```

## Snapshot Testing

### Setup

```bash
pip install pytest-textual-snapshot
```

### Basic Snapshot

```python
def test_app_appearance(snap_compare):
    """Test app renders correctly."""
    assert snap_compare("path/to/app.py")
```

### Snapshot with Interactions

```python
def test_after_click(snap_compare):
    """Test appearance after clicking."""
    assert snap_compare(
        "path/to/app.py",
        press=["tab", "enter"],
    )
```

### Snapshot with Custom Size

```python
def test_small_terminal(snap_compare):
    """Test appearance in small terminal."""
    assert snap_compare(
        "path/to/app.py",
        terminal_size=(40, 20),
    )
```

### Snapshot with Setup

```python
def test_with_setup(snap_compare):
    """Test with custom setup."""
    async def run_before(pilot):
        await pilot.click("#toggle")
        await pilot.pause()

    assert snap_compare("path/to/app.py", run_before=run_before)
```

### Running Snapshots

```bash
# First run generates snapshots (tests fail)
pytest

# Review snapshots in generated HTML report

# Accept snapshots
pytest --snapshot-update
```

## Testing Prompt Toolkit

### Testing Completers

```python
import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter

def test_word_completer():
    """Test word completer returns expected completions."""
    completer = WordCompleter(["help", "hello", "quit"])

    # Create document with cursor at end
    doc = Document("hel", cursor_position=3)

    # Get completions
    completions = list(completer.get_completions(doc, None))

    # Verify
    assert len(completions) == 2
    texts = [c.text for c in completions]
    assert "help" in texts
    assert "hello" in texts
```

### Testing Custom Completers

```python
from my_app import MyCustomCompleter

def test_custom_completer():
    """Test custom completer logic."""
    completer = MyCustomCompleter()

    # Test empty input
    doc = Document("", cursor_position=0)
    completions = list(completer.get_completions(doc, None))
    assert len(completions) > 0

    # Test partial match
    doc = Document("sta", cursor_position=3)
    completions = list(completer.get_completions(doc, None))
    texts = [c.text for c in completions]
    assert "status" in texts
    assert "start" in texts
```

### Testing History

```python
from prompt_toolkit.history import InMemoryHistory

def test_history():
    """Test history operations."""
    history = InMemoryHistory()

    # Add entries
    history.append_string("command 1")
    history.append_string("command 2")
    history.append_string("command 3")

    # Get all strings
    strings = history.get_strings()
    assert len(strings) == 3
    assert strings[-1] == "command 3"
```

### Testing Validators

```python
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError
from my_app import MyValidator

def test_validator_accepts_valid():
    """Test validator accepts valid input."""
    validator = MyValidator()
    doc = Document("valid input")

    # Should not raise
    validator.validate(doc)

def test_validator_rejects_invalid():
    """Test validator rejects invalid input."""
    validator = MyValidator()
    doc = Document("invalid!")

    with pytest.raises(ValidationError) as exc_info:
        validator.validate(doc)

    assert "error message" in str(exc_info.value)
```

## Test Organization

### Recommended Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_app.py           # Main app tests
├── test_widgets.py       # Custom widget tests
├── test_commands.py      # Command handler tests
├── test_completers.py    # Completer tests
└── snapshots/            # Generated by pytest-textual-snapshot
```

### conftest.py Patterns

```python
import pytest
from my_app import MyApp

@pytest.fixture
def app():
    """Create app instance."""
    return MyApp()

@pytest.fixture
def app_with_data():
    """Create app with test data."""
    app = MyApp()
    app.load_test_data()
    return app

@pytest.fixture
async def running_app():
    """Create and run app."""
    app = MyApp()
    async with app.run_test() as pilot:
        yield app, pilot
```

### Using Fixtures

```python
@pytest.mark.asyncio
async def test_with_fixture(running_app):
    """Test using fixture."""
    app, pilot = running_app

    await pilot.click("#button")
    assert app.query_one("#result").content == "Done"
```

## Common Test Patterns

### Testing Screen Navigation

```python
@pytest.mark.asyncio
async def test_screen_push():
    app = MyApp()
    async with app.run_test() as pilot:
        # Start on main screen
        assert app.screen.id == "main"

        # Navigate to settings
        await pilot.press("ctrl+comma")
        assert app.screen.id == "settings"

        # Go back
        await pilot.press("escape")
        assert app.screen.id == "main"
```

### Testing Form Submission

```python
@pytest.mark.asyncio
async def test_form_submission():
    app = MyApp()
    async with app.run_test() as pilot:
        # Fill form
        await pilot.click("#name-input")
        await pilot.press(*"John Doe")

        await pilot.click("#email-input")
        await pilot.press(*"john@example.com")

        # Submit
        await pilot.click("#submit-btn")

        # Verify
        assert app.form_submitted is True
        assert app.form_data["name"] == "John Doe"
```

### Testing Error States

```python
@pytest.mark.asyncio
async def test_validation_error():
    app = MyApp()
    async with app.run_test() as pilot:
        # Enter invalid data
        await pilot.click("#number-input")
        await pilot.press("a", "b", "c")
        await pilot.press("enter")

        # Check error displayed
        error = app.query_one("#error-message")
        assert "must be a number" in error.content.lower()
```
