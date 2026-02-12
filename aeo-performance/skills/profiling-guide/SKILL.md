---
name: profiling-guide
description: |
  Performance profiling methodologies, interpreting profiler output, and benchmarking techniques.
  Activate when: profiling application performance, reading flame graphs, benchmarking code,
  identifying bottlenecks, measuring CPU usage, analyzing memory allocation, I/O profiling.
---

# Performance Profiling Guide

## Profiling Methodology

```markdown
1. Define the goal:
   - What is slow? (specific endpoint, operation, user workflow)
   - How slow is it? (current measurement)
   - How fast should it be? (target)

2. Measure first:
   - Profile BEFORE optimizing (avoid optimizing the wrong thing)
   - Measure end-to-end, then narrow down
   - Use realistic data and load patterns

3. Identify the bottleneck:
   - Is it CPU-bound? (computation, parsing, serialization)
   - Is it I/O-bound? (disk, network, database)
   - Is it memory-bound? (allocation pressure, GC pauses, swapping)

4. Optimize the bottleneck:
   - Fix the biggest bottleneck first (Amdahl's Law)
   - Measure again after each change
   - Stop when the target is met
```

## CPU Profiling

### Python: cProfile

```python
# Command-line profiling
# python -m cProfile -s cumtime my_script.py

# Programmatic profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(20)  # Top 20 functions by cumulative time
```

### Interpreting cProfile Output

```markdown
Column meanings:
  ncalls    — Number of times the function was called
  tottime   — Time spent IN this function (excluding subfunctions)
  percall   — tottime / ncalls
  cumtime   — Time spent in this function INCLUDING subfunctions
  percall   — cumtime / ncalls
  filename  — File and function name

What to look for:
  High tottime  → This function itself is slow (optimize its code)
  High cumtime  → This function or something it calls is slow
  High ncalls   → Function called too many times (N+1 query, tight loop)
  tottime ≈ cumtime → Leaf function (doesn't call other slow things)
  tottime << cumtime → Time is spent in subfunctions (dig deeper)
```

### Python: py-spy (Sampling Profiler)

```bash
# Profile a running process (no code changes needed)
py-spy top --pid <PID>

# Generate flame graph
py-spy record -o profile.svg --pid <PID>

# Profile a command
py-spy record -o profile.svg -- python my_script.py
```

```markdown
py-spy advantages:
- No performance overhead on the profiled application
- Can attach to running processes
- Generates flame graphs directly
- No code modifications required
- Works with C extensions
```

### Line-Level Profiling

```python
# pip install line_profiler
# Decorate functions to profile
@profile  # Added by line_profiler
def slow_function(data):
    result = []
    for item in data:           # Line-by-line timing
        processed = transform(item)
        result.append(processed)
    return result

# Run with: kernprof -l -v my_script.py
```

```markdown
Output shows time per line:
  Line #    Hits     Time   Per Hit   % Time  Line Contents
       5    1000     500.0     0.5      2.0   for item in data:
       6    1000   20000.0    20.0     80.0     processed = transform(item)
       7    1000    4500.0     4.5     18.0     result.append(processed)

Interpretation:
- Line 6 uses 80% of the time → optimize transform()
- Line 7 uses 18% → consider pre-allocating the list
```

## Memory Profiling

### Python: tracemalloc

```python
import tracemalloc

tracemalloc.start()

# ... code that allocates memory ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)
```

### Python: memory_profiler

```python
# pip install memory_profiler
from memory_profiler import profile

@profile
def memory_heavy_function():
    data = [i ** 2 for i in range(1000000)]  # Shows memory per line
    filtered = [x for x in data if x % 2 == 0]
    return filtered

# Run with: python -m memory_profiler my_script.py
```

### Memory Profiling Patterns

```markdown
What to look for:
  Growing memory over time → Memory leak (objects not freed)
  Spike then release → Normal allocation pattern
  High baseline → Large data structures kept alive unnecessarily
  GC pauses → Too many short-lived objects

Common causes of high memory:
  - Loading entire files into memory (use streaming/generators)
  - Unbounded caches (use LRU with max size)
  - Circular references preventing garbage collection
  - String concatenation in loops (creates many intermediate strings)
  - Large query results not paginated
```

## I/O Profiling

### Database Query Profiling

```python
# SQLAlchemy query logging
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Django query logging
from django.db import connection
print(f"Queries executed: {len(connection.queries)}")
for query in connection.queries:
    print(f"  {query['time']}s: {query['sql'][:100]}")
```

```markdown
What to look for:
  N+1 queries:
    1 query for a list of users
    + N queries for each user's profile
    → Use eager loading (joinedload, prefetch_related)

  Slow queries:
    → Check EXPLAIN ANALYZE output
    → Look for sequential scans on large tables
    → Add indexes on filtered/joined columns

  Too many queries:
    → Batch operations (bulk insert, bulk update)
    → Use caching for frequently accessed data
    → Denormalize read-heavy data
```

### Network I/O Profiling

```markdown
Diagnosis tools:
  curl -w "@curl-timing.txt" <url>   # Detailed timing breakdown
  time python my_script.py           # Wall clock time vs CPU time

Timing breakdown:
  DNS lookup:        → Cache DNS, use connection pooling
  TCP connect:       → Use keep-alive connections
  TLS handshake:     → Use session resumption
  Time to first byte: → Server processing time
  Transfer time:     → Compression, payload size

If wall_time >> cpu_time:
  → Application is I/O bound (waiting on network, disk, or database)
  → Optimize by reducing I/O, adding concurrency, or caching
```

## Flame Graphs

### Reading Flame Graphs

```markdown
Anatomy:
  - X-axis: Proportion of time (NOT chronological)
  - Y-axis: Call stack depth (bottom = entry point, top = leaf functions)
  - Width of bar: Percentage of total time in that function
  - Color: Usually random or grouped by module (no special meaning)

How to read:
  1. Look at the widest bars at the TOP → most time-consuming leaf functions
  2. Look for "plateaus" → functions that take time themselves (not just calling others)
  3. Ignore narrow spikes → they're fast, don't optimize them
  4. Look for unexpected wide bars → functions you didn't expect to be slow

Common patterns:
  Wide plateau at top       → Single function is the bottleneck
  Many narrow columns       → Death by a thousand cuts (many small costs)
  Deep, narrow tower        → Deep recursion or call chain
  Wide bar in the middle    → Framework/library overhead
```

### Generating Flame Graphs

```bash
# Python (py-spy)
py-spy record -o flame.svg -- python my_script.py

# Node.js
node --prof my_script.js
node --prof-process isolate-*.log > processed.txt
# Use 0x: npx 0x my_script.js

# Generic (perf + FlameGraph)
perf record -g -- ./my_program
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```

## Benchmarking Techniques

### Microbenchmarking

```python
import timeit

# Benchmark a single expression
result = timeit.timeit(
    stmt="sorted(data)",
    setup="data = list(range(1000, 0, -1))",
    number=10000,
)
print(f"Average: {result / 10000 * 1000:.3f} ms")

# Compare two approaches
time_a = timeit.timeit("'-'.join(str(i) for i in range(100))", number=10000)
time_b = timeit.timeit("'-'.join(map(str, range(100)))", number=10000)
print(f"Generator: {time_a:.3f}s, Map: {time_b:.3f}s")
```

### Benchmarking Best Practices

```markdown
1. Warm up:
   - Run the code several times before measuring
   - JIT compilers, caches, and connection pools need warming

2. Multiple iterations:
   - Run many iterations and report median (not mean)
   - Report percentiles: P50, P95, P99
   - Show standard deviation to assess consistency

3. Realistic conditions:
   - Use production-like data sizes
   - Include realistic concurrency levels
   - Account for cold start vs warm state

4. Isolate variables:
   - Change one thing at a time
   - Compare apples to apples (same data, same machine)
   - Control for background processes and system load

5. Statistical significance:
   - Small differences (<5%) may be noise
   - Run enough iterations to be confident
   - Use statistical tests if making claims (t-test)

6. Avoid common pitfalls:
   - Dead code elimination (compiler removes unused results)
   - Constant folding (compiler pre-computes constant expressions)
   - Caching effects (second run is faster due to warm cache)
   - GC pauses (include GC time in measurements)
```

### Load Testing

```markdown
Tools:
  wrk:    wrk -t12 -c400 -d30s http://localhost:8080/api
  hey:    hey -n 10000 -c 100 http://localhost:8080/api
  k6:     k6 run load_test.js
  locust: Python-based, scriptable load testing

Key metrics:
  Throughput:     Requests per second (RPS)
  Latency:        P50, P95, P99 response times
  Error rate:     Percentage of failed requests
  Saturation:     CPU, memory, connection utilization

Load test patterns:
  Baseline:       Single user, measure per-request latency
  Ramp-up:        Gradually increase load until errors appear
  Stress:         Exceed expected capacity, observe degradation
  Soak:           Sustained load over hours (find memory leaks)
  Spike:          Sudden burst of traffic (test auto-scaling)
```

## Profiling Decision Tree

```markdown
Is it slow?
├── Measure end-to-end response time
├── Is most time in CPU?
│   ├── Yes → CPU profiler (cProfile, py-spy)
│   │   ├── Single hot function → Optimize algorithm
│   │   └── Many small costs → Look for N+1 patterns
│   └── No → I/O profiler
│       ├── Database → Query profiler (EXPLAIN ANALYZE)
│       ├── Network → Connection profiling (keep-alive, pooling)
│       └── Disk → I/O stats (iostat, strace)
├── Is memory growing?
│   ├── Yes → Memory profiler (tracemalloc, memory_profiler)
│   │   ├── Leak → Find unreleased references
│   │   └── High usage → Reduce data in memory (streaming, pagination)
│   └── No → Check GC pressure (many allocations/deallocations)
└── Is it intermittently slow?
    ├── GC pauses → Reduce allocation rate
    ├── Lock contention → Reduce lock scope
    └── Resource exhaustion → Check connection pools, file descriptors
```
