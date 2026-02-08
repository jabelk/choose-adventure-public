# Tasks: Memory Mode

**Input**: Design documents from `/specs/011-memory-mode/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add Profile and Character Pydantic models and extend the Story model. These models are shared across all user stories.

- [X] T001 Add Profile and Character Pydantic models to app/models.py — Profile with fields: profile_id (UUID), name, tier, themes (list[str]), art_style (str), tone (str), story_elements (list[str]), characters (list[Character]), created_at, updated_at. Character with fields: character_id (UUID), name, description, linked_profile_id (optional str). Include validation per data-model.md (name max 100 chars, characters max 10, etc.)
- [X] T002 Add optional `profile_id` field (str, default None) to the existing Story model in app/models.py — this stores which profile was used for the story session

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the ProfileService with CRUD operations and the prompt context builder. All user stories depend on this service.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create app/services/profile.py with ProfileService class — implement `__init__` that creates `data/profiles/` directory structure, define `PROFILES_DIR` constant matching the pattern used by GalleryService (`Path(__file__).resolve().parent.parent.parent / "data" / "profiles"`)
- [X] T004 Implement `create_profile(tier, name, themes, art_style, tone, story_elements)` method in app/services/profile.py — create a new Profile, serialize to JSON, write to `data/profiles/{tier}/{profile_id}.json`, return the Profile
- [X] T005 Implement `get_profile(tier, profile_id)` and `list_profiles(tier)` methods in app/services/profile.py — `get_profile` reads and deserializes a single profile JSON file, `list_profiles` globs all `*.json` files in the tier directory, deserializes each, returns sorted by name
- [X] T006 Implement `update_profile(tier, profile_id, name, themes, art_style, tone, story_elements)` method in app/services/profile.py — load existing profile, update fields, set updated_at, write back to disk
- [X] T007 Implement `delete_profile(tier, profile_id)` method in app/services/profile.py — delete the JSON file, then scan all other profiles in the same tier and set `linked_profile_id` to None on any characters that referenced the deleted profile (FR-003, edge case: graceful degradation)
- [X] T008 Implement `build_profile_context(profile, tier)` method in app/services/profile.py — given a Profile, build a text string that describes the user's preferences and characters for injection into the AI system prompt. Include themes, tone, story elements, and all character names/descriptions. If any character has a `linked_profile_id`, load that linked profile and include its characters too (one level deep only, per research.md Decision 4). Return a tuple of (content_guidelines_addition: str, image_style_addition: str)

**Checkpoint**: ProfileService fully functional — CRUD operations work, profile context can be built for prompt injection

---

## Phase 3: User Story 1 — Create and Manage a Profile (Priority: P1) 🎯 MVP

**Goal**: Users can create, view, edit, and delete profiles with preferences through a dedicated profile management page, scoped to their tier.

**Independent Test**: Navigate to `/{tier}/profiles`, create a profile with preferences, verify it persists across page refreshes, edit it, confirm changes are saved. Verify tier isolation by checking `/nsfw/profiles` shows no kids profiles.

### Implementation for User Story 1

- [X] T009 [P] [US1] Create templates/profiles.html — extends base.html, displays a list of profiles for the current tier (name, themes, art style, tone, story elements, character count), includes a "Create Profile" form with fields for name, themes (textarea, comma-separated), art_style, tone, story_elements (textarea, comma-separated), and edit/delete buttons per profile. Include a link back to the tier home page.
- [X] T010 [P] [US1] Add profile page CSS styles to static/css/style.css — styles for `.profile-list`, `.profile-card`, `.profile-form`, `.profile-field`, `.profile-actions`, and form layout consistent with existing `.prompt-form` styling
- [X] T011 [US1] Add profile CRUD routes to app/routes.py inside `create_tier_router()` — add `GET /profiles` (list page), `POST /profiles/create` (create and redirect), `POST /profiles/{profile_id}/delete` (delete and redirect). Import and instantiate ProfileService. Pass profile list and tier info to template context. Place routes BEFORE the gallery catch-all routes.
- [X] T012 [US1] Create templates/profile_edit.html — extends base.html, displays an edit form for a single profile (pre-filled with current values), shows the profile's character list (name, description, linked profile name if any). Include a save button for the profile form. Character management (add/edit/delete) will be added in US3.
- [X] T013 [US1] Add profile edit/update routes to app/routes.py — add `GET /profiles/{profile_id}` (edit page) and `POST /profiles/{profile_id}/update` (update and redirect back to edit page). Load the profile, pass it to template context along with other same-tier profiles (for future character linking dropdown).
- [X] T014 [US1] Add "Profiles" link to templates/home.html — add a link (e.g., `<a href="{{ url_prefix }}/profiles">Manage Profiles</a>`) near the gallery link in the `.home-header` section

**Checkpoint**: Profile CRUD fully functional — users can create, view, edit, and delete profiles. Tier isolation enforced.

---

## Phase 4: User Story 2 — Toggle Memory Mode at Story Start (Priority: P2)

**Goal**: Users can toggle memory mode on the home page, select a profile, and have their preferences influence AI story and image generation for the entire story session.

**Independent Test**: Create a profile with strong preferences (e.g., "pirates, dark ocean themes"), start a story with memory mode on, verify generated story reflects preferences. Start another story with same prompt but memory mode off, verify no preference influence.

### Implementation for User Story 2

- [X] T015 [US2] Add memory mode toggle and profile dropdown to templates/home.html — add a `.memory-mode-selector` section below the story length selector with a checkbox toggle labeled "Memory Mode" and a `<select>` dropdown populated with `{{ profiles }}`. Use simple JS to show/hide the dropdown when toggle changes. Hidden by default when `profiles` list is empty (FR-009). Submit `memory_mode` and `profile_id` as form fields.
- [X] T016 [US2] Add memory mode CSS styles to static/css/style.css — styles for `.memory-mode-selector`, `.memory-toggle`, `.profile-dropdown`, show/hide animation consistent with existing `.length-selector` and `.model-selector` styling
- [X] T017 [US2] Modify the `tier_home` route in app/routes.py to pass the profiles list to the template — call `profile_service.list_profiles(tier_config.name)` and add `profiles` to the template context
- [X] T018 [US2] Modify the `start_story` route in app/routes.py to accept `memory_mode` and `profile_id` form fields — add `memory_mode: str = Form("")` and `profile_id: str = Form("")` parameters. When `memory_mode == "on"` and profile_id is valid, load the profile via ProfileService, call `build_profile_context()`, augment `content_guidelines` and `image_style` with the returned additions. Store `profile_id` on the Story model.
- [X] T019 [US2] Modify the `make_choice` route in app/routes.py to re-apply profile preferences on subsequent scene generation — if `story_session.story.profile_id` is set, load the profile, call `build_profile_context()`, and augment `content_guidelines` and `image_style` before calling `story_service.generate_scene()`

**Checkpoint**: Memory mode fully functional — profiles influence story generation when toggled on, no effect when toggled off. Profile preferences persist across all scenes in a story session.

---

## Phase 5: User Story 3 — Add Characters to a Profile (Priority: P3)

**Goal**: Users can add, edit, and delete characters within a profile, with optional cross-profile linking. Characters appear in generated stories when memory mode is active.

**Independent Test**: Add a character "Lily, loves dinosaurs" to a kids profile, start a story with memory mode on, verify the story includes Lily. Link a character to another profile and verify cross-profile characters are included.

### Implementation for User Story 3

- [X] T020 [US3] Add character CRUD methods to ProfileService in app/services/profile.py — implement `add_character(tier, profile_id, name, description, linked_profile_id)`, `update_character(tier, profile_id, character_id, name, description, linked_profile_id)`, `delete_character(tier, profile_id, character_id)`. Enforce the 10-character limit per profile (FR-014). Validate linked_profile_id is same-tier only (FR-013).
- [X] T021 [US3] Add character management forms to templates/profile_edit.html — add an "Add Character" form with name, description, and a `<select>` dropdown for linked profile (populated with same-tier profiles excluding the current one). For each existing character, show an inline edit form (name, description, linked profile dropdown) and a delete button. Each form posts to the appropriate character route.
- [X] T022 [US3] Add character routes to app/routes.py inside `create_tier_router()` — add `POST /profiles/{profile_id}/characters/add`, `POST /profiles/{profile_id}/characters/{character_id}/update`, `POST /profiles/{profile_id}/characters/{character_id}/delete`. Each redirects back to the profile edit page.
- [X] T023 [US3] Update `build_profile_context()` in app/services/profile.py to include character descriptions — when building the prompt context string, list each character by name and description. For characters with `linked_profile_id`, load the linked profile and include its characters too (one level deep). Format as a clear instruction for the AI (e.g., "The following characters should appear in the story: Lily - a curious 5-year-old who loves dinosaurs...").

**Checkpoint**: Characters fully functional — users can add/edit/delete characters, link across profiles within the same tier, and characters appear in generated stories.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, validation, and end-to-end testing

- [X] T024 Verify tier isolation — create profiles in both kids and nsfw tiers, confirm no cross-tier visibility via UI or direct URL access (FR-003, SC-004)
- [X] T025 Verify profile deletion cleanup — delete a profile that is referenced by characters in another profile, confirm linked_profile_id is set to null gracefully (edge case)
- [X] T026 Verify empty profile behavior — toggle memory mode on with a profile that has no preferences set, confirm story generates normally (edge case)
- [X] T027 Verify profile persistence across server restarts — create profiles, stop server, restart, confirm all data intact (FR-002, SC-003)
- [X] T028 Run full quickstart.md validation (all 10 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T003-T008)
- **User Story 2 (Phase 4)**: Depends on Foundational phase AND User Story 1 (needs profiles to exist to test the toggle)
- **User Story 3 (Phase 5)**: Depends on Foundational phase AND User Story 1 (needs profile edit page)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on US2 or US3
- **User Story 2 (P2)**: Can start after Foundational — but needs at least one profile created (US1) to meaningfully test
- **User Story 3 (P3)**: Can start after Foundational — but adds character forms to profile_edit.html (created in US1)

### Within Each User Story

- Templates and CSS can be created in parallel (different files)
- Routes depend on templates existing
- Service methods must exist before routes call them

### Parallel Opportunities

- T001 and T002 can run in parallel (both modify models.py but are logically sequential — T002 depends on T001)
- T009 and T010 can run in parallel (template vs CSS — different files)
- T003-T008 are sequential (same file, building on each other)
- T020 (service) and T021 (template) can be developed concurrently (different files)

---

## Parallel Example: User Story 1

```bash
# Template and CSS can be created in parallel (different files):
Task: "Create profiles.html template"                    # T009
Task: "Add profile page CSS styles"                      # T010

# Routes are sequential (same file, depends on templates):
Task: "Add profile CRUD routes"                          # T011
Task: "Create profile_edit.html template"                # T012
Task: "Add profile edit/update routes"                   # T013
Task: "Add Profiles link to home.html"                   # T014
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Pydantic models)
2. Complete Phase 2: Foundational (ProfileService with CRUD + context builder)
3. Complete Phase 3: User Story 1 (profile management UI)
4. **STOP and VALIDATE**: Create profiles, edit, delete, verify persistence
5. Profile management is functional — no story influence yet, but data layer is solid

### Incremental Delivery

1. Setup + Foundational → Models and service ready
2. Add User Story 1 → Profile CRUD → Users can manage profiles
3. Add User Story 2 → Memory mode toggle → Profiles influence story generation
4. Add User Story 3 → Characters → Personalized characters in stories, cross-profile linking
5. Each story adds personalization depth without breaking the previous

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No new pip dependencies needed — Pydantic, FastAPI, and Jinja2 handle everything
- ProfileService follows the same pattern as GalleryService (JSON files, Pydantic serialization)
- Profile context injection is additive — it augments existing content_guidelines and image_style, never replaces them
- Cross-profile character links are one level deep — no recursive chains
- Commit after each phase completion
- Stop at any checkpoint to validate independently
