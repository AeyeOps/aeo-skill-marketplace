# Imports

D2 imports let you split a diagram across multiple `.d2` files for reuse and maintainability.

## Two import forms

### Regular import — assign as a value

```d2
# x.d2
x: { shape: circle }
```

```d2
# y.d2
a: @x.d2          # 'a' becomes a map equal to x.d2's contents
a -> b
```

After import, `a` IS the contents of `x.d2`, so `a` is a map containing a shape `x` with `shape: circle`. Reference it as `a.x`.

### Spread import — splice into surrounding map

```d2
# y.d2
a: {
  ...@x.d2        # x.d2's contents are spliced into 'a'
}
a -> b
```

Now `a` directly contains `x` (no extra wrapping). `a.x` exists with `shape: circle`.

> **Spread imports only work inside maps.** `a: ...@x.d2` (top-level, not inside a map) is invalid.

## File extension behavior

- Only `.d2` files can be imported. `@x.txt` is rejected.
- The autoformatter strips `.d2`: `x: @x.d2` → `x: @x`.
- Filenames with `.` need quotes: `@"schema-v0.1.2"`.

## Partial imports (`@file.path.inside`)

Pull a specific subtree out using dot syntax after the file name:

```d2
# people.d2
management: {
  joe: { shape: person; label: Joe Donutlover }
  jan: { shape: person; label: Jan Donutbaker }
}
employees: {
  toby: { shape: person; label: Toby Simonton }
}
```

```d2
# donut-flowchart.d2
...@people.management
joe -> donuts: loves
jan -> donuts: brings
```

Only `management.joe` and `management.jan` are pulled in (and they become root-level due to spread). `employees.toby` is not present.

## Relative paths

Relative paths resolve against the **importing file's** directory, not the working directory:

```
project/
├── shared/
│   └── classes.d2
└── diagrams/
    └── architecture.d2     # contains: ...@../shared/classes.d2
```

Autoformat removes unnecessary `./`: `@./x` → `@x`.

## Absolute paths

```d2
# Unix / macOS / Linux
x: @/absolute/path/to/file

# Windows (must quote — backslashes and colons)
x: @"C:\absolute\path\to\file"
```

URL imports are NOT supported. D2 only opens local `.d2` files.

## Common patterns

### Model-view: shared model, multiple views

`models.d2`:

```d2
postgres: {
  shape: cylinder
  icon: https://icons.terrastruct.com/dev%2Fpostgresql.svg
  icon.near: bottom-center
}
it: IT Guy {
  shape: person
  style.fill: maroon
}
vpn: {
  style.shadow: true
  tooltip: IP is 192.2.2.1
}
```

`access-view.d2`:

```d2
...@models
it -> vpn -> postgres: ssh
```

`audit-view.d2`:

```d2
...@models
auditor: { shape: person }
auditor -> postgres: read-only
```

### Modular classes: design system

`classes.d2`:

```d2
classes: {
  base:  { style: { border-radius: 4; shadow: true } }
  error: { style.fill: pink; style.stroke: red }
  med:   { width: 200; height: 200; style.font-size: 24 }
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
app.signup -> modal: continue registration
```

### Shared template wrapper

`template.d2`:

```d2
style: {
  fill: "#E3EDE6"
  fill-pattern: dots
  stroke: "#820758"
  stroke-width: 3
  border-radius: 2
  shadow: true
}
label: ""
```

`diagram.d2`:

```d2
template: {
  ...@template
  synergy: {
    our firm -> yours: value add
  }
}
```

### Version comparison

```d2
direction: right
Users 1: Users Table (v0.1) { ...@"users-v0.1" }
Users 2: Users Table (current) { ...@users-current }
Users 1 -> Users 2: schema migration
```

### Nested composition with layers (clickable drilldowns)

`overview.d2`:

```d2
serviceA -> serviceB
serviceB.link: layers.serviceB

layers: {
  serviceB: @serviceB
}
```

Clicking `serviceB` in the rendered output opens the imported `serviceB.d2` as a layer.

## Overrides + null after import

You can override imported shapes — and use `null` to remove them:

```d2
...@models           # brings in postgres, vpn, it
it.style.fill: navy  # override imported attr
vpn: null            # remove an imported shape
```

## Variables and imports

Vars and imports compose. Inner scopes shadow outer; `${var}` substitutions work across imports.

```d2
# theme-vars.d2
vars: {
  brand: {
    primary: "#4baae5"
    danger:  "#FE7070"
  }
}
```

```d2
# main.d2
...@theme-vars

button.style.fill: ${brand.primary}
alert.style.fill: ${brand.danger}
```

## Triple globs propagate; regular globs don't

`*` and `**` apply only within the file where they're declared. `***` carries through imports:

```d2
# style-baseline.d2
***.style.fill: lightblue
(*** -> ***)[*].style.stroke: gray
```

```d2
# main.d2
...@style-baseline   # triple glob is now active
a -> b
# a, b inherit the triple-glob style settings
```

## Cheat sheet

```text
a: @file                # regular import — assign to key
a: { ...@file }         # spread — splice into map
a: { ...@file.path }    # partial — drill in with dotted path

# Quoted file names (with dots)
@"schema-v0.1.2"

# Relative (autoformat strips ./)
@../shared/classes
@./local-file → @local-file

# Absolute
@/absolute/path
@"C:\windows\path"      # quotes required on Windows

# After import, override and delete
...@models
it.style.fill: navy
vpn: null
```
