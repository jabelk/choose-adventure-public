# Routes: Mobile-Optimized PWA

## New Static File Routes

These files are served by FastAPI's existing static file mount. No new route handlers needed.

### GET /static/manifest.json
- **Purpose**: Web app manifest for PWA installability
- **Response**: JSON manifest file
- **Cache**: Should be served with short cache headers (manifest changes on deploys)

### GET /static/sw.js
- **Purpose**: Service worker script
- **Response**: JavaScript file
- **Note**: Service workers must be served from the root scope or registered with the correct scope. If the static mount is at `/static/`, the SW scope will be limited to `/static/`. To get full-scope coverage, the SW may need to be served from `/sw.js` via a dedicated route.

### GET /sw.js (potential dedicated route)
- **Purpose**: Serve the service worker from the root path for full scope coverage
- **Response**: JavaScript file with `Content-Type: application/javascript`
- **Note**: Only needed if the static mount scope (`/static/`) is insufficient. The service worker needs scope `/` to intercept all page requests.

### GET /static/offline.html
- **Purpose**: Offline fallback page shown when a requested page isn't cached
- **Response**: Self-contained HTML page (no server-side template rendering needed)

### GET /static/icons/icon-192.png
- **Purpose**: PWA icon for home screen (192x192)
- **Response**: PNG image

### GET /static/icons/icon-512.png
- **Purpose**: PWA icon for splash screen (512x512)
- **Response**: PNG image

## Modified Routes

No existing route handlers are modified. All changes are in templates and static files.

## Service Worker Interception

The service worker intercepts all fetch requests matching its scope. It does NOT add new server routes — it operates entirely in the browser, intercepting requests before they reach the network.

### Interception Rules

| URL Pattern | Strategy | Behavior |
|-------------|----------|----------|
| `/static/css/*`, `/static/js/*`, `/static/icons/*` | Cache-first | Serve from cache; fall back to network |
| `/*/gallery`, `/*/gallery/*` | Network-first | Try network; fall back to cache if offline |
| `/static/images/*`, `/static/videos/*` | Stale-while-revalidate | Serve cached; update in background |
| `/*/story/start`, `/*/story/choose/*` | Network-only | Story generation requires server — show offline page if unavailable |
| All other requests | Network-first | Try network; fall back to cache or offline page |
