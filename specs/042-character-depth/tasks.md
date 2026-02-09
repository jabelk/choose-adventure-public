# Tasks: Enhanced Character Creation & Relationship Depth

**Input**: Design documents from `/specs/042-character-depth/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define attribute data structures and extend character model — shared by all user stories

- [x] T001 Define `CHARACTER_ATTRIBUTES` dict in `app/story_options.py` with all 12 attribute categories (hair_color, hair_length, eye_color, skin_tone, body_type, bust_size, height, temperament, energy, archetype, clothing_style, aesthetic_vibe), each with label, options list, tier_restrict, and group fields per `data-model.md`
- [x] T002 Define `RELATIONSHIP_STAGES` list and `RELATIONSHIP_PROMPTS` dict in `app/story_options.py` per `data-model.md`
- [x] T003 Add `attributes: dict[str, str]`, `relationship_stage: str`, `story_count: int`, `last_story_date: Optional[str]` fields to `RosterCharacter` model in `app/models.py` with backward-compatible defaults per `data-model.md`
- [x] T004 Add `compose_description(attributes: dict[str, str]) -> str` function to `app/services/character.py` that takes attribute dict and produces natural-language description string per plan.md D3
- [x] T005 Add `get_attributes_for_tier(tier_name: str) -> dict` function to `app/story_options.py` that filters `CHARACTER_ATTRIBUTES` by `tier_restrict`, returning only categories available for the given tier

**Checkpoint**: Model and data structures ready — user story implementation can begin

---

## Phase 2: User Story 1 — Structured Character Creator (Priority: P1) MVP

**Goal**: Replace free-text-only character creation with mobile-friendly pill selectors for physical attributes, personality, and style on the character roster page

**Independent Test**: Navigate to `/nsfw/characters`, tap "Create Character", fill in name, tap through attribute selectors (hair: blonde, body: athletic, personality: playful), save. Verify character appears with composed description. Edit character and verify pills are pre-selected.

### Implementation

- [x] T006 [US1] Add pill selector CSS styles to `static/css/style.css` — extend existing `.kink-pill` pattern with `.attr-pill` and `.attr-group` classes, 44px minimum tap targets, responsive wrapping, selected state highlighting
- [x] T007 [US1] Create `static/js/character-attributes.js` — `initAttributeSelectors(containerId, attributesConfig, preselected)` function that renders grouped pill selectors (radio-style single-select per category), composes description preview on selection change, and populates hidden `attr_*` form fields
- [x] T008 [US1] Add `GET /{tier}/characters/api/attributes` endpoint in `app/routes.py` that returns tier-filtered attribute options as JSON per `contracts/api.md`
- [x] T009 [US1] Modify character create/update form in `templates/characters.html` — add attribute selector container div above the description textarea, include `character-attributes.js` script, pass `CHARACTER_ATTRIBUTES` filtered by tier as template context
- [x] T010 [US1] Modify `POST /{tier}/characters/create` route in `app/routes.py` to accept `attr_*` form fields, build attributes dict, call `compose_description()` if no manual description provided, save both `attributes` and composed `description` to character
- [x] T011 [US1] Modify `POST /{tier}/characters/{id}/update` route in `app/routes.py` to accept `attr_*` form fields, rebuild attributes dict, re-compose description, update character
- [x] T012 [US1] Modify character edit form rendering in `app/routes.py` `GET /{tier}/characters` to pass existing `attributes` dict as JSON for pre-populating pill selectors via `initAttributeSelectors()` preselected parameter
- [x] T013 [US1] Add free-text override field to `templates/characters.html` below the composed description preview — text appended after composed description on save per spec FR-005
- [x] T014 [US1] Verify tier isolation: navigate to `/kids/characters` and confirm only age-appropriate attributes appear (hair_color, hair_length, eye_color, skin_tone, height — no body_type, bust_size, archetype)

**Checkpoint**: Characters can be created/edited with structured attributes on all tiers. Composed descriptions flow into AI prompts via existing `description` field.

---

## Phase 3: User Story 2 — Quick Character Builder on Story Start (Priority: P1)

**Goal**: Add the same structured attribute selectors inline on the story/agent start form so users can define a one-off character without visiting the roster page

**Independent Test**: Navigate to `/nsfw/`, expand Character section, tap attribute pills to define a character, start a story. Verify character attributes appear in AI narration.

### Implementation

- [x] T015 [US2] Add inline attribute selector section to `templates/home.html` in the character area — reuse `character-attributes.js` with `initAttributeSelectors()`, include `inline_attr_*` hidden fields for form submission
- [x] T016 [US2] Modify `POST /{tier}/start` route in `app/routes.py` to read `inline_attr_*` form fields, compose description, inject into `content_guidelines` and `image_style` — only when no roster character is selected (roster takes priority per spec)
- [x] T017 [US2] Add client-side logic in `templates/home.html` or `character-attributes.js` to disable/gray-out inline attribute pills when a roster character is selected in the picker, and re-enable when deselected
- [x] T018 [US2] Replicate inline attribute support for agent mode start in `app/routes.py` agent mode start route (same `inline_attr_*` field handling) — N/A: agent mode uses roster characters only, no manual character fields

**Checkpoint**: Users can define one-off characters via pill selectors on the story start form. Roster character selection takes priority over inline attributes.

---

## Phase 4: User Story 3 — Relationship Tracker (Priority: P2)

**Goal**: Track relationship stage per roster character, auto-advance on story completion, inject relationship context into AI prompts

**Independent Test**: Create a character, complete 2-3 stories with them. Verify relationship stage advances on character page. Start a new story and verify AI references prior history.

### Implementation

- [x] T019 [US3] Add `advance_relationship(tier: str, character_id: str)` method to `app/services/character.py` — increments `story_count`, advances `relationship_stage` one level (if not at max), updates `last_story_date` to current ISO date, saves character JSON
- [x] T020 [US3] Add relationship advancement calls in `app/routes.py` at all 5 `gallery_service.save_story()` call sites — after save_story, call `_advance_relationships_for_story()` helper, only on NSFW tier
- [x] T021 [US3] Modify character context building block in `app/routes.py` (4 locations) to include relationship context — check `relationship_stage` and `story_count`, format prompt from `RELATIONSHIP_PROMPTS` dict, append to character block
- [x] T022 [US3] Add relationship display section to `templates/characters.html` on the character edit page — show current stage as highlighted pill selector (6 stages), story count, last story date. Stage pills are tappable for manual override.
- [x] T023 [US3] Add `POST /{tier}/characters/{id}/relationship` route in `app/routes.py` for manual relationship stage adjustment — validate stage value against `RELATIONSHIP_STAGES`, update character, redirect to edit page
- [x] T024 [US3] Modify `static/js/character-picker.js` to show relationship stage badge on picker cards — emoji badge on characters with stage beyond "strangers"

**Checkpoint**: Relationship stage tracks across stories, auto-advances, is manually adjustable, and injects context into AI prompts.

---

## Phase 5: User Story 4 — Expanded Kink Toggles (Priority: P3)

**Goal**: Add 7+ new kink/theme toggles to the NSFW story start form

**Independent Test**: Navigate to `/nsfw/`, verify 11+ kink toggles appear as pills. Select one or more, start a story, verify AI incorporates themes.

### Implementation

- [x] T025 [P] [US4] Add 7 new entries to `KINK_TOGGLES` dict in `app/story_options.py` — role_reversal, power_dynamics, clothing_destruction, size_difference, dominance_submission, hypnosis, bimboification — each with display_name, story_prompt, and image_prompt_addition per spec
- [x] T026 [US4] Verify kink toggles render correctly in `templates/home.html` — existing template loop handles new entries automatically, but verify layout wraps properly with 11+ pills on mobile

**Checkpoint**: 11 kink toggles available on NSFW story start form. No code changes needed beyond data — existing infrastructure handles rendering and prompt injection.

---

## Phase 6: Polish & Verification

**Purpose**: Cross-cutting validation and cleanup

- [x] T027 Run existing test suite `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — all tests pass, no regressions
- [x] T028 Test backward compatibility — load an existing character JSON file (pre-attributes), verify it loads without errors with default empty attributes and "strangers" relationship stage
- [x] T029 Mobile usability check — verify all pill selectors have 44px+ tap targets, no horizontal scrolling, usable without keyboard on mobile viewport
- [x] T030 Run quickstart.md verification steps end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (US1)**: Depends on Phase 1 completion
- **Phase 3 (US2)**: Depends on Phase 2 (reuses `character-attributes.js` and pill CSS from US1)
- **Phase 4 (US3)**: Depends on Phase 1 only (model fields). Can run in parallel with Phase 2/3.
- **Phase 5 (US4)**: No dependencies on other phases — data-only addition. Can run anytime after Phase 1.
- **Phase 6 (Polish)**: Depends on all prior phases

### User Story Dependencies

- **US1 (Structured Creator)**: Depends on Phase 1 setup only. MVP candidate.
- **US2 (Inline Builder)**: Depends on US1 (reuses JS component and CSS). Must follow US1.
- **US3 (Relationship Tracker)**: Depends on Phase 1 model fields only. Independent of US1/US2.
- **US4 (Expanded Kinks)**: Fully independent. Can run anytime.

### Parallel Opportunities

- T001 and T002 can run in parallel (different data structures, same file but different sections)
- T006 and T007 can run in parallel (CSS vs JS, different files)
- T025 (US4) can run in parallel with any Phase 2/3/4 tasks (different file section, no dependencies)
- Phase 4 (US3) can run in parallel with Phase 2 (US1) after Phase 1 completes

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: User Story 1 (T006-T014)
3. **STOP and VALIDATE**: Create a character with pill selectors, verify composed description, edit and verify pre-selection
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Setup complete
2. Phase 2 (US1) → Structured character creator on roster page → Deploy
3. Phase 3 (US2) → Inline builder on story start → Deploy
4. Phase 4 (US3) → Relationship tracking → Deploy
5. Phase 5 (US4) → More kink toggles → Deploy
6. Phase 6 → Final verification

---

## Notes

- No new pip dependencies required
- All new fields on RosterCharacter have defaults — zero migration needed
- Kink toggles (US4) are the quickest win — pure data addition, no code changes
- Relationship tracker (US3) touches routes.py in 6+ places — be methodical
- NSFW-ONLY markers needed around bust_size, body_type, archetype attribute definitions for public export filtering
