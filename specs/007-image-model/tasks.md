# Tasks: Image Model Selection

**Input**: Design documents from `/specs/007-image-model/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested — manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Image Registry & Data Model)

**Purpose**: Create the image provider registry and add image_model field to Story models. These are blocking prerequisites for all user stories.

- [x] T001 Add `image_model` field (str, default `"dalle"`) to `Story` model in `app/models.py`
- [x] T002 [P] Add `image_model` field (str, default `"dalle"`) to `SavedStory` model in `app/models.py`
- [x] T003 Add `IMAGE_PROVIDERS` list, `get_available_image_models()`, `get_image_provider()`, `get_image_model_display_name()` functions to `app/models_registry.py` — two providers: dalle (OPENAI_API_KEY) and gemini (GEMINI_API_KEY)
- [x] T004 Add `default_image_model` field (str, default `"dalle"`) to `TierConfig` dataclass in `app/tiers.py`
- [x] T005 Refactor `ImageService.generate_image()` in `app/services/image.py` to accept an `image_model` parameter (str) and dispatch to the correct provider — extract OpenAI call into `_generate_dalle()`, add `_generate_gemini()` method using `google-genai` SDK with `response_modalities=["IMAGE"]`

**Checkpoint**: Image registry exists, Story models have image_model field, ImageService can generate with either provider.

---

## Phase 2: User Story 1 — Choose an Image Model (Priority: P1) 🎯 MVP

**Goal**: Users can select an image model on the start form (when multiple available), story generates images with that model.

**Independent Test**: Start a story with DALL-E, verify images generate. Start another with Gemini, verify images generate with different style.

### Implementation for User Story 1

- [x] T006 [US1] Update `POST /{tier}/story/start` in `app/routes.py` — accept `image_model` form parameter, validate against available image models, fall back to tier default, store on Story object, pass to `ImageService.generate_image()`
- [x] T007 [US1] Update `POST /{tier}/story/choose/{scene_id}/{choice_id}` in `app/routes.py` — read image_model from `story_session.story.image_model` and pass to `ImageService.generate_image()`
- [x] T008 [US1] Update `POST /{tier}/story/image/{scene_id}/retry` in `app/routes.py` — read image_model from `story_session.story.image_model` and pass to `ImageService.generate_image()`
- [x] T009 [US1] Update `GET /{tier}/` (tier_home) in `app/routes.py` — pass `available_image_models` list and `default_image_model` key to the template context
- [x] T010 [US1] Add conditional image model selector radio card section to `templates/home.html` — only render when `available_image_models|length > 1`, between text model selector and submit button, styled like model options, pre-select default, include hidden input when only one provider available
- [x] T011 [US1] Add `.image-model-selector` CSS styles in `static/css/style.css` if needed (may reuse existing `.model-selector` pattern)
- [x] T012 [US1] Update `GalleryService.save_story()` in `app/services/gallery.py` — include `image_model=story.image_model` when constructing SavedStory

**Checkpoint**: Image model selector on start form (conditional), stories generate with selected image model.

---

## Phase 3: User Story 2 — Tier Default Image Models (Priority: P2)

**Goal**: Each tier pre-selects its configured default image model. Fallback to first available if default is unavailable.

**Independent Test**: Visit /kids/ and verify DALL-E is pre-selected. Remove OPENAI_API_KEY, restart, verify fallback to Gemini.

### Implementation for User Story 2

- [x] T013 [US2] Update tier_home route in `app/routes.py` — compute effective default image model (tier's default_image_model if available, else first available image model's key), pass as `default_image_model` to template
- [x] T014 [US2] Update image model selector in `templates/home.html` — mark the radio button matching `default_image_model` as checked

**Checkpoint**: Tier defaults pre-selected, fallback works when default image model unavailable.

---

## Phase 4: User Story 3 — Image Model Attribution (Priority: P2)

**Goal**: Gallery story cards and reader show which image model generated each story's illustrations. Pre-existing stories show "DALL-E".

**Independent Test**: Complete a story with Gemini images. View gallery — verify "Gemini" appears. Open in reader — verify image model name in header.

### Implementation for User Story 3

- [x] T015 [US3] Display image model name on gallery story cards in `templates/gallery.html` — add image model display name alongside the text model name in story card info section
- [x] T016 [US3] Display image model name in gallery reader header in `templates/reader.html` — add image model name next to text model name
- [x] T017 [US3] Display image model name in scene header in `templates/scene.html` — add image model display name next to text model name (e.g., "Chapter 2 of ~5 · Claude · DALL-E")

**Checkpoint**: Gallery cards show image model name, reader shows image model name, scene header shows image model name.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation, backward compatibility verification, edge cases.

- [x] T018 Verify backward compatibility — load a pre-existing saved story JSON (without image_model field) and confirm it deserializes with `image_model="dalle"` without errors
- [x] T019 Verify story resume preserves image model — start a story with Gemini images, navigate away, resume from progress banner, verify story continues with Gemini images
- [x] T020 Run quickstart.md full validation — test all 11 scenarios manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — start immediately
- **Phase 2 (US1 - Choose Image Model)**: Depends on Phase 1 (needs registry, image_model field, provider dispatch)
- **Phase 3 (US2 - Tier Defaults)**: Depends on Phase 2 (extends image model selector behavior)
- **Phase 4 (US3 - Attribution)**: Depends on Phase 1 (needs image_model field on SavedStory). Can run parallel with Phase 2/3.
- **Phase 5 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Choose Image Model)**: Depends on Phase 1. Core feature — must be first.
- **US2 (Tier Defaults)**: Depends on US1 (extends the image model selector created in US1).
- **US3 (Attribution)**: Depends on Phase 1 only. Can proceed in parallel with US1/US2 since it touches different files (gallery.html, reader.html, scene.html).

### Within Each User Story

- Route changes before template changes (context must be available for templates)
- Registry helpers before routes (helpers must exist for routes to call)

### Parallel Opportunities

- T001 and T002 can run in parallel (same file but different model classes)
- US3 (Phase 4) can run in parallel with US1/US2 after Phase 1 completes:
  - US3 touches: gallery.html, reader.html, scene.html
  - US1 touches: routes.py, home.html, style.css, gallery.py
  - Minimal file overlap

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (registry, image_model fields, ImageService refactor)
2. Complete Phase 2: Choose an Image Model
3. **STOP and VALIDATE**: Start stories with DALL-E and Gemini, verify images generate correctly
4. Users can now compare image styles from different AI providers — core value delivered

### Incremental Delivery

1. Phase 1 → Foundation ready (registry, image_model fields, 2 providers)
2. Phase 2 (US1) → Image model selector works → Test independently (MVP!)
3. Phase 3 (US2) → Tier defaults → Test independently
4. Phase 4 (US3) → Image model attribution → Test independently
5. Phase 5 → Polish, backward compat verification, full validation

---

## Notes

- No new files — all changes extend existing modules
- No new dependencies — Gemini image gen uses existing `google-genai` package
- DALL-E uses existing `openai` package
- Both providers save to the same `static/images/{scene_id}.png` path
- Default `image_model="dalle"` on Story/SavedStory handles backward compatibility with zero migration
- Image model selector is conditionally rendered (only when 2+ providers available)
