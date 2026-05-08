# Edge Routing — Curves, Corners, and Waypoints

D2 gives you a lot of per-edge style control but very little control over the **path** an edge takes. The path is the engine's job. This file is about (a) what you actually control, (b) the few levers that change visual character of edges, and (c) the workarounds for the things D2 doesn't natively support.

Everything here is verified against D2 v0.7.x. Where docs and reality disagree, this file follows reality.

## What you control vs. what the engine controls

| Concern | Who decides |
|---|---|
| The route itself (where the line bends, which side of a node it enters) | Layout engine — global, not per-edge |
| Whether routes are orthogonal or curved | Engine — `dagre` curves, `elk` orthogonal, `tala` mixed |
| Stroke color, width, dash, opacity, animation | You — per edge or per class |
| Corner softness on orthogonal routes | You — per edge or per class, via `border-radius` |
| Arrowhead shape at either end | You — per edge |

Three things follow from this:
- You **cannot** mix true Bezier curves and orthogonal routes in the same diagram. Engine is global.
- You **can** mix sharp corners and rounded corners freely on a per-edge basis.
- You **can** style every other edge attribute independently.

## The big lever you probably aren't using: `style.border-radius`

`style.border-radius` on a connection rounds the corners of orthogonal routes. It only does anything when (a) the engine is `elk` and (b) the edge actually has corners (a perfectly straight edge has nothing to round).

The docs say the range is 0–20. **Higher values up to 100+ work without errors and produce visibly different results.** Empirically:

| Value | Visual character |
|---|---|
| `0` (default) | Sharp 90° corners. Architectural / technical look. |
| `5–10` | Subtle softening. Easy to miss. |
| `15–25` | Visibly rounded corners. The "soft architectural" sweet spot. |
| `50–100` | Reads as a Bezier curve, even though the underlying route is still orthogonal. Use when you want a curvy feel without giving up ELK's clean routing. |

```d2
vars: { d2-config: { layout-engine: elk } }
direction: right

src -> a: { style: { border-radius: 0 } }     # sharp
src -> b: { style: { border-radius: 15 } }    # soft
src -> c: { style: { border-radius: 50 } }    # curve-like
```

This is the single most useful per-edge styling control D2 exposes. If a user asks for "curved arrows" or "smoother lines", reach for this before switching engines.

## Curves vs. rounded corners — which is which

These are different visual idioms and they have to be chosen at the diagram level:

- **`dagre` engine** — every multi-segment route is a smooth Bezier curve from source to target. Diagonal flow. Global; no per-edge override.
- **`elk` engine + per-edge `border-radius`** — orthogonal route (only horizontal/vertical segments) with corners softened to whatever radius you pick. Right-angle skeleton, rounded joints. Per-edge.

Side-by-side guidance:

| Want | Use |
|---|---|
| Smooth flowing diagonals through the whole diagram | `dagre` (accept that you also lose ELK's clean container handling) |
| Crisp orthogonal routing for clarity, with one or two arrows softened | `elk` + selective `border-radius` |
| Architectural look where everything has soft corners | `elk` + `border-radius: 20` on a connection class applied everywhere |
| Whiteboard / hand-drawn look | Any engine + `vars.d2-config.sketch: true` (different lever — see styling-and-themes.md) |

You **cannot** ask `elk` for Bezier curves on a single edge, and you **cannot** ask `dagre` to make one specific edge orthogonal. The engine decides for the whole diagram.

## Per-edge style — the full working menu

These all stack on the same edge in any engine, controlled per-connection or per-class:

```d2
a -> b: my label {
  style: {
    stroke: "#cd102f"        # any color (quote hex)
    stroke-width: 2          # 0–15
    stroke-dash: 4           # 0–10 (0 = solid; larger = longer dashes)
    border-radius: 20        # softens corners; ELK orthogonal only
    animated: true           # marching-ants flow (SVG only, not PNG)
    opacity: 0.8             # 0..1
    font-color: "#0d47a1"
    font-size: 14
    italic: true
  }
  source-arrowhead: { shape: cf-many }
  target-arrowhead: { shape: diamond; style.filled: true }
}
```

Not valid on connections: `fill`, `shadow`, `3d`, `multiple`. Use `stroke` for connection color.

## Defaults + overrides — the class pattern

If you find yourself repeating the same edge style three or more times, hoist it into a class. The `style.X` syntax on an individual edge then overrides just that one attribute:

```d2
classes: {
  flow: {
    style: { stroke: "#2098d1"; stroke-width: 2; border-radius: 20 }
  }
  alert: {
    style: { stroke: "#cd102f"; stroke-width: 3; border-radius: 20; stroke-dash: 4 }
  }
  control: {
    style: { stroke: "#999"; stroke-width: 1; border-radius: 20; stroke-dash: 3 }
  }
}

a -> b: { class: flow }
b -> c: { class: flow }
a -> d: { class: alert }
a -> e: {
  class: control
  style.border-radius: 0   # one-off override of the class default
}
```

The override only changes the attribute you name. Everything else from the class still applies. Use this to set "all my data-flow edges look like X, except this one specific case."

## Multi-bend routing — the awkward bit

D2 has no waypoint primitive. The maintainer has confirmed in [discussion #2156](https://github.com/terrastruct/d2/discussions/2156) that attaching shapes to edges (and by extension, forcing routes through specific points) is a longstanding TODO ([issue #423](https://github.com/terrastruct/d2/issues/423)).

This means: **you cannot say "make this edge bend right, then up, then right again."** What you can do is one of these three things, in order of preference.

### 1. Trust ELK to route well (preferred)

This is what works in 90% of cases. ELK is genuinely good at routing around clusters when you don't fight it. The recipe:

- `vars.d2-config.layout-engine: elk`
- `direction: right` (or `down`) — pick the dominant flow
- **No `grid-rows:` / `grid-columns:` on containers whose children connect across containers** (see pitfall below)
- Real connections only — don't pre-position things

Then ELK does the right thing automatically. Edges that need to bypass a dense cluster will route over or under it. Edges within a row stay in the row. Cross-row edges break out cleanly.

### 2. Influence ELK with `direction:` and `near: <corner>`

If ELK is making a defensible but unwanted choice, the two levers that actually move it are:

- **`direction:` at the diagram root** — `right` produces left-to-right flow with cleaner L-bends than `down` for most architecture diagrams.
- **`near: top-left` / `top-right` / `bottom-left` / etc. on a specific shape** — pins it toward a canvas corner. This is the one positional hint that works with ELK. Note: `near: <other-shape-id>` is **TALA only**; ELK errors on it.

```d2
vars: { d2-config: { layout-engine: elk } }
direction: right

title: "Architecture" { near: top-center; shape: text }
legend: { near: bottom-right; ... }
```

### 3. Invisible-waypoint kludge (rare; fragile)

If you absolutely need a route to deviate from the natural path, you can chain through a zero-opacity 1×1 node and suppress arrowheads on the intermediate segments. This is a workaround, not a feature.

```d2
vars: { d2-config: { layout-engine: elk } }

src: { ... }
dst: { ... }

# The waypoint — invisible, near a canvas corner to displace it
wp: {
  label: ""
  width: 1
  height: 1
  near: top-right
  style: { opacity: 0; stroke-width: 0; fill: transparent }
}

src -> wp: {
  style: { stroke: "#cd102f"; border-radius: 20 }
  target-arrowhead.shape: none     # critical: hide the arrowhead on the segment ending at wp
}
wp -> dst: {
  style: { stroke: "#cd102f"; border-radius: 20 }
}
```

Caveats — read these before relying on this:

- The visible bend depends on ELK actually placing the waypoint off-axis. With only `near: <corner>`, ELK may collapse the waypoint onto the natural path if the layout is compact, producing a straight line.
- Two waypoints in a chain (`src -> wp1 -> wp2 -> dst`) for a Z-shape need `target-arrowhead.shape: none` on both intermediate segments.
- Each segment is technically a separate edge. Labels go on individual segments, not on the logical "whole" route.
- TALA is the proper tool here — its `near: <other-shape>` lets you anchor the waypoint to a real shape with a known position. If a user has TALA, prefer it.

## Pitfall: grid layout breaks ELK's orthogonal routing

This is not in the official docs but is empirically reproducible. When a container uses `grid-rows:` or `grid-columns:` and its children connect to shapes **outside** the grid, ELK silently falls back from orthogonal to polyline (diagonal) routing for those cross-grid edges. The visible result: lines that go diagonally across cards, often crossing through other content.

The fix is one of:

1. **Drop the grid.** Let ELK lay out the children itself. This is usually the cleanest fix — ELK arranges siblings in a row naturally and routes orthogonally.
2. **Connect to the parent container, not to individual grid children.** ELK can route orthogonally to the container as a whole.
3. **Switch to TALA.** TALA handles grid + cross-edges better. Paid.

Quick test you can run if you suspect this is biting you: render once with the grid, render once without the grid (just declare the children as siblings and let ELK arrange them). If the second is dramatically cleaner, this is the cause.

## What you cannot do (and shouldn't waste time trying)

- **Force ELK into strict orthogonal mode.** ELK has an `edgeRouting=ORTHOGONAL` option, but D2's CLI does not expose it. Only `--elk-algorithm`, `--elk-padding`, `--elk-nodeNodeBetweenLayers`, `--elk-edgeNodeBetweenLayers`, `--elk-nodeSelfLoop` are passable as of v0.7.x.
- **Mix routing styles in one diagram.** Engine is global. No per-edge engine override exists.
- **Place waypoints at exact pixel coordinates.** That's `top:` / `left:`, which is TALA-only.
- **Pin a waypoint near a non-corner shape with ELK.** `near: <other-shape>` is TALA-only.
- **Get `border-radius` to round a straight edge.** Without a corner to round, the attribute does nothing.

## Cookbook — common requests, working recipes

### "Make all the arrows curvy"

```d2
vars: { d2-config: { layout-engine: elk } }
classes: {
  curvy: { style: { stroke-width: 2; border-radius: 50 } }
}
(* -> *)[*].class: curvy   # apply to every edge
```

(Or, if you want true Bezier instead of softened orthogonal, switch to `dagre` and skip the class.)

### "Soft architectural look — orthogonal but rounded"

```d2
vars: { d2-config: { layout-engine: elk } }
classes: {
  edge: { style: { stroke: "#2098d1"; stroke-width: 2; border-radius: 20 } }
}
(* -> *)[*].class: edge
```

### "One critical-path arrow that stands out"

```d2
classes: {
  flow:  { style: { stroke: "#999"; stroke-width: 2; border-radius: 15 } }
  alert: { style: { stroke: "#cd102f"; stroke-width: 4; border-radius: 15; stroke-dash: 4 } }
}
a -> b: { class: flow }
b -> c: { class: flow }
a -> c: error path { class: alert }
```

### "Most arrows soft, but one specific one needs sharp corners for emphasis"

```d2
classes: {
  edge: { style: { stroke-width: 2; border-radius: 20 } }
}
a -> b: { class: edge }
b -> c: { class: edge }
a -> c: {
  class: edge
  style.border-radius: 0     # override only the radius
}
```

### "ER diagram with cardinality crow's-feet"

```d2
customer -> order: places {
  source-arrowhead.shape: cf-one-required
  target-arrowhead.shape: cf-many
  style.border-radius: 10
}
```

### "Animated data flow"

```d2
client -> api: requests {
  style: {
    stroke: "#2098d1"
    stroke-width: 3
    stroke-dash: 5
    animated: true        # SVG output only — no effect in PNG
    border-radius: 20
  }
}
```

## Choosing your defaults — the boring summary

For ~90% of architecture-style diagrams, this is the right starting point:

```d2
vars: {
  d2-config: {
    layout-engine: elk
    pad: 40
  }
}
direction: right

classes: {
  card: { style: { fill: "#f8f8f8"; stroke: "#2098d1"; stroke-width: 2 } }
  edge: { style: { stroke: "#2098d1"; stroke-width: 2; border-radius: 20 } }
}

# ... shapes and connections, no grid containers on connected groups ...
```

Then override per edge or per class as needed. This gives you crisp orthogonal routing, soft corners, a coherent palette, and full per-edge control when you need it.
