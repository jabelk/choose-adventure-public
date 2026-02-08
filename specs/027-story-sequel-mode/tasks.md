# Tasks: Story Sequel Mode

**Input**: Design documents from `/specs/027-story-sequel-mode/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not explicitly requested in the spec. Tests added in polish phase for completeness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new dependencies needed. Skip to foundational.

(No tasks in this phase.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Model fields and bug fix that all user stories depend on.

- [X] T001 [P] Add `parent_story_id: Optional[str] = None` and `sequel_context: str = ""` fields to `Story` model in `app/models.py`; add `parent_story_id: Optional[str] = None` and `sequel_story_ids: list[str] = Field(default_factory=list)` fields to `SavedStory` model in `app/models.py`
- [X] T002 [P] Fix `save_story()` in `app/services/gallery.py` to persist all Story fields to SavedStory — add missing fields: `art_style`, `protagonist_gender`, `protagonist_age`, `character_type`, `num_characters`, `writing_style`, `conflict_type`, `roster_character_ids`, `bedtime_mode`, `parent_story_id` to the `SavedStory()` constructor call
- [X] T003 [P] Add CSS styles for `.btn-continue-story` button and `.sequel-chain-nav` links in `static/css/style.css` — button styled like existing export buttons, chain nav links styled as small muted links above/below the reader nav

**Checkpoint**: Model fields and gallery persistence ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Continue a Completed Story (Priority: P1)

**Goal**: Users can click "Continue Story" on any completed gallery story to start a sequel that inherits characters, settings, and uses the ending scene as AI context.

**Independent Test**: Open a completed story in the gallery reader, click "Continue Story," verify a new active story session starts with inherited character fields and the AI's opening scene references the prior ending.

### Implementation for User Story 1

- [X] T004 [US1] Add `POST /gallery/{story_id}/continue` route in `app/routes.py` — load SavedStory via `gallery_service.get_story()`, verify `saved.tier == tier_config.name`, extract the ending scene (last scene in `path_history`), build content_guidelines from tier + sequel context prompt (per research.md Decision 5) + character blocks + kink prompts + story flavor, build image_style from tier + art_style, create new Story with inherited fields (`character_name`, `character_description`, `kinks`, `conflict_type`, `writing_style`, `art_style`, `model`, `image_model`, `roster_character_ids`, `protagonist_gender`, `protagonist_age`, `character_type`, `num_characters`, `parent_story_id=saved.story_id`), call `story_service.generate_scene()`, create StorySession, redirect to first scene
- [X] T005 [US1] Add "Continue Story" button to `templates/reader.html` — add a `<form action="{{ url_prefix }}/gallery/{{ story.story_id }}/continue" method="post">` with a submit button styled as `.btn-continue-story` in the `reader-nav` div, next to the export buttons

**Checkpoint**: Core sequel launch works. Users can continue any gallery story with one click. All character details carried over.

---

## Phase 4: User Story 2 - Sequel Customization Before Launch (Priority: P2)

**Goal**: A customization form appears between clicking "Continue Story" and generating the sequel, pre-filled with the original story's settings, allowing users to adjust length, kinks, prompt direction, and models.

**Independent Test**: Click "Continue Story," verify a form appears pre-filled with original settings, change the story length, submit, verify the sequel uses the updated length.

### Implementation for User Story 2

- [X] T006 [US2] Add `GET /gallery/{story_id}/continue` route in `app/routes.py` — load SavedStory, verify tier, extract settings, render `sequel_customize.html` with context: original story fields, available_models, available_image_models, art_styles, kink_toggles (for NSFW), story_option_groups
- [X] T007 [US2] Create `templates/sequel_customize.html` — extends `base.html`, form pre-filled with original story's length (radio buttons), kinks (checkboxes, NSFW only), character name/description (text inputs), model selectors, art style selector, and a new "sequel prompt" textarea for direction hint; form POSTs to the existing `POST /gallery/{story_id}/continue` route
- [X] T008 [US2] Update `POST /gallery/{story_id}/continue` route in `app/routes.py` to accept optional form parameters — add `length`, `kinks`, `sequel_prompt`, `model`, `image_model`, `art_style` as `Form("")` params with fallback to original story values; incorporate sequel_prompt into the sequel context prompt if provided
- [X] T009 [US2] Update "Continue Story" button in `templates/reader.html` to link to GET customization form instead of POST — change from `<form method="post">` to `<a href="{{ url_prefix }}/gallery/{{ story.story_id }}/continue">` styled as `.btn-continue-story`

**Checkpoint**: Sequel customization form works. Users can adjust settings before launching a sequel.

---

## Phase 5: User Story 3 - Sequel Chain Visibility (Priority: P3)

**Goal**: Gallery reader pages show sequel chain navigation — "Sequel of: [title]" and "Continued in: [title]" links — so users can trace multi-part sagas.

**Independent Test**: Create a sequel from a story, verify the sequel's reader page shows "Sequel of: [Original Title]" link, verify the original story's reader page shows "Continued in: [Sequel Title]" link.

### Implementation for User Story 3

- [X] T010 [US3] Add `update_sequel_link()` method to `GalleryService` in `app/services/gallery.py` — given a `parent_story_id` and `sequel_story_id`, load the parent story's JSON, append `sequel_story_id` to its `sequel_story_ids` list if not already present, write back to disk
- [X] T011 [US3] Call `update_sequel_link()` in `save_story()` in `app/services/gallery.py` — after saving a story, check if `story.parent_story_id` is set, and if so call `update_sequel_link(story.parent_story_id, story.story_id)`
- [X] T012 [US3] Update `gallery_reader` route in `app/routes.py` to pass sequel chain data to template — look up `parent_story` (if `saved.parent_story_id` is set, load via `gallery_service.get_story()`), look up sequel stories (for each ID in `saved.sequel_story_ids`, load title via `gallery_service.get_story()`), pass `parent_story` and `sequel_stories` to template context
- [X] T013 [US3] Add sequel chain navigation markup to `templates/reader.html` — before the `reader-nav` div, conditionally render "Sequel of: [title]" link (if `parent_story`) and "Continued in: [title]" links (for each `sequel_story`) using the `.sequel-chain-nav` CSS class

**Checkpoint**: Sequel chain visibility complete. Users can navigate between related stories in a chain.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation across all user stories.

- [X] T014 Create `tests/test_sequel_mode.py` with tests covering: continue button visible on reader page, POST continue route creates new session with inherited fields (character_name, kinks, model, image_model, art_style, parent_story_id), sequel context includes original ending content, cross-tier continue rejected, missing story redirects to gallery, save_story persists all fields including new parent_story_id and sequel_story_ids, sequel chain links appear on reader
- [X] T015 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — model fields and gallery fix can start immediately
- **User Story 1 (Phase 3)**: Depends on T001 + T002 (model fields and save_story fix)
- **User Story 2 (Phase 4)**: Depends on US1 complete (modifies the route and button created in US1)
- **User Story 3 (Phase 5)**: Depends on US1 complete (needs sequel stories in gallery to test chain links)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T001, T002, and T003 (model fields, gallery fix, CSS) can run in parallel (different files)
- T010 and T012 can run in parallel within US3 (different files: gallery.py vs routes.py)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 + T002 + T003 (model + gallery fix + CSS)
2. Complete T004 + T005 (continue route + reader button)
3. **STOP and VALIDATE**: Continue a gallery story, verify character carryover and sequel context
4. This alone delivers the core value — one-click sequel from any completed story

### Incremental Delivery

1. T001 + T002 + T003 → Foundation ready
2. T004 + T005 → One-click sequel works (MVP!)
3. T006-T009 → Customization form with adjustable settings
4. T010-T013 → Sequel chain navigation in gallery
5. T014-T015 → Tests confirm everything

---

## Notes

- The `continue_story` route follows the same pattern as `start_story`: build content_guidelines, build image_style, call generate_scene, create StorySession, redirect
- `save_story()` fix (T002) is a standalone bug fix that benefits all features — several Story fields were silently dropped
- P2 transforms the P1 POST button into a GET→form→POST flow; the POST handler gains optional form params but defaults to inherited values
- P3's forward reference update happens inside `save_story()` so it's automatic for all future sequels
- Total: 15 tasks across 6 phases
