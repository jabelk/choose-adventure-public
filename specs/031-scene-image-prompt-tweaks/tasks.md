# Tasks: Scene Image Prompt Tweaks

**Input**: Design documents from `/specs/031-scene-image-prompt-tweaks/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Added in polish phase.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

(No setup needed — no new dependencies.)

---

## Phase 2: Foundational

- [X] T001 [P] Add CSS styles for prompt edit overlay in `static/css/style.css` — `.prompt-edit-icon` (absolute positioned pencil icon on image hover), `.prompt-edit-panel` (textarea + buttons below image), `.prompt-edit-textarea`, `.prompt-edit-actions` (Regenerate + Cancel buttons), `.prompt-edit-loading` (spinner during generation), `.prompt-edit-error` (error message display)
- [X] T002 [P] Create `static/js/prompt-edit.js` — `initPromptEdit(config)` accepting `{container, prompt, regenerateUrl}`; click edit icon shows textarea with current prompt + Regenerate/Cancel buttons; Regenerate POSTs JSON `{prompt}` to URL, shows loading, replaces image src on success (with `?t=timestamp` cache-bust), shows error on failure; Cancel hides panel; validates non-empty prompt before submit

---

## Phase 3: User Story 1 - Edit and Regenerate Scene Image (Priority: P1)

- [X] T003 [US1] Add POST route `/story/image/{scene_id}/regenerate` in `app/routes.py` — accept JSON body `{prompt}`, validate non-empty, update `scene.image.prompt`, reset image status to PENDING, clear URL, start `image_service.generate_image()` as background task, save progress, return `{status: "generating"}`
- [X] T004 [US1] Update `templates/scene.html` — add edit icon overlay on scene image container (only when `scene.image.status.value == 'complete'` and `scene.image.prompt`); add `data-prompt` attribute with current prompt and `data-regenerate-url` with the regenerate route URL; include `prompt-edit.js` script; initialize `initPromptEdit()` per scene image container

---

## Phase 4: User Story 2 - Works on Both Tiers (Priority: P2)

- [X] T005 [US2] Verification task — the regenerate route is inside `create_tier_router()` and template/JS are shared; verify edit icon and regeneration work on both Kids and NSFW tier story pages

---

## Phase 5: User Story 3 - Gallery Reader Prompt Tweaks (Priority: P3)

- [X] T006 [US3] Add `update_story()` method to `app/services/gallery.py` — accepts a `SavedStory` object, serializes to JSON, writes to `data/stories/{story_id}.json`
- [X] T007 [US3] Add POST route `/gallery/{story_id}/{scene_id}/regenerate-image` in `app/routes.py` — accept JSON body `{prompt}`, validate non-empty, load SavedStory, create temporary Image object with new prompt, await `image_service.generate_image()` synchronously, update `saved_scene.image_prompt` and `saved_scene.image_url` (with cache-bust timestamp), call `gallery_service.update_story()`, return `{status: "complete", image_url: "..."}` on success or `{status: "failed", error: "..."}` on failure
- [X] T008 [US3] Update `templates/reader.html` — add edit icon overlay on scene image container (only when `scene.image_url` and `scene.image_prompt`); add `data-prompt` and `data-regenerate-url` attributes; initialize `initPromptEdit()` per scene image

---

## Phase 6: Polish

- [X] T009 Create `tests/test_prompt_tweaks.py` — test edit icon visible on active story scene with image (kids + nsfw), hidden when no image prompt, regenerate route returns `{status: "generating"}` with updated prompt, gallery regenerate route returns success, gallery reader shows edit icon
- [X] T010 Run full test suite to verify no regressions

---

## Notes

- Two new server routes: one for active stories (background task), one for gallery (synchronous).
- Image files are overwritten at the same path with `?t=timestamp` cache-busting.
- JS module is shared between scene.html and reader.html.
- Total: 10 tasks across 6 phases
