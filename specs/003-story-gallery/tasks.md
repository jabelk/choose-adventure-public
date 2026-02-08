# Tasks: Story Gallery

**Input**: Design documents from `/specs/003-story-gallery/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/routes.md, quickstart.md

**Tests**: Not explicitly requested in spec. Tests omitted per Principle V (Fun Over Perfection).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `app/`, `templates/`, `static/` at repository root

---

## Phase 1: Setup (New Infrastructure)

**Purpose**: Create new files and data structures needed by the gallery

- [x] T001 [P] Create `app/models.py` additions — Add `SavedStory`, `SavedScene`, and `SavedChoice` Pydantic models per data-model.md. SavedStory fields: story_id, title, prompt, tier, length, target_depth, created_at, completed_at, scenes (dict[str, SavedScene]), path_history (list[str]). SavedScene fields: scene_id, parent_scene_id, choice_taken_id, content, image_url, image_prompt, choices (list[SavedChoice]), is_ending, depth. SavedChoice fields: choice_id, text, next_scene_id.
- [x] T002 [P] Create `app/services/gallery.py` — Implement GalleryService class with methods: `save_story(story_session: StorySession) -> None` converts a StorySession to SavedStory and writes JSON to `data/stories/{story_id}.json`; `list_stories(tier: str) -> list[SavedStory]` reads all JSON files from `data/stories/`, filters by tier, returns sorted by completed_at descending; `get_story(story_id: str) -> SavedStory | None` loads a single story by ID. Ensure `data/stories/` directory is created on init. Handle corrupted files gracefully (log warning, skip).
- [x] T003 Ensure `data/stories/` directory is created on app startup in `app/main.py` — Add `os.makedirs(BASE_DIR / "data" / "stories", exist_ok=True)` alongside the existing static/images makedirs.

**Checkpoint**: SavedStory model exists. GalleryService can save and load stories. Data directory is created on startup.

---

## Phase 2: User Story 3 — Auto-Save Completed Stories (Priority: P1)

**Goal**: When a story reaches its ending, the system automatically saves the complete story (all scenes + path taken) to disk as a JSON file.

**Independent Test**: Start a short story in `/kids/`, play through to "The End". Check that `data/stories/` contains a new JSON file with the story data. Restart the server and verify the file persists.

### Implementation for User Story 3

- [x] T004 [US3] Wire auto-save into `app/routes.py` — In the `make_choice` handler inside `create_tier_router`, after a new scene with `is_ending=true` is generated and added to the session, call `gallery_service.save_story(story_session)`. Import and instantiate `GalleryService` at module level alongside `StoryService` and `ImageService`. The save should happen after `update_session` so the session is fully up-to-date.
- [x] T005 [US3] Also wire auto-save for stories that start as endings in `app/routes.py` — In the `start_story` handler, if the first scene generated has `is_ending=true` (very short story), also trigger the save. This handles edge cases where Claude generates an immediate ending.

**Checkpoint**: Completing a story creates a JSON file in `data/stories/`. File contains all metadata, scenes, and path_history. Abandoned stories create no files.

---

## Phase 3: User Story 1 — Browse Past Stories (Priority: P1) 🎯 MVP

**Goal**: Users see a gallery page showing all completed stories for their tier with title, thumbnail, prompt, and date. Accessible from the home page.

**Independent Test**: Complete a story, visit `/{tier}/gallery`, verify the story appears as a card. Restart the server and verify persistence. Check that kids gallery doesn't show nsfw stories.

### Implementation for User Story 1

- [x] T006 [US1] Add gallery route `GET /{tier}/gallery` in `app/routes.py` — Inside `create_tier_router`, add a gallery endpoint that calls `gallery_service.list_stories(tier_config.name)` and renders `gallery.html` with the stories list and tier context via `_ctx()`.
- [x] T007 [P] [US1] Create `templates/gallery.html` — Extends `base.html`. Shows a header ("Story Gallery" or "{tier.display_name} Gallery"), then a grid of story cards. Each card shows: the first scene's image (from `story.scenes[story.path_history[0]].image_url`, with fallback placeholder), story title, prompt excerpt (truncated to ~80 chars), and formatted date. Each card links to `{{ url_prefix }}/gallery/{{ story.story_id }}`. Include an empty state message ("No adventures yet! Start one to see it here.") with a link back to the home page. Add a "Back to Home" link at the top.
- [x] T008 [P] [US1] Add gallery card styles in `static/css/style.css` — Add `.gallery-header`, `.story-grid` (CSS grid, responsive 1-2 columns), `.story-card` (image thumbnail, title, prompt excerpt, date), `.story-card:hover` (accent border, slight lift), `.gallery-empty` (centered text, friendly message). Ensure styles use CSS custom properties for tier theming.
- [x] T009 [US1] Add gallery link to `templates/home.html` — Add a "View Gallery" link below the prompt form or in the header area. Link to `{{ url_prefix }}/gallery`. Style it as a subtle secondary link, not overpowering the main prompt form.

**Checkpoint**: Gallery page shows completed stories with cards. Tier isolation works. Empty state displays correctly. Gallery is accessible from the home page. Stories survive server restarts.

---

## Phase 4: User Story 2 — Read a Past Story (Priority: P2)

**Goal**: Users can click into a story from the gallery and read through it scene by scene in the original order taken.

**Independent Test**: Click a story card in the gallery. Verify first scene shows with text, image, and a "Next" button. Navigate through all scenes. Verify "Previous" works. Verify the final scene has no "Next" and shows "Back to Gallery".

### Implementation for User Story 2

- [x] T010 [US2] Add story reader routes in `app/routes.py` — Inside `create_tier_router`, add: `GET /{tier}/gallery/{story_id}` which loads the story via `gallery_service.get_story(story_id)`, validates it belongs to this tier, and redirects to `/{tier}/gallery/{story_id}/0`. `GET /{tier}/gallery/{story_id}/{scene_index}` which loads the story, validates tier and scene_index bounds, extracts the scene from `story.scenes[story.path_history[scene_index]]`, and renders `reader.html` with story, scene, scene_index, total_scenes, has_next, has_prev context. Invalid story_id or out-of-bounds index redirects to `/{tier}/gallery`.
- [x] T011 [P] [US2] Create `templates/reader.html` — Extends `base.html`. Shows story title and chapter indicator ("Chapter X of Y"). Displays scene image (or fallback) and scene narrative text. Navigation: "Previous" button (links to `{{ url_prefix }}/gallery/{{ story.story_id }}/{{ scene_index - 1 }}`, hidden on first scene), "Next" button (links to `{{ url_prefix }}/gallery/{{ story.story_id }}/{{ scene_index + 1 }}`, hidden on last scene). On the final scene, show "Back to Gallery" link to `{{ url_prefix }}/gallery`. Also add a persistent "Back to Gallery" link in the header.
- [x] T012 [P] [US2] Add reader styles in `static/css/style.css` — Add `.reader-header` (title + chapter), `.reader-nav` (flex row with prev/next buttons), `.reader-scene` (text and image layout similar to scene.html). Reuse existing `.scene-text`, `.scene-image-container` styles where possible. Ensure styles use CSS custom properties for tier theming.

**Checkpoint**: Clicking a gallery card opens the reader on the first scene. Next/Previous navigation works through all scenes in the original path order. Final scene shows "Back to Gallery". Reader is read-only (no choices).

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T013 [P] Validate quickstart.md — Follow `specs/003-story-gallery/quickstart.md` steps end-to-end.
- [x] T014 [P] Code cleanup — Review all modified files for: unused imports, hardcoded URLs that should use url_prefix, missing tier context in templates.
- [x] T015 Tier isolation audit — Complete a story in each tier. Verify each tier's gallery shows only its own stories. Verify reader URLs are tier-scoped.
- [x] T016 Manual end-to-end test — Play through a full story in kids tier (short length for speed), verify it auto-saves, appears in gallery, and is readable scene by scene. Restart the server and verify the story persists.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US3 Auto-Save (Phase 2)**: Depends on Phase 1 (needs SavedStory model and GalleryService)
- **US1 Browse Gallery (Phase 3)**: Depends on Phase 2 (needs saved stories to display)
- **US2 Read Story (Phase 4)**: Depends on Phase 3 (needs gallery page to link from)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Within Each Phase

- Phase 1: T001 and T002 can run in parallel (different files). T003 depends on nothing but is trivial.
- Phase 2: T004 first, then T005 (both modify routes.py).
- Phase 3: T006 first (adds route), then T007+T008 in parallel (template and CSS), then T009 (home link).
- Phase 4: T010 first (adds routes), then T011+T012 in parallel (template and CSS).
- Phase 5: T013-T016, sequential verification.

### Parallel Opportunities

```bash
# Phase 1: Setup tasks in parallel
Task: "Create SavedStory models in app/models.py"
Task: "Create GalleryService in app/services/gallery.py"

# Phase 3: Template and CSS in parallel (after route)
Task: "Create templates/gallery.html"
Task: "Add gallery styles in static/css/style.css"

# Phase 4: Template and CSS in parallel (after route)
Task: "Create templates/reader.html"
Task: "Add reader styles in static/css/style.css"
```

---

## Implementation Strategy

### MVP First (Auto-Save + Gallery Browsing)

1. Complete Phase 1: Setup (~10 min)
2. Complete Phase 2: Auto-Save (~15 min)
3. Complete Phase 3: Gallery Browsing (~30 min)
4. **STOP and VALIDATE**: Complete a story, verify it appears in the gallery, restart server, verify persistence
5. You now have a working story archive!

### Incremental Delivery

1. Complete Setup → Models and service ready
2. Add Auto-Save → Stories persist on completion
3. Add Gallery Browse → **Gallery is functional!** (MVP)
4. Add Story Reader → Full re-reading experience
5. Polish → Final audit and cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (per CLAUDE.md branching strategy)
- Stop at any checkpoint to validate story independently
- No tests were generated (not requested in spec, per Principle V — Fun Over Perfection)
- This feature adds new files and modifies existing ones — careful not to break v2 (content isolation) functionality
