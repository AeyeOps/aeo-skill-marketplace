# Testing Anti-Patterns

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
