# shadcn/ui Components Quick Reference

> **Note**: Use this reference BEFORE calling `mcp__shadcn__getComponent()` to save tokens. Only use MCP tools when you need detailed implementation or specific variant information.

## Core Components

### Form & Input

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Input** | Text input fields | `@/components/ui/input` | `type`, `placeholder`, `disabled` |
| **Textarea** | Multi-line text input | `@/components/ui/textarea` | `placeholder`, `rows` |
| **Label** | Form labels | `@/components/ui/label` | `htmlFor` |
| **Button** | Actions & submissions | `@/components/ui/button` | `variant`, `size`, `disabled` |
| **Checkbox** | Boolean selections | `@/components/ui/checkbox` | `checked`, `onCheckedChange` |
| **Radio Group** | Single selection from options | `@/components/ui/radio-group` | `value`, `onValueChange` |
| **Select** | Dropdown selection | `@/components/ui/select` | `value`, `onValueChange` |
| **Switch** | Toggle on/off | `@/components/ui/switch` | `checked`, `onCheckedChange` |
| **Slider** | Range selection | `@/components/ui/slider` | `min`, `max`, `step`, `value` |
| **Form** | Form wrapper (react-hook-form) | `@/components/ui/form` | Uses form context |

### Layout & Structure

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Card** | Content containers | `@/components/ui/card` | Composed: CardHeader, CardContent, CardFooter |
| **Separator** | Visual dividers | `@/components/ui/separator` | `orientation` |
| **Aspect Ratio** | Maintain aspect ratio | `@/components/ui/aspect-ratio` | `ratio` |
| **Scroll Area** | Custom scrollable regions | `@/components/ui/scroll-area` | `className` |
| **Resizable** | Resizable panels | `@/components/ui/resizable` | Uses ResizablePanel, ResizableHandle |

### Navigation

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Tabs** | Tabbed navigation | `@/components/ui/tabs` | `value`, `onValueChange` |
| **Navigation Menu** | Header navigation | `@/components/ui/navigation-menu` | Complex composition |
| **Breadcrumb** | Hierarchical navigation | `@/components/ui/breadcrumb` | Composed elements |
| **Pagination** | Page navigation | `@/components/ui/pagination` | `currentPage`, `totalPages` |

### Feedback & Overlay

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Dialog** | Modal dialogs | `@/components/ui/dialog` | `open`, `onOpenChange` |
| **Sheet** | Side panels/drawers | `@/components/ui/sheet` | `open`, `onOpenChange`, `side` |
| **Popover** | Floating content | `@/components/ui/popover` | `open`, `onOpenChange` |
| **Tooltip** | Hover hints | `@/components/ui/tooltip` | `content`, `side` |
| **Alert** | Important messages | `@/components/ui/alert` | `variant` |
| **Alert Dialog** | Confirmation dialogs | `@/components/ui/alert-dialog` | `open`, `onOpenChange` |
| **Toast** | Notifications | `@/components/ui/toast` | Uses toast hook |
| **Sonner** | Alternative toast | `@/components/ui/sonner` | Alternative to toast |
| **Progress** | Progress indicators | `@/components/ui/progress` | `value`, `max` |
| **Skeleton** | Loading placeholders | `@/components/ui/skeleton` | `className` |

### Data Display

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Table** | Data tables | `@/components/ui/table` | Composed: TableHeader, TableBody, TableRow, TableCell |
| **Badge** | Status indicators | `@/components/ui/badge` | `variant` |
| **Avatar** | User images | `@/components/ui/avatar` | Composed: AvatarImage, AvatarFallback |
| **Calendar** | Date selection | `@/components/ui/calendar` | `mode`, `selected`, `onSelect` |
| **Carousel** | Image carousels | `@/components/ui/carousel` | Uses CarouselContent, CarouselItem |
| **Accordion** | Collapsible content | `@/components/ui/accordion` | `type`, `value`, `onValueChange` |
| **Collapsible** | Expand/collapse content | `@/components/ui/collapsible` | `open`, `onOpenChange` |

### Menu & Commands

| Component | Use Case | Import Path | Key Props |
|-----------|----------|-------------|-----------|
| **Dropdown Menu** | Context menus | `@/components/ui/dropdown-menu` | Complex composition |
| **Context Menu** | Right-click menus | `@/components/ui/context-menu` | Similar to DropdownMenu |
| **Menubar** | Application menubar | `@/components/ui/menubar` | Complex composition |
| **Command** | Command palette | `@/components/ui/command` | Searchable command menu |
| **Combobox** | Autocomplete select | `@/components/ui/combobox` | Combines Command + Popover |

## Common Patterns

### Form with Validation
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Form, FormField, FormItem, FormLabel, FormControl } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

// Form combines: Input, Label, Button + react-hook-form + zod
```

### Modal Dialog
```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

// Dialog is composed of multiple sub-components
```

### Data Table
```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Table requires multiple composed components
```

### Toast Notifications
```tsx
import { useToast } from "@/components/ui/use-toast"
import { Toaster } from "@/components/ui/toaster"

// Add <Toaster /> to root, use useToast() hook
```

## Button Variants

```tsx
<Button variant="default">Default</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon">Icon</Button>
```

## Alert Variants

```tsx
<Alert variant="default">Default</Alert>
<Alert variant="destructive">Error/Warning</Alert>
```

## Badge Variants

```tsx
<Badge variant="default">Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
```

## Installation Commands

```bash
# Initialize shadcn/ui
npx shadcn@latest init

# Add specific components
npx shadcn@latest add button
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add sheet
npx shadcn@latest add table
npx shadcn@latest add toast
npx shadcn@latest add select
npx shadcn@latest add dropdown-menu
```

## When to Use MCP

Only call `mcp__shadcn__getComponent(component: "name")` when you need:
- Detailed implementation code
- Specific variant information not listed here
- Advanced composition patterns
- TypeScript type definitions
- Accessibility implementation details

For common use cases, use this reference to avoid token-heavy MCP calls.
