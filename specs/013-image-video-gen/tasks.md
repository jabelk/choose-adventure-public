# Tasks: Multi-Model Image & Video Generation

**Input**: Design documents from `/specs/013-image-video-gen/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Update models, registry, and tier defaults to support the expanded image model set and video mode. These changes are shared by all user stories.

- [X] T001 [P] Extend the Image model in app/models.py — add `video_url: Optional[str] = None`, `video_status: str = "none"`, `video_error: Optional[str] = None` fields for video tracking per scene
- [X] T002 [P] Extend the Story model in app/models.py — add `video_mode: bool = False` field to record whether video generation is enabled for this story
- [X] T003 [P] Extend the SavedScene model in app/models.py — add `video_url: Optional[str] = None` field to persist video references in saved stories
- [X] T004 [P] Extend the SavedStory model in app/models.py — add `video_mode: bool = False` field to persist video mode flag in saved stories
- [X] T005 Refactor IMAGE_PROVIDERS in app/models_registry.py — replace the existing `ModelProvider`-based IMAGE_PROVIDERS list with a new `ImageModel` dataclass that includes `key`, `display_name`, `provider` (group name for UI), `api_key_env`, `supports_input_fidelity: bool`, and `supports_references: bool`. Populate with 5 entries: `gpt-image-1` (OpenAI, fidelity=True, refs=True), `gpt-image-1-mini` (OpenAI, fidelity=False, refs=True), `gpt-image-1.5` (OpenAI, fidelity=True, refs=True), `grok-imagine` (xAI, fidelity=False, refs=True), `gemini` (Google, fidelity=False, refs=True). Update `get_available_image_models()`, `get_image_provider()`, and `get_image_model_display_name()` to work with the new dataclass. Ensure text model PROVIDERS list and functions remain unchanged.
- [X] T006 Update default_image_model in app/tiers.py — change the default value of `default_image_model` in the TierConfig dataclass from `"dalle"` to `"gpt-image-1"`. Update both TIERS entries if they explicitly set default_image_model.
- [X] T007 Add backward-compatible display name mapping in app/models_registry.py — ensure `get_image_model_display_name("dalle")` returns "DALL-E" (for old saved stories that have `image_model="dalle"`) by adding a legacy alias in the lookup function

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update the image service to support parameterized OpenAI models and add the Grok Imagine image generation method. All user stories depend on these service changes.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Parameterize the OpenAI model name in `_generate_dalle()` in app/services/image.py — change the hardcoded `model="gpt-image-1"` to accept a `model_name: str` parameter. In `images.generate()`, pass `model=model_name`. In `images.edit()`, pass `model=model_name` and only include `input_fidelity="high"` when the model is NOT `gpt-image-1-mini` (check against the registry's `supports_input_fidelity` flag or use a simple string check). Rename the method from `_generate_dalle` to `_generate_openai` since it now covers multiple models.
- [X] T009 Add `_generate_grok()` method to ImageService in app/services/image.py — create a new async method that generates images via xAI's Grok Imagine API. Use `AsyncOpenAI(base_url="https://api.x.ai/v1", api_key=settings.xai_api_key)` for basic generation with `model="grok-imagine-image"`, `response_format="b64_json"`, `n=1`. Initialize this client in `__init__` (only if `settings.xai_api_key` is set, similar to gemini_client pattern). Return raw image bytes from the base64 response.
- [X] T010 Update the `generate_image()` dispatcher in app/services/image.py — update the routing logic to dispatch to the correct method based on `image_model`: `"gpt-image-1"`, `"gpt-image-1-mini"`, `"gpt-image-1.5"` → `_generate_openai(prompt, model_name=image_model, reference_images=reference_images)`; `"grok-imagine"` → `_generate_grok(prompt, reference_images=reference_images)`; `"gemini"` → `_generate_gemini(prompt, reference_images=reference_images)`. Remove the old `"dalle"` check (or keep as fallback alias to `_generate_openai` with `model_name="gpt-image-1"`).
- [X] T011 Update the GalleryService `save_story()` in app/services/gallery.py — when converting StorySession to SavedStory, include the new `video_mode` field from `story.video_mode`. When converting Scene to SavedScene, include `video_url=scene.image.video_url if scene.image and scene.image.video_url else None`.

**Checkpoint**: Image service supports all 5 models. Gallery preserves video data. User story implementation can now begin.

---

## Phase 3: User Story 1 — Expanded Image Model Selection (Priority: P1) 🎯 MVP

**Goal**: Users see 5 image models grouped by provider in the home page selector and can generate images with any of them.

**Independent Test**: Start the server with all API keys configured. Visit the home page and verify 5 models appear grouped by provider (OpenAI, xAI, Google). Start a story with each model and confirm an image is generated. Check the scene view and gallery show the specific model name.

### Implementation for User Story 1

- [X] T012 [P] [US1] Update the image model selector in templates/home.html — replace the flat radio button list with a grouped layout. Import `available_image_models` (which now have a `provider` field) and group them by provider. Render section headers ("OpenAI", "xAI", "Google") with model options beneath each. Keep the existing radio button pattern (`name="image_model"`, `value="{{ img_model.key }}"`) but add provider group labels. If only one model is available, use a hidden input (existing behavior).
- [X] T013 [P] [US1] Add CSS styles for the grouped image model selector in static/css/style.css — add styles for `.model-group`, `.model-group-label` (provider header styling), and ensure the grouped layout looks clean within the existing `.model-options` container. Keep it visually consistent with the text model selector.
- [X] T014 [US1] Update the `start_story` route in app/routes.py — change the `image_model` form field default from `"dalle"` to `"gpt-image-1"`. Validation logic against `get_available_image_models()` already works since it checks `.key` — just verify it handles the new keys correctly.
- [X] T015 [US1] Update `get_image_model_display_name()` usage in templates — verify that `scene.html`, `gallery.html`, and `reader.html` all use `get_image_model_display_name(story.image_model)` and that it correctly displays the new model names (e.g., "GPT Image 1.5", "Grok Imagine"). The function was updated in T005/T007 to handle new keys and legacy "dalle" alias.
- [X] T016 [US1] Verify Grok Imagine image generation end-to-end — start a story with "Grok Imagine" selected, confirm an image generates successfully via the xAI API, and verify the image displays in the scene view. Handle the temporary URL response by ensuring the image bytes are saved to disk (the `_generate_grok` method from T009 returns base64 bytes, which the existing `generate_image` saves to disk).

**Checkpoint**: All 5 image models selectable and generating images. Model names display correctly throughout the UI. Backward-compatible with old "dalle" saved stories.

---

## Phase 4: User Story 2 — Reference Photo Support for New Providers (Priority: P2)

**Goal**: Reference photos from feature 012 work with all new image models when memory mode is active.

**Independent Test**: Upload a reference photo for a character, start a story with memory mode on using GPT Image 1.5, GPT Image 1 Mini, and Grok Imagine. Verify each provider receives and uses the reference photos.

### Implementation for User Story 2

- [X] T017 [US2] Add reference photo support to `_generate_grok()` in app/services/image.py — when `reference_images` is non-empty, use raw httpx to POST to `https://api.x.ai/v1/images/generations` with the reference image as a base64 data URI in the `image_url` field. Read the first reference image file, base64-encode it, and include it in the JSON body alongside the prompt. Fall back to the basic generation (via OpenAI SDK) if no valid reference image files exist. Import httpx at the top of the file.
- [X] T018 [US2] Update `_generate_openai()` reference photo handling in app/services/image.py — in the `images.edit()` call, look up the image model's `supports_input_fidelity` flag from the registry (import `get_image_provider` from models_registry) and conditionally include `input_fidelity="high"` only when the flag is True. This ensures GPT Image 1 Mini uses `images.edit` without `input_fidelity`, while GPT Image 1 and 1.5 use it with high fidelity.
- [X] T019 [US2] Verify reference photos work with all 5 models — test with memory mode on and a character with a reference photo: (1) GPT Image 1 → images.edit with input_fidelity="high", (2) GPT Image 1 Mini → images.edit without input_fidelity, (3) GPT Image 1.5 → images.edit with input_fidelity="high", (4) Grok Imagine → httpx with base64 image_url, (5) Gemini → existing inline_data (unchanged). Verify no errors for any model.

**Checkpoint**: Reference photos work with all 5 image models. Memory mode on = photos included. Memory mode off = no photos.

---

## Phase 5: User Story 3 — Video Generation for Story Scenes (Priority: P3)

**Goal**: Users can enable "Video Mode" and get short animated video clips for each story scene via Grok Imagine's video API.

**Independent Test**: Enable video mode, start a story, verify a video player appears in the scene view after the static image. Check that the video file is stored on disk. Verify video generation works asynchronously (image appears first, video loads later).

### Implementation for User Story 3

- [X] T020 [P] [US3] Add the "Video Mode" toggle to templates/home.html — add a checkbox toggle for video mode below the image model selector, using the same styling pattern as the memory mode toggle. Use `name="video_mode"` with `value="on"`. Only show the toggle when `video_mode_available` is True (passed from the route context). Include a brief description: "Generate short video clips for each scene (requires xAI)".
- [X] T021 [P] [US3] Add CSS styles for the video mode toggle and video player in static/css/style.css — add styles for the video mode toggle on the home page. Add styles for `.scene-video` container, `.scene-video video` (max-width, rounded corners matching image), `.video-loading` indicator, `.video-failed` message with retry button, `.video-badge` for gallery cards.
- [X] T022 [US3] Add `generate_video()` method to ImageService in app/services/image.py — create a new async method that: (1) sets `image.video_status = "generating"`, (2) POSTs to `https://api.x.ai/v1/videos/generations` via httpx with `model="grok-imagine-video"`, `prompt`, `duration=8`, `aspect_ratio="1:1"`, `resolution="720p"`, and optionally `image` (with the scene image as base64 data URI for image-to-video), (3) receives `{request_id}`, (4) polls GET `https://api.x.ai/v1/videos/{request_id}` every 5 seconds up to 60 attempts (5 minutes max), (5) downloads the video from the temporary URL, (6) saves as `static/videos/{scene_id}.mp4`, (7) sets `image.video_url = "/static/videos/{scene_id}.mp4"` and `image.video_status = "complete"`. On failure, sets `video_status = "failed"` and `video_error` with the error message. Create `STATIC_VIDEOS_DIR` constant alongside `STATIC_IMAGES_DIR`.
- [X] T023 [US3] Update `start_story` route in app/routes.py to support video mode — add `video_mode: str = Form("")` parameter. Set `story.video_mode = (video_mode == "on")`. Pass `video_mode_available` (True if `settings.xai_api_key` is set) to the home page template context. After the image generation task is created, if `story.video_mode` is True, create a chained task that waits for the image to complete then triggers `image_service.generate_video(image, scene.scene_id)`. Use a helper function `_chain_video_after_image()` that polls `image.status` until complete, then calls `generate_video`.
- [X] T024 [US3] Update `make_choice` route in app/routes.py to trigger video generation — same pattern as start_story: if `story_session.story.video_mode` is True, after creating the image generation task, create a chained video generation task for the new scene.
- [X] T025 [US3] Add video player and status display to templates/scene.html — below the existing image section, add a video section: if `scene.image.video_status == "complete"` and `scene.image.video_url`, render an HTML5 `<video>` element with `controls`, `playsinline`, `preload="metadata"`. If status is `"generating"` or `"pending"`, show a loading indicator ("Generating video..."). If status is `"failed"`, show an error message with a retry button.
- [X] T026 [US3] Add video status polling and retry to static/js/app.js — add JavaScript that polls `GET /{tier}/story/video/{scene_id}` every 5 seconds when the video status is "generating" or "pending". When the response returns `"complete"`, insert the `<video>` element dynamically (same pattern as image status polling). Add a retry click handler that POSTs to `/{tier}/story/video/{scene_id}/retry`.
- [X] T027 [US3] Add video status and retry routes to app/routes.py — add `GET /story/video/{scene_id}` that returns JSON `{status, url}` by checking `scene.image.video_status` and `scene.image.video_url`. Add `POST /story/video/{scene_id}/retry` that resets video status to "pending" and kicks off a new `generate_video` task. Follow the exact same pattern as the existing `image_status` and `retry_image` routes.

**Checkpoint**: Video mode toggle works. Videos generate asynchronously after images. Video player appears in scene view. Retry works for failed videos.

---

## Phase 6: User Story 4 — Video in Gallery and Reader (Priority: P4)

**Goal**: Saved stories with video mode display video clips in the gallery and reader views.

**Independent Test**: Generate a story with video mode on, save it, browse the gallery and verify the story card shows a video badge, open in reader and verify videos play inline.

### Implementation for User Story 4

- [X] T028 [P] [US4] Add video badge to gallery story cards in templates/gallery.html — when `story.video_mode` is True, display a small badge or icon (e.g., a play triangle or "Video" text) on the story card to indicate it contains video content. Add appropriate CSS class (from T021).
- [X] T029 [P] [US4] Add inline video player to the reader in templates/reader.html — for each scene, if `scene.video_url` is set, render an HTML5 `<video>` element below the scene image with `controls`, `playsinline`, `preload="metadata"`. If no video_url, render nothing (no placeholder, no broken elements). This ensures backward compatibility with pre-video stories.
- [X] T030 [US4] Verify backward compatibility with old saved stories — load a story saved before this feature (with `image_model="dalle"` and no `video_mode` field). Verify it displays correctly in the gallery (no video badge, shows "DALL-E" as model name) and in the reader (images only, no broken video elements). Pydantic defaults handle the missing fields.

**Checkpoint**: Gallery shows video badges. Reader plays videos inline. Old stories unaffected.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, cleanup, tier isolation, and end-to-end validation

- [X] T031 Add video file cleanup to story deletion — if/when a story deletion mechanism exists, ensure video files in `static/videos/` are deleted alongside image files. Check if gallery_service has a delete method; if not, this is a no-op since story files are retained by design (archival principle).
- [X] T032 Verify tier isolation for videos — generate a video in the kids tier, confirm the video file is served via the static files route and is accessible at `/static/videos/{scene_id}.mp4`. Note: unlike photos (which use tier-scoped routes), videos use the same static file pattern as images — tier isolation is enforced at the session/story level (the scene_id is only known to the tier's story session). Verify a user in the nsfw tier cannot discover kids tier video URLs.
- [X] T033 Verify graceful handling of missing video files — manually delete a video file from `static/videos/`, then load the scene. Confirm the video section shows "failed" or nothing (no broken `<video>` element, no error).
- [X] T034 Verify video generation fallback when xAI key is missing — remove XAI_API_KEY from .env, restart server. Verify: (1) Grok Imagine is not shown in image model selector, (2) Video mode toggle is hidden, (3) Starting a story works normally without video.
- [X] T035 Run full quickstart.md validation (all 10 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T007) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T008-T011)
- **User Story 2 (Phase 4)**: Depends on Foundational phase AND User Story 1 (needs new models working to test reference photos)
- **User Story 3 (Phase 5)**: Depends on Foundational phase AND User Story 1 (video generates after image, needs image models working)
- **User Story 4 (Phase 6)**: Depends on User Story 3 (needs video data in saved stories to test gallery/reader)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — foundation for all others
- **User Story 2 (P2)**: Can start after US1 — needs image generation working per model to test reference photos
- **User Story 3 (P3)**: Can start after US1 — needs image generation working to chain video after image
- **User Story 4 (P4)**: Must follow US3 — needs video-enabled stories to test gallery/reader display

### Within Each User Story

- Templates and CSS can be created in parallel (different files)
- Routes depend on service methods existing
- Service methods depend on model changes (Phase 1)

### Parallel Opportunities

- T001, T002, T003, T004 can run in parallel (all model changes in same file but independent fields)
- T012 and T013 can run in parallel (template vs CSS — different files)
- T020 and T021 can run in parallel (template vs CSS — different files)
- T028 and T029 can run in parallel (gallery template vs reader template — different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (model extensions, registry refactor, tier defaults)
2. Complete Phase 2: Foundational (image service parameterization, Grok Imagine method)
3. Complete Phase 3: User Story 1 (grouped UI selector, all 5 models generating images)
4. **STOP and VALIDATE**: Test each model generates images, verify display names, check backward compat
5. Image model expansion is fully functional — no video yet, but all image providers working

### Incremental Delivery

1. Setup + Foundational → Service layer ready for all 5 models
2. Add User Story 1 → Users can select and use all image models
3. Add User Story 2 → Reference photos work with all providers
4. Add User Story 3 → Video generation for story scenes
5. Add User Story 4 → Videos visible in gallery and reader
6. Each story adds capability without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- The `_generate_dalle` method is renamed to `_generate_openai` to reflect its expanded role
- Old saved stories with `image_model="dalle"` need backward-compatible display name handling (T007)
- Video generation is asynchronous and chained after image generation — image must complete first
- httpx is already a transitive dependency of the openai package, so no new pip install needed
- The xAI OpenAI-compatible endpoint (`base_url="https://api.x.ai/v1"`) works for `images.generate` but NOT for `images.edit` — use raw httpx for editing
- Video files use the same static file serving pattern as images — no tier-scoped route needed
- Commit after each phase completion
- Stop at any checkpoint to validate independently
