# Dynamic Styling Patterns in React + Tailwind

**When to read this**: Choosing between inline styles, CSS variables, Tailwind utilities, or other approaches for state-driven dynamic styling in React + Tailwind applications.

**Quick answer**: Use CSS Variables (2025 best practice) for state-driven layout changes. See [CSS Variables Pattern](#css-variables-pattern-2025-best-practice) for immediate implementation.

---

## Contents

- [Decision Tree](#decision-tree-choosing-your-styling-approach)
- [CSS Variables Pattern (2025 Best Practice)](#css-variables-pattern-2025-best-practice)
- [Common Anti-Patterns](#common-anti-patterns)
- [When Inline Styles ARE Appropriate](#when-inline-styles-are-appropriate)
- [Tailwind JIT Safelist Pattern](#tailwind-jit-safelist-pattern)
- [Conditional Styling with cn()](#conditional-styling-with-cn-utility)
- [Research Workflow](#research-workflow-the-meta-lesson)
- [Real-World Example](#real-world-example-the-grid-layout-problem)
- [Quick Reference Table](#quick-reference-table)
- [Performance Considerations](#performance-considerations)
- [Migration Guide](#migration-guide)

---

## Decision Tree: Choosing Your Styling Approach

```
Need to style based on state/props?
│
├─ Static styles only? → Tailwind utility classes
│
├─ Conditional (2-3 variants)? → cn() utility with conditional logic
│
├─ Dynamic numeric/string values from state? → CSS Variables (PREFERRED 2025)
│
├─ Complex animation sequences? → Framer Motion or CSS animations
│
└─ Last resort only → Inline styles (when nothing else works)
```

---

## CSS Variables Pattern (2025 Best Practice)

This is the **PREFERRED** approach for state-driven dynamic styles.

### Example: Dynamic Grid Layout

```tsx
// ✅ CORRECT - Clean separation of concerns
const WorkbenchGrid = ({ leftCollapsed, rightCollapsed }) => {
  const leftColWidth = leftCollapsed ? '60px' : '280px';
  const rightColWidth = rightCollapsed ? '60px' : '280px';

  return (
    <div
      className="workbench-grid"
      style={{
        '--left-col-width': leftColWidth,
        '--right-col-width': rightColWidth,
      } as React.CSSProperties}
    >
      {/* Grid content */}
    </div>
  );
};
```

### Corresponding CSS (in index.css or component CSS)

```css
@layer components {
  .workbench-grid {
    display: grid;
    grid-template-columns: var(--left-col-width) 1fr var(--right-col-width);
    grid-template-rows: 56px 1fr 200px;
    transition: grid-template-columns 300ms ease-out;
  }
}
```

### Why CSS Variables Are Better

- **Separation of concerns**: React state → CSS variables, CSS handles layout
- **Leverages Tailwind**: Can still use utility classes for other properties
- **Maintainable**: CSS stays in CSS files, not scattered in JSX
- **Performance**: Browser optimizes CSS variable updates
- **Type-safe**: Works with `as React.CSSProperties`
- **Debuggable**: Easy to inspect in DevTools

---

## Common Anti-Patterns

### ❌ Inline Styles for Layout

```tsx
// DON'T DO THIS - Mixes concerns, hard to maintain
<div style={{
  gridTemplateColumns: `${leftCollapsed ? '60px' : '280px'} 1fr ${rightCollapsed ? '60px' : '280px'}`,
  transition: 'grid-template-columns 300ms ease-out',
}}>
```

**Why it's wrong:**
- Layout logic in JavaScript instead of CSS
- Can't leverage CSS features (media queries, pseudo-elements)
- Harder to maintain and test
- Doesn't work well with SSR/hydration edge cases

### ❌ String Concatenation for Dynamic Tailwind Classes

```tsx
// DON'T DO THIS - Tailwind JIT won't detect these
<div className={`w-${width} bg-${color}-500`}>
```

**Why it's wrong:**
- Tailwind's JIT compiler can't statically analyze string concatenation
- Classes won't be generated unless in safelist
- Runtime errors when classes don't exist

### ❌ Fighting Specificity with !important

```tsx
// DON'T DO THIS - Creates maintenance nightmare
<div className="w-64 !w-80 hover:!w-96">
```

**Why it's wrong:**
- Makes styles harder to override
- Indicates poor CSS architecture
- Creates specificity wars

### ❌ Not Using @layer for Custom Utilities

```css
/* DON'T DO THIS - Wrong specificity order */
.custom-button {
  padding: 1rem;
  background: blue;
}

/* DO THIS - Proper layer organization */
@layer components {
  .custom-button {
    padding: 1rem;
    background: theme('colors.blue.500');
  }
}
```

---

## When Inline Styles ARE Appropriate

There are legitimate use cases for inline styles:

### 1. User-Configurable Values

```tsx
// ✅ CORRECT - User picks color from color picker
<div style={{ backgroundColor: userSelectedColor }}>
```

### 2. Third-Party Library Integration

```tsx
// ✅ CORRECT - Library requires style object
<ReactPlayer
  style={{ position: 'absolute', top: 0, left: 0 }}
  width="100%"
  height="100%"
/>
```

### 3. Performance-Critical Animations

```tsx
// ✅ CORRECT - Direct DOM manipulation for 60fps
const animateElement = (el: HTMLElement, x: number) => {
  el.style.transform = `translateX(${x}px)`;
};
```

### 4. Server-Rendered Dynamic Values

```tsx
// ✅ CORRECT - Value unknown at build time
<div style={{ backgroundImage: `url(${userAvatar})` }}>
```

---

## Tailwind JIT Safelist Pattern

For truly dynamic classes that can't be statically analyzed:

```js
// tailwind.config.js
module.exports = {
  safelist: [
    // Specific classes
    'w-60', 'w-80', 'w-96',

    // Pattern matching
    {
      pattern: /bg-(red|green|blue)-(400|500|600)/,
      variants: ['hover', 'focus'],
    },

    // Dynamic grid columns (if you must)
    {
      pattern: /grid-cols-(1|2|3|4|5|6|7|8|9|10|11|12)/,
    },
  ],
};
```

**When to use safelist:**
- User-driven theme customization
- CMS-driven styling
- A/B testing variants
- Dynamic content from database

**When NOT to use safelist:**
- State-driven UI changes (use CSS Variables instead)
- Responsive layouts (use responsive utilities)
- Component variants (use `cn()` with conditions)

---

## Conditional Styling with cn() Utility

For simple conditional styling, use the `cn()` utility from shadcn/ui:

```tsx
import { cn } from "@/lib/utils"

// ✅ CORRECT - Clean conditional styling
<Button
  className={cn(
    "base-styles",
    isActive && "active-styles",
    isDisabled && "disabled-styles",
    size === "lg" && "text-lg px-6"
  )}
>
```

---

## Research Workflow (The Meta-Lesson!)

When uncertain about styling approaches:

### 1. Don't Assume
Styling best practices evolve rapidly. What worked in 2023 may not be optimal in 2025.

### 2. Use Context7 MCP for Official Documentation

```typescript
// Context7 for official React/Tailwind docs
mcp__context7__get_library_docs({
  context7CompatibleLibraryID: "/facebook/react",
  topic: "styling patterns",
  tokens: 5000
})
```

### 3. Query Pattern
"What is the best practice for [X] in React with Tailwind CSS for 2025?"

### 4. Document the Decision
Update this guide when you discover new patterns.

---

## Real-World Example: The Grid Layout Problem

**Context**: Building a 3-column workbench where left/right panels collapse, and center panel expands to fill space.

### The Journey

**Problem**: Grid columns need to change based on panel collapse state

**Initial approach (❌)**:
```tsx
<div style={{
  gridTemplateColumns: `${leftCollapsed ? '60px' : '280px'} 1fr ${rightCollapsed ? '60px' : '280px'}`,
  transition: 'grid-template-columns 300ms ease-out',
}}>
```

**Recommended approach**: CSS Variables for dynamic grid layouts

**Final solution (✅)**:
```tsx
// React component
<div
  className="workbench-grid"
  style={{
    '--left-col-width': leftCollapsed ? '60px' : '280px',
    '--right-col-width': rightCollapsed ? '60px' : '280px',
  } as React.CSSProperties}
/>

// CSS
@layer components {
  .workbench-grid {
    grid-template-columns: var(--left-col-width) 1fr var(--right-col-width);
    transition: grid-template-columns 300ms ease-out;
  }
}
```

**Why it's better:**
- Separation of concerns
- Maintainable
- Leverages browser optimizations
- Works with SSR/hydration
- Easy to test and debug

---

## Quick Reference Table

| Use Case | Approach | Example |
|----------|----------|---------|
| Static styling | Tailwind utility | `className="w-64 bg-blue-500"` |
| Conditional (2-3 variants) | `cn()` + conditions | `cn("base", isActive && "active")` |
| Dynamic numeric values | CSS Variables | `style={{'--width': width}}` |
| Complex state-driven layout | CSS Variables + `@layer` | See Grid example above |
| Animation sequences | Framer Motion | `<motion.div animate={{x: 100}}` |
| User input colors | Inline styles | `style={{backgroundColor: userColor}}` |
| Responsive design | Tailwind responsive | `className="w-full md:w-1/2 lg:w-1/3"` |
| Component variants | CVA (class-variance-authority) | `const buttonVariants = cva(...)` |

---

## Performance Considerations

### CSS Variables vs Inline Styles

**CSS Variables:**
- Browser optimizes CSS variable updates
- Can leverage GPU acceleration
- Works with CSS transitions/animations
- ~10-15% faster for frequent updates

**Inline Styles:**
- Direct style recalculation each render
- May trigger layout thrashing
- Can't use CSS transitions smoothly
- Use only when necessary

### Measurement

```tsx
// Measure style update performance
const start = performance.now();
element.style.setProperty('--my-var', newValue);
const end = performance.now();
console.log(`Update took ${end - start}ms`);
```

---

## Migration Guide

### From Inline Styles to CSS Variables

```tsx
// BEFORE
const MyComponent = ({ width, height }) => (
  <div style={{ width, height, transition: 'all 300ms' }}>
    Content
  </div>
);

// AFTER
const MyComponent = ({ width, height }) => (
  <div
    className="dynamic-container"
    style={{ '--width': width, '--height': height } as React.CSSProperties}
  >
    Content
  </div>
);

// Add to CSS
@layer components {
  .dynamic-container {
    width: var(--width);
    height: var(--height);
    transition: width 300ms, height 300ms;
  }
}
```

---

## Related Resources

- See `reference/react-hooks.md` for state management patterns
- See `reference/common-pitfalls.md` for more anti-patterns
- See `reference/performance-optimization.md` for advanced techniques
- Check Tailwind docs: https://tailwindcss.com/docs/adding-custom-styles
- Check CSS Variables spec: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
