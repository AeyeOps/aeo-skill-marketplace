# Pie Charts

**Keyword:** `pie`

**Purpose:** Show proportional data distribution.

## Basic Syntax

```mermaid
pie title Distribution
    "Category A" : 45
    "Category B" : 30
    "Category C" : 25
```

## Show Data Values

```mermaid
pie showData
    "Sales" : 450
    "Marketing" : 300
    "R&D" : 250
```

## Configuration

```mermaid
%%{init: {'pie': {'textPosition': 0.9}}}%%
pie
    "A" : 40
    "B" : 60
```

**textPosition:** 0.0 (center) to 1.0 (edge), default 0.75

## Key Limitations
- Values must be positive numbers > 0
- Negative values cause errors
- Maximum 2 decimal places
- Slices ordered clockwise as defined

## When to Use
- Budget breakdowns
- Market share visualization
- Survey results
- Resource allocation
