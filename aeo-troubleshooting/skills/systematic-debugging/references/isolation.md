# Isolation Techniques

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
