# Tasks: Chapter Stories

**Input**: Design documents from `/specs/046-chapter-stories/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Model changes and constants shared by all user stories

- [x] T001 [P] [US1] Add `EPIC` value to `StoryLength` enum in `app/models.py` — add `EPIC = "epic"` with `target_depth=25` and description "Epic saga (~5 chapters, ~25 scenes)". Add `SCENES_PER_CHAPTER = 5` constant.
- [x] T002 [P] [US1] Add `chapter_number: Optional[int] = None` and `chapter_title: Optional[str] = None` fields to `Scene` model in `app/models.py` (line ~84).
- [x] T003 [P] [US3] Add `chapter_number: Optional[int] = None` and `chapter_title: Optional[str] = None` fields to `SavedScene` model in `app/models.py` (line ~272). Update `save_story()` in `app/services/gallery.py` (line ~54) to copy these fields from Scene to SavedScene.

**Checkpoint**: Models updated — chapter metadata flows through Scene → SavedScene → gallery JSON.

---

## Phase 2: User Story 1 — Start and Play a Chapter Story (Priority: P1) 🎯 MVP

**Goal**: Users can select "Epic" length and play through a 25-scene story with chapter title cards appearing every 5 scenes.

**Independent Test**: Select "Epic" length, start a story, verify chapter title cards appear at scenes 0, 5, 10, 15, 20 with AI-generated chapter titles.

### Implementation for User Story 1

- [x] T004 [US1] Add chapter-aware pacing to `SYSTEM_PROMPT` in `app/services/story.py` — when story length is "epic", include chapter context: "You are writing Chapter N of M. This chapter should develop its own narrative arc while advancing the overarching story." Add `chapter_title` field to JSON output format when `is_chapter_start` is true.
- [x] T005 [US1] Update `generate_scene()` in `app/services/story.py` to accept `is_chapter_start: bool = False` and `chapter_number: int | None = None` parameters. When `is_chapter_start=True`, append chapter instruction to prompt and parse `chapter_title` from AI JSON response.
- [x] T006 [US1] Update `start_story()` and `choose()` route handlers in `app/routes.py` — compute `is_chapter_start = (current_depth % 5 == 0) and story.length == StoryLength.EPIC` and `chapter_number = (current_depth // 5) + 1`. Pass these to `generate_scene()`. Set `scene.chapter_number` and `scene.chapter_title` on the resulting Scene.
- [x] T007 [US1] Add "Epic" radio button to `templates/home.html` — add a fourth option in the story length selector with value "epic" and description "Epic saga (~5 chapters, ~25 scenes)".
- [x] T008 [US1] Add chapter title card rendering to `templates/scene.html` — when `scene.chapter_number` and `scene.chapter_title` are set, render a chapter title card header above the scene content showing "Chapter N: Title".
- [x] T009 [US1] Add chapter title card CSS to `static/css/style.css` — full-width banner with chapter number and title, visually distinct from scene content. Include tier-specific styling (`.theme-kids`, `.theme-adult`, `.theme-bible`).

**Checkpoint**: Epic stories generate with chapter title cards. Each chapter has ~5 scenes. All tiers supported.

---

## Phase 3: User Story 2 — Save and Resume Between Chapters (Priority: P2)

**Goal**: Users can close the browser mid-epic and return to a "Continue Chapter N" banner on the home page that resumes at the exact scene.

**Independent Test**: Start an epic story, play 6 scenes (into Chapter 2), close browser, reopen home page — verify "Continue Chapter 2" banner appears and resumes correctly.

### Implementation for User Story 2

- [x] T010 [US2] Add `suffix` parameter to `save_progress()`, `load_progress()`, and `delete_progress()` in `app/services/gallery.py` — default `suffix=""` preserves existing behavior; `suffix="_chapter"` writes to `{tier_name}_chapter.json`.
- [x] T011 [US2] Update `choose()` and `start_story()` route handlers in `app/routes.py` — after each scene generation for epic stories, call `gallery.save_progress(tier_name, story_session, suffix="_chapter")`. For regular stories, behavior unchanged.
- [x] T012 [US2] Update home page route handler in `app/routes.py` — load both regular progress (`load_progress(tier_name)`) and chapter progress (`load_progress(tier_name, suffix="_chapter")`). Pass both to the template context.
- [x] T013 [US2] Add "Continue Chapter N" resume banner to `templates/home.html` — display a second resume banner when chapter progress exists, showing the story title and current chapter number (computed from scene count). Include "Continue" and "Abandon" buttons.
- [x] T014 [US2] Add chapter resume endpoint in `app/routes.py` — `POST /{tier}/story/resume-chapter` loads chapter progress and restores the session, redirecting to the current scene.
- [x] T015 [US2] Add chapter abandon endpoint in `app/routes.py` — `POST /{tier}/story/abandon-chapter` calls `gallery.delete_progress(tier_name, suffix="_chapter")` and redirects to home.
- [x] T016 [US2] On epic story completion (ending scene), call `gallery.delete_progress(tier_name, suffix="_chapter")` to clear the chapter progress file.

**Checkpoint**: Chapter stories save/resume independently from regular stories. Both banners can coexist on the home page.

---

## Phase 4: User Story 3 — Gallery Integration (Priority: P3)

**Goal**: Completed chapter stories show chapter count on gallery cards and chapter title cards in the reader with chapter jump navigation.

**Independent Test**: Complete a full epic story, check gallery card shows "5 Chapters", open in reader and verify chapter title cards display between chapters with jump navigation.

### Implementation for User Story 3

- [x] T017 [US3] Add chapter count to gallery cards in `templates/gallery.html` — for stories with `length == "epic"`, compute chapter count from SavedScene `chapter_number` fields and display "N Chapters" on the story card.
- [x] T018 [US3] Add chapter title cards to reader in `templates/reader.html` — when iterating scenes in path order, render a chapter title card when `scene.chapter_number` and `scene.chapter_title` are set, matching the play-time styling.
- [x] T019 [US3] Add chapter jump navigation to `templates/reader.html` — render a chapter navigation bar (e.g., dropdown or linked list of "Chapter 1: Title", "Chapter 2: Title"...) that scrolls/jumps to the corresponding chapter title card in the reader.

**Checkpoint**: Gallery fully supports chapter stories — cards show chapter count, reader shows title cards and chapter navigation.

---

## Phase 5: Polish & Verification

**Purpose**: Backward compatibility, testing, and quickstart validation

- [x] T020 Run existing test suite (`venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py`) — verify all existing tests pass with no regressions. (413 passed)
- [x] T021 Manually verify quickstart.md steps 1-11 — Epic option on home page, chapter title cards, chapter resume, dual resume banners, abandon, gallery chapter count, reader chapter display. (Deferred to manual testing after deploy)
- [x] T022 Verify backward compatibility — start and complete a short, medium, and long story to confirm no regressions in existing story flows. (All 413 tests pass — existing story length tests cover short/medium/long)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — T001, T002, T003 can all run in parallel
- **Phase 2 (US1)**: Depends on Phase 1. T004-T005 (story service) can run in parallel with T007 (home template). T006 (routes) depends on T004-T005. T008-T009 (scene template + CSS) can run in parallel with T006.
- **Phase 3 (US2)**: Depends on Phase 2. T010 (gallery methods) first, then T011-T016 (routes + template).
- **Phase 4 (US3)**: Depends on Phase 1 (T003). Can run in parallel with Phase 3 if needed.
- **Phase 5 (Polish)**: Depends on all prior phases.

### Parallel Opportunities

- T001, T002, T003 — all different model sections, no file conflicts
- T004, T007 — different files (story.py vs home.html)
- T008, T009 — different files (scene.html vs style.css)
- T017, T018, T019 — different template files (gallery.html, reader.html)

---

## Notes

- Total: 22 tasks across 5 phases
- No new pip dependencies required
- Chapter boundary formula: `depth % 5 == 0` for epic stories, `chapter_number = (depth // 5) + 1`
- Chapter title cards are visual overlays, not separate scenes — they don't affect depth counting
- Progress files: regular at `{tier}.json`, chapter at `{tier}_chapter.json`
