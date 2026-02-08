# Tasks: Reusable Character Roster

**Input**: Design documents from `/specs/023-character-roster/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Data model and service foundation for the character roster system

- [X] T001 Add RosterCharacter Pydantic model to app/models.py with fields: character_id (UUID), name (str, max 100), description (str, max 500), tier (str), photo_paths (list[str], max 3), created_at, updated_at. Add roster_character_ids (list[str]) field to Story model. Update Profile model: replace characters (list[Character]) with character_ids (list[str]).
- [X] T002 Create app/services/character.py with CharacterService class implementing: create_character(tier, name, description) returning RosterCharacter, get_character(tier, character_id) returning RosterCharacter or None, list_characters(tier) returning list sorted by name, save_character(character) writing JSON to data/characters/{tier}/{character_id}.json, delete_character(tier, character_id) removing JSON file and photos directory, name_exists(tier, name, exclude_id=None) for case-insensitive uniqueness check. Include constants MAX_CHARACTERS=20, DATA_DIR=Path("data/characters"). Ensure data/characters/{tier}/ directory created on first use.
- [X] T003 Add character photo management methods to app/services/character.py: save_character_photos(tier, character_id, files: list[UploadFile]) validating JPEG/PNG, max 10MB, max 3 photos, saving to data/characters/{tier}/{character_id}/photos/{index}_{id[:8]}.{ext} and updating character.photo_paths. Add delete_character_photo(tier, character_id, filename) removing a single photo file and updating photo_paths. Add get_character_photo_path(tier, character_id, filename) returning absolute Path or None.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update StoryTemplate dataclass and NSFW template definitions — required before story start integration (US2) and template integration (US4)

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Update StoryTemplate dataclass in app/tiers.py: replace character_name (str) and character_description (str) fields with character_names (list[str], default_factory=list) and character_data (list[dict], default_factory=list). Update all NSFW tier template instances to use the new fields — e.g., templates referencing "Margot Ellis" should use character_names=["Margot Ellis"] and character_data=[{"name": "Margot Ellis", "description": "Early 30s, honey-blonde hair..."}]. Ensure kids tier templates (which don't use character fields) still work with empty defaults.

**Checkpoint**: Foundation ready — model, service, and template dataclass are in place

---

## Phase 3: User Story 1 — Create and Save a Character (Priority: P1) MVP

**Goal**: Users can create, view, and persist characters from a dedicated management page on the NSFW tier

**Independent Test**: Navigate to /nsfw/characters, create a character with name and description, verify it appears in the list. Close browser, reopen, verify it persists.

### Implementation for User Story 1

- [X] T005 [US1] Create templates/characters.html extending base.html with: character list showing each character's name, truncated description (first 80 chars), and first photo thumbnail (if any); a create/edit form with name input (max 100), description textarea (max 500), and photo upload (reuse upload drop zone pattern from home.html); empty state message "No characters saved yet"; character count display ("N / 20 characters"); error/success flash message display. Include NSFW theme class and data-tier attribute.
- [X] T006 [US1] Add character management routes to app/routes.py inside create_tier_router(): GET /{prefix}/characters rendering characters.html with characters list, character_count, and max_characters context; POST /{prefix}/characters/create accepting multipart form (name, description, reference_photos) calling character_service.create_character() and save_character_photos(), enforcing 20-character limit and name uniqueness, redirecting to GET characters with flash; GET /{prefix}/characters/{character_id}/photo/{filename} serving photo files with correct Content-Type. Guard all character routes with a check: if tier_config.name != "nsfw", return 404.
- [X] T007 [US1] Add "Characters" navigation link to templates/base.html visible only when data-tier is "nsfw". Place it alongside existing nav items. Link to {{ url_prefix }}/characters.
- [X] T008 [US1] Add CSS styles to static/css/style.css for character management page: .character-list, .character-card (with thumbnail, name, description truncation), .character-form, .character-count, .character-empty-state. Style consistently with existing NSFW theme using CSS custom properties. Add responsive styles for mobile.

**Checkpoint**: US1 complete — character CRUD page works, characters persist as JSON files

---

## Phase 4: User Story 2 — Pick Saved Characters When Starting a Story (Priority: P2)

**Goal**: Multi-select character picker on the NSFW story start form lets users select saved characters whose data is injected into the story

**Independent Test**: Create 2 characters via US1, start a new story, select both from the picker, verify both characters' names/descriptions appear in generated content

### Implementation for User Story 2

- [X] T009 [US2] Add GET /{prefix}/characters/api/list JSON endpoint to app/routes.py returning all characters as JSON with character_id, name, description, photo_urls, photo_count. Guard with NSFW tier check.
- [X] T010 [US2] Create static/js/character-picker.js implementing multi-select character picker: render checkbox list of characters with name and truncated description; on checkbox toggle, add/remove character_id from hidden form fields (roster_character_ids[]); show selected character count; handle empty state ("No saved characters"). Export initCharacterPicker(characters, preselectedIds) function.
- [X] T011 [US2] Update templates/home.html to include character picker section above the existing Character name/description fields (NSFW tier only): add a container div for the picker, include character-picker.js script, call initCharacterPicker() with characters data passed from server context. Add hidden input fields for roster_character_ids[]. Keep existing manual character_name/character_description fields below the picker as "Or describe a character manually" section.
- [X] T012 [US2] Update the home page route (GET /{prefix}/) in app/routes.py to pass roster_characters list to template context (from character_service.list_characters(tier_config.name)) when tier is NSFW. Pass empty list for other tiers.
- [X] T013 [US2] Update POST /{prefix}/story/start in app/routes.py to accept roster_character_ids form field (list[str]). For each ID, load character via character_service.get_character(), build CHARACTER block(s) appended to content_guidelines (same format as existing character_name block but for each roster character), collect photo_paths from all roster characters (up to 3 total). Store roster_character_ids on Story object. Roster characters are additive with manual character_name/character_description.
- [X] T014 [US2] Update POST /{prefix}/story/choose/{scene_id}/{choice_id} in app/routes.py to rebuild roster character context on subsequent choices: if story.roster_character_ids is set, load each character, rebuild CHARACTER blocks and collect photo paths (same logic as story start).
- [X] T015 [US2] Add CSS styles to static/css/style.css for .character-picker, .character-picker-item, .character-picker-checkbox, .character-picker-selected-count. Style with NSFW theme colors. Ensure picker collapses nicely on mobile.

**Checkpoint**: US2 complete — characters can be selected from picker and appear in generated stories

---

## Phase 5: User Story 3 — Edit and Delete Characters (Priority: P3)

**Goal**: Users can edit existing character details/photos and delete characters with confirmation

**Independent Test**: Create a character, edit its description, verify the change persists. Delete a character, verify it's gone from list and picker.

### Implementation for User Story 3

- [X] T016 [US3] Add update and delete routes to app/routes.py: POST /{prefix}/characters/{character_id}/update accepting multipart form (name, description, reference_photos, remove_photos) calling character_service to update fields, save new photos, remove specified photos, enforce name uniqueness (excluding self), redirect with flash; POST /{prefix}/characters/{character_id}/delete removing character and photos directory via character_service.delete_character(), redirect with flash. Both routes guarded by NSFW tier check.
- [X] T017 [US3] Update templates/characters.html to add Edit and Delete buttons per character card. Edit button opens the create/edit form pre-filled with character's current name, description, and photo thumbnails (with remove buttons per photo). Delete button triggers a JavaScript confirm() dialog before submitting the delete form. When editing, the form action changes to the update endpoint with the character_id.
- [X] T018 [US3] Add update_character(tier, character_id, name, description) method to app/services/character.py that loads existing character, updates fields, sets updated_at, and saves. Add remove_character_photo(tier, character_id, filename) that deletes the file and updates photo_paths list.

**Checkpoint**: US3 complete — full CRUD operations work on character management page

---

## Phase 6: User Story 4 — Template Characters Reference Saved Roster (Priority: P4)

**Goal**: When a template is selected, its referenced characters are looked up in the roster and pre-selected in the picker. Fallback to inline template data if character not in roster.

**Independent Test**: Save "Margot Ellis" to roster. Select a template referencing "Margot Ellis". Verify she's pre-selected in the picker with roster data (not template inline data).

### Implementation for User Story 4

- [X] T019 [US4] Update template selection JavaScript in templates/home.html: modify selectTemplate() to read data-character-names (JSON array) and data-character-data (JSON array) from template card. For each name in character_names, check if a roster character with that name exists — if yes, check its checkbox in the picker; if no, inject the template's inline fallback data into the manual character fields or a hidden fallback context field.
- [X] T020 [US4] Update templates/home.html template cards to render new data attributes: data-character-names="{{ tpl.character_names | tojson }}" and data-character-data="{{ tpl.character_data | tojson }}" (replacing old data-character-name and data-character-description).
- [X] T021 [US4] Update POST /{prefix}/story/start in app/routes.py to accept an optional template_fallback_characters form field (JSON string of character data not found in roster). Parse and inject these fallback characters into content_guidelines alongside roster characters.

**Checkpoint**: US4 complete — templates pre-select roster characters and fall back gracefully

---

## Phase 7: Profile Migration & Integration

**Purpose**: Migrate existing profile characters to roster and update profile system

- [X] T022 Create scripts/migrate_profile_characters.py: read all profiles from data/profiles/nsfw/, for each profile with characters, create a RosterCharacter for each (with new UUID), copy photos from data/photos/{tier}/{profile_id}/{character_id}.{ext} to data/characters/{tier}/{new_id}/photos/, update profile JSON replacing characters list with character_ids list of new UUIDs, back up original profile files to data/profiles/nsfw/backups/ before modification. Make script idempotent (skip profiles already migrated — detected by presence of character_ids field).
- [X] T023 Update app/services/profile.py: remove add_character(), update_character(), delete_character(), save_character_photo(), delete_character_photo(), get_character_photo_path() methods. Update build_profile_context() to load roster characters by ID from character_service instead of reading inline characters. Update Profile model usage to expect character_ids instead of characters.
- [X] T024 Update profile routes in app/routes.py: remove the 6 character-specific profile routes (add/update/delete character, upload/delete/serve photo). Update GET /{prefix}/profiles/{profile_id} to pass roster_characters list and selected_character_ids to template context. Update POST /{prefix}/profiles/{profile_id}/update to accept character_ids form field (list of roster character IDs to associate with profile).
- [X] T025 Update templates/profiles.html (or profile edit template) to replace inline character management UI with a roster character picker (checkboxes for available roster characters, pre-checked for profile's current character_ids). Remove add/edit/delete character forms and photo upload for characters.
- [X] T026 Update POST /{prefix}/story/start in app/routes.py: when memory_mode is on and a profile is selected, auto-select the profile's character_ids in the roster picker (merge with any manually selected roster_character_ids from the form).

**Checkpoint**: Migration complete — profiles reference roster characters, old character routes removed

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Tests, validation, and cleanup

- [X] T027 Add character roster tests to tests/test_all_options.py: TestCharacterCreate (create character, name uniqueness, 20-char limit, photo upload, empty name rejection), TestCharacterPicker (picker appears on NSFW start form, hidden on kids, character data injected into story context, multi-select works), TestCharacterEditDelete (edit persists, delete removes, delete confirmation), TestCharacterTemplateIntegration (template pre-selects roster chars, fallback for missing chars), TestCharacterProfileIntegration (profile references roster chars, deleted char silently ignored), TestCharacterTierIsolation (kids tier returns 404 for character routes).
- [X] T028 Run full test suite with venv/bin/python -m pytest tests/ -v and verify all tests pass (existing + new character roster tests)
- [X] T029 Verify kids tier isolation: confirm no character routes, picker, or nav links appear on /kids/ pages. Confirm GET /kids/characters returns 404.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (needs model and service)
- **US1 (Phase 3)**: Depends on Phase 2 — first deliverable
- **US2 (Phase 4)**: Depends on Phase 3 (needs characters to exist for picker)
- **US3 (Phase 5)**: Depends on Phase 3 (needs characters to edit/delete)
- **US4 (Phase 6)**: Depends on Phase 4 (needs picker to pre-select into)
- **Migration (Phase 7)**: Depends on Phase 3 (needs character service) — can run in parallel with US2-US4
- **Polish (Phase 8)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: No story dependencies — standalone after foundational phase
- **US2 (P2)**: Requires US1 (characters must exist to pick from)
- **US3 (P3)**: Requires US1 (characters must exist to edit/delete) — can run in parallel with US2
- **US4 (P4)**: Requires US2 (needs the multi-select picker to pre-select into)

### Within Each User Story

- Models/services before routes
- Routes before templates
- Templates before JavaScript
- Core implementation before CSS polish

### Parallel Opportunities

- T002 and T003 (character service core + photo methods) are sequential (same file)
- T005 (template) and T008 (CSS) can run in parallel with T006 (routes)
- T009 (API endpoint) and T010 (JS picker) can run in parallel
- T016 (routes) and T018 (service methods) should be done together (same-feature coupling)
- US3 (Phase 5) can run in parallel with US2 (Phase 4) after US1 complete
- Phase 7 (migration) can start as soon as Phase 3 is done, parallel with US2-US4

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004)
3. Complete Phase 3: User Story 1 (T005-T008)
4. **STOP and VALIDATE**: Create a character, verify it persists, verify list works
5. Deploy if ready — character management page is usable standalone

### Incremental Delivery

1. Setup + Foundational → Model and service ready
2. Add US1 → Character CRUD page works → Deploy (MVP!)
3. Add US2 → Characters selectable in story start → Deploy
4. Add US3 → Edit/delete characters → Deploy
5. Add US4 → Templates reference roster → Deploy
6. Migration → Existing profile characters migrated → Deploy
7. Polish → Tests pass, tier isolation verified → Final deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Character service follows same patterns as existing profile service
- Reuse existing upload.js for photo upload on character management page
- All character routes guarded by NSFW tier check (return 404 on kids)
- Migration script is idempotent and creates backups
- Commit after each task or logical group
