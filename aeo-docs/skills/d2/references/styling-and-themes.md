# Styling and Themes

## The `style` block

Two equivalent forms — use whichever reads cleaner in context:

```d2
# Block form
api: {
  style: {
    fill: "#4baae5"
    stroke: "#1565c0"
    stroke-width: 3
    bold: true
  }
}

# Dot form
api.style.fill: "#4baae5"
api.style.stroke: "#1565c0"
api.style.stroke-width: 3
api.style.bold: true
```

> Always quote hex colors. Unquoted `#` starts a comment.

## All `style.*` properties

### Layout / appearance

| Property | Valid values | Applies to | Notes |
|---|---|---|---|
| `opacity` | float `0`–`1` | shapes, connections | |
| `stroke` | CSS color name, `"#hex"`, `"linear-gradient(c1, c2)"`, theme code | shapes, connections, root | On `sql_table`/`class`, this is the body color (not the border). |
| `stroke-width` | int `1`–`15` | shapes, connections, root | |
| `stroke-dash` | int `0`–`10` | shapes, connections, root | `0` = solid; higher = longer dashes. |
| `fill` | CSS color, hex, gradient, theme code, `transparent` | shapes (NOT connections), root | On `sql_table`/`class`, this is the header color. |
| `fill-pattern` | `dots`, `lines`, `grain`, `paper`, `none` | shapes (containers shine), root | |
| `border-radius` | int `0`–`20` | shapes, connections (ELK only) | `>15` ≈ pill. |
| `shadow` | bool | shapes only | |
| `3d` | bool | rectangle/square only | Adds isometric depth. |
| `multiple` | bool | shapes only | Stacked-paper look. |
| `double-border` | bool | rectangle/oval; root | |

### Text

| Property | Valid values | Notes |
|---|---|---|
| `font` | `mono` | Currently only `mono`. Falls back to Source Code Pro. |
| `font-size` | int `8`–`100` | |
| `font-color` | CSS color, hex, gradient, theme code | On tables/classes, header text only. |
| `bold` | bool | Default `true` on shape labels. Set `false` to see italic clearly. |
| `italic` | bool | |
| `underline` | bool | |
| `text-transform` | `uppercase`, `lowercase`, `title`, `capitalize`, `none` | Use `none` to defeat a theme's caps-lock (Terminal). |

### Connections / animations

| Property | Valid values | Applies to |
|---|---|---|
| `animated` | bool | shapes, connections |
| `filled` | bool | arrowhead shapes only |

`animated` on a connection draws a marching-ants stroke (SVG only — drops in PNG/PDF).

`filled` controls solid vs. outline for arrowhead shapes:
- `triangle`: filled by default; `style.filled: false` = outline.
- `diamond`, `circle`, `box`: outlined by default; `style.filled: true` = filled.

### Root-level styles

```d2
# Diagram background and frame
style.fill: "#0a0e1a"
style.fill-pattern: dots
style.stroke: "#1e402d"
style.stroke-width: 3
style.stroke-dash: 2
style.double-border: true
```

If you set a frame stroke at root, also set CLI `--pad` to give breathing room.

## Color formats

```d2
# 1. CSS named colors (case-insensitive)
x.style.fill: deepskyblue
x.style.fill: hotpink
x.style.fill: papayawhip

# 2. Hex (always quoted)
x.style.fill: "#4baae5"
x.style.fill: "#4baae580"     # 8-digit hex with alpha (~50%)

# 3. Linear gradient (the only gradient supported)
x.style.fill: "linear-gradient(#f69d3c, #3f87a6)"

# 4. Transparent
x.style.fill: transparent

# 5. Theme color codes (recommended for portability)
x.style.fill: B5
x.style.stroke: B2
x.style.font-color: B1
```

## Theme color codes

D2 themes define a semantic palette. Using codes (not raw hex) keeps your diagram theme-portable.

```
N1..N7   Neutrals/text:
         N1 = darkest text, N4 = borders/dividers, N7 = page background

B1..B6   Primary brand ramp (typically blues):
         B1 = darkest (text on B-fills), B6 = lightest fill

AA2, AA4, AA5    First accent ramp
AB4, AB5         Second accent ramp
```

Use the codes anywhere a color is accepted:

```d2
node.style.fill: B5
node.style.stroke: B2
node.style.font-color: B1

callout.style.fill: AA5
callout.style.stroke: AA2

warning.style.fill: AB5
warning.style.stroke: AB4
```

## Theme catalog (full list)

### Light themes

| ID | Name | Notes |
|---|---|---|
| `0` | Neutral default | The unconfigured default |
| `1` | Neutral Grey | Pure grayscale |
| `3` | Flagship Terrastruct | Brand blues + violets |
| `4` | Cool Classics | Cyan + lavender |
| `5` | Mixed Berry Blue | Blue + purple + pink |
| `6` | Grape Soda | Violet primary, blue accent |
| `7` | Aubergine | Deeper purple, teal accent |
| `8` | Colorblind Clear | Colorblind-safe blues, greens, ochres |
| `100` | Vanilla Nitro Cola | Warm tans + cobalt accent |
| `101` | Orange Creamsicle | Orange + green + yellow |
| `102` | Shirley Temple | Pink + coral + butter |
| `103` | Earth Tones | Browns + ochre |
| `104` | Everglade Green | Forest greens + tan |
| `105` | Buttered Toast | Yellow/tan |

### Special light themes (impose extra rules)

| ID | Name | Special |
|---|---|---|
| `300` | Terminal | Mono font, NO corner radius, double-border outermost container, dotted containers, ALL CAPS labels |
| `301` | Terminal Grayscale | Same as Terminal but no color |
| `302` | Origami | Paper texture everywhere, no rounded corners, double-border outermost container |
| `303` | C4 | C4-model styling (Person stroke convention, root-level grey, etc.) |

### Dark themes

| ID | Name |
|---|---|
| `200` | Dark Mauve |
| `201` | Dark Flagship Terrastruct |

### Setting a theme — three ways

```bash
# 1. CLI
d2 --theme=101 input.d2 output.svg
d2 -t 101 input.d2 output.svg

# 2. Env var
D2_THEME=101 d2 input.d2 output.svg

# 3. Inline
```

```d2
vars: {
  d2-config: {
    theme-id: 101
    dark-theme-id: 200
    layout-engine: elk
  }
}
```

CLI > env > inline `d2-config`.

### Dark theme

`--dark-theme` (or `D2_DARK_THEME`) embeds a `prefers-color-scheme: dark` variant in the SVG, so the same file flips colors based on the viewer's theme:

```bash
d2 --theme 0 --dark-theme 200 input.d2
```

### Special-theme opt-outs

Special themes (Terminal, Origami) impose defaults. Opt out per-shape:

```d2
# Cancel Terminal's caps lock on a single shape
shouty.style.text-transform: none
shouty.label: "lowercase exception"

# Cancel Origami's paper texture on a child
plain.style.fill-pattern: none
```

## Theme overrides — remap palette codes

Redefine palette codes inline so existing `B2`/`AA4`/etc. references take new colors:

```d2
vars: {
  d2-config: {
    theme-overrides: {
      B1: "#0d47a1"
      B2: "#1565c0"
      B3: "#1976d2"
      B4: "#2196f3"
      B5: "#90caf9"
      B6: "#e3f2fd"
      AA2: "#e65100"
      AA4: "#ff9800"
      AA5: "#ffe0b2"
    }
    dark-theme-overrides: { B5: "#0d47a1" }   # different overrides for dark
  }
}
```

## Sketch mode (hand-drawn look)

Wobbly hand-drawn rendering, blends Architect's Daughter + Fuzzy Bubbles fonts. Combines with any theme.

```bash
d2 --sketch input.d2 output.svg
D2_SKETCH=true d2 input.d2 output.svg
```

```d2
vars: {
  d2-config: { sketch: true }
}
```

Don't enable sketch by default — most users want polished. Reserve for whiteboard / casual contexts.

## Fonts

D2 ships:
- **Source Sans Pro** — default labels and Markdown
- **Source Code Pro** — code blocks and `style.font: mono`
- **Architect's Daughter + Fuzzy Bubbles** — sketch mode

Override via CLI flags:

```bash
d2 \
  --font-regular=./Helvetica-Regular.ttf \
  --font-italic=./Helvetica-Italic.ttf \
  --font-bold=./Helvetica-Bold.ttf \
  --font-semibold=./Helvetica-SemiBold.ttf \
  input.d2 output.svg
```

Mono variants: `--font-mono`, `--font-mono-bold`, `--font-mono-italic`, `--font-mono-semibold`.

Files MUST be `.ttf` (not `.otf` or `.woff`). Missing variants fall back to Source Sans Pro.

## Annotated full-style example

```d2
vars: {
  d2-config: {
    theme-id: 0
    layout-engine: elk
    pad: 40
    sketch: false
  }
}

# Diagram-level frame
style.fill-pattern: none

title: System Architecture {
  shape: text
  near: top-center
  style.font-size: 32
  style.bold: true
  style.font-color: B1
}

# Database with all the trimmings
db: Primary DB {
  shape: cylinder
  style: {
    fill: B5
    stroke: B2
    shadow: true
    multiple: true
    font-color: B1
    border-radius: 6
  }
}

# Container with patterned background
api: |md
  # API Layer
  - REST + GraphQL
  - Rate-limited
| {
  shape: rectangle
  style: {
    fill-pattern: lines
    stroke-dash: 3
    border-radius: 8
    font: mono
  }
}

worker: Background Worker {
  icon: https://icons.terrastruct.com/essentials%2F005-programmer.svg
  icon.near: outside-top-right
  label.near: bottom-center
}

# Styled connection with cardinality arrowheads
worker -> db: writes {
  style: {
    stroke: AA2
    stroke-width: 3
    stroke-dash: 5
    animated: true
    font-color: AA2
    italic: true
  }
  target-arrowhead: 1..N {
    shape: cf-many-required
  }
}

api -> worker: enqueue {
  source-arrowhead: { shape: diamond; style.filled: true }
  target-arrowhead: { shape: arrow }
}
```

## Cheat sheet

```text
opacity         0.0 .. 1.0
stroke          color | gradient | theme-code (B1..B6, AA2/4/5, AB4/5, N1..N7)
fill            color | gradient | theme-code | transparent  (NOT on connections)
fill-pattern    dots | lines | grain | paper | none
stroke-width    1 .. 15
stroke-dash     0 .. 10  (0 = solid)
border-radius   0 .. 20
shadow          true|false       (shapes only)
3d              true|false       (rectangle/square only)
multiple        true|false       (shapes only)
double-border   true|false       (rectangle/oval; root)
font            mono             (only legal value)
font-size       8 .. 100
font-color      color
bold            true|false       (default true on shapes)
italic          true|false
underline       true|false
text-transform  uppercase | lowercase | title | capitalize | none
animated        true|false       (marching ants on connection stroke; SVG only)
filled          true|false       (arrowhead shapes)

# Themes (CLI: --theme=N, --dark-theme=N; inline: vars.d2-config.theme-id):
# Light:  0 1 3 4 5 6 7 8 100 101 102 103 104 105
# Special light: 300 (Terminal) 301 (Terminal grayscale) 302 (Origami) 303 (C4)
# Dark:   200 201
```
