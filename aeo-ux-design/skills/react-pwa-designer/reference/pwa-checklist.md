# Progressive Web App (PWA) Checklist

Comprehensive checklist for building production-ready PWAs.

## Core Requirements

### ✅ Manifest File (`public/manifest.json`)

```json
{
  "name": "Full Application Name",
  "short_name": "App Name",
  "description": "Detailed description of your app",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "orientation": "portrait",
  "scope": "/",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ]
}
```

**Required Icon Sizes**: 72, 96, 128, 144, 152, 192, 384, 512

**⚠️ CRITICAL: Icon Validation**

Icon dimension mismatches are the **#1 cause of PWA installation failure**. Before deploying:

```bash
# MUST verify actual icon dimensions
file public/icons/icon-192x192.png
# Expected: PNG image data, 192 x 192

file public/icons/icon-512x512.png
# Expected: PNG image data, 512 x 512
```

**If icon dimensions don't match manifest declarations, PWA installation will fail with no error message.**

→ **See**: `pwa-icon-validation.md` for complete icon setup and validation guide

### ✅ HTML Meta Tags (`index.html`)

```html
<head>
  <!-- Primary Meta Tags -->
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="App description" />
  <meta name="theme-color" content="#ffffff" />

  <!-- Manifest -->
  <link rel="manifest" href="/manifest.json" />

  <!-- iOS Support -->
  <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="apple-mobile-web-app-title" content="App Name" />

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
</head>
```

### ✅ Service Worker

**Vite PWA Plugin** (Recommended):

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'robots.txt', 'icons/*.png'],
      manifest: {
        // manifest options (can reference separate file)
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ]
})
```

**Caching Strategies**:
- **CacheFirst**: Good for static assets
- **NetworkFirst**: Good for API calls, HTML
- **StaleWhileRevalidate**: Balance between speed and freshness
- **NetworkOnly**: Always fetch from network
- **CacheOnly**: Only use cache

## HTTPS Requirement

### ✅ Production Deployment

- Must be served over HTTPS
- `localhost` and `127.0.0.1` are exempt (for development)
- Use Let's Encrypt, Cloudflare, or hosting provider SSL

### Development

```bash
# Vite dev server (HTTP is OK for localhost)
npm run dev

# Preview with HTTPS (using mkcert)
npm run preview
```

## Performance Requirements

### ✅ Core Web Vitals

**Target Metrics**:
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

**Lighthouse Score Targets**:
- Performance: > 90
- Accessibility: 100
- Best Practices: > 95
- SEO: > 90
- PWA: 100

### ✅ Bundle Optimization

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui': ['@/components/ui'] // shadcn components
        }
      }
    },
    chunkSizeWarningLimit: 500
  }
})
```

**Code Splitting**:

```typescript
// Lazy load routes
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))

<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

### ✅ Image Optimization

- Use WebP format
- Implement lazy loading
- Use `srcset` for responsive images
- Compress images (TinyPNG, ImageOptim)

```tsx
<img
  src="/images/hero.webp"
  srcSet="/images/hero-320w.webp 320w,
          /images/hero-640w.webp 640w,
          /images/hero-1024w.webp 1024w"
  sizes="(max-width: 640px) 320px,
         (max-width: 1024px) 640px,
         1024px"
  loading="lazy"
  alt="Hero image"
/>
```

## Offline Functionality

### ✅ Offline Fallback

```typescript
// Service worker offline page
workbox: {
  navigateFallback: '/offline.html',
  navigateFallbackDenylist: [/^\/api\//]
}
```

### ✅ Network Status Detection

```typescript
import { useOnline } from '@/hooks/useOnline'

function App() {
  const isOnline = useOnline()

  return (
    <>
      {!isOnline && (
        <div className="offline-banner">
          You are currently offline
        </div>
      )}
      {/* rest of app */}
    </>
  )
}
```

### ✅ Offline Data Sync

Consider using:
- **IndexedDB** for local storage
- **Background Sync API** for data synchronization
- **Periodic Background Sync** for regular updates

## Installability

### ✅ Install Prompt

```typescript
import { useInstallPrompt } from '@/hooks/useInstallPrompt'

function InstallButton() {
  const { canInstall, promptInstall, isInstalled } = useInstallPrompt()

  if (isInstalled || !canInstall) return null

  return (
    <button onClick={promptInstall}>
      Install App
    </button>
  )
}
```

### ✅ iOS Add to Home Screen

No automatic prompt on iOS. Provide instructions:

```tsx
function IOSInstallPrompt() {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
  const isStandalone = (window.navigator as any).standalone

  if (!isIOS || isStandalone) return null

  return (
    <div className="ios-install-prompt">
      <p>Install this app: tap Share icon and "Add to Home Screen"</p>
    </div>
  )
}
```

## Update Mechanism

### ✅ Service Worker Updates

```typescript
import { useServiceWorker } from '@/hooks/useServiceWorker'

function UpdatePrompt() {
  const { updateAvailable, updateServiceWorker } = useServiceWorker()

  if (!updateAvailable) return null

  return (
    <div className="update-banner">
      <p>New version available!</p>
      <button onClick={updateServiceWorker}>Update Now</button>
    </div>
  )
}
```

## Security

### ✅ Content Security Policy

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com;
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
               font-src 'self' https://fonts.gstatic.com;
               img-src 'self' data: https:;
               connect-src 'self' https://api.example.com;">
```

### ✅ HTTPS Redirect

Configure in hosting provider or server:

```javascript
// Express example
app.use((req, res, next) => {
  if (req.header('x-forwarded-proto') !== 'https') {
    res.redirect(`https://${req.header('host')}${req.url}`)
  } else {
    next()
  }
})
```

## Accessibility

### ✅ PWA Accessibility

- Keyboard navigation works offline
- Screen readers announce offline state
- Focus management during updates
- Proper ARIA labels for install/update prompts

## Browser Support

### ✅ Feature Detection

```typescript
// Check service worker support
if ('serviceWorker' in navigator) {
  // Register service worker
}

// Check notification support
if ('Notification' in window) {
  // Request notification permission
}

// Check background sync support
if ('sync' in registration) {
  // Register background sync
}
```

### ✅ Fallbacks

- Provide non-PWA experience for unsupported browsers
- Progressive enhancement approach
- Graceful degradation

## Testing Checklist

### ✅ Lighthouse Audit

```bash
# Run Lighthouse
npx lighthouse https://your-app.com --view

# Or use Chrome DevTools > Lighthouse
```

### ✅ PWA Testing

- [ ] Install prompt appears (Chrome, Edge)
- [ ] App installs successfully
- [ ] App works offline
- [ ] Service worker updates properly
- [ ] Icons appear correctly on home screen
- [ ] Splash screen displays (Android)
- [ ] Theme color applies
- [ ] Network status detected
- [ ] Offline fallback page works
- [ ] Performance metrics pass
- [ ] All Lighthouse PWA checks pass

### ✅ Cross-Browser Testing

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (iOS and macOS)
- [ ] Samsung Internet

### ✅ Device Testing

- [ ] Android phone
- [ ] iPhone
- [ ] iPad
- [ ] Desktop (Windows, Mac, Linux)

## Deployment

### ✅ Build Configuration

```bash
# Build for production
npm run build

# Preview build
npm run preview
```

### ✅ Hosting Requirements

- HTTPS enabled
- Proper MIME types for manifest (`application/manifest+json`)
- Service worker served from root or appropriate scope
- Caching headers configured

### ✅ CDN Configuration

```
# Cache-Control headers
/static/*  Cache-Control: public, max-age=31536000, immutable
/index.html  Cache-Control: no-cache
/manifest.json  Cache-Control: no-cache
/service-worker.js  Cache-Control: no-cache
```

## Monitoring

### ✅ Analytics

Track PWA-specific metrics:
- Install rate
- Offline usage
- Service worker errors
- Update acceptance rate
- Performance metrics

### ✅ Error Tracking

```typescript
// Track service worker errors
navigator.serviceWorker.addEventListener('error', (error) => {
  // Log to error tracking service
  console.error('Service Worker error:', error)
})
```

## Quick Validation

Run this checklist before deployment:

```bash
# 1. Build the app
npm run build

# 2. Run Lighthouse audit
npx lighthouse http://localhost:4173 --view

# 3. Check manifest
curl http://localhost:4173/manifest.json

# 4. Verify service worker registration
# Open DevTools > Application > Service Workers

# 5. Test offline mode
# DevTools > Network > Offline checkbox

# 6. Validate icons
# All required sizes present in /icons/
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Service worker not registering | Check HTTPS, check console errors |
| Install prompt not showing | Check manifest, ensure not already installed |
| Offline mode not working | Check service worker caching strategy |
| Icons not showing | Verify icon paths, sizes, and MIME types |
| Updates not applying | Call `skipWaiting()` in service worker |
| iOS standalone detection failing | Use `(window.navigator as any).standalone` |

## Resources

- [web.dev PWA Checklist](https://web.dev/pwa-checklist/)
- [PWA Builder](https://www.pwabuilder.com/)
- [Workbox Documentation](https://developers.google.com/web/tools/workbox)
- [Vite PWA Plugin](https://vite-pwa-org.netlify.app/)
