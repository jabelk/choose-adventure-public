# Tasks: Admin Portal

**Input**: Design documents from `/specs/018-admin-portal/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md

**Tests**: No automated tests. Manual testing per quickstart.md.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the foundational files that all user stories depend on.

- [X] T001 [P] Create AdminService skeleton in app/services/admin.py — class with `__init__` that sets up paths to STORIES_DIR, PROGRESS_DIR, IMAGES_DIR, VIDEOS_DIR (reuse path constants from existing services).
- [X] T002 [P] Create admin.html template in templates/admin.html — extends base.html, empty dashboard layout with sections for: storage summary, saved stories, in-progress saves, orphan cleanup. Use existing CSS custom properties and base styles.
- [X] T003 Create admin router in app/admin_routes.py — `APIRouter(prefix="/admin")` with a single GET `/` route that renders admin.html with empty context. Import AdminService.
- [X] T004 Mount admin router in app/main.py — import admin_routes and `app.include_router()` after the tier routers.

**Checkpoint**: Navigating to `/admin` renders an empty dashboard page.

---

## Phase 2: User Story 1 & 2 — Storage Dashboard + Story Management (Priority: P1)

**Goal**: Show storage stats and list all stories with delete capability.

**Independent Test**: Visit `/admin`, see accurate counts/sizes, see story list, delete a story and confirm files are removed.

- [X] T005 [US1] Implement `get_storage_stats()` in app/services/admin.py — returns dict with file counts and total bytes for each directory (stories, images, videos, progress). Use `Path.glob()` and `stat().st_size`.
- [X] T006 [US1] Implement `list_all_stories()` in app/services/admin.py — load all `.json` files from STORIES_DIR across all tiers. Return list of dicts with story_id, title, tier, model, image_model, created_at, scene_count. Handle corrupted files gracefully (include them with an error flag and just the filename).
- [X] T007 [US1] [US2] Wire storage stats and story list into GET `/admin` route in app/admin_routes.py — call AdminService methods and pass results to template context.
- [X] T008 [US1] [US2] Update admin.html template — render storage summary cards (story count, image count, video count, in-progress count, disk sizes formatted as human-readable KB/MB/GB) and a stories table (title, tier, model, date, scenes, delete button).
- [X] T009 [US2] Implement `delete_story(story_id)` in app/services/admin.py — load story JSON, extract all scene IDs, delete matching .png from static/images/ and .mp4 from static/videos/ for each scene ID, then delete the story JSON file. Log what was deleted. Handle missing files gracefully.
- [X] T010 [US2] Add POST `/delete-story/{story_id}` route in app/admin_routes.py — call `delete_story()`, redirect to `/admin`. Include `onclick="return confirm('Delete this story and all its images/videos?')"` on the delete buttons in the template.

**Checkpoint**: Admin page shows accurate storage stats and story list. Stories can be deleted with full media cascade.

---

## Phase 3: User Story 3 — Orphan Cleanup (Priority: P2)

**Goal**: Detect and bulk-delete image/video files not referenced by any story.

**Independent Test**: Place a random .png in static/images/, visit admin, see it counted as orphan, run cleanup, confirm it's deleted.

- [X] T011 [US3] Implement `get_orphaned_files()` in app/services/admin.py — collect all scene IDs from all saved stories AND all in-progress saves into a set. Compare against filenames (stem) in static/images/ and static/videos/. Return list of orphan paths with total size.
- [X] T012 [US3] Implement `cleanup_orphans()` in app/services/admin.py — delete all files returned by `get_orphaned_files()`. Return count of files deleted and bytes freed.
- [X] T013 [US3] Wire orphan stats into GET `/admin` route and add POST `/cleanup-orphans` route in app/admin_routes.py — show orphan count and size in template, button triggers cleanup with confirmation, redirects to `/admin`.
- [X] T014 [US3] Update admin.html template — add orphan cleanup section showing count of orphaned images, orphaned videos, total orphan size, and a "Clean Up Orphans" button (disabled/hidden if count is 0).

**Checkpoint**: Orphaned files are detected and displayed. Cleanup removes them while preserving legitimate files.

---

## Phase 4: User Story 4 — In-Progress Management (Priority: P2)

**Goal**: List and delete in-progress story saves.

**Independent Test**: Start a story, visit admin, see in-progress entry, delete it, confirm progress file removed.

- [X] T015 [US4] Implement `list_in_progress()` in app/services/admin.py — read each .json file in PROGRESS_DIR, extract tier name (from filename), prompt excerpt, and scene count from the StorySession data. Handle corrupted files gracefully.
- [X] T016 [US4] Implement `delete_in_progress(tier_name)` in app/services/admin.py — delete the progress file for the given tier. Also delete associated scene images/videos (extract scene IDs from the session data first).
- [X] T017 [US4] Wire in-progress list into GET `/admin` route and add POST `/delete-progress/{tier_name}` route in app/admin_routes.py — show in-progress list in template, delete button with confirmation, redirect to `/admin`.
- [X] T018 [US4] Update admin.html template — add in-progress section showing tier name, prompt excerpt (truncated to ~80 chars), scene count, and delete button for each entry.

**Checkpoint**: In-progress saves are visible and deletable from admin.

---

## Phase 5: Polish

- [X] T019 Add success flash messages to admin.html — after delete or cleanup actions, show a brief confirmation message (e.g., "Story deleted. Removed 3 images and 1 video."). Pass message via query parameter on redirect.
- [X] T020 Verify admin page works in Docker — deploy to NUC and test all actions (view stats, delete story, cleanup orphans, delete in-progress).

---

## Dependencies

- **Phase 1**: No dependencies — setup files can be created independently (T001, T002 are [P])
- **Phase 2 (US1/US2)**: Depends on Phase 1 (router and template must exist)
- **Phase 3 (US3)**: Depends on Phase 1 (shares same router and template); can run in parallel with Phase 2 for service methods
- **Phase 4 (US4)**: Depends on Phase 1 (shares same router and template); can run in parallel with Phase 2/3 for service methods
- **Phase 5**: Depends on all previous phases

## Notes

- All admin service methods go in a single file `app/services/admin.py` — keep it simple
- All admin routes go in a single file `app/admin_routes.py`
- Single template `templates/admin.html` updated incrementally across phases
- Use POST-redirect-GET pattern for all destructive actions
- JavaScript `confirm()` for all delete/cleanup confirmations
- Human-readable file sizes (format bytes as KB/MB/GB) in template
- Commit after each phase completes
