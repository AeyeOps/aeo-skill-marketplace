# React PWA Designer Skill

A comprehensive Claude Code skill for building modern React progressive web applications with production-quality UI design.

## Overview

This skill combines:
- **SuperDesign Methodology** - 4-step design workflow (Layout → Theme → Animation → Implementation)
- **shadcn/ui Integration** - Leverages shadcn MCP for component discovery and implementation
- **React Best Practices** - TypeScript, hooks, composition patterns, state management
- **PWA Excellence** - Offline support, service workers, installability, performance optimization

## Activation Triggers

Claude will automatically activate this skill when users request:
- React application design or development
- Progressive Web App (PWA) features
- shadcn/ui component implementation
- Modern responsive web interfaces
- Component library creation
- Tailwind CSS design systems

## Workflow Phases

### 1. Discovery & Planning
- Requirements gathering
- Component discovery via `mcp__shadcn__getComponents()`
- Architecture planning (state, routing, data fetching)

### 2. Design (SuperDesign)
1. **Layout** - ASCII wireframes with shadcn component mapping
2. **Theme** - CSS variable generation (shadcn-compatible)
3. **Animation** - Micro-interaction specs
4. **Implementation** - React + TypeScript components

### 3. PWA Implementation
- Web manifest configuration
- Service worker strategies
- Offline functionality
- Performance optimization

### 4. Best Practices
- React patterns and hooks
- TypeScript integration
- Accessibility (WCAG AA)
- Performance benchmarks

## Key Features

### Tool Integration
- **shadcn MCP**: `mcp__shadcn__getComponents()` and `mcp__shadcn__getComponent()`
- **SuperDesign Tools**: Theme generation, file management

### Design Philosophy
- Mobile-first responsive design
- Accessibility by default
- Modern color systems (no bootstrap blue!)
- Performance-optimized (Lighthouse > 90)
- Progressive enhancement

### Component Structure
```
src/
├── components/
│   ├── ui/              # shadcn components
│   ├── features/        # Feature components
│   └── layouts/         # Layout components
├── hooks/               # Custom hooks
├── lib/utils.ts         # Utilities
└── styles/globals.css   # Theme CSS
```

## State Management Decision Tree

```
Simple local state → useState
Shared state (few components) → useContext
Complex shared state → Zustand/Jotai
Server state → React Query/SWR
Forms → React Hook Form + Zod
```

## Performance Targets

- ✅ Lighthouse score > 90
- ✅ First Contentful Paint < 1.8s
- ✅ Largest Contentful Paint < 2.5s
- ✅ Time to Interactive < 3.8s
- ✅ Cumulative Layout Shift < 0.1

## Accessibility Standards

- WCAG AA compliance (4.5:1 contrast)
- Keyboard navigation support
- Screen reader compatibility
- Semantic HTML structure
- Reduced motion support

## Example Use Cases

1. **Dashboard Applications** - Data tables, charts, filtering
2. **Authentication Flows** - Login, signup, password reset
3. **E-commerce** - Product catalogs, shopping carts, checkout
4. **Content Management** - WYSIWYG editors, media libraries
5. **Admin Panels** - Settings, user management, analytics

## Dependencies

### Core
- React 18.3+
- TypeScript 5.3+
- Tailwind CSS 3.4+
- shadcn/ui components
- Vite 5.1+

### Recommended
- react-hook-form + zod (forms)
- @tanstack/react-query (server state)
- zustand/jotai (client state)
- framer-motion (animations)
- vite-plugin-pwa (PWA)

## File Organization

Design artifacts saved to `.superdesign/design_iterations/`:
- `{project}_layout_1.txt` - ASCII wireframes
- `{project}_theme_1.css` - Theme CSS
- `{project}_animations_1.md` - Animation specs
- `{project}_v1.tsx` - Components

## Critical Rules

1. ✅ Always use actual tool calls (never text output)
2. ✅ Get user approval at each workflow step
3. ✅ Check shadcn MCP before implementation
4. ✅ Follow mobile-first responsive design
5. ✅ Maintain accessibility standards
6. ✅ Optimize for performance

## Compatibility

### Required Versions

| Dependency | Minimum Version | Recommended |
|------------|-----------------|-------------|
| **Node.js** | 18.0.0 | 20.x LTS |
| **React** | 18.3.0 | 18.3.1+ |
| **TypeScript** | 5.3.0 | 5.4.x+ |
| **Vite** | 5.1.0 | 5.2.x+ |
| **Tailwind CSS** | 3.4.0 | 3.4.x+ |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react-hook-form | ^7.50.0 | Form state management |
| zod | ^3.22.0 | Schema validation |
| @tanstack/react-query | ^5.0.0 | Server state management |
| zustand | ^4.5.0 | Client state management |
| framer-motion | ^11.0.0 | Animations |
| vite-plugin-pwa | ^0.19.0 | PWA support |

### Browser Support

**Modern Browsers** (Last 2 versions):
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ iOS Safari 14+
- ✅ Samsung Internet 14+

**PWA Features**:
- ✅ Service Workers: Chrome, Edge, Firefox, Safari 11.1+
- ⚠️ Install Prompt: Chrome, Edge (Safari requires manual add to home screen)
- ✅ Offline: All modern browsers with service worker support

## Version History

### v1.0.0 (2025-10-19)
**Initial Release**

- ✅ Complete SuperDesign methodology integration
- ✅ shadcn/ui MCP tool support
- ✅ React + TypeScript best practices
- ✅ PWA implementation guide
- ✅ 5 comprehensive reference files (progressive disclosure)
- ✅ 6 ready-to-use templates
- ✅ Accessibility (WCAG AA) patterns
- ✅ Troubleshooting guide with 6 common issues
- ✅ State management decision trees
- ✅ Performance optimization checklist

**Structure**:
- SKILL.md (main skill file)
- SuperDesign.md (design methodology reference)
- README.md (documentation)
- reference/ (5 markdown files)
- templates/ (6 boilerplate files)

## Skill Metadata

- **Created**: 2025-10-19
- **Format**: Claude Code Skill (directory-based)
- **Architecture**: Progressive disclosure (Anthropic best practices)
- **Total Files**: 14
- **Token Efficiency**: High (reference files loaded only when needed)
