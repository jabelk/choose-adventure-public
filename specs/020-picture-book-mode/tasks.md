# Tasks: Picture Book Mode

**Input**: Design documents from `/specs/020-picture-book-mode/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Shared model and helper changes needed by all user stories

- [X] T001 Add `extra_images: list[Image] = []` field to Scene model in app/models.py
- [X] T002 Add `extra_image_urls: list[str] = []` and `extra_image_prompts: list[str] = []` fields to SavedScene model in app/models.py
- [X] T003 Add `is_picture_book_age(protagonist_age: str) -> bool` helper to app/story_options.py that returns True for "toddler" and "young-child"

---

## Phase 2: Foundational

**Purpose**: Image service changes that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add `FAST_IMAGE_MODEL = "gpt-image-1-mini"` constant and `generate_extra_images()` method to ImageService in app/services/image.py — method takes extra_images list, scene_id, main_prompt, fast_model, optional reference_images; derives close-up and wide-shot prompts from main_prompt; generates each extra image in parallel using asyncio.gather; saves to `static/images/{scene_id}_extra_0.png` and `{scene_id}_extra_1.png`
- [X] T005 Update `save_story()` in app/services/gallery.py to persist `extra_image_urls` and `extra_image_prompts` from scene.extra_images when building SavedScene objects

**Checkpoint**: Foundation ready — model fields, helper, image service, and gallery persistence in place

---

## Phase 3: User Story 1 — Multi-Image Scene Generation (Priority: P1) 🎯 MVP

**Goal**: Scenes display 3 images for toddler/young-child ages, 1 image for all others

**Independent Test**: Start a kids story with "Toddler" age → scene shows 3 image placeholders. Start with "Older Child" → scene shows 1 image.

### Implementation for User Story 1

- [X] T006 [US1] In app/routes.py `start_story` handler, after main image generation kickoff, check `is_picture_book_age(story.protagonist_age)` — if true, create 2 extra Image objects with derived prompts (close-up + wide-shot from main image prompt), append to scene.extra_images, kick off `generate_extra_images()` as async task
- [X] T007 [US1] In app/routes.py `make_choice` handler, add the same picture book extra image generation logic as T006 (check age, create extra Images, kick off generation)
- [X] T008 [US1] In app/routes.py `custom_choice` handler, add the same picture book extra image generation logic as T006
- [X] T009 [US1] Update templates/scene.html to render extra images below the main image in a vertical layout — for each extra image in scene.extra_images, show loading placeholder (if generating), completed image (if complete), or failed state (if failed), using the same pattern as the main image container
- [X] T010 [US1] Add CSS styles for picture book image layout in static/css/style.css — vertical stack of images below main image, each with its own container, consistent sizing, label for image type (close-up / wide shot)

**Checkpoint**: Picture book mode generates and displays 3 images for young ages. Standard mode unchanged.

---

## Phase 4: User Story 2 — Faster Image Generation for Young Ages (Priority: P2)

**Goal**: Extra images use gpt-image-1-mini regardless of user's selected model; main image uses user's selected model

**Independent Test**: Start a picture book story with gpt-image-1 selected → verify main image uses gpt-image-1, extra images use gpt-image-1-mini

### Implementation for User Story 2

- [X] T011 [US2] In app/routes.py, when kicking off extra image generation (in start_story, make_choice, custom_choice), determine the fast model: check if gpt-image-1-mini is available (has API key), if yes use it, otherwise fall back to user's selected image model; pass this as the model to `generate_extra_images()`

**Checkpoint**: Extra images use fast model, main image uses user's selection.

---

## Phase 5: User Story 3 — Image Loading Experience (Priority: P3)

**Goal**: Each image has independent loading/polling/retry states. Gallery preserves and displays extra images.

**Independent Test**: Load a picture book scene → see 3 independent loading indicators. Retry one failed extra image without affecting others. View saved story in gallery reader → see all 3 images.

### Implementation for User Story 3

- [X] T012 [US3] Extend `GET /story/image/{scene_id}` endpoint in app/routes.py to include `extra_images` array in JSON response with index, status, url, and type fields for each extra image
- [X] T013 [US3] Update pollImageStatus() in static/js/app.js to process extra_images from the polling response — update each extra image container independently, show image when complete, show retry button when failed, keep polling until all images (main + extras) are resolved
- [X] T014 [US3] Add `POST /story/image/{scene_id}/retry-extra/{index}` endpoint in app/routes.py — validates scene/index, resets extra_images[index] status to PENDING, kicks off single extra image regeneration, redirects to scene
- [X] T015 [US3] Update templates/scene.html extra image containers to include retry buttons that call the retry-extra endpoint with the correct index
- [X] T016 [US3] Update templates/reader.html to display extra images for each scene — show extra_image_urls below the main image in the same vertical layout as scene.html

**Checkpoint**: Full independent loading/polling/retry for all images. Gallery reader shows all images.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation

- [X] T017 [P] Add picture book mode tests in tests/test_all_options.py — test is_picture_book_age helper, test extra images created for toddler/young-child ages, test no extra images for older-child/any/adult ages, test image status endpoint returns extra_images, test retry-extra endpoint, test gallery persistence of extra images
- [X] T018 Run all existing tests to verify no regressions in standard single-image mode
- [ ] T019 Run quickstart.md validation scenarios manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — core multi-image generation
- **US2 (Phase 4)**: Depends on Phase 3 — adds fast model selection to existing extra image flow
- **US3 (Phase 5)**: Depends on Phase 3 — adds polling/retry/gallery for extra images
- **Polish (Phase 6)**: Depends on Phases 3-5

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. Core feature — all other stories build on this.
- **US2 (P2)**: Depends on US1 (needs extra image generation to exist before selecting model).
- **US3 (P3)**: Depends on US1 (needs extra image containers to exist before adding polling/retry).
- US2 and US3 are independent of each other and could run in parallel after US1.

### Within Each User Story

- Models/helpers before services
- Services before routes
- Routes before templates
- Templates before JS/CSS

### Parallel Opportunities

- T001, T002, T003 touch different parts of different files — can run in parallel
- T006, T007, T008 all modify routes.py — must be sequential
- T009 (template) and T010 (CSS) touch different files — can run in parallel
- T012 (routes) must complete before T013 (JS) can consume the new response format
- T017 (tests) can run in parallel with T016 (reader template)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T005)
3. Complete Phase 3: User Story 1 (T006-T010)
4. **STOP and VALIDATE**: Start a kids story with toddler age — verify 3 images appear
5. Deploy if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → 3 images per scene for young ages → Deploy (MVP!)
3. Add US2 → Extra images use fast model → Deploy
4. Add US3 → Independent polling/retry/gallery → Deploy
5. Polish → Tests and validation → Final deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story should be independently testable after completion
- Commit after each phase or logical group
- US2 and US3 could be done in parallel after US1 but are sequenced here for single-developer flow
