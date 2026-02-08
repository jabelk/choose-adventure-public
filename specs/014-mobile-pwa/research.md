# Research: Mobile-Optimized PWA

## Decision 1: Service Workers over HTTP on LAN

**Decision**: Use Chrome's `chrome://flags/#unsafely-treat-insecure-origin-as-secure` flag for LAN IP addresses. Document this as a one-time setup step.

**Rationale**: Service workers require "secure contexts" (HTTPS or localhost). LAN IPs like `192.168.x.x` are not secure by default. Chrome's flag is the simplest workaround for a personal LAN app. Firefox has a similar developer setting. Safari has no workaround — accept that Safari on iOS will not get service worker features (the app still works, just without offline caching).

**Alternatives considered**:
- Self-signed HTTPS cert with mkcert: More complex setup, requires trusting certs on every device. Overkill for a personal LAN app.
- Reverse proxy with HTTPS (nginx/caddy): Adds infrastructure complexity for no real security benefit on a home LAN.
- Serve only on localhost and use SSH tunnels: Impractical for family phone use.

## Decision 2: Caching Strategy

**Decision**: Three-tier caching approach:
1. **Cache-first** for static assets (CSS, JS, icons, fonts) — versioned cache name, instant loads
2. **Network-first with cache fallback** for HTML pages (gallery, reader) — fresh content when online, cached when offline
3. **Stale-while-revalidate** for images and videos — serve cached immediately, update in background

**Rationale**: Static assets rarely change (only on deploys), so cache-first is fast and safe. HTML pages contain dynamic story data so network-first ensures freshness. Images/videos never change after generation, so stale-while-revalidate gives instant loads without staleness risk.

**Alternatives considered**:
- Cache-only for everything: Too aggressive — gallery HTML updates when new stories are added
- Network-only with offline fallback page: Misses the point — we want actual stories readable offline
- Workbox library: Adds dependency for something achievable in ~80 lines of vanilla JS

## Decision 3: Swipe Gesture Implementation

**Decision**: Vanilla JS touch event listeners with horizontal distance threshold (150px) and velocity detection (0.3 px/ms). Use `touch-action: pan-y pinch-zoom` CSS to let the browser handle vertical scrolling.

**Rationale**: The story reader has a simple left/right navigation model. A 150px threshold with velocity detection feels natural and prevents false triggers from scrolling. No library needed for this simple use case.

**Alternatives considered**:
- Hammer.js: Adds 7KB dependency for a single gesture we can implement in ~30 lines
- Pointer Events API: More universal but more complex; we only need touch on mobile
- CSS scroll snap: Different UX model (carousel-style) that doesn't map well to server-rendered page navigation

## Decision 4: Pull-to-Refresh

**Decision**: Use the browser's built-in pull-to-refresh in standalone PWA mode (Android). Add `overscroll-behavior-y: contain` only on pages where we want to disable it (scene view, to avoid conflicts with swipe gestures). No custom pull-to-refresh implementation.

**Rationale**: Android Chrome's built-in pull-to-refresh works out of the box in standalone mode and matches user expectations. Custom implementations add complexity for minimal benefit on a personal app. iOS standalone mode has inconsistent pull-to-refresh behavior but a manual refresh button is acceptable.

**Alternatives considered**:
- Custom pull-to-refresh with spinner animation: Over-engineered for a personal app
- Disable entirely and use refresh button: Loses the native feel on Android

## Decision 5: iOS PWA Limitations

**Decision**: Accept iOS limitations. Show an install instruction banner for iOS users (since there's no automatic install prompt). Service worker features will only work on Chrome/Firefox via the flag workaround — iOS Safari won't get offline support.

**Rationale**: iOS Safari has no flag to allow service workers over HTTP. Since this is a LAN app without HTTPS, iOS devices will use the app as a regular web page (which still works fine — they just can't read stories offline). The touch UI improvements benefit all devices regardless.

**Alternatives considered**:
- Set up HTTPS just for iOS: Disproportionate effort for one platform on a personal app
- Skip PWA entirely: Loses the native-feel benefits on Android which is the primary mobile device

## Decision 6: App Icons

**Decision**: Generate simple SVG-based PNG icons at 192x192 and 512x512 using a book emoji or simple design. Create both sizes as static files.

**Rationale**: This is a personal hobby app — professionally designed icons are unnecessary. A simple book/adventure icon serves the purpose.

**Alternatives considered**:
- Use favicon generator service: External dependency for a one-time task
- Skip icons: Manifest requires them for installability
