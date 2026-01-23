# Database Migrations

Patterns for safe, idempotent database migrations in Python CLI applications using PostgreSQL.

## Idempotent Migration Pattern

Migrations should be safe to run multiple times without errors or unintended side effects.

**Benefits:**
- Safe in CI/CD pipelines
- Easy rollback (re-run previous version)
- Development environment flexibility
- No "migration already applied" errors

---

## PostgreSQL IF NOT EXISTS Pattern

### Add Column

```sql
-- Safe to run multiple times
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        ALTER TABLE vendors ADD COLUMN custom_fields JSONB;
        COMMENT ON COLUMN vendors.custom_fields IS 'Custom fields with metadata';
        RAISE NOTICE 'Added custom_fields column';
    ELSE
        RAISE NOTICE 'custom_fields column already exists';
    END IF;
END $$;
```

### Create Table

```sql
-- Safe to run multiple times
CREATE TABLE IF NOT EXISTS vendors (
    id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(500),
    balance NUMERIC(15, 2),
    custom_fields JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Create Index

```sql
-- Safe to run multiple times
CREATE INDEX IF NOT EXISTS idx_vendors_custom_gin
ON vendors USING GIN (custom_fields);

CREATE INDEX IF NOT EXISTS idx_vendors_company_name
ON vendors (company_name);
```

### Add Constraint

```sql
-- Check if constraint exists before adding
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'vendors_balance_positive'
    ) THEN
        ALTER TABLE vendors
        ADD CONSTRAINT vendors_balance_positive CHECK (balance >= 0);
        RAISE NOTICE 'Added balance constraint';
    END IF;
END $$;
```

---

## Verification Steps

Verify migration succeeded:

```sql
-- Verify column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        RAISE EXCEPTION 'Migration failed - custom_fields column not created';
    ELSE
        RAISE NOTICE 'Migration verified - custom_fields exists';
    END IF;
END $$;

-- Verify index exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'vendors' AND indexname = 'idx_vendors_custom_gin'
    ) THEN
        RAISE EXCEPTION 'Migration failed - GIN index not created';
    ELSE
        RAISE NOTICE 'Migration verified - GIN index exists';
    END IF;
END $$;
```

---

## Python Migration Runner

### Basic Runner

```python
from sqlalchemy import text
from pathlib import Path

def run_migration(session, migration_file: Path):
    """Run SQL migration file

    Args:
        session: SQLAlchemy session
        migration_file: Path to .sql file

    Raises:
        Exception if migration fails
    """
    print(f"Running migration: {migration_file.name}")

    # Read SQL file
    with open(migration_file) as f:
        sql = f.read()

    try:
        # Execute SQL
        session.execute(text(sql))
        session.commit()
        print(f"✓ Migration successful: {migration_file.name}")
    except Exception as e:
        session.rollback()
        print(f"✗ Migration failed: {e}")
        raise

# Usage
session = get_session(settings)
migration_file = Path("scripts/migrate_add_custom_fields.sql")
run_migration(session, migration_file)
```

### Migration with Verification

```python
def run_migration_with_verification(session, migration_file, verify_fn=None):
    """Run migration and verify success

    Args:
        session: SQLAlchemy session
        migration_file: Path to .sql file
        verify_fn: Optional verification function

    Returns:
        Boolean indicating success
    """
    print(f"Running migration: {migration_file.name}")

    with open(migration_file) as f:
        sql = f.read()

    try:
        session.execute(text(sql))
        session.commit()

        # Run verification if provided
        if verify_fn:
            if not verify_fn(session):
                raise Exception("Verification failed")

        print(f"✓ Migration successful: {migration_file.name}")
        return True

    except Exception as e:
        session.rollback()
        print(f"✗ Migration failed: {e}")
        return False

# Verification function example
def verify_custom_fields_column(session):
    """Verify custom_fields column exists"""
    result = session.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    """))
    return result.rowcount > 0
```

---

## Complete Migration Example

**File:** `scripts/migrate_add_custom_fields.sql`

```sql
-- Idempotent migration to add JSONB columns for schema flexibility

-- Add custom_fields column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        ALTER TABLE vendors ADD COLUMN custom_fields JSONB;
        COMMENT ON COLUMN vendors.custom_fields IS 'Custom NetSuite fields (custentity_*) with lifecycle metadata';
        RAISE NOTICE 'Added custom_fields column to vendors table';
    ELSE
        RAISE NOTICE 'custom_fields column already exists in vendors table';
    END IF;
END $$;

-- Add raw_data column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'raw_data'
    ) THEN
        ALTER TABLE vendors ADD COLUMN raw_data JSONB;
        COMMENT ON COLUMN vendors.raw_data IS 'Complete NetSuite response for auditing';
        RAISE NOTICE 'Added raw_data column to vendors table';
    ELSE
        RAISE NOTICE 'raw_data column already exists in vendors table';
    END IF;
END $$;

-- Add schema_version column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'schema_version'
    ) THEN
        ALTER TABLE vendors ADD COLUMN schema_version INTEGER;
        COMMENT ON COLUMN vendors.schema_version IS 'Schema version at sync time';
        RAISE NOTICE 'Added schema_version column to vendors table';
    ELSE
        RAISE NOTICE 'schema_version column already exists in vendors table';
    END IF;
END $$;

-- Create GIN indexes
CREATE INDEX IF NOT EXISTS idx_vendors_custom_fields_gin
ON vendors USING GIN (custom_fields);

CREATE INDEX IF NOT EXISTS idx_vendors_raw_data_gin
ON vendors USING GIN (raw_data);

-- Verification
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        RAISE EXCEPTION 'Migration verification failed - custom_fields not created';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'vendors' AND indexname = 'idx_vendors_custom_fields_gin'
    ) THEN
        RAISE EXCEPTION 'Migration verification failed - GIN index not created';
    END IF;

    RAISE NOTICE 'Migration verification successful';
END $$;
```

---

## Migration Best Practices

### 1. Never DROP Columns

```sql
-- ✅ SAFE
ALTER TABLE records ADD COLUMN new_field VARCHAR;

-- ❌ DANGEROUS - Data loss!
ALTER TABLE records DROP COLUMN old_field;
```

**Why:** Fields may be temporarily removed from API, or data may be valuable for historical analysis.

### 2. Use Comments

```sql
COMMENT ON COLUMN vendors.custom_fields IS 'Custom NetSuite fields (custentity_*) with lifecycle metadata';
```

**Benefits:** Self-documenting schema, visible in database tools

### 3. Add Indexes Carefully

```sql
-- For JSONB columns
CREATE INDEX idx_name ON table USING GIN (jsonb_column);

-- For regular columns
CREATE INDEX idx_name ON table (column_name);

-- Partial index (only active records)
CREATE INDEX idx_name ON table (column) WHERE is_active = TRUE;
```

### 4. Transaction Safety

```sql
BEGIN;
  -- All migration operations
  ALTER TABLE ...
  CREATE INDEX ...
  -- Verify
COMMIT;
-- Atomicity: All or nothing
```

In Python migration runner, SQLAlchemy handles this automatically with session.commit/rollback.

---

## CLI Integration

### Init-DB Command

```python
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def init_db():
    """Initialize database schema with migrations"""
    session = get_session(settings)

    # Run migrations in order
    migrations = [
        Path("scripts/001_create_tables.sql"),
        Path("scripts/002_add_custom_fields.sql"),
        Path("scripts/003_add_indexes.sql"),
    ]

    for migration in migrations:
        if migration.exists():
            run_migration(session, migration)
        else:
            print(f"⚠ Migration file not found: {migration}")

    print("✓ Database initialized")
```

---

## Related Patterns

**This Skill:**
- [patterns/postgresql-jsonb.md](../patterns/postgresql-jsonb.md) - JSONB column patterns
- [patterns/schema-resilience.md](../patterns/schema-resilience.md) - 3-layer architecture

**NetSuite Integrations:**
- `patterns/schema-evolution.md` - NetSuite custom field evolution

---

## Summary

**Key Points:**

1. **Idempotent migrations** - Safe to run multiple times
2. **IF NOT EXISTS pattern** - PostgreSQL conditional operations
3. **Never DROP columns** - Additive migrations only
4. **Verification steps** - Confirm migration succeeded
5. **Comments for documentation** - Self-documenting schema
6. **Python runners** - Execute SQL with error handling
7. **CLI integration** - init-db command for setup

**Idempotent migrations prevent deployment failures and enable safe, repeatable database evolution.**
