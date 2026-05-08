---
name: d2
description: |
  Author D2 diagrams (the Terrastruct text-to-diagram language at https://d2lang.com). Use whenever the user wants to produce, edit, or render any kind of diagram with D2 — architecture, flowchart, sequence, ER/SQL schema, UML class, network topology, mind map, deployment, org chart, state machine, grid layout, mermaid-style flow, or anything similar — even when they don't say "D2" explicitly. Trigger on requests for `.d2` files, mentions of `d2`/`d2lang`, or open-ended diagramming tasks ("draw me a system diagram", "make a flowchart of X", "diagram the request flow", "give me an ER diagram for these tables"). Covers the full DSL — shapes, connections, containers, classes, vars, globs/filters, imports, layers/scenarios/steps, styling, themes, sketch mode, icons, markdown/LaTeX/code blocks, layout engines (dagre/elk/tala), CLI flags, and the specialized diagram shapes (sequence_diagram, sql_table, class, grid, hierarchy, c4-person, image, text/code).
---

# D2 — Authoring Diagrams

D2 is a declarative text-to-diagram language. You write a `.d2` file; the `d2` CLI compiles it to SVG/PNG/PDF/PPTX/GIF. Most files are short — five to fifty lines — and lean on layout engines (dagre/elk/tala) to position things automatically.

This skill is your reference for writing D2 well. The body below is the working overview; the detailed grammar and per-diagram-type references are in `references/`. Hand-edit examples are in `assets/examples/`.

## When to reach for which diagram type

Pick the shape that actually matches the data, not the one that's flashy. D2 has eight specialized diagram modes plus the general-purpose flowchart mode that does everything else.

- **Architecture / system / flow / mind map / org chart / state machine** → general D2 (default rectangle/cloud/cylinder/etc. shapes connected with arrows). This is the bread and butter; ~80% of D2 you write.
- **Time-ordered messages between actors** → `shape: sequence_diagram` (alice → bob → carol with messages).
- **Database schema / entity relationship** → `shape: sql_table` per table + crow's-foot connections (`cf-many` / `cf-one`).
- **UML class** → `shape: class` (fields + methods with visibility prefixes).
- **Anything that needs grid layout** → `grid-rows: N` / `grid-columns: N` on the container.
- **Tree from connections** → `shape: hierarchy`.
- **Image-only node (no rectangle around it)** → `shape: image`.
- **Plain text label / code block / LaTeX** → `shape: text`, `shape: code`, or a `|md ... |` / `|tex ... |` block.

If the user asks for a "Mermaid flowchart" or "Graphviz dot" or "PlantUML sequence diagram", D2 can produce the same diagram — just tell them you'll use D2's equivalent.

## Writing a D2 file: the minimum to know

```d2
# Comments start with '#'
direction: right                # up | down | left | right (default: down)

# Shapes are declared by mentioning them, optionally with a label
api: API Gateway                # `api` is the key, "API Gateway" is the label
db: { shape: cylinder }         # set shape via attributes
worker.shape: queue             # dot syntax also works

# Connections — these IMPLICITLY create the shapes if not already declared
api -> db: writes               # directed edge with label
worker <- queue                 # reverse direction
client <-> server               # bidirectional
metric -- log                   # undirected

# Chained connections
client -> api -> worker -> db

# Containers (nesting)
prod: {
  api -> db
  worker -> db
}
prod.api -> staging.api: replicate     # cross-container reference

# Styling — quote hex colors (unquoted '#' starts a comment!)
api.style.fill: "#4baae5"
api.style.stroke-width: 2
(api -> db)[0].style.stroke: red       # style a specific connection
```

That's enough to draft most diagrams. The rest is refinement.

### Identifiers and labels

- **Spaces are allowed in keys**: `web server.shape: hexagon` — `web server` is one identifier.
- **Dots nest**: `aws.vpc.subnet.ec2` creates a 4-deep hierarchy.
- **Quote when needed**: use double quotes for keys with `.` in them, single quotes to bypass `${var}` substitution and special meanings: `'literal text'`. Backticks are not used.
- **Multiline labels**: use `\n` (`api: my\nmulti-line\nlabel`) or a `|md ... |` block.
- **Labels can be Markdown**: `desc: |md\n  # Title\n  - bullet 1\n  - bullet 2\n|`.
- **Reserved keywords** (cannot be used as plain shape names without being attributes): `label`, `shape`, `icon`, `near`, `top`, `left`, `width`, `height`, `style`, `class`, `classes`, `vars`, `layers`, `scenarios`, `steps`, `direction`, `link`, `tooltip`, `constraint`, `source-arrowhead`, `target-arrowhead`, `grid-rows`, `grid-columns`, `grid-gap`, `vertical-gap`, `horizontal-gap`. To use one literally as a shape name, escape with a leading `\` or quote it.

### The eight `shape:` values that change layout/parsing rules

These have special handling. The rest (rectangle, square, page, parallelogram, document, cylinder, queue, package, step, callout, stored_data, person, diamond, oval, circle, hexagon, cloud, c4-person) only change appearance.

| Shape | What changes |
|---|---|
| `sequence_diagram` | Whole container is laid out as actor lanes + time arrows. See `references/sequence-diagrams.md`. |
| `sql_table` | Children become rows (`column-name: type` with optional `{constraint: primary_key}`). See `references/sql-and-er-diagrams.md`. |
| `class` | Children become UML fields/methods. Visibility via `+ - #` prefix. See `references/class-diagrams.md`. |
| `hierarchy` | Tree layout from connections. Position keywords forbidden. See `references/grid-diagrams.md`. |
| `image` | Borderless icon-only node. Pair with `icon: <url>`. |
| `text` | Plain text node, no surrounding box. |
| `code` | Code block (use `style.font: mono` and `|<lang> ... |` body). |
| `grid-rows: N` / `grid-columns: N` | Children flow into a grid in declaration order. See `references/grid-diagrams.md`. |

## Authoring workflow

1. **Pick the diagram type** (see table above). For ambiguous requests, draw it as a general flowchart — that's what most of D2 is.
2. **Sketch the structure first**: which shapes exist, what connects to what. Don't style yet.
3. **Render it AND look at it.** This is the most important step — see "Render and review" below. Compilation success ≠ a good diagram. D2 will happily emit a syntactically valid SVG that's visually broken.
4. **Iterate based on what you actually see.** Tight feedback loop. If something looks wrong, don't ship it — fix it and re-render.
5. **Set `direction:` if the auto-layout direction is wrong**. Default is top-to-bottom; `direction: right` is the most common override (good for sequence/process flows).
6. **Pick a layout engine if defaults look bad**:
   - `dagre` (default) for plain hierarchical flowcharts.
   - `elk` for SQL/UML/anything with deep nesting and cross-container edges, and for crisp orthogonal routing.
   - `tala` (paid) only when the user explicitly asks or the diagram needs `near: <other-shape>` or per-container `direction:`.
7. **Apply theming in one place** via `vars.d2-config` rather than scattered `style.*` overrides. Use semantic theme color codes (`B1`–`B6`, `AA2/4/5`, `AB4/5`, `N1`–`N7`) so themes still work.
8. **Add icons sparingly** from `https://icons.terrastruct.com` for AWS/GCP/Azure/dev/tech categories — they elevate architecture diagrams.
9. **Use `classes:` if you find yourself repeating styles** more than twice. Don't preemptively define classes.

## Render and review (DO NOT SKIP)

D2 errors loudly when syntax is wrong, but stays silent when the diagram is **visually broken**. The compiler will happily produce a diagram with overlapping text, truncated labels, mis-aligned cards, orphaned containers, illegible contrast, or comic spacing — and report `success`. So you have to look.

**Workflow:**

1. Render to PNG (easiest to view inline): `d2 input.d2 input.png`. PNG renders through headless Chromium so it requires Playwright/Chromium to be installed; SVG is a fallback that works without.
2. **Open the rendered file and actually look at it.** Use the Read tool on the PNG — it returns the image inline. For SVG, render PNG too just for the review step (the production output stays SVG).
3. Run the visual-quality checklist below.
4. If anything is wrong, fix the source and re-render. **Do not declare done until the rendered image meets the bar.** Two or three iterations is normal.

**Visual-quality checklist** — scan the image for each of these and fix what's broken:

- **Truncation.** Any label cut off mid-word? ("Personalizatio…", "Device mg…"). Usually a card-width problem — widen the card via `width:` on the class, or shorten the label.
- **Alignment.** In a row of cards, are they all the same height? D2's auto-sizing makes uneven rows by default. Set explicit `height:` on the class to force uniform.
- **Overflow.** Is text spilling out of its box? `|md` blocks especially can render text outside the box bounds. Use a fixed `width:` and `height:` to constrain, or shrink `font-size`.
- **Empty space / awkward gaps.** A row with 4 items in a 7-wide grid leaves three blank cells. Either re-center, re-grid, or fill with invisible padding (`shape: text` with `style.opacity: 0`).
- **Connection routing.** Are edges crossing through unrelated shapes? Try `--layout=elk` (orthogonal) instead of dagre. For complex architecture, ELK is almost always better. If edges still cut diagonally across content under ELK, the cause is usually a `grid-rows:` / `grid-columns:` container — see pitfall 15 and `references/edge-routing.md`.
- **Text readability.** At the diagram's natural scale, can you read every label? `font-size: 8` is the floor; below that, increase the box size or split content.
- **Border visibility.** Is the stroke visible against the fill? `stroke-width: 1` on a light-on-light combo disappears; bump to 2–4.
- **Color contrast.** Is white text on a light theme color invisible? Theme color codes (`B1` darkest → `B6` lightest) are designed to pair text/fill correctly.
- **Visual hierarchy.** Does the most important thing draw the eye first? If everything is equally bold/colored, nothing stands out.

**If you're tempted to skip the render step because "the syntax is correct": don't.** That's the failure mode this section exists to prevent. The user will be looking at the image, not at the source.

## A clean default `vars.d2-config` block

When you produce a polished diagram, put this near the top — it sets sensible defaults and makes the output theme-aware:

```d2
vars: {
  d2-config: {
    layout-engine: elk      # crisp orthogonal routing, good for most cases
    theme-id: 0             # Neutral default; see references/styling-and-themes.md for the full list
    pad: 40                 # tighter than the 100px default
    sketch: false           # set true for hand-drawn whiteboard look
  }
}
```

CLI flags (`--theme=N`, `--sketch`, `--layout=elk`) override these. Don't set `sketch: true` by default — the user usually wants the polished version.

## Rendering D2 to a file

If `d2` is available on the user's machine (or in this sandbox), render directly:

```bash
d2 input.d2 output.svg                      # SVG (default, best)
d2 input.d2 output.png                      # PNG (raster; needs Playwright/Chromium)
d2 input.d2 output.pdf                      # PDF (multi-board → multi-page)
d2 --layout=elk --theme=101 input.d2        # output defaults to input.svg
d2 --animate-interval=1500 in.d2 out.svg    # animate through layers/scenarios/steps
d2 --watch in.d2                            # live-reload server; opens a browser
d2 fmt in.d2                                # autoformat in place
d2 validate in.d2                           # parse-only check
```

If `d2` is **not** installed, do NOT `pip install`/`brew install` it without the user's blessing. Either:
- Just save the `.d2` file and tell them to render it (or paste at https://play.d2lang.com).
- Or offer to install with `brew install d2` (mac) / `curl -fsSL https://d2lang.com/install.sh | sh -s --` (linux/mac) / Windows MSI.

When you do produce a rendered file, prefer **SVG** unless the user explicitly needs PNG/PDF/PPTX. SVG keeps tooltips, links, animations, and infinite zoom; PNG strips all of that and needs a headless Chromium.

## Common pitfalls (these will bite you)

The full list is in `references/full-grammar-cheatsheet.md`. The top hits:

1. **Unquoted `#` is a comment.** `style.fill: #4baae5` is broken. Use `style.fill: "#4baae5"`.
2. **`->` not `-->`** for connections (no Mermaid-style double-dash).
3. **There's no `alt`/`opt`/`loop`/`par` keyword** in sequence diagrams — those are just nested groups whose key happens to be named `alt` etc. See `references/sequence-diagrams.md`.
4. **Class diagrams' `#` (protected) visibility collides with comments** — escape as `\#` or use the `# ` prefix without alphanumerics on the next char.
5. **`fill` is not allowed on connections.** Use `stroke` for connection color.
6. **`shape: hierarchy` forbids `top:`/`left:` keywords** — it'll error.
7. **Inside a `sequence_diagram`, all actors must be predeclared at the top of the container** if you want to reference them in nested groups.
8. **Single quotes prevent `${var}` substitution. Double quotes / unquoted text expand it.** Surprising if you're escaping for shell reasons.
9. **`(a -> b)[0]` indexes the first edge between a and b.** Multiple `a -> b` lines create distinct edges, not overrides — use the index syntax to restyle one of them.
10. **`near: <shape-id>` is TALA-only.** Cardinal `near: top-center` works in any engine.
11. **`|md` blocks ignore card box styling in practice.** Even though `|md` is documented as defaulting to a rectangle, applying `style.fill` / `style.stroke` / `style.border-radius` / `style.shadow` via a class on a `|md` shape often does nothing visible — the box is invisible behind the markdown rendering. **For boxed content with bullets, use `shape: rectangle` with a `\n`-separated label** (e.g. `iam: "Identity & Access\n\n• Authentication\n• SSO\n• User management" { class: card }`). Save `|md` for situations where you actually want rendered Markdown text without a surrounding box.
12. **Grid rows of unequal-content children render at unequal heights.** A row of cards where one has 5 lines of text and another has 2 will produce different-height boxes. Set explicit `height:` on the class so every card in the row is the same size.
13. **Multiple top-level grids lay out horizontally as siblings.** If you want stacked rows, wrap them in a parent container with `grid-columns: 1` (or `grid-rows: N`). Otherwise dagre/elk treats each grid as a peer and lines them up sideways.
14. **Hide intermediate-container labels with `label: ""`** when you're using nested grids structurally. Otherwise the row containers' names ("domains", "concerns") show up as visible labels in the rendered diagram.
15. **`grid-rows:` / `grid-columns:` on a connected container breaks ELK's orthogonal routing.** When grid children connect to shapes outside the grid, ELK silently falls back to diagonal/polyline routes for those cross-grid edges, producing the spaghetti-line look the engine is supposed to prevent. Drop the grid (let ELK arrange siblings itself) or connect to the parent container instead of individual children. See `references/edge-routing.md`.
16. **Per-edge `style.border-radius` is the curve lever, and it scales past the documented max.** Docs say 0–20, but values up to ~100 work and progressively soften corners. `border-radius: 20` is the architectural-soft sweet spot; `border-radius: 50–100` reads as a Bezier curve while keeping ELK's clean orthogonal routing. Per-edge AND per-class. See `references/edge-routing.md` for the full picture, including why true Bezier curves require switching engines.

## Reference files (load on demand)

The body above is enough for ~70% of cases. For the rest, read the relevant reference file:

- `references/edge-routing.md` — connection styling, curves vs. orthogonal, corner softening, multi-bend workarounds, the grid-vs-ELK pitfall in depth.
- `references/shapes-and-connections.md` — every shape value, every connection operator, arrowheads, labels, the full styling menu.
- `references/layouts.md` — engine selection (dagre/elk/tala), `direction:`, `near:`, `top:`/`left:`, `width:`/`height:` per engine.
- `references/styling-and-themes.md` — theme IDs, palette codes (`B1`–`B6`, `AA2`/`AA4`/`AA5`, `AB4`/`AB5`, `N1`–`N7`), sketch mode, custom theme overrides.
- `references/containers-classes-vars.md` — nesting, `classes:`, `vars:` substitution, inheritance.
- `references/grid-diagrams.md` — `grid-rows:` / `grid-columns:`, gap controls, layout caveats.
- `references/sequence-diagrams.md` — actor lanes, time arrows, nested groups (`alt`/`opt`/`loop`/`par`).
- `references/sql-and-er-diagrams.md` — `shape: sql_table`, crow's-foot cardinalities, ELK's exact-column routing.
- `references/class-diagrams.md` — `shape: class`, visibility prefixes, fields/methods.
- `references/markdown-and-text.md` — `|md` / `|tex` / `|<lang>` blocks, multi-line labels, the `|md` styling caveat.
- `references/icons-and-images.md` — `icon:`, `shape: image`, the icons.terrastruct.com catalog.
- `references/boards.md` — `layers:` / `scenarios:` / `steps:` for multi-board diagrams (multi-page PDFs, multi-slide PPTX, animated SVG).
- `references/globs-and-filters.md` — `*` wildcard, `&` filters, `**` deep glob.
- `references/imports.md` — `@import` and `...@import`, partial vs. spread imports.
- `references/cli-and-tooling.md` — every `d2` CLI flag, env vars, watch mode, `d2 fmt` and `d2 validate`.
- `references/full-grammar-cheatsheet.md` — the long-tail grammar quirks not covered above.