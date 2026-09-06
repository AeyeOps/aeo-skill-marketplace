# Root Cause Analysis

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
