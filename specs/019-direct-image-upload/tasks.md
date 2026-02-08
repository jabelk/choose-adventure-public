# Tasks: Direct Image Upload

**Input**: Design documents from `/specs/019-direct-image-upload/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md

**Tests**: No automated tests. Manual testing per quickstart.md.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the foundational files that all user stories depend on.

- [X] T001 [P] Create UploadService skeleton in app/services/upload.py — class with `__init__` that sets up `UPLOADS_DIR = Path("data/uploads")`, creates the directory if it doesn't exist. Add constants: `MAX_FILES = 3`, `MAX_FILE_SIZE = 10 * 1024 * 1024`, `ALLOWED_TYPES = {"image/jpeg", "image/png"}`.
- [X] T002 [P] Add `reference_photo_paths` field to Story model in app/models.py — add `reference_photo_paths: list[str] = Field(default_factory=list)` to the Story class. This stores absolute paths to uploaded temp files so they persist through the session.

**Checkpoint**: UploadService file exists with constants. Story model has the new field. No functional changes yet.

---

## Phase 2: User Story 1 & 2 — Upload Reference Photos + Thumbnail Preview (Priority: P1)

**Goal**: Users can upload 1-3 photos on the story start form with drag-and-drop, see thumbnail previews, remove photos, and have them passed as reference images to the image generator for every scene.

**Independent Test**: Upload 1-3 photos on the story form, verify thumbnails appear, remove one, start the story, verify generated images use the reference photos. Also test with no photos to confirm zero regression.

- [X] T003 [P] [US1] [US2] Create client-side upload JavaScript in static/js/upload.js — implement: (a) file input change handler that validates type (JPEG/PNG only) and size (10MB max), enforces max 3 files, (b) drag-and-drop handlers on the upload area (dragover, dragleave, drop), (c) thumbnail preview generation using FileReader.readAsDataURL(), (d) remove button (X) on each thumbnail that removes the file from the selection, (e) dynamic form enctype switch to multipart/form-data when files are present and back to default when empty, (f) maintain a DataTransfer object to track the current file list and sync it to the file input before form submit.
- [X] T004 [P] [US1] [US2] Add "Reference Photos" upload section to templates/home.html — add a new form section after the existing options (before the submit button) with: (a) section label "Reference Photos (optional)", (b) a drop zone div with dashed border that shows "Drag & drop photos here or click to browse", (c) a hidden file input with `accept="image/jpeg,image/png"` and `multiple`, (d) a thumbnail preview container div, (e) a status message area for errors (wrong type, too large, max exceeded). Include `<script src="{{ url_prefix }}/static/js/upload.js"></script>` at the end.
- [X] T005 [US1] Implement `save_upload_files(session_id, files)` in app/services/upload.py — accepts a session_id string and list of UploadFile objects. Validates each file (type in ALLOWED_TYPES, size <= MAX_FILE_SIZE, total count <= MAX_FILES). Creates `data/uploads/{session_id}/` directory. Saves each file as `{index}_{original_filename}` (sanitized). Returns list of absolute file path strings. Raises ValueError with descriptive message on validation failure.
- [X] T006 [US1] Implement `get_upload_paths(session_id)` in app/services/upload.py — returns list of absolute paths to all uploaded files for a given session_id. Returns empty list if the session directory doesn't exist.
- [X] T007 [US1] Modify start_story handler in app/routes.py — add `reference_photos: list[UploadFile] = File(default=[])` parameter. After session creation, if reference_photos is non-empty: call `upload_service.save_upload_files(session_id, reference_photos)` to save files and get paths. Store paths in `story.reference_photo_paths`. When determining photo_paths for image generation: if `story.reference_photo_paths` is non-empty, use those (direct uploads override profile photos per FR-008); otherwise fall back to profile photo_paths from memory mode.
- [X] T008 [US1] Modify make_choice handler in app/routes.py — when loading photo_paths for image generation, check `session.story.reference_photo_paths` first (direct uploads). If non-empty, use those. Otherwise fall back to profile-based photo_paths from memory mode. This ensures every scene in the story uses the uploaded reference photos.
- [X] T009 [US1] Add UploadService import and instantiation in app/routes.py — inside `create_tier_router()`, instantiate `upload_service = UploadService()`. Add the necessary import at the top of routes.py: `from app.services.upload import UploadService` and `from fastapi import File, UploadFile`.

**Checkpoint**: Users can upload photos, see thumbnails, remove them, and start stories with reference images used in every scene. Stories without uploads work normally.

---

## Phase 3: User Story 3 — Cleanup Temporary Files (Priority: P2)

**Goal**: Temporary uploaded photos are cleaned up when the story session ends or is abandoned.

**Independent Test**: Upload photos, start a story, complete or abandon it, verify `data/uploads/{session_id}/` is deleted.

- [X] T010 [US3] Implement `cleanup_session(session_id)` in app/services/upload.py — deletes the `data/uploads/{session_id}/` directory and all its contents using `shutil.rmtree()`. Handles gracefully if the directory doesn't exist (no error). Logs the cleanup action.
- [X] T011 [US3] Add cleanup on story completion in app/routes.py — in the `save_story` handler (where story is saved to gallery), after saving, call `upload_service.cleanup_session(session_id)` to remove temporary upload files.
- [X] T012 [US3] Add cleanup on new story start in app/routes.py — in the `start_story` handler, if there's an existing session (from cookie), call `upload_service.cleanup_session(old_session_id)` before creating the new session. This handles the "abandoned story" case.
- [X] T013 [US3] Add upload cleanup to admin delete-progress in app/admin_routes.py — when admin deletes an in-progress save, also clean up any associated upload files. Load the progress file to get the session_id, then call `UploadService().cleanup_session(session_id)`.
- [X] T014 [US3] Add orphaned upload directory cleanup to admin orphan detection in app/services/admin.py — in `get_orphaned_files()` and `cleanup_orphans()`, also check for upload directories in `data/uploads/` that don't match any active session. Include them in orphan counts and cleanup.

**Checkpoint**: Temp files are cleaned up on story completion, abandonment, and admin deletion. Orphaned upload directories are caught by admin cleanup.

---

## Phase 4: Polish

- [X] T015 Ensure data/uploads/ directory is created on app startup in app/main.py — add `Path("data/uploads").mkdir(parents=True, exist_ok=True)` alongside existing directory creation.
- [X] T016 Verify full flow per quickstart.md — run through all 6 test scenarios manually. Fix any issues found.

---

## Dependencies

- **Phase 1**: No dependencies — setup files can be created independently (T001, T002 are [P])
- **Phase 2 (US1/US2)**: Depends on Phase 1 (UploadService and Story model must exist). T003 and T004 can run in parallel (different files). T005-T006 depend on T001. T007-T009 depend on T005, T004.
- **Phase 3 (US3)**: Depends on Phase 2 (upload flow must work before cleanup can be tested)
- **Phase 4**: Depends on all previous phases

## Notes

- US1 and US2 are combined into Phase 2 because they're both P1 priority and deeply intertwined (the upload UI and preview are the same component)
- UploadService follows the same pattern as ProfileService for file handling
- The `File(default=[])` parameter in FastAPI allows the file upload to be optional — no files is fine
- `reference_photo_paths` is stored in the Story model (persisted in progress JSON) so it survives session restarts
- Client-side JS handles all preview/validation UX; server-side validates again for security
- Commit after each phase completes
