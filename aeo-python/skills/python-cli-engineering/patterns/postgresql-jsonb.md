# PostgreSQL JSONB for Schema Flexibility

Patterns for using PostgreSQL JSONB columns to handle evolving schemas, custom fields, and unknown data structures in Python CLI applications.

## When to Use JSONB

Use JSONB columns when:
- **Schema evolves frequently** (custom fields added/removed)
- **Unknown fields need capture** (complete API responses)
- **Flexibility over validation** (business rules change)
- **Preserve historical data** (field lifecycle tracking)

**Don't use JSONB when:**
- Schema is stable and well-known
- Type safety is critical
- Performance requirements are extreme
- Simple key-value storage sufficient

---

## Hybrid Schema Pattern (Recommended)

Combine typed columns for stable fields with JSONB for flexible fields.

### Database Schema

```sql
CREATE TABLE vendors (
    -- Typed columns (known, stable fields)
    id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(500),
    email VARCHAR(255),
    balance NUMERIC(15, 2),
    is_inactive BOOLEAN DEFAULT FALSE,
    last_modified_date TIMESTAMP,

    -- JSONB columns (flexible, evolving fields)
    custom_fields JSONB,  -- Business-specific custom fields
    raw_data JSONB,       -- Complete source data for audit

    -- Metadata
    synced_at TIMESTAMP DEFAULT NOW(),
    schema_version INTEGER
);

-- GIN index for fast JSONB queries
CREATE INDEX idx_vendors_custom_gin ON vendors USING GIN (custom_fields);
```

### SQLAlchemy Model

```python
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSONB, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class VendorRecord(Base):
    __tablename__ = "vendors"

    # Typed columns (fast queries, type-safe)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    company_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    is_inactive: Mapped[bool] = mapped_column(Boolean, default=False)
    last_modified_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # JSONB columns (flexible, schema-resilient)
    custom_fields: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom fields with metadata (custentity_* from NetSuite)"
    )
    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Complete source response for auditing"
    )

    # Metadata
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    schema_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

### Benefits

**Typed columns:**
- Fast queries (B-tree indexes)
- Type safety (database enforced)
- IDE autocomplete
- Clear schema documentation

**JSONB columns:**
- Schema flexibility (no migrations for new fields)
- Capture everything (no data loss)
- Still queryable (GIN indexes)
- Historical preservation

---

## JSONB Indexing

### GIN Index (Recommended)

**Generalized Inverted Index** - optimized for JSONB queries.

```sql
-- Create GIN index
CREATE INDEX idx_vendors_custom_gin ON vendors USING GIN (custom_fields);

-- Query performance comparable to typed columns
SELECT * FROM vendors WHERE custom_fields->>'region' = 'West';
-- Uses GIN index, fast!
```

**When to use:**
- Querying by JSONB values frequently
- JSONB columns > 100KB
- Need fast lookups

### Partial GIN Index

Index only active (non-deprecated) fields:

```sql
CREATE INDEX idx_vendors_active_custom ON vendors
USING GIN (custom_fields)
WHERE (custom_fields->'region'->>'deprecated')::boolean IS FALSE;
```

**Benefits:**
- Smaller index (faster updates)
- Only indexes relevant data

---

## Querying JSONB

### Basic Operators

```sql
-- Get text value (->>'key')
SELECT * FROM vendors
WHERE custom_fields->>'region' = 'West';

-- Get JSON value (->'key')
SELECT custom_fields->'region' FROM vendors;

-- Check key exists (?'key')
SELECT * FROM vendors
WHERE custom_fields ? 'region';

-- Contains (@>)
SELECT * FROM vendors
WHERE custom_fields @> '{"region": "West"}'::jsonb;
```

### SQLAlchemy Queries

```python
from sqlalchemy import func

# Simple equality
vendors = session.query(VendorRecord).filter(
    VendorRecord.custom_fields['region'].astext == 'West'
).all()

# With lifecycle metadata (nested path)
vendors = session.query(VendorRecord).filter(
    func.jsonb_extract_path_text(
        VendorRecord.custom_fields,
        'region',
        'value'
    ) == 'West'
).all()

# Check field exists
vendors = session.query(VendorRecord).filter(
    VendorRecord.custom_fields.has_key('region')
).all()

# Contains check
vendors = session.query(VendorRecord).filter(
    VendorRecord.custom_fields.contains({'region': 'West'})
).all()
```

### Helper Functions

```python
from sqlalchemy import text

class CustomFieldQuery:
    """Helper functions for querying JSONB fields"""

    @staticmethod
    def get_by_custom_field(session, model, field_name, field_value):
        """Query by custom field value"""
        return session.query(model).filter(
            func.jsonb_extract_path_text(
                model.custom_fields,
                field_name,
                'value'
            ) == str(field_value)
        ).all()

    @staticmethod
    def list_all_fields(session, model):
        """List all custom fields with counts"""
        table_name = model.__tablename__

        result = session.execute(text(f"""
            SELECT
                jsonb_object_keys(custom_fields) as field_name,
                COUNT(*) as count
            FROM {table_name}
            WHERE custom_fields IS NOT NULL
            GROUP BY field_name
            ORDER BY count DESC
        """))

        return {row.field_name: row.count for row in result}

    @staticmethod
    def get_field_value(custom_fields, field_name, default=None):
        """Extract field value from JSONB with metadata

        Args:
            custom_fields: JSONB dict from database
            field_name: Field to extract
            default: Default if not found

        Returns:
            Field value or default
        """
        if not custom_fields or field_name not in custom_fields:
            return default

        field_data = custom_fields[field_name]

        # Handle lifecycle metadata
        if isinstance(field_data, dict) and 'value' in field_data:
            return field_data['value']

        # Direct value
        return field_data
```

---

## Storing Data in JSONB

### Simple Values

```python
# Store simple JSONB
vendor = VendorRecord(
    id="123",
    company_name="Acme Corp",
    custom_fields={
        "region": "West",
        "payment_method": "ACH",
        "credit_rating": "A+"
    }
)
session.add(vendor)
session.commit()
```

### With Lifecycle Metadata

```python
from datetime import datetime

# Store with metadata
vendor = VendorRecord(
    id="123",
    company_name="Acme Corp",
    custom_fields={
        "region": {
            "value": "West",
            "first_seen": "2024-01-15T10:00:00Z",
            "last_seen": "2025-01-24T14:30:00Z",
            "deprecated": False
        },
        "payment_method": {
            "value": "ACH",
            "first_seen": "2024-01-15T10:00:00Z",
            "last_seen": "2025-01-24T14:30:00Z",
            "deprecated": False
        }
    },
    raw_data=complete_api_response  # Store everything
)
```

### Merge Strategy

```python
def merge_jsonb_fields(existing, new, timestamp):
    """Merge JSONB fields preserving historical data

    Args:
        existing: Existing JSONB dict (or None)
        new: New data from API
        timestamp: Current sync time

    Returns:
        Merged JSONB with lifecycle tracking
    """
    if existing is None:
        existing = {}

    merged = {}
    all_fields = set(existing.keys()) | set(new.keys())

    for field in all_fields:
        if field in new:
            # Field present in new data
            merged[field] = {
                "value": new[field],
                "last_seen": timestamp.isoformat(),
                "deprecated": False,
                "first_seen": (
                    existing.get(field, {}).get("first_seen") or
                    timestamp.isoformat()
                )
            }
        else:
            # Field removed from source (preserve historical data)
            merged[field] = existing[field]
            merged[field]["deprecated"] = True

    return merged
```

---

## Performance Considerations

### Query Performance

**With GIN index:**
```sql
-- Fast (uses index)
SELECT * FROM vendors WHERE custom_fields->>'region' = 'West';
-- Execution time: ~10ms for 10,000 records
```

**Without index:**
```sql
-- Slow (sequential scan)
SELECT * FROM vendors WHERE custom_fields->>'region' = 'West';
-- Execution time: ~500ms for 10,000 records
```

**Always create GIN indexes on JSONB columns you query frequently.**

### Storage Size

JSONB is binary format (more efficient than JSON text):
- Faster parsing (already binary)
- Smaller storage (compressed)
- Faster queries (optimized structure)

**Example:**
- JSON text: 1KB → 1KB stored
- JSONB: 1KB → 600-800 bytes stored

### Update Performance

JSONB updates rewrite entire column:

```python
# ❌ Inefficient for large JSONB
vendor.custom_fields['new_field'] = 'value'
# Rewrites entire custom_fields column
```

**Mitigation:**
- Keep JSONB columns focused (separate concerns)
- Use `raw_data` for complete backup, `custom_fields` for queryable data
- Update typed columns when possible

---

## Migration Pattern

Add JSONB columns to existing tables safely.

```sql
-- Idempotent migration
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        ALTER TABLE vendors ADD COLUMN custom_fields JSONB;
        COMMENT ON COLUMN vendors.custom_fields IS 'Custom fields with lifecycle metadata';
    END IF;
END $$;

-- Create index (safe to re-run)
CREATE INDEX IF NOT EXISTS idx_vendors_custom_gin
ON vendors USING GIN (custom_fields);

-- Verify
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'vendors' AND column_name = 'custom_fields'
    ) THEN
        RAISE EXCEPTION 'Migration failed - custom_fields not created';
    ELSE
        RAISE NOTICE 'Migration successful';
    END IF;
END $$;
```

---

## Related Patterns

**This Skill:**
- [schema-resilience.md](schema-resilience.md) - 3-layer architecture for evolving APIs
- [reference/database-migrations.md](../reference/database-migrations.md) - Idempotent migrations
- [pydantic-flexible.md](pydantic-flexible.md) - Flexible validation

**Example Applications:**
- **CRM systems** - Storing contacts/accounts with user-defined custom fields
- **Configuration management** - Application settings with varying structures
- **Event logging** - Flexible event payloads with mixed structured/unstructured data
- **API gateways** - Caching responses from third-party APIs with evolving schemas

---

## Summary

**Key Points:**

1. **Hybrid schema recommended** - Typed columns + JSONB for best of both
2. **GIN indexes critical** - Makes JSONB queries as fast as regular columns
3. **Lifecycle metadata** - Track first_seen, last_seen, deprecated
4. **Never destroy data** - Mark fields deprecated instead of deleting
5. **raw_data backup** - Store complete source data
6. **Idempotent migrations** - Safe to run multiple times
7. **Query helpers** - Abstract JSONB complexity

**JSONB enables schema flexibility without sacrificing query performance, critical for integrations with evolving external systems.**
