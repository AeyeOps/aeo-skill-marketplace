/**
 * Component Boilerplate Template
 *
 * Usage: Copy this template for new components
 * Replace ComponentName with your component name
 */

import { cn } from '@/lib/utils'

interface ComponentNameProps {
  className?: string
  children?: React.ReactNode
  // Add your props here
}

export function ComponentName({
  className,
  children,
  ...props
}: ComponentNameProps) {
  return (
    <div className={cn('component-base-styles', className)} {...props}>
      {children}
    </div>
  )
}

// Example with state and handlers
export function InteractiveComponent({
  onAction,
  className,
}: {
  onAction?: () => void
  className?: string
}) {
  const [isActive, setIsActive] = useState(false)

  const handleClick = () => {
    setIsActive(!isActive)
    onAction?.()
  }

  return (
    <button
      onClick={handleClick}
      className={cn(
        'base-styles',
        isActive && 'active-styles',
        className
      )}
    >
      {isActive ? 'Active' : 'Inactive'}
    </button>
  )
}
