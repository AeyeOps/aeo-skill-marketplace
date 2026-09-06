# Fixture Strategies

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
