# PWA Troubleshooting Guide

Comprehensive troubleshooting for React Progressive Web App issues.

---

## 🔍 Install Prompt Not Appearing (Chrome/Edge)

### Symptom
`beforeinstallprompt` event doesn't fire, no install button appears in address bar.

### Complete Diagnostic Checklist

Run through this checklist in order:

#### 1. HTTPS Requirement
- [ ] Site served over HTTPS (or `localhost` for development)
- [ ] No mixed content warnings (HTTP resources on HTTPS page)
- [ ] SSL certificate valid (check browser address bar)

**Quick test:**
```bash
# Check URL protocol
echo $PWA_URL | grep "^https://"
# Should return the URL if HTTPS

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com
# Should show valid certificate
```

#### 2. Manifest Validation
- [ ] Manifest file exists and loads (`/manifest.json`)
- [ ] Content-Type header is `application/manifest+json` or `application/json`
- [ ] `name` field present
- [ ] `short_name` field present
- [ ] `start_url` field present
- [ ] `display` set to `standalone` or `fullscreen`
- [ ] `icons` array has at least 192x192 and 512x512 icons
- [ ] **`prefer_related_applications` is `false` or absent** ⚠️

**Quick test:**
```bash
# Verify manifest loads
curl -I https://your-domain.com/manifest.json
# Should return: 200 OK

# Validate manifest content
curl https://your-domain.com/manifest.json | jq .
# Should parse as valid JSON

# Check critical fields
curl https://your-domain.com/manifest.json | jq '{name, short_name, start_url, display, icons: .icons | length}'
```

#### 3. Service Worker Registration
- [ ] Service worker registered successfully
- [ ] Service worker is active (not installing/waiting)
- [ ] Service worker has `fetch` event listener
- [ ] Service worker file accessible (`/sw.js` or `/service-worker.js`)
- [ ] No console errors during registration

**Quick test in DevTools:**
```
1. Open DevTools → Application → Service Workers
2. Check status: Should show "activated and is running"
3. Check scope: Should be "/" or appropriate path
4. No errors shown
```

**Quick test via code:**
```typescript
// Check service worker registration
const checkSW = async () => {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.getRegistration()
    console.log('SW registered:', !!registration)
    console.log('SW active:', !!registration?.active)
    console.log('SW scope:', registration?.scope)
  }
}
```

#### 4. Icon Validation
- [ ] 192x192 icon file exists
- [ ] 512x512 icon file exists
- [ ] **Icon files are EXACT pixel dimensions** (not larger/smaller)
- [ ] Icons are PNG format
- [ ] Icon paths in manifest match actual file locations
- [ ] Icons load without 404 errors

**Quick test:**
```bash
# Verify icon files exist
curl -I https://your-domain.com/android-chrome-192x192.png
curl -I https://your-domain.com/android-chrome-512x512.png
# Both should return: 200 OK

# Verify actual dimensions (requires download)
curl -o test-192.png https://your-domain.com/android-chrome-192x192.png
identify test-192.png
# Should show: 192 x 192

curl -o test-512.png https://your-domain.com/android-chrome-512x512.png
identify test-512.png
# Should show: 512 x 512
```

#### 5. User Engagement Requirements
- [ ] User has been on site for **30+ seconds**
- [ ] User has **interacted with page** (click, tap, scroll)
- [ ] App **not already installed**
- [ ] Not in incognito/private mode (some browsers)

**Note:** These are enforced by the browser and cannot be bypassed programmatically.

**Quick test:**
```typescript
// Track engagement (for debugging)
let engagementTime = 0
let hasInteracted = false

window.addEventListener('load', () => {
  setInterval(() => {
    engagementTime++
    console.log(`Engagement: ${engagementTime}s, Interacted: ${hasInteracted}`)
  }, 1000)
})

window.addEventListener('click', () => hasInteracted = true)
window.addEventListener('scroll', () => hasInteracted = true)
```

#### 6. Chrome DevTools Installability Check

**Most reliable method:**

```
1. Open Chrome DevTools
2. Go to Application tab
3. Click "Manifest" in sidebar
4. Look for "Installability" section at bottom
5. Check status:
   ✅ Green checkmark = Installable
   ❌ Red X = Not installable (reason shown)
```

**Common installability errors:**

| Error Message | Fix |
|---------------|-----|
| "Page does not work offline" | Service worker needs fetch event listener |
| "Manifest does not have a suitable icon" | Add 192x192 and 512x512 PNG icons |
| "No matching service worker detected" | Register service worker at root scope |
| "Service worker does not have a fetch handler" | Add fetch event in service worker |
| "Page is not loaded over HTTPS" | Enable HTTPS or use localhost |

---

## 🔧 Service Worker Not Registering

### Symptom
Console shows "SW registration failed" or service worker doesn't appear in DevTools.

### Diagnostic Steps

#### 1. File Not Found (404)

**Symptom:**
```
❌ TypeError: Failed to register a ServiceWorker
❌ HTTP 404: /sw.js
```

**Checks:**
- [ ] Service worker file exists
- [ ] File is in correct location (usually `/public/sw.js` or `/public/service-worker.js`)
- [ ] Build copies file to output directory (`/dist/`)
- [ ] File path in registration matches actual location

**Fix:**
```typescript
// Verify file exists
fetch('/sw.js').then(r => console.log('SW file exists:', r.ok))

// Check registration path matches file
navigator.serviceWorker.register('/sw.js') // Must match actual file location
```

#### 2. MIME Type Incorrect

**Symptom:**
```
❌ The script has an unsupported MIME type ('text/html')
```

**Checks:**
- [ ] Server sends `Content-Type: application/javascript`
- [ ] Not serving HTML error page as service worker

**Fix (server config):**

```nginx
# Nginx
location ~ /(service-worker|sw)\.js$ {
  add_header Content-Type application/javascript;
  add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

```javascript
// Express
app.get('/sw.js', (req, res) => {
  res.setHeader('Content-Type', 'application/javascript')
  res.setHeader('Cache-Control', 'no-cache')
  res.sendFile(path.join(__dirname, 'dist', 'sw.js'))
})
```

#### 3. Scope Issues

**Symptom:**
```
❌ The path of the provided scope is not under the max scope allowed
```

**Checks:**
- [ ] Service worker file at or above scope level
- [ ] Scope path doesn't exceed service worker location

**Fix:**
```typescript
// ❌ BAD - SW in subdirectory, trying to control root
// File: /js/sw.js
navigator.serviceWorker.register('/js/sw.js', { scope: '/' })
// Error: sw.js can only control /js/*

// ✅ GOOD - SW at root
// File: /sw.js
navigator.serviceWorker.register('/sw.js', { scope: '/' })
// Works: sw.js can control /*
```

#### 4. Syntax Error in Service Worker

**Symptom:**
```
❌ Uncaught SyntaxError: Unexpected token
❌ ServiceWorker script evaluation failed
```

**Checks:**
- [ ] Service worker JavaScript is valid
- [ ] No ES6+ syntax if targeting older browsers
- [ ] No `import` statements (use `importScripts()` instead)
- [ ] No JSX or TypeScript (must be compiled)

**Fix:**
```javascript
// ❌ BAD - ESM syntax in service worker
import { precache } from 'workbox-precaching'

// ✅ GOOD - Use importScripts
importScripts('https://cdn.jsdelivr.net/npm/workbox-cdn@6.5.4/workbox-sw.js')
```

---

## 📵 Offline Mode Not Working

### Symptom
App doesn't work when offline, no offline fallback page shows.

### Diagnostic Steps

#### 1. Service Worker Not Active

**Check:**
```
DevTools → Application → Service Workers
Status should be: "activated and is running"
```

**Fix:** See "Service Worker Not Registering" section above

#### 2. Missing Fetch Event Listener

**Problem:** Service worker doesn't intercept network requests

**Check service worker code:**
```javascript
// ❌ BAD - No fetch event
self.addEventListener('install', (event) => { /* ... */ })
self.addEventListener('activate', (event) => { /* ... */ })
// Missing fetch!

// ✅ GOOD - Has fetch event
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  )
})
```

#### 3. Cache Not Populated

**Check:**
```
DevTools → Application → Cache Storage
Should show cache entries
```

**Fix:** Ensure install event caches static assets:
```javascript
const CACHE_NAME = 'v1'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  )
})
```

#### 4. Offline Fallback Not Configured

**Problem:** No offline.html or fallback response

**Fix:**
```javascript
self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(async () => {
          const cache = await caches.open(CACHE_NAME)
          const fallback = await cache.match('/offline.html')
          return fallback || Response.error()
        })
    )
  }
})
```

---

## 🖼️ Icons Not Displaying Correctly

### Symptom
Broken icon images in manifest, wrong icons on home screen, or default browser icon.

### Diagnostic Steps

#### 1. Icon Dimension Mismatch

**Symptom:** Chrome DevTools shows "Image actual size does not match declared size"

**Fix:** See [`pwa-icon-validation.md`](./pwa-icon-validation.md) for complete guide

**Quick fix:**
```bash
# Verify actual dimensions
identify public/android-chrome-192x192.png
# Must show: 192 x 192

# Regenerate if wrong
convert source.png -resize 192x192! android-chrome-192x192.png
```

#### 2. Icon Files Not Found

**Symptom:** 404 errors in Network tab for icon requests

**Checks:**
- [ ] Icon files in `/public/` directory (Vite/React)
- [ ] Paths in manifest match actual file locations
- [ ] Icon files copied to build output (`/dist/`)

**Fix:**
```bash
# Verify files exist after build
ls -lh dist/*.png

# Verify URLs work
curl -I https://your-domain.com/android-chrome-192x192.png
```

#### 3. iOS Specific Issues

**Symptom:** Wrong icon on iOS home screen

**Problem:** iOS ignores manifest icons, requires `apple-touch-icon`

**Fix:**
```html
<!-- Must have this link tag -->
<link rel="apple-touch-icon" href="/apple-touch-icon.png">

<!-- Icon must be 180x180 PNG -->
```

---

## 🔄 Updates Not Applying

### Symptom
After deployment, users still see old version of app.

### Diagnostic Steps

#### 1. Service Worker Cache Not Updated

**Problem:** Old service worker still serving cached content

**Fix:** Increment cache version

```javascript
// ❌ Before deployment
const CACHE_VERSION = 'v1'

// ✅ After deployment - change version!
const CACHE_VERSION = 'v2'

// Also clean up old caches in activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_VERSION)
          .map(name => caches.delete(name))
      )
    })
  )
})
```

#### 2. Service Worker Not Updating

**Problem:** New service worker waits for old one to finish

**Fix:** Force immediate activation

```javascript
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting()) // Force activation
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // Clean up old caches...
    ]).then(() => self.clients.claim()) // Take control immediately
  )
})
```

#### 3. Browser Cache Blocking Updates

**Problem:** Browser caches service worker file itself

**Fix:** Set proper cache headers for service worker

```nginx
# Nginx - prevent caching of service worker
location ~ /(service-worker|sw)\.js$ {
  add_header Cache-Control "no-cache, no-store, must-revalidate";
  add_header Pragma "no-cache";
  add_header Expires "0";
}
```

```javascript
// Express
app.get('/sw.js', (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
  res.setHeader('Pragma', 'no-cache')
  res.setHeader('Expires', '0')
  res.sendFile(path.join(__dirname, 'dist', 'sw.js'))
})
```

#### 4. No User Notification of Updates

**Problem:** New version available but user not informed

**Fix:** Implement update prompt

```typescript
import { useEffect, useState } from 'react'

export function useServiceWorkerUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false)

  useEffect(() => {
    if (!('serviceWorker' in navigator)) return

    navigator.serviceWorker.ready.then(registration => {
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing

        newWorker?.addEventListener('statechange', () => {
          if (
            newWorker.state === 'installed' &&
            navigator.serviceWorker.controller
          ) {
            setUpdateAvailable(true)
          }
        })
      })
    })
  }, [])

  const applyUpdate = () => {
    navigator.serviceWorker.ready.then(registration => {
      registration.waiting?.postMessage({ type: 'SKIP_WAITING' })
    })
    window.location.reload()
  }

  return { updateAvailable, applyUpdate }
}

// In service worker
self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
})
```

---

## 🍎 iOS-Specific Issues

### App Not Opening in Standalone Mode

**Symptom:** App opens in Safari instead of standalone

**Checks:**
- [ ] `apple-mobile-web-app-capable` meta tag present and set to `yes`
- [ ] User added app via Safari (not Chrome/Edge on iOS)
- [ ] App opened from home screen (not browser)

**Fix:**
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Your App">
```

### Wrong App Title on iOS

**Symptom:** Generic title or wrong text under icon

**Fix:**
```html
<!-- Keep under 12 characters -->
<meta name="apple-mobile-web-app-title" content="YourApp">
```

### Detecting Standalone Mode

```typescript
// Check if running as installed PWA
const isStandalone = () => {
  // iOS
  if ((window.navigator as any).standalone === true) {
    return true
  }

  // Android/Chrome
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return true
  }

  return false
}
```

---

## 🐛 Debugging Tools

### Chrome DevTools

**Application Tab Checks:**

```
1. Manifest
   → Look for errors/warnings
   → Verify installability section

2. Service Workers
   → Check status (should be "activated")
   → Unregister for testing fresh install
   → Check "Update on reload" for development

3. Cache Storage
   → Verify cached assets
   → Clear cache to test fresh install

4. Storage → Clear Storage
   → Unregister service workers
   → Clear all data for fresh start
```

### Console Logging

**Service Worker Registration:**

```typescript
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(registration => {
      console.log('✅ SW registered:', {
        scope: registration.scope,
        installing: !!registration.installing,
        waiting: !!registration.waiting,
        active: !!registration.active
      })

      registration.addEventListener('updatefound', () => {
        console.log('🔄 SW update found')
      })
    })
    .catch(error => {
      console.error('❌ SW registration failed:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      })
    })
}
```

**Service Worker Events:**

```javascript
// In service worker
const logEvent = (eventName, details = {}) => {
  console.log(`[SW] ${eventName}:`, details)
}

self.addEventListener('install', (event) => {
  logEvent('INSTALL')
})

self.addEventListener('activate', (event) => {
  logEvent('ACTIVATE')
})

self.addEventListener('fetch', (event) => {
  logEvent('FETCH', { url: event.request.url, mode: event.request.mode })
})
```

### Lighthouse Audit

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run PWA audit
lighthouse https://your-domain.com --only-categories=pwa --view

# Save report
lighthouse https://your-domain.com --only-categories=pwa --output=html --output-path=./pwa-report.html
```

---

## ⚡ Quick Diagnostic Script

Run this in the browser console for instant diagnostics:

```javascript
(async () => {
  const checks = []

  // HTTPS check
  checks.push({
    name: 'HTTPS',
    pass: location.protocol === 'https:' || location.hostname === 'localhost',
    value: location.protocol
  })

  // Manifest check
  try {
    const manifestResp = await fetch('/manifest.json')
    const manifest = await manifestResp.json()
    checks.push({
      name: 'Manifest loads',
      pass: manifestResp.ok,
      value: manifestResp.status
    })
    checks.push({
      name: 'Manifest has name',
      pass: !!manifest.name,
      value: manifest.name
    })
    checks.push({
      name: 'Manifest has icons',
      pass: manifest.icons?.length >= 2,
      value: `${manifest.icons?.length || 0} icons`
    })
  } catch (e) {
    checks.push({ name: 'Manifest', pass: false, value: e.message })
  }

  // Service Worker check
  if ('serviceWorker' in navigator) {
    const reg = await navigator.serviceWorker.getRegistration()
    checks.push({
      name: 'SW registered',
      pass: !!reg,
      value: reg?.scope || 'Not registered'
    })
    checks.push({
      name: 'SW active',
      pass: !!reg?.active,
      value: reg?.active?.state || 'Not active'
    })
  } else {
    checks.push({ name: 'SW supported', pass: false, value: 'Not supported' })
  }

  // Output results
  console.table(checks)

  const failedChecks = checks.filter(c => !c.pass)
  if (failedChecks.length === 0) {
    console.log('✅ All checks passed!')
  } else {
    console.log(`❌ ${failedChecks.length} checks failed:`)
    failedChecks.forEach(c => console.log(`  - ${c.name}: ${c.value}`))
  }
})()
```

---

## 📋 Troubleshooting Flowchart

```
Install prompt not showing?
├─ Check DevTools → Application → Manifest → Installability
│  └─ Red X? → Fix issue shown
│
├─ HTTPS? → No → Enable HTTPS
│
├─ Manifest valid? → No → Fix manifest.json
│
├─ Icons 192x192 & 512x512? → No → Generate/verify icons
│  └─ See pwa-icon-validation.md
│
├─ Service worker active? → No → Debug SW registration
│
├─ Waited 30s + interacted? → No → Wait and interact
│
└─ Already installed? → Yes → Uninstall and retry
```

---

## 📚 Related Resources

- [pwa-icon-validation.md](./pwa-icon-validation.md) - Icon validation guide
- [pwa-checklist.md](./pwa-checklist.md) - Complete PWA checklist
- [common-pitfalls.md](./common-pitfalls.md) - Anti-patterns to avoid

---

**Remember:** Most PWA issues fall into 5 categories:
1. Icon dimension mismatches
2. Missing HTTPS
3. Invalid manifest
4. Service worker not registered/active
5. User engagement requirements not met

Check these first before diving into complex debugging.
