# Parameterized and Property-Based Tests

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
