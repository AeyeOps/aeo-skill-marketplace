# Containers, Classes, and Vars

These are the three structural mechanisms that turn a D2 file from a flat dump into something maintainable.

## 1. Containers (nesting)

Any shape can have children. The shape becomes a "container" automatically when it has at least one child.

### Two ways to nest

```d2
# Dot notation
aws.vpc.subnet.ec2

# Block notation
aws: {
  vpc: {
    subnet: {
      ec2
    }
  }
}

# Mix freely
aws.vpc: {
  subnet1
  subnet2
}
```

Each segment that doesn't already exist is created. Spaces are allowed inside a segment (`my server.vpc` — "my server" is one shape).

### Container labels

Two equivalent forms:

```d2
# Shorthand
gcloud: Google Cloud {
  auth -> db
}

# Reserved label keyword (use when you also need label.near etc.)
gcloud: {
  label: Google Cloud
  label.near: top-center
  auth -> db
}
```

### Cross-container edges

Use the full dotted path on either side of the connection:

```d2
prod.api -> staging.api: replicate
us-east.web.frontend -> us-west.web.frontend: failover
```

### `_` — parent reference

Inside a container, `_` means "the parent scope". Chain to walk up.

```d2
christmas: {
  presents
}
birthdays: {
  presents
  _.christmas.presents -> presents: regift
  _.christmas.style.fill: "#ACE1AF"
}
```

`_._.foo` — grandparent's `foo`. Only valid inside a map.

### `near` for container positioning

Pin a container or text node to a fixed point. Cardinal values work in all engines:

```
top-left      top-center     top-right
center-left                  center-right
bottom-left   bottom-center  bottom-right
```

```d2
title: |md
  # Architecture Overview
| { near: top-center }

legend: {
  near: bottom-right
  ok:  OK    { shape: text; style.font-color: green }
  err: Error { shape: text; style.font-color: red }
}
```

`near: <other-shape-id>` works only with the TALA layout engine.

## 2. Classes (`classes:` block)

Reusable bags of attributes. Define once, apply many.

### Define and apply

```d2
direction: right

classes: {
  load-balancer: {
    label: load\nbalancer
    width: 100
    height: 200
    style: {
      stroke-width: 0
      fill: "#44C7B1"
      shadow: true
      border-radius: 5
    }
  }
  unhealthy: {
    style: {
      fill: "#FE7070"
      stroke: "#F69E03"
    }
  }
}

web traffic -> web lb
web lb.class: load-balancer

web lb -> api1
web lb -> api2
web lb -> api3
api2.class: unhealthy

api1 -> cache lb
api3 -> cache lb
cache lb.class: load-balancer
```

### Multiple classes — array form

```d2
classes: {
  d2: {
    label: ""
    icon: https://play.d2lang.com/assets/icons/d2-logo.svg
  }
  sphere: {
    shape: circle
    style.stroke-width: 0
  }
}

logo.class: [d2; sphere]
```

Items in the array are separated with **semicolons**, not commas.

Order matters — later classes override earlier ones for shared attributes:

```d2
classes: {
  uno: { label: 1 }
  dos: { label: 2 }
}

x.class: [uno; dos]   # x label = "2"
y.class: [dos; uno]   # y label = "1"
```

### Override on individual shapes

When a shape sets the same attribute the class set, the shape wins:

```d2
classes: {
  unhealthy: { style.fill: red }
}
x.class: unhealthy
x.style.fill: orange   # x ends up orange
```

### Apply class to connections

```d2
classes: {
  async: { style.stroke-dash: 5 }
}

# Inline
a -> b: { class: async }

# Or post-hoc by indexing
a -> b
(a -> b)[0].class: async
```

### Classes as CSS-style tags (SVG hooks)

Whatever's in `class:` becomes a CSS class on the rendered SVG, so you can hook external CSS/JS:

```d2
classes: {
  highlight: { style.fill: yellow }
}
node.class: [highlight; needs-attention]
```

In the SVG, `node` will have `class="highlight needs-attention ..."` for downstream styling.

### Modular classes via imports

The standard pattern for "design system" reuse — one classes file imported across many diagrams:

`classes.d2`:

```d2
classes: {
  base:  { style: { border-radius: 4; shadow: true } }
  error: { style.fill: pink; style.stroke: red }
  med:   { width: 200; height: 200; style.font-size: 24 }
  large: { width: 300; height: 300; style.font-size: 28 }
  xlarge:{ width: 400; height: 400; style.font-size: 32 }
  person:{ shape: person; style.stroke-dash: 3 }
}
```

`main.d2`:

```d2
...@classes
user.class: person
error.class: [base; error]
modal.class: [base; med]

user -> app.signup: click
app.signup -> error: invalid fields
```

## 3. Vars (variables)

Define named values, reference them with `${name}`.

### Basic substitution

```d2
direction: right
vars: {
  server-name: Cat
}

server1: ${server-name}-1     # label: "Cat-1"
server2: ${server-name}-2     # label: "Cat-2"
server1 <-> server2
```

### Numbers, booleans

```d2
vars: {
  size: 200
  shadow-on: true
}
node: {
  width:  ${size}
  height: ${size}
  style.shadow: ${shadow-on}
}
```

### Nested vars (dot access)

```d2
vars: {
  brand: {
    primary:   "#4baae5"
    secondary: "#0d47a1"
    accent:    "#f59e0b"
  }
}

button: {
  style: {
    fill:   ${brand.primary}
    stroke: ${brand.secondary}
  }
}

cta: { style.fill: ${brand.accent} }
```

### Scoping (lexical, inner shadows outer)

A substitution looks up the variable in its current scope, then walks outward.

```d2
vars: { region: Global }

lb: ${region} load balancer

zone1: {
  vars: { region: us-east-1 }
  server: ${region} API     # uses inner var → "us-east-1 API"
}
# lb still uses outer var → "Global load balancer"
```

### Single quotes bypass substitution

Single-quoted strings are taken literally — `${...}` is NOT expanded. Double quotes (and unquoted text) DO expand.

```d2
vars: { names: John and Joyce }
a -> b: 'Send field ${names}'    # literal: "Send field ${names}"
a -> b: "Hello ${names}"         # expands: "Hello John and Joyce"
```

### Spread — `...${x}` and `...@file`

If a var (or imported file) is a map or array, `...${x}` splats its contents into the surrounding map.

```d2
vars: {
  shared-style: {
    style.shadow: true
    style.border-radius: 8
    style.fill: "#fff"
  }
}

card1: { ...${shared-style} }
card2: {
  ...${shared-style}
  style.fill: "#fef"   # overrides spread fill
}
```

Spread arrays into arrays:

```d2
vars: {
  base-constraints: [NOT NULL; UNQ]
}
table: {
  shape: sql_table
  id: int { constraint: [PK; ...${base-constraints}] }
}
```

### `vars.d2-config` — diagram-level configuration

A reserved sub-map that drives CLI-equivalent flags:

```d2
vars: {
  d2-config: {
    layout-engine: elk    # dagre | elk | tala
    theme-id: 4           # see references/styling-and-themes.md
    dark-theme-id: 200
    pad: 40
    center: true
    sketch: false
    theme-overrides: {    # remap theme color codes
      B1: "#0d47a1"
      B2: "#1565c0"
      AA2: "#e65100"
    }
  }
}
```

Equivalent to `d2 --layout=elk --theme=4 --dark-theme=200 --pad=40 --center input.d2`. CLI flags and env vars override `d2-config` values.

### `vars.d2-config.data` — third-party metadata

```d2
vars: {
  d2-config: {
    data: {
      generated-by: my-pipeline
      version: 1.2.3
    }
  }
}
```

D2 ignores this; downstream consumers can read it.

## Composition: classes + vars together

The idiomatic "design system" pattern combines all three:

```d2
# theme.d2 — vars + classes
vars: {
  brand: {
    primary: "#4baae5"
    danger:  "#FE7070"
    success: "#44C7B1"
  }
}

classes: {
  service: {
    shape: hexagon
    style.fill: ${brand.primary}
    style.font-color: white
  }
  storage: {
    shape: cylinder
    style.fill: ${brand.success}
  }
  alert: {
    style.fill: ${brand.danger}
    style.bold: true
  }
}
```

```d2
# main.d2
...@theme

api.class: service
db.class: storage
expired-job.class: [service; alert]

api -> db
expired-job -> db
```

This is the cleanest way to keep many diagrams consistent without copy-paste.
