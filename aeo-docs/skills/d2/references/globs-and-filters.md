# Globs and Filters

D2 globs match shapes/connections by name pattern and apply attributes to all matches. Used heavily for "set every X to Y" rules at the top of a file.

## Three glob levels

| Glob | Matches |
|---|---|
| `*`   | shapes/connections in the **current scope** only |
| `**`  | recursive — current scope and all descendants |
| `***` | global — everywhere, including across `layers:` and into `imports` |

```d2
# Current scope
*.style.stroke: black

# Recursive
**.style.font-size: 14

# Global (persists through imports & layers)
***.style.fill: lightblue
```

## Basic glob patterns

```d2
iphone 10
iphone 11 mini
iphone 11 pro
iphone 12 mini

*.height: 300       # apply height: 300 to all shapes
*mini.height: 200   # only those whose name ends with "mini"
*pro.height: 400    # only those whose name ends with "pro"
```

Globs are **case-insensitive**:

```d2
diddy kong
Donkey Kong
*kong.style.fill: brown    # matches both
```

Multiple `*`s in a single pattern:

```d2
teacher
thriller
thrifter
t*h*r.shape: person   # matches all three (literal "t", "h", "r" in order)
```

## Globs apply backwards AND forwards (lazy re-evaluation)

When a new shape is declared after a glob rule, D2 re-evaluates the rule against the new shape:

```d2
a

* -> y       # a -> y is created right now

b            # rule re-evaluates: b -> y added
c            # c -> y added too
```

Move glob rules to the **top** of a file when you want them to be the foundation; put them at the **bottom** when they should only apply to what's already declared.

## Glob connections — `(a -> b)[*]`

Address all connections between matching endpoints. `[*]` = all, `[N]` = the Nth (zero-indexed).

```d2
lady 1
lady 2
barbie

lady 1 -> barbie: hi barbie
lady 2 -> barbie: hi barbie

(lady* -> barbie)[*].style.stroke: pink
```

## Recursive — `**`

```d2
a: {
  b: {
    c
  }
}
**.style.border-radius: 7   # applies to a, a.b, a.b.c
```

In a connection context, `**` only matches non-container leaf shapes:

```d2
zone-A: {
  machine A
  machine B: {
    submachine A
    submachine B
  }
}

zone-A.** -> load balancer
# Connects machine A, submachine A, submachine B
# (NOT machine B, which is a container)
```

## Triple glob — `***` — persists through imports and layers

`**` is local to its scope. `***` is global — stays effective even after imports and inside nested `layers:`.

```d2
# style-baseline.d2
***.style.fill: lightblue
(*** -> ***)[*].style.stroke: red
```

```d2
# main.d2
...@style-baseline    # baseline rules now active
x -> y -> z

layers: {
  detail: {
    a -> b   # a, b also get fill: lightblue (***)
  }
}
```

## Filters — `&keyword: value`

Restrict the glob's match set. Any reserved keyword (or any custom attribute) works as a filter.

```d2
bravo team.shape: person
charlie team.shape: person
command center.shape: cloud
hq.shape: rectangle

*: {
  &shape: person       # only persons match
  style.multiple: true
}
```

### Property filters

`&connected: true` — has at least one connection:

```d2
**: {
  &connected: true
  style.fill: yellow
}
```

`&leaf: true` — non-container shapes only:

```d2
**: {
  &leaf: true
  style.stroke: red
}
```

### Filter with array values

If the attribute is an array, the filter matches when any element matches:

```d2
the-little-cannon: { class: [server; deployed] }
dino:              { class: [internal; deployed] }
catapult:          { class: [server] }

*: {
  &class: server          # matches the-little-cannon and catapult
  style.multiple: true
}
```

### Glob value `*` — "key must exist"

Use `*` as the filter value to mean "this attribute must be present, with any value":

```d2
*: {
  &link: *               # any shape with a link
  style.fill: red
}

x.link: https://example.com    # x matches
y                              # y has no link, doesn't match
```

### AND filters

Multiple `&` lines in the same map are ANDed:

```d2
**: {
  &connected: true
  &leaf: true
  style.stroke: red       # leaf AND connected
}
```

### Inverse filter — `!&`

Match everything that does NOT match:

```d2
*: {
  !&shape: person
  style.multiple: true    # everyone except persons
}
```

### Connection endpoint filters — `&src` / `&dst`

Filter connections by attributes of their endpoints:

```d2
a: { shape: circle; style.fill: blue }
b: { shape: rectangle; style.fill: red }
c: { shape: diamond; style.fill: green }

(* -> *)[*]: {
  &src.style.fill: blue     # connections starting at a blue shape
  style.stroke-dash: 3
}
(* -> *)[*]: {
  &dst.style.fill: green    # connections ending at a green shape
  style.stroke-width: 5
}
(* -> *)[*]: {
  &src: a                   # filter by absolute ID
  &dst: c
  style.stroke: red
}

a -> b
b -> c
a -> c
```

## Scoped globs

A glob applies only to its own scope's children. Use a fully qualified path or `**` to reach further:

```d2
foods: {
  pizzas: {
    cheese
    sausage
    pineapple
    *.shape: circle      # only affects foods.pizzas.*
  }
  humans: {
    john
    james
    *.shape: person      # only affects foods.humans.*
  }
  humans.* -> pizzas.pineapple: eats
}
```

## Last-write-wins ordering

Globs apply in the order they appear. A later rule overrides an earlier one for shared attributes; explicit settings on a shape override any glob:

```d2
a; b; c

*.style.fill: blue
*.style.fill: red       # final glob fill is red
b.style.fill: green     # b stays green (explicit)
```

## Removing things — `null`

Setting an attribute or shape to `null` removes it. Combine with globs to "do X to everything except…":

```d2
**.style.fill: red
b.style.fill: null      # b loses its fill (back to theme default)

# Bulk-delete connections in a layer override
(a -> *)[*]: null       # remove all connections starting at a
```

## Recipe: theme override at top of file

```d2
***.style.fill: "#fafafa"
***.style.stroke: "#444"
(*** -> ***)[*].style.stroke: "#888"
```

## Recipe: focus highlight via scenario

Hide everything except a path:

```d2
a -> b -> c -> d
e
f -> a

scenarios: {
  focus-on-path: {
    **.style.opacity: 0.15
    a.style.opacity: 1
    b.style.opacity: 1
    c.style.opacity: 1
    d.style.opacity: 1
    (a -> b)[0].style.opacity: 1
    (b -> c)[0].style.opacity: 1
    (c -> d)[0].style.opacity: 1
  }
}
```

## Nested globs — combining everything

```d2
conversation 1: {
  shape: sequence_diagram
  alice -> bob: hi
  bob -> alice: hi
}

conversation 2: {
  shape: sequence_diagram
  alice -> bob: hello again
  bob -> alice: hello
}

# Recursively, target every container that is a sequence_diagram,
# then within them, recursively set every actor to be a person.
**: {
  &shape: sequence_diagram
  **: { shape: person }
}
```

## Cheat sheet

```text
*           glob in current scope
**          glob recursively into descendants
***         glob globally (persists across imports/layers)

(* -> *)[*]   glob on connections
(a -> b)[0]   index a specific edge
(a -> b)[*]   all edges between a and b

&key: value     filter — only match when this is set
!&key: value    inverse filter
&key: *         filter — only match when this key is present (any value)
&connected      connected to at least one other shape
&leaf           non-container only
&src.attr       filter on the source endpoint
&dst.attr       filter on the destination endpoint

x: null         delete shape/connection/attribute
```
