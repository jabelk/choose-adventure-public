# Tasks: Refresh Templates Button

**Input**: Design documents from `/specs/034-refresh-templates/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed — existing project structure is sufficient.

(No tasks — project structure already exists)

---

## Phase 2: User Story 2 - Expanded Template Pool (Priority: P2)

**Goal**: Expand each tier's template pool to at least 12 templates so shuffling reveals genuinely new options.

**Independent Test**: Kids tier has >= 12 templates and NSFW tier has >= 12 templates in `app/tiers.py`.

**Note**: US2 is done first because US1 (the shuffle button) needs a larger pool to be meaningful.

### Implementation for User Story 2

- [X] T001 [US2] Add 6 new kids story templates to the kids tier `templates` list in app/tiers.py (Baking Adventure, Dinosaur Park, Rainbow Bridge, Pirate Penguins, Magic Garden, Robot Best Friend)
- [X] T002 [US2] Add 2 new NSFW story templates to the NSFW tier `templates` list in app/tiers.py (Wine Bar Encounter, Beach House Weekend)

**Checkpoint**: Both tiers have >= 12 templates in their pools.

---

## Phase 3: User Story 1 - Shuffle Visible Templates (Priority: P1) 🎯 MVP

**Goal**: Add a shuffle button that swaps visible template cards to a different random subset of 6 from the full pool, entirely client-side.

**Independent Test**: Load the home page on either tier, see 6 template cards, click "Shuffle" button, see a different set of 6 cards appear instantly.

### Implementation for User Story 1

- [X] T003 [P] [US1] Add `.template-hidden` and `.btn-shuffle` CSS styles in static/css/style.css
- [X] T004 [P] [US1] Create static/js/template-shuffle.js with `initTemplateShuffle(displayCount)` function: on load hide all cards then show random 6, shuffle button re-randomizes visible set using Fisher-Yates
- [X] T005 [US1] Update templates/home.html: add `data-template-index` attribute to each template card, add shuffle button next to template section label, include template-shuffle.js script and call `initTemplateShuffle(6)`

**Checkpoint**: Shuffle button works on both tiers, showing 6 random templates from the full pool.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T006 Write tests in tests/test_template_shuffle.py: verify shuffle button present on both tiers, verify all templates rendered in HTML (>= 12 per tier), verify template-shuffle.js included, verify existing template selection still works
- [X] T007 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **US2 (Phase 2)**: No dependencies — adds data to `app/tiers.py`
- **US1 (Phase 3)**: Depends on US2 (needs the larger pool to be meaningful, though technically works with any pool size)
- **Polish (Phase 4)**: Depends on US1 + US2

### Within User Story 1

- T003 and T004 can run in parallel (different files)
- T005 depends on T003 and T004 (references both CSS and JS)

### Parallel Opportunities

```bash
# T003 and T004 can run in parallel:
Task: "Add shuffle button CSS in static/css/style.css"
Task: "Create template-shuffle.js in static/js/"
```

---

## Implementation Strategy

### MVP First

1. T001 + T002: Expand template pools
2. T003 + T004 (parallel): CSS + JS for shuffle
3. T005: Wire up in home.html
4. T006 + T007: Tests and validation
