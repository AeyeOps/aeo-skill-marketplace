# Grid Diagrams and Hierarchies

D2 has two structural layouts that override the auto-layout engine: grid (`grid-rows:` / `grid-columns:`) and hierarchy (`shape: hierarchy`).

## Grid diagrams

Adding `grid-rows: N` or `grid-columns: N` to a container makes its children flow into a grid in declaration order.

### Single-axis grid

```d2
quarterly-roadmap: {
  grid-columns: 3        # 3 columns; rows fill as needed

  Q1
  Q2
  Q3
  Q4
  Q5
}
```

Children fill column-first across the row, then wrap to the next row when the column count is met.

```d2
features: {
  grid-rows: 2           # 2 rows; columns fill as needed

  feature 1
  feature 2
  feature 3
  feature 4
}
```

`grid-rows` fills row-first instead.

### Two-axis grid

```d2
ports-and-adapters: {
  grid-rows: 3
  grid-columns: 4

  inbound      adapter-1   port-1   domain-1
  inbound-2    adapter-2   port-2   domain-2
  inbound-3    adapter-3   port-3   domain-3
}
```

When both are set, you get a fixed grid. The dominant direction (which fills first) is determined by **which keyword is declared first**:

```d2
# rows fill first (row-major)
grid-rows: 3
grid-columns: 4

# columns fill first (column-major)
grid-columns: 4
grid-rows: 3
```

### Grid gaps

```d2
matrix: {
  grid-rows: 3
  grid-columns: 3
  grid-gap: 30                   # uniform gap

  vertical-gap: 50              # OR set independently
  horizontal-gap: 10

  a; b; c
  d; e; f
  g; h; i
}
```

When both `grid-gap` and `vertical-gap`/`horizontal-gap` are set, the more specific one wins.

### Cell sizing

You can set `width:` or `height:` on individual cells, but **rows and columns equalize to the largest cell**, so a tall cell makes its whole row tall.

```d2
grid: {
  grid-columns: 3
  big: { width: 200; height: 200 }
  small1
  small2
}
```

To force visual gaps without affecting size, use invisible padding shapes:

```d2
grid: {
  grid-columns: 4

  cell1
  spacer1: ""           # invisible padding
  spacer1.style.opacity: 0
  cell2
  cell3
}
```

### Nested grids

```d2
dashboard: {
  grid-columns: 2

  metrics: {
    grid-rows: 2
    revenue
    daily-active-users
    churn
    NPS
  }

  events: {
    grid-rows: 2
    signups
    conversions
    cancellations
    refunds
  }
}
```

### Connections inside vs. outside grids

Connections **inside** a grid are routed to/from the cells normally — but the cells themselves stay locked in place. Connections **between** a grid cell and an external shape route between the grid container and the shape, not to the specific cell.

If you need to connect to a specific cell from outside, restructure: make the grid's cells siblings instead of nested.

### Using grids for tables

Set `grid-gap: 0` and remove borders to make tightly packed table rows:

```d2
table: {
  grid-columns: 3
  grid-gap: 0
  style: {
    stroke-width: 0
  }

  # Header row
  h1: NAME    { style: { fill: lightgray; bold: true } }
  h2: ROLE    { style: { fill: lightgray; bold: true } }
  h3: SALARY  { style: { fill: lightgray; bold: true } }

  # Data rows
  Alice;     Engineer;    100000
  Bob;       Designer;    95000
  Carol;     PM;          110000
}
```

### Animating a grid build-up

Each step adds one more cell — use with `--animate-interval=1500`:

```d2
build: {
  grid-columns: 3

  steps: {
    1: { a }
    2: { b }
    3: { c }
    4: { d }
  }
}
```

## Hierarchy (`shape: hierarchy`)

Renders the connections inside as a tree. Children of the hierarchy container are nodes; connections become parent→child relationships.

```d2
org: {
  shape: hierarchy

  CEO
  CTO
  CFO
  COO

  CEO -> CTO
  CEO -> CFO
  CEO -> COO

  CTO -> "VP Eng"
  CTO -> "VP Data"
  CFO -> "VP Finance"
}
```

### Hard rules

- **You cannot use `top:` / `left:` / `near:` inside a `shape: hierarchy` container.** D2 errors out.
- The tree direction follows the container's `direction:`.
- Self-loops are not supported in hierarchies.

```d2
direction: right        # tree grows to the right
family-tree: {
  shape: hierarchy
  Grandparent -> Parent1
  Grandparent -> Parent2
  Parent1 -> Child1
  Parent1 -> Child2
  Parent2 -> Child3
}
```

## When to use which

| Situation | Use |
|---|---|
| Wireframe / dashboard / table layout | `grid-rows` / `grid-columns` |
| Strict M×N tile arrangement | grid (set both axes) |
| Org chart, file tree, taxonomy | `shape: hierarchy` |
| Family tree, decision tree | `shape: hierarchy` |
| Anything where positions should auto-route | default (no grid, no hierarchy) — let dagre/elk/tala work |
| Pure flowchart with branches | default — don't use hierarchy unless you really want strict tree layout |

## Cheat sheet

```text
container: {
  grid-rows: N            # rows fill first if set first
  grid-columns: N         # columns fill first if set first
  grid-gap: N             # uniform gap
  vertical-gap: N         # row-direction gap
  horizontal-gap: N       # column-direction gap

  child1; child2; child3  # populate cells in declaration order
}

container: {
  shape: hierarchy        # tree layout
  a -> b
  a -> c
  b -> d
}
# Note: top/left/near are FORBIDDEN inside shape: hierarchy
```
