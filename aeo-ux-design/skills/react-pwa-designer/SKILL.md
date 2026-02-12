---
name: react-pwa-designer
description: Architect modern React progressive web apps with offline-first capabilities and responsive interfaces. Integrates shadcn/ui component library, service worker patterns, and mobile-friendly layouts. Consult when building installable web applications or designing component-driven UIs.
---

# React PWA Designer

Design and build modern React progressive web applications using SuperDesign methodology, shadcn/ui components, and React best practices.

## When to Use This Skill

Trigger this skill when the user requests:
- Designing or building React applications
- Creating progressive web apps (PWAs)
- Implementing shadcn/ui components
- Building modern, responsive web interfaces
- Creating React component libraries
- Designing with Tailwind CSS and modern design systems
- Converting designs to React components

## Reference File Index

### Getting Started
- [README.md](README.md) - Complete skill overview
- @reference/setup-guide.md - Project initialization, dependencies, configuration
- [templates/.superdesign/README.md](templates/.superdesign/README.md) - SuperDesign directory usage

### React Patterns
- @reference/react-hooks.md - Custom hooks and patterns
- @reference/component-patterns.md - Component architecture, compound components, render props
- @reference/state-management-patterns.md - useState vs Context vs Zustand vs React Query

### Styling & Layout
- @reference/dynamic-styling-patterns.md - CSS Variables, Tailwind, inline styles
- @reference/layout-patterns.md - Flex scrolling, grid, responsive design, text overflow
- @reference/shadcn-components.md - shadcn/ui integration (check BEFORE MCP calls)

### PWA
- @reference/pwa-checklist.md - PWA requirements checklist
- @reference/pwa-icon-validation.md - Icon validation (CRITICAL - read before generating icons!)
- @reference/pwa-troubleshooting.md - Installation, service worker, offline issues

### Quality
- @reference/code-quality-tooling.md - ESLint, TypeScript, Prettier configuration
- @reference/common-pitfalls.md - Anti-patterns to avoid
- @reference/accessibility.md - WCAG AA patterns and examples
- @reference/implementation-examples.md - Complete code examples (Dashboard, Auth Flow)

### Templates
- [templates/vite.config.ts](templates/vite.config.ts) - Vite + PWA configuration
- [templates/tailwind.config.js](templates/tailwind.config.js) - Tailwind CSS setup
- [templates/tsconfig.json](templates/tsconfig.json) - TypeScript configuration
- [templates/manifest.json](templates/manifest.json) - PWA manifest template
- `templates/component-boilerplate.tsx` - React component template
- `templates/custom-hook-template.ts` - Custom hook structure
- `templates/service-worker.ts` - Manual service worker implementation

## SuperDesign Workflow

Four-phase methodology. **Get user approval before proceeding at each phase.**

### Phase 1: Discovery & Planning

1. **Understand Requirements** - App purpose, target users, PWA needs (offline, installable, notifications)
2. **Component Discovery** - Use `mcp__shadcn__getComponents()` and `mcp__shadcn__getComponent()` to identify matching components
3. **Architecture Planning** - Component hierarchy, state management, routing, data fetching

### Phase 2: Design

**Reference**: See [SuperDesign.md](SuperDesign.md) for complete methodology.

1. **Layout Design** - ASCII wireframes showing component structure and responsive breakpoints
2. **Theme Design** - MUST use tool calls (never text output), save to `.superdesign/design_iterations/theme_[n].css`
3. **Animation Design** - Micro-syntax specs for transitions, loading states, interactions
4. **Component Implementation** - Compose from shadcn primitives with proper TypeScript types

### Phase 3: PWA Implementation

1. **Icons** - MUST READ @reference/pwa-icon-validation.md first (dimension mismatches = silent install failure)
2. **Manifest** - Use `templates/manifest.json` as starting point
3. **Service Worker** - Vite PWA Plugin (recommended) or manual via `templates/service-worker.ts`
4. **Verify** - See @reference/pwa-checklist.md for complete requirements

### Phase 4: Development

- **React patterns** → @reference/react-hooks.md, @reference/component-patterns.md
- **State management** → @reference/state-management-patterns.md
- **TypeScript & linting** → @reference/code-quality-tooling.md
- **Performance** - React.memo, virtualization, code splitting, bundle monitoring
- **Troubleshooting** → @reference/pwa-troubleshooting.md

### Session Scoping

- Limit to 15-20 files maximum per session
- Focus on single feature or component per iteration
- Complete cycle: Implementation → Tests → Commit before next scope

## Tool Usage Decision Tree

```
Need component info?
├─ Common component details → Check @reference/shadcn-components.md FIRST
├─ Detailed implementation/variants → mcp__shadcn__getComponent("name")
└─ List all available components → mcp__shadcn__getComponents()

Need library documentation?
├─ React hooks/patterns → Check @reference/react-hooks.md FIRST
├─ State management → Check @reference/state-management-patterns.md FIRST
├─ Styling decisions → Check @reference/dynamic-styling-patterns.md FIRST
├─ PWA requirements → Check @reference/pwa-checklist.md FIRST
├─ Need official/latest docs → mcp__context7__resolve_library_id() then get_library_docs()
└─ Common Context7 libraries:
   /facebook/react, /vite-pwa/vite-plugin-pwa, /GoogleChrome/workbox,
   /tanstack/react-query, /pmndrs/zustand, /shadcn/ui
```

**Rule**: Always check reference files before MCP calls to save tokens.

## Quick Decision Trees

### Component Selection

```
Need interactive element?
├─ Button/action → <Button>
├─ Link/navigation → <Link> or <a>
├─ Input field → <Input> or <Textarea>
├─ Toggle → <Switch> or <Checkbox>
└─ Selection → <Select> or <RadioGroup>

Need layout container?
├─ Content box → <Card>
├─ Modal → <Dialog>
├─ Side panel → <Sheet>
├─ Dropdown → <DropdownMenu>
└─ Sections → <Tabs> or <Accordion>

Need feedback?
├─ Loading → <Skeleton> or <Progress>
├─ Notification → <Toast> or <Alert>
├─ Hint → <Tooltip>
└─ Confirmation → <AlertDialog>
```

### State Management

```
What kind of state?
├─ Local to component → useState
├─ Shared (2-3 components) → Props or useContext
├─ Complex app state → Zustand or Jotai
├─ Server data → React Query or SWR
└─ Form state → React Hook Form + Zod
```

## Critical Reminders

1. **ALWAYS use actual tool calls** - Never output "Called tool: ..." as text
2. **Get user approval** at each workflow step before proceeding
3. **Use tool calls for theme generation** - Never output CSS as text
4. **Save to .superdesign/design_iterations/** for all design artifacts
5. **Check reference files before MCP** for component details
6. **Follow React best practices** - hooks, TypeScript, composition
7. **PWA icons MUST match manifest exactly** - see @reference/pwa-icon-validation.md
8. **Avoid bootstrap blue colors** - use modern design systems
9. **Mobile-first responsive** - always design for smallest screen first
10. **Accessibility required** - ARIA labels, keyboard nav, semantic HTML, WCAG AA contrast
