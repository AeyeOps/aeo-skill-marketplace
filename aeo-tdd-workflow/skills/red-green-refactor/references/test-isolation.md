# Test Isolation

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
