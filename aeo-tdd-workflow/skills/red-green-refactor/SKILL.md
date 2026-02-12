---
name: red-green-refactor
description: |
  TDD cycle mechanics, test-first patterns, and fixture strategies.
  Activate when: practicing TDD, writing tests first, doing red-green-refactor,
  learning test-driven development, choosing test types, writing unit tests.
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

## AAA Pattern (Arrange-Act-Assert)

```markdown
Structure every test with three distinct sections:

Arrange: Set up the test context
  - Create objects, set state, configure mocks
  - Prepare input data
  - Set expectations for dependencies

Act: Execute the behavior under test
  - Call the function or method
  - Trigger the event
  - Should be ONE line (or very few)

Assert: Verify the result
  - Check return values
  - Verify state changes
  - Confirm interactions with dependencies
```

### Examples

```python
# Clean AAA structure
def test_user_registration_sends_welcome_email():
    # Arrange
    email_service = MockEmailService()
    user_service = UserService(email_service=email_service)
    registration_data = {"email": "user@example.com", "name": "Ada"}

    # Act
    user = user_service.register(registration_data)

    # Assert
    assert user.email == "user@example.com"
    assert email_service.sent_count == 1
    assert email_service.last_recipient == "user@example.com"
```

```python
# Multiple assertions about one behavior are fine
def test_order_summary_includes_all_fields():
    # Arrange
    order = Order(items=[Item("Widget", 9.99)], customer="Ada")

    # Act
    summary = order.get_summary()

    # Assert
    assert summary["customer"] == "Ada"
    assert summary["item_count"] == 1
    assert summary["total"] == 9.99
```

### Anti-Patterns

```markdown
✗ Arrange-Assert (no act — testing setup, not behavior)
✗ Act-Assert (no arrange — implicit state is fragile)
✗ Arrange-Act-Act-Assert (testing two behaviors in one test)
✗ Arrange-Act-Assert-Act-Assert (test should be split)
✗ Assert-first (assertions before the action — confusing)
```

## Fixture Strategies

### Inline Setup
Define test data directly in the test. Best for simple tests where context matters.

```python
def test_full_name_combines_first_and_last():
    user = User(first_name="Ada", last_name="Lovelace")
    assert user.full_name == "Ada Lovelace"
```

### Factory Functions
Create reusable builders for common objects. Best when many tests need similar data.

```python
def make_user(**overrides):
    defaults = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "role": "developer",
    }
    defaults.update(overrides)
    return User(**defaults)

def test_admin_users_have_elevated_permissions():
    admin = make_user(role="admin")
    assert admin.can_delete_users is True
```

### Shared Fixtures (pytest)
Use `@pytest.fixture` for setup that multiple tests share.

```python
@pytest.fixture
def database():
    db = create_test_database()
    db.migrate()
    yield db
    db.drop()

@pytest.fixture
def user_repo(database):
    return UserRepository(database)

def test_save_and_retrieve_user(user_repo):
    user_repo.save(User(name="Ada"))
    found = user_repo.find_by_name("Ada")
    assert found is not None
```

### Fixture Best Practices

```markdown
DO:
- Keep fixtures minimal — only what the test needs
- Name fixtures after what they represent, not what they do
- Use factory functions for variation (make_user, make_order)
- Isolate tests — each test gets its own state
- Clean up after tests (use yield + teardown or context managers)

DON'T:
- Share mutable state between tests
- Create "god fixtures" that set up everything
- Nest fixtures more than 2 levels deep
- Use fixtures to test setup logic (test the fixture separately)
- Rely on test execution order
```

## Test Isolation

### Why Isolation Matters
```markdown
Tests must be independent:
- Any test can run alone and pass
- Any test can run in any order and pass
- Tests can run in parallel without interfering
- A failing test means ONE thing is broken, not cascading failures
```

### Isolation Techniques

```markdown
1. Fresh state per test
   - Reset database/state before or after each test
   - Use transactions that roll back (database tests)
   - Create new object instances (don't reuse)

2. Dependency injection
   - Pass dependencies as parameters
   - Replace real dependencies with test doubles
   - Avoid global state and singletons in tests

3. Test doubles
   - Stub: Returns canned responses (for queries)
   - Mock: Verifies interactions (for commands)
   - Fake: Simplified working implementation (in-memory DB)
   - Spy: Records calls for later assertion

4. Environment isolation
   - Use separate test configuration
   - Isolate file system access (temp directories)
   - Mock external HTTP calls (no network in unit tests)
   - Use unique identifiers to prevent collisions
```

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
