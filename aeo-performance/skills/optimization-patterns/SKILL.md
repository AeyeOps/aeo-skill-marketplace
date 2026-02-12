---
name: optimization-patterns
description: |
  Caching strategies, database optimization, algorithmic complexity, and when NOT to optimize.
  Activate when: optimizing performance, implementing caching, fixing N+1 queries,
  improving database queries, reducing latency, choosing data structures, deciding whether to optimize.
---

# Optimization Patterns

## When NOT to Optimize

```markdown
The first rule of optimization: DON'T.
The second rule: DON'T YET. (Measure first.)

Do NOT optimize when:
- You haven't measured (you're guessing where the bottleneck is)
- The code is fast enough for current and near-future requirements
- The optimization makes the code significantly harder to understand
- The optimization saves microseconds in code that runs once
- You're prematurely abstracting "for performance"

DO optimize when:
- Users are experiencing measurable latency or failures
- Profiling shows a clear bottleneck (not a hunch)
- The system can't scale to meet known upcoming load
- SLA/SLO targets are being missed
- Resource costs are growing unsustainably

Optimization checklist:
1. Define the performance target (response time, throughput, resource usage)
2. Measure current performance against the target
3. Profile to find the bottleneck
4. Optimize the bottleneck
5. Measure again to verify improvement
6. Stop when the target is met
```

## Caching Strategies

### Cache Hierarchy

```markdown
Level 1: In-process cache (dict, LRU cache)
  Speed: ~1 ns
  Size: Limited by process memory
  Scope: Single process
  Use for: Computed values, parsed configs, small lookup tables

Level 2: Local distributed cache (Redis, Memcached)
  Speed: ~1 ms
  Size: Gigabytes
  Scope: Shared across processes/services
  Use for: Session data, API responses, database query results

Level 3: CDN / Edge cache
  Speed: ~10-100 ms
  Size: Terabytes
  Scope: Geographically distributed
  Use for: Static assets, API responses for anonymous users

Level 4: Browser cache
  Speed: ~0 ms (no network)
  Size: Varies
  Scope: Single user
  Use for: Static assets, SPA bundles, images
```

### Cache Invalidation Patterns

```markdown
Time-based (TTL):
  - Set expiration time on cached entries
  - Simple but stale data possible during TTL window
  - Good for: data that can be slightly stale (product listings, news)

Event-based:
  - Invalidate cache when underlying data changes
  - Always fresh but requires invalidation infrastructure
  - Good for: data that must be current (user profiles, inventory counts)

Write-through:
  - Write to cache AND database simultaneously
  - Cache is always current
  - Higher write latency, simpler read logic

Write-behind:
  - Write to cache first, async write to database
  - Lower write latency, risk of data loss
  - Good for: high-write scenarios where loss is acceptable (metrics, logs)

Cache-aside (Lazy Loading):
  - On miss: read from DB, write to cache, return
  - On hit: return from cache
  - Most common pattern for read-heavy workloads
```

### Python LRU Cache

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def expensive_computation(key: str) -> dict:
    # Result is cached based on arguments
    return perform_heavy_calculation(key)

# Monitor cache performance
print(expensive_computation.cache_info())
# CacheInfo(hits=950, misses=50, maxsize=1024, currsize=50)

# Clear when needed
expensive_computation.cache_clear()
```

### Cache Pitfalls

```markdown
Cache stampede:
  Problem: TTL expires, 1000 requests hit the database simultaneously
  Fix: Lock so only one request rebuilds cache; others wait or serve stale

Cache poisoning:
  Problem: Bad data gets cached, served to all users
  Fix: Validate before caching, add manual purge capability

Unbounded cache:
  Problem: Cache grows until OOM
  Fix: Always set maxsize; use LRU eviction

Over-caching:
  Problem: Everything cached, hard to debug stale data
  Fix: Only cache what profiling shows is a bottleneck
```

## Database Query Optimization

### N+1 Query Detection and Fix

```markdown
The N+1 problem:
  1 query: SELECT * FROM orders                     (fetch all orders)
  N queries: SELECT * FROM products WHERE id = ?    (one per order item)
  Total: N+1 queries for N items → linear growth with data

Detection:
- Log query count per request (Django: django-debug-toolbar)
- Look for repeated identical queries with different parameters
- Profile with SQLAlchemy echo=True
```

```python
# N+1 PROBLEM: One query per order's items
orders = session.query(Order).all()
for order in orders:
    print(order.items)  # Each access triggers a new query

# FIXED: Eager loading with joinedload
from sqlalchemy.orm import joinedload
orders = session.query(Order).options(joinedload(Order.items)).all()
for order in orders:
    print(order.items)  # Already loaded, no additional queries

# FIXED: Subquery loading (better for large result sets)
from sqlalchemy.orm import subqueryload
orders = session.query(Order).options(subqueryload(Order.items)).all()
```

### Index Strategy

```markdown
When to add an index:
- Column used in WHERE clauses frequently
- Column used in JOIN conditions
- Column used in ORDER BY
- Column with high selectivity (many unique values)

When NOT to add an index:
- Column with few unique values (boolean, status with 3 values)
- Table with very few rows (< 1000)
- Column that's written more than read
- Table that needs maximum insert throughput

Index types:
  B-tree (default): General purpose, equality and range queries
  Hash: Equality only, faster for exact matches
  GIN: Full-text search, array/JSONB containment
  BRIN: Very large tables with natural ordering (timestamps)

Checking if indexes are used:
  EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'pending';
  Look for "Index Scan" (good) vs "Seq Scan" (bad on large tables)
```

### Query Optimization Checklist

```markdown
- [ ] Use EXPLAIN ANALYZE to understand query plan
- [ ] Add indexes for frequently filtered/joined columns
- [ ] Select only needed columns (avoid SELECT *)
- [ ] Use LIMIT for paginated results
- [ ] Avoid functions on indexed columns in WHERE (breaks index usage)
- [ ] Batch bulk operations (INSERT ... VALUES (a), (b), (c))
- [ ] Use connection pooling (pgbouncer, SQLAlchemy pool)
- [ ] Denormalize read-heavy data (materialized views)
- [ ] Avoid DISTINCT when a better join eliminates duplicates
- [ ] Use EXISTS instead of COUNT(*) when checking presence
```

## Algorithmic Complexity

### Big-O Quick Reference

```markdown
O(1)        — Constant: hash lookup, array access by index
O(log n)    — Logarithmic: binary search, balanced tree operations
O(n)        — Linear: single pass through data, linear search
O(n log n)  — Linearithmic: efficient sorting (merge sort, timsort)
O(n²)       — Quadratic: nested loops, naive string matching
O(2^n)      — Exponential: brute-force subsets, naive Fibonacci
O(n!)       — Factorial: brute-force permutations

Practical impact (n = 1,000,000):
  O(1):       1 operation
  O(log n):   20 operations
  O(n):       1,000,000 operations
  O(n log n): 20,000,000 operations
  O(n²):      1,000,000,000,000 operations ← too slow
```

### Common Optimization Patterns

```python
# O(n²) → O(n) with a set for lookups
# BAD: Check if item exists in list (O(n) per check × O(n) items = O(n²))
duplicates = []
for item in items:
    if item in items_list:  # O(n) scan
        duplicates.append(item)

# GOOD: Convert to set first (O(1) per lookup)
items_set = set(items_list)  # O(n) one-time cost
duplicates = [item for item in items if item in items_set]  # O(n)

# O(n²) → O(n) with a dictionary for grouping
# BAD: Group items by category (nested loop)
for category in categories:
    group = [item for item in items if item.category == category]

# GOOD: Single-pass grouping with defaultdict
from collections import defaultdict
groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)
```

### Data Structure Selection

```markdown
Need fast lookup by key?
  → dict (O(1) average)

Need fast membership testing?
  → set (O(1) average)

Need ordered data with fast insert/delete?
  → list (if small), sorted containers (if large)

Need FIFO queue?
  → collections.deque (O(1) append and popleft)
  → NOT list (list.pop(0) is O(n))

Need priority queue?
  → heapq (O(log n) push and pop)

Need counting?
  → collections.Counter
```

## Lazy Loading

```markdown
Load data only when it's actually needed, not upfront.

Patterns:
  Lazy initialization:
    - Don't compute until first access
    - Cache the result for subsequent accesses

  Pagination:
    - Load 20 items per page, not 10,000 at once
    - Use cursor-based pagination for large datasets

  Generators (Python):
    - yield items one at a time instead of building a list
    - Processes data in constant memory regardless of size

  Virtual scrolling (UI):
    - Only render visible rows in a table
    - Load more as user scrolls
```

```python
# Eager: loads ALL records into memory
def get_all_records():
    return list(db.query("SELECT * FROM huge_table"))  # OOM risk

# Lazy: yields records one at a time
def get_all_records():
    cursor = db.execute("SELECT * FROM huge_table")
    for row in cursor:  # Fetches in batches from database
        yield row
```

## Connection Pooling

```markdown
Problem: Opening a new database connection per request is slow (~50ms).
Solution: Maintain a pool of open connections and reuse them.

Pool configuration:
  min_connections:  Minimum idle connections (keep warm)
  max_connections:  Maximum total connections (prevent overload)
  max_idle_time:    Close idle connections after this duration
  connection_timeout: Wait this long for a free connection
  max_lifetime:     Recycle connections to prevent staleness

Sizing guidelines:
  pool_size = expected_concurrent_requests × avg_queries_per_request
  But: don't exceed database max_connections / number_of_app_instances
  Rule of thumb: Start with 5-10 per instance, adjust based on monitoring
```

```python
# SQLAlchemy connection pool
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,          # 10 connections in pool
    max_overflow=20,       # Allow up to 20 extra under load
    pool_timeout=30,       # Wait 30s for a connection
    pool_recycle=1800,     # Recycle connections every 30 min
    pool_pre_ping=True,    # Test connections before using
)
```

## Performance Anti-Patterns

```markdown
Premature optimization:
  "We might need this to handle 10M users" (you have 100)
  → Optimize when you have evidence, not speculation

Optimizing the wrong thing:
  Spending a week optimizing a function that takes 1% of total time
  → Profile first, optimize the bottleneck (Amdahl's Law)

Micro-optimizing in a macro-slow system:
  Inlining functions while the database query takes 2 seconds
  → Fix the big rocks before polishing pebbles

Caching everything:
  Adding Redis caching when the database query is 5ms
  → Caching adds complexity; only cache if it solves a real problem

Copy-paste parallelism:
  Making code async/parallel without measuring if I/O is the bottleneck
  → Concurrency helps I/O-bound work, not CPU-bound work

Choosing clever over clear:
  Bit manipulation tricks that save 2ns but confuse every reader
  → Readable code is maintainable code; only get clever in hot loops
```
