# State Management Patterns in React

**When to read this**: Choosing between useState, useContext, Zustand, React Query, or other state solutions for React applications.

**Quick answer**: Use useState for local state, React Query for server state, useContext for shared UI state (theme, auth status), and Zustand for complex client state. See [Decision Tree](#decision-tree-choosing-state-management) for details.

---

## Contents

- [Decision Tree](#decision-tree-choosing-state-management)
- [Local State (useState)](#local-state-usestate)
- [Shared State (useContext)](#shared-state-usecontext)
- [Complex Client State (Zustand)](#complex-client-state-zustand)
- [Server State (React Query)](#server-state-react-query)
- [Form State (React Hook Form)](#form-state-react-hook-form)
- [URL State (React Router)](#url-state-react-router)
- [Common Anti-Patterns](#common-anti-patterns)
- [Real-World Examples](#real-world-examples)
- [Migration Strategies](#migration-strategies)
- [Research Workflow](#research-workflow)
- [Quick Reference](#quick-reference)

---

## Decision Tree: Choosing State Management

```
What kind of state do you need?

├─ LOCAL to single component?
│  └─ useState / useReducer
│     Examples: Form inputs, toggle states, local UI

├─ SHARED across 2-3 components (same tree)?
│  ├─ Simple prop passing works? → Props
│  └─ Too much drilling? → useState + props or lift to parent

├─ SHARED across many components (app-wide)?
│  ├─ Simple values (theme, locale, auth status)? → useContext
│  └─ Complex state with updates? → Zustand or Jotai

├─ SERVER data (API, database)?
│  ├─ REST/GraphQL → React Query (TanStack Query)
│  ├─ Real-time → React Query + WebSockets
│  └─ Firebase → Firebase hooks

├─ FORM data?
│  ├─ Simple (1-3 fields) → useState
│  └─ Complex (validation, errors) → React Hook Form + Zod

└─ URL state (filters, pagination)?
   └─ React Router (useSearchParams)
```

---

## Local State (useState)

### When to Use

- **Component-specific state**: Values used only within one component
- **Simple values**: Booleans, strings, numbers, simple objects
- **No sharing needed**: Other components don't need access

### Pattern

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

### Advanced: useState with Objects

```typescript
interface FormData {
  name: string;
  email: string;
}

function Form() {
  const [form, setForm] = useState<FormData>({ name: '', email: '' });

  const updateField = (field: keyof FormData, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <>
      <input value={form.name} onChange={e => updateField('name', e.target.value)} />
      <input value={form.email} onChange={e => updateField('email', e.target.value)} />
    </>
  );
}
```

### When NOT to Use

- ❌ Server data (use React Query)
- ❌ Shared across many components (use Context or Zustand)
- ❌ Complex forms with validation (use React Hook Form)

---

## Shared State (useContext)

### When to Use

- **App-wide simple values**: Theme, locale, auth status
- **Rarely changing data**: User profile, app config
- **2-10 components need access**: Enough to justify Context, not so many that performance matters

### Pattern

```typescript
import { createContext, useContext, useState } from 'react';

// 1. Create context with type
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// 2. Create provider component
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Create custom hook for consuming
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// 4. Usage
function App() {
  return (
    <ThemeProvider>
      <Header />
      <Main />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();
  return <button onClick={toggleTheme}>Theme: {theme}</button>;
}
```

### Performance Optimization

**Problem**: Context re-renders all consumers when value changes.

**Solution**: Split contexts or use memoization.

```typescript
// ✅ SOLUTION 1 - Split into multiple contexts
const ThemeValueContext = createContext<'light' | 'dark'>('light');
const ThemeActionsContext = createContext<{ toggleTheme: () => void }>(null!);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const actions = useMemo(
    () => ({
      toggleTheme: () => setTheme(prev => (prev === 'light' ? 'dark' : 'light')),
    }),
    []
  );

  return (
    <ThemeValueContext.Provider value={theme}>
      <ThemeActionsContext.Provider value={actions}>
        {children}
      </ThemeActionsContext.Provider>
    </ThemeValueContext.Provider>
  );
}
```

### When NOT to Use

- ❌ Frequently updating state (causes re-renders)
- ❌ Large state objects (hard to optimize)
- ❌ Complex state logic (use Zustand)

---

## Complex Client State (Zustand)

### When to Use

- **Complex client state**: Shopping cart, user preferences, UI state
- **Frequent updates**: State changes often
- **Global access**: Many components need access
- **Performance matters**: Want to avoid Context re-render issues

### Installation

```bash
pnpm add zustand
```

### Pattern

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 1. Define state type
interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  total: number;
}

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

// 2. Create store
export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) =>
        set((state) => ({
          items: [...state.items, item],
        })),

      removeItem: (id) =>
        set((state) => ({
          items: state.items.filter((item) => item.id !== id),
        })),

      clearCart: () => set({ items: [] }),

      // Derived/computed state
      get total() {
        return get().items.reduce((sum, item) => sum + item.price * item.quantity, 0);
      },
    }),
    {
      name: 'cart-storage', // LocalStorage key
    }
  )
);

// 3. Usage (no Provider needed!)
function Cart() {
  const items = useCartStore((state) => state.items);
  const removeItem = useCartStore((state) => state.removeItem);
  const total = useCartStore((state) => state.total);

  return (
    <div>
      {items.map((item) => (
        <div key={item.id}>
          {item.name} - ${item.price}
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
      <p>Total: ${total}</p>
    </div>
  );
}
```

### Advantages over Context

- ✅ No Provider wrapper needed
- ✅ Selective subscription (only re-renders when selected state changes)
- ✅ DevTools support
- ✅ Middleware (persist, immer, devtools)
- ✅ TypeScript-friendly

### Slices Pattern (Large Stores)

```typescript
// Split large store into slices
interface UserSlice {
  user: User | null;
  setUser: (user: User) => void;
}

interface SettingsSlice {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

type AppState = UserSlice & SettingsSlice;

const createUserSlice = (set): UserSlice => ({
  user: null,
  setUser: (user) => set({ user }),
});

const createSettingsSlice = (set): SettingsSlice => ({
  theme: 'light',
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
});

export const useAppStore = create<AppState>()((...a) => ({
  ...createUserSlice(...a),
  ...createSettingsSlice(...a),
}));
```

---

## Server State (React Query)

### When to Use

- **Fetching data from APIs**: REST, GraphQL, WebSockets
- **Caching needed**: Avoid refetching same data
- **Background updates**: Refresh data automatically
- **Optimistic updates**: Update UI before server confirms

### Installation

```bash
pnpm add @tanstack/react-query @tanstack/react-query-devtools
```

### Setup

```typescript
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Basic Query Pattern

```typescript
import { useQuery } from '@tanstack/react-query';

interface User {
  id: string;
  name: string;
  email: string;
}

function UserProfile({ userId }: { userId: string }) {
  const {
    data: user,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

async function fetchUser(userId: string): Promise<User> {
  const res = await fetch(`/api/users/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch user');
  return res.json();
}
```

### Mutation Pattern

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateUserForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (newUser: { name: string; email: string }) =>
      fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      }).then((res) => res.json()),

    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    mutation.mutate({
      name: formData.get('name') as string,
      email: formData.get('email') as string,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create User'}
      </button>
      {mutation.isError && <p>Error: {mutation.error.message}</p>}
    </form>
  );
}
```

### Optimistic Updates

```typescript
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['todos'] });

    // Snapshot previous value
    const previousTodos = queryClient.getQueryData(['todos']);

    // Optimistically update
    queryClient.setQueryData(['todos'], (old: Todo[]) => [...old, newTodo]);

    // Return context with snapshot
    return { previousTodos };
  },
  onError: (err, newTodo, context) => {
    // Rollback on error
    queryClient.setQueryData(['todos'], context?.previousTodos);
  },
  onSettled: () => {
    // Refetch after success or error
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

---

## Form State (React Hook Form)

### When to Use

- **Complex forms**: 5+ fields, validation, conditional fields
- **Performance matters**: Large forms with many inputs
- **Integration needed**: Zod schema validation

### Installation

```bash
pnpm add react-hook-form zod @hookform/resolvers
```

### Pattern

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// 1. Define schema
const formSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type FormData = z.infer<typeof formSchema>;

// 2. Use in component
function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = async (data: FormData) => {
    await createUser(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('email')} placeholder="Email" />
        {errors.email && <p>{errors.email.message}</p>}
      </div>

      <div>
        <input {...register('password')} type="password" placeholder="Password" />
        {errors.password && <p>{errors.password.message}</p>}
      </div>

      <div>
        <input {...register('confirmPassword')} type="password" placeholder="Confirm" />
        {errors.confirmPassword && <p>{errors.confirmPassword.message}</p>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

---

## URL State (React Router)

### When to Use

- **Shareable state**: Filters, search, pagination
- **Bookmarkable**: Users should be able to bookmark the state
- **Browser history**: Back/forward button should work

### Pattern

```typescript
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();

  const category = searchParams.get('category') || 'all';
  const page = Number(searchParams.get('page')) || 1;

  const updateFilter = (newCategory: string) => {
    setSearchParams({ category: newCategory, page: '1' });
  };

  const nextPage = () => {
    setSearchParams({ category, page: String(page + 1) });
  };

  return (
    <div>
      <select value={category} onChange={(e) => updateFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
      </select>

      <ProductGrid category={category} page={page} />

      <button onClick={nextPage}>Next Page</button>
    </div>
  );
}
```

---

## Common Anti-Patterns

### ❌ Anti-Pattern 1: useState for Server Data

```typescript
// ❌ DON'T DO THIS
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchUser(userId)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  // Manual loading/error handling, no caching, no refetching...
}

// ✅ DO THIS - Use React Query
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });
  // Automatic caching, refetching, loading states!
}
```

### ❌ Anti-Pattern 2: Context for Everything

```typescript
// ❌ DON'T DO THIS - Massive context causes re-renders
const AppContext = createContext({
  user: null,
  cart: [],
  theme: 'light',
  locale: 'en',
  notifications: [],
  // ... 20 more fields
});

// ✅ DO THIS - Split contexts or use Zustand
const UserContext = createContext(null);
const ThemeContext = createContext('light');
const useCartStore = create((set) => ({ items: [], addItem: ... }));
```

### ❌ Anti-Pattern 3: Prop Drilling Instead of Context

```typescript
// ❌ DON'T DO THIS
function App() {
  const [theme, setTheme] = useState('light');
  return <Layout theme={theme} setTheme={setTheme} />;
}

function Layout({ theme, setTheme }) {
  return <Header theme={theme} setTheme={setTheme} />;
}

function Header({ theme, setTheme }) {
  return <ThemeToggle theme={theme} setTheme={setTheme} />;
}

// ✅ DO THIS - Use Context for 3+ levels
const ThemeContext = createContext(...);
// No prop drilling!
```

---

## Real-World Examples

### Example 1: E-Commerce Cart

**Requirements**: Add/remove items, persist across sessions, accessible from anywhere

**Solution**: Zustand with persist middleware

```typescript
export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addItem: (item) => set((state) => ({ items: [...state.items, item] })),
      removeItem: (id) => set((state) => ({ items: state.items.filter(i => i.id !== id) })),
    }),
    { name: 'cart-storage' }
  )
);
```

### Example 2: User Dashboard with API Data

**Requirements**: Fetch user data, cache it, refresh periodically

**Solution**: React Query

```typescript
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  refetchInterval: 1000 * 60, // Refresh every minute
});
```

---

## Migration Strategies

### From useState to React Query

```typescript
// BEFORE - useState
const [users, setUsers] = useState<User[]>([]);
useEffect(() => {
  fetchUsers().then(setUsers);
}, []);

// AFTER - React Query
const { data: users = [] } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
});
```

### From Context to Zustand

```typescript
// BEFORE - Context
const ThemeContext = createContext(...);

// AFTER - Zustand
export const useThemeStore = create((set) => ({
  theme: 'light',
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
}));
```

---

## Research Workflow

When uncertain about state management:

### 1. Don't Assume
State management best practices evolve. Redux dominated in 2018, but Zustand/React Query are preferred in 2025.

### 2. Use Context7 MCP for Official Documentation

```typescript
// Context7 for official docs
mcp__context7__get_library_docs({
  context7CompatibleLibraryID: "/tanstack/react-query",
  topic: "mutations and optimistic updates",
  tokens: 5000
})
```

### 3. Document Decisions
Update this guide when you discover new patterns.

---

## Quick Reference

| State Type | Solution | When to Use |
|------------|----------|-------------|
| Local (component-only) | `useState` | Toggle states, form inputs, local UI |
| Shared (2-3 components) | Props or `useState` + lift | Simple values passed down |
| Shared (app-wide, simple) | `useContext` | Theme, locale, auth status |
| Shared (app-wide, complex) | Zustand | Shopping cart, complex UI state |
| Server data | React Query | API calls, caching, background sync |
| Form data (complex) | React Hook Form + Zod | Multi-field forms with validation |
| URL state | React Router (`useSearchParams`) | Filters, pagination, search |

---

## Related Resources

- See `reference/code-quality-tooling.md` for TypeScript state typing
- See `reference/dynamic-styling-patterns.md` for theme state patterns
- Official React Query docs: https://tanstack.com/query/latest
- Zustand docs: https://zustand-demo.pmnd.rs/
- React Hook Form: https://react-hook-form.com/
