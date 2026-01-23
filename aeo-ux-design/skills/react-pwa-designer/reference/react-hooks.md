# React Hooks Patterns Reference

Common React hooks patterns for PWA development with TypeScript.

## Core Hooks

### useState - State Management

```typescript
// Basic state
const [count, setCount] = useState(0)
const [text, setText] = useState('')
const [isOpen, setOpen] = useState(false)

// Object state
interface User {
  name: string
  email: string
}
const [user, setUser] = useState<User>({ name: '', email: '' })

// Array state
const [items, setItems] = useState<string[]>([])

// Lazy initialization (expensive computation)
const [data, setData] = useState(() => {
  return expensiveComputation()
})

// Functional updates (when new state depends on previous)
setCount(prev => prev + 1)
setItems(prev => [...prev, newItem])
```

### useEffect - Side Effects

```typescript
// Run once on mount
useEffect(() => {
  fetchData()
}, [])

// Run on dependency change
useEffect(() => {
  fetchUser(userId)
}, [userId])

// Cleanup function
useEffect(() => {
  const subscription = subscribeToData()
  return () => subscription.unsubscribe()
}, [])

// Multiple effects (separate concerns)
useEffect(() => {
  // Effect 1: Fetch data
}, [dependency1])

useEffect(() => {
  // Effect 2: Update document title
}, [dependency2])
```

### useRef - Persistent Values

```typescript
// DOM reference
const inputRef = useRef<HTMLInputElement>(null)
inputRef.current?.focus()

// Mutable value (doesn't trigger re-render)
const countRef = useRef(0)
countRef.current += 1

// Previous value tracking
const usePrevious = <T,>(value: T): T | undefined => {
  const ref = useRef<T>()
  useEffect(() => {
    ref.current = value
  })
  return ref.current
}
```

### useMemo - Expensive Computations

```typescript
// Memoize expensive computation
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.localeCompare(b))
}, [items])

// Memoize object/array to prevent re-renders
const config = useMemo(() => ({
  apiUrl: process.env.API_URL,
  timeout: 5000
}), [])

// Derived state
const filteredUsers = useMemo(() => {
  return users.filter(u => u.isActive)
}, [users])
```

### useCallback - Memoized Functions

```typescript
// Memoize callback to prevent child re-renders
const handleClick = useCallback(() => {
  doSomething(id)
}, [id])

// Form handlers
const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value)
}, [])

// With dependencies
const handleSubmit = useCallback(async () => {
  await submitForm(formData)
}, [formData])
```

## Custom Hooks

### useLocalStorage

```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue] as const
}

// Usage
const [name, setName] = useLocalStorage('name', 'John')
```

### useDebounce

```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

// Usage
const [searchTerm, setSearchTerm] = useState('')
const debouncedSearch = useDebounce(searchTerm, 500)
```

### useFetch

```typescript
interface FetchState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

function useFetch<T>(url: string): FetchState<T> {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url)
        if (!response.ok) throw new Error('Network response was not ok')
        const data = await response.json()
        setState({ data, loading: false, error: null })
      } catch (error) {
        setState({ data: null, loading: false, error: error as Error })
      }
    }

    fetchData()
  }, [url])

  return state
}

// Usage
const { data, loading, error } = useFetch<User>('/api/user')
```

### useOnClickOutside

```typescript
function useOnClickOutside<T extends HTMLElement>(
  ref: RefObject<T>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return
      }
      handler(event)
    }

    document.addEventListener('mousedown', listener)
    document.addEventListener('touchstart', listener)

    return () => {
      document.removeEventListener('mousedown', listener)
      document.removeEventListener('touchstart', listener)
    }
  }, [ref, handler])
}

// Usage
const dropdownRef = useRef<HTMLDivElement>(null)
useOnClickOutside(dropdownRef, () => setIsOpen(false))
```

### useMediaQuery

```typescript
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

// Usage
const isMobile = useMediaQuery('(max-width: 768px)')
const isDark = useMediaQuery('(prefers-color-scheme: dark)')
```

### useToggle

```typescript
function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}

// Usage
const [isOpen, toggleOpen] = useToggle()
```

### useInterval

```typescript
function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = useRef(callback)

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (delay === null) return

    const id = setInterval(() => savedCallback.current(), delay)
    return () => clearInterval(id)
  }, [delay])
}

// Usage
useInterval(() => {
  fetchLatestData()
}, 5000)
```

### usePrevious

```typescript
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>()

  useEffect(() => {
    ref.current = value
  }, [value])

  return ref.current
}

// Usage
const [count, setCount] = useState(0)
const prevCount = usePrevious(count)
```

### useWindowSize

```typescript
interface WindowSize {
  width: number
  height: number
}

function useWindowSize(): WindowSize {
  const [windowSize, setWindowSize] = useState<WindowSize>({
    width: window.innerWidth,
    height: window.innerHeight
  })

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      })
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return windowSize
}

// Usage
const { width, height } = useWindowSize()
```

## PWA-Specific Hooks

### useOnline

```typescript
function useOnline(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return isOnline
}
```

### useServiceWorker

```typescript
function useServiceWorker() {
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null)

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .then(reg => {
          setRegistration(reg)

          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing
            newWorker?.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setUpdateAvailable(true)
              }
            })
          })
        })
    }
  }, [])

  const updateServiceWorker = () => {
    registration?.waiting?.postMessage({ type: 'SKIP_WAITING' })
    window.location.reload()
  }

  return { updateAvailable, updateServiceWorker }
}
```

### useInstallPrompt

```typescript
function useInstallPrompt() {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [isInstalled, setIsInstalled] = useState(false)

  useEffect(() => {
    const handler = (e: BeforeInstallPromptEvent) => {
      e.preventDefault()
      setInstallPrompt(e)
    }

    window.addEventListener('beforeinstallprompt', handler as any)
    window.addEventListener('appinstalled', () => setIsInstalled(true))

    return () => {
      window.removeEventListener('beforeinstallprompt', handler as any)
    }
  }, [])

  const promptInstall = async () => {
    if (!installPrompt) return false

    installPrompt.prompt()
    const { outcome } = await installPrompt.userChoice

    if (outcome === 'accepted') {
      setInstallPrompt(null)
      return true
    }
    return false
  }

  return { canInstall: !!installPrompt, promptInstall, isInstalled }
}
```

## Form Hooks (with react-hook-form)

### Basic Form

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

type FormData = z.infer<typeof formSchema>

function LoginForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: ''
    }
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

## Best Practices

### ✅ Do

- Use `useCallback` for functions passed to child components
- Use `useMemo` for expensive computations
- Cleanup effects properly (return cleanup function)
- Use TypeScript generics for custom hooks
- Keep hooks at the top level (not in conditions)
- Separate concerns into multiple `useEffect` calls

### ❌ Don't

- Don't call hooks conditionally or in loops
- Don't create unnecessary re-renders (missing memoization)
- Don't forget cleanup functions for subscriptions/timers
- Don't mutate state directly (always use setState)
- Don't use `useEffect` for transforming data (use `useMemo`)
- Don't create custom hooks that could be simple functions

## Performance Tips

1. **Memoize expensive computations** with `useMemo`
2. **Memoize callbacks** with `useCallback` when passing to children
3. **Use React.memo** for expensive child components
4. **Lazy load** components with `React.lazy`
5. **Debounce** rapid state updates (search inputs, resize handlers)
6. **Batch state updates** in event handlers
