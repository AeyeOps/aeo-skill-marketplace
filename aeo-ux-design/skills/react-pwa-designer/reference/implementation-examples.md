# Implementation Examples

**When to read this**: Building specific features and need concrete implementation patterns.

**Quick answer**: See the example that matches your use case below.

---

## Contents

- [Example 1: Dashboard with Data Table](#example-1-dashboard-with-data-table)
- [Example 2: Authentication Flow](#example-2-authentication-flow)

---

## Example 1: Dashboard with Data Table

**User Request**: "Build a dashboard with a data table and filtering"

### Response Flow

#### 1. Layout Design

```
┌─────────────────────────────────────────────┐
│  Dashboard Header (shadcn: Card)            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Metric  │ │ Metric  │ │ Metric  │       │
│  │ Card    │ │ Card    │ │ Card    │       │
│  └─────────┘ └─────────┘ └─────────┘       │
├─────────────────────────────────────────────┤
│  Filters & Search (Input, Select, Button)  │
├─────────────────────────────────────────────┤
│  Data Table (shadcn: Table + DataTable)    │
│  ┌─────────────────────────────────────┐   │
│  │ Col 1 │ Col 2 │ Col 3 │ Actions    │   │
│  ├─────────────────────────────────────┤   │
│  │ Data  │ Data  │ Data  │ Edit|Del   │   │
│  └─────────────────────────────────────┘   │
│  [Pagination]                               │
└─────────────────────────────────────────────┘
```

#### 2. Component Discovery

```
mcp__shadcn__getComponents() → Find: card, table, input, select, button
mcp__shadcn__getComponent(component: "table") → Get details
```

#### 3. Theme

Generate using modern dark mode style (reference SuperDesign methodology)

#### 4. Implementation

Create `DashboardTable.tsx` with shadcn components

```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export function Dashboard() {
  return (
    <div className="flex flex-col gap-4 p-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">1,234</p>
          </CardContent>
        </Card>
        {/* More metric cards... */}
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Input placeholder="Search..." />
        <Select>
          <option>All Categories</option>
        </Select>
        <Button>Filter</Button>
      </div>

      {/* Data Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* Table rows... */}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}
```

### Component Stack Used

- **shadcn components**: Card, Table, Input, Select, Button
- **Layout**: CSS Grid (3 columns) + Flexbox
- **State**: useState for filters, search
- **Data fetching**: React Query (optional, for real data)

### Key Patterns Applied

1. **Grid layout** for metric cards (responsive: 3 cols → 1 col mobile)
2. **Card composition** for containing metrics and table
3. **Table component** from shadcn with proper semantic HTML
4. **Filter state management** with controlled inputs

---

## Example 2: Authentication Flow

**User Request**: "Create a login page with form validation"

### Component Stack

- **shadcn**: Card, Form, Input, Button, Label
- **react-hook-form**: Form state management
- **zod**: Validation schema
- **React Router**: Navigation after login

### Implementation Pattern

```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters")
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    // API call to authenticate
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values)
    })

    if (response.ok) {
      const data = await response.json()
      // Store token, redirect, etc.
      localStorage.setItem("token", data.token)
      navigate("/dashboard")
    } else {
      // Handle error
      form.setError("root", { message: "Invalid credentials" })
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="you@example.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full">
                Sign In
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Key Patterns Applied

1. **Zod schema validation** - Type-safe validation with error messages
2. **React Hook Form integration** - Controlled form with minimal re-renders
3. **shadcn Form components** - Accessible form structure with ARIA attributes
4. **Error handling** - Field-level and form-level errors
5. **Centered layout** - Flex centering for login page
6. **Responsive card** - `max-w-md` constrains width on large screens

### Validation Schema Patterns

```typescript
// Common validation patterns
const schemas = {
  // Email
  email: z.string().email("Invalid email"),

  // Password strength
  password: z.string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "At least one uppercase letter")
    .regex(/[0-9]/, "At least one number"),

  // Confirm password
  confirmPassword: z.string(),

  // Phone number
  phone: z.string().regex(/^\d{10}$/, "Must be 10 digits"),

  // Optional field
  middleName: z.string().optional(),

  // Required select
  country: z.enum(["US", "UK", "CA"], {
    errorMap: () => ({ message: "Please select a country" })
  })
}

// Password confirmation validation
const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  confirmPassword: z.string()
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})
```

### Navigation After Login

```typescript
import { useNavigate } from "react-router-dom"

function LoginForm() {
  const navigate = useNavigate()

  async function onSubmit(values) {
    const response = await fetch("/api/login", { /* ... */ })
    if (response.ok) {
      navigate("/dashboard", { replace: true }) // Replace history
    }
  }
}
```

### Protected Route Pattern

```typescript
// ProtectedRoute.tsx
import { Navigate } from "react-router-dom"

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token")
  return token ? children : <Navigate to="/login" replace />
}

// App.tsx
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

---

## Related Resources

- See `state-management-patterns.md` for form state patterns
- See `code-quality-tooling.md` for TypeScript types
- See `component-patterns.md` for more compositional patterns
- See `accessibility.md` for ARIA patterns in forms
