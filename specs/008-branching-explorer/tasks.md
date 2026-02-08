# Tasks: Story Branching Explorer

**Input**: Design documents from `/specs/008-branching-explorer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Vendor D3.js and create the tree building helper module

- [x] T001 Download and vendor D3.js v7 minified to static/js/d3.v7.min.js
- [x] T002 Add D3.js script tag to templates/base.html (before app.js, in scripts block)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core tree logic and model method that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `navigate_to(scene_id)` method to StorySession in app/models.py — rebuilds path_history by walking parent_scene_id chain from root to target scene
- [x] T004 Create app/tree.py with `build_tree(scenes, current_scene_id, path_history)` function — converts flat scenes dict to nested tree structure for D3.js (returns dict with id, label, is_ending, is_current, on_path, choice_text, children)

**Checkpoint**: Foundation ready — tree building and scene navigation available for all user stories

---

## Phase 3: User Story 1 — Explore Alternate Branches (Priority: P1) 🎯 MVP

**Goal**: Users can go back to a previous choice point, pick a different option, and generate a new branch while preserving the original branch.

**Independent Test**: Start a story, make 2-3 choices, go back, pick different choice. Verify new branch generates, old branch preserved, explored choices visually marked. (Quickstart steps 2-3)

### Implementation for User Story 1

- [x] T005 [US1] Add explored choice indicators to templates/scene.html — pass `explored_choices` set from route, add CSS class `explored` to choice buttons where `choice.choice_id in explored_choices`, show checkmark or "explored" label
- [x] T006 [US1] Add explored choice CSS styles to static/css/style.css — `.choice-btn.explored` styling with subtle indicator (checkmark icon or text label), works with both kids and adult themes
- [x] T007 [US1] Modify `view_scene` route in app/routes.py to compute and pass `explored_choices` (set of choice_ids where `choice.next_scene_id is not None`) to the scene template

**Checkpoint**: Branching already works via existing make_choice logic. Users can now see which choices are explored and navigate between branches via go-back. All branches are preserved in the scenes dict.

---

## Phase 4: User Story 2 — Tree Map During Active Play (Priority: P2)

**Goal**: Users can toggle a visual tree map showing all explored branches, their current position, and click any node to jump to that scene.

**Independent Test**: With a branched story, click "Story Map" button, verify tree renders with current node highlighted, click a different node to navigate. (Quickstart steps 4-5)

### Implementation for User Story 2

- [x] T008 [P] [US2] Create static/js/tree-map.js with `renderTreeMap(containerId, treeData, currentId, urlPrefix, mode)` function — uses D3 d3.tree() layout, d3.linkHorizontal() edges, SVG rendering, click handlers, current node highlighting, path styling, responsive scrollable container
- [x] T009 [P] [US2] Add tree map CSS styles to static/css/style.css — tree map container, SVG node styles, current node highlight, on-path styling, toggle button, collapsed/expanded states, theme-aware colors
- [x] T010 [US2] Add `GET /{tier}/story/tree` JSON route to app/routes.py — calls build_tree() from app/tree.py, returns JSON with tree and current_id
- [x] T011 [US2] Add `POST /{tier}/story/navigate/{scene_id}` route to app/routes.py — looks up scene_id in session scenes, calls navigate_to(), redirects to scene page
- [x] T012 [US2] Modify `view_scene` route in app/routes.py to pass `has_branches` (bool: story has more than one leaf) and `tree_data` (JSON from build_tree) to the scene template
- [x] T013 [US2] Add "Story Map" toggle button and collapsible tree map container to templates/scene.html — toggle button in nav area (visible when has_branches or 2+ scenes), tree map container with D3 rendering, include tree-map.js script, pass tree_data as JSON to renderTreeMap in "active" mode

**Checkpoint**: Active play tree map fully functional — users can visualize and navigate the story tree during play

---

## Phase 5: User Story 3 — Gallery Reader with Tree Map (Priority: P3)

**Goal**: Gallery reader uses scene-ID-based navigation and shows a tree map for browsing branched completed stories.

**Independent Test**: Complete a branched story, view in gallery reader. Verify tree map shows all branches, click nodes to navigate between scenes. (Quickstart steps 6-7)

### Implementation for User Story 3

- [x] T014 [US3] Modify `gallery_story` route in app/routes.py to redirect to root scene ID instead of index 0 — find root scene (parent_scene_id is None), redirect to `/{tier}/gallery/{story_id}/{root_scene_id}`
- [x] T015 [US3] Change `gallery_reader` route in app/routes.py from `/{tier}/gallery/{story_id}/{scene_index:int}` to `/{tier}/gallery/{story_id}/{scene_id:str}` — look up scene by ID in saved.scenes dict, build tree data, pass to template
- [x] T016 [US3] Update templates/reader.html to replace linear prev/next navigation with tree map — add always-visible tree map container, render with tree-map.js in "gallery" mode, change navigation links from index-based to scene-ID-based URLs

**Checkpoint**: Gallery reader supports branched stories with full tree navigation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Backward compatibility, resume support, and end-to-end validation

- [x] T017 Verify backward compatibility with pre-existing linear stories in gallery — test that stories saved before branching display as single-path trees with no errors (FR-011)
- [x] T018 Verify progress save/resume preserves all branches — start branched story, close browser, resume and confirm all branches appear in tree map (FR-010)
- [x] T019 Run full quickstart.md validation (all 10 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T003, T004)
- **User Story 2 (Phase 4)**: Depends on Foundational phase (T003, T004) and US1 (T007 for explored_choices pattern)
- **User Story 3 (Phase 5)**: Depends on Foundational phase and US2 (T008 tree-map.js needed)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational, but T012 extends the view_scene route from T007 — implement after US1
- **User Story 3 (P3)**: Depends on tree-map.js from US2 (T008) — implement after US2

### Within Each User Story

- Route changes before template changes (templates depend on context variables from routes)
- CSS can be done in parallel with route/template work

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T003 and T004 can run in parallel (different files: models.py vs tree.py)
- T008 and T009 can run in parallel (different files: tree-map.js vs style.css)
- T014 and T016 can be started in parallel once T015 route change is defined

---

## Parallel Example: User Story 2

```bash
# Launch parallel tasks (different files):
Task: "Create tree-map.js component in static/js/tree-map.js"  # T008
Task: "Add tree map CSS styles to static/css/style.css"         # T009

# Then sequential (same files or dependencies):
Task: "Add tree JSON route to app/routes.py"                    # T010
Task: "Add navigate route to app/routes.py"                     # T011
Task: "Modify view_scene route in app/routes.py"                # T012
Task: "Add tree map UI to templates/scene.html"                 # T013
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (vendor D3.js)
2. Complete Phase 2: Foundational (navigate_to + build_tree)
3. Complete Phase 3: User Story 1 (explored indicators)
4. **STOP and VALIDATE**: Test branching and explored indicators
5. Branching is functional even without the tree map visualization

### Incremental Delivery

1. Setup + Foundational → Tree logic ready
2. Add User Story 1 → Explored choice indicators → Branching works visually
3. Add User Story 2 → Tree map during play → Full active-play experience
4. Add User Story 3 → Gallery tree map → Complete explorable archive
5. Each story adds visual/navigation value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Branching behavior already works via existing make_choice route (checks next_scene_id) — US1 focuses on visual indicators
- The existing GalleryService.save_story() already saves ALL scenes (not just path_history) — FR-007 is already satisfied
- D3.js is vendored as a single file (~280KB), no npm or build tools
- Commit after each phase completion
- Stop at any checkpoint to validate independently
