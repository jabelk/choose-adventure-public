# Tasks: Story Recap / "Previously On..."

**Input**: Design documents from `/specs/044-story-recap/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

---

## Phase 1: Setup (Model Extension)

**Purpose**: Add the recap cache field to the StorySession model

- [x] T001 Add `recap_cache: dict[str, str] = Field(default_factory=dict)` field to `StorySession` model in `app/models.py` — stores cached recap text keyed by path hash

**Checkpoint**: StorySession model ready for recap caching

---

## Phase 2: User Story 1 — "Story So Far" Recap Section (Priority: P1) MVP

**Goal**: Collapsible recap section on scene pages at depth 2+, auto-expanded on resume, collapsed during active play. AI-generated summary fetched asynchronously.

**Independent Test**: Start a story, progress 3+ scenes, leave, resume from gallery. Verify recap section appears expanded with a 2-3 sentence summary. Navigate to next scene and verify it's collapsed.

### Implementation

- [x] T002 [US1] Add `generate_recap(scenes: list[Scene], model: str, content_guidelines: str)` async method to `StoryService` in `app/services/story.py` — calls `_call_provider()` with a recap-specific system prompt that requests a 2-3 sentence summary of the story events from the provided scene list, includes content_guidelines for tier-appropriate language
- [x] T003 [US1] Add `GET /{tier}/story/recap/{scene_id}` endpoint inside `create_tier_router()` in `app/routes.py` — checks `story_session.recap_cache` for a matching path-based key (`"|".join(path_history[:depth+1])`), if cached returns `{"status": "ok", "text": recap_text}` immediately, if not cached calls `story_service.generate_recap()` with `story_session.get_full_context()[:depth]` (scenes before current), caches result, returns JSON; on error returns `{"status": "error"}`
- [x] T004 [US1] Add `?resumed=1` query parameter to the redirect URL in the `resume_story()` route in `app/routes.py` — append `?resumed=1` to the scene redirect URL so the view handler can detect a resume
- [x] T005 [US1] Update `view_scene` handler in `app/routes.py` to pass recap context to template — add `show_recap` (True when `scene.depth >= 1`), `recap_expanded` (True when `request.query_params.get("resumed") == "1"`), and `recap_url` (`f"{url_prefix}/story/recap/{scene.scene_id}"`) to the template context dict
- [x] T006 [US1] Add collapsible "Story so far" section to `templates/scene.html` — insert a `<details>` element after the scene header and before the scene image, with a `<summary>` toggle reading "Story so far", conditionally add `open` attribute when `recap_expanded` is true, include a `<div id="recap-content">` placeholder with a loading spinner; only render when `show_recap` is true
- [x] T007 [US1] Add recap fetch JavaScript to `static/js/app.js` — on page load, if the recap container exists, fetch the `recap_url` from the `data-recap-url` attribute; on success set the recap text content; on error hide the recap section entirely; if the `<details>` element starts open (resume), fetch immediately; if collapsed, fetch on first toggle open
- [x] T008 [US1] Add CSS styles for `.recap-section`, `.recap-summary`, `.recap-text`, `.recap-loading` in `static/css/style.css` — subtle styling that matches the scene header aesthetic, italic recap text, small font size, appropriate padding for mobile

**Checkpoint**: Recap section works end-to-end. Scene pages at depth 2+ show the collapsible section. Resume shows it expanded. Active play shows it collapsed. AI generates summaries. Caching works.

---

## Phase 3: User Story 3 — Tier-Appropriate Recap Language (Priority: P3)

**Goal**: Recaps adapt language and tone to each tier's content style

**Independent Test**: Start stories in kids, nsfw, and bible tiers, progress 3+ scenes, expand recap section, verify language matches tier voice.

### Implementation

- [x] T009 [US3] Enhance the recap system prompt in `generate_recap()` in `app/services/story.py` — add tier-specific recap instructions: for kids tier include "Use very simple words and short sentences a 3-year-old can understand", for bible tier include "Use warm, reverent language befitting a Bible story", for nsfw include "Preserve the story's mature tone and atmosphere"; the `content_guidelines` parameter already carries the tier rules, but add explicit recap-style guidance on top

**Checkpoint**: Recaps in each tier use language appropriate to their audience.

---

## Phase 4: Polish & Verification

**Purpose**: Cross-cutting validation and cleanup

- [x] T010 Run existing test suite `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — all tests pass, no regressions
- [x] T011 Test backward compatibility — verify existing stories and sessions work without the new `recap_cache` field (default empty dict)
- [x] T012 Run quickstart.md verification steps end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (US1)**: Depends on Phase 1 completion
- **Phase 3 (US3)**: Depends on Phase 2 (needs `generate_recap()` method)
- **Phase 4 (Polish)**: Depends on all prior phases

### Parallel Opportunities

- T006, T007, T008 (template, JS, CSS) can run in parallel after T003-T005 are done
- T009 (tier language) can start as soon as T002 is done

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: User Story 1 (T002-T008)
3. **STOP and VALIDATE**: Start a story, progress 3 scenes, leave, resume — verify recap appears expanded
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Model ready
2. Phase 2 (US1) → Recap working → Deploy
3. Phase 3 (US3) → Tier-appropriate language → Deploy
4. Phase 4 → Final verification

---

## Notes

- No new pip dependencies required
- `recap_cache` default `{}` ensures zero migration needed
- The `generate_recap()` method reuses `_call_provider()` — no new AI service infrastructure
- Path-based cache key auto-invalidates on branch navigation changes
- The `?resumed=1` query parameter is the simplest resume detection — no model mutation needed
- Graceful degradation: JS hides the recap section on error, never shows error to user
