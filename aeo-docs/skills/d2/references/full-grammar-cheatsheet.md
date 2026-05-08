# Full Grammar Cheatsheet

A terse, syntax-only one-pager. For semantics and examples, see the topic-specific reference files.

## File anatomy

```d2
# Comments start with '#'
# """ block
# multi-line comment """

direction: right                # global direction (up|down|left|right)

vars: {                          # variables block
  d2-config: {                   # render configuration
    layout-engine: elk           # dagre | elk | tala
    theme-id: 0
    dark-theme-id: 200
    pad: 40
    sketch: false
    center: true
    theme-overrides: { B1: "#hex"; ... }
    data: { arbitrary: keys }    # third-party metadata
  }
  my-var: value
}

classes: {                       # reusable style bags
  foo: { style.fill: red; ... }
  bar: { width: 200; ... }
}

style: {                         # ROOT-level diagram styling
  fill: "#background"
  stroke: "#frame"
  stroke-width: 3
  fill-pattern: dots
  double-border: true
}

# Shape declarations and connections
a -> b -> c
```

## Identifiers

```d2
simple
"with dot.in name"            # quote when key has '.'
'literal ${not-expanded}'     # single-quote = no var substitution
"label-with-${var}"           # double-quote = expand vars
\#hash-literal                # escape '#' in keys (visibility prefix in classes)
\style                         # escape reserved keyword
```

## Shapes

```d2
key
key: Label
key: { shape: <name>; label: Long label; style: { ... } }
key.shape: <name>
key.style.fill: "#hex"

# Shape values:
# rectangle (default), square, page, parallelogram, document, cylinder,
# queue, package, step, callout, stored_data, person, diamond, oval,
# circle, hexagon, cloud, c4-person
# text, code, image
# class, sql_table, sequence_diagram, hierarchy
```

## Connections

```d2
a -> b               # directed
a <- b               # reverse
a <-> b              # bidirectional
a -- b               # undirected

a -> b -> c          # chained
a -> b: My Label
a -> b: { style.stroke: red }

# Multiple connections between same pair
a -> b
a -> b
(a -> b)[0].style.stroke: red    # index a specific edge
(a -> b)[*].style.stroke: red    # all edges between a and b
```

## Arrowheads

```d2
a -> b: {
  source-arrowhead: { shape: <ahshape>; style.filled: true; label: 1 }
  target-arrowhead: { shape: <ahshape>; style.filled: true; label: N }
}

# Arrowhead shape values:
#   triangle, arrow, diamond, circle, box, cross
#   cf-one, cf-one-required, cf-many, cf-many-required
```

## Containers (nesting)

```d2
parent.child.grandchild           # dot syntax
parent: {
  child: {
    grandchild
  }
}
parent.child -> other.descendant  # cross-container edge

container: {
  _.sibling -> other              # _ = parent scope
}
```

## Labels

```d2
shape: Plain label
shape: "label, with comma"
shape: |md
  # Markdown
  - bullet
|
shape: |tex
  E = mc^2
|
shape: |go
  fmt.Println("syntax-highlighted code")
|

# Pipe collisions: escalate
shape: || pipes | inside ||       # double-pipe
shape: ||| triple |||             # triple-pipe
shape: |' ... '|                  # custom delimiter

# Label position
shape.label.near: top-center      # 9 inside positions
shape.label.near: outside-top-center   # 8 outside positions
shape.label.near: border-top-center    # 9 border positions
```

## Styling

```d2
shape.style.<attr>: value
# OR
shape: { style: { attr: value; ... } }

# Properties:
opacity         0.0 .. 1.0
stroke          color | gradient | theme-code
fill            color | gradient | theme-code | transparent  (NOT on connections)
fill-pattern    dots | lines | grain | paper | none
stroke-width    1 .. 15
stroke-dash     0 .. 10
border-radius   0 .. 20
shadow          true | false      (shapes only)
3d              true | false      (rectangle/square only)
multiple        true | false      (shapes only)
double-border   true | false      (rectangle/oval; root)
font            mono              (only legal value)
font-size       8 .. 100
font-color      color
bold            true | false
italic          true | false
underline       true | false
text-transform  uppercase | lowercase | title | capitalize | none
animated        true | false
filled          true | false      (arrowhead shapes only)
```

## Theme color codes

```
N1..N7    neutrals (text, dividers, surfaces)
B1..B6    primary brand ramp
AA2, AA4, AA5    accent A
AB4, AB5         accent B
```

## Classes

```d2
classes: {
  my-class: {
    label: ...
    style: { fill: red; ... }
  }
}

shape.class: my-class
shape.class: [class1; class2]      # multiple — semicolon separated
```

## Vars

```d2
vars: { name: value }
shape: ${name}              # substitute
shape: '${name}'            # NO substitute (single quotes)
shape: "Hello ${name}"      # YES substitute (double quotes)

# Spread (inside maps)
shape: { ...${var-map} }
```

## Globs

```d2
*           current scope
**          recursive (descendants)
***         global (persists across imports/layers)

# On connections
(* -> *)[*].style.stroke: red
(a -> b)[0]                # index a specific edge between a, b

# Filters
&shape: person                     # only match shapes whose shape: is person
!&shape: person                    # inverse — anything except persons
&connected: true                   # has at least one edge
&leaf: true                        # not a container
&class: server                     # in array — element-match
&link: *                           # has 'link' attr (any value)
&src.attr / &dst.attr              # filter on connection endpoints

# Multiple & lines = AND
*: {
  &shape: person
  &connected: true
  ...
}
```

## Imports

```d2
a: @file.d2                  # regular — assign
a: { ...@file.d2 }            # spread — splice into map
a: { ...@file.d2.path.in.file }   # partial — drill in

# Quote names with dots
@"schema-v0.1.2"

# Relative (autoformat strips ./)
@../shared/classes
@./local → @local

# Absolute
@/abs/path
@"C:\windows\path"           # quote on Windows
```

## Boards (multi-diagram)

```d2
layers: {
  detail-1: { ... }          # NO inheritance
  detail-2: { ... }
}

scenarios: {
  variant: { ... }           # inherits parent layer; declare deltas
}

steps: {
  1: { ... }
  2: { ... }                 # inherits step 1
  3: { ... }                 # inherits step 2
}

# Internal nav
shape.link: layers.<name>
shape.link: scenarios.<name>
shape.link: steps.<n>
shape.link: _root_           # back to root
shape.link: _                # up one board
```

## Special diagram shapes

```d2
# Sequence diagrams
container: {
  shape: sequence_diagram
  alice -> bob: msg
  bob.note: text
  alt: { ... }    opt: { ... }    par: { ... }    loop: { ... }
}

# SQL tables
table: {
  shape: sql_table
  col_name: type
  col_name: type { constraint: primary_key }
  col_name: type { constraint: [primary_key; foreign_key] }
}

# UML class
MyClass: {
  shape: class
  field: type
  +public_field: type
  -private_field: type
  \#protected_field: type
  method(arg: type): return-type
}

# Hierarchy (tree)
container: {
  shape: hierarchy
  a -> b
  a -> c
}
# Note: top:/left:/near: forbidden inside

# Grid
container: {
  grid-rows: 3
  grid-columns: 4
  grid-gap: 30
  vertical-gap: 50
  horizontal-gap: 10
  child1; child2; child3
}

# Image-only node
logo: {
  shape: image
  icon: <url>
  width: 256; height: 256
}

# Plain text / code
note: { shape: text; ... }
code: { shape: code; style.font: mono }
```

## Positioning

```d2
# 'near' for shape position (any engine)
shape.near: top-left | top-center | top-right
shape.near: center-left | center-right
shape.near: bottom-left | bottom-center | bottom-right

# 'near' relative to another shape (TALA only)
shape.near: <other-shape-id>

# Locked pixel position (TALA only)
shape.top: 100
shape.left: 200

# Sizes
shape.width: N
shape.height: N
# (containers: only ELK supports width/height on containers)

# Label/icon positioning (any engine)
shape.label.near: outside-bottom-center
shape.icon.near: outside-top-right
```

## Tooltips and links

```d2
shape: { tooltip: Hover text }
shape: { tooltip: |md  ## Markdown body  | }
shape: { tooltip.near: top-center }    # always visible (pinned)

shape: { link: https://example.com }
shape: { link: layers.<name> }         # internal nav
```

## Null (delete)

```d2
shape: null
shape.attr: null
(a -> b)[0]: null
```

## Common pitfalls

| Don't | Do |
|---|---|
| `style.fill: #4baae5` (unquoted hex = comment) | `style.fill: "#4baae5"` |
| `a --> b` (Mermaid) | `a -> b` |
| `loop { ... }` (PlantUML keyword) | `loop: { ... }` (just a nested container in `sequence_diagram`) |
| `#protected:` in class diagrams | `\#protected:` or `"#protected":` |
| `style.fill: red` on a connection | use `stroke` (fill is shape-only) |
| `top: 100` in dagre/elk | only TALA supports `top:`/`left:` |
| `near: <id>` in dagre/elk | only TALA supports shape-relative `near:` |
| `width: 400` on container in dagre/tala | only ELK honors container size |
| `x.# comment in label` | `x: My label \# escaped` |
```
