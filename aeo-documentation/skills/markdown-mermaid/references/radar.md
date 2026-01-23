# Radar Charts

**Keyword:** `radar-beta`

**Purpose:** Multi-dimensional data comparison (spider/polar charts).

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Axis Definition](#axis-definition)
- [Data Curves](#data-curves)
- [Title](#title)
- [Configuration](#configuration)
- [Styling](#styling)
- [Example: Product Comparison](#example-product-comparison)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
radar-beta
    axis Performance, Usability, Cost, Scalability, Security
    curve Product_A{5, 4, 3, 4, 5}
    curve Product_B{3, 5, 4, 3, 4}
```

## Axis Definition

**Inline:**
```mermaid
radar-beta
    axis A, B, C, D
```

**With labels:**
```mermaid
radar-beta
    axis axis1["Performance"]
    axis axis2["Reliability"], axis3["Cost"]
```

## Data Curves

**Positional values:**
```mermaid
radar-beta
    axis A, B, C
    curve series1{10, 20, 30}
```

**Key-value pairs:**
```mermaid
radar-beta
    axis A, B, C
    curve series1{A: 10, C: 30, B: 20}
```

**With labels:**
```mermaid
radar-beta
    axis A, B, C
    curve series1["Product Alpha"]{5, 4, 3}
```

## Title

```mermaid
radar-beta
    title Performance Comparison
```

## Configuration

**Legend:**
```yaml
---
config:
  radar:
    showLegend: false
---
radar-beta
    curve A{1, 2, 3}
```

**Scale:**
```yaml
config:
  radar:
    min: 0
    max: 10
    ticks: 5
```

**Graticule:**
```yaml
config:
  radar:
    graticule: polygon
```

Options: `circle` (default), `polygon`

## Styling

```yaml
config:
  radar:
    axisColor: '#333333'
    curveOpacity: 0.7
    graticuleStrokeWidth: 1
    legendFontSize: 14
    curveTension: 0.17
```

## Example: Product Comparison

```mermaid
radar-beta
    title Product Feature Comparison
    axis Performance, Usability, Cost, Scalability, Security, Support
    curve "Product A"{9, 8, 4, 7, 9, 6}
    curve "Product B"{7, 9, 7, 6, 7, 8}
    curve "Product C"{6, 7, 9, 8, 6, 7}
```

## Key Limitations
- Experimental feature (v11.6.0+)
- Best with 3-8 dimensions
- Overlapping curves may be hard to read

## When to Use
- Product comparisons
- Skill assessments
- Performance metrics
- Multi-criteria analysis
