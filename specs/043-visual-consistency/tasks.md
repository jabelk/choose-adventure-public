# Tasks: Character Visual Consistency

**Input**: Design documents from `/specs/043-visual-consistency/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

---

## Phase 1: Setup (Model Extension)

**Purpose**: Add the rolling reference field to the Story model

- [x] T001 Add `generated_reference_path: str = Field(default="")` field to `Story` model in `app/models.py` — stores the absolute file path of the most recently generated scene image for use as a rolling reference in subsequent scenes

**Checkpoint**: Story model ready for reference tracking

---

## Phase 2: User Story 1 — Auto-Carry Reference Image Across Scenes (Priority: P1) MVP

**Goal**: Pass roster photos + most recent generated scene image as references to every image generation call after scene 1

**Independent Test**: Start a story with a roster character who has a photo, complete 3 scenes, verify character appearance remains consistent across all scene images.

### Implementation

- [x] T002 [US1] Add `_build_reference_images(story_session, character_service)` helper function inside `create_tier_router()` in `app/routes.py` — collects roster character photos (up to 2 if generated ref exists, up to 3 if not), appends `story.generated_reference_path` if set and file exists, caps at 3 total, returns `list[str] | None`
- [x] T003 [US1] Add `_generate_and_track_reference(image, scene_id, image_model, reference_images, story)` async wrapper function in `app/routes.py` — awaits `image_service.generate_image()`, then if `image.status == COMPLETE` sets `story.generated_reference_path` to the generated file path (`STATIC_IMAGES_DIR / f"{scene_id}.png"`)
- [x] T004 [US1] Update story start route (`POST /{tier}/start`) in `app/routes.py` — replace direct `asyncio.create_task(image_service.generate_image(...))` with `asyncio.create_task(_generate_and_track_reference(...))`, use `_build_reference_images()` for the reference list
- [x] T005 [US1] Update continue story route (`POST /{tier}/story/continue`) in `app/routes.py` — replace `choice_photo_paths` assembly with `_build_reference_images()`, replace `generate_image` task with `_generate_and_track_reference`
- [x] T006 [US1] Update agent mode continue route (`POST /{tier}/story/agent/continue`) in `app/routes.py` — same changes as T005 for the agent mode continuation path
- [x] T007 [US1] Update sequel start route in `app/routes.py` — replace photo path assembly with `_build_reference_images()`, replace `generate_image` task with `_generate_and_track_reference`
- [x] T008 [US1] Update image retry route (`POST /{tier}/story/image/{scene_id}`) in `app/routes.py` — pass references from `_build_reference_images()` instead of no references, use `_generate_and_track_reference` wrapper
- [x] T009 [US1] Update image regenerate route (`POST /{tier}/story/image/{scene_id}/regenerate`) in `app/routes.py` — pass references from `_build_reference_images()`, use `_generate_and_track_reference` wrapper
- [x] T010 [US1] Verify `_setup_extra_images` (picture book mode) continues to pass references correctly — should use the same `_build_reference_images()` output, but only the primary image updates the rolling reference (not extra variations)

**Checkpoint**: Scene images maintain visual consistency across a full story. Rolling reference updates after each successful generation.

---

## Phase 3: User Story 2 — Reference Image Display on Story Page (Priority: P2)

**Goal**: Show a visual indicator when reference images are being used for consistency

**Independent Test**: Start a story with a roster character photo, verify a "Visual consistency active" badge appears near the scene image on the story page.

### Implementation

- [x] T011 [US2] Add `has_reference_images` boolean to story page template context in `app/routes.py` — set to True when `_build_reference_images()` returns a non-empty list, pass to all story page render calls
- [x] T012 [US2] Add reference indicator badge to `templates/story.html` — small subtle badge (e.g., camera icon + "Consistent") shown near the scene image when `has_reference_images` is true, hidden when false
- [x] T013 [US2] Add CSS styles for `.reference-indicator` badge in `static/css/style.css` — subtle, non-intrusive styling that doesn't distract from the story content

**Checkpoint**: Users can see when visual consistency is active during story generation.

---

## Phase 4: User Story 3 — Opt-Out / Reset Visual Reference (Priority: P3)

**Goal**: Allow users to clear generated scene references mid-story for intentional appearance changes

**Independent Test**: Start a story, progress 2 scenes, tap "Reset appearance", verify next scene generates without prior scene visual constraints.

### Implementation

- [x] T014 [US3] Add `POST /{tier}/story/reset-appearance` route in `app/routes.py` — clears `story.generated_reference_path` to empty string, redirects back to story page with a flash message
- [x] T015 [US3] Add "Reset appearance" button to `templates/story.html` — small secondary button near the reference indicator, only shown when `story.generated_reference_path` is set, submits POST to reset-appearance route
- [x] T016 [US3] Add CSS for reset button in `static/css/style.css` — small, secondary-style button that doesn't compete with main story actions

**Checkpoint**: Users can reset visual references mid-story for transformation scenes or fresh looks.

---

## Phase 5: Polish & Verification

**Purpose**: Cross-cutting validation and cleanup

- [x] T017 Run existing test suite `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — all tests pass, no regressions
- [x] T018 Test backward compatibility — verify existing stories and sessions work without the new field (default empty string)
- [x] T019 Run quickstart.md verification steps end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (US1)**: Depends on Phase 1 completion
- **Phase 3 (US2)**: Depends on Phase 2 (needs `_build_reference_images()` helper)
- **Phase 4 (US3)**: Depends on Phase 2 (needs `generated_reference_path` field in use)
- **Phase 5 (Polish)**: Depends on all prior phases

### Parallel Opportunities

- T011, T012, T013 (US2) can run after T002-T003 are done (only needs the helper function)
- T014, T015, T016 (US3) can run after T001 is done (only needs the model field)
- Phase 3 and Phase 4 can run in parallel once Phase 2 core tasks (T002-T003) are complete

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: User Story 1 (T002-T010)
3. **STOP and VALIDATE**: Start a 3-scene story with roster character photos, verify visual consistency
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Model ready
2. Phase 2 (US1) → Visual consistency active → Deploy
3. Phase 3 (US2) → Reference indicator visible → Deploy
4. Phase 4 (US3) → Reset appearance available → Deploy
5. Phase 5 → Final verification

---

## Notes

- No new pip dependencies required
- `generated_reference_path` default `""` ensures zero migration needed
- The `_generate_and_track_reference` wrapper is the key new pattern — it wraps existing `generate_image()` calls without modifying `ImageService` itself
- All `generate_image()` call sites in routes.py must be updated (approximately 7-8 sites)
- Picture book extra images should NOT update the rolling reference — only the primary scene image does
