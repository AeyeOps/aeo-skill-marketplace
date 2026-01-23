# Accessibility (A11y) Reference

WCAG 2.1 Level AA compliance patterns for React PWAs.

## Core Principles (POUR)

1. **Perceivable** - Information must be presentable to users in ways they can perceive
2. **Operable** - UI components must be operable
3. **Understandable** - Information and operation must be understandable
4. **Robust** - Content must be robust enough for assistive technologies

## Semantic HTML

### ✅ Use Proper Elements

```tsx
// ❌ Bad
<div onClick={handleClick}>Submit</div>
<div onClick={handleNav}>Home</div>

// ✅ Good
<button onClick={handleClick}>Submit</button>
<Link to="/">Home</Link>

// ❌ Bad
<div className="heading">Page Title</div>

// ✅ Good
<h1>Page Title</h1>
```

### ✅ Heading Hierarchy

```tsx
<header>
  <h1>Site Title</h1>  {/* Only one h1 per page */}
</header>

<main>
  <h2>Section Title</h2>
  <h3>Subsection</h3>
  <h3>Another Subsection</h3>

  <h2>Another Section</h2>
  <h3>Subsection</h3>
</main>

// ❌ Don't skip levels (h1 → h3)
// ✅ Do maintain hierarchy (h1 → h2 → h3)
```

### ✅ Landmarks

```tsx
<body>
  <header>
    <nav aria-label="Main navigation">...</nav>
  </header>

  <main>
    <section aria-labelledby="products-heading">
      <h2 id="products-heading">Products</h2>
      ...
    </section>
  </main>

  <aside aria-label="Related content">...</aside>

  <footer>...</footer>
</body>
```

## ARIA Attributes

### Common ARIA Patterns

```tsx
// Button with loading state
<button
  aria-busy={isLoading}
  aria-disabled={isDisabled}
  disabled={isDisabled}
>
  {isLoading ? 'Loading...' : 'Submit'}
</button>

// Expandable section
<button
  aria-expanded={isExpanded}
  aria-controls="content-1"
  onClick={toggle}
>
  Toggle Content
</button>
<div id="content-1" hidden={!isExpanded}>
  Content here
</div>

// Modal dialog
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Confirm Action</h2>
  <p id="dialog-description">Are you sure?</p>
  <button>Confirm</button>
  <button>Cancel</button>
</div>

// Live region for announcements
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {statusMessage}
</div>

// Alert
<div role="alert" aria-live="assertive">
  Error: Form submission failed
</div>
```

### ARIA Labels

```tsx
// Icon-only button
<button aria-label="Close dialog">
  <X className="h-4 w-4" />
</button>

// Search input
<label htmlFor="search">Search</label>
<input
  id="search"
  type="search"
  aria-label="Search products"
  placeholder="Search..."
/>

// Link with additional context
<a href="/delete" aria-label="Delete user John Doe">
  Delete
</a>

// Form with description
<label htmlFor="password">Password</label>
<input
  id="password"
  type="password"
  aria-describedby="password-hint"
/>
<span id="password-hint">
  Must be at least 8 characters
</span>
```

## Keyboard Navigation

### ✅ Focus Management

```tsx
import { useRef, useEffect } from 'react'

function Dialog({ isOpen, onClose }: DialogProps) {
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (isOpen) {
      // Focus first focusable element
      closeButtonRef.current?.focus()
    }
  }, [isOpen])

  // Trap focus within dialog
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
    // Implement focus trap
  }

  return (
    <div role="dialog" onKeyDown={handleKeyDown}>
      <button ref={closeButtonRef} onClick={onClose}>
        Close
      </button>
      {/* dialog content */}
    </div>
  )
}
```

### ✅ Skip Links

```tsx
function App() {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header>...</header>
      <main id="main-content" tabIndex={-1}>
        ...
      </main>
    </>
  )
}

// CSS for skip link
/*
.skip-link {
  position: absolute;
  left: -9999px;
  z-index: 999;
}

.skip-link:focus {
  left: 50%;
  transform: translateX(-50%);
  top: 0;
}
*/
```

### ✅ Keyboard Shortcuts

```tsx
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    // Cmd/Ctrl + K for search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      openSearch()
    }
  }

  document.addEventListener('keydown', handleKeyPress)
  return () => document.removeEventListener('keydown', handleKeyPress)
}, [])
```

## Color & Contrast

### ✅ WCAG AA Requirements

**Normal Text (< 18pt)**: 4.5:1 contrast ratio
**Large Text (≥ 18pt or 14pt bold)**: 3:1 contrast ratio

```tsx
// ❌ Bad - Low contrast
<p className="text-gray-400 bg-gray-300">Text</p>

// ✅ Good - Sufficient contrast
<p className="text-gray-900 bg-white">Text</p>
<p className="text-white bg-gray-900">Text</p>
```

### ✅ Don't Rely on Color Alone

```tsx
// ❌ Bad - Color only
<span className="text-red-500">Error</span>

// ✅ Good - Color + icon/text
<span className="text-red-500">
  <AlertCircle className="inline h-4 w-4" />
  Error: Invalid input
</span>

// ✅ Good - Visual indicator + accessible text
<button className="border-2 border-green-500">
  <Check className="h-4 w-4" />
  <span className="sr-only">Selected</span>
</button>
```

## Forms

### ✅ Accessible Form Pattern

```tsx
function ContactForm() {
  const [errors, setErrors] = useState<Record<string, string>>({})

  return (
    <form noValidate onSubmit={handleSubmit}>
      {/* Name field */}
      <div>
        <label htmlFor="name" className="required">
          Name
        </label>
        <input
          id="name"
          type="text"
          aria-required="true"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <span id="name-error" role="alert" className="error">
            {errors.name}
          </span>
        )}
      </div>

      {/* Email with hint */}
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          aria-describedby="email-hint email-error"
        />
        <span id="email-hint" className="hint">
          We'll never share your email
        </span>
        {errors.email && (
          <span id="email-error" role="alert" className="error">
            {errors.email}
          </span>
        )}
      </div>

      {/* Submit */}
      <button type="submit" aria-busy={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}
```

### ✅ Required Field Indicators

```css
/* Visual indicator */
.required::after {
  content: " *";
  color: red;
  aria-hidden: "true";
}

/* Screen reader text */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

## Images & Icons

### ✅ Alt Text

```tsx
// Decorative image
<img src="/decorative.png" alt="" role="presentation" />

// Informative image
<img src="/chart.png" alt="Sales increased 25% in Q4" />

// Functional image (link/button)
<button>
  <img src="/search.svg" alt="Search" />
</button>

// Complex image
<figure>
  <img src="/complex-chart.png" alt="Quarterly sales data" />
  <figcaption>
    Detailed description: Sales in Q1: $100k, Q2: $150k...
  </figcaption>
</figure>

// Icon with text (hide icon from screen readers)
<button>
  <Search aria-hidden="true" className="h-4 w-4" />
  <span>Search</span>
</button>

// Icon only (provide accessible label)
<button aria-label="Search">
  <Search className="h-4 w-4" />
</button>
```

## Tables

### ✅ Accessible Data Table

```tsx
<table>
  <caption>Employee Information</caption>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Department</th>
      <th scope="col">Salary</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">John Doe</th>
      <td>Engineering</td>
      <td>$100,000</td>
    </tr>
  </tbody>
</table>
```

## Animation & Motion

### ✅ Respect prefers-reduced-motion

```css
/* Default animation */
.animated {
  animation: slide-in 0.3s ease-out;
}

/* Reduce or remove for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  .animated {
    animation: none;
  }

  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```tsx
// React hook
function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(query.matches)

    const listener = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches)
    query.addEventListener('change', listener)

    return () => query.removeEventListener('change', listener)
  }, [])

  return prefersReducedMotion
}
```

## Live Regions

### ✅ Status Updates

```tsx
function SearchResults() {
  const [results, setResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  return (
    <>
      {/* Announce loading and results */}
      <div role="status" aria-live="polite" className="sr-only">
        {isLoading ? 'Loading results...' : `Found ${results.length} results`}
      </div>

      <div aria-live="off">
        {results.map(result => (
          <div key={result.id}>{result.title}</div>
        ))}
      </div>
    </>
  )
}
```

### ✅ Error Messages

```tsx
<div role="alert" aria-live="assertive">
  {error && <p>{error.message}</p>}
</div>
```

## Testing

### ✅ Automated Testing

```bash
# Install axe-core for React
npm install --save-dev @axe-core/react

# Use in development
```

```tsx
// index.tsx (development only)
if (process.env.NODE_ENV !== 'production') {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000)
  })
}
```

### ✅ Manual Testing Checklist

- [ ] Keyboard-only navigation works
- [ ] Screen reader announces content correctly
- [ ] Focus indicators visible
- [ ] Color contrast passes WCAG AA
- [ ] Forms have proper labels and error messages
- [ ] Images have appropriate alt text
- [ ] Headings create logical structure
- [ ] Interactive elements are keyboard accessible
- [ ] No keyboard traps
- [ ] Live regions announce updates
- [ ] Reduced motion respected

### ✅ Tools

- **Chrome DevTools Lighthouse**: Accessibility audit
- **axe DevTools**: Browser extension
- **WAVE**: Web accessibility evaluation tool
- **Screen readers**: NVDA (Windows), JAWS (Windows), VoiceOver (Mac/iOS)
- **Keyboard**: Tab, Shift+Tab, Enter, Space, Arrow keys, Escape

## Common Patterns

### Accordion

```tsx
<div>
  <button
    aria-expanded={isExpanded}
    aria-controls="panel-1"
    onClick={toggle}
  >
    Section Title
  </button>
  <div id="panel-1" hidden={!isExpanded}>
    Content
  </div>
</div>
```

### Tabs

```tsx
<div role="tablist" aria-label="Product tabs">
  <button
    role="tab"
    aria-selected={selectedTab === 'description'}
    aria-controls="description-panel"
    id="description-tab"
  >
    Description
  </button>
  {/* More tabs */}
</div>

<div
  role="tabpanel"
  id="description-panel"
  aria-labelledby="description-tab"
  hidden={selectedTab !== 'description'}
>
  Content
</div>
```

### Tooltip

```tsx
<button aria-describedby="tooltip-1">
  Help
</button>
<div id="tooltip-1" role="tooltip">
  Helpful information
</div>
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
