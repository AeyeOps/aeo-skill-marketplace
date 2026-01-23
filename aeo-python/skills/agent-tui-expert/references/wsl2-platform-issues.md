# WSL2 Platform Issues for Textual TUI Development

**CRITICAL: Read this first if developing Textual apps in WSL2.**

This document captures hard-won lessons from extensive debugging of Textual applications running in WSL2 environments. These issues cost 12+ hours to diagnose and resolve.

## The Big Problem: Horizontal Resize Doesn't Work

### Symptoms

- Vertical resize (making terminal taller/shorter) works perfectly
- Horizontal resize (making terminal wider/narrower) does nothing
- Header/Footer backgrounds resize, but their contents don't
- Main content area stays fixed at original width
- Problem persists across all terminals (Windows Terminal, Warp, etc.)

### Root Cause

**Microsoft WSL Issue #1001**: WSL2 does not propagate `SIGWINCH` signals for horizontal-only terminal resizes.

- When you resize only horizontally, the Linux kernel inside WSL2 never receives the signal
- `shutil.get_terminal_size()` returns stale cached values
- `stty size` subprocess calls may not have proper stdin access
- Textual's driver never sees the resize event

### The Solution: ioctl TIOCGWINSZ Polling

The only reliable method is to directly query the kernel's terminal driver using `ioctl`:

```python
import fcntl
import struct
import sys
import termios
from textual.geometry import Size
from textual import events

class MyApp(App):
    def __init__(self) -> None:
        super().__init__()
        self._last_polled_size: tuple[int, int] | None = None

    def on_mount(self) -> None:
        # Poll terminal size every 500ms as WSL2 workaround
        self.set_interval(0.5, self._poll_terminal_size, pause=False)
        self._poll_terminal_size()  # Initial poll

    def _poll_terminal_size(self) -> None:
        """Poll terminal size - workaround for WSL2 SIGWINCH bug."""
        cols, rows = 0, 0

        # ioctl TIOCGWINSZ - direct kernel query, most reliable
        for fd in (sys.stdin.fileno(), sys.stdout.fileno(), sys.stderr.fileno()):
            try:
                result = fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\x00" * 8)
                rows, cols = struct.unpack("HHHH", result)[:2]
                if cols > 0 and rows > 0:
                    break
            except Exception:
                continue

        # Fallback to shutil (may be stale on WSL2)
        if cols <= 0 or rows <= 0:
            import shutil
            try:
                cols, rows = shutil.get_terminal_size(fallback=(0, 0))
            except Exception:
                return

        if cols <= 0 or rows <= 0:
            return

        current = (self.size.width, self.size.height)
        polled = (cols, rows)

        if self._last_polled_size != polled:
            self._last_polled_size = polled
            if polled != current:
                # Force update internal size state
                new_size = Size(cols, rows)
                self._size = new_size
                if hasattr(self, "_driver") and self._driver:
                    self._driver._size = new_size
                self.screen._size = new_size

                # Post synthetic resize event
                self.post_message(
                    events.Resize(
                        size=new_size,
                        virtual_size=new_size,
                        container_size=new_size,
                    )
                )
                self.screen.refresh(layout=True)
```

### Why Other Methods Fail

| Method | Problem on WSL2 |
|--------|-----------------|
| `shutil.get_terminal_size()` | Returns cached values, misses horizontal resize |
| `stty size` subprocess | Needs stdin attached to terminal, unreliable in subprocess |
| `os.get_terminal_size()` | Same caching issue as shutil |
| Relying on SIGWINCH | Signal never arrives for horizontal-only resize |

### Key Points

1. **Poll interval**: 500ms is responsive without being wasteful
2. **Update ALL internal state**: `app._size`, `driver._size`, `screen._size`
3. **Post synthetic event**: Textual needs the Resize message to trigger layout
4. **Force screen refresh**: Call `screen.refresh(layout=True)` after posting

---

## Layout Gotchas That Break Sidebars

### Never Force Fixed Pixel Widths on Flex Containers

**Problem**: Setting `widget.styles.width = pixel_value` on containers that use `1fr` breaks flexible layout.

```python
# BAD - breaks sidebar toggle
def on_resize(self, event: events.Resize) -> None:
    for selector in ["#main-layout", "#left-content"]:
        widget = self.query_one(selector)
        widget.styles.width = event.size.width  # Overwrites 1fr!
```

When you set `#left-content` to full screen width, there's no room for the sidebar even when visible.

**Solution**: Let CSS `1fr` units handle sizing naturally.

```python
# GOOD - let CSS handle it
def on_resize(self, event: events.Resize) -> None:
    self.call_after_refresh(self._post_resize_refresh)
```

### Don't Mix Horizontal Container with CSS Grid

**Problem**: Using `layout: grid` CSS on a `Horizontal` container causes conflicts.

```python
# In compose():
with Horizontal(id="main-layout"):  # Natural horizontal layout
    yield Vertical(id="left-content")
    yield Vertical(id="sidebar")
```

```css
/* BAD - conflicts with Horizontal's natural behavior */
#main-layout {
    layout: grid;
    grid-size: 2 1;
    grid-columns: 1fr 40;
}
```

**Solution**: Use `Horizontal`'s natural layout with CSS `display: none/block` for toggling.

```css
/* GOOD - works with Horizontal container */
#main-layout {
    width: 1fr;
    height: 1fr;
}

#left-content {
    width: 1fr;
    height: 100%;
}

#sidebar {
    width: 40;
    height: 100%;
    display: none;
}

#sidebar.visible {
    display: block;
}
```

### Sidebar Toggle Pattern That Works

```python
def action_toggle_sidebar(self) -> None:
    sidebar = self.query_one("#sidebar")
    if sidebar.has_class("visible"):
        sidebar.remove_class("visible")
    else:
        sidebar.add_class("visible")
    # Just toggle display, let Horizontal handle layout
    sidebar.styles.display = "block" if sidebar.has_class("visible") else "none"
    sidebar.refresh(layout=True)
```

---

## Debugging Textual Apps

### Enable Debug Logging

```python
class MyApp(App):
    LOGGING = "debug"  # Enables detailed logging
```

### Log Locations

```
~/.cache/<app-name>/logs/textual.log   # Textual events
~/.cache/<app-name>/logs/app.log       # Custom app logs
```

### Log Widget Sizes

```python
def _log_sizes(self) -> None:
    for selector in ["#main-content", "#sidebar", "#left-content"]:
        try:
            w = self.query_one(selector)
            self.log(f"{selector}: {w.size.width}x{w.size.height}")
        except Exception:
            self.log(f"{selector}: not found")
```

### Watch for Hide Events

When debugging sidebar issues, look for unexpected `Hide()` events:

```
Hide() >>> Vertical(id='sidebar') method=<Widget.on_hide>
```

This indicates the sidebar is being hidden when it should be visible.

### Key Log Patterns

| Pattern | Meaning |
|---------|---------|
| `<action> action_name='toggle_sidebar'` | Action was triggered |
| `Vertical(id='sidebar', classes='visible')` | Class was added |
| `Hide() >>> Vertical(id='sidebar')` | Widget is being hidden |
| `display: none` in styles | CSS is hiding the widget |

---

## Recommended App Structure for WSL2

```python
class WSL2CompatibleApp(App):
    LOGGING = "debug"

    def __init__(self) -> None:
        super().__init__()
        self._last_polled_size: tuple[int, int] | None = None
        self._sidebar_visible: bool = False

    def on_mount(self) -> None:
        # WSL2 resize workaround
        self.set_interval(0.5, self._poll_terminal_size, pause=False)
        self._poll_terminal_size()

    def _poll_terminal_size(self) -> None:
        # [ioctl polling code from above]
        pass

    def on_resize(self, event: events.Resize) -> None:
        # Don't force widths - let CSS handle it
        self.call_after_refresh(self._post_resize_refresh)

    def _post_resize_refresh(self) -> None:
        self.screen.refresh(layout=True)
```

---

## Quick Checklist for WSL2 TUI Development

- [ ] Implement ioctl TIOCGWINSZ polling (500ms interval)
- [ ] Update all internal size state before posting resize event
- [ ] Never set fixed pixel widths on flex containers
- [ ] Use `display: none/block` for toggling panels
- [ ] Don't use `layout: grid` on `Horizontal` containers
- [ ] Enable `LOGGING = "debug"` during development
- [ ] Check logs in `~/.cache/<app>/logs/`
- [ ] Test horizontal AND vertical resize separately
- [ ] Verify sidebar toggle works with resizing

---

## References

- [Microsoft WSL Issue #1001](https://github.com/microsoft/WSL/issues/1001) - SIGWINCH not sent for horizontal resize
- [Textual GitHub #3527](https://github.com/Textualize/textual/issues/3527) - Resize events fire before layout
- [termios TIOCGWINSZ](https://man7.org/linux/man-pages/man4/tty_ioctl.4.html) - Terminal size ioctl
