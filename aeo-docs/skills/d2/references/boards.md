# Boards: Layers, Scenarios, Steps

D2 has three keywords for declaring **additional boards** in one diagram. A "board" is one rendered view; only one board is visible at a time. The CLI exports them as multiple SVGs (with click-through navigation), an animated SVG/GIF, or a multi-page PDF/PPTX.

| Keyword | Inheritance from parent? |
|---|---|
| `layers`    | NO — fresh start |
| `scenarios` | YES — full inheritance, declare deltas only |
| `steps`     | YES, **from the previous step** (chained) |

Until you use one of these, your diagram is a single root board.

## Layers — independent boards

Each layer is a fresh board. Use for **different levels of abstraction** or **different views** that don't share content. Common idiom: high-level overview → drill-down into a specific subsystem.

```d2
explain: |md
  This is the top layer — highest level of abstraction.
| { near: top-center }

Tik Tok's User Data: { link: layers.tiktok }

layers: {
  tiktok: {
    explain: |md
      One layer deeper.

      Tik Tok's CEO explained that user data is stored in two places.
    | { near: top-center }

    Virginia data center <-> Hong Kong data center
    Virginia data center.link: layers.virginia
    Hong Kong data center.link: layers.hongkong

    layers: {
      virginia: {
        direction: right
        Oracle Databases: { shape: cylinder; style.multiple: true }
        US residents -> Oracle Databases: access
        US residents: { shape: person }
        Third party auditors -> Oracle Databases: verify
      }
      hongkong: {
        direction: right
        Legacy Databases: { shape: cylinder; style.multiple: true }
      }
    }
  }
}
```

Layers nest arbitrarily deep. Use `link: layers.<name>` on a shape to make it click-navigable.

## Scenarios — same diagram, different state

A scenario inherits ALL shapes/connections from its parent layer. You declare only **deltas** — modifications, additions, or `null` deletions.

Use for: "what does this diagram look like during X?" — failure mode, security incident, hotfix flow, off-peak load.

```d2
direction: right

title: {
  label: Normal deployment
  near: bottom-center
  shape: text
  style.font-size: 40
  style.underline: true
}

local.code -> github.dev: commit
github.dev -> github.master.workflows: merge trigger
github.master.workflows -> aws.builders: upload and run
aws.builders -> aws.s3: upload binaries
aws.ec2 <- aws.s3: pull binaries

# Hidden in default; brought in for hotfix
local.code -> aws.ec2: { style.opacity: 0.0 }

scenarios: {
  hotfix: {
    title.label: Hotfix deployment

    (local.code -> github.dev)[0].style: {
      stroke: "#ca052b"
      opacity: 0.1
    }

    github.dev.style.opacity: 0.1
    github.master.workflows.style.opacity: 0.1
    (github.master.workflows -> aws.builders)[0].style.opacity: 0.1

    (local.code -> aws.ec2)[0]: {
      style.opacity: 1
      style.stroke-dash: 5
      style.stroke: "#167c3c"
    }
  }
}
```

In `hotfix`, all the original shapes/connections still exist (because of inheritance) — the scenario just dims the irrelevant parts and emphasizes the hotfix path.

## Steps — sequential timeline (chained inheritance)

Step N inherits from Step N-1. The first step inherits from its containing layer/scenario. Use for **building up a diagram one piece at a time** — animated walkthroughs, tutorials, "before / during / after" sequences.

```d2
Chicken's plan: {
  style.font-size: 35
  near: top-center
  shape: text
}

steps: {
  1: {
    Approach road
  }
  2: {
    Approach road -> Cross road    # Approach road still exists (from step 1)
  }
  3: {
    Cross road -> Make you wonder why   # both prior nodes still around
  }
}
```

Removing inherited content uses `null`:

```d2
steps: {
  1: { a; b; c; a -> b }
  2: { (a -> b)[0]: null; b -> c }   # remove the a->b edge, add b->c
  3: { b: null }                      # remove b (and any edges to/from it)
}
```

## Choosing between them

| Use | When you want |
|---|---|
| `layers` | Independent boards — different abstractions, different views, drill-downs. |
| `scenarios` | Variants of one diagram — keep base, tweak/highlight differences. |
| `steps` | A timeline — each frame shows the world after one more event. |

You can mix them. A layer can have its own `scenarios:`; a scenario can have `steps:`.

```d2
layers: {
  architecture: {
    a -> b -> c
    scenarios: {
      failure: {
        b.style.fill: red
        steps: {
          detection: { a -> ops: alert }
          recovery:  { b.style.fill: green }
        }
      }
    }
  }
}
```

## Internal links — `link:` between boards

Use the `link` attribute to make a shape click-navigable to another board:

```d2
home: { link: layers.detail }

layers: {
  detail: {
    back: ← home { link: _root_ }   # special id for root board
    a -> b
  }
}
```

Path forms in `link:` values:
- `layers.<name>` — sibling layer
- `scenarios.<name>` — sibling scenario
- `steps.<n>` — sibling step
- `_root_` — root board
- Chained: `layers.parent.layers.child`

`_` in a `link:` value (different meaning from scope `_`) walks up one board:

```d2
The shire: {
  journey: { link: layers.rivendell }
}

layers: {
  rivendell: {
    elves: { elrond -> frodo: gives advice }
    take me home sam.link: _              # back to root (one level up)

    layers: {
      moria: {
        dwarves
        take me home sam.link: _._        # up two boards
      }
    }
  }
}
```

## Quoting board names with dots

```d2
a.link: layers."2012.06"

layers: {
  "2012.06": { hello }
}
```

## Nested composition with imports

A real-world architecture file can split each subsystem into its own file and pull them in as layers:

`overview.d2`:

```d2
serviceA -> serviceB
serviceB.link: layers.serviceB

layers: {
  serviceB: @serviceB.d2
}
```

Clicking `serviceB` in the rendered overview opens the imported `serviceB.d2` as a layer.

## Exporting multi-board diagrams

The CLI's behavior depends on the output format:

| Format | Behavior |
|---|---|
| **Multiple SVGs** (default) | One SVG per board, organized into directories. Internal `layers.x` links rewritten to relative file paths. |
| **Single animated SVG** | Pass `--animate-interval=<ms>` (e.g. 1200) to package all boards into one SVG that auto-cycles. Best for short sequences. |
| **Animated GIF** | Same idea, for contexts where SVG doesn't render. |
| **PDF** | One board per page; click-links target other pages. |
| **PPTX** | One slide per board. Internal links become slide-to-slide links. |

```bash
d2 in.d2 out.svg                          # multi-svg (default)
d2 --animate-interval=1200 in.d2 out.svg  # animated svg
d2 in.d2 out.gif                          # animated gif
d2 in.d2 out.pdf                          # multi-page PDF
d2 in.d2 out.pptx                         # PowerPoint
```

`--bundle=true` (default) bundles all assets into one SVG.

## Rendering a specific board only

```bash
d2 --target='' in.d2 out.svg            # root only, no children
d2 --target='layers.x.*' in.d2 out.svg  # layer x and all its descendants
d2 --target='layers.x' in.d2 out.svg    # just that one board
```

## Cheat sheet

```text
# Layers — independent boards
layers: {
  detail-1: { ... }    # fresh start
  detail-2: { ... }
}

# Scenarios — inherit from parent, declare deltas
scenarios: {
  variant-a: {
    foo.style.fill: red    # tweak existing shape
    new-thing               # add new shape
    bar: null               # delete inherited shape
  }
}

# Steps — chained inheritance
steps: {
  1: { ... }
  2: { ... }   # inherits step 1
  3: { ... }   # inherits step 2
}

# Internal navigation
shape.link: layers.<name>
shape.link: scenarios.<name>
shape.link: steps.<n>
shape.link: _root_         # back to root
shape.link: _              # up one board
shape.link: _._            # up two boards

# CLI — animated multi-board
d2 --animate-interval=1500 in.d2 out.svg
```
