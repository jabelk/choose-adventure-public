# Tasks: Coloring Page Export

**Input**: Design documents from `/specs/028-coloring-page-export/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not explicitly requested in the spec. Tests added in polish phase for completeness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new dependencies needed. Skip to foundational.

(No tasks in this phase.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Service method and CSS that all user stories depend on.

- [X] T001 [P] Add `generate_coloring_page()` method to `ImageService` in `app/services/image.py` — accepts `image_prompt: str`, `scene_id: str`, and `image_model: str`; checks if `static/images/{scene_id}_coloring.png` exists on disk and returns the URL immediately if so; otherwise builds the coloring page prompt by prepending "Simple black and white coloring page line art, thick outlines, no shading, no color, no grayscale, suitable for children to color in. Scene: " to the original prompt; calls the same image generation backend as `generate_image()`; saves result as `static/images/{scene_id}_coloring.png`; returns the URL path `/static/images/{scene_id}_coloring.png`
- [X] T002 [P] Add CSS styles for coloring page UI in `static/css/style.css` — `.coloring-page-section` container, `.btn-coloring` button (styled like existing `.btn-export`), `.coloring-page-image` display area, `.coloring-downloads` row for PNG/PDF download links, `.coloring-loading` spinner state, `.coloring-error` error message with retry

**Checkpoint**: Service and styles ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Generate and Download Coloring Page PNG (Priority: P1)

**Goal**: Users can click "Coloring Page" on a gallery reader scene, see a generated line-art image, and download it as PNG.

**Independent Test**: Navigate to a gallery story reader, click "Coloring Page" on a scene with an image prompt, verify line-art image appears inline with a "Download PNG" link.

### Implementation for User Story 1

- [X] T003 [US1] Add `GET /gallery/{story_id}/{scene_id}/coloring` route in `app/routes.py` — MUST be declared before the catch-all `GET /gallery/{story_id}/{scene_id}` route (same pattern as 027-sequel-mode); load SavedStory, verify tier, get scene's `image_prompt`, call `image_service.generate_coloring_page(image_prompt, scene_id, saved.image_model)`, return JSON `{"url": coloring_url}` on success or `{"error": message}` on failure with 500 status
- [X] T004 [US1] Create `static/js/coloring-page.js` — exports `initColoringPage(config)` accepting `{coloringUrl, pdfUrl, sceneHasPrompt}`; on button click: disable button, show loading spinner, fetch `coloringUrl`, on success display inline image + download links (PNG direct link, PDF link), on error show error message with retry button; hide button entirely if `sceneHasPrompt` is false
- [X] T005 [US1] Update `templates/reader.html` — add a "Coloring Page" button below the scene image container (only if `scene.image_prompt`); add a `<div id="coloring-page-area">` placeholder for the generated image and download links; include `coloring-page.js` script; initialize with `initColoringPage({coloringUrl, pdfUrl, sceneHasPrompt: bool})`

**Checkpoint**: Core coloring page generation works. Users can generate and download PNG from any gallery scene.

---

## Phase 4: User Story 2 - Download Coloring Page as Print-Ready PDF (Priority: P2)

**Goal**: Users can download a generated coloring page as a single-page print-ready PDF.

**Independent Test**: Generate a coloring page, click "Download PDF," verify a valid PDF downloads with the image sized for US Letter paper.

### Implementation for User Story 2

- [X] T006 [US2] Add `export_coloring_pdf()` function in `app/services/export.py` — accepts a PNG file path, creates a single-page PDF using fpdf2 with US Letter paper (216mm x 279mm), 20mm margins, image centered and scaled to fit page width (176mm) while maintaining aspect ratio; returns PDF bytes
- [X] T007 [US2] Add `GET /gallery/{story_id}/{scene_id}/coloring/pdf` route in `app/routes.py` — MUST be declared before both the `/coloring` route and the catch-all `/{scene_id}` route; load SavedStory, verify tier, check if `static/images/{scene_id}_coloring.png` exists on disk, if not return 404 JSON error, if yes call `export_coloring_pdf()` with the file path, return PDF as `Response` with `application/pdf` content type and `Content-Disposition: attachment` header with filename `{story_title}_coloring_{scene_id}.pdf`
- [X] T008 [US2] Update `static/js/coloring-page.js` to include "Download PDF" link pointing to the PDF endpoint URL alongside the "Download PNG" link in the coloring page display area

**Checkpoint**: PDF download works. Users can generate a coloring page and download as either PNG or PDF.

---

## Phase 5: User Story 3 - Coloring Pages on Both Tiers (Priority: P3)

**Goal**: NSFW tier users can generate coloring pages identically to kids tier.

**Independent Test**: Navigate to an NSFW gallery story reader, click "Coloring Page," verify it generates and downloads identically to the kids tier.

### Implementation for User Story 3

- [X] T009 [US3] Verify both tiers work — the routes are defined inside `create_tier_router()` which already scopes to each tier; no code changes needed; run manual verification that the coloring page button appears on an NSFW gallery story reader page and generates correctly (this is a verification task, not a code task)

**Checkpoint**: Both tiers confirmed working.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation across all user stories.

- [X] T010 Create `tests/test_coloring_page.py` with tests covering: coloring page button visible when scene has image_prompt, button hidden when scene has no image_prompt, GET /coloring returns JSON with URL, GET /coloring/pdf returns PDF response, cross-tier coloring rejected, missing story/scene redirects, coloring page cached on disk (second request returns same URL without regeneration)
- [X] T011 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — service method and CSS can start immediately
- **User Story 1 (Phase 3)**: Depends on T001 + T002 (service method and CSS)
- **User Story 2 (Phase 4)**: Depends on US1 complete (PDF route needs coloring page to exist)
- **User Story 3 (Phase 5)**: Depends on US1 complete (needs working coloring page feature to verify)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T001 and T002 (service method and CSS) can run in parallel (different files)
- T003, T004, and T005 within US1 are sequential (route → JS → template integration)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 + T002 (service + CSS)
2. Complete T003 + T004 + T005 (route + JS + template)
3. **STOP and VALIDATE**: Generate a coloring page from a gallery story, verify PNG downloads
4. This alone delivers the core value — one-click coloring page from any gallery scene

### Incremental Delivery

1. T001 + T002 → Foundation ready
2. T003 + T004 + T005 → PNG generation and download works (MVP!)
3. T006 + T007 + T008 → PDF download added
4. T009 → Both tiers verified
5. T010 + T011 → Tests confirm everything

---

## Notes

- The coloring page routes MUST be declared before the catch-all `GET /gallery/{story_id}/{scene_id}` route — same ordering issue fixed in 027-sequel-mode. The route order should be: `/coloring/pdf` → `/coloring` → `/{scene_id}` (most specific first).
- `generate_coloring_page()` implements file-on-disk caching — if `{scene_id}_coloring.png` exists, return immediately without API call.
- The JS handles the full client-side flow: button click → loading → display + downloads → error/retry.
- Total: 11 tasks across 6 phases
