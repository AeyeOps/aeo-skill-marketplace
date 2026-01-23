/**
 * Custom Hook Template
 *
 * Usage: Copy this template for new custom hooks
 * Replace useCustomHook with your hook name
 */

import { useState, useEffect, useCallback } from 'react'

interface UseCustomHookOptions {
  initialValue?: string
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

interface UseCustomHookReturn {
  data: any | null
  loading: boolean
  error: Error | null
  refetch: () => void
}

export function useCustomHook(
  options: UseCustomHookOptions = {}
): UseCustomHookReturn {
  const { initialValue, onSuccess, onError } = options

  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      // Your logic here
      const result = await fetch('/api/data')
      const json = await result.json()

      setData(json)
      onSuccess?.(json)
    } catch (err) {
      const error = err as Error
      setError(error)
      onError?.(error)
    } finally {
      setLoading(false)
    }
  }, [onSuccess, onError])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  }
}

// Example usage in a component:
/*
function MyComponent() {
  const { data, loading, error, refetch } = useCustomHook({
    initialValue: '',
    onSuccess: (data) => console.log('Success!', data),
    onError: (error) => console.error('Error:', error),
  })

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <pre>{JSON.stringify(data, null, 2)}</pre>
      <button onClick={refetch}>Refresh</button>
    </div>
  )
}
*/
