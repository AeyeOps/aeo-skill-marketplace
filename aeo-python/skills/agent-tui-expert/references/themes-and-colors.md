# Themes and Colors

Textual's built-in theme system for consistent, professional styling.

## Default Theme Policy

**Recommendation:** Use a built-in theme as the base, then layer minimal layout CSS on top.

```python
class MyApp(App):
    # Use built-in theme - no custom color definitions needed
    theme = "textual-dark"  # or "nord", "gruvbox", "tokyo-night"

    CSS = """
    /* Only layout rules - colors come from theme */
    #sidebar { dock: left; width: 25; }
    #main { height: 1fr; }
    """
```

This approach:
- Provides professional colors out of the box
- Ensures consistency across widgets
- Reduces CSS boilerplate
- Enables easy theme switching

## Built-in Themes

| Theme | Description |
|-------|-------------|
| `textual-dark` | Default dark theme |
| `textual-light` | Default light theme |
| `nord` | Nord color palette (cool, bluish) |
| `gruvbox` | Gruvbox retro palette (warm, earthy) |
| `tokyo-night` | Tokyo Night palette (purple/blue accents) |
| `solarized-light` | Solarized light variant |

### Switching Themes

```python
class MyApp(App):
    # Set default theme
    theme = "nord"

    def action_toggle_theme(self) -> None:
        # Switch at runtime
        self.theme = "gruvbox" if self.theme == "nord" else "nord"
```

Users can also switch themes via Command Palette (Ctrl+P).

### Preview Themes

```bash
# Preview all themes and colors interactively
textual colors
```

## Theme Variables

### Base Colors

| Variable | Purpose |
|----------|---------|
| `$primary` | Primary brand color |
| `$secondary` | Secondary brand color |
| `$accent` | Accent/highlight color |
| `$foreground` | Default text color |
| `$background` | Screen background |
| `$surface` | Widget/panel background |
| `$panel` | Panel background (slightly different from surface) |
| `$boost` | Emphasized background |
| `$warning` | Warning indicators |
| `$error` | Error indicators |
| `$success` | Success indicators |

### Using Theme Variables

```css
Screen {
    background: $background;
}

#sidebar {
    background: $surface;
    border: solid $primary;
}

.error-message {
    color: $error;
    background: $error-darken-3;
}

Button {
    background: $primary;
}

Button:hover {
    background: $primary-lighten-1;
}
```

### Shade Variations

Each base color has lighter and darker variants:

```css
/* Lighter shades */
$primary-lighten-1    /* Slightly lighter */
$primary-lighten-2    /* Lighter */
$primary-lighten-3    /* Lightest */

/* Darker shades */
$primary-darken-1     /* Slightly darker */
$primary-darken-2     /* Darker */
$primary-darken-3     /* Darkest */
```

**Example:**

```css
Button {
    background: $primary;
}

Button:hover {
    background: $primary-lighten-1;
}

Button:focus {
    background: $primary-lighten-2;
    border: thick $accent;
}

Button.-disabled {
    background: $primary-darken-2;
    opacity: 0.5;
}
```

### Text Colors

| Variable | Purpose |
|----------|---------|
| `$text` | Default text |
| `$text-muted` | De-emphasized text |
| `$text-disabled` | Disabled state text |

### Widget-Specific Variables

```css
/* Buttons */
$button-foreground
$button-color-foreground

/* Input fields */
$input-selection-background
$input-cursor-foreground
$input-cursor-background

/* Scrollbars */
$scrollbar-background
$scrollbar-color
$scrollbar-color-hover
$scrollbar-color-active

/* Links */
$link-background
$link-color
$link-style

/* Footer */
$footer-foreground
$footer-background
```

## Color Formats

### Named Colors

Textual recognizes standard web color names:

```css
background: red;
color: aliceblue;
border: solid dodgerblue;
```

Common named colors: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `black`, `gray`, `orange`, `purple`, `pink`, `brown`, `lime`, `navy`, `teal`, `olive`, `maroon`, `aqua`, `fuchsia`, `silver`

### Hex Colors

```css
/* 6-digit hex */
background: #FF5733;

/* 3-digit shorthand */
background: #F53;

/* 8-digit with alpha */
background: #FF5733A0;

/* 4-digit shorthand with alpha */
background: #F53A;
```

### RGB/RGBA

```css
/* RGB (0-255) */
background: rgb(255, 87, 51);

/* RGBA with alpha (0-1) */
background: rgba(255, 87, 51, 0.5);
```

### HSL/HSLA

```css
/* HSL (hue 0-360, saturation %, lightness %) */
background: hsl(14, 100%, 60%);

/* HSLA with alpha */
background: hsla(14, 100%, 60%, 0.5);
```

## ANSI Colors

For terminal-compatible colors, use ANSI color names:

### Standard ANSI Colors

```css
color: ansi_black;
color: ansi_red;
color: ansi_green;
color: ansi_yellow;
color: ansi_blue;
color: ansi_magenta;
color: ansi_cyan;
color: ansi_white;
```

### Bright ANSI Colors

```css
color: ansi_bright_black;   /* Often gray */
color: ansi_bright_red;
color: ansi_bright_green;
color: ansi_bright_yellow;
color: ansi_bright_blue;
color: ansi_bright_magenta;
color: ansi_bright_cyan;
color: ansi_bright_white;
```

### When to Use ANSI Colors

- Building apps that should match terminal aesthetics
- Ensuring consistent appearance across different terminal emulators
- Creating tools that integrate with existing terminal workflows

## Common Patterns

### Consistent Widget Styling

```css
/* Use theme variables for all colors */
.panel {
    background: $surface;
    border: solid $primary;
    padding: 1;
}

.panel-header {
    background: $primary;
    color: $text;
    text-style: bold;
}

.panel-content {
    background: $background;
}
```

### Status Indicators

```css
.status-success {
    color: $success;
    background: $success-darken-3;
}

.status-warning {
    color: $warning;
    background: $warning-darken-3;
}

.status-error {
    color: $error;
    background: $error-darken-3;
}
```

### Focus and Hover States

```css
Widget:focus {
    border: thick $accent;
}

Button:hover {
    background: $primary-lighten-1;
}

Input:focus {
    border: tall $accent;
    background: $surface-lighten-1;
}
```

### Dark/Light Mode Support

Built-in themes handle dark/light automatically. To support both:

```python
class MyApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle Dark Mode")]

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
```

The `self.dark` property switches between light and dark variants of the current theme.

## Resources

- [Textual Design Guide](https://textual.textualize.io/guide/design/) - Themes and variables
- [Textual Color Reference](https://textual.textualize.io/css_types/color/) - All color formats
- [Textual Styles Reference](https://textual.textualize.io/guide/styles/) - CSS properties
