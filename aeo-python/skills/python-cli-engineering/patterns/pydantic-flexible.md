# Pydantic for Inconsistent APIs

Patterns for using Pydantic validation with real-world APIs that return inconsistent or unpredictable data structures.

## The Challenge

Real-world APIs are messy:
- **Nullable inconsistency:** Sometimes null, sometimes empty string, sometimes missing
- **Type variations:** Number as string, date as various formats
- **Nested unpredictability:** Sometimes object, sometimes just ID
- **Extra fields:** API returns fields not in documentation

**Strict Pydantic fails:**
```python
class StrictModel(BaseModel):
    date_field: datetime  # Fails on "", null, missing, or invalid format
    amount: float         # Fails on "1000.00" (string)
    status: Literal["active", "inactive"]  # Fails on "ACTIVE" (case)
```

---

## Configuration Patterns

### Allow Extra Fields

Accept unknown fields without validation errors:

```python
from pydantic import BaseModel

class FlexibleModel(BaseModel):
    # Known fields explicitly typed
    id: str
    name: str
    status: str

    class Config:
        extra = "allow"  # Don't fail on unknown fields
        populate_by_name = True  # Accept both snake_case and camelCase
```

**Benefits:**
- No errors when API adds new fields
- Captures all data (access via `__dict__`)
- Type-safe for known fields

**Usage:**
```python
data = {
    "id": "123",
    "name": "Test",
    "status": "active",
    "unknown_field": "Some value",  # Captured automatically
    "another": 42
}

model = FlexibleModel(**data)
# model.id = "123"
# model.name = "Test"
# model.__dict__["unknown_field"] = "Some value"
```

### Support Field Name Aliases

```python
from pydantic import Field

class APIModel(BaseModel):
    company_name: str = Field(alias="companyName")
    last_modified: datetime = Field(alias="lastModifiedDate")

    class Config:
        populate_by_name = True  # Accept both names

# Works with either name
model1 = APIModel(companyName="Acme")
model2 = APIModel(company_name="Acme")
```

---

## Field Validators

### Handle Empty Strings

```python
from pydantic import field_validator

class APIModel(BaseModel):
    date_field: datetime | None = None

    @field_validator("date_field", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty string to None"""
        if v == "" or v is None:
            return None
        return v

# Handles all cases
model1 = APIModel(date_field="2025-01-24")  # Parses datetime
model2 = APIModel(date_field="")             # Converts to None
model3 = APIModel(date_field=None)           # Already None
model4 = APIModel()                          # Missing field, defaults None
```

### Parse String Numbers

```python
from decimal import Decimal

class TransactionModel(BaseModel):
    amount: Decimal

    @field_validator("amount", mode="before")
    @classmethod
    def parse_string_number(cls, v):
        """Convert string to Decimal"""
        if isinstance(v, str):
            return Decimal(v)
        return v

# Handles both
model1 = TransactionModel(amount=1000.50)     # Decimal
model2 = TransactionModel(amount="1000.50")   # String → Decimal
```

### Normalize Case

```python
from pydantic import field_validator

class APIModel(BaseModel):
    status: str

    @field_validator("status", mode="before")
    @classmethod
    def normalize_case(cls, v):
        """Normalize to lowercase"""
        if isinstance(v, str):
            return v.lower()
        return v

# All normalized
model1 = APIModel(status="Active")   # → "active"
model2 = APIModel(status="ACTIVE")   # → "active"
model3 = APIModel(status="active")   # → "active"
```

---

## Model Validators

### Extract Reference Objects

Handle NetSuite-style reference objects:

```python
from pydantic import model_validator

class VendorModel(BaseModel):
    id: str
    company_name: str
    currency: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_references(cls, data):
        """Extract reference objects to simple values

        NetSuite returns: {"currency": {"id": "1", "refName": "USD"}}
        Store: "USD"
        """
        if "currency" in data and isinstance(data["currency"], dict):
            # Prefer refName (human-readable)
            data["currency"] = (
                data["currency"].get("refName") or
                data["currency"].get("id")
            )

        if "terms" in data and isinstance(data["terms"], dict):
            data["terms"] = data["terms"].get("refName") or data["terms"].get("id")

        return data

# API returns
api_data = {
    "id": "123",
    "companyName": "Acme",
    "currency": {"id": "1", "refName": "USD", "links": [...]}
}

# Pydantic extracts
vendor = VendorModel(**api_data)
# vendor.currency = "USD" (not the dict)
```

### Handle Multiple Date Formats

```python
from pydantic import field_validator
from datetime import datetime

class APIModel(BaseModel):
    created_date: datetime | None = None

    @field_validator("created_date", mode="before")
    @classmethod
    def parse_flexible_date(cls, v):
        """Parse various date formats"""
        if not v or v == "":
            return None

        if isinstance(v, datetime):
            return v

        # Try multiple formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue

        # Fallback: log and return None
        print(f"Warning: Could not parse date '{v}'")
        return None
```

---

## Optional vs Required Fields

### Make Everything Optional (Defensive)

```python
class DefensiveModel(BaseModel):
    # Make all fields optional with sensible defaults
    id: str | None = None
    name: str | None = None
    amount: float = 0.0
    date: datetime | None = None
    status: str = "unknown"

    @model_validator(mode="after")
    def validate_required(self):
        """Validate business requirements after parsing"""
        if not self.id:
            raise ValueError("ID is required")
        return self
```

**Benefits:**
- Parsing almost never fails
- Handle missing/null/empty gracefully
- Business validation separate from parsing

### Partial Models

For APIs with optional expansions:

```python
class VendorBase(BaseModel):
    """Minimal vendor data (always present)"""
    id: str
    company_name: str

class VendorComplete(VendorBase):
    """Complete vendor with optional fields"""
    email: str | None = None
    phone: str | None = None
    balance: float = 0.0
    custom_fields: dict = {}

# Use appropriate model based on API call
base_vendor = VendorBase(**query_response)      # Only IDs
full_vendor = VendorComplete(**get_response)    # Complete data
```

---

## Real-World Example (NetSuite)

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class VendorBillModel(BaseModel):
    """NetSuite Vendor Bill with flexible validation"""

    # Required fields
    id: str
    tran_id: str = Field(alias="tranId")

    # Optional fields (handle missing/empty)
    tran_date: datetime | None = Field(None, alias="tranDate")
    due_date: datetime | None = Field(None, alias="dueDate")
    amount: float | None = None
    status: str | None = None
    memo: str | None = None

    # Reference fields
    entity: str | None = None  # Will be extracted from {"id": "123", "refName": "Vendor Name"}
    currency: str | None = None

    class Config:
        extra = "allow"  # Capture all custom fields
        populate_by_name = True

    @field_validator("tran_date", "due_date", mode="before")
    @classmethod
    def handle_empty_dates(cls, v):
        """Convert empty string to None"""
        return v if v else None

    @model_validator(mode="before")
    @classmethod
    def extract_all_references(cls, data):
        """Extract all reference objects to simple values"""
        for field in ["entity", "currency", "terms", "account"]:
            if field in data and isinstance(data[field], dict):
                data[field] = data[field].get("refName") or data[field].get("id")
        return data
```

---

## Error Handling

### Collect Validation Errors

```python
from pydantic import ValidationError

def parse_api_response(data_list):
    """Parse API responses, collect errors instead of failing"""
    valid_records = []
    errors = []

    for item in data_list:
        try:
            model = APIModel(**item)
            valid_records.append(model)
        except ValidationError as e:
            errors.append({
                "item_id": item.get("id", "unknown"),
                "errors": e.errors()
            })

    # Log errors for investigation
    if errors:
        print(f"Validation errors: {len(errors)}/{len(data_list)}")
        for error in errors:
            print(f"  Item {error['item_id']}: {error['errors']}")

    return valid_records
```

**Benefits:**
- Don't lose entire batch due to one bad record
- Collect error details for debugging
- Partial success acceptable

---

## Related Patterns

**This Skill:**
- [schema-resilience.md](schema-resilience.md) - 3-layer architecture
- [postgresql-jsonb.md](postgresql-jsonb.md) - JSONB storage patterns

**NetSuite Integrations:**
- `patterns/schema-evolution.md` - NetSuite custom field handling

---

## Summary

**Key Points:**

1. **extra="allow"** - Accept unknown fields from API
2. **Optional fields** - Use `field | None` for nullable/missing
3. **Field validators** - Handle empty strings, format variations
4. **Model validators** - Extract nested objects, normalize data
5. **Collect errors** - Don't fail entire batch on one bad record
6. **Defensive defaults** - Provide sensible defaults for missing data

**Flexible Pydantic configuration prevents validation errors from inconsistent APIs while maintaining type safety for known fields.**
