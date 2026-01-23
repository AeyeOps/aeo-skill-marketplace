---
name: automating-computer-use-testing
description: Generate Gemini 2.5 computer-use automation scripts and natural-language goal files for web application QA. Produces Playwright-based test harnesses for browser automation with scenario generation capabilities. Activate for UI test automation, visual regression testing, or AI-driven browser interaction workflows.
---

# Automating Computer-Use Testing

A comprehensive skill for creating Gemini 2.5 Computer Use automation scripts, natural-language goal files, and Playwright-based test harnesses for QA testing of web applications.

## When to Use This Skill

Trigger this skill when the user requests:
- Automating UI testing for web applications
- Creating QA automation scripts
- Writing goal files for Gemini computer use
- Generating Playwright-based test harnesses
- Automating browser interactions (clicking, typing, scrolling)
- Creating test scenarios for regression testing
- Building computer-use automation workflows
- Testing React/Vue/Angular/web applications
- Form automation and validation testing
- Visual regression testing

**Complete overview**: See [README.md](README.md)

## Core Workflow

### Phase 1: Requirements Analysis

1. **Understand the Application**
   - What application are you testing? (URL, tech stack)
   - What are the key UI patterns? (panels, forms, modals, navigation)
   - What user flows need automation? (login, checkout, data entry)
   - Are there existing test scenarios or manual test plans?

2. **Define Automation Objectives**
   - What is the primary goal? (regression testing, UI validation, workflow automation)
   - What constitutes "passing"? (success criteria)
   - What should be verified? (UI elements, data validation, visual appearance)
   - What edge cases or error scenarios should be tested?

3. **Scope the Automation**
   - Which features to include?
   - Which features to exclude or defer?
   - How many test scenarios? (recommend 5-10 per goal file)
   - Expected runtime? (recommend <10 minutes per automation)

### Phase 2: Goal File Generation

The goal file is a natural-language document that Gemini 2.5 Computer Use reads to understand what to test.

**Goal File Structure** (Use template from `templates/goal_template.txt`):
```
[Role Description]
You are a QA engineer testing the [Application Name].

Your goal is to [primary objective].

## Test Session Overview
1. [Step 1: Initial navigation]
2. [Step 2: Verify initial load state]
3. [Step 3-N: Test features]

## Success Criteria
- [Criterion 1: specific, measurable]
- [Criterion 2: specific, measurable]

## Reporting
Document what worked, what broke, UX notes
```

**Key Principles for Goal Files:**
- **Be specific:** "Click the collapse icon on Investigation Explorer panel" not "Click something"
- **Include verification:** "Verify panel collapses with 300ms animation"
- **Define success criteria:** Measurable, observable outcomes
- **Number steps:** Use numbered lists for sequential actions
- **Scope appropriately:** 5-10 test scenarios per file

**For complete best practices:** → See `reference/best_practices.md` section "Goal File Best Practices"

### Phase 3: Harness Script Generation

The harness script is a Python program that:
1. Launches a Playwright browser
2. Calls Gemini 2.5 Computer Use API
3. Executes function calls (click, type, scroll, navigate)
4. Captures screenshots for Gemini to observe state
5. Handles safety confirmations
6. Manages token budgets and context pruning

**Harness Script Template:** → Use `templates/harness_template.py`

**Key Components:**

1. **Configuration** (environment variables):
   - `GOOGLE_API_KEY` - Your Gemini API key (required)
   - `SPA_URL` - Application URL to test
   - `SCREEN_WIDTH` / `SCREEN_HEIGHT` - Viewport size
   - `TURN_LIMIT` - Max reasoning turns
   - `HEADLESS` - Run browser in headless mode

   → See `templates/env_template.env` for complete configuration

2. **Function Call Handlers:**
   - `navigate(url)` - Navigate to URL
   - `click_at(x, y)` - Click normalized coordinates (0-1000)
   - `type_text_at(x, y, text, press_enter, clear_before)` - Type text
   - `scroll_document(direction)` / `scroll_at(x, y, direction, pixels)` - Scroll
   - `key_combination(keys)` - Press keyboard shortcuts
   - `wait_5_seconds()`, `go_back()`, `go_forward()`

   → See `reference/gemini_api_reference.md` for complete API documentation

3. **Critical Implementation Details:**
   - **Coordinate normalization:** Gemini returns 0-1000, denormalize to viewport pixels
   - **Safety confirmations:** Prompt operator for risky actions
   - **Context pruning:** Keep recent 5 turns to prevent token overflow
   - **Screenshot capture:** After each action for Gemini to observe state

   → See `reference/best_practices.md` section "Harness Script Best Practices"

### Phase 4: Testing & Iteration

1. **Run Initial Automation**
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   python gemini_computer_use.py
   ```

2. **Analyze Results**
   - Review Gemini's QA summary (what worked, what broke)
   - Check for console errors or visual glitches
   - Verify success criteria were met

3. **Refine & Iterate**
   - Update goal file based on findings
   - Adjust success criteria if needed
   - Add verification steps for uncovered issues

   → If issues occur, see `reference/troubleshooting.md`

## Examples

### Example 1: Web Application QA Testing

**User Request:**
"Automate QA testing for a React PWA with a 4-panel investigation workspace. Test panel collapse/expand, selection-driven updates."

**Generated Artifacts:**
1. **Goal file** based on `templates/goal_template.txt`
2. **Harness script** from `templates/harness_template.py`
3. **Environment config** from `templates/env_template.env`

**Key test scenarios:**
- Verify 4-panel layout renders correctly
- Test panel collapse/expand with animation
- Validate selection-driven architecture
- Check visual fidelity and console errors

→ See complete example: `examples/example_webapp_testing.md`

### Example 2: Form Automation

**User Request:**
"Automate filling out a multi-step registration form with validation testing."

**Key test scenarios:**
- Navigate to registration page
- Fill out form fields
- Test required field validation
- Test email format validation
- Submit form and verify confirmation

→ See complete example: `examples/example_form_automation.md`

### Example 3: Visual Regression Testing

**User Request:**
"Create automation to compare current UI against baseline screenshots."

**Key test scenarios:**
- Navigate to each page/view
- Capture full-page screenshots
- Compare against baselines
- Identify visual differences
- Report similarity scores

→ See complete example: `examples/example_visual_regression.md`

## Quick Decision Trees

### Automation Type Selection

```
What do you need to test?
├─ Web app UI interactions → Use Example 1 (webapp testing)
├─ Form validation → Use Example 2 (form automation)
├─ Visual appearance → Use Example 3 (visual regression)
├─ E2E user workflow → Combine multiple patterns
└─ API testing → Use different tool (not computer-use)
```

### Goal File Scope

```
How many test scenarios?
├─ Simple feature (login, form) → 3-5 scenarios
├─ Medium feature (dashboard, workflow) → 5-10 scenarios
├─ Complex feature (full app) → Split into multiple goal files
└─ Too complex? → Break into phases, run separately
```

### Troubleshooting Decision Tree

```
Automation failing?
├─ Clicks miss targets → Check coordinate normalization
├─ Token limit exceeded → Verify context pruning enabled
├─ Page not loading → Increase timeout or check URL
├─ Goal file ignored → Make instructions more specific
└─ Other issues → See reference/troubleshooting.md
```

## Validation Tools

### Goal File Validator

Before running automation, validate your goal file:

```bash
python scripts/validate_goal.py gemini_goal.txt
```

Checks for:
- Role description present
- Goal statement present
- Numbered test steps (≥3)
- Success criteria defined
- Reporting structure included

### Requirements Analyzer

Interactive tool to help structure your goal file:

```bash
python scripts/analyze_requirements.py
```

Prompts for application details and outputs suggested goal file structure.

## Supporting Files

This skill uses progressive disclosure - additional files loaded only when needed:

### Templates (`templates/`)
- **goal_template.txt** - Natural-language goal template
- **harness_template.py** - Python Playwright harness (395 lines, complete implementation)
- **env_template.env** - Environment variables configuration

### When to Read Reference Files

**Read [reference/gemini_api_reference.md](reference/gemini_api_reference.md) when:**
- Need to understand specific function call parameters
- Want to see complete API examples
- Debugging function call failures
- Implementing custom function handlers

**Read [reference/best_practices.md](reference/best_practices.md) when:**
- Goal file not activating automation correctly
- Harness script has coordinate or timing issues
- Token budget errors occurring
- Want to optimize performance

**Read [reference/troubleshooting.md](reference/troubleshooting.md) when:**
- Installation or setup issues
- Automation failing with errors
- Clicks missing targets
- Page not loading or timing out
- Any unexpected behavior

### Examples (`examples/`)
- [example_webapp_testing.md](examples/example_webapp_testing.md) - Christina workspace QA (complete goal file)
- [example_form_automation.md](examples/example_form_automation.md) - Form validation testing (step-by-step)
- [example_visual_regression.md](examples/example_visual_regression.md) - Visual comparison testing (screenshot workflow)

### Reference Documentation (`reference/`)
- **gemini_api_reference.md** - Complete Gemini Computer Use API documentation
  - Authentication and setup
  - All function calls with parameters
  - Safety decisions
  - Token management
  - Code examples

- **best_practices.md** - Comprehensive best practices guide
  - Goal file best practices (specificity, verification, success criteria)
  - Harness script best practices (coordinates, timeouts, safety, errors)
  - Token management (budgets, pruning, monitoring)
  - Visual verification (screenshots, fidelity, timing)
  - Performance optimization

- **troubleshooting.md** - Common issues and solutions
  - Installation issues
  - API key issues
  - Coordinate issues (clicks missing targets)
  - Token budget issues
  - Browser issues (timeouts, failures)
  - Performance issues
  - Complete debugging guide

### Scripts (`scripts/`)
- **validate_goal.py** - Validates goal file structure
- **analyze_requirements.py** - Interactive requirements analyzer

## Dependencies & Installation

**Required:**
- Python 3.8+
- `google-genai` SDK
- `playwright`
- `GOOGLE_API_KEY` environment variable

**Installation:**
```bash
pip install google-genai playwright
playwright install --with-deps chromium
export GOOGLE_API_KEY="your-key-here"
```

## Quick Start

1. **Tell Claude what you need to test:**
   ```
   I need to automate testing for my React app's login form.
   Test email validation, password requirements, and successful login.
   ```

2. **Claude generates:**
   - Goal file with test scenarios
   - Harness script ready to run
   - Environment configuration

3. **Run the automation:**
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   python gemini_computer_use.py
   ```

4. **Review results and iterate**

## Key Reminders

1. **Goal files are natural language** - Write like you're instructing a human QA engineer
2. **Be specific and measurable** - "Click the blue Submit button" not "Click button"
3. **Coordinates are normalized** - Always denormalize 0-1000 to viewport pixels
4. **Prune context regularly** - Keep recent 5 turns to prevent token overflow
5. **Safety confirmations required** - Prompt operator for risky actions
6. **Scope appropriately** - 5-10 test scenarios per goal file
7. **Validate before running** - Use `scripts/validate_goal.py`

## Success Metrics

- **Time savings:** 80% reduction in automation creation time (4 hours → 48 minutes)
- **Quality:** 90% of generated goal files pass validation without manual edits
- **Consistency:** Templates enforce best practices automatically

## Common Patterns

### Pattern: Basic UI Testing
```
1. Use templates/goal_template.txt as starting point
2. Fill in application-specific details
3. Generate harness from templates/harness_template.py
4. Run and iterate based on results
```

### Pattern: Form Validation Testing
```
1. Review examples/example_form_automation.md
2. Adapt test scenarios to your form
3. Include both positive and negative test cases
4. Verify error messages display correctly
```

### Pattern: Visual Regression
```
1. Review examples/example_visual_regression.md
2. Capture baseline screenshots first run
3. Compare subsequent runs against baseline
4. Document visual differences found
```

---

**Built on research from:**
- Christina Investigation Workspace automation
- Claude Skills best practices (docs.claude.com)
- Gemini 2.5 Computer Use API (ai.google.dev)
- Industry QA automation patterns

**Ready to automate?** Just describe what you need to test!
