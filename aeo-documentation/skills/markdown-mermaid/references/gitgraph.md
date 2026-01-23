# GitGraph Diagrams

**Keyword:** `gitGraph`

**Purpose:** Visualize Git branching and merging workflows.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Commits](#commits)
- [Branching](#branching)
- [Checkout/Switch](#checkoutswitch)
- [Merging](#merging)
- [Cherry-Pick](#cherry-pick)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    checkout main
    merge develop
```

## Commits

```mermaid
gitGraph
    commit
    commit id: "feature-123"
    commit tag: "v1.0.0"
    commit type: HIGHLIGHT
```

**Commit types:**
- `NORMAL` - Solid circle (default)
- `REVERSE` - Crossed circle
- `HIGHLIGHT` - Filled rectangle

**Custom IDs:**
```mermaid
gitGraph
    commit id: "abc123"
    commit id: "def456"
```

**Tags:**
```mermaid
gitGraph
    commit
    commit tag: "v1.0"
```

## Branching

```mermaid
gitGraph
    commit
    branch feature1
    commit
    branch feature2
    commit
```

**Branch with options:**
```mermaid
gitGraph
    commit
    branch feature order: 2
```

## Checkout/Switch

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    checkout main
    commit
```

**Note:** `checkout` and `switch` are interchangeable.

## Merging

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
```

**Merge with tag:**
```mermaid
gitGraph
    commit
    branch feature
    commit
    checkout main
    merge feature tag: "release-1.0"
```

## Cherry-Pick

```mermaid
gitGraph
    commit id: "A"
    branch develop
    commit id: "B"
    commit id: "C"
    checkout main
    cherry-pick id: "B"
```

**Cherry-pick parent (merge commits):**
```mermaid
gitGraph
    commit
    branch feature
    commit id: "F1"
    checkout main
    merge feature id: "M1"
    checkout feature
    commit id: "F2"
    checkout main
    cherry-pick id: "M1" parent: "F1"
```

## Key Limitations
- Branch names conflicting with keywords must be quoted
- Cherry-pick requires commit to exist on different branch
- Self-merge prohibited (causes error)
- Current branch must have at least one commit before cherry-pick
- Merge commit cherry-pick requires parent ID

## When to Use
- Git workflow documentation
- Branching strategy illustration
- Release process visualization
- Training materials
