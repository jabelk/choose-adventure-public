# Tasks: Cover Art Generator

**Input**: Design documents from `/specs/045-cover-art-generator/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

---

## Phase 1: Setup (Model Extension)

**Purpose**: Add cover art fields to the SavedStory model

- [x] T001 Add `cover_art_url: Optional[str] = None` and `cover_art_status: str = "none"` fields to `SavedStory` model in `app/models.py` — stores cover image URL and generation status (none/generating/complete/failed)

**Checkpoint**: SavedStory model ready for cover art; existing gallery JSON files still load correctly with defaults

---

## Phase 2: User Story 1 — Cover Art on Story Completion (Priority: P1) MVP

**Goal**: When a story completes and is saved to gallery, generate a book-cover-style image asynchronously. Gallery shows cover art as thumbnail, falling back to first scene image.

**Independent Test**: Complete a story in any tier, navigate to the gallery, and verify the story card shows a cover art image after generation completes.

### Implementation

- [x] T002 [US1] Add `async generate_cover_art(story_id, title, prompt, image_model, tier, art_style)` method to `GalleryService` in `app/services/gallery.py` — builds a cover-specific image prompt from the story title and original prompt, calls `image_service.generate_image()`, saves image as `{story_id}_cover.png` in `static/images/`, then re-reads the story JSON, updates `cover_art_url` and `cover_art_status` to "complete", and re-writes the JSON; on failure sets status to "failed" and re-writes
- [x] T003 [US1] Update `save_story()` in `app/services/gallery.py` to set `cover_art_status = "generating"` on the SavedStory before writing the JSON file — this ensures the initial save includes the "generating" status
- [x] T004 [US1] Add `asyncio.create_task()` call after each `gallery_service.save_story()` invocation in `app/routes.py` — there are 5 trigger points (lines ~709, ~955, ~1319, ~1512, ~2963) where stories are saved on completion; each should kick off `gallery_service.generate_cover_art()` as a background task, passing `story_session.story.story_id`, `story_session.story.title`, `story_session.story.prompt`, `story_session.story.image_model`, `tier_config.name`, and `story_session.story.art_style`
- [x] T005 [US1] Update gallery card in `templates/gallery.html` to show cover art as thumbnail — check `story.cover_art_url` and `story.cover_art_status == "complete"` first; if available show the cover image; otherwise fall back to the existing first-scene-image logic
- [x] T006 [US1] Add CSS title/author overlay on gallery cards in `static/css/style.css` — position story title text over the cover art thumbnail using CSS overlay (absolute positioning over the card image); style differently per tier theme class

**Checkpoint**: Cover art generates on story completion, appears as gallery thumbnail on next page load. Falls back to first scene image when cover not ready.

---

## Phase 3: User Story 2 — Tier-Appropriate Cover Styling (Priority: P2)

**Goal**: Cover art prompts adapt to each tier's visual identity

**Independent Test**: Complete stories in kids, bible, and NSFW tiers. Verify each gallery shows covers with visually distinct, audience-appropriate styling.

### Implementation

- [x] T007 [US2] Add tier-specific cover style constants in `app/services/gallery.py` — define `COVER_STYLES` dict mapping tier names to cover prompt style strings: kids = "Bright, colorful children's book cover illustration, whimsical, friendly, cheerful atmosphere, picture book aesthetic", bible = "Warm, reverent Bible storybook cover illustration, golden light, classical painting style, inspirational", nsfw = "Stylized, atmospheric book cover art, bold composition, cinematic lighting, mature aesthetic"
- [x] T008 [US2] Update `generate_cover_art()` in `app/services/gallery.py` to incorporate tier-specific cover style and art style into the cover prompt — use `COVER_STYLES.get(tier, "")` for the base style, append `get_art_style_prompt(art_style)` if an art style was selected

**Checkpoint**: Covers across all tiers have visually distinct, audience-appropriate styling.

---

## Phase 4: User Story 3 — Regenerate Cover Art (Priority: P3)

**Goal**: Users can regenerate cover art for a completed story from the gallery

**Independent Test**: View a completed story in the gallery reader, click "Regenerate Cover", verify a new cover image is generated.

### Implementation

- [x] T009 [US3] Add `POST /{tier}/gallery/{story_id}/regenerate-cover` endpoint in `app/routes.py` — loads the SavedStory from disk via `gallery_service.get_story()`, updates `cover_art_status` to "generating" in the JSON, kicks off `gallery_service.generate_cover_art()` as an async task, redirects back to the gallery reader page for that story
- [x] T010 [US3] Add "Regenerate Cover" button to `templates/reader.html` — add a small form/button near the story header or export buttons area that POSTs to the regenerate-cover endpoint; only show when viewing the first scene of a completed story

**Checkpoint**: Users can regenerate covers. New cover replaces old one after generation.

---

## Phase 5: Polish & Verification

**Purpose**: Cross-cutting validation and cleanup

- [x] T011 Run existing test suite `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — all tests pass, no regressions (413 passed)
- [x] T012 Test backward compatibility — verify existing gallery stories without `cover_art_url` field load correctly (Pydantic defaults)
- [x] T013 Run quickstart.md verification steps end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (US1)**: Depends on Phase 1 completion
- **Phase 3 (US2)**: Depends on Phase 2 (needs `generate_cover_art()` method)
- **Phase 4 (US3)**: Depends on Phase 2 (needs `generate_cover_art()` method and gallery infrastructure)
- **Phase 5 (Polish)**: Depends on all prior phases

### Parallel Opportunities

- T005 and T006 (template and CSS) can run in parallel after T002-T004 are done
- T007 and T008 (tier styles) can start as soon as T002 is done
- T009 and T010 (regenerate endpoint and button) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: User Story 1 (T002-T006)
3. **STOP and VALIDATE**: Complete a story, check gallery for cover art
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Model ready
2. Phase 2 (US1) → Cover art on completion → Deploy
3. Phase 3 (US2) → Tier-appropriate styling → Deploy
4. Phase 4 (US3) → Regenerate button → Deploy
5. Phase 5 → Final verification

---

## Notes

- No new pip dependencies required
- `cover_art_url` and `cover_art_status` defaults ensure zero migration needed
- `generate_cover_art()` reuses `ImageService.generate_image()` — no new image infrastructure
- Cover images saved as `{story_id}_cover.png` to avoid collision with scene images
- The async task re-reads and re-writes the story JSON file after image generation
- Graceful degradation: gallery shows first scene image if cover is missing/failed
