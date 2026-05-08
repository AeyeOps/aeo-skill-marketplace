# CLI and Tooling

## Synopsis

```
d2 [flags] file.d2 [file.svg | file.png | file.pdf | file.pptx | file.gif | file.txt]
d2 layout [name]
d2 fmt file.d2 ...
d2 play [--theme=0] [--sketch] file.d2
d2 validate file.d2
d2 themes
d2 version
```

If only one positional arg is given, output defaults to the input name with `.svg`. Use `-` for either argument to read from stdin / write to stdout.

## Common invocations

```bash
d2 input.d2 output.svg                                   # SVG (default, best)
d2 input.d2                                              # implicit input.svg
d2 input.d2 output.png                                   # PNG (needs Playwright)
d2 input.d2 output.pdf                                   # PDF
d2 input.d2 output.pptx                                  # PowerPoint
d2 input.d2 output.gif                                   # animated GIF (needs --animate-interval)
echo "x -> y" | d2 - - > example.svg                    # stdin → stdout
d2 input.d2 --stdout-format png - > out.png             # non-default stdout format
d2 --layout=elk --theme=101 --sketch input.d2 out.svg    # combine flags
d2 --watch input.d2                                      # live-reload server
d2 fmt input.d2                                          # autoformat in place
d2 fmt --check *.d2                                      # CI lint mode (exits non-zero if unformatted)
d2 validate input.d2                                     # parse-only check
```

## All flags

| Flag (long) | Short | Env | Default | Description |
|---|---|---|---|---|
| `--watch` | `-w` | `D2_WATCH` | `false` | Live-reload server. Use `--host`/`--port` to control bind. |
| `--host` | `-h` | `HOST` | `localhost` | Host for `--watch` |
| `--port` | `-p` | `PORT` | `0` | Port for `--watch` (`0` = random) |
| `--bundle` | `-b` | `D2_BUNDLE` | `true` | Bundle assets and layers into output SVG |
| `--force-appendix` | | `D2_FORCE_APPENDIX` | `false` | Add tooltip/link appendix to SVG (auto-on for PNG) |
| `--debug` | `-d` | `DEBUG` | `false` | Verbose logs |
| `--img-cache` | | `IMG_CACHE` | `true` | Cache remote icons in watch mode |
| `--layout` | `-l` | `D2_LAYOUT` | `dagre` | `dagre` \| `elk` \| `tala` |
| `--theme` | `-t` | `D2_THEME` | `0` | Theme ID (see references/styling-and-themes.md) |
| `--dark-theme` | | `D2_DARK_THEME` | `-1` | Dark theme ID (SVG only) |
| `--pad` | | `D2_PAD` | `100` | Padding pixels |
| `--animate-interval` | | `D2_ANIMATE_INTERVAL` | `0` | ms between board frames (SVG/GIF only) |
| `--timeout` | | `D2_TIMEOUT` | `120` | Render timeout, seconds |
| `--version` | `-v` | | | Print version |
| `--sketch` | `-s` | `D2_SKETCH` | `false` | Hand-drawn rendering |
| `--stdout-format` | | | | `svg`\|`png`\|`ascii`\|`txt`\|`pdf`\|`pptx`\|`gif` for stdout |
| `--browser` | | `BROWSER` | | Browser for `--watch`. Set to `0` to suppress |
| `--center` | `-c` | `D2_CENTER` | `false` | Center SVG in viewbox |
| `--scale` | | `SCALE` | `-1` | `0.5` halves; `-1` = fit |
| `--target` | | | `*` | Board to render (`*` = all, `''` = root only, `layers.x.*` = subtree) |
| `--font-regular` | | `D2_FONT_REGULAR` | | Path to regular `.ttf` |
| `--font-italic` | | `D2_FONT_ITALIC` | | Path to italic `.ttf` |
| `--font-bold` | | `D2_FONT_BOLD` | | Path to bold `.ttf` |
| `--font-semibold` | | `D2_FONT_SEMIBOLD` | | Path to semibold `.ttf` |
| `--font-mono` | | `D2_FONT_MONO` | | Path to mono `.ttf` |
| `--font-mono-bold` | | `D2_FONT_MONO_BOLD` | | Path to mono-bold `.ttf` |
| `--font-mono-italic` | | `D2_FONT_MONO_ITALIC` | | Path to mono-italic `.ttf` |
| `--font-mono-semibold` | | `D2_FONT_MONO_SEMIBOLD` | | Path to mono-semibold `.ttf` |
| `--check` | | `D2_CHECK` | `false` | With `fmt`: report unformatted (exit 1) instead of rewriting |
| `--no-xml-tag` | | `D2_NO_XML_TAG` | `false` | Strip `<?xml ...?>` from SVG (HTML embedding) |
| `--salt` | | | | Suffix for SVG element IDs (avoid clashes when embedding multiple) |
| `--omit-version` | | `OMIT_VERSION` | `false` | Don't embed D2 version footer |
| `--ascii-mode` | | `D2_ASCII_MODE` | `extended` | `extended` (Unicode box-drawing) or `standard` (pure ASCII) for `.txt` output |

CLI flags > env vars > inline `vars.d2-config` settings.

## Subcommands

### `d2 fmt file.d2 [file.d2 ...]`

Auto-format `.d2` files in place. With `--check`, exits with status 1 and prints unformatted file paths instead of writing.

```bash
d2 fmt diagram.d2          # rewrites in place
d2 fmt --check *.d2        # CI lint mode
```

If `inputPath` is a directory, looks for `index.d2` inside.

### `d2 layout [name]`

```bash
d2 layout            # list available engines
d2 layout dagre      # show dagre's specific options
d2 layout elk        # show ELK's specific options
d2 layout tala       # only available if TALA binary is on $PATH
```

### `d2 themes`

Lists every theme by ID and name, grouped under "Light:" and "Dark:".

### `d2 validate file.d2`

Parses the file and reports errors. Accepts `-` for stdin.

### `d2 play [--theme=0] [--sketch] file.d2`

URL-encodes the script and opens `https://play.d2lang.com/?script=<encoded>&...` in the browser. Honors `--theme` and `--sketch` for the URL state.

### `d2 version`

Prints the version string. Equivalent to `-v` / `--version`.

## Output formats

### SVG (default)

Best for web embedding, interactivity (tooltips, links, animations).

- Always SVG when `outputPath == "-"` unless `--stdout-format` says otherwise.
- D2 SVGs use HTML `<foreignObject>` for Markdown labels, so they're meant for **web** viewing (browsers). May not render correctly in Inkscape or Adobe Illustrator.
- `--no-xml-tag` strips the XML processing instruction for direct HTML embedding.
- Multi-board → multiple SVGs in directories (with rewritten internal links). Use `--animate-interval` for a single animated SVG instead.

### PNG

- Best for emails, READMEs, slack pastes.
- Implementation: D2 spins up Playwright + headless Chromium, screenshots the SVG.
- First invocation triggers a one-time Playwright dependency install.
- Loses interactivity — D2 appends a textual appendix listing tooltips/links.
- Larger file size, not vector.

If you see `failed to launch Chromium`, install the headless browser:

```bash
npm install -g @playwright
npx playwright install --with-deps chromium
# or
d2 init-playwright
```

### PDF

Best for printable docs, paginated multi-board diagrams. Each board → one page. Internal `link`s remain clickable. Inherits PNG's Playwright dependency.

### PPTX

One board → one slide. Internal links become slide-to-slide links; external links become hyperlinks. Works in PowerPoint, Google Slides, Keynote.

`.ppt` is rejected — use `.pptx`.

### GIF

For contexts that don't support SVG. Renders every board to PNG, assembles via `xgif`. `--animate-interval` controls per-frame ms (defaults to `1000` for GIF when unspecified).

### ASCII (`.txt`)

Two modes:
- `--ascii-mode extended` (default): Unicode box-drawing chars (`┌`, `─`, `│`, `▶`)
- `--ascii-mode standard`: pure ASCII (`+`, `-`, `|`, `>`)

Forces ELK layout. Many styles are no-ops (shadow, multiple, animated).

## Multi-board diagrams to stdout

Multi-board diagrams **cannot be written to stdout** — D2 returns `multiboard output cannot be written to stdout`. Write to a file instead.

## Installation

### Install script (recommended)

```bash
curl -fsSL https://d2lang.com/install.sh | sh -s -- --dry-run    # inspect first
curl -fsSL https://d2lang.com/install.sh | sh -s --              # install
curl -fsSL https://d2lang.com/install.sh | sh -s -- --uninstall  # uninstall
curl -fsSL https://d2lang.com/install.sh | sh -s -- --tala       # also install TALA
```

### macOS — Homebrew

```bash
brew install d2
brew install d2 --HEAD   # latest from source
```

### Linux

- Void Linux: `xbps-install d2`
- Other distros: install script or standalone tarball.

### Go install (from source)

```bash
go install oss.terrastruct.com/d2@latest    # requires Go ≥ 1.20
```

Caveat: this won't include manpages.

### Windows

- `.msi` installers from GitHub releases — adds `d2` to `$PATH`.
- Tarballs work in MSYS2/Git Bash.
- WSL works like any Linux install.
- Community: `scoop install main/d2` or `choco install d2`.

### Docker

```bash
docker run --rm -it -u "$(id -u):$(id -g)" \
  -v "$PWD:/home/debian/src" \
  -p 127.0.0.1:8080:8080 \
  terrastruct/d2:latest --watch helloworld.d2
```

### Verify

```bash
d2 version
d2 themes
d2 layout
```

## Editor integrations

### Official

- VS Code: https://github.com/terrastruct/d2-vscode (syntax, format, hover, live preview)
- Vim: https://github.com/terrastruct/d2-vim
- Obsidian: https://github.com/terrastruct/d2-obsidian
- Slack: https://d2lang.com/tour/slack
- Discord: https://d2lang.com/tour/discord

### Community

- Tree-sitter grammar: https://github.com/ravsii/tree-sitter-d2
- Emacs `d2-mode`: https://github.com/andorsk/d2-mode
- Hugo (Goldmark): https://github.com/FurqanSoftware/goldmark-d2
- MdBook: https://github.com/danieleades/mdbook-d2
- MkDocs: https://github.com/landmaj/mkdocs-d2-plugin
- VitePress: https://github.com/BadgerHobbs/vitepress-plugin-d2
- Zed: https://github.com/gabeidx/zed-d2

### Programmatic SDKs

- Python (`py-d2`)
- JavaScript (`d2lang-js`, `@terrastruct/d2`)
- C# (`d2lang-cs`)
- Clojure (`dictim`)

### Importers

- Postgres → ERD, Mongo → D2, Structurizr → D2, AsyncAPI → D2, ROS2 → D2.

## The ecosystem

### Playground — https://play.d2lang.com

Interactive web editor with live SVG preview. Shareable URLs encode script + theme + sketch flag in query string. The CLI's `d2 play` builds these URLs.

### Hosted icons — https://icons.terrastruct.com

Free icon library for AWS/Azure/GCP/dev/tech/infra/essentials. Use directly with `icon: <url>`.

### Comparison site — https://text-to-diagram.com

Compares D2 head-to-head with Mermaid, Graphviz, PlantUML. Useful for tool-choice justification.

## Common errors

### Compile / parse

```
err: failed to compile diagram.d2: diagram.d2:3:5: unexpected token "}"
```

D2's parser collects multiple errors. Common causes: unmatched braces, bad arrow syntax (`-->` is invalid; use `->`), unquoted reserved keywords used as shape names, circular vars references.

### Theme not found

```
-t[heme] could not be found. The available options are: ...
```

Pick from `d2 themes` output.

### Layout engine not found

```
D2_LAYOUT "tala" is not bundled and could not be found in your $PATH.
```

Install TALA, or use `dagre` / `elk`.

### Chromium / Playwright

```
err: failed to launch Chromium
```

Run `npx playwright install --with-deps chromium` or `d2 init-playwright`.

### Flag conflicts

| Error | Cause |
|---|---|
| `--animate-interval can only be used when exporting to SVG or GIF.` | Used with PNG/PDF/PPTX |
| `-w[atch] cannot be combined with reading input from stdin` | `d2 -w - out.svg` |
| `-w[atch] cannot be combined with --target` | `--watch` + non-`*` `--target` |
| `multiboard output cannot be written to stdout` | Multi-board → `-` |
| `D2 does not support ppt exports, did you mean "pptx"?` | `.ppt` extension |

### Render-target

```
render target "<path>" not found
```

`--target=layers.foo` where `foo` doesn't exist.

### Font

```
expected .ttf file but <path> has extension <ext>
```

D2 doesn't accept `.otf` or `.woff`.

### Lint (CI)

```
found 3 unformatted files. Run d2 fmt to fix.
```

`d2 fmt --check` exits non-zero so CI can gate on formatting.

## Quick debugging recipes

```bash
DEBUG=1 d2 -d diagram.d2                 # verbose
d2 layout dagre                          # see all dagre flags
d2 layout elk                            # see all ELK flags
d2 fmt diagram.d2                        # canonicalize before diffing
d2 validate -                            # parse check from stdin
echo "x -> y" | d2 - -                   # round-trip test
D2_THEME=300 D2_SKETCH=1 d2 in.d2 out.svg
```
