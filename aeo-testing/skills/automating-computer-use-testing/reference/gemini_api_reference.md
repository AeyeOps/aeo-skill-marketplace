# Gemini 2.5 Computer Use API Reference

Complete API reference for building Gemini computer-use automations.

## Model

**Model ID:** `gemini-2.5-computer-use-preview-10-2025`

This is the preview model for computer use capabilities. As of October 2025, this is the recommended model for browser automation.

## Authentication

```python
from google import genai

API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)
```

**Required:** Set `GOOGLE_API_KEY` environment variable with your Gemini API key.

## Tool Configuration

```python
from google.genai import types

tool = types.Tool(
    computer_use=types.ToolComputerUse(
        environment=types.Environment.ENVIRONMENT_BROWSER,
    )
)
```

This configures the Computer Use tool to operate in a browser environment.

## Generate Content

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=contents,  # List of Content objects
    config=types.GenerateContentConfig(
        tools=[tool],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )
)
```

**Parameters:**
- `model` - Model ID (required)
- `contents` - List of Content objects (conversation history)
- `config` - GenerateContentConfig with tools and thinking settings

**Returns:** Response object with candidates containing function calls

## Content Structure

```python
from google.genai.types import Content, Part

contents = [
    Content(
        role="user",
        parts=[
            Part(text="Natural-language goal or instruction"),
            Part.from_bytes(data=screenshot, mime_type="image/png"),
        ],
    ),
    Content(
        role="model",
        parts=[
            Part(function_call=...),  # Function call from model
        ],
    ),
    Content(
        role="user",
        parts=[
            Part(function_response=...),  # Response to function call
        ],
    ),
]
```

**Roles:**
- `user` - User messages (goals, screenshots, function responses)
- `model` - Model responses (function calls, text)

## Function Calls

When Gemini decides to take an action, it returns a function call in the response.

### Extracting Function Calls

```python
candidate = response.candidates[0]

for part in candidate.content.parts:
    if hasattr(part, "function_call"):
        function_call = part.function_call
        name = function_call.name
        args = function_call.args or {}
        # Execute function...
```

### Available Functions

#### 1. navigate

Navigate the browser to a URL.

**Args:**
- `url` (string, required) - URL to navigate to

**Example:**
```python
{
  "url": "https://example.com"
}
```

**Execution:**
```python
page.goto(url, wait_until="load")
```

#### 2. click_at

Click at normalized coordinates.

**Args:**
- `x` (int, required) - X coordinate (0-1000, normalized)
- `y` (int, required) - Y coordinate (0-1000, normalized)

**Example:**
```python
{
  "x": 500,  # Center of screen horizontally
  "y": 300
}
```

**Execution:**
```python
x_pixel = int(x / 1000 * screen_width)
y_pixel = int(y / 1000 * screen_height)
page.mouse.click(x_pixel, y_pixel)
```

**Important:** Coordinates are normalized to 0-1000. You MUST denormalize to viewport pixels before passing to Playwright.

#### 3. type_text_at

Click at coordinates, optionally clear field, type text, optionally press Enter.

**Args:**
- `x` (int, required) - X coordinate (0-1000)
- `y` (int, required) - Y coordinate (0-1000)
- `text` (string, required) - Text to type
- `press_enter` (bool, default: true) - Press Enter after typing
- `clear_before_typing` (bool, default: true) - Clear field before typing

**Example:**
```python
{
  "x": 500,
  "y": 400,
  "text": "john.doe@example.com",
  "press_enter": False,
  "clear_before_typing": True
}
```

**Execution:**
```python
x_pixel = int(x / 1000 * screen_width)
y_pixel = int(y / 1000 * screen_height)
page.mouse.click(x_pixel, y_pixel)

if clear_before_typing:
    # Ctrl+A (Windows/Linux) or Cmd+A (Mac)
    page.keyboard.press("Control+A")  # or "Meta+A" on Mac
    page.keyboard.press("Backspace")

page.keyboard.type(text)

if press_enter:
    page.keyboard.press("Enter")
```

#### 4. scroll_document

Scroll the entire page.

**Args:**
- `direction` (string, required) - "up" or "down"

**Example:**
```python
{
  "direction": "down"
}
```

**Execution:**
```python
delta = 800
if direction == "down":
    page.mouse.wheel(0, delta)
elif direction == "up":
    page.mouse.wheel(0, -delta)
```

#### 5. scroll_at

Move mouse to coordinates, then scroll.

**Args:**
- `x` (int, required) - X coordinate (0-1000)
- `y` (int, required) - Y coordinate (0-1000)
- `direction` (string, required) - "up" or "down"
- `pixels` (int, default: 600) - Scroll distance in pixels

**Example:**
```python
{
  "x": 500,
  "y": 500,
  "direction": "down",
  "pixels": 800
}
```

**Execution:**
```python
x_pixel = int(x / 1000 * screen_width)
y_pixel = int(y / 1000 * screen_height)
page.mouse.move(x_pixel, y_pixel)

dy = pixels if direction == "down" else -pixels
page.mouse.wheel(0, dy)
```

#### 6. key_combination

Press keyboard shortcut.

**Args:**
- `keys` (string or array, required) - Key combo like "Ctrl+A" or ["Ctrl", "A"]

**Example:**
```python
{
  "keys": "Ctrl+A"
}
# OR
{
  "keys": ["Ctrl", "A"]
}
```

**Execution:**
```python
# Normalize key combo
combo = normalize_key_combo(keys)  # e.g., "Ctrl+A" -> "Control+A"
page.keyboard.press(combo)
```

**Supported Keys:**
- Modifiers: Control, Shift, Alt, Meta (Cmd on Mac)
- Special: Enter, Escape, Tab, Backspace, Delete, Space
- Arrows: ArrowUp, ArrowDown, ArrowLeft, ArrowRight
- Single chars: A-Z, 0-9, etc.

#### 7. wait_5_seconds

Pause execution for 5 seconds.

**Args:** None

**Example:**
```python
{}
```

**Execution:**
```python
import time
time.sleep(5)
```

#### 8. go_back / go_forward

Browser navigation.

**Args:** None

**Example:**
```python
{}
```

**Execution:**
```python
page.go_back(wait_until="load")
# OR
page.go_forward(wait_until="load")
```

## Safety Decisions

Gemini may flag risky actions and request confirmation.

**Detection:**
```python
args = function_call.args
safety_decision = args.get("safety_decision")

if safety_decision:
    explanation = safety_decision.get("explanation")
    print(f"Safety warning: {explanation}")
    # Prompt operator for confirmation
```

**Confirmation Workflow:**
```python
def get_safety_confirmation(safety_decision):
    explanation = safety_decision.get("explanation")
    print(f"Safety service requires confirmation!")
    print(explanation)

    decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    if decision.lower().startswith("y"):
        return "CONTINUE"
    else:
        return "TERMINATE"

# In function execution:
if safety_decision:
    decision = get_safety_confirmation(safety_decision)
    if decision == "TERMINATE":
        # Stop automation
        return [("TERMINATE", {"terminated_by_user": True})]
    # Continue if CONTINUE
```

## Function Responses

After executing function calls, send responses back to Gemini.

```python
from google.genai.types import FunctionResponse

# Create function response
parts = []
for name, result in execution_results:
    parts.append(
        Part(
            function_response=FunctionResponse(
                name=name,
                response={"url": current_url, **result},
            )
        )
    )

# Add to conversation
contents.append(Content(role="user", parts=parts))
```

**Important:** Include screenshot after execution so Gemini can observe the new state.

```python
screenshot = page.screenshot(type="png")
parts.append(Part.from_bytes(data=screenshot, mime_type="image/png"))
```

## Token Management

### max_tokens and budget_tokens

```python
config = types.GenerateContentConfig(
    tools=[tool],
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        budget_tokens=10000,  # Max tokens for thinking
    ),
    max_tokens=16000,  # Max total tokens (must be > budget_tokens)
)
```

**Requirement:** `max_tokens` must be **strictly greater** than `budget_tokens`.

**Typical Values:**
- `budget_tokens`: 5000-10000
- `max_tokens`: 10000-16000

### Context Pruning

To prevent token overflow, prune old conversation turns:

```python
def prune_contents(contents, keep_turns=5):
    """Keep first message (system prompt) + recent N turns."""
    if len(contents) <= 1:
        return

    tail = contents[1:]  # Everything after first message
    max_tail = keep_turns * 2  # N user + N assistant messages

    if len(tail) <= max_tail:
        return

    # Keep only recent turns
    tail = tail[-max_tail:]
    contents[:] = [contents[0], *tail]
```

**Recommendation:** Keep recent 5 turns (10 messages: 5 user, 5 assistant).

## Complete Example

```python
from google import genai
from google.genai import types
from google.genai.types import Content, Part
from playwright.sync_api import sync_playwright

# Setup
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-computer-use-preview-10-2025"

tool = types.Tool(
    computer_use=types.ToolComputerUse(
        environment=types.Environment.ENVIRONMENT_BROWSER,
    )
)

config = types.GenerateContentConfig(
    tools=[tool],
    thinking_config=types.ThinkingConfig(include_thoughts=True),
)

# Launch browser
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page(viewport={"width": 1920, "height": 1080})
page.goto("http://localhost:5173")

# Initial screenshot
screenshot = page.screenshot(type="png")

# Conversation
contents = [
    Content(
        role="user",
        parts=[
            Part(text="Test the application thoroughly..."),
            Part.from_bytes(data=screenshot, mime_type="image/png"),
        ],
    )
]

# Agent loop
for turn in range(30):
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=config
    )

    candidate = response.candidates[0]
    contents.append(candidate.content)

    # Check for function calls
    has_calls = any(hasattr(p, "function_call") for p in candidate.content.parts)
    if not has_calls:
        # Done
        break

    # Execute function calls
    for part in candidate.content.parts:
        if hasattr(part, "function_call"):
            name = part.function_call.name
            args = part.function_call.args or {}
            # Execute function (navigate, click, type, etc.)
            # ...

    # Capture new screenshot and send response
    screenshot = page.screenshot(type="png")
    contents.append(
        Content(
            role="user",
            parts=[
                Part(function_response=FunctionResponse(name=name, response={})),
                Part.from_bytes(data=screenshot, mime_type="image/png"),
            ],
        )
    )

    # Prune context
    prune_contents(contents)

browser.close()
```

## Best Practices

1. **Always denormalize coordinates** (0-1000 → viewport pixels)
2. **Capture screenshots** after each action for Gemini to observe
3. **Implement safety confirmations** for risky actions
4. **Prune context** to prevent token overflow (keep recent 5 turns)
5. **Monitor token budgets** (`max_tokens` > `budget_tokens`)
6. **Add timeouts** to Playwright operations (avoid hangs)
7. **Handle errors gracefully** (wrap function calls in try/except)

## References

- Official docs: https://ai.google.dev/gemini-api/docs/computer-use
- Playwright docs: https://playwright.dev/python/
- Template implementation: See `../templates/harness_template.py` for complete pattern
