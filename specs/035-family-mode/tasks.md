# Tasks: Family Mode

**Input**: Design documents from `/specs/035-family-mode/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Models and service that all user stories depend on.

- [X] T001 Add FamilyChild, FamilyParent, and Family Pydantic models to app/models.py (FamilyChild: name/gender/age, FamilyParent: name, Family: tier/children/parents)
- [X] T002 Create app/services/family.py with FamilyService class: get_family(tier), save_family(family), delete_family(tier), build_family_context(family) methods. Storage at data/family/{tier}/family.json

**Checkpoint**: Models and service exist, can create/read/delete family data programmatically.

---

## Phase 2: User Story 1 - Create and Save a Family (Priority: P1) 🎯 MVP

**Goal**: Family settings page where users add children (name/gender/age) and parents (name), save the family, and see it persist.

**Independent Test**: Open /kids/family, add 2 children and 1 parent, save, reload page, confirm data persisted.

### Implementation for User Story 1

- [X] T003 [P] [US1] Create templates/family.html with family settings form: add child fields (name, gender select, age number), add parent fields (name), display saved family members, back-to-home link. Extends base.html
- [X] T004 [P] [US1] Add family form CSS styles to static/css/style.css: .family-member-card, .family-form-section, .family-add-row (reuse existing .character-field, .btn patterns)
- [X] T005 [US1] Add family routes to app/routes.py inside create_tier_router: GET /{tier}/family (settings page), POST /{tier}/family/save (save form data with children[] and parents[] arrays). Import and instantiate FamilyService
- [X] T006 [US1] Add "Family" link to templates/home.html header alongside existing Gallery, Profiles, Characters links

**Checkpoint**: Users can navigate to Family page, add children and parents, save, and see persisted data on reload.

---

## Phase 3: User Story 2 - Family Members Injected Into Stories (Priority: P2)

**Goal**: Family Mode toggle on home page; when enabled, family names are injected into the story generation prompt.

**Independent Test**: Create a family, enable Family Mode toggle, start a story, verify the content_guidelines include family member names.

### Implementation for User Story 2

- [X] T007 [US2] Add Family Mode toggle to templates/home.html: checkbox with name="family_mode" value="on", shown only when family exists for the tier. Pass `family` context variable from tier_home handler
- [X] T008 [US2] Add family_mode Form parameter to start_story route in app/routes.py. When family_mode=="on", load family via FamilyService.get_family(tier), call build_family_context(family), append result to content_guidelines
- [X] T009 [US2] Add family_mode support to surprise route in app/routes.py: read family_mode from form, inject family context if enabled (same pattern as start_story)

**Checkpoint**: Stories started with Family Mode on include family member names in the AI prompt.

---

## Phase 4: User Story 3 - Edit and Delete Family Members (Priority: P3)

**Goal**: Users can remove individual children/parents and delete the entire family.

**Independent Test**: Create a family with 2 children, remove one child, confirm only 1 remains. Delete entire family, confirm Family page shows empty state.

### Implementation for User Story 3

- [X] T010 [US3] Add remove-child and remove-parent POST routes to app/routes.py: POST /{tier}/family/remove-child/{index} and POST /{tier}/family/remove-parent/{index}. Each loads family, removes the member at the given index, re-saves
- [X] T011 [US3] Add delete-family POST route to app/routes.py: POST /{tier}/family/delete. Calls FamilyService.delete_family(tier) and redirects to family page
- [X] T012 [US3] Update templates/family.html to show remove buttons next to each saved family member and a "Delete Family" button at the bottom when a family exists

**Checkpoint**: Individual members can be removed and entire family can be deleted.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T013 Write tests in tests/test_family_mode.py: family page returns 200, create family via POST, family persists on reload, family link on home page, Family Mode toggle shown when family exists, toggle hidden when no family, remove child works, delete family works, tier isolation (kids family not on nsfw)
- [X] T014 Run full test suite to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — creates models and service
- **US1 (Phase 2)**: Depends on Foundational (needs models + service)
- **US2 (Phase 3)**: Depends on US1 (needs family to exist for toggle to appear)
- **US3 (Phase 4)**: Depends on US1 (needs family to exist to edit/delete)
- **Polish (Phase 5)**: Depends on all user stories

### Within User Story 1

- T003 and T004 can run in parallel (different files: template vs CSS)
- T005 depends on T003 (routes render the template)
- T006 is independent (just adds a link)

### Parallel Opportunities

```bash
# T003 and T004 can run in parallel:
Task: "Create family.html template"
Task: "Add family CSS styles"
```

---

## Implementation Strategy

### MVP First (US1)

1. T001 + T002: Models + FamilyService
2. T003 + T004 (parallel): Template + CSS
3. T005 + T006: Routes + home link
4. **VALIDATE**: Family page works, data persists

### Incremental Delivery

1. Foundation + US1 → Family can be created and saved
2. US2 → Family names injected into stories
3. US3 → Edit and delete support
4. Polish → Tests and validation
