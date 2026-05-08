# ZenUML (Alternative Sequence Diagrams)

**Keyword:** `zenuml`

**Purpose:** Programming-like syntax for sequence diagrams.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Message Types](#message-types)
- [Control Flow](#control-flow)
- [Participants](#participants)
- [Comments](#comments)
- [Key Differences from Standard Sequence Diagrams](#key-differences-from-standard-sequence-diagrams)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
zenuml
    A.method() {
        B.process()
        return result
    }
```

## Message Types

**Sync (blocking):**
```mermaid
zenuml
    A.syncCall() {
        B.work()
    }
```

**Async (non-blocking):**
```mermaid
zenuml
    @Async
    A.asyncCall()
```

**Creation:**
```mermaid
zenuml
    new B()
    B.initialize()
```

**Reply:**
```mermaid
zenuml
    A.request() {
        return "response"
    }
```

## Control Flow

**Loops:**
```mermaid
zenuml
    while(condition) {
        A.repeat()
    }

    for(i in items) {
        A.process(i)
    }
```

**Conditionals:**
```mermaid
zenuml
    if(success) {
        A.proceed()
    } else if(retry) {
        A.retry()
    } else {
        A.fail()
    }
```

**Parallel:**
```mermaid
zenuml
    par {
        A.task1()
        B.task2()
    }
```

**Optional:**
```mermaid
zenuml
    opt {
        A.optional()
    }
```

**Exception handling:**
```mermaid
zenuml
    try {
        A.riskyOperation()
    } catch {
        A.handleError()
    } finally {
        A.cleanup()
    }
```

## Participants

**Annotators:**
```mermaid
zenuml
    @Actor Alice
    @Database UserDB
    @Boundary API

    Alice.login() {
        API.authenticate()
        UserDB.verify()
    }
```

**Aliases:**
```mermaid
zenuml
    A as Alice
    B as Bob
    Alice.message(Bob)
```

## Comments

```mermaid
zenuml
    // This is a comment
    A.method()
```

**Supports markdown in comments.**

## Key Differences from Standard Sequence Diagrams

- Programming-like syntax (curly braces)
- Implicit participant declaration
- Natural nesting with `{}`
- Different control flow syntax
- `new` keyword for creation

## Key Limitations (Experimental)
- Uses lazy loading & async rendering
- Syntax may change
- Limited compared to mature sequence diagram

## When to Use
- Developers preferring code-like syntax
- Complex nested interactions
- Programming language flow documentation
- Alternative to standard sequence diagrams
