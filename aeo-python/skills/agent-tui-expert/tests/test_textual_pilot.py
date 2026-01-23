"""Canonical Textual Pilot API Tests.

This is the exemplar test file showing how to test Textual apps using:
- run_test() async context manager
- Pilot API (press, click, hover)
- Widget queries and assertions

Use as reference for testing any Textual application.

Run: pytest test_textual_pilot.py -v
"""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static


# --- App Under Test ---


class CounterApp(App):
    """Simple counter app for testing."""

    CSS = """
    #count {
        text-align: center;
        height: 3;
        border: solid $primary;
    }
    """

    BINDINGS = [
        ("i", "increment", "Increment"),
        ("d", "decrement", "Decrement"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def compose(self) -> ComposeResult:
        yield Static(str(self.count), id="count")
        yield Button("Increment", id="increment")
        yield Button("Decrement", id="decrement")
        yield Input(placeholder="Enter value...", id="input")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "increment":
            self.action_increment()
        elif event.button.id == "decrement":
            self.action_decrement()

    def action_increment(self) -> None:
        self.count += 1
        self.query_one("#count", Static).update(str(self.count))

    def action_decrement(self) -> None:
        self.count -= 1
        self.query_one("#count", Static).update(str(self.count))


# --- Tests ---


@pytest.mark.asyncio
async def test_initial_state() -> None:
    """Test app starts with count at 0."""
    app = CounterApp()
    async with app.run_test() as pilot:
        count_widget = app.query_one("#count", Static)
        assert count_widget.content == "0"


@pytest.mark.asyncio
async def test_increment_button() -> None:
    """Test clicking increment button increases count."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Click increment button
        await pilot.click("#increment")

        # Verify count increased
        count_widget = app.query_one("#count", Static)
        assert count_widget.content == "1"


@pytest.mark.asyncio
async def test_decrement_button() -> None:
    """Test clicking decrement button decreases count."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Click decrement button
        await pilot.click("#decrement")

        # Verify count decreased
        count_widget = app.query_one("#count", Static)
        assert count_widget.content == "-1"


@pytest.mark.asyncio
async def test_multiple_actions() -> None:
    """Test multiple actions via key bindings (more reliable than rapid clicks)."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Key presses are more reliable than rapid button clicks
        await pilot.press("i")  # Increment
        assert app.count == 1

        await pilot.press("i")  # Increment
        assert app.count == 2

        await pilot.press("i")  # Increment
        assert app.count == 3

        await pilot.press("d")  # Decrement
        assert app.count == 2

        # Verify widget content matches
        count_widget = app.query_one("#count", Static)
        assert count_widget.content == "2"


@pytest.mark.asyncio
async def test_keyboard_input() -> None:
    """Test typing into input widget."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Focus the input
        await pilot.click("#input")

        # Type text
        await pilot.press("h", "e", "l", "l", "o")

        # Verify input value
        input_widget = app.query_one("#input", Input)
        assert input_widget.value == "hello"


@pytest.mark.asyncio
async def test_input_submit() -> None:
    """Test submitting input with Enter."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Focus and type
        await pilot.click("#input")
        await pilot.press("t", "e", "s", "t")

        # Submit with Enter
        await pilot.press("enter")

        # Input should still have the value
        input_widget = app.query_one("#input", Input)
        assert input_widget.value == "test"


@pytest.mark.asyncio
async def test_custom_terminal_size() -> None:
    """Test app with custom terminal dimensions."""
    app = CounterApp()
    async with app.run_test(size=(120, 40)) as pilot:
        # App should render in larger terminal
        assert app.screen.size.width == 120
        assert app.screen.size.height == 40


@pytest.mark.asyncio
async def test_query_multiple_widgets() -> None:
    """Test querying multiple widgets."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Query all buttons
        buttons = app.query(Button)
        assert len(buttons) == 2

        # Verify button IDs
        button_ids = [b.id for b in buttons]
        assert "increment" in button_ids
        assert "decrement" in button_ids


@pytest.mark.asyncio
async def test_app_state_after_actions() -> None:
    """Test app state tracking."""
    app = CounterApp()
    async with app.run_test() as pilot:
        # Initial state
        assert app.count == 0

        # After increment
        await pilot.click("#increment")
        assert app.count == 1

        # After decrement
        await pilot.click("#decrement")
        assert app.count == 0
