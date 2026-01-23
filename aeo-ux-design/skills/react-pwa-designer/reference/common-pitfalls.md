# Common Pitfalls & Anti-Patterns

Mistakes to avoid when building React PWAs with shadcn/ui.

## React Anti-Patterns

### ❌ Mutating State Directly

```tsx
// ❌ BAD - Mutates state directly
const [user, setUser] = useState({ name: 'John', age: 30 })
user.age = 31 // Wrong!
setUser(user) // Won't trigger re-render

// ✅ GOOD - Creates new object
setUser({ ...user, age: 31 })
// Or
setUser(prev => ({ ...prev, age: 31 }))
```

### ❌ Missing Dependencies in useEffect

```tsx
// ❌ BAD - Missing dependency
useEffect(() => {
  fetchUser(userId)
}, []) // userId should be in deps!

// ✅ GOOD - Includes all dependencies
useEffect(() => {
  fetchUser(userId)
}, [userId])
```

### ❌ Creating Functions Inside Render

```tsx
// ❌ BAD - Creates new function on every render
function Parent() {
  return <Child onClick={() => console.log('click')} />
}

// ✅ GOOD - Memoizes function
function Parent() {
  const handleClick = useCallback(() => {
    console.log('click')
  }, [])

  return <Child onClick={handleClick} />
}
```

### ❌ Not Cleaning Up Effects

```tsx
// ❌ BAD - Subscription leak
useEffect(() => {
  const subscription = subscribeToData()
  // Missing cleanup!
}, [])

// ✅ GOOD - Proper cleanup
useEffect(() => {
  const subscription = subscribeToData()
  return () => subscription.unsubscribe()
}, [])
```

### ❌ Using Index as Key

```tsx
// ❌ BAD - Index as key (for dynamic lists)
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// ✅ GOOD - Unique ID as key
{items.map((item) => (
  <div key={item.id}>{item.name}</div>
))}
```

## shadcn/ui Pitfalls

### ❌ Not Importing Globals CSS

```tsx
// ❌ BAD - Missing global styles
import { Button } from '@/components/ui/button'

// ✅ GOOD - Import globals.css in main.tsx
import './globals.css'
import { Button } from '@/components/ui/button'
```

### ❌ Incorrect Dialog Composition

```tsx
// ❌ BAD - Dialog state managed incorrectly
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>...</DialogContent>
</Dialog>

// ✅ GOOD - Controlled dialog with state
const [open, setOpen] = useState(false)

<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>...</DialogContent>
</Dialog>
```

### ❌ Not Using Form Components Properly

```tsx
// ❌ BAD - Not using shadcn Form wrapper
<form>
  <Input {...form.register('email')} />
</form>

// ✅ GOOD - Use shadcn Form with react-hook-form
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      control={form.control}
      name="email"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input {...field} />
          </FormControl>
        </FormItem>
      )}
    />
  </form>
</Form>
```

### ❌ Overriding shadcn Styles Incorrectly

```tsx
// ❌ BAD - Inline styles (won't work with variants)
<Button style={{ backgroundColor: 'red' }}>Click</Button>

// ✅ GOOD - Use className with Tailwind
<Button className="bg-red-500 hover:bg-red-600">Click</Button>

// ✅ BETTER - Extend variants in component
const buttonVariants = cva({
  variants: {
    variant: {
      danger: "bg-red-500 hover:bg-red-600"
    }
  }
})
```

### ❌ Not Using cn() Utility

```tsx
// ❌ BAD - Manual className concatenation
<div className={`${baseClass} ${isActive ? 'active' : ''}`}>

// ✅ GOOD - Use cn() helper
import { cn } from '@/lib/utils'

<div className={cn(baseClass, isActive && 'active')}>
```

## PWA Pitfalls

### ❌ Missing Viewport Meta Tag

```html
<!-- ❌ BAD - No viewport tag -->
<head>
  <title>My App</title>
</head>

<!-- ✅ GOOD - Viewport for mobile -->
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My App</title>
</head>
```

### ❌ Service Worker Scope Issues

```tsx
// ❌ BAD - Service worker in subdirectory
navigator.serviceWorker.register('/js/service-worker.js')
// Only works for /js/* scope

// ✅ GOOD - Service worker at root
navigator.serviceWorker.register('/service-worker.js')
// Works for entire app
```

### ❌ Not Handling Update Prompts

```tsx
// ❌ BAD - Service worker updates silently
navigator.serviceWorker.register('/sw.js')

// ✅ GOOD - Prompt user for updates
const registration = await navigator.serviceWorker.register('/sw.js')

registration.addEventListener('updatefound', () => {
  const newWorker = registration.installing
  newWorker.addEventListener('statechange', () => {
    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
      showUpdatePrompt() // Notify user
    }
  })
})
```

### ❌ Caching Everything

```typescript
// ❌ BAD - Cache everything indiscriminately
workbox.routing.registerRoute(
  /.*/,
  new workbox.strategies.CacheFirst()
)

// ✅ GOOD - Strategic caching
// Static assets - CacheFirst
workbox.routing.registerRoute(
  /\.(?:js|css|png|jpg|jpeg|svg|gif)$/,
  new workbox.strategies.CacheFirst()
)

// API calls - NetworkFirst
workbox.routing.registerRoute(
  /\/api\/.*/,
  new workbox.strategies.NetworkFirst()
)

// HTML - NetworkFirst with fallback
workbox.routing.registerRoute(
  /\.html$/,
  new workbox.strategies.NetworkFirst()
)
```

### ❌ Icon Dimension Mismatch (CRITICAL!)

**The #1 PWA installation blocker**

```json
// ❌ BAD - Manifest says 192x192, but file is actually 1024x1024
{
  "icons": [
    { "src": "/icon-192x192.png", "sizes": "192x192" }  // File is wrong size!
  ]
}

// Result: PWA installation fails silently on Chrome/Edge
// No error message in console
// Hours of debugging to discover
```

**Why it happens:**
- High-res source image resized incorrectly
- Filename suggests correct size, but actual pixels are wrong
- Manifest validator doesn't check actual file dimensions

**How to prevent:**

```bash
# ALWAYS verify actual icon dimensions
file public/icon-192x192.png
# MUST show: PNG image data, 192 x 192

# Wrong output means fix immediately:
# PNG image data, 1024 x 1024  ← WRONG! Will break PWA

# Correct generation with ImageMagick
convert source.png -resize 192x192! icon-192x192.png
convert source.png -resize 512x512! icon-512x512.png
```

**See `pwa-icon-validation.md` for complete guide**

### ❌ Missing Icon Sizes

```json
// ❌ BAD - Only one icon size
{
  "icons": [
    { "src": "/icon.png", "sizes": "192x192" }
  ]
}

// ✅ GOOD - Multiple sizes (at minimum: 192, 512, 180 for iOS)
{
  "icons": [
    { "src": "/icon-192x192.png", "sizes": "192x192" },
    { "src": "/icon-512x512.png", "sizes": "512x512" },
    { "src": "/apple-touch-icon.png", "sizes": "180x180" }
  ]
}
```

## TypeScript Pitfalls

### ❌ Using `any` Type

```tsx
// ❌ BAD - Loses type safety
const handleClick = (data: any) => {
  console.log(data.name) // No autocomplete, no type checking
}

// ✅ GOOD - Proper typing
interface User {
  name: string
  email: string
}

const handleClick = (data: User) => {
  console.log(data.name) // Type safe!
}
```

### ❌ Not Typing Event Handlers

```tsx
// ❌ BAD - Implicit any
const handleChange = (e) => {
  setValue(e.target.value)
}

// ✅ GOOD - Explicit types
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value)
}
```

### ❌ Wrong useState Type Inference

```tsx
// ❌ BAD - Type inferred as undefined | User
const [user, setUser] = useState()

// ✅ GOOD - Explicit generic
const [user, setUser] = useState<User | null>(null)
```

## Performance Pitfalls

### ❌ Not Code Splitting

```tsx
// ❌ BAD - Import everything upfront
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import Profile from './pages/Profile'

// ✅ GOOD - Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))
const Profile = lazy(() => import('./pages/Profile'))

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
    <Route path="/profile" element={<Profile />} />
  </Routes>
</Suspense>
```

### ❌ Unnecessary Re-renders

```tsx
// ❌ BAD - Creates new object on every render
<Component config={{ theme: 'dark' }} />

// ✅ GOOD - Memoize config
const config = useMemo(() => ({ theme: 'dark' }), [])
<Component config={config} />

// ❌ BAD - Not memoizing expensive component
function ExpensiveChild({ data }) {
  // Heavy computation
  return <div>{process(data)}</div>
}

// ✅ GOOD - Memoize component
const ExpensiveChild = memo(({ data }) => {
  const processed = useMemo(() => process(data), [data])
  return <div>{processed}</div>
})
```

### ❌ Loading All Data Upfront

```tsx
// ❌ BAD - Load everything
const { data } = useQuery('users', () => fetchAllUsers())

// ✅ GOOD - Pagination/infinite scroll
const { data, fetchNextPage } = useInfiniteQuery(
  'users',
  ({ pageParam = 0 }) => fetchUsers(pageParam, 20)
)
```

## Accessibility Pitfalls

### ❌ Missing Alt Text

```tsx
// ❌ BAD - No alt text
<img src="/logo.png" />

// ✅ GOOD - Descriptive alt
<img src="/logo.png" alt="Company Logo" />

// ✅ GOOD - Decorative image
<img src="/decoration.png" alt="" role="presentation" />
```

### ❌ Div Buttons

```tsx
// ❌ BAD - Div as button
<div onClick={handleClick}>Click me</div>

// ✅ GOOD - Proper button
<button onClick={handleClick}>Click me</button>
```

### ❌ Missing Focus Indicators

```css
/* ❌ BAD - Removes focus outline */
*:focus {
  outline: none;
}

/* ✅ GOOD - Custom focus style */
*:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}
```

## Security Pitfalls

### ❌ Exposing Secrets

```tsx
// ❌ BAD - API key in client code
const API_KEY = 'sk_live_abc123'
fetch(`/api/data?key=${API_KEY}`)

// ✅ GOOD - API key on server
// Use environment variables for public keys only
const PUBLIC_KEY = import.meta.env.VITE_PUBLIC_KEY
```

### ❌ Unvalidated User Input

```tsx
// ❌ BAD - Direct innerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ GOOD - Sanitize or use text content
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />

// ✅ BETTER - Avoid innerHTML
<div>{userInput}</div>
```

## State Management Pitfalls

### ❌ Prop Drilling

```tsx
// ❌ BAD - Passing props through many levels
<App>
  <Layout user={user}>
    <Content user={user}>
      <Profile user={user} />
    </Content>
  </Layout>
</App>

// ✅ GOOD - Use Context or state management
const UserContext = createContext()

<UserContext.Provider value={user}>
  <App>
    <Layout>
      <Content>
        <Profile />
      </Content>
    </Layout>
  </App>
</UserContext.Provider>
```

### ❌ Too Much State

```tsx
// ❌ BAD - Derived state
const [items, setItems] = useState([])
const [filteredItems, setFilteredItems] = useState([])

useEffect(() => {
  setFilteredItems(items.filter(i => i.isActive))
}, [items])

// ✅ GOOD - Compute during render
const [items, setItems] = useState([])
const filteredItems = useMemo(
  () => items.filter(i => i.isActive),
  [items]
)
```

## Build & Deployment Pitfalls

### ❌ Not Minifying Code

```typescript
// ❌ BAD - Development build in production
npm run dev

// ✅ GOOD - Production build
npm run build
npm run preview
```

### ❌ Missing Environment Variables

```typescript
// ❌ BAD - No fallback
const API_URL = import.meta.env.VITE_API_URL

// ✅ GOOD - Fallback or validation
const API_URL = import.meta.env.VITE_API_URL || 'https://api.default.com'

if (!API_URL) {
  throw new Error('VITE_API_URL is required')
}
```

### ❌ Hardcoded URLs

```tsx
// ❌ BAD - Hardcoded
fetch('http://localhost:3000/api/data')

// ✅ GOOD - Environment variable
const API_URL = import.meta.env.VITE_API_URL
fetch(`${API_URL}/api/data`)
```

## Quick Checklist

Before deploying, verify you're NOT doing these:

- [ ] Mutating state directly
- [ ] Missing useEffect dependencies
- [ ] Using index as key for dynamic lists
- [ ] Missing globals.css import
- [ ] Inline styles on shadcn components
- [ ] Service worker in wrong location
- [ ] Missing viewport meta tag
- [ ] Using `any` type in TypeScript
- [ ] Not code splitting routes
- [ ] Divs instead of buttons
- [ ] Missing alt text on images
- [ ] Exposing secrets in client code
- [ ] Prop drilling instead of context
- [ ] Development build in production

## Resources

- [React Docs: Common Mistakes](https://react.dev/learn/you-might-not-need-an-effect)
- [shadcn/ui Installation](https://ui.shadcn.com/docs/installation)
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
