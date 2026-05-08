# Timeline Diagrams

**Keyword:** `timeline`

**Purpose:** Chronological event visualization.

## Basic Syntax

```mermaid
timeline
    title Project Timeline
    2020 : Project Start
         : Requirements
    2021 : Development
         : Testing
    2022 : Launch
```

## Sections/Ages

```mermaid
timeline
    title Evolution
    section Prehistoric
        10000 BC : Event A
        5000 BC : Event B
    section Ancient
        3000 BC : Event C
        1000 BC : Event D
```

## Multiple Events per Period

**Inline:**
```mermaid
timeline
    2025 : Event 1 : Event 2 : Event 3
```

**Vertical:**
```mermaid
timeline
    2025 : Event 1
         : Event 2
         : Event 3
```

## Text Wrapping

```mermaid
timeline
    2025 : Very long event description that will wrap automatically
    2026 : Forced<br>line break
```

## Color Customization

**Multi-color (default):**
Each time period gets unique color.

**Disable multi-color:**
```yaml
---
config:
  timeline:
    disableMulticolor: true
---
timeline
    2020 : Event A
    2021 : Event B
```

**Custom colors:**
```yaml
---
config:
  themeVariables:
    cScale0: '#ff0000'
    cScale1: '#00ff00'
    cScale2: '#0000ff'
    cScaleLabel0: '#ffffff'
---
timeline
    Period 1 : Event
```

## Key Limitations (Experimental)
- Syntax may change in future releases
- Icon integration experimental
- Limited formatting options

## When to Use
- Historical timelines
- Project milestones
- Product roadmaps
- Event chronologies
