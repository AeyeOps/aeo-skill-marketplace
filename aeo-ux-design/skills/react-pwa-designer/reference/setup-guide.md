# Setup Guide & Dependencies

**When to read this**: Starting a new React PWA project or adding dependencies.

**Quick answer**: See [Required Packages](#required-packages) for minimal setup.

---

## Contents

- [Required Packages](#required-packages)
- [Optional Enhancement Packages](#optional-enhancement-packages)
- [Installation Steps](#installation-steps)
- [Configuration Files](#configuration-files)

---

## Required Packages

Minimal dependencies for a React + shadcn/ui + PWA project:

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Core Dependencies Explained

| Package | Purpose |
|---------|---------|
| `react` + `react-dom` | React core libraries |
| `react-router-dom` | Client-side routing |
| `class-variance-authority` | shadcn/ui variant styling |
| `clsx` + `tailwind-merge` | Conditional className merging (`cn()` utility) |
| `lucide-react` | Icon library (used by shadcn/ui) |

### Dev Dependencies Explained

| Package | Purpose |
|---------|---------|
| `@types/react` + `@types/react-dom` | TypeScript type definitions |
| `typescript` | TypeScript compiler |
| `vite` | Build tool and dev server |
| `tailwindcss` | CSS framework |
| `autoprefixer` + `postcss` | CSS post-processing |

---

## Optional Enhancement Packages

Add these based on project needs:

### Forms & Validation

```json
{
  "dependencies": {
    "react-hook-form": "^7.51.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0"
  }
}
```

**Install:**
```bash
pnpm add react-hook-form zod @hookform/resolvers
```

### State Management

```json
{
  "dependencies": {
    "zustand": "^4.5.0",
    // OR
    "jotai": "^2.7.0"
  }
}
```

**Install:**
```bash
# Zustand (recommended for most apps)
pnpm add zustand

# Jotai (for atomic state)
pnpm add jotai
```

### Server State (Data Fetching)

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.28.0",
    // OR
    "swr": "^2.2.0"
  }
}
```

**Install:**
```bash
# React Query (recommended for REST/GraphQL)
pnpm add @tanstack/react-query

# SWR (lightweight alternative)
pnpm add swr
```

### Animations

```json
{
  "dependencies": {
    "framer-motion": "^11.0.0"
  }
}
```

**Install:**
```bash
pnpm add framer-motion
```

### PWA

```json
{
  "devDependencies": {
    "vite-plugin-pwa": "^0.19.0",
    "workbox-window": "^7.0.0"
  }
}
```

**Install:**
```bash
pnpm add -D vite-plugin-pwa workbox-window
```

### Testing

```json
{
  "devDependencies": {
    "vitest": "^1.4.0",
    "@testing-library/react": "^14.2.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
```

**Install:**
```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

---

## Installation Steps

### 1. Create New Vite Project

```bash
pnpm create vite my-app --template react-ts
cd my-app
pnpm install
```

### 2. Install Tailwind CSS

```bash
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Install shadcn/ui

```bash
pnpm dlx shadcn@latest init
```

This prompts for:
- TypeScript: Yes
- Style: Default
- Base color: Slate (or your preference)
- CSS variables: Yes

### 4. Add Components

```bash
# Add individual components as needed
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add card
pnpm dlx shadcn@latest add input
# etc.
```

### 5. Install Optional Packages

```bash
# Forms
pnpm add react-hook-form zod @hookform/resolvers

# State management
pnpm add zustand

# Server state
pnpm add @tanstack/react-query

# PWA
pnpm add -D vite-plugin-pwa
```

---

## Configuration Files

### vite.config.ts

See `templates/vite.config.ts` for complete PWA configuration.

Basic setup:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### tailwind.config.js

See `templates/tailwind.config.js` for shadcn/ui configuration.

Basic setup:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### tsconfig.json

See `templates/tsconfig.json` for complete TypeScript configuration.

Key settings:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Package Management Notes

### Using pnpm (Recommended)

**Why pnpm:**
- Faster installation
- More efficient disk usage (content-addressable storage)
- Strict dependency resolution (avoids phantom dependencies)

**Common commands:**
```bash
pnpm install           # Install all dependencies
pnpm add <pkg>         # Add production dependency
pnpm add -D <pkg>      # Add dev dependency
pnpm remove <pkg>      # Remove dependency
pnpm update            # Update all dependencies
```

### Avoiding npm/yarn

Per project guidelines (CLAUDE.md), always use `pnpm`:

```bash
# ❌ Don't use
npm install
yarn add

# ✅ Use instead
pnpm install
pnpm add
```

---

## Related Resources

- See `templates/vite.config.ts` for full Vite + PWA configuration
- See `templates/tailwind.config.js` for Tailwind + shadcn setup
- See `templates/tsconfig.json` for TypeScript configuration
- See `pwa-checklist.md` for PWA-specific requirements
