---
name: test-design-patterns
description: |
  Test pyramid, testing anti-patterns, parameterized tests, and coverage interpretation.
  Activate when: designing test strategy, choosing test types, fixing test anti-patterns,
  writing parameterized tests, interpreting code coverage, understanding mutation testing.
---

# Test Design Patterns

## The Test Pyramid

```
        /  E2E  \          Few, slow, expensive
       /----------\        Test critical user journeys
      / Integration \      Moderate count, moderate speed
     /----------------\    Test component interactions
    /    Unit Tests     \  Many, fast, cheap
   /--------------------\  Test individual behaviors
```

### Layer Guidelines

```markdown
Unit Tests (70% of test suite):
  Speed: < 10ms each
  Scope: Single function, method, or class
  Dependencies: All mocked or stubbed
  When to write: Every behavior, every branch, every edge case
  Example: calculate_tax(100, "CA") returns 7.25

Integration Tests (20% of test suite):
  Speed: < 1s each
  Scope: Two or more components interacting
  Dependencies: Real database, real file system, mocked externals
  When to write: Database queries, API endpoints, service boundaries
  Example: POST /api/orders creates order and sends confirmation

End-to-End Tests (10% of test suite):
  Speed: Seconds to minutes each
  Scope: Full application from user perspective
  Dependencies: All real (or realistic staging environment)
  When to write: Critical user workflows, smoke tests
  Example: User can sign up, create project, and invite teammate
```

### Inverted Pyramid (Anti-Pattern)

```markdown
Problem: Too many E2E tests, too few unit tests
Symptoms:
  - Test suite takes 30+ minutes
  - Tests are flaky (pass sometimes, fail others)
  - Small code changes break many tests
  - Team avoids running tests locally
  - "It works on my machine" is common

Fix:
  1. Identify behavior each E2E test covers
  2. Write unit tests for that behavior
  3. Keep only the critical-path E2E tests
  4. Convert integration tests to unit tests where possible
```

## Testing Anti-Patterns

### The Liar
Test that always passes regardless of behavior.

```python
# BAD: Test passes even if logic is wrong
def test_discount():
    result = calculate_discount(100)
    assert result is not None  # This passes for ANY non-None value

# GOOD: Test verifies specific expected value
def test_discount_is_10_percent_for_orders_over_100():
    result = calculate_discount(150)
    assert result == 15.0
```

### The Giant
One test that verifies too many behaviors.

```python
# BAD: Testing everything in one test
def test_user_service():
    user = create_user("ada@test.com")
    assert user.email == "ada@test.com"
    user.update_name("Ada Lovelace")
    assert user.name == "Ada Lovelace"
    user.deactivate()
    assert user.is_active is False
    users = list_users()
    assert len(users) == 1

# GOOD: One behavior per test
def test_create_user_sets_email():
    user = create_user("ada@test.com")
    assert user.email == "ada@test.com"

def test_update_name_changes_display_name():
    user = create_user("ada@test.com")
    user.update_name("Ada Lovelace")
    assert user.name == "Ada Lovelace"
```

### The Mockery
Over-mocking to the point where you're testing mocks, not code.

```python
# BAD: Everything is mocked, testing nothing real
def test_process_order(mock_db, mock_email, mock_payment, mock_inventory):
    mock_payment.charge.return_value = True
    mock_inventory.check.return_value = True
    result = process_order(order, mock_db, mock_email, mock_payment, mock_inventory)
    assert result is True  # But does the REAL code work?

# GOOD: Mock only external boundaries, test real logic
def test_process_order_charges_correct_amount():
    mock_payment = MockPaymentGateway()
    order = Order(items=[Item("Widget", 9.99, qty=2)])
    process_order(order, payment=mock_payment)
    assert mock_payment.last_charge_amount == 19.98
```

### The Inspector
Testing internal implementation rather than external behavior.

```python
# BAD: Testing HOW, not WHAT
def test_sort_uses_quicksort():
    sorter = Sorter()
    sorter.sort([3, 1, 2])
    assert sorter._algorithm_used == "quicksort"

# GOOD: Testing observable behavior
def test_sort_returns_ascending_order():
    assert Sorter().sort([3, 1, 2]) == [1, 2, 3]
```

### The Flaky Test
Test that passes and fails intermittently.

```markdown
Common causes and fixes:

Time-dependent:
  ✗ assert result.timestamp == datetime.now()
  ✓ assert result.timestamp is not None (or freeze time)

Order-dependent:
  ✗ assert results == [item_a, item_b]  (set has no order)
  ✓ assert set(results) == {item_a, item_b}

Race condition:
  ✗ start_background_task(); assert task.done  (timing)
  ✓ start_background_task(); wait_for(task, timeout=5)

Shared state:
  ✗ Test A writes to DB, Test B reads (coupling)
  ✓ Each test uses its own isolated state

Network-dependent:
  ✗ Calling real external APIs in tests
  ✓ Mock/stub external calls, test integration separately
```

## Parameterized Tests

Run the same test logic with different inputs and expected outputs.

### pytest.mark.parametrize

```python
import pytest

@pytest.mark.parametrize("input_val, expected", [
    (0, "zero"),
    (1, "one"),
    (-1, "negative"),
    (100, "positive"),
    (None, "invalid"),
])
def test_classify_number(input_val, expected):
    assert classify_number(input_val) == expected
```

### Table-Driven Tests (Go Style)

```python
class TestPriceCalculator:
    test_cases = [
        # (description, quantity, unit_price, discount, expected)
        ("no discount", 1, 10.00, 0, 10.00),
        ("10% discount", 1, 10.00, 0.10, 9.00),
        ("bulk pricing", 100, 10.00, 0, 900.00),
        ("zero quantity", 0, 10.00, 0, 0.00),
        ("free item", 1, 0.00, 0, 0.00),
    ]

    @pytest.mark.parametrize("desc, qty, price, discount, expected", test_cases)
    def test_calculate_price(self, desc, qty, price, discount, expected):
        result = calculate_price(qty, price, discount)
        assert result == expected, f"Failed: {desc}"
```

### When to Parameterize

```markdown
Good candidates:
- Same logic, different inputs (validation rules)
- Boundary value testing (off-by-one, limits)
- Format conversion (parse/serialize pairs)
- Error cases (different invalid inputs, same error type)

Bad candidates:
- Different test logic per case (just write separate tests)
- Tests that need different setup per case
- Tests where failure message needs to explain context
```

## Property-Based Testing

Instead of specific examples, define properties that must always hold.

```python
from hypothesis import given
from hypothesis import strategies as st

# Property: sorting then checking produces sorted output
@given(st.lists(st.integers()))
def test_sort_produces_sorted_output(xs):
    result = my_sort(xs)
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))

# Property: encoding then decoding returns original
@given(st.text())
def test_encode_decode_roundtrip(text):
    assert decode(encode(text)) == text

# Property: output length equals input length
@given(st.lists(st.integers()))
def test_sort_preserves_length(xs):
    assert len(my_sort(xs)) == len(xs)
```

### Useful Properties to Test

```markdown
Roundtrip:       decode(encode(x)) == x
Idempotence:     f(f(x)) == f(x)
Invariant:       len(sort(xs)) == len(xs)
Commutativity:   f(a, b) == f(b, a)
Associativity:   f(f(a, b), c) == f(a, f(b, c))
Identity:        f(x, identity) == x
Oracle:          new_implementation(x) == trusted_implementation(x)
Hard to compute: verify(x, solve(x)) is True (easier to check than solve)
```

## Mutation Testing

Tests test the code. Mutation testing tests the tests.

### How It Works

```markdown
1. Start with a passing test suite
2. Mutator makes a small change ("mutant") to the source code:
   - Replace > with >=
   - Replace + with -
   - Remove a function call
   - Change a constant
   - Negate a condition
3. Run the test suite against the mutant
4. If tests fail → mutant "killed" (tests caught the change) ✓
5. If tests pass → mutant "survived" (tests missed the change) ✗

Mutation score = killed mutants / total mutants × 100%
Target: >80% mutation score
```

### Common Mutation Operators

```markdown
Arithmetic:     + → -, * → /, % → *
Relational:     > → >=, == → !=, < → <=
Logical:        and → or, not removed
Constant:       0 → 1, true → false, "" → "x"
Statement:      remove function call, remove return
Conditional:    if(cond) → if(true), if(cond) → if(false)
```

### Interpreting Surviving Mutants

```markdown
A surviving mutant means one of:
1. Missing test: Write a test that catches this mutation
2. Equivalent mutant: The change doesn't affect behavior (ignore)
3. Weak assertion: Strengthen your assertions

Example surviving mutant:
  Original:  if (age >= 18): return "adult"
  Mutant:    if (age > 18): return "adult"
  Survived because: No test checks age == 18 (boundary)
  Fix: Add test_classify_age_18_returns_adult()
```

## Coverage Interpretation

### What Coverage Measures

```markdown
Line coverage:    Which lines were executed
Branch coverage:  Which conditional branches were taken
Path coverage:    Which execution paths were followed
Function coverage: Which functions were called

Line coverage is necessary but not sufficient.
100% line coverage does NOT mean the code is well-tested.
```

### Coverage Traps

```markdown
False confidence from high coverage:
  - Lines executed but results not asserted
  - Happy path covered but edge cases missing
  - Implementation tested but behavior not verified

Example of misleading 100% coverage:
  def divide(a, b):
      return a / b

  def test_divide():
      divide(10, 2)  # 100% line coverage, but:
                      # - No assertion on result
                      # - Division by zero not tested
                      # - Float precision not tested
```

### Healthy Coverage Practices

```markdown
Guidelines:
- Aim for 80%+ line coverage as a baseline
- Focus on branch coverage for conditional logic
- Use coverage to find UNTESTED code, not to prove quality
- Never game coverage metrics (writing tests just to hit lines)
- High-risk code (payments, auth, data) deserves near-100% coverage
- Generated code, configuration, and glue code can have lower coverage
- Review uncovered lines: are they dead code or missing tests?

Coverage as a ratchet:
- Set a minimum threshold (e.g., 80%)
- Never allow coverage to decrease
- Increase the threshold as the suite matures
- Fail CI if coverage drops below threshold
```
