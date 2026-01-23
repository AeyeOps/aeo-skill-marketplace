# Schema Resilience for Evolving APIs

Architecture patterns for building Python CLI applications that remain stable when external API schemas change.

## The Problem

External APIs evolve continuously:
- **New fields added** (new features, business requirements)
- **Old fields removed** (deprecated functionality)
- **Field types modified** (string → enum, number → object)
- **No advance notice** (schema changes deployed without warning)

**Traditional approach fails:**
```python
# ❌ Breaks when API changes
class APIRecord:
    field1: str
    field2: int
    # What happens when API adds field3?
    # What happens when field2 is removed?
```

**Symptoms:**
- Validation errors when new fields added
- KeyError when fields removed
- Type errors when field types change
- Manual code updates required after each API change

---

## 3-Layer Architecture

Separate concerns to isolate schema changes.

### Layer 1: Source (API)

**Characteristics:**
- Returns complete data
- Schema changes over time
- No control over changes
- Must accept whatever comes

**Responsibility:** Fetch raw data

```python
def fetch_from_api(client, record_id):
    """Fetch raw data from API (accept everything)"""
    response = client.get(f'/api/records/{record_id}')
    return response.json()  # Complete, unvalidated data
```

### Layer 2: Storage (Database)

**Characteristics:**
- Typed columns for known fields (performance)
- JSONB for unknown/custom fields (flexibility)
- **Never destroys data** (additive only)
- Preserves historical state

**Responsibility:** Store all data safely

```python
class Record(Base):
    # Typed (known fields)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Flexible (unknown fields)
    custom_fields: Mapped[dict] = mapped_column(JSONB)
    raw_data: Mapped[dict] = mapped_column(JSONB)
```

### Layer 3: Application (Business Logic)

**Characteristics:**
- Queries only needed fields
- Handles missing fields gracefully
- No hard dependencies on deprecated fields
- Validates business rules (not schema)

**Responsibility:** Process data safely

```python
def process_record(record):
    """Process record handling field variations"""
    # Required field (from typed column)
    name = record.name

    # Optional field (from JSONB, may not exist)
    region = record.custom_fields.get('region', 'Unknown')

    # Nested field (with default)
    payment = (
        record.custom_fields.get('payment_method', {}).get('value', 'Check')
    )

    return {
        "name": name,
        "region": region,
        "payment": payment
    }
```

---

## Field Classification

Systematically distinguish stable from evolving fields.

### Define Known Fields

```python
from typing import Final

KNOWN_FIELDS: Final[frozenset[str]] = frozenset([
    "id", "name", "email", "status", "created_at", "updated_at"
])

def is_known_field(field_name: str) -> bool:
    """Check if field is known (stable)"""
    return field_name in KNOWN_FIELDS
```

### Split Function

```python
def split_fields(api_data: dict) -> tuple[dict, dict]:
    """Split API data into known vs unknown fields

    Returns:
        (known_fields, unknown_fields)
    """
    known = {}
    unknown = {}

    for key, value in api_data.items():
        if is_known_field(key):
            known[key] = value
        else:
            unknown[key] = value

    return known, unknown

# Usage
known, unknown = split_fields(api_response)

record = Record(
    **known,  # Typed columns
    custom_fields=unknown,  # JSONB
    raw_data=api_response  # Complete backup
)
```


---

## Merge Strategy

Preserve historical data when fields disappear from API.

```python
from datetime import datetime

def merge_custom_fields(existing, new, timestamp):
    """Merge custom fields preserving historical data

    Args:
        existing: Current custom_fields JSONB (or None)
        new: New custom fields from API
        timestamp: Current sync timestamp

    Returns:
        Merged custom fields with lifecycle metadata
    """
    if existing is None:
        existing = {}

    merged = {}
    all_fields = set(existing.keys()) | set(new.keys())

    for field in all_fields:
        if field in new:
            # Field present in API response
            merged[field] = {
                "value": new[field],
                "last_seen": timestamp.isoformat(),
                "deprecated": False,
                "first_seen": (
                    existing.get(field, {}).get("first_seen") or
                    timestamp.isoformat()
                ),
            }
        else:
            # Field removed from API (preserve historical data)
            merged[field] = existing[field]
            merged[field]["deprecated"] = True

    return merged
```

**Stored structure:**
```json
{
  "active_field": {
    "value": "Current value",
    "first_seen": "2024-01-15T10:00:00Z",
    "last_seen": "2025-01-24T14:30:00Z",
    "deprecated": false
  },
  "removed_field": {
    "value": "Historical value",
    "first_seen": "2023-01-01T00:00:00Z",
    "last_seen": "2024-06-01T09:00:00Z",
    "deprecated": true
  }
}
```

---

## Pydantic Configuration

Use Pydantic with flexible validation.

### Accept Extra Fields

```python
from pydantic import BaseModel, Field

class FlexibleModel(BaseModel):
    # Known fields explicitly typed
    id: str
    name: str
    status: str

    class Config:
        extra = "allow"  # Don't fail on unknown fields
        populate_by_name = True  # Support field name aliases

# Usage
data = {
    "id": "123",
    "name": "Test",
    "status": "active",
    "new_unknown_field": "Some value",  # Automatically captured
    "another_field": 42
}

model = FlexibleModel(**data)
# model.id = "123"
# model.name = "Test"
# model.__dict__ contains all fields including unknown
```

### Field Validators

Handle variations in field values:

```python
from pydantic import field_validator, model_validator

class APIModel(BaseModel):
    date_field: datetime | None = None

    @field_validator("date_field", mode="before")
    @classmethod
    def handle_empty_dates(cls, v):
        """Convert empty string to None"""
        if v == "" or v is None:
            return None
        return v

    @model_validator(mode="before")
    @classmethod
    def extract_nested_refs(cls, data):
        """Extract reference objects"""
        # {"currency": {"id": "1", "refName": "USD"}} → "USD"
        if "currency" in data and isinstance(data["currency"], dict):
            data["currency"] = data["currency"].get("refName") or data["currency"].get("id")
        return data
```


---

## Migration Strategy

### Rule: Never DROP, Only ADD

```sql
-- ✅ SAFE - Adding columns
ALTER TABLE records ADD COLUMN IF NOT EXISTS new_field VARCHAR;

-- ❌ NEVER - Dropping based on API changes
ALTER TABLE records DROP COLUMN old_field;
```

**Why:**
- API may temporarily remove fields (bugs, rollbacks)
- Fields may return in future API versions
- Historical data valuable for analysis
- No harm in keeping unused columns

### Idempotent Migrations

```sql
-- Safe to run multiple times
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'records' AND column_name = 'custom_fields'
    ) THEN
        ALTER TABLE records ADD COLUMN custom_fields JSONB;
        CREATE INDEX idx_records_custom_gin ON records USING GIN (custom_fields);
        RAISE NOTICE 'Added custom_fields column';
    ELSE
        RAISE NOTICE 'custom_fields column already exists';
    END IF;
END $$;
```

**Benefits:**
- Run migration scripts multiple times without errors
- Safe in CI/CD pipelines
- Easy rollback (just re-run previous version)

See [../reference/database-migrations.md](../reference/database-migrations.md) for detailed patterns

---

## Handling Field Removal

### Graceful Degradation

```python
def get_field_safely(record, field_path, default=None):
    """Get field value handling removal gracefully

    Args:
        record: Database record
        field_path: Dot-separated path (e.g., 'custom_fields.region.value')
        default: Value if field missing

    Returns:
        Field value or default
    """
    parts = field_path.split('.')
    current = record

    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)

        if current is None:
            return default

    return current if current is not None else default

# Usage
region = get_field_safely(vendor, 'custom_fields.region.value', default='Unknown')
# Never raises KeyError, even if field removed
```

---

## Related Patterns

**This Skill:**
- [postgresql-jsonb.md](postgresql-jsonb.md) - JSONB query patterns and indexing
- [pydantic-flexible.md](pydantic-flexible.md) - Flexible validation patterns
- [../reference/database-migrations.md](../reference/database-migrations.md) - Migration patterns

**Common Use Cases:**
- **E-commerce APIs** - Product catalogs with varying attributes across categories
- **SaaS integrations** - Third-party APIs that add custom fields over time
- **Multi-tenant systems** - Different tenants with different field requirements
- **Analytics platforms** - User-defined custom dimensions and metrics

**Reference Implementation:**

## Summary

**Key Points:**

1. **3-layer separation** - Source, Storage, Application (isolate concerns)
2. **Hybrid schema** - Typed columns for known, JSONB for unknown
3. **Never destroy data** - Mark deprecated instead of deleting
4. **Field classification** - Systematically split known vs unknown
5. **Merge strategy** - Preserve historical data with lifecycle tracking
6. **Graceful degradation** - Handle missing fields without errors
7. **Idempotent migrations** - Safe to run repeatedly

**This architecture prevents API schema changes from breaking your application, a common cause of production outages in integrations.**
