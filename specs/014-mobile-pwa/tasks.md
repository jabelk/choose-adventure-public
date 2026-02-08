# Tasks: Mobile-Optimized PWA

**Input**: Design documents from `/specs/014-mobile-pwa/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create PWA foundation files (manifest, icons, base template changes) that all user stories depend on.

- [X] T001 [P] Create the web app manifest at static/manifest.json — include `name` ("Choose Your Own Adventure"), `short_name` ("Adventure"), `start_url` ("/"), `display` ("standalone"), `background_color` ("#1a1a2e"), `theme_color` ("#f0c040"), and `icons` array with entries for 192x192 and 512x512 PNG icons at `/static/icons/icon-192.png` and `/static/icons/icon-512.png`.
- [X] T002 [P] Generate PWA icon files — create static/icons/icon-192.png (192x192) and static/icons/icon-512.png (512x512). Use Python PIL/Pillow to generate simple book-themed icons with the app's accent color (#f0c040) background and a book emoji or "A" letter. Create the static/icons/ directory.
- [X] T003 Update templates/base.html — add `<link rel="manifest" href="/static/manifest.json">` in the `<head>`. Add `<meta name="theme-color" content="#f0c040">`. Add `<meta name="apple-mobile-web-app-capable" content="yes">`. Add `<meta name="apple-mobile-web-app-status-bar-style" content="default">`. Ensure the existing viewport meta tag has `viewport-fit=cover`. Add a service worker registration `<script>` block at the end of `<body>` that checks `if ('serviceWorker' in navigator)` and registers `/sw.js` with `scope: '/'`.
- [X] T004 Add a dedicated route in app/main.py to serve the service worker from `/sw.js` — the service worker must be served from the root path (not `/static/sw.js`) to have scope over the entire app. Add a `GET /sw.js` route that reads `static/sw.js` and returns it with `Content-Type: application/javascript` and `Cache-Control: no-cache` headers. Also add a `GET /manifest.json` route that serves `static/manifest.json` with `Content-Type: application/json`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the service worker with caching logic and the offline fallback page. These are required before any user story features can work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create the service worker at static/sw.js — implement the core service worker lifecycle: (1) `install` event: open a `static-v1` cache and pre-cache the offline fallback page (`/static/offline.html`) plus key static assets (`/static/css/style.css`, `/static/js/app.js`, `/static/js/tree-map.js`, `/static/js/voice-input.js`). Call `self.skipWaiting()`. (2) `activate` event: delete any old caches whose names don't match the current version whitelist (`static-v1`, `pages-v1`, `media-v1`). Call `clients.claim()`. (3) `fetch` event: implement three-tier routing — cache-first for `/static/css/`, `/static/js/`, `/static/icons/` requests; network-first with cache fallback for HTML document requests (cache in `pages-v1`); stale-while-revalidate for `/static/images/` and `/static/videos/` requests (cache in `media-v1`). For network failures on uncached pages, return the offline fallback.
- [X] T006 Create the offline fallback page at static/offline.html — a self-contained HTML page (no Jinja2 templating, no external dependencies beyond inline CSS) that shows a friendly message: "You're offline — Story generation requires a network connection, but your previously browsed stories are available in the Gallery." Include a link to the gallery (`/kids/gallery` and `/nsfw/gallery`) and a "Try Again" button that calls `location.reload()`. Style it to match the app's dark theme using inline CSS.

**Checkpoint**: Service worker registers, caches static assets, and shows offline fallback. PWA foundation ready for user story features.

---

## Phase 3: User Story 1 — Installable App with Offline Gallery Reading (Priority: P1) 🎯 MVP

**Goal**: Users can install the app to their home screen, browse gallery stories offline, and see a splash screen on launch.

**Independent Test**: Install the app via Chrome. Browse gallery stories online. Go offline. Verify cached stories load with images. Verify offline fallback appears for uncached content.

### Implementation for User Story 1

- [X] T007 [P] [US1] Add install prompt handling to static/js/app.js — listen for the `beforeinstallprompt` event, store the event object, and show a dismissible install banner at the top of the page. The banner should say "Install this app for the best experience" with an "Install" button that calls `event.prompt()`. After the user installs or dismisses, hide the banner. Store dismissal in `localStorage` so the banner doesn't reappear. Also add `online`/`offline` event listeners that toggle a `.offline-indicator` element visibility.
- [X] T008 [P] [US1] Add CSS for the install banner and offline indicator in static/css/style.css — add styles for `.install-banner` (fixed top banner with accent background, dismiss button), `.offline-indicator` (subtle bar at top showing "You're offline — browsing cached content"), and `.install-banner-hidden` (display: none). The offline indicator should use a muted warning style.
- [X] T009 [US1] Add the install banner and offline indicator HTML to templates/base.html — add a `<div class="install-banner" id="install-banner" style="display:none">` before the main content with the install button and dismiss button. Add a `<div class="offline-indicator" id="offline-indicator" style="display:none">` that shows when offline. Wire up the offline indicator visibility in the SW registration script block: `window.addEventListener('online', ...)` and `window.addEventListener('offline', ...)`.
- [X] T010 [US1] Enhance the service worker fetch handler in static/sw.js for gallery offline support — ensure that when a user browses a gallery story page (`/*/gallery/*/`), the HTML response AND all embedded image/video URLs are cached. For gallery list pages (`/*/gallery`), cache the response in `pages-v1`. For reader pages (`/*/gallery/*/*`), cache in `pages-v1`. The stale-while-revalidate strategy for `/static/images/*` and `/static/videos/*` already handles media caching from T005 — verify it works for gallery reader images by testing with DevTools offline mode.
- [X] T011 [US1] Verify PWA installability end-to-end — open Chrome DevTools → Application → Manifest and confirm no errors. Run Lighthouse PWA audit and check installability criteria pass. Test the install flow: click the install banner → app installs → reopens in standalone mode with splash screen. Test offline: browse 2 gallery stories online → go offline → verify both stories load from cache with images.

**Checkpoint**: App is installable, launches in standalone mode, gallery stories work offline. This is the MVP.

---

## Phase 4: User Story 2 — Touch-Optimized UI (Priority: P2)

**Goal**: All UI elements are comfortable to use on phone screens with proper touch target sizes and responsive layout.

**Independent Test**: Open on a 375px-wide viewport. Navigate through all pages. Verify no horizontal overflow, all buttons are tappable, and tap feedback is visible.

### Implementation for User Story 2

- [X] T012 [P] [US2] Add touch target and responsive fixes to static/css/style.css — audit and fix all interactive elements: (1) Ensure `.choice-btn` has `min-height: 48px` and `padding: 14px 16px` on mobile. (2) Ensure `.btn`, `.btn-primary`, `.btn-secondary` have `min-height: 44px`. (3) Ensure `.model-option .option-card` has `min-height: 44px`. (4) Add `@media (max-width: 600px)` rules: `.story-grid` single column, `.scene-header` stack vertically, `.resume-banner` stack vertically, `.gallery-link` full width. (5) Ensure `.prompt-form textarea` has `font-size: 16px` on mobile (prevents iOS auto-zoom).
- [X] T013 [P] [US2] Add touch feedback (active states) to static/css/style.css — add `:active` pseudo-class styles for all tappable elements: `.choice-btn:active` (scale down slightly and darken), `.btn:active` (scale 0.97), `.suggestion-chip:active` (background change), `.story-card:active` (slight press effect). Use `@media (hover: none)` to only apply on touch devices to avoid desktop interference.
- [X] T014 [US2] Fix any horizontal overflow issues — test all pages at 320px viewport width. Common fixes: ensure `.scene-header` wraps text with `flex-wrap: wrap` and `.chapter` uses `overflow: hidden; text-overflow: ellipsis`. Ensure `.model-group .model-option` wraps properly at small widths. Add `overflow-x: hidden` to `body` as a safety net. Ensure images use `max-width: 100%`.
- [X] T015 [US2] Verify touch optimization on mobile — test on a real phone or Chrome responsive mode at 375px: (1) All buttons are easy to tap without accidental adjacent taps. (2) Text is readable without zooming. (3) Forms work well with on-screen keyboard. (4) Gallery cards are easy to tap. (5) No horizontal scrolling on any page.

**Checkpoint**: All pages are touch-friendly and fully responsive from 320px to 1200px.

---

## Phase 5: User Story 3 — Swipe Navigation and Pull-to-Refresh (Priority: P3)

**Goal**: Users can swipe left/right to navigate between explored story chapters and pull-to-refresh on gallery pages.

**Independent Test**: Open a story with multiple chapters. Swipe right to go back, swipe left to go forward. On gallery page, pull down to refresh.

### Implementation for User Story 3

- [X] T016 [P] [US3] Create the swipe gesture handler at static/js/swipe.js — implement a `SwipeNav` class/function that: (1) listens for `touchstart`, `touchmove`, `touchend` on a target element. (2) Tracks touch start/end X/Y coordinates and timestamps. (3) Detects horizontal swipes when `Math.abs(deltaX) > 150` OR velocity > 0.3 px/ms, AND `Math.abs(deltaX) > Math.abs(deltaY)` (horizontal dominates vertical). (4) Ignores swipes that start on `video`, `canvas`, or `.tree-map-container` elements (check `event.target.closest()`). (5) Calls a `onSwipeLeft` or `onSwipeRight` callback. Export an `initSwipeNav(element, callbacks)` function.
- [X] T017 [P] [US3] Add swipe-related CSS to static/css/style.css — add `touch-action: pan-y pinch-zoom` to `.scene-text` and `.scene-image-container` (allow vertical scroll, JS handles horizontal). Add `overscroll-behavior-x: none` to `body` in standalone PWA mode (detected via `@media (display-mode: standalone)`). Add a subtle swipe hint animation class `.swipe-hint` for first-time users (optional).
- [X] T018 [US3] Integrate swipe navigation into templates/scene.html — add `<script src="/static/js/swipe.js"></script>` in the scripts block. Add a script that calls `initSwipeNav` on the scene content area. For swipe right (back): submit the "Go Back" form programmatically (same as clicking the Go Back button). For swipe left (forward): if the current scene has a `next_scene_id` in `path_history`, navigate to it. Pass `scene.parent_scene_id` and the next scene ID (if any) as data attributes on the scene container so swipe.js can read them. Also pass `url_prefix` for building navigation URLs.
- [X] T019 [US3] Configure pull-to-refresh behavior — for the gallery and reader pages, allow the browser's built-in pull-to-refresh (default behavior in standalone PWA mode on Android). For the scene view, add `overscroll-behavior-y: contain` to prevent pull-to-refresh (since swipe gestures are active). This is CSS-only — add the rule in static/css/style.css scoped to the scene page (`.scene-text` parent or a new `.scene-container` wrapper).
- [X] T020 [US3] Verify swipe and pull-to-refresh — test on a real phone or touch simulator: (1) Swipe right on a scene → navigates back. (2) Swipe left on a scene → navigates forward (if path exists). (3) Swipe on home page → nothing happens. (4) Swipe over a video element → swipe is ignored. (5) Pull down on gallery page → page refreshes. (6) Pull down on scene page → no refresh (overscroll contained).

**Checkpoint**: Swipe navigation works in scene view. Pull-to-refresh works on gallery. Gestures don't interfere with other interactions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, cache management, and final validation

- [X] T021 Add cache version management comment to static/sw.js — add a clear comment at the top with the cache version constants (`STATIC_CACHE`, `PAGES_CACHE`, `MEDIA_CACHE`) and instructions for incrementing versions on deploy. Ensure the `activate` handler properly cleans up old cache versions.
- [X] T022 Handle offline image fallback — in the service worker fetch handler, when an image request fails and there's no cached version, return a simple SVG placeholder (inline data URI) instead of letting the browser show a broken image icon. Create a small inline SVG in the service worker that says "Image unavailable offline".
- [X] T023 Add `apple-touch-icon` link tags to templates/base.html — add `<link rel="apple-touch-icon" href="/static/icons/icon-192.png">` for iOS home screen icon support. iOS doesn't use the manifest icons — it needs this explicit link tag.
- [X] T024 Verify progressive enhancement — open the app in a browser WITHOUT the Chrome flag (service worker won't register). Verify: (1) All pages load and work normally. (2) No JavaScript errors related to missing service worker. (3) Install banner doesn't appear (since SW isn't available). (4) Swipe navigation still works (it's touch events, not SW-dependent).
- [X] T025 Run full quickstart.md validation (all 10 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T004)
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T005-T006)
- **User Story 2 (Phase 4)**: Can start after Setup (Phase 1) — CSS-only changes, independent of service worker
- **User Story 3 (Phase 5)**: Can start after Setup (Phase 1) — JS gesture code, independent of service worker
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (service worker must exist) — foundation for offline features
- **User Story 2 (P2)**: Independent of US1 — CSS-only responsive/touch improvements
- **User Story 3 (P3)**: Independent of US1 — JS gesture navigation, no SW dependency

### Within Each User Story

- Templates and CSS changes can run in parallel (different files)
- JS changes that depend on template data attributes must follow template changes
- Verification tasks must follow all implementation tasks in that story

### Parallel Opportunities

- T001 and T002 can run in parallel (manifest vs icons — different files)
- T007 and T008 can run in parallel (JS vs CSS — different files)
- T012 and T013 can run in parallel (both CSS but different concerns, same file — do sequentially)
- T016 and T017 can run in parallel (JS vs CSS — different files)
- US2 and US3 can start in parallel after Phase 1 (both are CSS/JS changes)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (manifest, icons, base template, SW route)
2. Complete Phase 2: Foundational (service worker, offline page)
3. Complete Phase 3: User Story 1 (install prompt, offline gallery, verification)
4. **STOP and VALIDATE**: Test installability, offline reading, splash screen
5. The app is a PWA with offline gallery reading — core value delivered

### Incremental Delivery

1. Setup + Foundational → PWA shell ready with offline fallback
2. Add User Story 1 → Installable app with offline gallery reading
3. Add User Story 2 → Touch-optimized responsive UI
4. Add User Story 3 → Swipe navigation and pull-to-refresh
5. Each story adds capability without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No new pip dependencies — all PWA features are browser-native APIs
- Service worker MUST be served from `/sw.js` (root scope) not `/static/sw.js`
- Chrome flag `chrome://flags/#unsafely-treat-insecure-origin-as-secure` must be set on mobile devices to test service worker on LAN IP
- iOS Safari will NOT get service worker features (no HTTP flag workaround) — accept gracefully
- Cache version names should be incremented on each deploy to force cache refresh
- Commit after each phase completion
- Stop at any checkpoint to validate independently
