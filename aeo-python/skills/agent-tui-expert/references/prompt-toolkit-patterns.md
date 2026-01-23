# Prompt Toolkit Patterns

Detailed patterns for Python Prompt Toolkit.

## Basic Prompts and PromptSession

### Simple Prompt

```python
from prompt_toolkit import prompt

# One-shot prompt
text = prompt("Enter text: ")
print(f"You entered: {text}")
```

### PromptSession for Multiple Inputs

```python
from prompt_toolkit import PromptSession

# Session maintains state across prompts
session = PromptSession()

while True:
    try:
        text = session.prompt(">>> ")
        if text.strip() == "exit":
            break
        print(f"You said: {text}")
    except KeyboardInterrupt:
        continue
    except EOFError:
        break
```

### Async Prompts

```python
from prompt_toolkit import PromptSession

async def main():
    session = PromptSession()

    while True:
        text = await session.prompt_async(">>> ")
        if text == "quit":
            break
        print(f"Processing: {text}")
```

## History

### FileHistory (Persistent)

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

# History persists across program restarts
session = PromptSession(
    history=FileHistory("~/.myapp_history")
)

text = session.prompt(">>> ")
# Use Up/Down arrows to navigate history
```

### InMemoryHistory

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

# History only for current session
history = InMemoryHistory()

# Pre-populate history
history.append_string("previous command 1")
history.append_string("previous command 2")

session = PromptSession(history=history)
```

### History Search

```python
# Built-in: Ctrl+R for reverse search
# Type partial match, then Ctrl+R to cycle through matches

session = PromptSession(
    history=FileHistory(".history"),
    enable_history_search=True,  # Default is True
)
```

## Completions

### WordCompleter

```python
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# Simple word list
completer = WordCompleter([
    "help", "quit", "status", "version",
    "start", "stop", "restart",
])

text = prompt("Command: ", completer=completer)
```

### WordCompleter with Meta

```python
from prompt_toolkit.completion import WordCompleter

# Words with descriptions
completer = WordCompleter(
    words=["help", "quit", "status"],
    meta_dict={
        "help": "Show help information",
        "quit": "Exit the application",
        "status": "Show current status",
    },
    ignore_case=True,
)
```

### NestedCompleter

```python
from prompt_toolkit.completion import NestedCompleter

# Hierarchical command completion
completer = NestedCompleter.from_nested_dict({
    "show": {
        "version": None,
        "status": None,
        "config": {
            "all": None,
            "network": None,
            "security": None,
        },
    },
    "set": {
        "verbose": {"on": None, "off": None},
        "debug": {"on": None, "off": None},
    },
    "help": None,
    "quit": None,
})

text = prompt("cli> ", completer=completer)
```

### Custom Completer

```python
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

class FileCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor

        # Get files matching current input
        import os
        try:
            files = os.listdir(".")
            for name in files:
                if name.startswith(text.split()[-1] if text else ""):
                    yield Completion(
                        name,
                        start_position=-len(text.split()[-1]) if text else 0,
                        display_meta="directory" if os.path.isdir(name) else "file",
                    )
        except Exception:
            pass

text = prompt("File: ", completer=FileCompleter())
```

### FuzzyCompleter

```python
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter

# Wrap any completer for fuzzy matching
base_completer = WordCompleter(["authentication", "authorization", "account"])
completer = FuzzyCompleter(base_completer)

# Now "auth" matches "authentication" and "authorization"
text = prompt("> ", completer=completer)
```

### Complete While Typing

```python
session = PromptSession(
    completer=completer,
    complete_while_typing=True,  # Show completions as you type
)
```

## Key Bindings

### Custom Key Bindings

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

@bindings.add("c-t")  # Ctrl+T
def _(event):
    """Insert current time."""
    from datetime import datetime
    event.app.current_buffer.insert_text(
        datetime.now().strftime("%H:%M:%S")
    )

@bindings.add("c-l")  # Ctrl+L
def _(event):
    """Clear screen."""
    event.app.renderer.clear()

@bindings.add("c-x", "c-c")  # Ctrl+X Ctrl+C
def _(event):
    """Exit application."""
    event.app.exit()

session = PromptSession(key_bindings=bindings)
```

### Conditional Key Bindings

```python
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition

bindings = KeyBindings()

# Only active when buffer is empty
@Condition
def buffer_is_empty():
    return len(get_app().current_buffer.text) == 0

@bindings.add("c-d", filter=buffer_is_empty)
def _(event):
    """Exit on Ctrl+D when empty."""
    event.app.exit()

@bindings.add("c-d", filter=~buffer_is_empty)
def _(event):
    """Delete character when not empty."""
    event.app.current_buffer.delete()
```

### Vi Mode

```python
from prompt_toolkit import PromptSession

# Enable Vi key bindings
session = PromptSession(vi_mode=True)

# Or switch dynamically
from prompt_toolkit.enums import EditingMode
session = PromptSession(editing_mode=EditingMode.VI)
```

## Validation

### Validator Class

```python
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

class IntegerValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and not text.isdigit():
            raise ValidationError(
                message="Please enter a valid integer",
                cursor_position=len(text),
            )

number = prompt("Enter number: ", validator=IntegerValidator())
```

### Validator from Callable

```python
from prompt_toolkit.validation import Validator

# Simple callable validator
validator = Validator.from_callable(
    lambda text: text.isdigit() or text == "",
    error_message="Not a valid number",
    move_cursor_to_end=True,
)

text = prompt("Number: ", validator=validator)
```

### Validate While Typing

```python
session = PromptSession(
    validator=validator,
    validate_while_typing=True,  # Show errors as you type
)
```

## Multiline Input

### Basic Multiline

```python
from prompt_toolkit import prompt

# Meta+Enter or Escape+Enter to submit
text = prompt("Enter text (Meta+Enter to submit):\n", multiline=True)
```

### Continuation Prompt

```python
def continuation(width, line_number, is_soft_wrap):
    return "... "

text = prompt(
    ">>> ",
    multiline=True,
    prompt_continuation=continuation,
)
```

### Conditional Multiline

```python
from prompt_toolkit.filters import Condition

# Multiline only when line ends with backslash
@Condition
def multiline_filter():
    app = get_app()
    return app.current_buffer.text.endswith("\\")

session = PromptSession(
    multiline=multiline_filter,
)
```

## Auto-Suggestions

### From History

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

session = PromptSession(
    auto_suggest=AutoSuggestFromHistory(),
)

# Shows gray suggestion text from history
# Press Right arrow or Ctrl+E to accept
```

### Custom Auto-Suggest

```python
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

class CommandSuggester(AutoSuggest):
    def get_suggestion(self, buffer, document):
        text = document.text

        # Suggest based on prefix
        suggestions = {
            "hel": "p",
            "qui": "t",
            "sta": "tus",
        }

        for prefix, suffix in suggestions.items():
            if text == prefix:
                return Suggestion(suffix)
        return None

session = PromptSession(auto_suggest=CommandSuggester())
```

## Styling

### Custom Style

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

style = Style.from_dict({
    # Prompt
    "": "#ansiwhite",
    "prompt": "#ansicyan bold",

    # Completion menu
    "completion-menu.completion": "bg:#008888 #ffffff",
    "completion-menu.completion.current": "bg:#00aaaa #000000",

    # Scrollbar
    "scrollbar.background": "bg:#88aaaa",
    "scrollbar.button": "bg:#222222",
})

session = PromptSession(style=style)
text = session.prompt([("class:prompt", ">>> ")])
```

### Bottom Toolbar

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

def bottom_toolbar():
    return HTML("<b>F1</b> Help | <b>Ctrl+D</b> Exit")

session = PromptSession(bottom_toolbar=bottom_toolbar)
```

### Right Prompt

```python
from prompt_toolkit import PromptSession
from datetime import datetime

def get_rprompt():
    return datetime.now().strftime("%H:%M:%S")

session = PromptSession(rprompt=get_rprompt)
```

## Integration with Textual

### Using Suggester in Textual Input

```python
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.suggester import SuggestFromList

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter command...",
            suggester=SuggestFromList([
                "help", "quit", "status", "version",
            ]),
        )
```

### Custom Suggester

```python
from textual.suggester import Suggester

class CommandSuggester(Suggester):
    async def get_suggestion(self, value: str) -> str | None:
        commands = ["help", "quit", "status", "start", "stop"]
        for cmd in commands:
            if cmd.startswith(value) and cmd != value:
                return cmd
        return None

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Input(suggester=CommandSuggester())
```

### Sharing History Pattern

```python
# For Textual apps that need prompt_toolkit-style history:
# Store history in a shared location, load on startup

from pathlib import Path

HISTORY_FILE = Path.home() / ".myapp_history"

class MyApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.command_history: list[str] = []
        self._load_history()

    def _load_history(self) -> None:
        if HISTORY_FILE.exists():
            self.command_history = HISTORY_FILE.read_text().splitlines()

    def _save_history(self) -> None:
        HISTORY_FILE.write_text("\n".join(self.command_history[-1000:]))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.command_history.append(event.value)
        self._save_history()
```

## Common REPL Pattern

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter

def create_repl():
    completer = NestedCompleter.from_nested_dict({
        "help": None,
        "quit": None,
        "show": {"status": None, "config": None},
    })

    session = PromptSession(
        history=FileHistory(".repl_history"),
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        complete_while_typing=False,
    )

    print("Interactive REPL (type 'help' or 'quit')")

    while True:
        try:
            text = session.prompt(">>> ").strip()

            if not text:
                continue
            if text == "quit":
                print("Goodbye!")
                break
            if text == "help":
                print("Commands: help, quit, show status, show config")
                continue

            # Process command
            print(f"Executing: {text}")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    create_repl()
```
