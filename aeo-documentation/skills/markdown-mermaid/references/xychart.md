# XY Charts

**Keyword:** `xychart-beta`

**Purpose:** Plot data on X/Y axes (line and bar charts).

## Basic Syntax

```mermaid
xychart-beta
    title "Sales Data"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Revenue" 0 --> 100
    line [20, 45, 60, 80]
    bar [15, 40, 55, 75]
```

## Chart Types

**Line chart:**
```mermaid
xychart-beta
    line [2.3, 45.5, 67.2, -12.4]
```

**Bar chart:**
```mermaid
xychart-beta
    bar [100, 200, 150, 300]
```

**Combined:**
```mermaid
xychart-beta
    x-axis [Jan, Feb, Mar]
    line "Actual" [10, 20, 15]
    bar "Target" [12, 18, 16]
```

## Axis Configuration

**X-axis (categorical):**
```mermaid
x-axis "Month" [Jan, "Feb 2025", Mar]
```

**X-axis (numeric range):**
```mermaid
x-axis "Time (s)" 0 --> 100
```

**Y-axis (always numeric):**
```mermaid
y-axis "Temperature (C)" -20 --> 40
```

**Auto-range:**
```mermaid
y-axis "Auto-scaled"
```

## Orientation

**Horizontal:**
```mermaid
xychart-beta horizontal
    x-axis [A, B, C]
    bar [10, 20, 30]
```

## Title

```mermaid
xychart-beta
    title "Chart Title"
```

Multi-word titles require quotes.

## Key Limitations
- Only line and bar charts supported
- Y-axis cannot have categorical values (numeric only)
- X-axis supports categorical OR numeric (not mixed)
- Limited advanced charting features

## When to Use
- Simple data visualization
- Embedded charts in documentation
- Quick trend analysis
- Comparative bar charts
