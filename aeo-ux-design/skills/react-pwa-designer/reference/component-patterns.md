# Component Patterns

**When to read this**: Building React components and need common compositional patterns.

**Quick answer**: See the pattern that matches your architecture below.

---

## Contents

- [Feature-First Component Structure](#feature-first-component-structure)
- [shadcn + Custom Component Extension](#shadcn--custom-component-extension)
- [Data Fetching Hook Pattern](#data-fetching-hook-pattern)
- [Compound Component Pattern](#compound-component-pattern)
- [Render Props Pattern](#render-props-pattern)

---

## Feature-First Component Structure

**When to use**: Organizing code by feature rather than by file type.

**Benefits**:
- Colocates related files (components, hooks, API)
- Easier to find feature-specific code
- Better for large applications
- Supports feature flags and lazy loading

### Directory Structure

```
features/
├── auth/
│   ├── components/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── PasswordReset.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useSession.ts
│   └── api/
│       └── authApi.ts
└── dashboard/
    ├── components/
    │   ├── DashboardLayout.tsx
    │   ├── MetricCard.tsx
    │   └── ActivityFeed.tsx
    ├── hooks/
    │   └── useDashboardData.ts
    └── api/
        └── dashboardApi.ts
```

### Example Implementation

```typescript
// features/auth/hooks/useAuth.ts
import { useState } from "react"
import { authApi } from "../api/authApi"

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  async function login(email: string, password: string) {
    setLoading(true)
    try {
      const user = await authApi.login({ email, password })
      setUser(user)
      return user
    } finally {
      setLoading(false)
    }
  }

  return { user, loading, login }
}

// features/auth/components/LoginForm.tsx
import { useAuth } from "../hooks/useAuth"

export function LoginForm() {
  const { login, loading } = useAuth()
  // Form implementation...
}
```

---

## shadcn + Custom Component Extension

**When to use**: Need to add custom styling or behavior to shadcn components.

**Pattern**: Wrap shadcn components and add custom variants.

### Example: Gradient Button

```typescript
import { Button, ButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function GradientButton({ className, ...props }: ButtonProps) {
  return (
    <Button
      className={cn(
        "bg-gradient-to-r from-purple-500 to-pink-500",
        "hover:from-purple-600 hover:to-pink-600",
        "transition-all duration-300",
        className
      )}
      {...props}
    />
  )
}
```

### Example: Icon Button

```typescript
import { Button, ButtonProps } from "@/components/ui/button"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface IconButtonProps extends ButtonProps {
  icon: LucideIcon
  label: string
}

export function IconButton({
  icon: Icon,
  label,
  className,
  ...props
}: IconButtonProps) {
  return (
    <Button
      className={cn("flex items-center gap-2", className)}
      {...props}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Button>
  )
}
```

### Example: Animated Card

```typescript
import { Card, CardProps } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export function AnimatedCard({ className, ...props }: CardProps) {
  return (
    <Card
      className={cn(
        "transition-all duration-200",
        "hover:shadow-lg hover:-translate-y-1",
        "cursor-pointer",
        className
      )}
      {...props}
    />
  )
}
```

---

## Data Fetching Hook Pattern

**When to use**: Fetching data from APIs with React Query or SWR.

**Benefits**:
- Automatic caching and revalidation
- Loading and error states handled
- Optimistic updates
- Polling and refetching

### React Query Pattern

```typescript
import { useQuery } from '@tanstack/react-query'

export function useUserData(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useUserData(userId)

  if (isLoading) return <Skeleton />
  if (error) return <ErrorMessage error={error} />

  return <div>{data.name}</div>
}
```

### Mutation Pattern

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'

export function useUpdateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (user: User) => updateUser(user),
    onSuccess: (data, variables) => {
      // Invalidate and refetch user queries
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] })
    },
    onError: (error) => {
      // Handle error (toast notification, etc.)
    }
  })
}

// Usage
function EditUserForm({ user }: { user: User }) {
  const { mutate, isPending } = useUpdateUser()

  function onSubmit(values: User) {
    mutate(values)
  }
}
```

### SWR Pattern

```typescript
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function useUser(id: string) {
  const { data, error, isLoading } = useSWR(
    `/api/users/${id}`,
    fetcher,
    {
      refreshInterval: 30000, // Poll every 30s
      revalidateOnFocus: true,
    }
  )

  return {
    user: data,
    isLoading,
    isError: error
  }
}
```

---

## Compound Component Pattern

**When to use**: Building complex components with multiple sub-components that share state.

**Benefits**:
- Flexible composition
- Implicit state sharing
- Clean API
- Prevents prop drilling

### Example: Tabs Component

```typescript
import { createContext, useContext, useState } from "react"

interface TabsContextValue {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

function useTabs() {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error("Tabs components must be used within Tabs")
  }
  return context
}

export function Tabs({
  defaultTab,
  children
}: {
  defaultTab: string
  children: React.ReactNode
}) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  )
}

Tabs.List = function TabsList({ children }: { children: React.ReactNode }) {
  return <div className="flex border-b">{children}</div>
}

Tabs.Tab = function Tab({
  value,
  children
}: {
  value: string
  children: React.ReactNode
}) {
  const { activeTab, setActiveTab } = useTabs()
  const isActive = activeTab === value

  return (
    <button
      className={`px-4 py-2 ${isActive ? 'border-b-2 border-primary' : ''}`}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  )
}

Tabs.Panel = function TabPanel({
  value,
  children
}: {
  value: string
  children: React.ReactNode
}) {
  const { activeTab } = useTabs()
  if (activeTab !== value) return null

  return <div className="p-4">{children}</div>
}

// Usage
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab value="profile">Profile</Tabs.Tab>
    <Tabs.Tab value="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="profile">Profile content</Tabs.Panel>
  <Tabs.Panel value="settings">Settings content</Tabs.Panel>
</Tabs>
```

---

## Render Props Pattern

**When to use**: Sharing logic between components while allowing customization of rendered output.

**Benefits**:
- Logic reuse without component coupling
- Full control over rendering
- Type-safe with TypeScript

### Example: Mouse Position Tracker

```typescript
interface MousePositionProps {
  children: (position: { x: number; y: number }) => React.ReactNode
}

export function MousePosition({ children }: MousePositionProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    function handleMouseMove(e: MouseEvent) {
      setPosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return children(position)
}

// Usage
<MousePosition>
  {({ x, y }) => (
    <div>
      Mouse position: {x}, {y}
    </div>
  )}
</MousePosition>
```

### Example: Data Loader

```typescript
interface DataLoaderProps<T> {
  url: string
  children: (data: T | null, loading: boolean, error: Error | null) => React.ReactNode
}

export function DataLoader<T>({ url, children }: DataLoaderProps<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [url])

  return children(data, loading, error)
}

// Usage
<DataLoader<User> url="/api/user/123">
  {(user, loading, error) => {
    if (loading) return <Spinner />
    if (error) return <Error error={error} />
    if (!user) return <NotFound />
    return <UserCard user={user} />
  }}
</DataLoader>
```

---

## Related Resources

- See `state-management-patterns.md` for state patterns
- See `react-hooks.md` for hook patterns
- See `implementation-examples.md` for complete examples
- See `code-quality-tooling.md` for TypeScript patterns
