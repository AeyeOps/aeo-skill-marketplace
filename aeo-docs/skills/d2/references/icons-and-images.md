# Icons and Images

## The `icon:` field

Any shape can have an icon. Set `icon:` to a URL or a local path:

```d2
deploy: {
  icon: https://icons.terrastruct.com/aws%2FDeveloper%20Tools%2FAWS-CodeDeploy.svg
}

backup: {
  icon: ./images/backup.png   # local path (relative to the .d2 file)
}
```

Icons can also be set on **connections** — they appear at the midpoint of the line:

```d2
deploy -> backup: {
  icon: https://icons.terrastruct.com/infra%2F002-backup.svg
}
```

## The official icon catalog

D2 hosts a free icon library at **`https://icons.terrastruct.com`**. Categories include:

| Category | URL prefix |
|---|---|
| AWS | `aws/...` |
| Azure | `azure/...` |
| GCP | `gcp/...` |
| Generic tech (servers, routers, switches) | `tech/...` |
| Developer tools (GitHub, GitLab, Docker) | `dev/...` |
| Infrastructure | `infra/...` |
| Generic essentials (programmer, profits, etc.) | `essentials/...` |

URLs are **percent-encoded** — slashes inside category paths become `%2F`, spaces become `%20`. Browse at `https://icons.terrastruct.com` to find specific icons; clicking copies the URL.

```d2
# Common patterns
ec2: { icon: https://icons.terrastruct.com/aws%2FCompute%2F_Instance%2FAmazon-EC2_C4-Instance_light-bg.svg }
github: { icon: https://icons.terrastruct.com/dev/github.svg }
server: { icon: https://icons.terrastruct.com/tech/022-server.svg }
postgres: { icon: https://icons.terrastruct.com/dev%2Fpostgresql.svg }
```

You can also use any other public SVG/PNG URL.

## Icon + label combinations

When a shape has both `icon:` and a label, D2 places the icon automatically — corner-ish for containers, center for leaves. Override placement with `icon.near`:

```d2
worker: Background Worker {
  icon: https://icons.terrastruct.com/essentials%2F005-programmer.svg
  icon.near: outside-top-right
  label.near: bottom-center
}
```

`icon.near` accepts the same set as `label.near`:

```
top-left, top-center, top-right
center-left, center-right
bottom-left, bottom-center, bottom-right

outside-top-left, outside-top-center, outside-top-right
outside-left-center, outside-right-center
outside-bottom-left, outside-bottom-center, outside-bottom-right

border-top-left, border-top-center, border-top-right
border-left-center, border-right-center
border-bottom-left, border-bottom-center, border-bottom-right
```

## `shape: image` — borderless image-only nodes

When you want the icon to BE the shape (no surrounding rectangle), use `shape: image`:

```d2
direction: right

server: {
  shape: image
  icon: https://icons.terrastruct.com/tech/022-server.svg
}
github: {
  shape: image
  icon: https://icons.terrastruct.com/dev/github.svg
}
server -> github
```

## Sizing icons

Icons inherit `width:` / `height:` from their shape:

```d2
big-icon: {
  shape: image
  icon: https://icons.terrastruct.com/tech/022-server.svg
  width: 256
  height: 256
}
```

For non-`image` shapes, the icon scales proportionally to the shape's size.

## Local files

The CLI resolves relative paths against the input `.d2` file's directory:

```
project/
├── architecture.d2
└── images/
    └── my-cat.png
```

```d2
# in architecture.d2
my_cat: {
  icon: ./images/my-cat.png
}
```

This works for SVG, PNG, JPG. The image gets embedded into the output SVG at render time.

## A complete iconography example

```d2
direction: right
vars: { d2-config: { layout-engine: elk } }

# Persona
user: User {
  shape: person
  icon: https://icons.terrastruct.com/essentials%2F004-user.svg
}

# Edge — CDN
cdn: CloudFront {
  shape: image
  icon: https://icons.terrastruct.com/aws%2FNetworking%20%26%20Content%20Delivery%2FAmazon-CloudFront.svg
}

# Compute
api: API {
  icon: https://icons.terrastruct.com/aws%2FCompute%2F_Instance%2FAmazon-EC2_C4-Instance_light-bg.svg
  icon.near: outside-top-right
}

# Storage
db: Postgres {
  shape: cylinder
  icon: https://icons.terrastruct.com/dev%2Fpostgresql.svg
  icon.near: bottom-center
}

# CI/CD
gh: GitHub {
  shape: image
  icon: https://icons.terrastruct.com/dev/github.svg
}

user -> cdn -> api -> db: writes
gh -> api: deploy
```

## Tips

- **Don't overdo it.** A whole diagram of brand icons gets noisy. Use icons to mark *type* (compute / storage / queue / external service / human), not to decorate every node.
- **Container-level icons** sit at the corner; leaf icons sit center. Use `icon.near: outside-top-right` to standardize positions across an architecture diagram.
- **`shape: image` strips the border** — good for product/brand logos. For technical diagrams, regular shapes with `icon:` are usually clearer.
- **Cache concerns**: in `--watch` mode, set `--img-cache=false` if remote images change between renders; otherwise D2 caches them.

## Cheat sheet

```text
shape.icon: <url-or-path>            # icon on any shape (including connections)
shape.icon.near: <position>          # explicit positioning

shape: image                         # borderless image-only node
shape.icon: <url>
shape.width: 200; shape.height: 200  # size the image

# Icon catalog: https://icons.terrastruct.com
# Categories: aws, azure, gcp, tech, dev, infra, essentials
# URLs use %2F for / and %20 for space
```
