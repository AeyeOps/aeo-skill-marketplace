#!/usr/bin/env python3
"""Gemini computer-use automation harness for web application QA testing.

This script automates QA testing of web applications using Gemini's
computer-use capabilities. It validates multi-panel layouts, selection-driven
architecture, interactive components, and visual fidelity against prototypes.

Usage:
    GOOGLE_API_KEY=... python harness_template.py

Relevant environment variables (all optional except `GOOGLE_API_KEY`):
    WEBAPP_URL                     – Base URL to open (default: http://localhost:5173)
    COMPUTER_USE_GOAL              – Natural-language QA instructions for the agent
    COMPUTER_USE_WIDTH             – Viewport width in pixels (default: 1920)
    COMPUTER_USE_HEIGHT            – Viewport height in pixels (default: 1080)
    COMPUTER_USE_TURNS             – Maximum reasoning turns (default: 30)
    COMPUTER_USE_HEADLESS          – "true"/"false" toggle for headless browser
    GOOGLE_COMPUTER_USE_MODEL      – Gemini model id (default: computer-use preview)
    COMPUTER_USE_EXCLUDED          – Comma-separated list of functions to disable

The script expects `playwright` browsers to be installed (`pip install playwright && playwright install --with-deps chromium`).
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from termcolor import cprint
except ModuleNotFoundError:  # pragma: no cover - best-effort fallback
    def cprint(message: str, color: str | None = None) -> None:
        """Fallback printing helper when termcolor isn't available."""
        print(message)

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from google import genai
from google.genai import types
from google.genai.types import Content, Part

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GOOGLE_API_KEY env var to your Gemini API key before running.")

MODEL_ID = os.getenv("GOOGLE_COMPUTER_USE_MODEL", "gemini-2.5-computer-use-preview-10-2025")

# Webapp typically runs on Vite default port 5173
SCREEN_WIDTH = int(os.getenv("COMPUTER_USE_WIDTH", "1920"))
SCREEN_HEIGHT = int(os.getenv("COMPUTER_USE_HEIGHT", "1080"))

SPA_URL = os.getenv("WEBAPP_URL", "http://localhost:5173")

DEFAULT_GOAL_PATH = Path(__file__).resolve().parent / "goal.txt"


def _load_goal_from_file() -> str | None:
    try:
        contents = DEFAULT_GOAL_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return contents or None


USER_GOAL = os.getenv("COMPUTER_USE_GOAL")
if USER_GOAL:
    USER_GOAL = USER_GOAL.strip()
else:
    USER_GOAL = _load_goal_from_file() or (
        "Open the web application at the configured localhost URL, "
        "verify all panels render correctly, test interactive components, "
        "select different items and observe panel updates, "
        "then provide a QA summary of what works and what's broken."
    )

EXCLUDED_FUNCTIONS = [
    fn.strip()
    for fn in os.getenv("COMPUTER_USE_EXCLUDED", "").split(",")
    if fn.strip()
]

TURN_LIMIT = int(os.getenv("COMPUTER_USE_TURNS", "30"))
HEADLESS = os.getenv("COMPUTER_USE_HEADLESS", "false").lower() in {"1", "true", "yes"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def denormalize_x(x: int, screen_width: int) -> int:
    """Gemini returns coordinates normalised to 0..999 – convert to pixels."""
    return int(x / 1000 * screen_width)


def denormalize_y(y: int, screen_height: int) -> int:
    return int(y / 1000 * screen_height)


KEY_ALIASES = {
  'ctrl': 'Control',
  'control': 'Control',
  'shift': 'Shift',
  'alt': 'Alt',
  'option': 'Alt',
  'meta': 'Meta',
  'cmd': 'Meta',
  'command': 'Meta',
  'escape': 'Escape',
  'esc': 'Escape',
  'enter': 'Enter',
  'return': 'Enter',
  'space': 'Space',
  'spacebar': 'Space',
  'tab': 'Tab',
  'backspace': 'Backspace',
  'delete': 'Delete',
  'arrowup': 'ArrowUp',
  'arrowdown': 'ArrowDown',
  'arrowleft': 'ArrowLeft',
  'arrowright': 'ArrowRight',
}


def normalize_key_token(token: str) -> str:
    token_lower = token.strip().lower()
    if not token_lower:
        return ''
    if token_lower in KEY_ALIASES:
        return KEY_ALIASES[token_lower]
    if len(token_lower) == 1:
        return token_lower.upper()
    return token_lower.capitalize()


def normalize_key_combo(value: str) -> str:
    separators = '+' if '+' in value else ('-' if '-' in value else None)
    if separators:
        parts = [normalize_key_token(part) for part in value.replace('-', '+').split('+')]
        parts = [part for part in parts if part]
        return '+'.join(parts) if parts else ''
    return normalize_key_token(value)


def prune_contents(contents: List[Content], keep_turns: int = 5) -> None:
    if len(contents) <= 1:
        return
    tail = contents[1:]
    max_tail = keep_turns * 2
    if len(tail) <= max_tail:
        return
    tail = tail[-max_tail:]
    contents[:] = [contents[0], *tail]


def get_safety_confirmation(safety_decision: Dict[str, Any]) -> str:
    """Prompt the operator when the model flags a potentially risky action."""
    cprint("Safety service requires explicit confirmation!", color="red")
    explanation = safety_decision.get("explanation")
    if explanation:
        print(explanation)

    decision = ""
    while decision.lower() not in {"y", "n", "ye", "yes", "no"}:
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    return "CONTINUE" if decision.lower().startswith("y") else "TERMINATE"


def execute_function_calls(
    candidate: types.Candidate,
    page: Page,
    screen_width: int,
    screen_height: int,
) -> List[Tuple[str, Dict[str, Any]]]:
    """Execute Gemini-generated computer-use function calls via Playwright."""
    results: List[Tuple[str, Dict[str, Any]]] = []
    function_calls: List[types.FunctionCall] = []

    for part in candidate.content.parts:
        if getattr(part, "function_call", None):
            function_calls.append(part.function_call)

    for function_call in function_calls:
        name = function_call.name
        args = function_call.args or {}
        print(f" -> Executing: {name} {args}")

        extra_fields: Dict[str, Any] = {}

        try:
            safety_decision = args.get("safety_decision")
            if safety_decision:
                decision = get_safety_confirmation(safety_decision)
                if decision == "TERMINATE":
                    print("Terminating agent loop due to user choice.")
                    return [("TERMINATE", {"terminated_by_user": True})]
                extra_fields["safety_acknowledgement"] = "true"

            if name == "open_web_browser":
                # Browser already managed via Playwright context
                pass

            elif name == "navigate":
                url = args.get("url")
                if not url:
                    raise ValueError("navigate requires 'url'")
                page.goto(url, wait_until="load")

            elif name == "click_at":
                x = denormalize_x(args["x"], screen_width)
                y = denormalize_y(args["y"], screen_height)
                page.mouse.click(x, y)
                page.wait_for_load_state("load", timeout=5000)

            elif name == "type_text_at":
                x = denormalize_x(args["x"], screen_width)
                y = denormalize_y(args["y"], screen_height)
                text = args.get("text", "")
                press_enter = bool(args.get("press_enter", True))
                clear_before = bool(args.get("clear_before_typing", True))

                page.mouse.click(x, y)
                if clear_before:
                    if os.name == "nt":
                        page.keyboard.press("Control+A")
                    else:
                        page.keyboard.press("Meta+A")
                    page.keyboard.press("Backspace")

                page.keyboard.type(text)
                if press_enter:
                    page.keyboard.press("Enter")

            elif name == "wait_5_seconds":
                time.sleep(5)

            elif name == "go_back":
                page.go_back(wait_until="load")

            elif name == "go_forward":
                page.go_forward(wait_until="load")

            elif name == "scroll_document":
                direction = args.get("direction", "down")
                delta = 800 if direction in {"down", "up"} else 0
                if direction == "down":
                    page.mouse.wheel(0, delta)
                elif direction == "up":
                    page.mouse.wheel(0, -delta)

            elif name == "scroll_at":
                direction = args.get("direction", "down")
                distance = int(args.get("pixels", 600))
                x = denormalize_x(args.get("x", 500), screen_width)
                y = denormalize_y(args.get("y", 500), screen_height)
                page.mouse.move(x, y)
                dy = distance if direction == "down" else -distance
                page.mouse.wheel(0, dy)

            elif name == "key_combination":
                keys_arg = args.get("keys")
                if not keys_arg:
                    raise ValueError("key_combination requires 'keys'")
                if isinstance(keys_arg, str):
                    combo = normalize_key_combo(keys_arg)
                    if combo:
                        page.keyboard.press(combo)
                else:
                    for token in keys_arg:
                        combo = normalize_key_combo(str(token))
                        if combo:
                            page.keyboard.press(combo)

            else:
                print(f"Warning: Unimplemented function {name}")

            page.wait_for_timeout(500)
            results.append((name, extra_fields or {}))

        except Exception as exc:  # pragma: no cover - runtime safeguard
            print(f"Error executing {name}: {exc}")
            results.append((name, {"error": str(exc), **extra_fields}))

    print(f"[gemini] processed {len(function_calls)} calls, responses {len(results)}")
    return results


def make_function_response_parts(page: Page, exec_results: List[Tuple[str, Dict[str, Any]]]) -> List[Part]:
    """Bundle post-action screenshots for the model to observe the new state."""
    current_url = page.url
    parts: List[Part] = []

    for index, (name, result) in enumerate(exec_results):
        payload = {"url": current_url, **result}

        parts.append(
            Part(
                function_response=types.FunctionResponse(
                    name=name,
                    response=payload,
                )
            )
        )

    return parts


# ---------------------------------------------------------------------------
# Main agent loop
# ---------------------------------------------------------------------------
def main() -> None:
    client = genai.Client(api_key=API_KEY)

    if EXCLUDED_FUNCTIONS:
        print(
            "[gemini] Warning: EXCLUDED_FUNCTIONS not supported by current google-genai SDK "
            "version; ignoring values: "
            + ", ".join(EXCLUDED_FUNCTIONS)
        )

    tool = types.Tool(
        computer_use=types.ToolComputerUse(
            environment=types.Environment.ENVIRONMENT_BROWSER,
        )
    )

    config = types.GenerateContentConfig(
        tools=[tool],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )

    print("Launching Chromium for Web Application QA...")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=HEADLESS)
    context = browser.new_context(viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT})
    page = context.new_page()

    try:
        try:
            print(f"Navigating to web application at {SPA_URL}...")
            page.goto(SPA_URL, wait_until="load")
        except PlaywrightError as exc:
            print(
                f"[gemini] Failed to reach web application at {SPA_URL}.\n"
                "Start the dev server (e.g., `npm run dev`) or set WEBAPP_URL, then rerun."
            )
            raise SystemExit(1) from exc

        initial_screenshot = page.screenshot(type="png")

        contents: List[Content] = [
            Content(
                role="user",
                parts=[
                    Part(text=USER_GOAL),
                    Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
                ],
            )
        ]

        for turn in range(TURN_LIMIT):
            print(f"\n--- QA Turn {turn + 1} ---")
            response = client.models.generate_content(model=MODEL_ID, contents=contents, config=config)
            candidate = response.candidates[0]
            contents.append(candidate.content)

            has_calls = any(getattr(part, "function_call", None) for part in candidate.content.parts)
            if not has_calls:
                text_out = " ".join(
                    part.text for part in candidate.content.parts if getattr(part, "text", None)
                )
                print("QA Agent finished:", text_out)
                break

            exec_results = execute_function_calls(candidate, page, SCREEN_WIDTH, SCREEN_HEIGHT)
            if any(name == "TERMINATE" for name, _ in exec_results):
                break

            response_parts = make_function_response_parts(page, exec_results)
            contents.append(Content(role="user", parts=response_parts))
            prune_contents(contents)

    finally:
        print("\nClosing browser...")
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()
