---
name: red-green-refactor
description: |
  Use when practicing TDD: writing the failing test first, making it pass with the minimum
  code, refactoring under green, choosing between unit, integration, and end-to-end tests, or
  deciding how to build fixtures (inline, factory functions, shared pytest fixtures). Covers
  the red-green-refactor cycle with the mistakes at each phase, test-first case ordering, the
  transformation priority premise, Arrange-Act-Assert, fixture strategies, and test isolation,
  with Python examples.
license: MIT
metadata:
  author: AeyeOps
  version: "0.3.1"
  summary: The TDD cycle in practice, from the first failing test to fixtures and test isolation, with Python examples.
---

# Red-Green-Refactor: The TDD Cycle

## The Core Cycle

```
RED → GREEN → REFACTOR → repeat

RED:      Write a failing test that defines desired behavior
GREEN:    Write the minimum code to make the test pass
REFACTOR: Improve the code without changing behavior (tests still pass)
```

### RED Phase — Write a Failing Test

**Goal**: Define what the code should do before writing it.

```markdown
Rules:
1. Write exactly ONE test at a time
2. The test must fail for the RIGHT reason (expected behavior missing, not syntax error)
3. The test must be specific and focused on one behavior
4. Name the test to describe the behavior: test_[action]_[condition]_[expectation]

Common mistakes:
✗ Writing multiple tests before any implementation
✗ Writing a test that already passes (not testing new behavior)
✗ Testing implementation details instead of behavior
✗ Vague test names like "test_it_works"
```

Example (Python):
```python
# RED: Define the behavior we want
def test_calculate_discount_applies_10_percent_for_orders_over_100():
    order = Order(total=150.00)
    discount = calculate_discount(order)
    assert discount == 15.00  # Fails: calculate_discount doesn't exist yet
```

### GREEN Phase — Make It Pass

**Goal**: Write the simplest code that makes the test pass. Nothing more.

```markdown
Rules:
1. Write ONLY enough code to pass the failing test
2. It's OK to hardcode, use naive algorithms, or be "dumb"
3. Do NOT add edge case handling until you have a test for it
4. Do NOT refactor yet — just make it work
5. Run the test after every change to confirm it passes

Common mistakes:
✗ Writing a complete, polished implementation
✗ Handling edge cases without tests for them
✗ Refactoring while trying to go green
✗ Adding features that no test requires
```

Example:
```python
# GREEN: Simplest code that passes
def calculate_discount(order):
    if order.total > 100:
        return order.total * 0.10
    return 0
```

### REFACTOR Phase — Improve the Design

**Goal**: Clean up the code while keeping all tests green.

```markdown
Rules:
1. All tests must pass BEFORE refactoring
2. All tests must pass AFTER refactoring
3. Run tests after every small change
4. Change structure, not behavior
5. Apply one refactoring at a time

What to refactor:
- Remove duplication (DRY within reason)
- Improve naming (variables, functions, classes)
- Extract methods or classes for clarity
- Simplify conditionals
- Reduce coupling

Common mistakes:
✗ Changing behavior during refactoring
✗ Making too many changes at once
✗ Skipping the refactor phase entirely
✗ Gold-plating (over-engineering)
```

## Test-First Patterns

### Start with the Simplest Case
```markdown
Order of test cases:
1. Degenerate case (empty input, zero, null)
2. Simple positive case (single item, happy path)
3. Boundary cases (at the edge of rules)
4. Negative cases (invalid input, error conditions)
5. Complex cases (multiple items, combinations)

Example for a "fizzbuzz" function:
1. test_returns_number_as_string → "1"
2. test_returns_fizz_for_3 → "Fizz"
3. test_returns_buzz_for_5 → "Buzz"
4. test_returns_fizzbuzz_for_15 → "FizzBuzz"
5. test_returns_fizz_for_multiples_of_3 → 6, 9, 12
```

### Transformation Priority Premise
When going from RED to GREEN, prefer simpler transformations:

```markdown
Priority (simplest first):
1. {} → nil           (no code → return nil/null)
2. nil → constant     (return a constant value)
3. constant → variable (replace constant with a variable)
4. unconditional → conditional (add an if statement)
5. scalar → collection (single value → list/array)
6. statement → recursion (iterate → recurse)
7. value → mutated value (transform data)

Apply the highest-priority transformation that makes the test pass.
This prevents over-engineering during the GREEN phase.
```

### When to Write Which Test Type

```markdown
Unit tests (TDD primary loop):
  - Individual functions and methods
  - Business logic and calculations
  - Data transformations
  - State machines
  - Write these FIRST, they drive the design

Integration tests:
  - Database queries and transactions
  - API endpoint request/response
  - External service interactions
  - Write these AFTER unit tests define the contracts

End-to-end tests:
  - Critical user workflows
  - Smoke tests for deployment
  - Write few of these; they're slow and brittle
```

## Test Structure, Fixtures, and Isolation

- [references/aaa-pattern.md](references/aaa-pattern.md): Arrange-Act-Assert structure, two worked examples, and the five structural anti-patterns.
- [references/fixtures.md](references/fixtures.md): inline setup, factory functions, shared pytest fixtures, and the fixture rules.
- [references/test-isolation.md](references/test-isolation.md): why every test must run alone and in any order, and the four isolation techniques.

## TDD Rhythm Tips

```markdown
Keep the cycle fast:
- Entire RED-GREEN-REFACTOR cycle should take minutes, not hours
- If GREEN takes more than 10 minutes, the step is too big — go back to RED
- Run tests continuously (use a file watcher)
- Commit after every successful GREEN or REFACTOR

Signs you're doing it right:
- Tests run in seconds (< 5s for unit test suite)
- Each test is a few lines long
- Test names read like a specification
- You feel confident changing code because tests catch mistakes
- Code coverage emerges naturally (not chased)

Signs something is wrong:
- Tests are hard to write → design problem (code is too coupled)
- Tests are slow → too many integration tests, or poor isolation
- Tests break when refactoring → testing implementation, not behavior
- Many tests fail for one change → tests are too coupled to each other
```

## Keep this skill current

When an example here stops matching current pytest behavior, or a rule proves wrong in use, correct it in the same session. Replace the superseded text; do not append a note.
