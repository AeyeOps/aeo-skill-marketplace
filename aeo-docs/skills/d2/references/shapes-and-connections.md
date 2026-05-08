# D2 Shapes and Connections — full reference

## All shape values

`shape:` accepts any of these. Most are visual variations on a rectangle; the eight at the bottom of the table change semantics.

### Visual-only shapes (just change appearance)

| `shape:` value | What it looks like / when to use |
|---|---|
| `rectangle` | Default. The boring box. |
| `square` | Forced 1:1 box. |
| `page` | Document page corner. Use for "doc"/"spec". |
| `parallelogram` | Skewed box. Flowchart input/output. |
| `document` | Wavy-bottom doc. |
| `cylinder` | DB / storage. |
| `queue` | Side-bar queue / stream / kafka topic. |
| `package` | Box with tab. Use for module/package. |
| `step` | Chevron-shaped step in a process flow. |
| `callout` | Speech-bubble-like callout. |
| `stored_data` | Stored-data tape symbol. |
| `person` | Stick figure. Users/actors. |
| `diamond` | Decision node in flowcharts. |
| `oval` | Ellipse. |
| `circle` | Forced 1:1 circle. |
| `hexagon` | Honeycomb cell. Service/k8s pod-ish. |
| `cloud` | Cloud bubble. Internet/external service. |
| `c4-person` | C4-model styled person. (Pairs with theme `303`.) |

### Semantic shapes (change parsing / layout rules)

| `shape:` value | Effect |
|---|---|
| `text` | Plain text — no surrounding box. |
| `code` | Code block — combine with `style.font: mono` and a `\|<lang> ... \|` body. |
| `image` | Borderless image-only node. Pair with `icon: <url>`. Set `width:`/`height:` to size. |
| `class` | UML class. Children become fields/methods. |
| `sql_table` | DB table. Children become rows (column-name: type). |
| `sequence_diagram` | Container is laid out as actor lanes + time arrows. |
| `hierarchy` | Tree layout from connections. Forbids `top:`/`left:`. |
| `grid-rows: N` / `grid-columns: N` | (Not a `shape:` value but acts like one) — children flow into a grid. |

### Setting the shape

```d2
# Three equivalent forms
db: { shape: cylinder }
db.shape: cylinder
db: My Database { shape: cylinder }
```

## Connections

### The four operators

```d2
a -> b      # directed (a to b)
a <- b      # reverse (b to a — equivalent to b -> a)
a <-> b     # bidirectional (two-headed arrow)
a -- b      # undirected (no arrowhead)
```

### Chained connections

```d2
client -> api -> worker -> db
# Same as:
# client -> api
# api -> worker
# worker -> db
```

### Connections create shapes implicitly

If `client` was never declared, the line above creates it. To pre-declare with attributes, do so above the connection line.

### Labeling a connection

```d2
api -> db: writes
api -> db: "long, comma-containing label"
api -> db: |md
  Returns a `User` object.
  - On 404, returns null
|
```

### Multiple connections between the same pair

Each line creates a *new* edge — they do not override.

```d2
api -> db: read
api -> db: write
api -> db: backup
```

To address one specifically, index it:

```d2
(api -> db)[0].style.stroke: green
(api -> db)[1].style.stroke: red
(api -> db)[2].style.stroke-dash: 4
```

`(api -> db)[*]` matches all connections between the pair.

## Arrowheads

By default, `->` and `<-` use a triangle; `<->` uses a triangle on both sides; `--` has none.

### Custom arrowhead shapes

Override either end with `source-arrowhead` or `target-arrowhead`:

```d2
a -> b: {
  target-arrowhead: {
    shape: diamond
    style.filled: true
  }
}
```

**All arrowhead `shape:` values** (these are valid only as arrowhead shapes, not as standalone shape values):

| Value | Look | Common use |
|---|---|---|
| `triangle` | filled triangle (default) | generic arrow |
| `arrow` | sharper triangle | emphatic arrow |
| `diamond` | rhombus (use `style.filled: true` for solid) | UML composition / aggregation |
| `circle` | small circle | UML association |
| `box` | small square | UML realization |
| `cross` | crossed line | UML "no" / break |
| `cf-one` | crow's foot "one" | ER cardinality |
| `cf-one-required` | crow's foot, exactly one | ER cardinality |
| `cf-many` | crow's foot, many | ER cardinality |
| `cf-many-required` | crow's foot, one or more | ER cardinality |

### Arrowhead labels

Short labels are allowed on arrowheads. Useful for cardinalities:

```d2
order -> customer: placed by {
  source-arrowhead: 1..*
  target-arrowhead: 1
}
```

### Useful arrowhead recipes

```d2
# UML inheritance (target = empty triangle)
sub -> super: {
  target-arrowhead: {
    shape: triangle
    style.filled: false
  }
}

# UML composition (target = solid diamond)
container -> part: {
  target-arrowhead: {
    shape: diamond
    style.filled: true
  }
}

# UML aggregation (target = empty diamond)
team -> member: {
  target-arrowhead: {
    shape: diamond
    style.filled: false
  }
}

# ER one-to-many
customer -> order: places {
  source-arrowhead.shape: cf-one-required
  target-arrowhead.shape: cf-many
}
```

## Labels — every form

### Shorthand on the shape line

```d2
api: API Gateway
```

### Long label via `label:` attribute

```d2
api: { label: API Gateway }
```

Only needed when you also want sub-attributes like `label.near`.

### Multiline labels

```d2
# Newline in a quoted string
note: "First line\nSecond line"

# Markdown block (best for long content)
desc: |md
  # Section heading

  Paragraph **bold**, *italic*.
  - bullet
  - bullet
|

# Plain text block (no markdown rendering, just a label)
text-only: |
  Just a multi-line label,
  newlines preserved as-is.
|
```

### Label position via `label.near`

Inside the shape:
```
top-left      top-center     top-right
center-left                  center-right
bottom-left   bottom-center  bottom-right
```

Outside the shape (note the order swap on the left/right rows):
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
service: API {
  label.near: outside-bottom-center
}
```

For connection labels, valid positions are `start`, `center`, `end`:

```d2
a -> b: synced { label.near: start }
```

### Unicode and emoji labels

Both work natively (font permitting):

```d2
welcome: 你好 — مرحبا — こんにちは — 🌍🚀
fail -> retry: 🔁
```

### Quoting and escaping

| Situation | What to do |
|---|---|
| Hex color | Quote: `"#4baae5"` (unquoted `#` starts a comment) |
| Key contains `.` | Quote: `"server-v1.2"` |
| Key is a reserved keyword | Escape with `\` or quote: `\style: foo` |
| Want to use `${var}` literally | Single-quote: `'${var}'` |
| Comment in a label | Escape `#` as `\#` |
| Want vertical bar `\|` in a label | Use a different delimiter: `name: \|`md ... `\|` or `name: \|\|md ... \|\|` |

## Comments

```d2
# Line comment
api -> db   # trailing comment

# Block comment using triple-double-quotes
"""
This is a multi-line block comment.
Useful for inline docs at the top of a file.
"""
```

## The `null` value (delete)

Setting any key to `null` removes it. Useful in scenarios/steps and after `...@import`s.

```d2
# Remove a shape (and all its incoming/outgoing edges)
to-remove: null

# Remove an attribute
api.style.fill: null

# Remove a specific connection
(a -> b)[0]: null
```

## Connection styling — quick reference

```d2
a -> b: requests {
  style: {
    stroke: "#1565c0"        # color
    stroke-width: 2          # 0..15
    stroke-dash: 4           # 0..10 (0 = solid)
    animated: true           # marching-ants stroke (SVG only)
    opacity: 0.8             # 0..1
    border-radius: 20        # softens orthogonal corners (ELK only). Range works far beyond
                             # the documented 0–20: 15–25 = soft architectural, 50–100 = curve-like.
                             # Per-edge AND per-class. No effect on straight edges or under dagre.
    font-color: "#0d47a1"
    font-size: 14
    italic: true
  }
}
```

For the full picture of edge routing, curves vs. orthogonal, multi-bend workarounds, and the grid-vs-ELK pitfall: see `references/edge-routing.md`.

`fill` and `shadow` and `3d` and `multiple` are **not** valid on connections.

## Source-arrowhead vs target-arrowhead — a caveat

Arrowheads are only rendered on real endpoints. `a -> b` has no source arrowhead — only target. So `source-arrowhead.shape: diamond` on a `->` connection does nothing. Use `<-` or `<->` if you want a source-side decoration.

## Width and height

```d2
big-box: {
  width: 400        # all engines (non-containers)
  height: 200
}

# Containers: only ELK currently honors width/height on containers.
prod: {
  width: 800
  height: 600
  api -> db
}
```

## Cheat sheet

```text
# Shape declaration:
key: Label                       # shape with label
key.shape: <shape-name>          # shape attribute via dot
key: { shape: <name>; label: L } # shape via attributes block

# Connection operators:
a -> b      # directed
a <- b      # reverse
a <-> b     # bidirectional
a -- b      # undirected

# Connection styling/label:
a -> b: My Label { style.stroke: red }

# Multiple connections between same pair:
a -> b
a -> b
(a -> b)[0].style: { ... }       # first edge
(a -> b)[*].style: { ... }       # all edges

# Arrowheads:
a -> b: { source-arrowhead: { shape: diamond; style.filled: true } }
a -> b: { target-arrowhead: { shape: cf-many } }
a -> b: { target-arrowhead.label: 1..* }      # short cardinality label

# Labels with markdown:
key: |md
  # Markdown
  - bullet
|
```
