---
name: test-design-patterns
description: |
  Use when designing a test strategy or reviewing QA practice: deciding the test pyramid
  split between unit, integration, and end-to-end tests, fixing test anti-patterns (the liar,
  the giant, the mockery, the inspector, the flaky test), writing parameterized or
  table-driven tests, adding property-based tests, reading mutation testing results, or
  interpreting code coverage numbers. Python and pytest examples throughout.
license: MIT
metadata:
  author: AeyeOps
  version: "0.3.1"
  summary: Test strategy patterns covering the test pyramid, anti-patterns, parameterized and property-based tests, mutation testing, and coverage interpretation.
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

| Anti-pattern | Symptom | Fix |
|---|---|---|
| The Liar | passes for any non-None result | assert the specific expected value |
| The Giant | one test verifies many behaviors | one behavior per test |
| The Mockery | every collaborator mocked, nothing real runs | mock only external boundaries |
| The Inspector | asserts on internals such as `_algorithm_used` | assert observable behavior |
| The Flaky Test | passes and fails intermittently | remove time, order, race, shared-state, and network dependence |

Before-and-after code for each: [references/anti-patterns.md](references/anti-patterns.md).

## Parameterized and Property-Based Tests

`pytest.mark.parametrize`, table-driven cases, when to parameterize and when not to, and
Hypothesis properties (roundtrip, idempotence, invariant, oracle):
[references/parameterized-and-property-tests.md](references/parameterized-and-property-tests.md).

## Mutation Testing

How mutants are generated, the common operators, the target score, and how to read a
surviving mutant: [references/mutation-testing.md](references/mutation-testing.md).

## Coverage Interpretation

What line, branch, path, and function coverage measure, the false-confidence traps, and
coverage as a ratchet in CI: [references/coverage.md](references/coverage.md).

## Keep this skill current

When an example here stops matching current pytest or Hypothesis behavior, or a rule proves wrong in use, correct it in the same session. Replace the superseded text; do not append a note.
