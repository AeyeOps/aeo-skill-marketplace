# Troubleshooting Guide for Gemini Computer-Use Automation

Common issues and solutions for Gemini computer-use automations.

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'google.genai'`

**Cause:** Gemini SDK not installed

**Solution:**
```bash
pip install google-genai
```

**Verify:**
```bash
python -c "import google.genai; print('Gemini SDK installed')"
```

### Issue: `ModuleNotFoundError: No module named 'playwright'`

**Cause:** Playwright not installed

**Solution:**
```bash
pip install playwright
playwright install --with-deps chromium
```

**Verify:**
```bash
python -c "import playwright; print('Playwright installed')"
```

### Issue: Browser fails to launch

**Cause:** Playwright browsers not installed

**Solution:**
```bash
playwright install --with-deps chromium
```

**Note:** `--with-deps` installs system dependencies (required on Linux).

## API Key Issues

### Issue: `RuntimeError: Set GOOGLE_API_KEY env var`

**Cause:** `GOOGLE_API_KEY` environment variable not set

**Solution:**
```bash
export GOOGLE_API_KEY="your-key-here"
```

**Persistent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export GOOGLE_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Verify:**
```bash
echo $GOOGLE_API_KEY
```

### Issue: `401 Unauthorized` from Gemini API

**Cause:** Invalid API key

**Solution:**
1. Verify API key is correct
2. Check key has Computer Use API access enabled
3. Generate new key at https://aistudio.google.com/apikey

## Coordinate Issues

### Issue: Clicks miss target element

**Symptom:** Gemini clicks wrong location, element not activated

**Cause:** Coordinates not denormalized from 0-1000 range

**Solution:** Verify denormalization logic
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

**Check:** Print coordinates before clicking
```python
print(f"Clicking at ({x_pixel}, {y_pixel}) on {SCREEN_WIDTH}x{SCREEN_HEIGHT} viewport")
page.mouse.click(x_pixel, y_pixel)
```

### Issue: Clicks at (0, 0) or viewport corner

**Cause:** Using normalized coordinates directly without denormalization

**Solution:** Always denormalize before passing to Playwright

## Token Budget Issues

### Issue: `max_tokens must be strictly greater than budget_tokens`

**Cause:** `max_tokens` ≤ `budget_tokens` in config

**Solution:** Increase `max_tokens` or decrease `budget_tokens`
```python
config = types.GenerateContentConfig(
    tools=[tool],
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        budget_tokens=10000,  # Must be less than max_tokens
    ),
    max_tokens=16000,  # Must be greater than budget_tokens
)
```

**Recommended:**
- Simple tasks: `budget_tokens=5000`, `max_tokens=10000`
- Complex tasks: `budget_tokens=10000`, `max_tokens=16000`

### Issue: Token limit exceeded errors

**Symptom:** `Error: Context length exceeded` or `429 Too Many Requests`

**Cause:** Conversation history too long, exceeds model limits

**Solution:** Implement or verify context pruning
```python
def prune_contents(contents, keep_turns=5):
    if len(contents) <= 1:
        return

    tail = contents[1:]
    max_tail = keep_turns * 2

    if len(tail) > max_tail:
        tail = tail[-max_tail:]
        contents[:] = [contents[0], *tail]

# Call after each turn:
prune_contents(contents, keep_turns=5)
```

**Aggressive pruning (if still failing):**
```python
prune_contents(contents, keep_turns=3)  # Keep only recent 3 turns
```

## Browser Issues

### Issue: Page fails to load

**Symptom:** `Timeout 30000ms exceeded` waiting for load

**Cause:** Slow application or network, default timeout too short

**Solution:** Increase timeout
```python
page.goto(url, wait_until="load", timeout=30000)  # 30 seconds
```

**Alternative:** Use `networkidle` instead of `load`
```python
page.goto(url, wait_until="networkidle", timeout=30000)
```

### Issue: Application URL unreachable

**Symptom:** `net::ERR_CONNECTION_REFUSED` or `Failed to reach application`

**Cause:** Application not running or wrong URL

**Solution:**
1. Verify application is running:
   ```bash
   curl http://localhost:5173
   ```
2. Check correct port in `SPA_URL` environment variable
3. Start application:
   ```bash
   npm run dev  # or appropriate start command
   ```

### Issue: Headless mode fails but non-headless works

**Symptom:** Automation works with `HEADLESS=false` but fails with `HEADLESS=true`

**Cause:** GPU rendering issues in headless mode

**Solution:** Disable GPU acceleration
```python
browser = playwright.chromium.launch(
    headless=True,
    args=["--disable-gpu", "--no-sandbox"]
)
```

## Function Call Issues

### Issue: `type_text_at` doesn't clear field

**Symptom:** New text appends to existing text instead of replacing

**Cause:** `clear_before_typing=True` not working correctly

**Solution:** Verify Ctrl+A / Cmd+A logic
```python
if clear_before:
    if os.name == "nt":  # Windows
        page.keyboard.press("Control+A")
    else:  # Mac/Linux
        page.keyboard.press("Meta+A")  # Mac
        # OR
        page.keyboard.press("Control+A")  # Linux
    page.keyboard.press("Backspace")
```

**Alternative:** Use Playwright's `fill()` method
```python
page.locator(f'[data-testid="email-field"]').fill(text)
```

### Issue: Keyboard shortcuts don't work

**Symptom:** `key_combination("Ctrl+A")` has no effect

**Cause:** Key normalization incorrect

**Solution:** Verify key normalization
```python
KEY_ALIASES = {
    'ctrl': 'Control',
    'control': 'Control',
    'cmd': 'Meta',
    'command': 'Meta',
    'shift': 'Shift',
    'alt': 'Alt',
    # ...
}

def normalize_key_combo(value: str) -> str:
    parts = value.replace('-', '+').split('+')
    normalized = []
    for part in parts:
        lower = part.strip().lower()
        if lower in KEY_ALIASES:
            normalized.append(KEY_ALIASES[lower])
        else:
            normalized.append(part.strip())
    return '+'.join(normalized)

# Usage:
combo = normalize_key_combo("Ctrl+A")  # Returns "Control+A"
page.keyboard.press(combo)
```

## Goal File Issues

### Issue: Gemini doesn't follow goal file instructions

**Symptom:** Gemini ignores steps, skips verification, or does unrelated actions

**Cause:** Goal file too vague, missing context, or poorly structured

**Solution:**
1. **Be more specific:**
   - Bad: "Test the form"
   - Good: "Click the submit button on the registration form, then verify the success message 'Account created!' displays"

2. **Add context:**
   - Include application description
   - Explain what features do and why they matter

3. **Number steps:**
   - Use numbered lists (1, 2, 3)
   - Makes sequence clear

4. **Validate goal file:**
   ```bash
   python scripts/validate_goal.py gemini_goal.txt
   ```

### Issue: Goal file not found

**Symptom:** `FileNotFoundError: gemini_goal.txt`

**Cause:** Goal file in wrong location or wrong filename

**Solution:**
1. Check file location relative to harness script:
   ```python
   DEFAULT_GOAL_PATH = Path(__file__).resolve().parent / "gemini_goal.txt"
   ```
2. Verify filename matches (case-sensitive)
3. Or set goal via environment variable:
   ```bash
   export COMPUTER_USE_GOAL="Test the application..."
   ```

## Safety Confirmation Issues

### Issue: Automation hangs waiting for confirmation

**Symptom:** Script pauses indefinitely, no progress

**Cause:** Safety confirmation required but no input provided

**Solution:**
1. **Check for safety prompt:**
   ```
   Safety service requires explicit confirmation!
   [explanation of risk]
   Do you wish to proceed? [Y]es/[N]o
   ```
2. **Respond:** Type `Y` or `N` and press Enter

3. **Disable safety prompts for testing (NOT recommended for production):**
   ```python
   # Auto-approve all safety decisions (DANGEROUS)
   def get_safety_confirmation(safety_decision):
       return "CONTINUE"  # Always approve
   ```

## Screenshot Issues

### Issue: Screenshots are black or empty

**Symptom:** Screenshots captured but show black screen or no content

**Cause:** Page not fully loaded before screenshot

**Solution:** Wait for page to stabilize
```python
page.mouse.click(x, y)
page.wait_for_load_state("networkidle", timeout=5000)
page.wait_for_timeout(500)  # Additional buffer
screenshot = page.screenshot(type="png")
```

### Issue: Screenshots too large, slowing automation

**Symptom:** Each turn takes >10 seconds due to screenshot size

**Cause:** Full-page screenshots with high resolution

**Solution:** Use viewport screenshots (default)
```python
screenshot = page.screenshot(type="png")  # Viewport only (fast)
```

**Alternative:** Use JPEG with compression
```python
screenshot = page.screenshot(type="jpeg", quality=70)  # Smaller file
```

## Performance Issues

### Issue: Automation very slow (>1 minute per turn)

**Symptom:** Each reasoning turn takes 60+ seconds

**Cause:** Token budget too high, screenshots too large, or network latency

**Solution:**
1. **Reduce token budget:**
   ```python
   budget_tokens=5000  # Lower than default 10000
   ```

2. **Use viewport screenshots:**
   ```python
   screenshot = page.screenshot(type="png")  # Not full_page=True
   ```

3. **Prune more aggressively:**
   ```python
   prune_contents(contents, keep_turns=3)  # Keep only recent 3 turns
   ```

### Issue: Automation doesn't finish within turn limit

**Symptom:** Reaches `TURN_LIMIT` without completing goal

**Cause:** Goal too complex, vague instructions, or errors blocking progress

**Solution:**
1. **Review goal file:** Is it specific enough? Are steps clear?
2. **Check for errors:** Console errors blocking progress?
3. **Increase turn limit:**
   ```bash
   export TURN_LIMIT=50
   ```
4. **Split into smaller goals:** Break complex automation into multiple runs

## Common Error Messages

### `PlaywrightError: Target closed`

**Cause:** Browser or page closed unexpectedly

**Solution:** Check for crashes, ensure browser stays open

### `TimeoutError: Timeout 5000ms exceeded`

**Cause:** Operation took longer than timeout

**Solution:** Increase timeout or check if application is responsive

### `ReferenceError: page is not defined`

**Cause:** Playwright page object not initialized

**Solution:** Ensure `page = context.new_page()` called before use

### `AttributeError: 'NoneType' object has no attribute 'args'`

**Cause:** Function call args is None

**Solution:** Use `args = function_call.args or {}`

## Debugging Tips

### 1. Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Print Function Calls

```python
for function_call in function_calls:
    print(f"Executing: {function_call.name} with args: {function_call.args}")
```

### 3. Capture Screenshots on Error

```python
try:
    page.mouse.click(x, y)
except Exception as exc:
    error_screenshot = page.screenshot(type="png")
    with open("error_screenshot.png", "wb") as f:
        f.write(error_screenshot)
    print(f"Error screenshot saved: error_screenshot.png")
    raise
```

### 4. Run with Low Turn Limit First

```bash
export TURN_LIMIT=5
python gemini_computer_use.py
```

Validates goal file and initial steps work correctly.

### 5. Monitor Browser Console

In non-headless mode, open DevTools and watch Console for errors:
```python
browser = playwright.chromium.launch(headless=False, devtools=True)
```

## Getting Help

If issue persists after troubleshooting:

1. **Check examples:**
   - `examples/example_webapp_testing.md` - Dashboard workspace automation
   - `examples/example_form_automation.md` - Form testing
   - `examples/example_visual_regression.md` - Visual regression

2. **Review reference docs:**
   - `reference/gemini_api_reference.md` - Complete API reference
   - `reference/best_practices.md` - Best practices guide

3. **Validate setup:**
   ```bash
   python -c "import google.genai, playwright; print('Dependencies OK')"
   python scripts/validate_goal.py gemini_goal.txt
   ```

4. **Common issues checklist:**
   - -  `GOOGLE_API_KEY` set correctly
   - -  Application running and reachable
   - -  Playwright browsers installed (`playwright install chromium`)
   - -  Coordinates denormalized (0-1000 → pixels)
   - -  Context pruning enabled
   - -  `max_tokens` > `budget_tokens`

5. **GitHub Issues:**
   - Check existing issues: https://github.com/google/generative-ai-python/issues
   - Create new issue with reproducible example

## Summary

Most common issues:
1. **Coordinates not denormalized** → Always convert 0-1000 to pixels
2. **Token budget exceeded** → Implement context pruning (keep recent 5 turns)
3. **Application not running** → Verify app URL is accessible
4. **Goal file too vague** → Be specific, number steps, include verification
5. **Timeouts too short** → Increase to 5000-10000ms for slow apps

Follow best practices in `reference/best_practices.md` to avoid most issues.
