# Stack Traces and Error Patterns

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
