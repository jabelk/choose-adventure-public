# Tasks: Image Gallery View

**Input**: Design documents from `/specs/030-image-gallery-view/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Added in polish phase.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

(No setup needed — no new dependencies.)

---

## Phase 2: Foundational

- [X] T001 [P] Add CSS styles for image gallery overlay in `static/css/style.css` — `.image-gallery-overlay` (fixed position, black bg, z-index 9999), `.gallery-image` (centered, max-width/height 100%), `.gallery-nav-btn` (left/right arrows), `.gallery-close-btn` (top-right), `.gallery-counter` (bottom-center)
- [X] T002 [P] Create `static/js/image-gallery.js` — `initImageGallery(config)` accepting `{images: string[], startIndex: number}`; creates overlay on trigger; supports left/right arrow keys, touch swipe (50px threshold), close button, Escape key; displays position counter; hides nav arrows at boundaries

---

## Phase 3: User Story 1 - View Story Images Full-Screen (Priority: P1)

- [X] T003 [US1] Update `templates/reader.html` — add "Image Gallery" button in the `.reader-nav` section (conditionally shown only if story has images); build image URL list from story scenes in path_history order (main image + extra images per scene, skip scenes without images); include `image-gallery.js` script; initialize with image list JSON
- [X] T004 [US1] Wire the "Image Gallery" button click to `openImageGallery()` function in the JS module

---

## Phase 4: User Story 2 - Counter and Navigation (Priority: P2)

- [X] T005 [US2] Already included in T002 — position counter ("1 / 7") is part of the overlay UI; verify counter updates on navigation

---

## Phase 5: User Story 3 - Both Tiers (Priority: P3)

- [X] T006 [US3] Verification task — routes are inside `create_tier_router()`, template and JS are shared; verify gallery button appears on both Kids and NSFW gallery reader pages

---

## Phase 6: Polish

- [X] T007 Create `tests/test_image_gallery.py` — test gallery button visible when story has images, hidden when no images, visible on both tiers, image list JSON contains correct URLs in path_history order
- [X] T008 Run full test suite to verify no regressions

---

## Notes

- Purely client-side feature — no new server routes.
- Image list built in Jinja2 template from `saved.path_history` + `saved.scenes`.
- Total: 8 tasks across 6 phases
