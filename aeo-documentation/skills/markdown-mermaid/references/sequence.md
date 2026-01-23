# Sequence Diagrams

**Keyword:** `sequenceDiagram`

**Purpose:** Show interactions between actors/systems over time.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Participants](#participants)
- [Message Types](#message-types)
- [Activation Boxes](#activation-boxes)
- [Control Flow](#control-flow)
- [Notes](#notes)
- [Grouping (Boxes)](#grouping-boxes)
- [Lifecycle](#lifecycle)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
sequenceDiagram
    participant A
    participant B
    A->>B: Message
    B-->>A: Response
```

## Participants

**Auto-declaration:** Participants appear in order of first use.

**Explicit ordering:**
```mermaid
sequenceDiagram
    participant Alice
    participant Bob as B
    actor Charlie
```

**Actor types** (via JSON config):
- Actor (default rectangle)
- Boundary
- Control
- Entity
- Database
- Collections
- Queue

## Message Types

| Syntax | Line Style | Arrow |
|--------|------------|-------|
| `->` | Solid | None |
| `-->` | Dotted | None |
| `->>` | Solid | Filled |
| `-->>` | Dotted | Filled |
| `-x` | Solid | Cross |
| `--x` | Dotted | Cross |
| `-)` | Solid | Open (async) |
| `--)` | Dotted | Open (async) |

## Activation Boxes

```mermaid
sequenceDiagram
    A->>+B: Request
    B-->>-A: Response
```

Or explicit:
```mermaid
sequenceDiagram
    A->>B: Request
    activate B
    B-->>A: Response
    deactivate B
```

## Control Flow

**Loops:**
```mermaid
sequenceDiagram
    loop Every minute
        A->>B: Heartbeat
    end
```

**Alternatives:**
```mermaid
sequenceDiagram
    alt Success
        A->>B: Success path
    else Failure
        A->>B: Error path
    end
```

**Optional:**
```mermaid
sequenceDiagram
    opt Extra validation
        A->>B: Validate
    end
```

**Parallel:**
```mermaid
sequenceDiagram
    par Action 1
        A->>B: Task 1
    and Action 2
        A->>C: Task 2
    end
```

**Critical regions:**
```mermaid
sequenceDiagram
    critical Establish connection
        A->>B: Connect
    option Timeout
        A->>B: Retry
    end
```

## Notes

```mermaid
sequenceDiagram
    Note left of A: Left note
    Note right of B: Right note
    Note over A,B: Spanning note
```

## Grouping (Boxes)

```mermaid
sequenceDiagram
    box Purple Backend
        participant A
        participant B
    end
    box Green Frontend
        participant C
    end
```

## Lifecycle

```mermaid
sequenceDiagram
    A->>B: Request
    create participant C
    B->>C: Initialize
    destroy C
    B->>A: Done
```

## Key Limitations
- "end" keyword can break diagrams (wrap in quotes)
- Line breaks use `<br/>` HTML tag
- Complex nesting may affect rendering

## When to Use
- API interaction documentation
- Protocol specification
- Message flow analysis
- Use case scenarios
