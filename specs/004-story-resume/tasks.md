# Tasks: Story Resume

**Input**: Design documents from `/specs/004-story-resume/`
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

**Purpose**: Create the progress persistence layer and data directory

- [x] T001 Add `data/progress/` directory creation to `app/main.py` — Add `os.makedirs(BASE_DIR / "data" / "progress", exist_ok=True)` alongside the existing `data/stories` makedirs call.
- [x] T002 Add progress persistence methods to `app/services/gallery.py` — Add three methods to GalleryService: `save_progress(tier_name: str, story_session: StorySession)` serializes the full StorySession to `data/progress/{tier_name}.json` using `model_dump_json(indent=2)`; `load_progress(tier_name: str) -> StorySession | None` loads and validates the JSON file, returning None if missing or corrupted (log warning on corruption); `delete_progress(tier_name: str)` deletes the progress file if it exists. Use a `PROGRESS_DIR` constant similar to the existing `STORIES_DIR`.
- [x] T003 Add `data/progress/` to `.gitignore` — Add the line `data/progress/` below the existing `data/stories/` entry.

**Checkpoint**: GalleryService can save, load, and delete progress files. The `data/progress/` directory is created on startup.

---

## Phase 2: User Story 1 — Resume an In-Progress Story (Priority: P1) 🎯 MVP

**Goal**: Users can close their browser mid-story and resume from the exact scene when they return.

**Independent Test**: Start a story in `/kids/`, make 2 choices, close browser. Reopen tier home — verify resume banner with story title. Click "Continue" — verify you're back at the last scene.

### Implementation for User Story 1

- [x] T004 [US1] Wire auto-save into `start_story` in `app/routes.py` — After creating the session and before returning the redirect, call `gallery_service.save_progress(tier_config.name, story_session)`. Skip if the scene is an ending (the gallery save already handles that). Also, before generating the new story, call `gallery_service.delete_progress(tier_config.name)` to replace any existing in-progress save (FR-009).
- [x] T005 [US1] Wire auto-save into `make_choice` in `app/routes.py` — After `update_session(session_id, story_session)`, call `gallery_service.save_progress(tier_config.name, story_session)`. If the new scene is an ending, call `gallery_service.delete_progress(tier_config.name)` instead (the gallery save already happens).
- [x] T006 [US1] Wire auto-save into `go_back` in `app/routes.py` — After `update_session(session_id, story_session)`, call `gallery_service.save_progress(tier_config.name, story_session)`.
- [x] T007 [US1] Add resume check to `tier_home` in `app/routes.py` — In the `tier_home` handler, call `gallery_service.load_progress(tier_config.name)`. If a StorySession is returned, extract `resume_story` context: `title` (from story.title), `prompt` (from story.prompt), `scene_count` (len of path_history). Pass `resume_story` dict to the template context.
- [x] T008 [US1] Add resume route `GET /{tier}/story/resume` in `app/routes.py` — New route inside `create_tier_router`. Load StorySession from `gallery_service.load_progress(tier_config.name)`. If None, redirect to home. Otherwise: create an in-memory session via `create_session()`, set the session cookie, and redirect to `/{tier}/story/scene/{story.current_scene_id}`. Handle corrupted files by deleting progress and redirecting to home.
- [x] T009 [US1] Add resume banner to `templates/home.html` — Above the prompt form, add a conditional block: `{% if resume_story %}` showing a banner with the story title, scene count, a "Continue" link (to `{{ url_prefix }}/story/resume`), and a "Start Fresh" button (form POST to `{{ url_prefix }}/story/abandon`). `{% endif %}`.
- [x] T010 [P] [US1] Add resume banner styles to `static/css/style.css` — Add `.resume-banner` styles: card-like appearance with accent border, story title prominent, two action buttons side by side ("Continue" primary, "Start Fresh" secondary). Use CSS custom properties for tier theming. Should sit naturally above the prompt form.

**Checkpoint**: Starting a story auto-saves to disk. Closing browser and reopening shows resume banner. Clicking "Continue" restores the session and navigates to the last scene. Story survives server restarts.

---

## Phase 3: User Story 2 — Abandon a Story and Start Fresh (Priority: P2)

**Goal**: Users can explicitly abandon their in-progress story and return to a clean prompt form.

**Independent Test**: With an in-progress story, visit home page, click "Start Fresh". Verify banner disappears, prompt form is clean, progress file is deleted.

### Implementation for User Story 2

- [x] T011 [US2] Add abandon route `POST /{tier}/story/abandon` in `app/routes.py` — New route inside `create_tier_router`. Call `gallery_service.delete_progress(tier_config.name)`. Get the session ID from the cookie and call `delete_session(session_id)` if it exists (import `delete_session` from `app.session`). Delete the session cookie on the response. Redirect to `/{tier}/`.

**Checkpoint**: Clicking "Start Fresh" on the resume banner deletes the progress file, clears the session, and returns to a clean home page with no banner.

---

## Phase 4: User Story 3 — Completed Stories Clear the Save (Priority: P1)

**Goal**: Completing a story removes the in-progress save and moves it to the gallery.

**Independent Test**: Resume an in-progress story, play to "The End". Visit home — no banner. Visit gallery — story appears.

### Implementation for User Story 3

- [x] T012 [US3] Verify completion cleanup in `make_choice` in `app/routes.py` — Confirm that the `delete_progress` call added in T005 (when `new_scene.is_ending`) correctly removes the progress file when a story completes. Also verify the existing `gallery_service.save_story()` call still runs. This should already be handled by T005 — this task is a verification pass, not new code.
- [x] T013 [US3] Verify completion cleanup in `start_story` in `app/routes.py` — Confirm that if the first scene is an ending, the progress file is not created (or is immediately deleted). The `delete_progress` call in T004 (before generating) plus the skip-if-ending logic should handle this. Verification pass only.

**Checkpoint**: Completing a story results in: no progress file, story in gallery, no resume banner on home page.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T014 [P] Validate quickstart.md — Follow `specs/004-story-resume/quickstart.md` steps end-to-end.
- [x] T015 [P] Code cleanup — Review all modified files for: unused imports, missing error handling on file I/O, hardcoded paths that should use constants.
- [x] T016 Tier isolation audit — Start a story in kids tier, verify `data/progress/kids.json` exists. Visit nsfw tier home — verify no resume banner. Start a story in nsfw — verify both files exist independently.
- [x] T017 Server restart test — With an in-progress kids story, stop and restart the server. Visit kids home — verify resume banner appears. Click "Continue" — verify full story state restored.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 Resume (Phase 2)**: Depends on Phase 1 (needs progress persistence methods)
- **US2 Abandon (Phase 3)**: Depends on Phase 2 (needs resume banner to exist for the "Start Fresh" button)
- **US3 Completion Cleanup (Phase 4)**: Depends on Phase 2 (verification of T004/T005 behavior)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Within Each Phase

- Phase 1: T001, T002, T003 can all run in parallel (different files).
- Phase 2: T004 → T005 → T006 (all modify routes.py sequentially). T007 after T004-T006. T008 after T007. T009 after T007 (needs template context). T010 in parallel with T009 (CSS vs template).
- Phase 3: T011 depends on Phase 2 complete.
- Phase 4: T012-T013 are verification tasks, depend on Phase 2.
- Phase 5: T014-T017, sequential verification.

### Parallel Opportunities

```bash
# Phase 1: All setup tasks in parallel
Task: "Add data/progress/ dir creation in app/main.py"
Task: "Add progress methods to app/services/gallery.py"
Task: "Add data/progress/ to .gitignore"

# Phase 2: Template and CSS in parallel (after route work)
Task: "Add resume banner to templates/home.html"
Task: "Add resume banner styles to static/css/style.css"
```

---

## Implementation Strategy

### MVP First (Auto-Save + Resume)

1. Complete Phase 1: Setup (~5 min)
2. Complete Phase 2: Resume Story (~20 min)
3. **STOP and VALIDATE**: Start a story, close browser, reopen — verify resume works
4. You now have working story persistence!

### Incremental Delivery

1. Complete Setup → Progress persistence ready
2. Add Resume (US1) → **Story resume is functional!** (MVP)
3. Add Abandon (US2) → Users can start fresh
4. Verify Completion (US3) → Gallery integration confirmed
5. Polish → Final audit and cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (per CLAUDE.md branching strategy)
- Stop at any checkpoint to validate story independently
- No tests were generated (not requested in spec, per Principle V — Fun Over Perfection)
- This feature modifies existing files heavily (routes.py, gallery.py, home.html) — careful not to break existing gallery functionality
- Phase 4 (US3) is mostly verification — the actual cleanup logic is wired in Phase 2
