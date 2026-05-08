# Layout Engines

D2 ships with multiple layout engines. You pick one per render.

| Engine | Bundled? | Cost | When to use |
|---|---|---|---|
| `dagre` | yes (default) | free | Hierarchical flowcharts, fast |
| `elk` | yes | free | Best general-purpose; SQL/UML/deep-nesting |
| `tala` | external binary | paid | Software-architecture-specific |

## Selecting an engine

Three mechanisms, in increasing precedence (rightmost wins):

```d2
# 1. Inline
vars: { d2-config: { layout-engine: elk } }
```

```bash
# 2. Env var
D2_LAYOUT=elk d2 input.d2

# 3. CLI flag (highest)
d2 --layout=elk input.d2
```

## `dagre` (default)

Reference: https://github.com/dagrejs/dagre — same engine MermaidJS uses for flowcharts.

**Pros**:
- Very fast.
- Good for plain hierarchical / layered flowcharts.

**Cons**:
- Unmaintained since 2018.
- Multi-segment routes are *curved*, not orthogonal.
- No native ancestor↔descendant edge support — D2 ships a shim.
- Edge routing can be inexplicable (occasional dagre issue #256 quirks).

**Use for**: simple flowcharts, you prioritize speed, no cross-container edges.

## `elk` (recommended)

Reference: https://www.eclipse.org/elk/reference.html — Eclipse Layout Kernel; actively maintained.

**Pros**:
- Clean **orthogonal** routes.
- Handles container ↔ container routing natively.
- Fast.
- Routes SQL tables to **exact columns**.
- Honors `width:` and `height:` on containers (other engines ignore).

**Cons**:
- Strictly hierarchical.
- Some routes have unnecessary bends.
- No symmetry consideration.
- **`grid-rows:` / `grid-columns:` on a connected container breaks orthogonal routing.** When grid children connect to shapes outside the grid, ELK silently falls back to polyline (diagonal) routes for those cross-grid edges. Drop the grid or connect to the parent container instead. Detailed in `references/edge-routing.md`.
- Edge routing is **engine-global** — there is no per-edge way to make one specific edge curve while others stay orthogonal. For corner softening on a per-edge basis, use `style.border-radius` (still orthogonal underneath, just rounded joints). For true Bezier curves, switch the engine to `dagre`.

**Use for**: SQL/ER diagrams, UML, deep nesting, anything with cross-container edges. Honestly, for most polished diagrams.

## `tala` (paid, external)

Closed-source, paid. Install separately: https://github.com/terrastruct/tala. Manual: https://github.com/terrastruct/TALA/blob/master/TALA_User_Manual.pdf.

**Pros**:
- General orthogonal layout (not hierarchy/tree-only) — produces whiteboard-like layouts for non-hierarchical graphs.
- `top:` and `left:` for **locked positions** (TALA only).
- Considers symmetry.
- First-class container handling.
- Per-container `direction:` (TALA only).
- `near: <other-shape>` (TALA only).
- Connections route to exact rows/columns.
- Dynamic label positioning to avoid obstructions.

**Cons**:
- Paid.
- More layout volatility — small label changes can cascade into different layouts.

**Use for**: software architecture, non-hierarchical graphs, when you need pixel-locked positions or per-container directions.

## Feature support matrix

| Feature | dagre | elk | tala |
|---|---|---|---|
| `near: <constant>` (top-left, etc.) | ✓ | ✓ | ✓ |
| `near: <other-shape-id>` | ✗ | ✗ | ✓ |
| `width`/`height` on non-containers | ✓ | ✓ | ✓ |
| `width`/`height` on containers | ✗ | ✓ | planned |
| `top:` / `left:` (lock position) | ✗ | ✗ | ✓ |
| Ancestor → descendant edges | ✗ shim | ✓ | ✓ |
| Per-container `direction:` | ✗ | ✗ | ✓ |
| ASCII export support | falls back to ELK | ✓ | ✓ |

## `direction:`

Global directional hint. Values: `up`, `down` (default), `left`, `right`.

```d2
direction: right
a -> b -> c
```

For dagre/elk, `direction` is **global only** — the algorithms are inherently single-direction hierarchical.

For TALA, you can set `direction:` per-container:

```d2
vars: { d2-config: { layout-engine: tala } }
direction: down

a -> b -> c

b: {
  direction: right       # local override (TALA only)
  1 -> 2 -> 3
}

a: {
  direction: left        # local override (TALA only)
  foo -> bar
}
```

## `near` for positioning

`near` accepts these absolute positions for *any* shape (works in all engines):

```
top-left      top-center     top-right
center-left                  center-right
bottom-left   bottom-center  bottom-right
```

Common patterns:

```d2
title: |md
  # System Architecture
| { near: top-center }

legend: {
  near: bottom-right
  ok:  OK    { shape: text; style.font-color: green }
  err: Error { shape: text; style.font-color: red }
}

note: |md
  # Read me
  Click any service to drill in.
| { near: center-left }
```

`near: <shape-id>` (TALA only):

```d2
vars: { d2-config: { layout-engine: tala } }
aws: { load_balancer -> api; api -> db }

explanation: |md
  # Why we chose AWS
  - Better uptime
  - Free credits
| { near: aws }
```

## `label.near` and `icon.near` (any engine)

Per-shape positioning of label/icon. Adds `outside-*` and `border-*` prefixes:

Inside the shape:
```
top-left      top-center     top-right
center-left                  center-right
bottom-left   bottom-center  bottom-right
```

Outside the bounding box (note order swap on left/right rows):
```
outside-top-left      outside-top-center      outside-top-right
outside-left-center                            outside-right-center
outside-bottom-left   outside-bottom-center   outside-bottom-right
```

On the border:
```
border-top-left, border-top-center, border-top-right
border-left-center, border-right-center
border-bottom-left, border-bottom-center, border-bottom-right
```

```d2
direction: right
service: API {
  label.near: outside-bottom-center
  icon: https://icons.terrastruct.com/essentials%2F005-programmer.svg
  icon.near: outside-top-right
}
```

## `top:` / `left:` (TALA only)

Lock pixel positions. The engine routes around the locked shape:

```d2
vars: { d2-config: { layout-engine: tala } }
locked-shape: {
  top: 100
  left: 200
}
```

## `width:` and `height:`

```d2
my-shape: {
  width: 400
  height: 200
}
```

For non-containers, all engines honor this. For containers, **only ELK** currently honors `width:` / `height:` on containers (TALA support is on the roadmap; dagre never supports it).

## Choosing per situation

| The diagram is… | Use |
|---|---|
| A short flowchart | `dagre` (default) |
| An ER / UML / schema diagram | `elk` |
| A deeply nested architecture | `elk` |
| Anything with `near: <other-shape>` or per-container `direction:` | `tala` |
| Anything where you want pixel-locked positions | `tala` |
| Plain markdown notes pinned to corners | any engine |

## Cheat sheet

```text
# CLI
d2 --layout=dagre|elk|tala input.d2

# Inline
vars: { d2-config: { layout-engine: elk } }

# Direction (global)
direction: up | down | left | right       # default: down

# Direction (per-container, TALA only)
container: { direction: right; ... }

# Position
shape.near: top-center | center-right | ...        # any engine
shape.near: <other-shape-id>                       # TALA only
shape.top: 100; shape.left: 200                    # TALA only

# Size
shape.width: 200; shape.height: 100                # all engines for non-containers
container.width: 400; container.height: 300        # ELK only for containers

# Label/icon position (any engine)
shape.label.near: outside-bottom-center
shape.icon.near: outside-top-right
```
