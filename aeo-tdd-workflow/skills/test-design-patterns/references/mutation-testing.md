# Mutation Testing

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
