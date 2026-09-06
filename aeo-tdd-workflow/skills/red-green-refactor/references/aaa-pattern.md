# AAA Pattern (Arrange-Act-Assert)

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
