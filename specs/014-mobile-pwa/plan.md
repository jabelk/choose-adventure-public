# Implementation Plan: Mobile-Optimized PWA

**Branch**: `014-mobile-pwa` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/014-mobile-pwa/spec.md`

## Summary

Convert the choose-your-own-adventure web app into a Progressive Web App with installability, offline gallery reading, touch-optimized UI, and gesture navigation. Uses a service worker for multi-tier caching (static assets cache-first, HTML network-first, media stale-while-revalidate), web app manifest for standalone mode, and vanilla JS touch events for swipe navigation.

## Technical Context

**Language/Version**: Python 3 (backend unchanged), Vanilla JavaScript (service worker + gestures)
**Primary Dependencies**: No new pip/npm dependencies. All PWA features are browser-native APIs.
**Storage**: Browser Cache API (via service worker) for offline content
**Testing**: Manual testing via Chrome DevTools (Application tab), Lighthouse PWA audit
**Target Platform**: Mobile browsers (Chrome Android primary, Firefox, iOS Safari degraded)
**Project Type**: Web application (FastAPI + Jinja2 templates + static files)
**Performance Goals**: <500ms app shell load from cache, <1s offline story load
**Constraints**: HTTP-only LAN hosting (no HTTPS), service workers require browser flag on LAN IPs
**Scale/Scope**: Personal app, 1-5 concurrent users on home LAN

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | PWA manifest uses tier-specific start_url. Service worker caches per-URL so tier content stays separate. No cross-tier cache leakage. |
| II. Local-First | PASS | PWA enhances the local-first model — offline reading means content works even without the server. No cloud dependencies added. |
| III. Iterative Simplicity | PASS | No new server dependencies. Service worker is ~80 lines of vanilla JS. No build tools, no framework. |
| IV. Archival by Design | PASS | Offline caching extends the archival principle — stories are accessible even when the server is down. Gallery browsing works offline. |
| V. Fun Over Perfection | PASS | Built-in pull-to-refresh over custom implementation. Simple touch events over gesture libraries. Accept iOS limitations rather than over-engineering HTTPS. |

**Post-design re-check**: All 5 principles PASS.

## Project Structure

### Documentation (this feature)

```text
specs/014-mobile-pwa/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal — no new server models)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── routes.md        # New/modified routes
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (new and modified files)

```text
static/
├── manifest.json            # NEW: Web app manifest
├── sw.js                    # NEW: Service worker
├── offline.html             # NEW: Offline fallback page
├── icons/
│   ├── icon-192.png         # NEW: Home screen icon (192x192)
│   └── icon-512.png         # NEW: Home screen icon (512x512)
├── css/
│   └── style.css            # MODIFIED: Touch targets, mobile responsive fixes, swipe CSS
└── js/
    ├── app.js               # MODIFIED: Install prompt, offline detection
    └── swipe.js             # NEW: Swipe gesture navigation

templates/
├── base.html                # MODIFIED: Add manifest link, SW registration, meta tags
├── scene.html               # MODIFIED: Swipe container data attributes
└── offline.html             # NEW: Offline fallback template (or static HTML)
```

**Structure Decision**: No new server-side code. All PWA features are client-side (manifest, service worker, CSS, JS). The existing FastAPI backend serves the manifest and service worker as static files.

## File Change Map

| File | Action | Purpose |
|------|--------|---------|
| `static/manifest.json` | CREATE | Web app manifest for installability |
| `static/sw.js` | CREATE | Service worker: caching, offline serving |
| `static/offline.html` | CREATE | Friendly offline fallback page |
| `static/icons/icon-192.png` | CREATE | PWA icon 192x192 |
| `static/icons/icon-512.png` | CREATE | PWA icon 512x512 |
| `static/js/swipe.js` | CREATE | Swipe gesture detection for scene navigation |
| `static/js/app.js` | MODIFY | Add install prompt handler, offline detection |
| `static/css/style.css` | MODIFY | Touch targets, mobile responsive, swipe CSS, active states |
| `templates/base.html` | MODIFY | Manifest link, viewport meta, SW registration script, theme-color meta |
| `templates/scene.html` | MODIFY | Swipe container setup, scene navigation data attributes |
| `app/main.py` | MODIFY | Serve manifest.json and sw.js at correct paths (if not already covered by static mount) |
