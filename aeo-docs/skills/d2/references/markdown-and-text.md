# Markdown, LaTeX, and Code Blocks

D2 supports three kinds of "block content" inside labels: Markdown, LaTeX, and syntax-highlighted code. The syntax is the same — a pipe-delimited block with a language tag.

## The block delimiter syntax

```d2
key: |<lang>
  ...content...
|
```

The default delimiter is `|`. If your content contains `|`, escalate to `||` or `|||` or pick a custom non-alphanumeric delimiter:

```d2
ts-code: |ts
  const x: string = "hello";
|

with-pipe: ||ts
  declare function f(): A | B;
||

triple-pipe: |||ts
  const works = (a > 1) || (b < 2);
|||

custom-delim: |`ts
  declare function f(): A | B;
  const works = (a > 1) || (b < 2)
`|
```

## Markdown

```d2
explanation: |md
  # I can do headers
  ## Including subheaders

  Paragraphs with **bold**, *italic*, ~~strikethrough~~, and `inline code`.

  - Bullet list
  - Item two
    - Nested

  1. Ordered
  2. List

  > Blockquote

  [Link text](https://example.com)
  ![Alt text](https://example.com/image.png)

  ---

  | Col 1 | Col 2 |
  |-------|-------|
  | A     | B     |
|
```

The `|md` block creates a Markdown text block — by default a rectangle-shaped node. Override:

```d2
explanation.shape: text         # remove the rectangle border
explanation.style.font-size: 18
```

### Markdown features supported

D2 uses GitHub-flavored Markdown. Supported:

- Headings (`#` through `######`)
- Bold (`**bold**` or `__bold__`)
- Italic (`*italic*` or `_italic_`)
- Strikethrough (`~~text~~`)
- Inline code (`` `code` ``)
- Code fences (triple backticks with language)
- Lists — ordered (`1.`), unordered (`-`, `*`), nested
- Links — `[text](url)` (clickable in SVG output)
- Images — `![alt](url)`
- Blockquotes (`>`)
- Tables — standard `|col|col|` syntax
- Horizontal rule (`---`)

### Markdown labels on existing shapes

To put Markdown on a shape that's already declared:

```d2
api: { shape: rectangle }
api.label: |md
  ### API Service
  - REST + GraphQL
  - Rate-limited at 100 req/sec
|
```

Or in one go:

```d2
api: |md
  ### API Service
  - REST + GraphQL
| {
  shape: rectangle
}
```

## Code blocks (syntax-highlighted)

Use the language name (or alias) as the tag. D2 uses Chroma for highlighting — every Chroma language works.

```d2
example: |go
  package main

  import "fmt"

  func main() {
      fmt.Println("Hello")
  }
|

py-example: |python
  def fib(n):
      a, b = 0, 1
      for _ in range(n):
          yield a
          a, b = b, a + b
|
```

Convenience aliases:

| Alias | Real |
|---|---|
| `md` | `markdown` |
| `tex` | `latex` |
| `js` | `javascript` |
| `go` | `golang` |
| `py` | `python` |
| `rb` | `ruby` |
| `ts` | `typescript` |

Unknown languages render as plain text without highlighting. Use `shape: code` to suppress the rectangle:

```d2
snippet: |js
  const x = 42
| {
  shape: code
  style.font: mono
}
```

## LaTeX / math

```d2
formula: |latex
  \displaystyle\sum_{i=0}^{\infty} \frac{1}{i!}
|

# 'tex' is an alias
quadratic: |tex
  x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
|
```

LaTeX renders via MathJax — display math, not document layout.

### LaTeX limitations

- **No native line breaks.** Use `\displaylines{first \\ second}` for multi-line equations.
- **`font-size` is ignored.** Use TeX size commands instead: `\tiny`, `\small`, `\normal`, `\large`, `\huge`.

```d2
big-formula: |tex
  \huge E = mc^2
|

multi-line: |tex
  \displaylines{
    a = b + c \\
    d = e \cdot f
  }
|
```

### Bundled MathJax extensions

D2 ships these MathJax packages — no extra setup:

- `amsmath`, `amssymb` — AMS math/symbols
- `color` — colored math
- `mathtools` — extended math notation
- `physics` — physics notation (`\bra`, `\ket`, etc.)
- `cancel` — `\cancel` strikethrough
- `gensymb` — `\degree`, `\micro`
- `mhchem` — chemistry (`\ce{H2O}`, etc.)
- `braket` — Dirac bra-ket notation

```d2
chemistry: |tex
  \ce{H2 + O2 -> H2O}
|

physics: |tex
  \bra{\psi}\hat{H}\ket{\phi}
|
```

## `shape: text` and `shape: code`

Use these when you don't need a surrounding rectangle:

```d2
note: This is just a label. {
  shape: text
}

snippet: |sh
  curl -X POST /api -d '{"x": 1}'
| {
  shape: code
  style.font: mono
}
```

## Block strings — alternative delimiters

Recap: when content contains `|`, escalate the delimiter. Anything non-alphanumeric, non-space, non-underscore works:

```d2
single:  | plain text |
double:  || pipes | inside ||
triple:  ||| pipes || inside |||
custom:  |' python
  print("|||" in "hello|||world")
'|
```

## Unicode and emoji

Render directly. Font coverage depends on the active font:

```d2
welcome: 你好 — مرحبا — こんにちは — 🌍🚀
fail -> retry: 🔁
```

## Tooltips with Markdown

Tooltips can also use the `|md ... |` block syntax for rich formatting:

```d2
service: API {
  tooltip: |md
    ## Service contract
    - Rate limit: 100/sec
    - Auth: Bearer token
  |
  tooltip.near: top-center
}
```

When `tooltip.near` is set, the tooltip is **always visible** (not hover-only).

## Cheat sheet

```text
key: |md     ... |             # markdown block
key: |tex    ... |             # LaTeX (MathJax)
key: |latex  ... |             # alias of tex
key: |go     ... |             # syntax-highlighted Go
key: |py     ... |             # alias for python
key: |js     ... |             # alias for javascript
key: |ts     ... |             # alias for typescript

# Pipe collisions: escalate delimiter
key: || ... ||                 # double-pipe
key: ||| ... |||               # triple-pipe
key: |` ... `|                 # custom char

shape: text   # plain label without surrounding box
shape: code   # code block without surrounding box
```
