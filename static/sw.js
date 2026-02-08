// Service Worker — Choose Your Own Adventure PWA
// Cache version constants — increment on deploy to force refresh
const STATIC_CACHE = 'static-v1';
const PAGES_CACHE = 'pages-v1';
const MEDIA_CACHE = 'media-v1';
const CACHE_WHITELIST = [STATIC_CACHE, PAGES_CACHE, MEDIA_CACHE];

// Assets to pre-cache on install
const PRECACHE_URLS = [
    '/static/offline.html',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/tree-map.js',
    '/static/js/voice-input.js',
    '/static/js/lightbox.js',
];

// Offline SVG placeholder for failed image requests
const OFFLINE_IMAGE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
    <rect fill="#1a1a2e" width="400" height="300"/>
    <text fill="#606080" font-family="sans-serif" font-size="16" text-anchor="middle" x="200" y="140">Image unavailable offline</text>
    <text fill="#606080" font-family="sans-serif" font-size="40" text-anchor="middle" x="200" y="190">🖼</text>
</svg>`;

// Install: pre-cache static assets and offline fallback
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) =>
                Promise.all(
                    cacheNames
                        .filter((name) => !CACHE_WHITELIST.includes(name))
                        .map((name) => caches.delete(name))
                )
            )
            .then(() => self.clients.claim())
    );
});

// Fetch: three-tier routing strategy
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Only handle same-origin GET requests
    if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
        return;
    }

    // 1. Cache-first for static CSS, JS, icons
    if (url.pathname.startsWith('/static/css/') ||
        url.pathname.startsWith('/static/js/') ||
        url.pathname.startsWith('/static/icons/')) {
        event.respondWith(cacheFirst(event.request, STATIC_CACHE));
        return;
    }

    // 2. Stale-while-revalidate for images and videos
    if (url.pathname.startsWith('/static/images/') ||
        url.pathname.startsWith('/static/videos/')) {
        event.respondWith(staleWhileRevalidate(event.request, MEDIA_CACHE));
        return;
    }

    // 3. Network-first for HTML document requests
    if (event.request.headers.get('Accept')?.includes('text/html')) {
        event.respondWith(networkFirst(event.request, PAGES_CACHE));
        return;
    }

    // Default: network-first for everything else
    event.respondWith(networkFirst(event.request, PAGES_CACHE));
});

// Cache-first strategy
async function cacheFirst(request, cacheName) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        // For image requests, return SVG placeholder
        if (request.url.match(/\.(png|jpg|jpeg|gif|webp|svg)(\?.*)?$/i)) {
            return new Response(OFFLINE_IMAGE_SVG, {
                headers: { 'Content-Type': 'image/svg+xml' },
            });
        }
        return new Response('Offline', { status: 503 });
    }
}

// Network-first with cache fallback
async function networkFirst(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;

        // For HTML requests, show offline fallback
        if (request.headers.get('Accept')?.includes('text/html')) {
            const offlinePage = await caches.match('/static/offline.html');
            if (offlinePage) return offlinePage;
        }

        return new Response('Offline', { status: 503 });
    }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);

    const fetchPromise = fetch(request)
        .then((response) => {
            if (response.ok) {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch(() => null);

    // Return cached immediately, or wait for network
    if (cached) return cached;

    const response = await fetchPromise;
    if (response) return response;

    // Image/video fallback
    if (request.url.match(/\.(png|jpg|jpeg|gif|webp|svg)(\?.*)?$/i)) {
        return new Response(OFFLINE_IMAGE_SVG, {
            headers: { 'Content-Type': 'image/svg+xml' },
        });
    }

    return new Response('Offline', { status: 503 });
}
