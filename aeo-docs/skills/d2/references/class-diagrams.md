# UML Class Diagrams

Use `shape: class` for a UML class node. Children become fields and methods.

## Basic class

```d2
User: {
  shape: class

  # Fields:  name: type
  id:       int
  name:     string
  email:    string

  # Methods: name(args): return-type
  save():            void
  validate():        bool
  rename(s string):  void
}
```

D2 distinguishes fields from methods by the parentheses on the key.

## Visibility prefixes

| Prefix | Meaning |
|---|---|
| `+` | public |
| `-` | private |
| `#` | protected |

```d2
Account: {
  shape: class

  +id:           int
  +name:         string
  -password_hash: string
  \#balance:     decimal     # protected — escape '#' or it starts a comment

  +deposit(amount decimal): bool
  -hash_password(): void
  \#audit(action string): void
}
```

**The `#` (protected) prefix collides with D2 comments — escape as `\#` or quote the key:**

```d2
"#balance": decimal
\#audit(action string): void
```

## Generics (parameterized types)

Quote the key so the brackets aren't parsed:

```d2
Repository: {
  shape: class
  "find(id: int): Option<User>":  void
  "list(): List<User>":            void
}
```

Or escape the angle brackets if your D2 version supports it. Quoting is the safe path.

## Static / abstract modifiers

D2 has no first-class static/abstract keyword. Convention:

- **Abstract**: `style.italic: true` on the field key (or the whole class)
- **Static**: `style.underline: true` on the field key

```d2
MathUtils: {
  shape: class
  PI: float
  PI.style.underline: true     # static

  computeArea(r: float): float
  computeArea.style.underline: true
}

AbstractShape: {
  shape: class
  style.italic: true            # whole class abstract

  area(): float
  area.style.italic: true        # abstract method
}
```

## Class styling

Like `sql_table`, color semantics flip on `class`:

- `style.fill` — class-name **header** background
- `style.stroke` — body (members area) background
- `style.font-color` — class-name **header** text only

```d2
User: {
  shape: class
  style: {
    fill:   "#1565c0"
    stroke: "#e3f2fd"
    font-color: white
    border-radius: 6
    shadow: true
  }
  id: int
  name: string
}
```

## UML relationships (the connections)

D2 doesn't have dedicated relationship operators — express them with arrowhead shape + filled toggle:

| Relationship | Arrow | Source arrowhead | Target arrowhead |
|---|---|---|---|
| Inheritance / generalization | `child -> parent` | (none) | `triangle`, `style.filled: false` (empty) |
| Realization / interface impl | `class -> interface` | (none) | `triangle`, `style.filled: false` + `style.stroke-dash: 5` |
| Composition (whole owns part) | `whole -> part` | (none) | `diamond`, `style.filled: true` |
| Aggregation (whole has part) | `whole -> part` | (none) | `diamond`, `style.filled: false` |
| Association | `a -> b` | (none) | `triangle` (default) |
| Dependency | `a -> b` (`stroke-dash: 5`) | (none) | `triangle` |

### Inheritance

```d2
Animal: {
  shape: class
  +name: string
  +makeSound(): void
}

Dog: {
  shape: class
  +breed: string
  +bark(): void
}

# Dog inherits from Animal — empty triangle pointing at parent
Dog -> Animal: {
  target-arrowhead: {
    shape: triangle
    style.filled: false
  }
}
```

### Realization (implements interface)

```d2
Comparable: {
  shape: class
  style.italic: true              # interface convention
  +compareTo(other Object): int
}

Integer: {
  shape: class
  +value: int
}

Integer -> Comparable: {
  style.stroke-dash: 5            # dashed = realize
  target-arrowhead: {
    shape: triangle
    style.filled: false
  }
}
```

### Composition (filled diamond — strong ownership)

```d2
House: {
  shape: class
  -rooms: List<Room>
}

Room: {
  shape: class
  -area: float
}

House -> Room: {
  target-arrowhead: {
    shape: diamond
    style.filled: true
  }
  target-arrowhead.label: 1..*
}
```

### Aggregation (empty diamond — weak ownership)

```d2
Team: {
  shape: class
  -members: List<Player>
}

Player: {
  shape: class
  -name: string
}

Team -> Player: {
  target-arrowhead: {
    shape: diamond
    style.filled: false
  }
  target-arrowhead.label: 0..*
}
```

### Multiplicities

Use `target-arrowhead.label` and `source-arrowhead.label`:

```d2
Order -> OrderLine: {
  target-arrowhead: {
    shape: diamond
    style.filled: true
    label: 1..*
  }
  source-arrowhead.label: 1
}
```

## A complete banking-domain example

```d2
direction: right
vars: { d2-config: { layout-engine: elk } }

# Abstract base
AbstractAccount: {
  shape: class
  style.italic: true

  \#owner: Customer
  \#balance: Decimal

  +deposit(amount Decimal): bool
  +withdraw(amount Decimal): bool
  \#audit(): void
  \#audit.style.italic: true        # abstract method
}

CheckingAccount: {
  shape: class
  +overdraftLimit: Decimal
  +applyMonthlyFee(): void
}

SavingsAccount: {
  shape: class
  +interestRate: float
  +accrueInterest(): Decimal
}

Customer: {
  shape: class
  +id: int
  +name: string
  +email: string
}

Transaction: {
  shape: class
  +id: int
  +amount: Decimal
  +occurredAt: DateTime
}

Loggable: {
  shape: class
  style.italic: true                 # interface
  +log(message: string): void
}

# Inheritance
CheckingAccount -> AbstractAccount: {
  target-arrowhead: { shape: triangle; style.filled: false }
}
SavingsAccount -> AbstractAccount: {
  target-arrowhead: { shape: triangle; style.filled: false }
}

# Realization
AbstractAccount -> Loggable: {
  style.stroke-dash: 5
  target-arrowhead: { shape: triangle; style.filled: false }
}

# Composition: customer owns accounts
Customer -> AbstractAccount: {
  target-arrowhead: {
    shape: diamond
    style.filled: true
    label: 1..*
  }
  source-arrowhead.label: 1
}

# Aggregation: account has transactions (weak ownership)
AbstractAccount -> Transaction: {
  target-arrowhead: {
    shape: diamond
    style.filled: false
    label: 0..*
  }
}
```

## Cheat sheet

```text
MyClass: {
  shape: class

  # field
  field: type
  +public_field: type
  -private_field: type
  \#protected_field: type

  # method
  doSomething(arg: type): return-type
  +static_field: type
  +static_field.style.underline: true     # static
  +abstract_method(): void
  +abstract_method.style.italic: true      # abstract
}

# UML relationships (target-arrowhead reference):
# Inheritance:    triangle, style.filled: false
# Realization:    triangle, style.filled: false + stroke-dash: 5
# Composition:    diamond, style.filled: true
# Aggregation:    diamond, style.filled: false
# Multiplicity:   target-arrowhead.label: 1..*
```
