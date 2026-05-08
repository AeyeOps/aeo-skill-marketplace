# SQL Tables and ER Diagrams

Use `shape: sql_table` for any database-shaped node — table, ER entity, schema row.

## Basic table

```d2
users: {
  shape: sql_table
  id:         int
  email:      string
  created_at: timestamp
}
```

Each child becomes a row. Key = column name, value = type. Both are free-form strings — D2 doesn't validate SQL types.

## Constraints

```d2
users: {
  shape: sql_table
  id:         int        { constraint: primary_key }
  email:      string     { constraint: unique }
  org_id:     int        { constraint: foreign_key }
  username:   string     { constraint: not_null }
  age:        int
}
```

D2 displays constraints with abbreviation marks next to each column:

| `constraint:` value | Mark | Meaning |
|---|---|---|
| `primary_key` | `PK` | Primary key |
| `foreign_key` | `FK` | Foreign key |
| `unique` | `UNQ` | Unique constraint |
| `not_null` (or any custom) | passed through | Custom |

The `constraint:` value is also passed through — you can use any string and it's rendered as-is. This is intentional: you can write `constraint: NOT NULL`, `constraint: CHECK >0`, etc.

## Composite primary keys (and other multi-constraints)

`constraint:` accepts an array (semicolon-separated):

```d2
order_items: {
  shape: sql_table
  order_id:   int { constraint: [primary_key; foreign_key] }
  product_id: int { constraint: [primary_key; foreign_key] }
  quantity:   int
}
```

## Foreign-key relationships (the connections)

Connect specific columns of two tables. Use crow's-foot arrowheads (`cf-one`, `cf-one-required`, `cf-many`, `cf-many-required`) to encode cardinality:

```d2
users: {
  shape: sql_table
  id: int { constraint: primary_key }
  org_id: int { constraint: foreign_key }
}

orgs: {
  shape: sql_table
  id: int { constraint: primary_key }
}

# Many-to-one: many users belong to one org (required)
users.org_id -> orgs.id: {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
```

### Cardinality recipes

| Relationship | Source arrowhead | Target arrowhead |
|---|---|---|
| One to many (required) | `cf-one-required` | `cf-many` |
| One to one | `cf-one-required` | `cf-one-required` |
| Many to many | `cf-many` | `cf-many` |
| Optional one to many | `cf-one` | `cf-many` |
| One to zero-or-more | `cf-one-required` | `cf-many` |
| One to one-or-more | `cf-one-required` | `cf-many-required` |

```d2
# One to many
customer.id -> order.customer_id: {
  source-arrowhead.shape: cf-one-required
  target-arrowhead.shape: cf-many
}

# Many to many (through join table)
student.id -> enrollment.student_id: {
  source-arrowhead.shape: cf-one-required
  target-arrowhead.shape: cf-many
}
course.id -> enrollment.course_id: {
  source-arrowhead.shape: cf-one-required
  target-arrowhead.shape: cf-many
}
```

## Reserved-keyword column names

If a column name collides with a D2 reserved keyword (`label`, `shape`, `style`, etc.), quote it:

```d2
my_table: {
  shape: sql_table
  id: int
  "shape": string         # quoted — would otherwise be the table's shape attribute
  "label": string
}
```

## Per-row sub-properties

You can attach attributes to a specific row by using its key:

```d2
users: {
  shape: sql_table
  id: int { constraint: primary_key }
  email: string

  # row-level styling — note this only works for some attrs
  email.style.fill: lightyellow
}
```

Most styling on individual rows is limited; for richer visuals, prefer styling the table as a whole.

## Table-wide styling

`fill` colors the **header**; `stroke` colors the body:

```d2
users: {
  shape: sql_table
  style: {
    fill:   "#1565c0"     # header background
    stroke: "#bbdefb"     # body background
    font-color: white     # header text only
    border-radius: 6
    shadow: true
  }
  id: int { constraint: primary_key }
  email: string
}
```

## A complete ER diagram example

```d2
direction: right
vars: {
  d2-config: {
    layout-engine: elk        # ELK routes to exact rows
    theme-id: 0
  }
}

# Lookup tables
roles: {
  shape: sql_table
  id:    int    { constraint: primary_key }
  name:  string { constraint: unique }
}

orgs: {
  shape: sql_table
  id:        int    { constraint: primary_key }
  name:      string { constraint: not_null }
  plan_tier: string
}

# Core entities
users: {
  shape: sql_table
  id:         int    { constraint: primary_key }
  email:      string { constraint: [unique; not_null] }
  org_id:     int    { constraint: foreign_key }
  role_id:    int    { constraint: foreign_key }
  created_at: timestamp
}

orders: {
  shape: sql_table
  id:           int    { constraint: primary_key }
  user_id:      int    { constraint: foreign_key }
  total_cents:  int    { constraint: not_null }
  placed_at:    timestamp
}

order_items: {
  shape: sql_table
  order_id:   int { constraint: [primary_key; foreign_key] }
  product_id: int { constraint: [primary_key; foreign_key] }
  quantity:   int { constraint: not_null }
  price_cents: int
}

products: {
  shape: sql_table
  id:    int    { constraint: primary_key }
  sku:   string { constraint: unique }
  name:  string
}

# Relationships with crow's-foot
users.org_id  -> orgs.id:  {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
users.role_id -> roles.id: {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
orders.user_id -> users.id: {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
order_items.order_id -> orders.id: {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
order_items.product_id -> products.id: {
  source-arrowhead.shape: cf-many
  target-arrowhead.shape: cf-one-required
}
```

## Tips for SQL diagrams

- **Use ELK or TALA**, not dagre. ELK and TALA route connections to the exact column row; dagre points at the table as a whole.
- **`direction: right`** usually reads better for ER diagrams than the default top-down.
- **Quote column names that collide with D2 reserved keywords**: `"label"`, `"shape"`, `"style"`, `"class"`, etc.
- **Don't try to put a real CHECK or DEFAULT into the column** — D2 just renders the column as text. You can put it in the type field as documentation: `created_at: timestamp DEFAULT NOW()`.
- **Composite keys** use `constraint: [primary_key; foreign_key]` (semicolon-separated array).
- **Sequence the FK arrows from many to one** by convention: `child.fk_col -> parent.pk`.

## Cheat sheet

```text
my_table: {
  shape: sql_table
  col_name:  type                                  # plain row
  col_name:  type { constraint: primary_key }      # with constraint
  col_name:  type { constraint: [primary_key; foreign_key] }  # multi
}

# FK / cardinality
table_a.col -> table_b.col: {
  source-arrowhead.shape: cf-many | cf-one | cf-many-required | cf-one-required
  target-arrowhead.shape: cf-many | cf-one | cf-many-required | cf-one-required
}

# Style header vs body
table.style.fill:   "#1565c0"   # header
table.style.stroke: "#bbdefb"   # body
```
