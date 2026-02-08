# Tasks: Mid-Story Length Control

**Input**: Design documents from `/specs/025-mid-story-length/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not explicitly requested in the spec. Tests will be added in the polish phase for completeness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup needed — this feature adds to existing files only. No new dependencies, no new models, no project structure changes.

(No tasks in this phase.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: CSS styles shared by both buttons, placed before user story phases since both US1 and US2 need them.

- [X] T001 Add `.story-length-controls` container and shared button styles (`.btn-keep-going`, `.btn-wrap-up`) to `static/css/style.css`

**Checkpoint**: Styles ready — button implementation can begin.

---

## Phase 3: User Story 1 - Extend Story with "Keep Going" (Priority: P1)

**Goal**: Users near the end of a story can click "Keep Going" to extend the target depth by 3, preventing the AI from wrapping up.

**Independent Test**: Start a story, advance to depth >= target_depth - 2, verify "Keep Going" button appears, click it, verify target_depth increased by 3, verify redirect back to same scene.

### Implementation for User Story 1

- [X] T002 [US1] Add POST `/story/keep-going/{scene_id}` route inside `create_tier_router()` in `app/routes.py` — get session, increase `story_session.story.target_depth` by 3, persist with `update_session()`, redirect back to scene
- [X] T003 [US1] Add "Keep Going" button to `templates/scene.html` inside the non-ending `{% else %}` block, wrapped in `{% if scene.depth >= story.target_depth - 2 %}`, as a POST form pointing to `{{ url_prefix }}/story/keep-going/{{ scene.scene_id }}`

**Checkpoint**: "Keep Going" button visible and functional when story approaches target depth.

---

## Phase 4: User Story 2 - End Story Early with "Wrap It Up" (Priority: P2)

**Goal**: Users can click "Wrap It Up" after at least 2 scenes to reduce target_depth so the AI concludes within 1-2 more scenes.

**Independent Test**: Start a long story, advance past depth 2, verify "Wrap It Up" button appears, click it, verify target_depth set to current_depth + 2 (or current_depth + 1 if boundary), verify redirect.

### Implementation for User Story 2

- [X] T004 [US2] Add POST `/story/wrap-up/{scene_id}` route inside `create_tier_router()` in `app/routes.py` — get session, compute new target as `scene.depth + 2`, if new target <= scene.depth then set to `scene.depth + 1`, persist with `update_session()`, redirect back to scene
- [X] T005 [US2] Add "Wrap It Up" button to `templates/scene.html` inside the non-ending `{% else %}` block, wrapped in `{% if scene.depth >= 2 %}`, as a POST form pointing to `{{ url_prefix }}/story/wrap-up/{{ scene.scene_id }}`

**Checkpoint**: Both buttons visible and functional at appropriate depths.

---

## Phase 5: User Story 3 - Button Visibility Rules (Priority: P3)

**Goal**: Buttons appear only when contextually appropriate — correct depth thresholds, hidden on endings, hidden in gallery reader.

**Independent Test**: Navigate through a story at various depths verifying button visibility: depth 0 (neither), depth 2 with high target (wrap only), depth near target (both), ending (neither), gallery (neither).

### Implementation for User Story 3

- [X] T006 [US3] Verify gallery reader exclusion — confirm `templates/reader.html` does NOT include length control buttons (no changes needed if reader.html is a separate template)
- [X] T007 [US3] Wrap both buttons in a single `<div class="story-length-controls">` container in `templates/scene.html` with proper conditional logic ensuring the container only renders when at least one button would be visible

**Checkpoint**: All visibility rules correct across all contexts.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation across all user stories.

- [X] T008 Create `tests/test_mid_story_length.py` with tests covering: keep-going route increases target_depth by 3, wrap-up route sets target_depth correctly, wrap-up boundary case (depth + 2 <= depth), button visibility in scene HTML at various depths, buttons absent from gallery reader, redirect behavior for both routes, no-session redirect
- [X] T009 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — CSS can start immediately
- **User Story 1 (Phase 3)**: Depends on T001 (CSS)
- **User Story 2 (Phase 4)**: Depends on T001 (CSS); independent of US1
- **User Story 3 (Phase 5)**: Depends on T003 and T005 (both buttons must exist to organize them)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T002 and T004 (routes) can be implemented in parallel since they are separate route handlers in the same file but non-overlapping code
- T003 and T005 (template) should be done sequentially since they modify the same section of `scene.html`

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 (CSS)
2. Complete T002 + T003 (Keep Going route + button)
3. **STOP and VALIDATE**: Test Keep Going independently
4. This alone provides the most impactful feature — extending stories

### Incremental Delivery

1. T001 → Foundation ready
2. T002 + T003 → Keep Going works (MVP!)
3. T004 + T005 → Wrap It Up works
4. T006 + T007 → Visibility polish
5. T008 + T009 → Tests confirm everything

---

## Notes

- No new models or services needed — this feature operates entirely on the existing `Story.target_depth` field
- Both routes follow the same pattern as existing routes (Go Back, Make Choice): POST → session update → redirect
- Gallery exclusion is free because gallery uses `reader.html`, not `scene.html`
- Total: 9 tasks across 6 phases
