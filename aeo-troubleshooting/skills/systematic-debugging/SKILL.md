---
name: systematic-debugging
description: |
  Root cause analysis, hypothesis-driven debugging, and isolation techniques.
  Activate when: debugging an issue, reading stack traces, performing root cause analysis,
  troubleshooting errors, reproducing bugs, isolating failures, binary search debugging.
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

### Stack Trace Anatomy

```markdown
Reading a stack trace (bottom-up for most languages):

  Traceback (most recent call last):        ← Start reading here (most recent)
    File "app.py", line 45, in main         ← Entry point
      result = process_data(raw_input)
    File "processor.py", line 23, in process_data  ← Called from main
      validated = validate(data)
    File "validator.py", line 12, in validate      ← Called from process_data
      raise ValueError("Field 'email' missing")   ← ROOT CAUSE
  ValueError: Field 'email' missing                ← Error type and message

Key information to extract:
1. Error type (ValueError, TypeError, NullPointerException)
2. Error message (the specific complaint)
3. File and line number of the failure
4. The call chain that led to the failure
5. Which layer of YOUR code (not library code) is nearest to the error
```

### Common Error Patterns

```markdown
TypeError / AttributeError:
  → Variable is wrong type or None
  → Check: what is the actual value? Add print/log before the failing line

KeyError / IndexError:
  → Accessing data that doesn't exist
  → Check: what are the actual keys/indices? Log the container contents

ConnectionError / TimeoutError:
  → Network or service issue
  → Check: is the service running? Is the URL correct? DNS resolving?

PermissionError:
  → File system or OS-level access denied
  → Check: file ownership, permissions, SELinux context

ImportError / ModuleNotFoundError:
  → Missing or misconfigured dependency
  → Check: is it installed? Right virtual environment? Correct version?

MemoryError / OOM:
  → Resource exhaustion
  → Check: data size, unbounded loops, missing pagination, leaked resources
```

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

### Binary Search Debugging

When you don't know where the bug is, bisect the problem space.

```markdown
Code bisection:
1. Identify a known-good point and a known-bad point
2. Test the midpoint
3. If midpoint is good → bug is in the second half
4. If midpoint is bad → bug is in the first half
5. Repeat until you find the exact line/commit

Git bisect (for regression bugs):
  git bisect start
  git bisect bad HEAD           # Current is broken
  git bisect good v1.2.0        # This version worked
  # Git checks out midpoint — test it
  git bisect good               # or "git bisect bad"
  # Repeat until Git identifies the commit

Code comment bisection:
1. Comment out the bottom half of the suspect code
2. If bug disappears → it's in the commented half
3. If bug remains → it's in the uncommented half
4. Repeat within the narrowed section
```

### Input Isolation

```markdown
Narrow down which input triggers the bug:

1. Test with minimal input (empty, single item)
2. Test with known-good input
3. Gradually add complexity until the bug appears
4. The last addition is the trigger

For data-driven bugs:
- Compare working and failing input sets
- Diff the inputs to find the difference
- Test each difference independently
- Check for encoding issues, special characters, edge values
```

### Environment Isolation

```markdown
Determine if the bug is environment-specific:

1. Does it reproduce locally? In staging? In production only?
2. Compare: OS, language version, dependency versions
3. Check: environment variables, configuration files, secrets
4. Test in a clean environment (fresh container, new virtualenv)
5. If environment-specific, diff the configurations

Common environment differences:
- Different dependency versions (check lock files)
- Missing environment variables or secrets
- File path differences (Windows vs Unix)
- Timezone and locale settings
- Resource limits (memory, file descriptors, CPU)
- Network configuration (proxies, DNS, firewalls)
```

### Dependency Isolation

```markdown
Determine if a dependency is the cause:

1. Check if the dependency was recently updated
2. Pin to the previous version and test
3. Read the dependency's changelog for breaking changes
4. Search the dependency's issue tracker for similar reports
5. Create a minimal reproduction using only the dependency

Dependency debugging tools:
- pip freeze / npm list → exact installed versions
- git log -- requirements.txt → when dependencies changed
- pip show [package] → version and location
- pip install [package]==old.version → test previous version
```

## Step 5: Root Cause Analysis

### The 5 Whys

```markdown
Start with the symptom and ask "Why?" repeatedly:

Symptom: The API returns 500 errors intermittently.
Why? → The database query times out.
Why? → The query scans the entire table (no index).
Why? → The index was dropped during a migration.
Why? → The migration script had a DROP INDEX without a corresponding CREATE.
Why? → Migration code review didn't catch the missing index recreation.

Root cause: Migration review process doesn't check for index preservation.
Fix: Add migration checklist item for index verification.
```

### Fault Tree Analysis

```markdown
Work backwards from the failure:

API returns 500
├── Database error
│   ├── Connection timeout
│   │   ├── Pool exhausted (connections leaked?)
│   │   └── Network latency spike
│   └── Query error
│       ├── Schema mismatch (migration issue?)
│       └── Data integrity violation
├── Application error
│   ├── Null pointer (missing data?)
│   ├── Logic error (wrong branch?)
│   └── Resource exhaustion (memory/disk?)
└── Infrastructure error
    ├── Service down
    ├── DNS failure
    └── Certificate expired
```

## Debugging Tools Quick Reference

```markdown
Print/Log debugging:
  - Add log statements before and after suspect code
  - Log variable values, types, and lengths
  - Use structured logging (key=value pairs)
  - Remove debug logs after fixing (or use debug log level)

Interactive debugger:
  Python: import pdb; pdb.set_trace()  (or breakpoint())
  Node.js: debugger; statement + --inspect flag
  Java: IDE breakpoints (IntelliJ, Eclipse)

  Debugger commands (pdb):
    n (next)     — step over
    s (step)     — step into
    c (continue) — run to next breakpoint
    p expr       — print expression
    pp expr      — pretty print
    w (where)    — show stack trace
    l (list)     — show source code

Profilers (when the bug is performance):
  Python: cProfile, py-spy, line_profiler
  Node.js: --prof, clinic.js
  General: flame graphs, perf

Network debugging:
  curl -v  — verbose HTTP request/response
  dig/nslookup — DNS resolution
  traceroute — network path
  tcpdump/Wireshark — packet capture
```

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
