# Best Practices for Gemini Computer-Use Automation

Comprehensive guide for creating robust, maintainable computer-use automations.

## Goal File Best Practices

### 1. Be Specific and Actionable

**Good:**
```
Click the collapse icon (chevron pointing down) on the Investigation Explorer panel header.
```

**Bad:**
```
Click something to collapse.
```

**Why:** Specific instructions help Gemini locate the correct UI element. Include visual details (icon shape, color) and location context (panel name, header).

### 2. Include Verification Steps

**Good:**
```
Verify the panel collapses smoothly with a 300ms animation, the chevron rotates 180 degrees to point up, and the panel content becomes hidden.
```

**Bad:**
```
Collapse the panel.
```

**Why:** Verification ensures automation can detect if action succeeded. Observable outcomes (animation duration, icon rotation, hidden content) provide clear success/failure indicators.

### 3. Define Measurable Success Criteria

**Good:**
```
Success Criteria:
- All 6 panels render correctly (Explorer, Resources, Canvas, Properties, Intelligence, Console)
- Panel collapse animation completes in 250-350ms
- No console errors or warnings visible
- Layout matches christina_workspace_1.html visual benchmark
```

**Bad:**
```
Success Criteria:
- App works
- Looks good
```

**Why:** Measurable criteria enable objective pass/fail determination. Quantitative metrics (6 panels, 250-350ms) and comparisons (visual benchmark) provide clear targets.

### 4. Structure Reporting Consistently

**Always Include:**
- **What worked**: Features that behave as expected
- **What broke**: Bugs, console errors, visual glitches, broken functionality
- **UX notes**: Friction points, confusing interactions, suggestions

**Optional:**
- Visual comparison (similarity scores, difference highlights)
- Performance metrics (load time, animation duration)
- Accessibility notes (keyboard navigation, screen reader compatibility)

### 5. Scope Appropriately

**Recommendation:** 5-10 test scenarios per goal file

**Why:**
- Keeps automation runtime <10 minutes
- Maintains focus (single feature or workflow)
- Easier to debug failures
- Clearer reporting

**If you have 20+ scenarios:**
- Split into multiple goal files (e.g., goal_login.txt, goal_checkout.txt)
- Run separately and combine results

### 6. Number Steps Sequentially

**Good:**
```
1. Navigate to http://localhost:5173
2. Verify homepage loads
3. Click "Products" in navigation
4. Verify products page displays
```

**Bad:**
```
- Navigate to app
- Check if page loaded
- Go to products
- Make sure products show up
```

**Why:** Numbered steps create clear sequence. Helps Gemini understand dependencies (step 4 depends on step 3).

### 7. Add Context and Purpose

**Good:**
```
You are a QA engineer testing the Christina Investigation Workspace, a professional support intelligence platform for enterprise analysts.

Your goal is to validate the Investigation-Centric 4-panel workspace implementation matches the design specification.
```

**Bad:**
```
You test stuff.

Test the app.
```

**Why:** Context helps Gemini understand what the application does and why features matter. Better decisions about what to prioritize and how to report findings.

## Harness Script Best Practices

### 1. Coordinate Normalization

Gemini returns coordinates in range 0-1000 (normalized). You MUST denormalize to viewport pixels.

**Correct:**
```python
def denormalize_x(x: int, screen_width: int) -> int:
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    return int(y / 1000 * screen_height)

# In function execution:
x_pixel = denormalize_x(args["x"], SCREEN_WIDTH)
y_pixel = denormalize_y(args["y"], SCREEN_HEIGHT)
page.mouse.click(x_pixel, y_pixel)
```

**Incorrect:**
```python
# Don't do this!
page.mouse.click(args["x"], args["y"])  # Wrong: using normalized coords directly
```

### 2. Timeout Management

Add timeouts to prevent hanging on slow operations.

**Recommended:**
```python
page.goto(url, wait_until="load", timeout=10000)  # 10 second timeout
page.wait_for_load_state("load", timeout=5000)   # 5 second timeout
page.mouse.click(x, y)
page.wait_for_timeout(500)  # Small delay after click
```

**Adjust based on app:**
- Fast apps: 3000ms (3 seconds)
- Average apps: 5000ms (5 seconds)
- Slow apps: 10000ms (10 seconds)

### 3. Safety Confirmation Workflow

Always implement explicit confirmation for risky actions.

**Required:**
```python
def get_safety_confirmation(safety_decision: dict) -> str:
    """Prompt operator when model flags risky action."""
    explanation = safety_decision.get("explanation", "Unknown risk")
    print(f"\nSafety warning: {explanation}")

    decision = ""
    while decision.lower() not in {"y", "n", "yes", "no"}:
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    return "CONTINUE" if decision.lower().startswith("y") else "TERMINATE"

# In function execution:
safety_decision = args.get("safety_decision")
if safety_decision:
    decision = get_safety_confirmation(safety_decision)
    if decision == "TERMINATE":
        return [("TERMINATE", {"terminated_by_user": True})]
```

**Never:** Auto-approve risky actions without operator confirmation.

### 4. Context Pruning

Prevent token overflow by pruning old conversation turns.

**Recommended:**
```python
def prune_contents(contents: List[Content], keep_turns: int = 5) -> None:
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

# Call after each turn:
prune_contents(contents, keep_turns=5)
```

**Why:** Keeps recent context (5 turns = 10 messages) while preventing token overflow. System prompt always preserved.

### 5. Error Handling

Wrap function calls in try/except to handle failures gracefully.

**Recommended:**
```python
results = []

for function_call in function_calls:
    name = function_call.name
    args = function_call.args or {}

    try:
        # Execute function
        if name == "click_at":
            x = denormalize_x(args["x"], SCREEN_WIDTH)
            y = denormalize_y(args["y"], SCREEN_HEIGHT)
            page.mouse.click(x, y)

        page.wait_for_timeout(500)
        results.append((name, {}))

    except Exception as exc:
        print(f"Error executing {name}: {exc}")
        results.append((name, {"error": str(exc)}))

return results
```

**Benefits:**
- Automation doesn't crash on single failure
- Errors logged for debugging
- Model can see error and adapt

## Token Management Best Practices

### 1. Monitor Budget Relationship

**Rule:** `max_tokens` must be strictly greater than `budget_tokens`

**Recommended Values:**
```python
config = types.GenerateContentConfig(
    tools=[tool],
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        budget_tokens=10000,  # Thinking budget
    ),
    max_tokens=16000,  # Total budget (must be > 10000)
)
```

**If you see errors:**
- Increase `max_tokens` (e.g., 20000)
- OR decrease `budget_tokens` (e.g., 8000)

### 2. Track Token Usage

Monitor usage per turn to predict when pruning is needed.

**Recommended:**
```python
# After each response
token_count = len(str(response))  # Rough estimate
print(f"Turn {turn}: ~{token_count} chars")

if token_count > 10000:
    print("Warning: High token usage, consider pruning more aggressively")
```

### 3. Adjust Based on Complexity

**Simple tasks** (form filling, navigation):
- `budget_tokens`: 5000
- `keep_turns`: 3

**Complex tasks** (multi-step workflows, debugging):
- `budget_tokens`: 10000
- `keep_turns`: 5

**Very complex tasks** (visual regression, comprehensive testing):
- `budget_tokens`: 15000
- `keep_turns`: 7

## Visual Verification Best Practices

### 1. Capture Screenshots After Each Action

**Recommended:**
```python
# Execute function call
page.mouse.click(x, y)
page.wait_for_timeout(500)  # Wait for UI to update

# Capture screenshot
screenshot = page.screenshot(type="png")

# Bundle with function response
parts.append(Part.from_bytes(data=screenshot, mime_type="image/png"))
```

**Why:** Screenshots enable Gemini to observe the new state and self-correct if action didn't work as expected.

### 2. Balance Fidelity with Performance

**High fidelity** (slow but accurate):
```python
screenshot = page.screenshot(type="png", full_page=True)  # Full page
```

**Standard** (recommended):
```python
screenshot = page.screenshot(type="png")  # Viewport only
```

**Low fidelity** (fast but compressed):
```python
screenshot = page.screenshot(type="jpeg", quality=70)  # JPEG with compression
```

**Recommendation:** Use standard (PNG viewport) for most automations.

### 3. Wait for UI to Stabilize

Before capturing screenshot, wait for:
- Images to load
- Animations to complete
- Fonts to render

**Recommended:**
```python
page.mouse.click(x, y)
page.wait_for_load_state("networkidle", timeout=3000)  # Wait for network idle
page.wait_for_timeout(500)  # Additional buffer
screenshot = page.screenshot(type="png")
```

## Performance Optimization

### 1. Use Headless Mode for CI/CD

**Development:**
```python
browser = playwright.chromium.launch(headless=False)  # See browser
```

**CI/CD:**
```python
browser = playwright.chromium.launch(headless=True)  # Faster
```

### 2. Limit Turn Count

Set reasonable turn limit based on automation complexity.

**Recommended:**
- Simple: 10-15 turns
- Medium: 20-30 turns
- Complex: 30-50 turns

**If automation doesn't finish:**
- Review goal file (too vague? missing steps?)
- Check for errors (console errors blocking progress?)
- Increase turn limit cautiously (don't go >100)

### 3. Cache Screenshots (Advanced)

For visual regression testing, compare screenshots efficiently.

**Recommended:**
```python
import hashlib

def screenshot_hash(screenshot: bytes) -> str:
    """Generate hash for screenshot comparison."""
    return hashlib.sha256(screenshot).hexdigest()

# Compare
current_hash = screenshot_hash(current_screenshot)
baseline_hash = screenshot_hash(baseline_screenshot)

if current_hash == baseline_hash:
    print("No visual changes detected")
else:
    print("Visual regression detected")
```

## Code Organization

### 1. Separate Configuration

**Recommended:**
```python
# config.py
class Config:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_ID = os.getenv("GOOGLE_COMPUTER_USE_MODEL", "gemini-2.5-computer-use-preview-10-2025")
    SPA_URL = os.getenv("SPA_URL", "http://localhost:5173")
    SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", "1920"))
    SCREEN_HEIGHT = int(os.getenv("SCREEN_HEIGHT", "1080"))
    TURN_LIMIT = int(os.getenv("TURN_LIMIT", "30"))
    HEADLESS = os.getenv("HEADLESS", "false").lower() in {"1", "true", "yes"}
```

### 2. Modular Function Handlers

**Recommended:**
```python
# function_handlers.py
class FunctionHandlers:
    def __init__(self, page, screen_width, screen_height):
        self.page = page
        self.screen_width = screen_width
        self.screen_height = screen_height

    def handle_click_at(self, args):
        x = denormalize_x(args["x"], self.screen_width)
        y = denormalize_y(args["y"], self.screen_height)
        self.page.mouse.click(x, y)

    def handle_type_text_at(self, args):
        # Implementation...

    # More handlers...
```

### 3. Reusable Utilities

**Recommended:**
```python
# utils.py
def denormalize_x(x: int, screen_width: int) -> int:
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    return int(y / 1000 * screen_height)

def prune_contents(contents: List[Content], keep_turns: int = 5) -> None:
    # Implementation...

def load_goal_from_file(file_path: Path) -> str:
    # Implementation...
```

## Testing & Validation

### 1. Validate Goal File

Before running automation:
```bash
python scripts/validate_goal.py gemini_goal.txt
```

Checks for:
- Role description
- Goal statement
- Numbered steps
- Success criteria
- Reporting structure

### 2. Dry Run with Low Turn Limit

Test goal file with low turn limit first:
```bash
export TURN_LIMIT=5
python gemini_computer_use.py
```

Validates:
- Goal file is readable
- Gemini understands instructions
- First few actions work correctly

### 3. Monitor Console Output

Watch for:
- Gemini's function calls (are they sensible?)
- Execution errors (coordinate issues? timeouts?)
- Token usage warnings

**Good:**
```
Turn 1: Executing navigate to http://localhost:5173
Turn 2: Executing click_at (500, 300)
Turn 3: Executing type_text_at (500, 400, "test@example.com")
```

**Bad:**
```
Turn 1: Error executing click_at: Invalid coordinates
Turn 2: Error executing click_at: Timeout waiting for element
Turn 3: Error executing click_at: Page not loaded
```

## Summary

**Goal Files:**
1. Be specific and actionable
2. Include verification steps
3. Define measurable success criteria
4. Scope to 5-10 scenarios
5. Number steps sequentially

**Harness Scripts:**
1. Denormalize coordinates (0-1000 → pixels)
2. Add timeouts (prevent hanging)
3. Implement safety confirmations
4. Prune context (keep recent 5 turns)
5. Handle errors gracefully

**Token Management:**
1. Ensure `max_tokens` > `budget_tokens`
2. Monitor usage per turn
3. Adjust based on complexity

**Visual Verification:**
1. Capture screenshots after each action
2. Balance fidelity with performance
3. Wait for UI to stabilize

**Testing:**
1. Validate goal file before running
2. Dry run with low turn limit
3. Monitor console output

Following these practices ensures robust, maintainable automations that produce reliable results.
