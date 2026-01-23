/**
 * Service Worker for React PWA
 *
 * Production-tested implementation with:
 * - Stale-while-revalidate caching strategy
 * - Offline fallback support
 * - Automatic cache management
 * - TypeScript types
 *
 * Place this file in /public/sw.ts and compile to /public/sw.js
 * DO NOT import this file in your React app - it runs independently
 */

/// <reference lib="webworker" />
declare const self: ServiceWorkerGlobalScope
export {}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CACHE_VERSION = 'v1' // Increment this for each deployment
const STATIC_CACHE = `static-${CACHE_VERSION}`
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`

// Files to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/apple-touch-icon.png',
  '/android-chrome-192x192.png',
  '/android-chrome-512x512.png',
]

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if request is an API call
 */
const isApiRequest = (request: Request): boolean => {
  try {
    const url = new URL(request.url)
    return (
      url.origin === self.location.origin &&
      (url.pathname.startsWith('/api/') || url.pathname.startsWith('/graphql'))
    )
  } catch {
    return false
  }
}

/**
 * Check if request is same-origin
 */
const isSameOrigin = (request: Request): boolean => {
  try {
    const url = new URL(request.url)
    return url.origin === self.location.origin
  } catch {
    return false
  }
}

/**
 * Fetch and cache a request
 */
const fetchAndCache = async (
  request: Request,
  cacheName: string = DYNAMIC_CACHE
): Promise<Response> => {
  try {
    const response = await fetch(request)

    // Only cache successful GET requests from same origin (not API)
    if (
      response &&
      response.status === 200 &&
      request.method === 'GET' &&
      isSameOrigin(request) &&
      !isApiRequest(request)
    ) {
      const cache = await caches.open(cacheName)
      cache.put(request, response.clone())
    }

    return response
  } catch (error) {
    // Network request failed, try to return cached version
    const cache = await caches.open(DYNAMIC_CACHE)
    const cachedResponse = await cache.match(request)

    if (cachedResponse) {
      console.log('[SW] Returning cached response for:', request.url)
      return cachedResponse
    }

    // For navigation requests, return offline page
    if (request.mode === 'navigate') {
      const offlinePage = await cache.match('/offline.html')
      if (offlinePage) {
        return offlinePage
      }
    }

    throw error
  }
}

// ============================================================================
// SERVICE WORKER LIFECYCLE EVENTS
// ============================================================================

/**
 * INSTALL EVENT
 * Triggered when service worker is first installed or updated
 */
self.addEventListener('install', (event: ExtendableEvent) => {
  console.log('[SW] Installing service worker...', CACHE_VERSION)

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets')
        return cache.addAll(STATIC_ASSETS)
      })
      .then(() => {
        console.log('[SW] Installation complete')
        return self.skipWaiting()
      })
      .catch((error) => {
        console.error('[SW] Installation failed:', error)
      })
  )
})

/**
 * ACTIVATE EVENT
 * Triggered when service worker becomes active
 */
self.addEventListener('activate', (event: ExtendableEvent) => {
  console.log('[SW] Activating service worker...', CACHE_VERSION)

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return (
                cacheName !== STATIC_CACHE &&
                cacheName !== DYNAMIC_CACHE
              )
            })
            .map((cacheName) => {
              console.log('[SW] Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            })
        )
      })
      .then(() => {
        console.log('[SW] Activation complete')
        return self.clients.claim()
      })
  )
})

/**
 * FETCH EVENT
 * Intercepts all network requests
 */
self.addEventListener('fetch', (event: FetchEvent) => {
  const { request } = event

  if (request.method !== 'GET' || !isSameOrigin(request)) {
    return
  }

  // API Requests: Network-first
  if (isApiRequest(request)) {
    event.respondWith(
      fetch(request).catch(() => new Response(null, { status: 503 }))
    )
    return
  }

  // Stale-while-revalidate
  event.respondWith(
    (async () => {
      const cache = await caches.open(DYNAMIC_CACHE)
      const cachedResponse = await cache.match(request)

      const fetchPromise = fetchAndCache(request).catch(() => null)

      if (cachedResponse) {
        fetchPromise.catch(() => {})
        return cachedResponse
      }

      const networkResponse = await fetchPromise
      if (networkResponse) return networkResponse

      if (request.mode === 'navigate') {
        const offlinePage = await cache.match('/offline.html')
        if (offlinePage) return offlinePage
      }

      return Response.error()
    })()
  )
})

/**
 * MESSAGE EVENT
 */
self.addEventListener('message', (event: ExtendableMessageEvent) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
})