# Tasks: Bedtime Story Mode

**Input**: Design documents from `/specs/026-bedtime-story-mode/`
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

**Purpose**: Model field and content guidelines constants that all user stories depend on.

- [X] T001 [P] Add `bedtime_mode: bool = False` field to `Story` model and `SavedStory` model in `app/models.py`
- [X] T002 [P] Add `BEDTIME_CONTENT_GUIDELINES` and `BEDTIME_IMAGE_STYLE` constants to `app/tiers.py` — bedtime guidelines instruct AI to be gentle, soothing, no tension, always end with character settling in for sleep; bedtime image style emphasizes soft warm nighttime cozy moonlit imagery

**Checkpoint**: Model field and constants ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Bedtime Story Toggle (Priority: P1)

**Goal**: Parents can check a "Bedtime Mode" toggle on the kids home page to start calming, short bedtime stories with bedtime-specific AI guidelines and image style.

**Independent Test**: Enable bedtime toggle on kids home, start a story, verify target_depth is 3, verify bedtime content guidelines are applied, verify bedtime_mode flag is persisted on story.

### Implementation for User Story 1

- [X] T003 [US1] Add bedtime mode checkbox to `templates/home.html` — visible only when `tier.name == 'kids'`, placed before the upload section as a toggle row with label "Calming bedtime story with warm night theme"
- [X] T004 [US1] Add `bedtime_mode: str = Form("")` parameter to `start_story` route in `app/routes.py` — when `bedtime_mode == "on"` and tier is kids: append `BEDTIME_CONTENT_GUIDELINES` to content_guidelines, override image_style with `BEDTIME_IMAGE_STYLE`, force `story_length = StoryLength.SHORT` and `target_depth = 3`, set `story.bedtime_mode = True`
- [X] T005 [US1] Update surprise route in `app/routes.py` to accept bedtime mode — add hidden `bedtime_mode` input to the surprise form in `templates/home.html`, add JS in home.html scripts block to sync bedtime checkbox state to the hidden input; in the surprise route, read `bedtime_mode` from form and apply same overrides as start_story
- [X] T006 [US1] Update `make_choice` route in `app/routes.py` to rebuild bedtime guidelines — after rebuilding content_guidelines from tier, check `story_session.story.bedtime_mode` and if True, append `BEDTIME_CONTENT_GUIDELINES` and override image_style with `BEDTIME_IMAGE_STYLE`
- [X] T007 [US1] Update `custom_choice` route in `app/routes.py` with same bedtime guidelines rebuild as T006

**Checkpoint**: Bedtime stories generated with calming guidelines, short length, and bedtime image style. Core feature works end-to-end.

---

## Phase 4: User Story 2 - Bedtime Night Theme (Priority: P2)

**Goal**: Scene pages for bedtime stories render with a warm, dimmed night color scheme.

**Independent Test**: Start a bedtime story, navigate to a scene, verify the page has the bedtime theme class and warm dark colors instead of the bright kids theme.

### Implementation for User Story 2

- [X] T008 [P] [US2] Add `.theme-bedtime` CSS custom properties to `static/css/style.css` — deep indigo/navy background, soft amber accents, muted warm text, reduced contrast for low-light viewing; also add bedtime-specific styles for `.bedtime-mode-selector` toggle on home page
- [X] T009 [US2] Pass `bedtime_mode` flag to scene template context in `view_scene` route in `app/routes.py` — add `"bedtime_mode": story_session.story.bedtime_mode` to the template context dict
- [X] T010 [US2] Add bedtime theme class to scene page in `templates/scene.html` — add `{% if bedtime_mode %}theme-bedtime{% endif %}` to body class via an inline style block or script that adds the class to document.body when bedtime_mode is true

**Checkpoint**: Bedtime scenes render with warm night theme. Non-bedtime scenes unaffected.

---

## Phase 5: User Story 3 - Wind-Down Timer (Priority: P3)

**Goal**: A subtle elapsed timer appears on bedtime scene pages and gently pulses after 5 minutes.

**Independent Test**: Start a bedtime story, verify timer appears and counts up, wait (or mock) past 5 minutes and verify visual change. Non-bedtime stories have no timer.

### Implementation for User Story 3

- [X] T011 [P] [US3] Create `static/js/bedtime-timer.js` — initialize timer using `sessionStorage` key `bedtime_start_time`, display elapsed mm:ss, add `.wind-down` class to timer element after 300 seconds (5 minutes), export `initBedtimeTimer()` function
- [X] T012 [P] [US3] Add wind-down timer CSS styles to `static/css/style.css` — `.bedtime-timer` positioning (small overlay in scene header area), `.wind-down` gentle pulse animation using `@keyframes`, muted amber color scheme matching bedtime theme
- [X] T013 [US3] Add bedtime timer markup and script to `templates/scene.html` — conditionally render timer div and include `bedtime-timer.js` script when `bedtime_mode` is true, call `initBedtimeTimer()` on page load

**Checkpoint**: Timer visible on bedtime scenes, pulses at 5 minutes, absent from non-bedtime scenes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation across all user stories.

- [X] T014 Create `tests/test_bedtime_mode.py` with tests covering: toggle visible on kids home only, not visible on NSFW home, bedtime story starts with target_depth 3, bedtime_mode flag persisted on story, bedtime content guidelines applied, surprise me respects bedtime mode, bedtime theme class on scene page, no bedtime theme on non-bedtime scene, timer markup present on bedtime scene, timer absent on non-bedtime scene, keep-going still works during bedtime
- [X] T015 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — model + constants can start immediately
- **User Story 1 (Phase 3)**: Depends on T001 + T002 (model field and constants)
- **User Story 2 (Phase 4)**: Depends on US1 complete (needs bedtime_mode on story to test theme)
- **User Story 3 (Phase 5)**: Depends on US2 complete (timer renders within bedtime theme)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T001 and T002 (model + constants) can run in parallel (different files)
- T008 (CSS) can run in parallel with T009 and T010 (different files)
- T011 and T012 (JS + CSS for timer) can run in parallel (different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 + T002 (model + constants)
2. Complete T003-T007 (toggle, routes, surprise, make_choice, custom_choice)
3. **STOP and VALIDATE**: Bedtime stories work with calming guidelines and short length
4. This alone delivers the core value — calming bedtime stories

### Incremental Delivery

1. T001 + T002 → Foundation ready
2. T003-T007 → Bedtime toggle works (MVP!)
3. T008-T010 → Night theme on scene pages
4. T011-T013 → Wind-down timer
5. T014-T015 → Tests confirm everything

---

## Notes

- Bedtime mode follows the exact same pattern as `video_mode`: boolean on Story, checkbox on form, behavior applied in routes
- Content guidelines are additive (appended to kids guidelines, not replacing them) to preserve safety rules
- Gallery reader exclusion is free — `reader.html` is separate from `scene.html`
- Total: 15 tasks across 6 phases
