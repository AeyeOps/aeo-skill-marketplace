# Code Quality Tooling: Linting & Type Hygiene

**When to read this**: Setting up or troubleshooting ESLint, TypeScript, Prettier, or resolving type/lint errors in React + PWA projects.

**Quick answer**: Use TypeScript strict mode + ESLint with React/a11y plugins + Prettier + lint-staged. See [Recommended Configuration](#recommended-configuration) for copy-paste setup.

---

## Contents

- [Decision Tree](#decision-tree-choosing-your-tooling-setup)
- [Recommended Configuration](#recommended-configuration)
- [TypeScript Configuration Hygiene](#typescript-configuration-hygiene)
- [ESLint Configuration](#eslint-configuration)
- [Prettier Integration](#prettier-integration)
- [Pre-commit Hooks](#pre-commit-hooks-husky--lint-staged)
- [Common Type Errors & Solutions](#common-type-errors--solutions)
- [Linting for PWA-Specific Concerns](#linting-for-pwa-specific-concerns)
- [CI/CD Integration](#cicd-integration)
- [Real-World Examples](#real-world-examples)
- [Research Workflow](#research-workflow)
- [Quick Reference](#quick-reference)

---

## Decision Tree: Choosing Your Tooling Setup

```
Starting a new React + PWA project?
│
├─ TypeScript? (Strongly recommended)
│  ├─ Yes → Use strict mode + path aliases
│  └─ No → Consider migrating (better DX, fewer bugs)
│
├─ Linting strategy?
│  ├─ Minimal → ESLint + @typescript-eslint/recommended
│  ├─ Standard → Add react-hooks + jsx-a11y
│  └─ Strict → Add Airbnb config or custom strict rules
│
├─ Code formatting?
│  └─ Always → Prettier with ESLint integration
│
└─ Pre-commit enforcement?
   ├─ Solo project → Optional (but recommended)
   └─ Team project → Required (Husky + lint-staged)
```

---

## Recommended Configuration

### Complete Setup (Copy-Paste Ready)

**1. Install dependencies**:
```bash
pnpm add -D typescript @types/react @types/react-dom
pnpm add -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
pnpm add -D eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier
pnpm add -D husky lint-staged
```

**2. TypeScript config** (`tsconfig.json`):
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting - STRICT MODE */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "noUncheckedIndexedAccess": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**3. ESLint config** (`.eslintrc.cjs`):
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:prettier/recommended', // Must be last
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-unused-vars': [
      'error',
      { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
    ],
    'react/prop-types': 'off', // Using TypeScript
    'no-console': ['warn', { allow: ['warn', 'error'] }],
  },
}
```

**4. Prettier config** (`.prettierrc`):
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**5. Husky + lint-staged** (`package.json`):
```json
{
  "scripts": {
    "prepare": "husky install",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

**6. Initialize Husky**:
```bash
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

---

## TypeScript Configuration Hygiene

### Strict Mode Settings (Recommended)

```json
{
  "compilerOptions": {
    "strict": true,              // Enable all strict checks
    "noImplicitAny": true,       // No implicit 'any' types
    "strictNullChecks": true,    // Null/undefined must be explicit
    "strictFunctionTypes": true, // Function param contravariance
    "strictBindCallApply": true, // Strict bind/call/apply
    "noImplicitThis": true,      // 'this' must have explicit type
    "alwaysStrict": true,        // Emit "use strict"

    // Additional safety
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true  // Array/object access returns T | undefined
  }
}
```

### Path Aliases Setup

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@utils/*": ["./src/lib/utils/*"]
    }
  }
}
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/lib/utils'),
    },
  },
})
```

### React-Specific Type Patterns

**Component Props**:
```typescript
// ✅ CORRECT - Interface for props
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

// ✅ CORRECT - Function component (not React.FC)
export function Button({ variant = 'primary', size = 'md', ...props }: ButtonProps) {
  return <button {...props} />
}

// ❌ AVOID - React.FC (deprecated pattern)
export const Button: React.FC<ButtonProps> = ({ variant, size, ...props }) => {
  return <button {...props} />
}
```

**Event Handlers**:
```typescript
// ✅ CORRECT - Typed event handlers
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.preventDefault();
};

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  console.log(e.target.value);
};

const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
};
```

**Generic Components**:
```typescript
// ✅ CORRECT - Generic component
interface SelectProps<T> {
  options: T[];
  value: T;
  onChange: (value: T) => void;
  renderOption: (option: T) => React.ReactNode;
}

export function Select<T>({ options, value, onChange, renderOption }: SelectProps<T>) {
  return (
    <select onChange={(e) => onChange(options[Number(e.target.value)])}>
      {options.map((option, index) => (
        <option key={index} value={index}>
          {renderOption(option)}
        </option>
      ))}
    </select>
  );
}
```

---

## ESLint Configuration

### Recommended Rule Set

```javascript
// .eslintrc.cjs
module.exports = {
  rules: {
    // TypeScript
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-module-boundary-types': 'off',

    // React
    'react/prop-types': 'off', // Using TypeScript
    'react/react-in-jsx-scope': 'off', // React 17+ automatic
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // Accessibility
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/aria-props': 'error',
    'jsx-a11y/aria-role': 'error',
    'jsx-a11y/click-events-have-key-events': 'warn',

    // General
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'prefer-const': 'error',
    'no-var': 'error',
  },
}
```

### PWA-Specific ESLint Rules

```javascript
// Custom rule for service worker scope
module.exports = {
  overrides: [
    {
      files: ['**/service-worker.ts', '**/sw.ts'],
      rules: {
        'no-restricted-globals': ['error', 'document', 'window', 'localStorage'],
        '@typescript-eslint/no-unused-vars': 'off', // addEventListener params
      },
      env: {
        serviceworker: true,
        browser: false,
      },
    },
  ],
}
```

---

## Prettier Integration

### ESLint + Prettier Cooperation

**Install**:
```bash
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier
```

**ESLint config** (must be last in extends):
```javascript
module.exports = {
  extends: [
    // ... other configs
    'plugin:prettier/recommended', // ← Must be last!
  ],
}
```

### VS Code Integration

**`.vscode/settings.json`**:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Pre-commit Hooks (Husky + lint-staged)

### Setup

**1. Install**:
```bash
pnpm add -D husky lint-staged
npx husky install
```

**2. Add pre-commit hook**:
```bash
npx husky add .husky/pre-commit "npx lint-staged"
```

**3. Configure lint-staged** (`package.json`):
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,css}": [
      "prettier --write"
    ]
  }
}
```

### Performance Optimization

**Only check staged files** (not entire codebase):
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix --max-warnings 0",
      "prettier --write",
      "bash -c 'tsc --noEmit'"  // Type check only staged
    ]
  }
}
```

---

## Common Type Errors & Solutions

### Quick Reference Table

| Error | Cause | Solution |
|-------|-------|----------|
| `Object is possibly 'null'` | Not checking for null | Add null check: `if (obj) { ... }` or `obj?.property` |
| `Object is possibly 'undefined'` | Optional property access | Use optional chaining: `obj?.prop` or nullish coalescing: `obj ?? default` |
| `Type 'X' is not assignable to type 'Y'` | Type mismatch | Fix type definition or use type assertion: `value as Type` |
| `Property 'foo' does not exist on type` | Missing type definition | Add to interface or use type assertion |
| `Argument of type 'unknown'` | Type not inferred from catch/API | Add explicit type: `error as Error` |
| `Element implicitly has an 'any' type` | No index signature | Add index signature: `[key: string]: T` or use `Record<string, T>` |

### Detailed Solutions

**1. Object is possibly null/undefined**:
```typescript
// ❌ ERROR
const user = users.find(u => u.id === id);
console.log(user.name); // Error: Object is possibly 'undefined'

// ✅ SOLUTION 1 - Null check
const user = users.find(u => u.id === id);
if (user) {
  console.log(user.name);
}

// ✅ SOLUTION 2 - Optional chaining
console.log(user?.name);

// ✅ SOLUTION 3 - Non-null assertion (use sparingly!)
console.log(user!.name); // Only if you're 100% sure it exists
```

**2. Array/Object index access**:
```typescript
// With noUncheckedIndexedAccess: true
const items = ['a', 'b', 'c'];
const first = items[0]; // Type: string | undefined

// ✅ SOLUTION - Check before use
if (first) {
  console.log(first.toUpperCase());
}
```

**3. Event types**:
```typescript
// ❌ ERROR
const handleClick = (e) => { // Parameter 'e' implicitly has 'any' type
  console.log(e.target.value);
};

// ✅ SOLUTION
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log(e.currentTarget.value);
};
```

**4. Async errors in catch blocks**:
```typescript
// ❌ PROBLEM
try {
  await fetchData();
} catch (error) {
  console.log(error.message); // Error: 'error' is of type 'unknown'
}

// ✅ SOLUTION 1 - Type guard
try {
  await fetchData();
} catch (error) {
  if (error instanceof Error) {
    console.log(error.message);
  }
}

// ✅ SOLUTION 2 - Type assertion (less safe)
try {
  await fetchData();
} catch (error) {
  console.log((error as Error).message);
}
```

---

## Linting for PWA-Specific Concerns

### Service Worker Linting

**Prevent DOM access in service workers**:
```javascript
// .eslintrc.cjs
module.exports = {
  overrides: [
    {
      files: ['**/service-worker.ts', '**/sw.ts'],
      env: {
        serviceworker: true,
        browser: false, // ← Prevents DOM globals
      },
      rules: {
        'no-restricted-globals': [
          'error',
          'document',
          'window',
          'localStorage',
          'sessionStorage',
        ],
      },
    },
  ],
}
```

### Manifest.json Validation

**Use JSON schema validation**:
```bash
pnpm add -D @types/web-app-manifest
```

```typescript
// manifest.ts
import type { WebAppManifest } from '@types/web-app-manifest';

export const manifest: WebAppManifest = {
  name: 'My PWA',
  short_name: 'PWA',
  // TypeScript ensures all fields are valid!
};
```

### Accessibility Linting

**jsx-a11y essential rules**:
```javascript
module.exports = {
  extends: ['plugin:jsx-a11y/recommended'],
  rules: {
    'jsx-a11y/alt-text': 'error', // Images must have alt
    'jsx-a11y/aria-role': 'error', // Valid ARIA roles
    'jsx-a11y/click-events-have-key-events': 'warn', // Keyboard support
    'jsx-a11y/no-static-element-interactions': 'warn',
  },
}
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - run: pnpm install

      - name: Type check
        run: pnpm type-check

      - name: Lint
        run: pnpm lint

      - name: Build
        run: pnpm build
```

### Fail Build on Errors

```json
// package.json
{
  "scripts": {
    "lint": "eslint . --ext ts,tsx --max-warnings 0",
    "type-check": "tsc --noEmit",
    "ci": "pnpm type-check && pnpm lint && pnpm build"
  }
}
```

---

## Real-World Examples

### Example 1: The Exhaustive Deps Warning

**Problem**: React Hook useEffect has a missing dependency

```typescript
// ❌ WARNING
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []); // ← Warning: missing 'userId' dependency
}
```

**Solutions**:

```typescript
// ✅ SOLUTION 1 - Add dependency
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);

// ✅ SOLUTION 2 - Disable if intentional (rare!)
useEffect(() => {
  fetchUser(userId).then(setUser);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);

// ✅ SOLUTION 3 - Extract to ref if needed
const userIdRef = useRef(userId);
useEffect(() => {
  fetchUser(userIdRef.current).then(setUser);
}, []);
```

### Example 2: The Type Import Problem

**Problem**: When to use `import type` vs `import`

```typescript
// ❌ INEFFICIENT - Imports at runtime
import { User } from './types';

// ✅ CORRECT - Type-only import (erased at compile time)
import type { User } from './types';

// ✅ MIXED - Import both value and type
import { createUser, type User } from './api';
```

**ESLint rule** to enforce:
```javascript
module.exports = {
  rules: {
    '@typescript-eslint/consistent-type-imports': [
      'error',
      { prefer: 'type-imports' },
    ],
  },
}
```

---

## Research Workflow

When uncertain about tooling configurations:

### 1. Don't Assume
Tooling evolves rapidly. ESLint rules from 2023 may be deprecated in 2025.

### 2. Use Context7 MCP for Official Documentation

```typescript
// Context7 for official docs
mcp__context7__get_library_docs({
  context7CompatibleLibraryID: "/typescript-eslint/typescript-eslint",
  topic: "recommended configurations",
  tokens: 5000
})
```

### 3. Query Patterns
- "What are the 2025 best practices for [ESLint/TypeScript/Prettier] in React?"
- "How to configure [tool] for [use case]?"
- "Common [TypeScript/ESLint] errors in React and solutions"

### 4. Document Decisions
Update this guide when you discover new patterns or deprecated practices.

---

## Quick Reference

### Essential Commands

```bash
# Type check
pnpm type-check

# Lint
pnpm lint

# Lint and fix
pnpm lint --fix

# Format
pnpm format

# Run all checks
pnpm type-check && pnpm lint && pnpm build
```

### VS Code Extensions

- **ESLint** (dbaeumer.vscode-eslint)
- **Prettier** (esbenp.prettier-vscode)
- **Error Lens** (usernamehw.errorlens) - Inline errors

### Troubleshooting Checklist

- [ ] TypeScript installed? (`pnpm list typescript`)
- [ ] ESLint config present? (`.eslintrc.cjs` or `.eslintrc.json`)
- [ ] Prettier config present? (`.prettierrc`)
- [ ] Path aliases in both `tsconfig.json` and `vite.config.ts`?
- [ ] ESLint + Prettier not conflicting? (`eslint-config-prettier` installed)
- [ ] VS Code using workspace TypeScript? (Check bottom-right status bar)
- [ ] Node modules installed? (`pnpm install`)

---

## Related Resources

- See `reference/dynamic-styling-patterns.md` for CSS/styling type safety
- See `reference/state-management-patterns.md` for state typing strategies
- Official TypeScript docs: https://www.typescriptlang.org/
- TypeScript ESLint: https://typescript-eslint.io/
- ESLint Rules: https://eslint.org/docs/latest/rules/
