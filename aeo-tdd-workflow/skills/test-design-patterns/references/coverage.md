# Coverage Interpretation

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
