# Tasks: Image Retry & Polish

**Input**: Design documents from `/specs/005-image-polish/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested — manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Shared CSS & Layout)

**Purpose**: Update the image container to prevent layout shift and prepare CSS infrastructure used by all user stories.

- [x] T001 Update `.scene-image-container` to use `aspect-ratio: 1` (1024x1024 images) and add `position: relative` for overlay positioning in `static/css/style.css`
- [x] T002 [P] Replace `.image-placeholder-shimmer` with a CSS pulsing gradient animation (`@keyframes pulse-gradient`) and remove the spinner element in `static/css/style.css`
- [x] T003 [P] Add `.image-progress-text` style for rotating progress messages inside the placeholder in `static/css/style.css`

**Checkpoint**: Image container has fixed aspect ratio, shimmer replaced with pulse animation. No layout shift foundation is in place.

---

## Phase 2: User Story 1 — Retry Failed Images (Priority: P1) 🎯 MVP

**Goal**: When image generation fails, show a "Retry" button instead of static "Image unavailable". Clicking retry triggers a new generation attempt without page reload.

**Independent Test**: Set an invalid OpenAI API key, start a story, verify failed state shows retry button. Restore key, click Retry, verify image generates.

### Implementation for User Story 1

- [x] T004 [US1] Add `POST /{tier}/story/image/{scene_id}/retry` endpoint in `app/routes.py` — load session, find scene, guard against GENERATING status, reset image (status→PENDING, url→None, error→None), start background task, save progress, return JSON
- [x] T005 [US1] Add `showFailedState(container, sceneId)` function in `static/js/app.js` — render error message + retry button that calls `retryImage(sceneId)`
- [x] T006 [US1] Add `retryImage(sceneId)` function in `static/js/app.js` — POST to retry endpoint, on success show generating placeholder, start polling with `pollImageStatus(sceneId)`
- [x] T007 [US1] Update `pollImageStatus()` in `static/js/app.js` — on failure status call `showFailedState()` instead of `showFallback()`, on timeout call `showFailedState()`
- [x] T008 [US1] Update failed state markup in `templates/scene.html` — replace static "Image unavailable" div with a container that includes retry button markup, passing `scene.scene_id` for JS
- [x] T009 [US1] Add `.image-failed-state` and `.btn-retry` CSS styles in `static/css/style.css` — error message + button styled with tier accent colors

**Checkpoint**: Failed images show retry button. Clicking retry triggers new generation. Repeated failures show retry again.

---

## Phase 3: User Story 2 — Improved Generation Progress (Priority: P1)

**Goal**: Replace the basic spinner with a polished pulsing gradient animation and rotating progress text. Image fade-in on completion. No layout shift.

**Independent Test**: Start a new story, observe pulsing gradient (not spinner), progress text rotating, smooth fade-in when image arrives, no layout shift.

### Implementation for User Story 2

- [x] T010 [US2] Update generating state markup in `templates/scene.html` — replace spinner+span with pulsing placeholder div containing progress text element, add `data-scene-id` attribute for JS
- [x] T011 [US2] Add rotating progress messages in `static/js/app.js` — array of messages ("Creating your illustration...", "Painting the scene...", etc.) that cycle every 3 seconds during generation
- [x] T012 [US2] Update `showImage()` in `static/js/app.js` to transition from generating placeholder to image smoothly — clear placeholder, insert image with opacity 0, fade in
- [x] T013 [US2] Ensure `pollImageStatus()` re-shows generating placeholder when re-entered (for background generation returning to scene) in `static/js/app.js`

**Checkpoint**: Generating state shows pulsing gradient + rotating text. Image fades in smoothly. No layout shift on transition.

---

## Phase 4: User Story 3 — Regenerate Any Image (Priority: P2)

**Goal**: Completed images show a small "Regenerate" button overlay. Clicking it replaces the image with the generating state and requests a new image.

**Independent Test**: View a scene with a completed image. Hover to see "Regenerate" button (desktop). Click it. Verify image replaced with loading, then new image appears.

### Implementation for User Story 3

- [x] T014 [US3] Add regenerate button markup to completed image state in `templates/scene.html` — small overlay button in bottom-right corner of image container, only when not in gallery reader context
- [x] T015 [US3] Add `.btn-regenerate` CSS styles in `static/css/style.css` — overlay positioning, hover-reveal on desktop, always visible on mobile, themed with accent colors
- [x] T016 [US3] Wire regenerate button click to `retryImage(sceneId)` in `static/js/app.js` — reuse the retry function since the backend endpoint handles both retry and regenerate
- [x] T017 [US3] Update `showImage()` in `static/js/app.js` to include regenerate button in the completed image DOM, with click handler calling `retryImage()`

**Checkpoint**: Completed images show regenerate overlay. Clicking regenerate replaces image with loading state, new image appears.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Duplicate prevention, gallery reader exclusion, tier theming verification, progress save consistency.

- [x] T018 Disable retry/regenerate buttons during generation — add `disabled` attribute and visual state while `pollImageStatus` is active in `static/js/app.js`
- [x] T019 Verify gallery reader (`templates/reader.html`) does NOT show regenerate button — confirm reader template uses plain `<img>` without interactive controls (should require no changes)
- [x] T020 Verify tier theming — confirm pulsing gradient, buttons, and failed state use CSS custom properties (`var(--accent)`, `var(--bg-secondary)`, etc.) so both kids and nsfw tiers render correctly
- [x] T021 Run quickstart.md full validation — test all 8 scenarios manually, verify all acceptance criteria pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — start immediately
- **Phase 2 (US1 - Retry)**: Depends on Phase 1 (needs updated container + CSS)
- **Phase 3 (US2 - Progress)**: Depends on Phase 1 (needs pulsing animation CSS)
- **Phase 4 (US3 - Regenerate)**: Depends on Phase 2 (reuses retry endpoint + `retryImage()` function)
- **Phase 5 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Retry)**: Can start after Phase 1. No dependency on other stories.
- **US2 (Progress)**: Can start after Phase 1. Independent from US1 (different files/functions).
- **US3 (Regenerate)**: Depends on US1 (reuses `retryImage()` and the POST retry endpoint).

### Within Each User Story

- Route changes before JS changes (endpoint must exist for fetch calls)
- CSS before template changes (styles must exist for classes)
- Template markup before JS behavior (DOM elements must exist for JS to target)

### Parallel Opportunities

- T002 and T003 can run in parallel (different CSS sections)
- US1 (Phase 2) and US2 (Phase 3) can proceed in parallel after Phase 1:
  - US1 touches: routes.py, app.js (showFailedState, retryImage), scene.html (failed state), style.css (failed styles)
  - US2 touches: scene.html (generating state), app.js (progress messages, showImage update), style.css (progress text)
  - Minimal file overlap — coordinate scene.html and app.js edits

---

## Parallel Example: Phase 2 + Phase 3

```bash
# After Phase 1 completes, US1 and US2 can start in parallel:

# US1 thread:
Task: "Add POST retry endpoint in app/routes.py"
Task: "Add showFailedState() in static/js/app.js"
Task: "Add retryImage() in static/js/app.js"

# US2 thread (parallel):
Task: "Update generating state markup in templates/scene.html"
Task: "Add rotating progress messages in static/js/app.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational CSS
2. Complete Phase 2: Retry Failed Images
3. **STOP and VALIDATE**: Test retry flow end-to-end
4. Users can now recover from failed images — highest-impact improvement

### Incremental Delivery

1. Phase 1 → Foundation ready (layout shift fixed, pulse animation)
2. Phase 2 (US1) → Retry works → Test independently (MVP!)
3. Phase 3 (US2) → Polished loading → Test independently
4. Phase 4 (US3) → Regenerate works → Test independently
5. Phase 5 → Polish, verify gallery exclusion, tier theming

---

## Notes

- No model changes needed — existing `Image`/`ImageStatus` supports all states
- The retry endpoint handles both retry (FAILED→GENERATING) and regenerate (COMPLETE→GENERATING)
- All CSS uses `var(--accent)` and theme custom properties for automatic tier theming
- Gallery reader uses `reader.html` template which is separate from `scene.html` — no changes needed
- Background generation already works (existing `asyncio.create_task`) — FR-007 is satisfied by existing architecture
