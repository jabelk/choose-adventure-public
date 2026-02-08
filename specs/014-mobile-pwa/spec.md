# Feature Specification: Mobile-Optimized PWA

**Feature Branch**: `014-mobile-pwa`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Mobile-Optimized PWA - Convert the web app into a Progressive Web App with app manifest, service worker for offline gallery reading, responsive touch-optimized UI, and install prompt."

## User Scenarios & Testing

### User Story 1 - Installable App with Offline Gallery Reading (Priority: P1)

A user on their phone or tablet visits the app over the LAN and gets prompted to "Add to Home Screen." After installing, the app launches in standalone mode with a splash screen and home screen icon — it feels like a native app. Previously viewed stories from the gallery are cached and readable even when the device is offline or away from the LAN. Static assets (CSS, JS, images) are cached so the app shell loads instantly.

**Why this priority**: The core value proposition of a PWA — installability, app-like experience, and offline access to content. Without this, the remaining stories are just UI polish.

**Independent Test**: Install the app to the home screen on a phone. Browse a few stories in the gallery. Turn on airplane mode. Re-open the app and verify the cached stories are fully readable with images. Verify the app launches with a splash screen and runs in standalone mode (no browser chrome).

**Acceptance Scenarios**:

1. **Given** a user visits the app in a mobile browser, **When** the browser detects the PWA manifest and service worker, **Then** the user sees an "Add to Home Screen" install prompt or can install via browser menu.
2. **Given** a user has installed the app to their home screen, **When** they tap the app icon, **Then** the app launches in standalone mode with a themed splash screen and no browser address bar.
3. **Given** a user has previously browsed gallery stories while online, **When** the device goes offline, **Then** the user can still open and read those cached stories with their images and videos.
4. **Given** a user is offline, **When** they try to start a new story or access content not yet cached, **Then** they see a friendly offline message explaining that story generation requires a network connection.
5. **Given** a user returns to the LAN after being offline, **When** they open the app, **Then** new content loads normally and the cache is updated with any new stories they browse.

---

### User Story 2 - Touch-Optimized UI (Priority: P2)

The existing UI is adapted for comfortable use on small screens and touch devices. Choice buttons are large enough for thumb tapping, text is readable without zooming, and the layout adapts fluidly from desktop to phone screens. Interactive elements have proper touch target sizes (minimum 44x44 points) and visual feedback on tap.

**Why this priority**: Even without the PWA shell, a touch-friendly responsive design makes the app usable on phones right now. This is the most impactful UI change for mobile users.

**Independent Test**: Open the app on a phone (or in responsive mode in desktop browser). Navigate through story creation, scene reading, and gallery browsing. Verify all buttons are easily tappable, text is readable, and no horizontal scrolling occurs.

**Acceptance Scenarios**:

1. **Given** a user opens the app on a phone in portrait mode, **When** they view any page, **Then** the content fills the viewport width without horizontal overflow and text is readable without zooming.
2. **Given** a user is reading a scene on a phone, **When** they tap a choice button, **Then** the button has at least 44x44 point touch target and provides visual tap feedback.
3. **Given** a user is viewing the gallery on a phone, **When** they browse story cards, **Then** cards stack vertically in a single column and are easy to tap.
4. **Given** a user on a phone views any form (story prompt, profile edit), **When** they interact with form elements, **Then** inputs are properly sized for touch, keyboards don't obscure content, and form submission is easy.

---

### User Story 3 - Swipe Navigation and Pull-to-Refresh (Priority: P3)

Users can swipe left/right on the scene view to navigate back and forward through story chapters they've already visited. Pull-to-refresh on the gallery and story pages triggers a page reload to fetch fresh content. These gestures make the app feel native and reduce the need for small button taps.

**Why this priority**: Gesture navigation is a polish feature that enhances the native feel but is not essential for basic mobile usability. The app is fully functional with button-based navigation alone.

**Independent Test**: Open a story with multiple explored chapters. Swipe right to go back to the previous chapter, swipe left to go forward. On the gallery page, pull down to refresh the story list.

**Acceptance Scenarios**:

1. **Given** a user is reading a scene that has a parent scene (not the first chapter), **When** they swipe right on the scene content area, **Then** they navigate to the previous chapter (same as pressing the "Go Back" button).
2. **Given** a user is reading a scene where they previously chose a path forward, **When** they swipe left, **Then** they navigate forward to the next scene on the current path.
3. **Given** a user is on the gallery page, **When** they pull down from the top, **Then** the page refreshes and shows the latest story list.
4. **Given** a user swipes on a non-navigable area (e.g., the home page form), **When** the swipe occurs, **Then** nothing unexpected happens — swipe gestures only activate in the scene reader context.

---

### Edge Cases

- What happens when cache storage is full on the device? The app gracefully degrades — new content simply isn't cached, but the app continues working normally online.
- What happens when a cached story's images fail to load offline? Show a placeholder instead of a broken image icon.
- What happens when the service worker updates? The user sees the new version on their next app launch without needing to clear cache manually.
- What happens on very old browsers that don't support service workers? The app works identically to today — all PWA features are progressive enhancements.
- What happens when the user tries to use voice input while offline? Voice input requires network; show a clear message that it's unavailable offline.
- How do swipe gestures interact with the video player? Swipe gestures do not fire when the user is interacting with media elements.

## Requirements

### Functional Requirements

- **FR-001**: The app MUST include a web app manifest that defines the app name, icons, theme color, background color, display mode (standalone), and start URL.
- **FR-002**: The app MUST provide home screen icons in at least two sizes (192x192 and 512x512 pixels).
- **FR-003**: The app MUST include a service worker that caches all static assets (CSS, JS, fonts, icons) on install using a cache-first strategy.
- **FR-004**: The service worker MUST cache gallery story data and associated images/videos when the user browses them, using a network-first strategy with cache fallback.
- **FR-005**: The app MUST serve cached gallery stories and their media when the device is offline.
- **FR-006**: The app MUST display a user-friendly offline indicator when network-dependent features (story generation, voice input) are unavailable.
- **FR-007**: The app MUST show a splash screen with the app icon and name when launched from the home screen.
- **FR-008**: All interactive elements MUST have a minimum touch target size of 44x44 CSS pixels on mobile viewports.
- **FR-009**: The layout MUST be fully responsive with no horizontal overflow at viewport widths from 320px to 1200px.
- **FR-010**: Choice buttons in the scene view MUST provide visual tap feedback (e.g., active state) on touch devices.
- **FR-011**: The scene reader MUST support horizontal swipe gestures for back/forward navigation between explored chapters.
- **FR-012**: Swipe gestures MUST NOT interfere with scrolling, media interaction, or other touch actions.
- **FR-013**: The gallery page and story pages MUST support pull-to-refresh to reload content.
- **FR-014**: The service worker MUST update transparently — new versions activate on next app launch without user intervention.
- **FR-015**: The app MUST function identically to the current version on browsers that do not support service workers (progressive enhancement).
- **FR-016**: The viewport MUST be configured to prevent unwanted zooming while maintaining accessibility zoom capability.
- **FR-017**: The app MUST display an install prompt banner for users who have not yet installed the PWA.

### Key Entities

- **App Manifest**: Metadata describing the app's identity, icons, display preferences, and start URL — consumed by the browser for installation and standalone launch.
- **Service Worker**: Background script managing asset caching, offline content serving, and cache update lifecycle.
- **Cache Store**: Named cache(s) holding versioned static assets and user-browsed story content for offline access.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The app passes a Lighthouse PWA audit with a score of 90 or above on installability and offline capability.
- **SC-002**: Previously browsed gallery stories load fully (text + images) within 1 second when the device is offline.
- **SC-003**: All pages render without horizontal scrolling on viewports as narrow as 320px.
- **SC-004**: 100% of interactive elements (buttons, links, form controls) have touch targets of at least 44x44 CSS pixels on mobile.
- **SC-005**: Swipe navigation between scenes completes within 300ms of gesture recognition.
- **SC-006**: The app can be installed to the home screen on both iOS Safari and Android Chrome.
- **SC-007**: Static assets (app shell) load from cache in under 500ms on repeat visits.

## Assumptions

- The app is served over HTTP on a trusted LAN (not HTTPS). Service workers typically require HTTPS, but browsers allow service workers on `localhost` and some allow them on LAN IPs. The implementation should handle this constraint (e.g., using `localhost` or configuring the browser to allow insecure service workers for the LAN IP).
- Push notifications are explicitly out of scope — this is a LAN-only personal app.
- Background sync is out of scope — there's no offline-to-online write path (story generation is online-only).
- The existing CSS is already somewhat responsive but needs refinement for strict mobile compliance (touch targets, small viewports).
- Home screen icons will be simple generated assets, not professionally designed.

## Scope Boundaries

### In Scope
- Web app manifest and service worker setup
- Offline caching of static assets and browsed gallery stories
- Responsive touch-optimized CSS refinements
- Swipe gestures for scene navigation
- Pull-to-refresh on gallery/story pages
- Install prompt/banner
- Splash screen configuration via manifest

### Out of Scope
- Push notifications
- Background sync / offline story generation queuing
- App store listing (Google Play TWA, Apple App Clip)
- Server-sent events for real-time updates
- Complex cache invalidation strategies
- Offline-first architecture for story creation
