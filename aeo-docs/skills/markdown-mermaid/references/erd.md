# Entity Relationship Diagrams (ERD)

**Keyword:** `erDiagram`

**Purpose:** Model database schemas and entity relationships.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Entity Definition](#entity-definition)
- [Attribute Constraints](#attribute-constraints)
- [Cardinality Notation](#cardinality-notation)
- [Relationship Examples](#relationship-examples)
- [Relationship Aliases](#relationship-aliases)
- [Diagram Direction](#diagram-direction)
- [Styling](#styling)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
erDiagram
    CUSTOMER {
        string id PK
        string name
        string email UK
    }
    ORDER {
        string orderId PK
        string customerId FK
        date orderDate
    }
    CUSTOMER ||--o{ ORDER : places
```

## Entity Definition

```mermaid
erDiagram
    ENTITY_NAME {
        datatype attributeName constraints "comment"
    }
```

**Example:**
```mermaid
erDiagram
    USER {
        uuid userId PK "Primary key"
        string username UK "Unique username"
        string email UK "Unique email"
        datetime createdAt "Account creation"
    }
```

## Attribute Constraints
- `PK` - Primary Key
- `FK` - Foreign Key
- `UK` - Unique Key

## Cardinality Notation

**Crow's foot notation:**

| Marker | Meaning |
|--------|---------|
| `\|o` | Zero or one |
| `\|\|` | Exactly one |
| `}o` | Zero or more (many) |
| `}\|` | One or more |

**Syntax:** `ENTITY1 [left][right]--[right][left] ENTITY2 : label`

## Relationship Examples

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : "places"
    ORDER ||--|{ LINE_ITEM : "contains"
    PRODUCT ||--o{ LINE_ITEM : "included in"
```

**Identifying vs Non-identifying:**
- `--` Solid line (identifying relationship)
- `..` Dashed line (non-identifying relationship)

```mermaid
erDiagram
    PARENT ||--|| CHILD : "identifies"
    PARENT ||..o{ REFERENCE : "references"
```

## Relationship Aliases

Alternative syntax:
```mermaid
erDiagram
    CUSTOMER }|..|{ PRODUCT : "one or more"
    CUSTOMER ||--|| ADDRESS : "exactly one"
```

## Diagram Direction

```mermaid
%%{init: {'er': {'layoutDirection': 'LR'}}}%%
erDiagram
    A ||--|| B : relates
```

Options: `TB`, `BT`, `LR`, `RL`

## Styling

```mermaid
erDiagram
    CUSTOMER
    style CUSTOMER fill:#f9f,stroke:#333

    classDef important fill:#ff6,stroke:#f00
    ORDER:::important
```

## Key Limitations
- Data types are cosmetic (not validated)
- Complex many-to-many requires junction tables
- Comments must be quoted

## When to Use
- Database schema design
- Data modeling workshops
- Technical documentation
- Migration planning
