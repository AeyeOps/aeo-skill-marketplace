# Quadrant Charts

**Keyword:** `quadrantChart`

**Purpose:** Four-quadrant analysis (priority matrix, SWOT, etc.).

## Basic Syntax

```mermaid
quadrantChart
    title Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Quick Wins
    quadrant-2 Major Projects
    quadrant-3 Fill-ins
    quadrant-4 Thankless Tasks
    Task A: [0.3, 0.8]
    Task B: [0.7, 0.9]
    Task C: [0.2, 0.2]
```

## Axis Configuration

**Full syntax:**
```mermaid
x-axis Left Label --> Right Label
y-axis Bottom Label --> Top Label
```

**Short syntax:**
```mermaid
x-axis Horizontal Axis
y-axis Vertical Axis
```

## Quadrant Labels

- `quadrant-1` - Top right
- `quadrant-2` - Top left
- `quadrant-3` - Bottom left
- `quadrant-4` - Bottom right

## Data Points

**Basic:**
```mermaid
Point Name: [x, y]
```

**With styling:**
```mermaid
Point A: [0.9, 0.8] radius: 15, color: #ff0000
```

**Class-based styling:**
```mermaid
quadrantChart
    Point A:::class1: [0.5, 0.5]
    classDef class1 color: #109060, radius: 20
```

**Style properties:**
- `color` - Fill color
- `radius` - Point size
- `stroke-width` - Border width
- `stroke-color` - Border color

## Key Limitations
- Coordinates must be 0.0 to 1.0
- Limited to 2D visualization
- Fixed quadrant layout

## When to Use
- Priority matrices (Eisenhower)
- Risk/impact assessment
- SWOT analysis
- Strategic planning
