# Mindmaps

**Keyword:** `mindmap`

**Purpose:** Hierarchical information organization using indentation.

## Basic Syntax

```mermaid
mindmap
    Root Topic
        Branch 1
            Sub-topic 1A
            Sub-topic 1B
        Branch 2
            Sub-topic 2A
```

## Node Shapes

```mermaid
mindmap
    root[Root Square]
        child1(Rounded)
        child2((Circle))
        child3)Bang(
        child4{{Cloud}}
```

**Shape syntax:**
- `[text]` - Square
- `(text)` - Rounded square
- `((text))` - Circle
- `)text(` - Bang
- `{{text}}` - Cloud
- Plain text - Default

## Icons

```mermaid
mindmap
    Root
        Task1::icon(fa fa-check)
        Task2::icon(mdi mdi-account)
```

**Supported icon sets:**
- Font Awesome 5
- Material Design Icons

**Note:** Icon integration is experimental and may change.

## Classes

```mermaid
mindmap
    Root
        Important:::highlight
        Normal

classDef highlight fill:#ff0,stroke:#f00,stroke-width:3px
```

## Layout

```yaml
---
config:
  look: classic
  layout: tidy-tree
---
mindmap
    Root
```

**Layout algorithms:** `tidy-tree` (v9.4.0+)

## Key Limitations
- Icon feature is experimental
- Indentation must be consistent
- Complex hierarchies may affect readability

## When to Use
- Brainstorming sessions
- Knowledge organization
- Concept mapping
- Hierarchical note-taking
