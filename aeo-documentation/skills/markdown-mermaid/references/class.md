# Class Diagrams

**Keyword:** `classDiagram`

**Purpose:** Model object-oriented structures with classes, attributes, methods, and relationships.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Class Definition](#class-definition)
- [Members](#members)
- [Visibility Modifiers](#visibility-modifiers)
- [Method Classifiers](#method-classifiers)
- [Return Types](#return-types)
- [Generic Types](#generic-types)
- [Relationships](#relationships)
- [Annotations](#annotations)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
classDiagram
    class ClassName {
        +String attribute
        -int privateField
        +method() void
        #protectedMethod()$
    }
```

## Class Definition

**Bracket syntax:**
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
```

**Colon syntax:**
```mermaid
classDiagram
    class Animal
    Animal : +String name
    Animal : +makeSound() void
```

## Members

**Attributes:** No parentheses
```
+publicAttribute
-privateAttribute
#protectedAttribute
~packageAttribute
```

**Methods:** Include parentheses
```
+publicMethod()
-privateMethod()
#protectedMethod()
~packageMethod()
```

## Visibility Modifiers
- `+` Public
- `-` Private
- `#` Protected
- `~` Package/Internal

## Method Classifiers
- `*` Abstract: `method()*`
- `$` Static: `method()$`

## Return Types

```mermaid
classDiagram
    class Calculator {
        +add(int a, int b) int
        +divide(float x, float y) float
    }
```

## Generic Types

```mermaid
classDiagram
    class List~T~ {
        +add(T item)
        +get(int index) T
    }
    class Map~K,V~ {
        +put(K key, V value)
    }
```

**Note:** Nested generics like `List~List~int~~` are supported, but comma-separated generics have limited support.

## Relationships

| Syntax | Type | Meaning |
|--------|------|---------|
| `<\|--` | Inheritance | Extends/implements |
| `*--` | Composition | Strong "has-a" |
| `o--` | Aggregation | Weak "has-a" |
| `-->` | Association | Uses/knows |
| `--` | Link (solid) | Generic connection |
| `..>` | Dependency | Temporary usage |
| `..\|>` | Realization | Interface implementation |
| `..` | Link (dashed) | Weak connection |

**With cardinality:**
```mermaid
classDiagram
    Customer "1" --> "*" Order
    Order "*" --> "1..*" LineItem
```

## Annotations

```mermaid
classDiagram
    class Shape {
        <<interface>>
        +draw()*
    }
    class AbstractBase {
        <<abstract>>
        +process()*
    }
    class UserService {
        <<service>>
        +getUser()
    }
    class Status {
        <<enumeration>>
        ACTIVE
        INACTIVE
    }
```

## Key Limitations
- Class names: alphanumeric, underscores, dashes only
- Comma-separated generics not fully supported
- Complex nested relationships may require careful formatting

## When to Use
- Software architecture documentation
- Database schema modeling
- OOP design planning
- API structure visualization
