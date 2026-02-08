# Data Model: Mobile-Optimized PWA

This feature adds no new server-side models. All data structures are client-side browser APIs.

## Client-Side Entities

### App Manifest (manifest.json)
- `name`: Full app name ("Choose Your Own Adventure")
- `short_name`: Abbreviated name for home screen ("Adventure")
- `start_url`: Landing page URL ("/")
- `display`: Display mode ("standalone")
- `background_color`: Splash screen background color
- `theme_color`: Browser UI theme color
- `icons`: Array of icon objects with `src`, `sizes`, `type`

### Cache Stores (Browser Cache API)
- `static-v1`: Versioned cache for CSS, JS, fonts, icons — cache-first strategy
- `pages-v1`: Versioned cache for HTML pages (gallery, reader) — network-first strategy
- `media-v1`: Versioned cache for images and videos — stale-while-revalidate strategy

### Service Worker State
- Registration status: registered/failed/unsupported
- Cache version: tracked via cache name suffix (v1, v2, etc.)
- Online/offline status: tracked via `navigator.onLine` and `online`/`offline` events

## No Server-Side Changes

The existing Pydantic models (Story, Scene, Image, SavedStory, etc.) are unchanged. The service worker intercepts fetch requests at the browser level — the server is unaware of the caching layer.
