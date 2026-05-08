# State Diagrams

**Keyword:** `stateDiagram-v2` (or legacy `stateDiagram`)

**Purpose:** Model state machines and transitions.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [State Definitions](#state-definitions)
- [Transitions](#transitions)
- [Start and End States](#start-and-end-states)
- [Composite States](#composite-states)
- [Forks and Joins](#forks-and-joins)
- [Choice Points](#choice-points)
- [Notes](#notes)
- [Concurrency](#concurrency)
- [Direction](#direction)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active: start
    Active --> Idle: stop
    Active --> [*]: terminate
```

## State Definitions

**Simple ID:**
```mermaid
stateDiagram-v2
    StateA
```

**With description:**
```mermaid
stateDiagram-v2
    state "Waiting for Input" as Waiting
```

**Colon notation:**
```mermaid
stateDiagram-v2
    Waiting: Waiting for user input
```

## Transitions

```mermaid
stateDiagram-v2
    State1 --> State2: Trigger event
    State2 --> State3
```

## Start and End States

```mermaid
stateDiagram-v2
    [*] --> Initial: Entry
    Final --> [*]: Exit
```

## Composite States

```mermaid
stateDiagram-v2
    state ProcessingGroup {
        [*] --> Validating
        Validating --> Processing
        Processing --> [*]
    }
```

**Multiple nesting:**
```mermaid
stateDiagram-v2
    state Level1 {
        state Level2 {
            [*] --> Deep
        }
    }
```

## Forks and Joins

```mermaid
stateDiagram-v2
    state fork <<fork>>
    [*] --> fork
    fork --> Task1
    fork --> Task2

    state join <<join>>
    Task1 --> join
    Task2 --> join
    join --> [*]
```

## Choice Points

```mermaid
stateDiagram-v2
    state decision <<choice>>
    [*] --> decision
    decision --> StateA: condition1
    decision --> StateB: condition2
```

## Notes

```mermaid
stateDiagram-v2
    State1
    note right of State1
        Important note
    end note
```

## Concurrency

```mermaid
stateDiagram-v2
    [*] --> Active
    state Active {
        [*] --> Task1
        --
        [*] --> Task2
    }
```

## Direction

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A --> B --> [*]
```

## Key Limitations
- ClassDef styling cannot apply to start/end states
- Composite state styling is in development
- Complex concurrency may affect rendering

## When to Use
- State machine implementation
- Workflow status modeling
- Game state management
- Protocol state tracking
