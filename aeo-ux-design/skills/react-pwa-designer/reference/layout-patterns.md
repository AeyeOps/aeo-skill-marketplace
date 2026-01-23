# Layout Patterns for React PWAs

**When to read this**: Building panels, grids, or resizable containers with React + Tailwind + shadcn/ui.

**Quick answer**: See [Flex Container Scrolling](#flex-container-scrolling-pattern) for the most common issue.

---

## Contents

- [Flex Container Scrolling Pattern](#flex-container-scrolling-pattern)
- [CSS Grid + Dynamic Columns](#css-grid--dynamic-columns-pattern)
- [Conditional Transitions for Interactive Elements](#conditional-transitions-pattern)
- [Truncation vs Wraparound](#truncation-vs-wraparound-decision)

---

## Flex Container Scrolling Pattern

### The Problem

Flex containers with collapsible content (accordions, expandable lists) don't scroll properly even with `overflow-y-auto`.

```tsx
// ❌ BAD - Won't scroll when content overflows
<div className="h-full flex flex-col">
  <div>Panel Header</div>
  <div className="flex-1 overflow-y-auto">
    <Accordion>...</Accordion>  {/* Content exceeds height but no scrollbar */}
  </div>
</div>
```

### Why It Happens

Flex children default to `min-height: auto`, which prevents them from shrinking below their content size. The browser says "content is 2000px tall, so flex child must be 2000px tall" - even though the parent is only 500px.

### The Solution

```tsx
// ✅ CORRECT - Scrolls properly
<div className="flex flex-col h-full overflow-hidden">  {/* overflow-hidden constrains */}
  <div className="flex-shrink-0">Panel Header</div>     {/* Fixed size */}
  <div className="flex-1 min-h-0 overflow-y-auto">      {/* min-h-0 allows shrink */}
    <Accordion>...</Accordion>
  </div>
</div>
```

### Key Points

1. **Parent**: Add `overflow-hidden` to constrain total height
2. **Fixed elements**: Use `flex-shrink-0` on headers/footers
3. **Scrollable area**: Add `min-h-0` + `overflow-y-auto` together
4. **Why `min-h-0`**: Overrides default `min-height: auto` so flex child can shrink

### When This Pattern Applies

- ✅ Panels with accordions or collapsible sections
- ✅ Sidebars with dynamic content lists
- ✅ Modals/dialogs with variable content height
- ✅ Chat interfaces with message history
- ✅ Any container where content height is unpredictable

---

## CSS Grid + Dynamic Columns Pattern

### The Problem

Grid columns overlap when using CSS Variables for dynamic widths without explicit placement.

```tsx
// ❌ BAD - Auto-placement causes overlap when widths change
<div className="grid grid-cols-[var(--left)_1fr_var(--right)]">
  <div>Left</div>   {/* May overlap center when --left changes */}
  <div>Center</div>
  <div>Right</div>
</div>
```

### Why It Happens

CSS Grid's auto-placement algorithm doesn't recalculate positions reliably when CSS Variable values change. The browser tries to be "smart" about placement, but dynamic changes confuse it.

### The Solution

```tsx
// ✅ CORRECT - Explicit placement prevents overlap
<div className="grid grid-cols-[var(--left)_1fr_var(--right)] grid-rows-[56px_1fr_200px]">
  <div className="col-start-1 row-start-2">Left</div>
  <div className="col-start-2 row-start-2">Center</div>
  <div className="col-start-3 row-start-2">Right</div>
</div>
```

### Grid Placement Classes

```tsx
// Column placement
col-start-1  col-start-2  col-start-3
col-span-2   col-span-3   col-span-full

// Row placement
row-start-1  row-start-2  row-start-3
row-span-2   row-span-3   row-span-full

// Combined
className="col-start-2 row-start-1 col-span-2"
```

### Complete Example: 3×3 Grid with Dynamic Columns

```tsx
const [leftWidth, setLeftWidth] = useState(280);
const [rightWidth, setRightWidth] = useState(280);

return (
  <div
    className="grid gap-0 h-screen"
    style={{
      '--left': `${leftWidth}px`,
      '--right': `${rightWidth}px`,
      gridTemplateColumns: 'var(--left) 1fr var(--right)',
      gridTemplateRows: '56px 1fr 200px',
    } as React.CSSProperties}
  >
    {/* Header - spans all columns */}
    <div className="col-span-3 row-start-1">Header</div>

    {/* Main row - explicit column placement */}
    <div className="col-start-1 row-start-2">Left Panel</div>
    <div className="col-start-2 row-start-2">Center Content</div>
    <div className="col-start-3 row-start-2">Right Panel</div>

    {/* Footer - spans all columns */}
    <div className="col-span-3 row-start-3">Footer</div>
  </div>
);
```

### When This Pattern Applies

- ✅ IDE-style layouts with resizable panels
- ✅ Dashboard grids with dynamic column widths
- ✅ Any grid where column/row sizes change based on state
- ✅ Multi-panel workbenches with collapse/expand

---

## Conditional Transitions Pattern

### The Problem

Transitions lag behind user interactions (dragging, resizing) making the interface feel sluggish.

```tsx
// ❌ BAD - Transition active during drag makes it feel slow
<div className="grid transition-all duration-300">
  <ResizeGrip onDrag={(delta) => setWidth(w => w + delta)} />
</div>
// Mouse moves 100px → Visual only moves 30px (transition still catching up)
```

### Why It Happens

CSS transitions smooth changes over time (e.g., 300ms). When dragging, you want **instant** visual feedback (1:1 tracking), but the transition adds lag between state change and visual update.

### The Solution

```tsx
// ✅ CORRECT - Disable transition during interaction
const [isDragging, setIsDragging] = useState(false);

return (
  <div className={`grid ${isDragging ? '' : 'transition-all duration-300'}`}>
    <ResizeGrip
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => setIsDragging(false)}
      onDrag={(delta) => setWidth(w => w + delta)}
    />
  </div>
);
```

### CSS Approach (Conditional Class)

```tsx
// Component
<div className={`grid ${isDragging ? '' : 'grid-transition'}`}>

// CSS (in index.css)
@layer components {
  .grid-transition {
    transition: grid-template-columns 300ms ease-out;
  }
}
```

### When Transitions Should Be Active

- ✅ **Button clicks** (collapse/expand) - smooth animation desired
- ✅ **Keyboard shortcuts** (Ctrl+B) - visual feedback for state change
- ✅ **Programmatic changes** - aesthetic smooth transitions

### When Transitions Should Be Disabled

- ❌ **Dragging** - needs instant 1:1 tracking
- ❌ **Resizing** - direct manipulation requires immediate feedback
- ❌ **Scrolling** - browser handles this natively
- ❌ **Real-time data updates** - avoid visual lag

### Complete Example: Resizable Panel

```tsx
const ResizablePanel = () => {
  const [width, setWidth] = useState(280);
  const [isDragging, setIsDragging] = useState(false);

  return (
    <div
      className={`panel ${isDragging ? '' : 'transition-width'}`}
      style={{ width: `${width}px` }}
    >
      <ResizeGrip
        onDragStart={() => setIsDragging(true)}
        onDrag={(delta) => setWidth(w => Math.max(200, Math.min(500, w + delta)))}
        onDragEnd={() => setIsDragging(false)}
      />
      Panel Content
    </div>
  );
};
```

---

## Truncation vs Wraparound Decision

### The Problem

Text truncation (`truncate`) hides information when containers resize, breaking the value proposition of resizable panels.

```tsx
// ❌ BAD - User makes panel narrow, loses critical info
<div className="truncate">
  POG Health Check for Store 60 in Circle K Region 5...
</div>
// User narrows panel → "POG Health..."  (Region info lost!)
```

### The Decision Tree

```
Is the container width fixed?
├─ Yes (fixed width) → Use `truncate` (acceptable)
└─ No (resizable/responsive) → Use `break-words` (required)
    └─ Why? User can adjust width to see all content
```

### Fixed-Width Container (Truncate OK)

```tsx
// ✅ OK - Width never changes, truncate acceptable
<div className="w-64 truncate">
  {longText}
</div>
```

### Resizable/Responsive Container (Wraparound Required)

```tsx
// ✅ CORRECT - Text wraps when panel narrows
<div className="break-words">
  POG Health Check for Store 60 in Circle K Region 5
</div>

// User narrows panel →
// POG Health Check for
// Store 60 in Circle K
// Region 5
// (All info still visible!)
```

### Common Scenarios

| Scenario | Pattern | Class |
|----------|---------|-------|
| Sidebar with resize grip | Wraparound | `break-words` |
| Responsive mobile layout | Wraparound | `break-words` |
| Table cell (fixed columns) | Truncate | `truncate` |
| Tooltip text | Truncate | `truncate` |
| Accordion content in resizable panel | Wraparound | `break-words` |
| Fixed-width badge | Truncate | `truncate` |
| Chat message in resizable window | Wraparound | `break-words` |

### With Line Clamping (Best of Both)

```tsx
// ✅ BEST - Wraps to 2 lines, then truncates
<div className="break-words line-clamp-2">
  {longText}
</div>
// Shows first 2 lines with wraparound, truncates overflow
```

### Key Points

1. **Resizable panels = wraparound** (user controls width, needs all content)
2. **Fixed width = truncate OK** (space constraint is known)
3. **Accessibility**: Screen readers get full text regardless
4. **Line-clamp**: Good middle ground for known maximum height

---

## Quick Reference

### Scrolling Not Working?
```tsx
<div className="flex flex-col h-full overflow-hidden">
  <div className="flex-1 min-h-0 overflow-y-auto">
    {/* Content */}
  </div>
</div>
```

### Grid Columns Overlapping?
```tsx
<div className="grid" style={{ gridTemplateColumns: 'var(--w1) 1fr var(--w2)' }}>
  <div className="col-start-1">A</div>
  <div className="col-start-2">B</div>
  <div className="col-start-3">C</div>
</div>
```

### Resize Feels Sluggish?
```tsx
const [dragging, setDragging] = useState(false);
<div className={dragging ? '' : 'transition-all'}>
```

### Text Hidden When Resizing?
```tsx
<div className="break-words">  {/* Not truncate */}
```

---

## Related Resources

- See `dynamic-styling-patterns.md` for CSS Variables pattern
- See `common-pitfalls.md` for more anti-patterns
- Check CSS Tricks: [Flexbox Min-Height Issue](https://css-tricks.com/flexbox-truncated-text/)
- Check MDN: [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
