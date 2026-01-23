# Treemap Diagrams

**Keyword:** `treemap-beta`

**Purpose:** Hierarchical data as nested rectangles.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Node Types](#node-types)
- [Hierarchy with Indentation](#hierarchy-with-indentation)
- [Styling](#styling)
- [Configuration](#configuration)
- [Value Formatting](#value-formatting)
- [Example: Budget Allocation](#example-budget-allocation)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
treemap-beta
    "Root"
        "Category A"
            "Item A1": 100
            "Item A2": 50
        "Category B"
            "Item B1": 75
            "Item B2": 125
```

## Node Types

**Sections (parent nodes):**
```mermaid
"Section Name"
```

**Leaf nodes (with values):**
```mermaid
"Leaf Name": value
```

## Hierarchy with Indentation

```mermaid
treemap-beta
"Company"
    "Engineering"
        "Backend": 45
        "Frontend": 30
        "DevOps": 15
    "Sales"
        "Enterprise": 60
        "SMB": 40
    "Marketing"
        "Content": 20
        "Paid Ads": 35
```

## Styling

**Class-based:**
```mermaid
treemap-beta
"Root"
    "Important":::highlight: 100
    "Normal": 50

classDef highlight fill:#ff0,stroke:#f00
```

## Configuration

```yaml
---
config:
  treemap:
    useMaxWidth: true
    padding: 10
    showValues: true
    valueFontSize: 12
    labelFontSize: 14
    valueFormat: ','
---
treemap-beta
"Data"
    "A": 1000
    "B": 2500
```

**Options:**
- `useMaxWidth` - Scale to 100% width (default: true)
- `padding` - Space between nodes (default: 10)
- `showValues` - Display values (default: true)
- `valueFontSize` - Value text size (default: 12)
- `labelFontSize` - Label text size (default: 14)
- `valueFormat` - D3 format specifier (default: ',')

## Value Formatting

**D3 Specifiers:**
```yaml
valueFormat: '$,.2f'  # $1,234.56
valueFormat: '.1%'    # 45.6%
valueFormat: ',.0f'   # 1,234
```

**Common formats:**
- `,` - Thousands separator
- `$` - Dollar prefix
- `.2f` - Two decimals
- `.1%` - Percentage with one decimal

## Example: Budget Allocation

```mermaid
treemap-beta
"2025 Budget"
    "Development"
        "Salaries": 500000
        "Tools": 50000
        "Training": 25000
    "Infrastructure"
        "Cloud": 100000
        "Licenses": 30000
    "Marketing"
        "Advertising": 150000
        "Events": 75000
```

## Key Limitations
- Experimental feature
- Limited visual customization
- Best for 2-4 hierarchy levels

## When to Use
- Budget visualization
- Disk usage analysis
- Portfolio allocation
- Organizational structure
