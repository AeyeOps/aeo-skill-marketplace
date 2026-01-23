# Block Diagrams

**Keyword:** `block-beta`

**Purpose:** Custom layout diagrams with manual positioning (CSS grid-style).

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Columns and Layout](#columns-and-layout)
- [Block Shapes](#block-shapes)
- [Composite Blocks](#composite-blocks)
- [Space Blocks](#space-blocks)
- [Edges and Connections](#edges-and-connections)
- [Block Width](#block-width)
- [Key Principle](#key-principle)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
block-beta
    columns 3
    A B C
    D E F
```

## Columns and Layout

```mermaid
block-beta
    columns 4
    Block1 Block2 Block3 Block4
    Block5:2 Block6:2
```

**Block spanning:** `BlockName:n` (spans n columns)

## Block Shapes

```mermaid
block-beta
    A["Rectangle"]
    B("Rounded")
    C(["Stadium"])
    D[["Subroutine"]]
    E[("Cylinder")]
    F(("Circle"))
    G>"Asymmetric"]
    H{"Rhombus"}
    I{{"Hexagon"}}
    J[/"Parallelogram"/]
    K[\"Trapezoid"\]
    L(("Double Circle"))
```

## Composite Blocks

```mermaid
block-beta
    block:group1
        A
        B
    end
    block:group2
        C
        D
    end
```

## Space Blocks

```mermaid
block-beta
    columns 3
    A space B
    space:2 C
    D E space
```

**Sized spaces:** `space:n` (n columns)

## Edges and Connections

```mermaid
block-beta
    A --> B
    B --> C
    A -.-> C

    A -- "Label" --> D
```

## Block Width

```mermaid
block-beta
    columns 3
    A["Small"]
    B["Medium Block"]:2
    C["Large Block Description"]:3
```

## Key Principle

Block diagrams provide **full manual control** over positioning, unlike flowcharts with automatic layout.

## Key Limitations
- Requires manual layout planning
- No automatic positioning
- Complex layouts need careful column calculation

## When to Use
- Network diagrams
- System architecture
- Infrastructure layouts
- Custom positioned components
