"""Prompt Toolkit REPL with History and Completions.

This is the canonical example of a REPL-style interface with:
- Persistent file-based history
- Nested command completion
- Auto-suggestions from history
- Custom styling

Use as reference for building interactive shells and REPLs.

Run: python ptk_repl.py
"""

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style


# Custom style
STYLE = Style.from_dict({
    "prompt": "ansicyan bold",
    "": "ansiwhite",
})

# Commands with nested completions
COMMANDS = NestedCompleter.from_nested_dict({
    "help": None,
    "quit": None,
    "exit": None,
    "show": {
        "status": None,
        "config": None,
        "history": None,
    },
    "set": {
        "verbose": {"on": None, "off": None},
        "debug": {"on": None, "off": None},
    },
    "run": {
        "sync": None,
        "build": None,
        "test": None,
    },
})


def create_session() -> PromptSession[str]:
    """Create a configured prompt session."""
    history_file = Path.home() / ".myrepl_history"

    return PromptSession(
        history=FileHistory(str(history_file)),
        completer=COMMANDS,
        auto_suggest=AutoSuggestFromHistory(),
        style=STYLE,
        vi_mode=False,  # Set True for Vi key bindings
    )


def handle_command(command: str) -> bool:
    """Handle a command. Returns False to exit."""
    command = command.strip().lower()

    if command in ("quit", "exit"):
        print("Goodbye!")
        return False

    if command == "help":
        print("Available commands:")
        print("  help              - Show this help")
        print("  quit/exit         - Exit the REPL")
        print("  show status       - Show current status")
        print("  show config       - Show configuration")
        print("  show history      - Show command history")
        print("  set verbose on/off- Set verbose mode")
        print("  set debug on/off  - Set debug mode")
        print("  run sync          - Run sync operation")
        print("  run build         - Run build operation")
        print("  run test          - Run tests")
        return True

    if command.startswith("show "):
        what = command[5:]
        print(f"Showing: {what}")
        return True

    if command.startswith("set "):
        print(f"Setting: {command[4:]}")
        return True

    if command.startswith("run "):
        print(f"Running: {command[4:]}")
        return True

    if command:
        print(f"Unknown command: {command}")
        print("Type 'help' for available commands")

    return True


def main() -> None:
    """Run the REPL."""
    session = create_session()

    print("Interactive REPL")
    print("Type 'help' for commands, 'quit' to exit")
    print("Tip: Press Tab for completions, Up/Down for history\n")

    while True:
        try:
            text = session.prompt(">>> ")
            if not handle_command(text):
                break
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
