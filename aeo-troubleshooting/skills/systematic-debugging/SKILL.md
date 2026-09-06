---
name: systematic-debugging
description: |
  Use when debugging a failure, reading a stack trace, reproducing a flaky or intermittent
  bug, isolating a regression, or running a root cause analysis. Hypothesis-driven debugging
  with a recorded experiment at every step: reproduce, read the whole error, form and test one
  hypothesis at a time, isolate by binary search over code and commits (git bisect), inputs,
  environment, and dependencies, then trace the root cause with 5 Whys and a fault tree. Also
  covers stack-trace anatomy, an error-pattern lookup table, and a debugger, profiler, and
  network tools reference.
license: MIT
metadata:
  author: AeyeOps
  version: "0.3.2"
  summary: Hypothesis-driven debugging from reproduction to root cause, isolating by bisection over code, inputs, environment, and dependencies.
---

# Systematic Debugging

## The Debugging Mindset

```markdown
Debugging is a scientific process:
1. Observe the symptom
2. Form a hypothesis about the cause
3. Design an experiment to test the hypothesis
4. Observe the result
5. Refine the hypothesis and repeat

Key principles:
- Change ONE thing at a time
- Verify assumptions — don't trust, verify
- Read the actual error message (carefully, fully)
- The bug is in your code, not the compiler (almost always)
- Recent changes are the most likely culprit
```

## Step 1: Reproduce the Issue

Before debugging, make the bug happen reliably.

```markdown
Reproduction checklist:
1. Can you trigger it on demand?
   - If yes → proceed to diagnosis
   - If no → gather more information first

2. Minimum reproduction:
   - Strip away unrelated code until you have the smallest case that fails
   - Remove dependencies, simplify inputs, reduce data
   - The smaller the repro, the faster you'll find the cause

3. Document the reproduction steps:
   - Environment: OS, language version, dependencies
   - Input data: exact values that trigger the bug
   - Steps: numbered, specific, repeatable
   - Expected: what should happen
   - Actual: what does happen (exact error, screenshot, log)

4. Intermittent bugs:
   - Record exact timestamps and conditions
   - Look for patterns: time of day, load level, data volume
   - Add logging to narrow the window
   - Consider race conditions, resource limits, garbage collection
```

## Step 2: Read the Error

Read the whole message and the whole stack trace before forming any hypothesis; the root
cause line is usually the deepest frame in your own code, not the last line printed.
[references/stack-traces.md](references/stack-traces.md) has the stack-trace anatomy and the
error-pattern table (TypeError, KeyError, ConnectionError, PermissionError, ImportError,
MemoryError) with the first check to make for each.

## Step 3: Hypothesis-Driven Debugging

### Form Hypotheses

```markdown
Start with the most likely causes:

1. What changed recently?
   - Code changes (git diff, git log)
   - Configuration changes
   - Dependency updates
   - Infrastructure changes
   - Data changes

2. Where is the failure?
   - Which component/layer fails?
   - Input side (bad data coming in) or output side (bad data going out)?
   - Your code or a dependency?

3. Hypothesis format:
   "I believe [cause] is responsible because [evidence].
    I will test this by [experiment].
    If I'm right, I expect [outcome]."
```

### Test Each Hypothesis

```markdown
Experiment techniques:
- Add targeted logging at the hypothesis point
- Use a debugger to inspect state at the failure
- Change one variable and observe the effect
- Comment out suspected code and see if behavior changes
- Use a known-good input to see if the path works at all
- Compare behavior between working and broken environments

Record results:
  Hypothesis: [description]
  Test: [what you did]
  Result: [what happened]
  Conclusion: Confirmed / Refuted / Inconclusive
  Next: [next hypothesis or deeper investigation]
```

## Step 4: Isolation Techniques

When no hypothesis stands out, or the failure site is unknown, bisect the problem space
instead of guessing. [references/isolation.md](references/isolation.md) covers binary search
over code and commits (`git bisect`), input isolation, environment isolation, and dependency
isolation, each with the commands to run.

## Step 5: Root Cause Analysis

A fix at the failure site is a patch; the root cause is the condition that let the failure
happen. [references/root-cause.md](references/root-cause.md) walks the 5 Whys and fault tree
analysis with worked examples.

## Debugging Tools

Logging, interactive debuggers (pdb, `node --inspect`), profilers, and network tools, with
their commands: [references/tools.md](references/tools.md).

## Debugging Checklist

```markdown
When you're stuck:
- [ ] Did you read the entire error message?
- [ ] Did you check the logs at the time of failure?
- [ ] Did you verify your assumptions about the state?
- [ ] Did you check what changed recently? (git diff, git log)
- [ ] Did you try a clean environment?
- [ ] Did you search for the exact error message online?
- [ ] Did you try the simplest possible input?
- [ ] Did you check the documentation for the failing function?
- [ ] Did you take a break? (Fresh eyes find bugs faster)
- [ ] Did you explain the problem to someone (rubber duck)?
```

## Keep this skill current

When a technique here fails in use, or a tool command no longer matches its current release, correct the step in the same session. Replace the superseded text; do not append a note.
