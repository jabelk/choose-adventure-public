# Tasks: Photo Import

**Input**: Design documents from `/specs/012-photo-import/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install new dependency, extend Character model, add photo storage directory to .gitignore.

- [X] T001 Install Pillow dependency for image dimension validation — run `venv/bin/pip install Pillow` and add `Pillow` to requirements.txt (or verify it's listed)
- [X] T002 Add optional `photo_path` field (str, default None) to the Character model in app/models.py — this stores the relative path from the data root to the photo file (e.g., `photos/kids/{profile_id}/{character_id}.jpg`)
- [X] T003 Add `data/photos/` to .gitignore alongside existing `data/profiles/` entry

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add photo file management methods to ProfileService and extend the profile context builder. All user stories depend on these service methods.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add photo storage constants and directory helper to app/services/profile.py — define `PHOTOS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "photos"`, add a `_photo_dir(tier, profile_id)` helper method that creates and returns `PHOTOS_DIR / tier / profile_id`
- [X] T005 Implement `save_character_photo(tier, profile_id, character_id, photo_bytes, content_type)` method in app/services/profile.py — validate content_type is JPEG or PNG, validate file size ≤ 5 MB, determine extension from content_type, save to `data/photos/{tier}/{profile_id}/{character_id}.{ext}`, delete any previous photo for this character, update the character's `photo_path` field in the profile JSON, return a tuple of (success: bool, warning: str | None) where warning is set if image dimensions are < 256x256 (use Pillow to check)
- [X] T006 Implement `delete_character_photo(tier, profile_id, character_id)` method in app/services/profile.py — delete the photo file from disk if it exists, set the character's `photo_path` to None in the profile JSON
- [X] T007 Implement `get_character_photo_path(tier, profile_id, character_id)` method in app/services/profile.py — return the absolute file path to the character's photo if `photo_path` is set and the file exists on disk, otherwise return None (graceful handling of missing/corrupted files per FR-015)
- [X] T008 Extend `delete_character()` in app/services/profile.py to also delete the character's photo file from disk before removing the character from the profile (FR-012)
- [X] T009 Extend `delete_profile()` in app/services/profile.py to also delete the entire `data/photos/{tier}/{profile_id}/` directory and all photos in it when a profile is deleted (FR-013)
- [X] T010 Extend `build_profile_context()` in app/services/profile.py to return a third value: a list of absolute photo file paths for characters that have photos — change return type from `tuple[str, str]` to `tuple[str, str, list[str]]`. Include photo paths from cross-profile linked characters (one level deep). Only include paths where the file actually exists on disk.

**Checkpoint**: ProfileService has all photo management methods. `build_profile_context()` returns photo paths alongside text context.

---

## Phase 3: User Story 1 — Upload a Reference Photo for a Character (Priority: P1) 🎯 MVP

**Goal**: Users can upload, replace, and remove reference photos for characters. Thumbnails appear on character cards.

**Independent Test**: Navigate to a profile edit page, upload a JPEG for a character, verify the thumbnail appears. Replace with a new photo, verify it changes. Remove the photo, verify it disappears. Try uploading a .gif — verify error. Try uploading > 5 MB — verify error.

### Implementation for User Story 1

- [X] T011 [P] [US1] Add photo upload form and thumbnail display to templates/profile_edit.html — for each character card, add: (1) an `<img>` thumbnail showing the current photo via `{{ url_prefix }}/photos/{{ profile.profile_id }}/{{ char.character_id }}` if `char.photo_path` is set, (2) a file upload form (`enctype="multipart/form-data"`) that POSTs to `{{ url_prefix }}/profiles/{{ profile.profile_id }}/characters/{{ char.character_id }}/photo`, (3) a "Remove Photo" button that POSTs to the photo delete route. Also add a photo upload field to the "Add Character" form.
- [X] T012 [P] [US1] Add photo thumbnail and upload form CSS styles to static/css/style.css — styles for `.character-photo`, `.character-photo img` (thumbnail sizing, border-radius), `.photo-upload-form`, `.photo-actions`, `.btn-remove-photo`. Thumbnail should be ~80x80px with object-fit cover.
- [X] T013 [US1] Add photo upload route to app/routes.py inside `create_tier_router()` — add `POST /profiles/{profile_id}/characters/{character_id}/photo` that accepts `photo: UploadFile`, reads the bytes, calls `profile_service.save_character_photo()`, handles errors (wrong format, too large) by redirecting with error query param, handles warnings (small image) by redirecting with warning query param. Redirect back to profile edit page.
- [X] T014 [US1] Add photo delete route to app/routes.py inside `create_tier_router()` — add `POST /profiles/{profile_id}/characters/{character_id}/photo/delete` that calls `profile_service.delete_character_photo()` and redirects back to profile edit page.
- [X] T015 [US1] Add photo serving route to app/routes.py inside `create_tier_router()` — add `GET /photos/{profile_id}/{character_id}` that calls `profile_service.get_character_photo_path()`, reads the file bytes, and returns a `Response` with the appropriate `Content-Type` header (image/jpeg or image/png based on file extension). Return 404 if photo not found. This enforces tier isolation since the route is scoped to `/{tier}/`.
- [X] T016 [US1] Add warning flash display support to templates/profile_edit.html — show a non-blocking warning banner (`.flash-warning` style) when the `warning` query param is present (e.g., "Image is smaller than 256x256 pixels — AI results may be poor")

**Checkpoint**: Photo upload, replace, remove, and thumbnail display all working. Validation enforced (format, size). Tier-isolated photo serving.

---

## Phase 4: User Story 2 — AI Image Generation Uses Reference Photos (Priority: P2)

**Goal**: When memory mode is active and a profile has characters with photos, the reference photos are passed to the AI image generation APIs to produce personalized story images.

**Independent Test**: Upload a reference photo for a character, start a story with memory mode on, verify the image generation request includes the reference photo. Start a story with memory mode off, verify no reference photos are included.

### Implementation for User Story 2

- [X] T017 [US2] Modify `_generate_dalle()` in app/services/image.py to accept an optional `reference_images: list[str]` parameter — when reference_images is non-empty, use `self.openai_client.images.edit()` with `model="gpt-image-1"`, `input_fidelity="high"`, and the photo files as input images instead of `images.generate()`. When empty, behavior is unchanged. Read each file path into bytes and convert to the format expected by the OpenAI API.
- [X] T018 [US2] Modify `_generate_gemini()` in app/services/image.py to accept an optional `reference_images: list[str]` parameter — when reference_images is non-empty, include the photo files as `inline_data` parts in the content array alongside the text prompt. Prepend the prompt with "Generate an image incorporating the people from the reference photos:". When empty, behavior is unchanged.
- [X] T019 [US2] Modify `generate_image()` in app/services/image.py to accept and pass through an optional `reference_images: list[str] = None` parameter — pass it down to `_generate_dalle()` or `_generate_gemini()` based on the selected model. Default to None for backward compatibility.
- [X] T020 [US2] Modify the `start_story` route in app/routes.py to collect reference photo paths from the profile context — when memory mode is on and a profile is loaded, unpack the third return value from `build_profile_context()` (the list of photo paths), and pass it to the `image_service.generate_image()` call as `reference_images`. Update the existing tuple unpacking from `(ctx_addition, style_addition)` to `(ctx_addition, style_addition, photo_paths)`.
- [X] T021 [US2] Modify the `make_choice` route in app/routes.py to re-apply reference photo paths on subsequent scene generation — same pattern as start_story: when `story_session.story.profile_id` is set, unpack photo paths from `build_profile_context()` and pass to `image_service.generate_image()`.

**Checkpoint**: Memory mode with photos produces personalized images. Memory mode off or no photos = standard generation unchanged.

---

## Phase 5: User Story 3 — Photo Management and Housekeeping (Priority: P3)

**Goal**: Photos are cleaned up on character/profile deletion. File size limits enforced.

**Independent Test**: Delete a character with a photo, verify the file is removed. Delete a profile with photo-linked characters, verify all photos cleaned up. Upload > 5 MB, verify rejection.

### Implementation for User Story 3

- [X] T022 [US3] Verify that `delete_character()` in app/services/profile.py correctly deletes the character's photo file — this was implemented in T008; test by creating a character with a photo, deleting the character, and verifying the photo file is gone from disk
- [X] T023 [US3] Verify that `delete_profile()` in app/services/profile.py correctly removes the entire photo directory — this was implemented in T009; test by creating a profile with multiple photo-linked characters, deleting the profile, and verifying the `data/photos/{tier}/{profile_id}/` directory is gone
- [X] T024 [US3] Verify upload validation — test that uploading a non-JPEG/PNG file returns an error, and that uploading a file > 5 MB returns an error. These validations were implemented in T005/T013.

**Checkpoint**: All cleanup and validation verified end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, validation, and end-to-end testing

- [X] T025 Verify tier isolation for photos — upload a photo in the kids tier, try accessing it via `http://localhost:8080/nsfw/photos/{profile_id}/{character_id}`, confirm 404 (FR-014, SC-004)
- [X] T026 Verify graceful handling of missing photo files — manually delete a photo file from disk, then load the profile edit page, confirm no error and no broken image displayed (FR-015)
- [X] T027 Verify cross-profile linked character photos — create two profiles in the same tier, add characters with photos to each, link a character to the other profile, start a story with memory mode on, verify both profiles' character photos are included in image generation
- [X] T028 Verify fallback when image model doesn't support references — if only text-based generation is available, confirm the story still generates normally without photos (FR-016)
- [X] T029 Run full quickstart.md validation (all 10 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T004-T010)
- **User Story 2 (Phase 4)**: Depends on Foundational phase AND User Story 1 (needs photos to exist to test generation)
- **User Story 3 (Phase 5)**: Depends on Foundational phase AND User Story 1 (needs photo upload working to test cleanup)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on US2 or US3
- **User Story 2 (P2)**: Can start after Foundational — but needs photos uploaded (US1) to meaningfully test
- **User Story 3 (P3)**: Mostly verification of existing implementations from earlier phases

### Within Each User Story

- Templates and CSS can be created in parallel (different files)
- Routes depend on templates existing
- Service methods must exist before routes call them

### Parallel Opportunities

- T011 and T012 can run in parallel (template vs CSS — different files)
- T017 and T018 can run in parallel (DALL-E vs Gemini — different methods, same file but independent)
- T001 and T003 can run in parallel (different files)
- T022, T023, T024 are independent verification tasks that can run in parallel

---

## Parallel Example: User Story 1

```bash
# Template and CSS can be created in parallel (different files):
Task: "Add photo upload form and thumbnail to profile_edit.html"    # T011
Task: "Add photo thumbnail CSS styles"                              # T012

# Routes are sequential (same file, depends on templates):
Task: "Add photo upload route"                                      # T013
Task: "Add photo delete route"                                      # T014
Task: "Add photo serving route"                                     # T015
Task: "Add warning flash display"                                   # T016
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Pillow, model extension, .gitignore)
2. Complete Phase 2: Foundational (photo CRUD methods in ProfileService)
3. Complete Phase 3: User Story 1 (upload/replace/remove photos, thumbnails)
4. **STOP and VALIDATE**: Upload photos, verify thumbnails, test constraints
5. Photo management is functional — no AI integration yet, but upload/display works

### Incremental Delivery

1. Setup + Foundational → Service layer ready
2. Add User Story 1 → Photo CRUD UI → Users can upload and manage photos
3. Add User Story 2 → AI integration → Photos influence image generation
4. Add User Story 3 → Verification → Cleanup and validation confirmed
5. Each story adds personalization depth without breaking the previous

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- New pip dependency: Pillow (for reading image dimensions to show < 256x256 warning)
- Photo serving route enforces tier isolation — photos at `/{tier}/photos/...` can only access that tier's files
- `build_profile_context()` return type changes from `tuple[str, str]` to `tuple[str, str, list[str]]` — all existing callers in routes.py must be updated to unpack three values
- OpenAI integration uses `images.edit` (not `images.generate`) when reference images are present
- Commit after each phase completion
- Stop at any checkpoint to validate independently
