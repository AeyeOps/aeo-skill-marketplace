---
name: common-failure-patterns
description: |
  Common failure patterns organized by category with symptoms, causes, and fixes.
  Activate when: diagnosing dependency conflicts, environment issues, PATH problems,
  permission errors, CORS errors, DNS failures, timeout issues, async bugs,
  concurrency problems, race conditions, memory leaks, deadlocks.
---

# Common Failure Patterns

## Dependency Conflicts

### Version Mismatch
```markdown
Symptoms:
- ImportError or ModuleNotFoundError at runtime
- "No matching distribution found" during install
- Tests pass locally but fail in CI
- AttributeError on functions that "should exist"

Diagnosis:
  pip freeze | grep <package>    # What's actually installed?
  pip show <package>             # Version + dependencies
  pip check                      # Dependency compatibility check
  npm ls <package>               # Node dependency tree
  npm ls --all 2>&1 | grep ERR   # Find conflicts

Common causes:
- Lock file not committed (pip.lock, yarn.lock, package-lock.json)
- Different Python/Node version between local and CI
- Transitive dependency updated with breaking change
- Multiple packages requiring conflicting versions

Fixes:
- Pin exact versions in requirements.txt / package.json
- Use lock files and commit them to version control
- Use virtual environments to isolate project dependencies
- Run pip install --upgrade --force-reinstall <package>
- For Node: delete node_modules and reinstall
```

### Diamond Dependency Problem
```markdown
Symptoms:
- "Conflicting dependencies" during installation
- Package A requires X>=2.0 but Package B requires X<2.0

Fixes:
1. Check if newer versions of A or B resolve the conflict
2. Use dependency resolution tools (pip-compile, npm dedupe)
3. Fork and patch the more restrictive package
4. Replace one of the conflicting packages with an alternative
```

## Environment Issues

### PATH Problems
```markdown
Symptoms:
- "command not found" for installed tools
- Wrong version of a tool runs (which python → unexpected path)
- Works in one terminal but not another
- Works for one user but not another

Diagnosis:
  which <command>           # Where is it found?
  echo $PATH                # What's in PATH?
  type <command>            # Is it alias, function, or binary?
  env | grep PATH           # Full PATH variable
  ls -la $(which <command>) # Symlink target

Common causes:
- Tool installed in user directory but PATH has system directory first
- Shell profile (.bashrc, .zshrc) not sourced in this session
- Different shell (bash vs zsh) with different profiles
- Virtual environment not activated
- PATH modified by a tool installer without restarting shell

Fixes:
- Add the correct directory to PATH in your shell profile
- Source the profile: source ~/.bashrc or source ~/.zshrc
- Use absolute paths as a temporary fix
- Check for conflicting PATH entries (earlier entries win)
```

### Permission Errors
```markdown
Symptoms:
- "Permission denied" on file operations
- "EACCES" (Node.js), PermissionError (Python)
- Works as root but not as regular user
- Works locally but fails in container/CI

Diagnosis:
  ls -la <file>               # Check owner and permissions
  stat <file>                 # Detailed file attributes
  id                          # Current user and groups
  namei -l <path>             # Permissions on entire path chain
  getfacl <file>              # ACL permissions (if applicable)

Common causes:
- File created by root or different user
- Directory missing execute permission (can't traverse)
- Mounted volume with restrictive permissions
- SELinux or AppArmor blocking access
- umask setting creating restrictive default permissions

Fixes:
  chmod 644 <file>            # Read/write for owner, read for others
  chmod 755 <directory>       # Execute needed to enter directories
  chown user:group <file>     # Change ownership
  # In Docker: run as non-root user matching host UID
  # In CI: check runner user and directory permissions
```

### Environment Variable Issues
```markdown
Symptoms:
- KeyError or "environment variable not set"
- Application uses wrong configuration (staging vs production)
- Works in terminal but fails as a service/cron job

Diagnosis:
  env | grep <VAR>            # Is it set?
  printenv <VAR>              # Value of specific variable
  # In Python: os.environ.get('VAR', 'default')
  # In Node: process.env.VAR

Common causes:
- Variable set in shell but not exported (export VAR=value)
- Variable set in .bashrc but process started differently
- .env file not loaded (missing dotenv setup)
- Docker container missing --env or --env-file
- CI/CD secrets not configured for this environment

Fixes:
- Use .env files with a loader (python-dotenv, dotenv for Node)
- Set in systemd service file, Docker Compose, or CI config
- Fail fast with clear error message if required var is missing
- Document required environment variables in README or .env.example
```

## Network Errors

### CORS Errors
```markdown
Symptoms:
- "Access-Control-Allow-Origin" error in browser console
- API works from curl/Postman but fails from browser
- Preflight OPTIONS request returns 403 or missing headers
- "has been blocked by CORS policy"

This is a BROWSER-ONLY issue — the server must set headers.

Diagnosis:
  # Check response headers
  curl -I -X OPTIONS https://api.example.com/endpoint \
    -H "Origin: https://yoursite.com" \
    -H "Access-Control-Request-Method: POST"

Required server response headers:
  Access-Control-Allow-Origin: https://yoursite.com  (or * for public APIs)
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE
  Access-Control-Allow-Headers: Content-Type, Authorization
  Access-Control-Allow-Credentials: true  (if sending cookies)

Common causes:
- Backend missing CORS middleware
- Allowed origins list doesn't include the frontend URL
- Credentials mode enabled but origin is wildcard (*)
- Preflight (OPTIONS) request not handled by server
- Reverse proxy stripping CORS headers

Fixes:
- Add CORS middleware to backend (flask-cors, cors npm package)
- Configure allowed origins explicitly (avoid * in production)
- Ensure OPTIONS requests reach your CORS handler
- Check proxy/CDN configuration isn't stripping headers
```

### DNS Failures
```markdown
Symptoms:
- "Could not resolve hostname"
- "getaddrinfo ENOTFOUND"
- "Name or service not known"
- Works with IP address but not hostname

Diagnosis:
  dig <hostname>              # DNS resolution details
  nslookup <hostname>         # Simple DNS lookup
  host <hostname>             # Another DNS query tool
  cat /etc/resolv.conf        # DNS server configuration
  ping <hostname>             # Basic connectivity test

Common causes:
- DNS server is down or unreachable
- Hostname is misspelled
- DNS record doesn't exist or hasn't propagated
- /etc/resolv.conf points to wrong DNS server
- Docker container using wrong DNS configuration
- VPN or firewall blocking DNS queries

Fixes:
- Verify hostname spelling
- Try alternative DNS (8.8.8.8, 1.1.1.1)
- Check DNS record exists: dig <hostname> @8.8.8.8
- In Docker: set --dns flag or configure daemon DNS
- Wait for DNS propagation (TTL, typically minutes to hours)
```

### Timeout Errors
```markdown
Symptoms:
- "Connection timed out" (can't establish connection)
- "Read timed out" (connected but no response)
- "Gateway Timeout" (502/504 from proxy)
- Request hangs for a long time then fails

Diagnosis:
  # Test basic connectivity
  telnet <host> <port>
  nc -zv <host> <port>

  # Measure response time
  curl -o /dev/null -w "Total: %{time_total}s\n" <url>

  # Trace network path
  traceroute <host>

Common causes:
- Server is overloaded or down
- Firewall blocking the port
- Client timeout set too low for the operation
- Network latency between client and server
- DNS resolution is slow
- Connection pool exhausted
- Backend processing takes too long (slow query, heavy computation)

Fixes:
- Increase timeout for legitimately slow operations
- Add connection pooling and reuse
- Implement retry with exponential backoff
- Add circuit breaker to prevent cascade failures
- Optimize slow server-side operations
- Check firewall rules (security groups, iptables)
```

## Async and Concurrency Bugs

### Race Conditions
```markdown
Symptoms:
- Bug appears intermittently under load
- Result depends on timing or order of operations
- Works single-threaded but fails multi-threaded
- "Lost updates" — data written then overwritten

Classic example:
  Thread A: read balance (100)
  Thread B: read balance (100)
  Thread A: write balance (100 + 50 = 150)
  Thread B: write balance (100 - 30 = 70)   ← Thread A's write is lost!

Diagnosis:
- Add timestamps to logs and correlate concurrent operations
- Increase concurrency to make the race more likely
- Use thread-sanitizer or race-condition detection tools
- Look for shared mutable state accessed without synchronization

Fixes:
- Use locks/mutexes for shared state: with lock: ...
- Use atomic operations where available
- Use database transactions with appropriate isolation level
- Apply optimistic locking (version column, compare-and-swap)
- Redesign to avoid shared mutable state (message passing, queues)
```

### Deadlocks
```markdown
Symptoms:
- Application freezes/hangs completely
- No error message — just stops responding
- CPU is idle but application makes no progress
- Threads waiting on each other

Classic pattern:
  Thread A: locks Resource 1, waits for Resource 2
  Thread B: locks Resource 2, waits for Resource 1
  → Neither can proceed

Diagnosis:
- Thread dump: kill -3 <pid> (Java), faulthandler (Python)
- Database: SELECT * FROM pg_locks WHERE NOT granted;
- Look for circular dependencies in lock acquisition

Fixes:
- Always acquire locks in a consistent global order
- Use timeouts on lock acquisition
- Use try-lock with fallback
- Reduce lock scope (hold locks for minimum time)
- Use lock-free data structures where possible
- In databases: keep transactions short, access tables in consistent order
```

### Unhandled Promise/Async Errors
```markdown
Symptoms:
- "UnhandledPromiseRejection" (Node.js)
- Silent failures (async code fails but nothing logs it)
- "RuntimeWarning: coroutine was never awaited" (Python)
- Function returns before async work completes

Common causes:
- Missing await keyword
- Missing .catch() on Promise chain
- async function called without await (fire-and-forget)
- Error thrown inside callback but not propagated

Fixes:
  # JavaScript
  ✗ fetchData()                    # Missing await
  ✓ await fetchData()
  ✓ fetchData().catch(handleError)

  # Python
  ✗ asyncio.create_task(work())    # Error lost if work() fails
  ✓ task = asyncio.create_task(work())
    task.add_done_callback(handle_error)
```

## Memory Leaks

### Symptoms
```markdown
- Memory usage grows steadily over time
- Application gets slower over time
- OOM (Out of Memory) kills after hours/days of running
- Garbage collector runs more frequently
```

### Common Causes

```markdown
Event listeners not removed:
  ✗ element.addEventListener('click', handler)  # Never removed
  ✓ Cleanup: element.removeEventListener('click', handler)

Growing collections:
  ✗ cache = {}  # Keys added, never evicted
  ✓ Use LRU cache with max size

Closures holding references:
  ✗ Large objects referenced by closures that outlive their usefulness
  ✓ Set references to null when no longer needed

Circular references (in non-GC languages):
  ✗ A references B, B references A → neither freed
  ✓ Use weak references or explicit cleanup

Database connections not closed:
  ✗ conn = db.connect()  # Never closed
  ✓ with db.connect() as conn:  # Auto-cleanup via context manager
```

### Diagnosis

```markdown
Python:
  tracemalloc.start()          # Track memory allocations
  objgraph.show_most_common_types()  # Find leaked objects
  gc.get_referrers(obj)        # What holds a reference?

Node.js:
  --inspect + Chrome DevTools → Memory tab → Heap snapshots
  Compare two snapshots to find growing objects

General:
  Monitor RSS (Resident Set Size) over time
  If it grows without bound → leak
  If it grows then levels off → just needs more memory
```
