# Tasks: Favorite Characters Across Stories (Kids)

**Input**: Design documents from `/specs/033-kids-favorite-characters/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Included — verify kids tier access, character creation, picker visibility, tier isolation, and NSFW regression.

**Organization**: Tasks grouped by user story. This feature is primarily about removing NSFW-only gates from existing infrastructure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (No changes needed)

**Purpose**: No project initialization required — all infrastructure already exists.

> Skipped — the character roster service, models, storage, JS module, and templates are all already implemented.

---

## Phase 2: Foundational (Remove NSFW-Only Route Guards)

**Purpose**: Remove route-level NSFW gates so character endpoints work on all tiers

**⚠️ CRITICAL**: Must complete before any user story testing

- [X] T001 Remove `if tier_config.name != "nsfw": return 404` guards from all 6 character route handlers (characters_page, create_character_route, update_character_route, delete_character_route, serve_roster_photo, list_characters_api) in app/routes.py
- [X] T002 Remove `if tier_config.name == "nsfw":` gate on roster character loading in the home page handler so roster characters load for all tiers in app/routes.py

**Checkpoint**: Character routes now respond on both kids and NSFW tiers

---

## Phase 3: User Story 1 - Kids Can Save Favorite Characters (Priority: P1) 🎯 MVP

**Goal**: Kids tier users can access the character management page and create/view characters

**Independent Test**: Navigate to `/kids/characters`, create a character, verify it appears in the list

### Implementation for User Story 1

- [X] T003 [US1] Remove `{% if tier.name == 'nsfw' %}` gate on the "Characters" link in templates/home.html and make link text tier-aware ("My Characters" for kids, "Characters" for NSFW)
- [X] T004 [US1] Add tier-aware heading and placeholder text in templates/characters.html — "My Characters" heading and kid-friendly examples (e.g. "Mr. Snuggles") for kids tier, keep "Character Roster" and current placeholders for NSFW

**Checkpoint**: Kids tier home page shows "My Characters" link, character management page works

---

## Phase 4: User Story 2 - Pick Favorite Characters When Starting a Story (Priority: P2)

**Goal**: Kids tier story start form shows a character picker when saved characters exist

**Independent Test**: Create a character on kids tier, then go to story start form — character picker should appear with the saved character

### Implementation for User Story 2

- [X] T005 [US2] Remove `{% if tier.name == 'nsfw' %}` gate on the character picker section (details/summary block with picker + manual fields) in templates/home.html
- [X] T006 [US2] Remove `{% if tier.name == 'nsfw' and roster_characters %}` gate on character picker JS initialization in templates/home.html

**Checkpoint**: Kids tier story start form shows character picker when characters exist

---

## Phase 5: User Story 3 - Edit and Delete Favorite Characters (Priority: P3)

**Goal**: Kids tier users can edit and delete characters from the management page

**Independent Test**: Create a character on kids tier, edit its description, verify change persists. Delete it, verify it's gone.

### Implementation for User Story 3

> Edit and delete functionality is already implemented in the routes (T001 removed the guards) and the characters.html template already has edit/delete UI. No additional code changes needed.

- [X] T007 [US3] Verify edit and delete work on kids tier — manual verification step confirming routes and template already support this after T001 guard removal (no code changes needed)

**Checkpoint**: Kids tier character CRUD is fully functional

---

## Phase 6: User Story 4 - NSFW Tier Continues Working Unchanged (Priority: P4)

**Goal**: Verify NSFW character roster still works identically after changes

**Independent Test**: Navigate to NSFW character page, create/edit/delete a character, use character picker on story start — all should work as before

### Implementation for User Story 4

> No code changes — this is a regression verification phase. The automated tests (T008) cover this.

- [X] T008 [US4] Verify NSFW tier character roster is unchanged — confirmed by automated tests (no code changes needed)

**Checkpoint**: NSFW tier works identically to before

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation

- [X] T009 Create tests for kids tier character access (page access, character creation, picker visibility, tier isolation, NSFW regression) in tests/test_kids_characters.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — remove route guards first
- **US1 (Phase 3)**: Depends on Phase 2 — routes must be unblocked before template changes matter
- **US2 (Phase 4)**: Depends on Phase 2 — picker needs roster loading for all tiers
- **US3 (Phase 5)**: Depends on Phase 2 — edit/delete routes must be unblocked
- **US4 (Phase 6)**: Depends on all other phases — regression check
- **Polish (Phase 7)**: Depends on all user stories

### Parallel Opportunities

- T003 and T004 can run in parallel (different template files)
- T005 and T006 are in the same file but sequential (T005 modifies content block, T006 modifies scripts block)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Remove route guards
2. Complete Phase 3: Update home.html link + characters.html labels
3. **STOP and VALIDATE**: Kids can access character page and create characters

### Incremental Delivery

1. Foundational → Route guards removed, endpoints work on all tiers
2. Add US1 (character page access) → Kids can manage characters (MVP!)
3. Add US2 (picker on story start) → Kids can pick saved characters
4. Add US3 → Verify edit/delete works
5. Add US4 → Verify NSFW regression
6. Polish → Automated tests

---

## Notes

- This is one of the smallest features — primarily removing conditional gates
- The CharacterService, models, JS module, and templates are already fully tier-scoped
- No new routes, no new services, no new models, no new JS
- Main risk: accidentally breaking NSFW character roster — mitigated by regression tests
