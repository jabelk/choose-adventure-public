# Tasks: "Surprise Me" Button

**Input**: Design documents from `/specs/024-surprise-me-button/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Tests included for core endpoint behavior and tier isolation.

**Organization**: Tasks grouped by user story. This is a small feature — most tasks are sequential since they touch overlapping files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed — this feature builds entirely on existing infrastructure.

(No tasks — existing project structure, dependencies, and routing framework are already in place.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extract shared story-start logic so both `start_story()` and `surprise_me()` can use it without duplication.

- [X] T001 Extract the core story-start logic from the `start_story()` route handler into a reusable helper function `_do_start_story()` inside `create_tier_router()` in app/routes.py. The helper should accept all the same parameters as the form handler (prompt, length, model, image_model, art_style, flavor options, kinks, etc.) and return the same Response. Update `start_story()` to call this helper.

**Checkpoint**: Existing story start behavior unchanged — refactor only, no new features.

---

## Phase 3: User Story 1 - One-Tap Random Story Start (Priority: P1)

**Goal**: Clicking "Surprise Me" starts a story with randomly selected parameters — zero user input.

**Independent Test**: POST to `/{tier}/story/surprise` returns a redirect to the story page with a new story created using random parameters.

### Implementation for User Story 1

- [X] T002 [US1] Add the `POST /story/surprise` route inside `create_tier_router()` in app/routes.py. The route should: (1) randomly select a template from `tier_config.templates` using `random.choice`, or pick from a small hardcoded fallback prompts list if no templates exist; (2) randomly select one value from each story flavor option group via `get_option_groups()` and `choices_for_tier(tier_config.name)`; (3) randomly select an art style from `get_art_styles(tier_config.name)`; (4) randomly select a length from `["short", "medium", "long"]`; (5) pick the first available AI model and image model; (6) call `_do_start_story()` with the assembled parameters.
- [X] T003 [US1] Add the "Surprise Me" button to the home page in templates/home.html. Place a `<form action="{{ url_prefix }}/story/surprise" method="post">` with a single submit button near the bottom of the form, next to the existing "Start Adventure" button. The button should be disabled when `available_models` is empty (same as Start Adventure).

**Checkpoint**: "Surprise Me" button visible on both tiers, clicking it starts a random story.

---

## Phase 4: User Story 2 - Tier-Appropriate Random Selection (Priority: P2)

**Goal**: Random selections are always scoped to the current tier — kids never gets NSFW content.

**Independent Test**: POST to `/kids/story/surprise` never includes kink parameters; POST to `/nsfw/story/surprise` may include 0-2 random kinks.

### Implementation for User Story 2

- [X] T004 [US2] Add NSFW-specific kink randomization to the surprise route in app/routes.py. For NSFW tier only: randomly select 0-2 kink keys from `KINK_TOGGLES.keys()` using `random.sample` with a random count via `random.randint(0, 2)`. Pass selected kinks to `_do_start_story()`. For kids tier: always pass empty kinks list.
- [X] T005 [US2] Add fallback prompt lists (one for kids, one for NSFW) as module-level constants in app/routes.py. Kids fallbacks should be whimsical child-safe prompts (e.g., "A friendly dragon learns to bake cupcakes"). NSFW fallbacks should be adult-themed prompts. These are only used when `tier_config.templates` is empty.

**Checkpoint**: Kids tier surprise always kid-safe, NSFW tier includes random kinks.

---

## Phase 5: User Story 3 - Prominent Button Placement (Priority: P3)

**Goal**: The "Surprise Me" button is visually prominent, fun, and easy to find on both tiers.

**Independent Test**: Load home page and verify button is visible, styled distinctly, and positioned prominently.

### Implementation for User Story 3

- [X] T006 [P] [US3] Add CSS styles for the surprise-me button in static/css/style.css. Style the `.btn-surprise` class with a distinct gradient or accent color, slight animation on hover (e.g., scale or shimmer), and ensure it's visually differentiated from `.btn-primary`. Include responsive styles for mobile.
- [X] T007 [US3] Update the button layout in templates/home.html to place the "Surprise Me" button and "Start Adventure" button side by side in a `.btn-row` flex container at the bottom of the form. Ensure proper spacing and alignment on both desktop and mobile.

**Checkpoint**: Button is prominent, fun-looking, and responsive.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T008 [P] Create tests in tests/test_surprise_me.py: (1) TestSurpriseKids: POST /kids/story/surprise returns 303 redirect; (2) TestSurpriseNSFW: POST /nsfw/story/surprise returns 303 redirect; (3) TestSurpriseKidsNoKinks: verify kids surprise response does not include kink parameters; (4) TestSurpriseButtonVisible: GET /kids/ and /nsfw/ both contain "Surprise Me" in response text.
- [X] T009 Run full test suite with `venv/bin/python -m pytest tests/ -v` to verify no regressions across all existing tests.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A — no setup needed
- **Foundational (Phase 2)**: T001 must complete before T002 (surprise route needs the helper)
- **US1 (Phase 3)**: T002 depends on T001; T003 can run in parallel with T002
- **US2 (Phase 4)**: T004 depends on T002; T005 can run in parallel
- **US3 (Phase 5)**: T006 and T007 can start after T003
- **Polish (Phase 6)**: T008 after all implementation; T009 after T008

### User Story Dependencies

- **User Story 1 (P1)**: Depends on T001 (foundational refactor). No other story dependencies.
- **User Story 2 (P2)**: Extends the surprise route from US1 (T002). Independent of US3.
- **User Story 3 (P3)**: Updates the template from US1 (T003). Independent of US2.

### Parallel Opportunities

- T003 (template button) and T002 (route) can be developed in parallel
- T005 (fallback prompts) can run in parallel with T004 (kink randomization)
- T006 (CSS) can run in parallel with T007 (template layout update)
- T008 (tests) runs in parallel with nothing — it validates everything

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001: Extract helper function (foundational)
2. Complete T002 + T003: Route + button (US1)
3. **STOP and VALIDATE**: Click "Surprise Me" on both tiers, verify stories start

### Incremental Delivery

1. T001 → Foundation ready
2. T002 + T003 → MVP: button works on both tiers
3. T004 + T005 → Tier isolation: kinks on NSFW, safe fallbacks
4. T006 + T007 → Polish: button looks great
5. T008 + T009 → Confidence: all tests pass

---

## Notes

- This is a small feature — 9 tasks total
- The refactor in T001 is the most important step to avoid code duplication
- Kids tier content isolation is enforced by the existing `choices_for_tier()` and `get_art_styles()` functions — no extra filtering needed
- Fallback prompts (T005) are a safety net for the edge case where a tier has no templates
