# Feature Specification: Reusable Character Roster

**Feature Branch**: `023-character-roster`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Reusable Character Roster — Save characters like Margot Ellis and Kayla Rae as persistent entries you can pick from a dropdown instead of re-typing name and description each time. Separate from profiles — these are fictional characters with name, physical description, and optionally a reference photo. Manageable from a dedicated page. NSFW tier only. Characters have: name (required), physical description (required), and optionally one or more reference photos (reuse the existing photo upload system). A character management page lists all saved characters with edit/delete. On the story start form, a 'Pick a character' dropdown appears above the character name/description fields. Selecting a character pre-fills those fields (and attaches their reference photos). User can still manually type a character instead. Characters are stored as JSON files in data/characters/{tier}/ similar to how profiles work. Characters should also be selectable in the story templates — templates can reference a saved character by name. Limit to maybe 20 characters max per tier to keep it manageable."

## Clarifications

### Session 2026-02-07

- Q: How should the roster relate to existing profile characters (Profile.characters)? → A: Roster replaces profile characters — migrate existing profile chars to roster, remove character storage from profiles.
- Q: Where should roster character photos be stored? → A: `data/characters/{tier}/{character_id}/photos/` — self-contained per character directory.
- Q: Should profiles retain the ability to reference roster characters after migration? → A: Yes — profiles store a list of roster character IDs. When a profile is selected, its referenced characters are auto-selected.
- Q: Should the roster support selecting multiple characters for a single story? → A: Yes — multi-select. Allow picking multiple roster characters, all injected into story context.
- Q: How should templates reference characters with multi-select support? → A: Templates store a list of character names, all matched against the roster and pre-selected.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Save a Character (Priority: P1)

The user navigates to a character management page accessible from the NSFW tier home page. They fill in a character name and physical description, and optionally upload one or more reference photos. They save the character, and it appears in their character list. The character persists across browser sessions — it's stored on the server, not in session memory.

This is the foundational user story. Without the ability to create and persist characters, none of the other stories (picking characters, template integration) are possible.

**Why this priority**: Creating and saving characters is the core data operation that everything else depends on.

**Independent Test**: Navigate to the character management page, create a new character with name and description, verify it appears in the list. Close the browser, reopen, and verify the character is still there.

**Acceptance Scenarios**:

1. **Given** the user is on the NSFW tier, **When** they navigate to the character management page, **Then** they see a list of saved characters (or an empty state if none exist).
2. **Given** the user is on the character management page, **When** they fill in a name and description and tap Save, **Then** the character is saved and appears in the list.
3. **Given** the user is creating a character, **When** they upload one or more reference photos, **Then** the photos are stored alongside the character data.
4. **Given** a character already exists, **When** the user views the character list, **Then** they see the character's name, a truncated description, and a thumbnail of the first photo (if any).
5. **Given** the user has 20 characters saved, **When** they try to create a 21st, **Then** the system shows an error indicating the limit has been reached.

---

### User Story 2 - Pick Saved Characters When Starting a Story (Priority: P2)

When starting a new story on the NSFW tier, a multi-select character picker appears above the character name and description fields. The user can select one or more saved characters. All selected characters' names, descriptions, and reference photos are injected into the story context. The user can still manually type an additional character using the existing name/description fields alongside any roster selections.

This is the primary payoff of saving characters — the user no longer has to re-type "Margot Ellis, early 30s, honey-blonde hair, hazel eyes..." every time, and can easily set up multi-character stories.

**Why this priority**: This is the main value delivery — reusing saved characters in new stories. However, it requires characters to exist first (US1).

**Independent Test**: Create two characters (US1), then start a new story. Select both characters from the picker and verify they appear as selected. Start the story and verify both characters appear in the generated content.

**Acceptance Scenarios**:

1. **Given** the user has saved characters, **When** they view the story start form on the NSFW tier, **Then** a multi-select character picker appears above the character name/description fields.
2. **Given** the user selects one or more characters from the picker, **When** the selection is made, **Then** all selected characters' names and descriptions are shown as selected and will be injected into the story context.
3. **Given** the selected characters have reference photos, **When** the characters are selected, **Then** all their reference photos are attached to the story.
4. **Given** the user has selected roster characters, **When** they also type a name and description in the manual character fields, **Then** both the roster characters and the manual character are included in the story.
5. **Given** the user has no saved characters, **When** they view the story start form, **Then** the character picker is not shown (or shows "No saved characters"), and the manual character fields work as before.
6. **Given** the user has selected characters and then deselects all, **When** they clear the selections, **Then** no roster characters are included and the manual fields are available as before.

---

### User Story 3 - Edit and Delete Characters (Priority: P3)

The user can edit an existing character's name, description, or photos from the character management page. They can also delete characters they no longer want. Editing opens the character in a form pre-filled with current values. Deleting requires a confirmation to prevent accidental loss.

**Why this priority**: Management operations (edit/delete) are important for long-term usability but not required for the initial create-and-use workflow.

**Independent Test**: Create a character, then edit its description. Verify the change persists. Delete a character and verify it no longer appears in the list or the story start dropdown.

**Acceptance Scenarios**:

1. **Given** a character exists, **When** the user taps Edit, **Then** a form opens pre-filled with the character's current name, description, and photos.
2. **Given** the user is editing a character, **When** they change the description and tap Save, **Then** the updated description is persisted.
3. **Given** the user is editing a character, **When** they upload a new photo or remove an existing one, **Then** the photo changes are saved.
4. **Given** a character exists, **When** the user taps Delete, **Then** a confirmation prompt appears before deletion.
5. **Given** the user confirms deletion, **When** the character is deleted, **Then** it no longer appears in the character list or the story start dropdown.
6. **Given** a character is used in a story template, **When** the character is deleted, **Then** the template falls back to its inline character data (does not break).

---

### User Story 4 - Template Characters Reference Saved Roster (Priority: P4)

Story templates on the NSFW tier can reference a list of saved characters by name. When a template is selected, all referenced characters that exist in the roster are pre-selected in the character picker (using the latest description and photos from the roster). Characters referenced by the template that don't exist in the roster fall back to the template's inline character data.

**Why this priority**: This is a polish feature that enhances the template experience but is not required for core character reuse. Templates already have inline character data that works without the roster.

**Independent Test**: Save characters named "Margot Ellis" and "Kayla Rae" to the roster. Select a template that references both names. Verify both characters are pre-selected in the picker using their roster descriptions/photos.

**Acceptance Scenarios**:

1. **Given** a template references character names that exist in the roster, **When** the user selects that template, **Then** all matching characters are pre-selected in the character picker using their roster data.
2. **Given** a template references a character name that does NOT exist in the roster, **When** the user selects that template, **Then** the template's inline character data for that character is used as a fallback (injected into context directly).
3. **Given** the user has updated a character in the roster, **When** they select a template referencing that character, **Then** the updated roster data is used.
4. **Given** a template references multiple characters and some exist in the roster while others don't, **When** the user selects that template, **Then** roster characters are pre-selected and non-roster characters use the template's inline fallback data.

---

### Edge Cases

- What happens if the user tries to create a character with a name that already exists? The system shows an error asking them to use a different name or edit the existing character. Names must be unique within a tier.
- What happens if the character's reference photos are deleted from disk (e.g., manual cleanup)? The character still loads but the photos section shows "Photos unavailable." The character remains usable without photos.
- What happens if the user navigates to the character page on the kids tier? The character roster page is not accessible on the kids tier. It only exists on the NSFW tier.
- What happens if the character data file is corrupted or invalid? The system skips that character and logs a warning. Other characters still load normally.
- What happens when photos exceed the upload size limit? The existing photo upload validation applies — same size limits and format restrictions as the story start form.
- What happens when multiple selected characters' combined photos exceed the upload limit? The system includes photos from characters in selection order, up to the limit (3 photos max). Additional photos are silently excluded with a note shown to the user.
- What happens when a profile references a roster character that no longer exists? The deleted character reference is silently ignored — the profile still loads, but that character is not pre-selected. No error is shown.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The NSFW tier MUST provide a character management page accessible from the home page navigation.
- **FR-002**: Users MUST be able to create a character with a name (required, unique within tier) and physical description (required).
- **FR-003**: Users MUST be able to optionally attach one or more reference photos to a character, using the same upload mechanism as the story start form.
- **FR-004**: Character data MUST persist across browser sessions (server-side storage, not session-only).
- **FR-005**: The character management page MUST display all saved characters with name, truncated description, and photo thumbnail.
- **FR-006**: The NSFW story start form MUST include a multi-select character picker that lists all saved characters.
- **FR-007**: Selecting one or more characters from the picker MUST inject all selected characters' names and descriptions into the story context.
- **FR-008**: Selecting characters with reference photos MUST attach all their photos to the story.
- **FR-008a**: The user MUST be able to use both roster character selections and the manual character name/description fields together — they are additive, not mutually exclusive.
- **FR-009**: Users MUST be able to edit an existing character's name, description, and photos.
- **FR-010**: Users MUST be able to delete a character, with a confirmation step before deletion.
- **FR-011**: The system MUST enforce a maximum of 20 characters per tier.
- **FR-012**: Character names MUST be unique within a tier (case-insensitive comparison).
- **FR-013**: The character roster feature MUST NOT be accessible on the kids tier.
- **FR-014**: Story templates MUST support referencing a list of character names. For each referenced name, if the character exists in the roster it MUST be pre-selected in the picker using roster data; otherwise the template's inline character data MUST be used as fallback.
- **FR-015**: Deleting a character MUST NOT break any story templates — templates fall back to their inline character data for deleted characters.
- **FR-016**: The user MUST be able to deselect characters from the picker to remove them from the story context.
- **FR-017**: Existing characters stored in profiles MUST be migrated to the roster as part of this feature. After migration, character storage MUST be removed from the profile system.
- **FR-018**: Profiles that previously referenced characters MUST continue to function after migration (profiles reference roster characters instead of storing them inline).
- **FR-019**: Profiles MUST be able to store a list of roster character IDs as references. When a profile is selected for a story, its referenced roster characters MUST be auto-selected in the character dropdown.
- **FR-020**: If a profile references a roster character that has been deleted, the reference MUST be silently ignored (no error, character simply not pre-selected).

### Key Entities

- **Character**: A reusable fictional character entry with a unique name, physical description, and optional reference photos. Belongs to a specific tier. Limited to 20 per tier. Persisted on the server across sessions.
- **Character Photo**: A reference image associated with a character, permanently stored at `data/characters/{tier}/{character_id}/photos/`. Uses the same upload validation (size limits, format restrictions) as the story start form but with permanent storage (not session-scoped).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create and save a new character in under 30 seconds (name + description, no photos).
- **SC-002**: Selecting a saved character from the dropdown pre-fills all fields in under 1 second (instant, no page reload).
- **SC-003**: 100% of saved characters appear in both the management page and the story start dropdown.
- **SC-004**: Character data persists indefinitely across browser sessions until manually deleted.
- **SC-005**: Deleting a character does not break any existing story templates — templates continue to function with fallback data.
- **SC-006**: The character roster is not visible or accessible from the kids tier.

## Assumptions

- The character roster replaces the existing Profile.characters system. Existing profile characters MUST be migrated to the roster, and the character fields removed from profiles. Profiles will no longer store characters directly.
- Characters are scoped to a tier (NSFW only at launch), but the storage structure supports future expansion to other tiers.
- Character photos reuse the existing upload infrastructure — same file size limits, same supported formats (JPEG, PNG), same storage location pattern.
- The character management page is a simple CRUD interface — no search, no filtering, no sorting. With a 20-character limit, a flat list is sufficient.
- Character data is stored as individual JSON files at `data/characters/{tier}/{character_id}.json`, with photos stored at `data/characters/{tier}/{character_id}/photos/`. Each character's data and photos are self-contained in the same directory tree.
- The character picker on the story start form is client-side JavaScript — selecting characters updates the form without a page reload.
- Templates reference characters by a list of names (string match). There is no formal ID-based linking between templates and roster characters. Templates will be updated from single `character_name`/`character_description` fields to a `character_names` list plus inline fallback data per character.
- Roster character selections and manual character entry are additive. The user can select multiple roster characters AND type an additional character manually. All are included in the story context.
- Selected roster characters' photos are combined and attached to the story. The total photo count across all selected characters is subject to the existing upload limits.
- The edit form reuses the same layout as the create form, pre-filled with existing values.
- After migration, profiles store a list of roster character IDs (not inline character data). When a profile is active, its referenced characters are auto-selected in the character dropdown on the story start form. Deleted roster characters are silently dropped from profile references.

## Scope Boundaries

**In scope**:
- Character CRUD (create, read, update, delete) on a dedicated management page
- "Pick a character" dropdown on the NSFW story start form
- Auto-fill of name, description, and photo attachment on character selection
- Template integration — templates reference roster characters by name
- 20-character limit per tier
- NSFW tier only
- Migration of existing profile characters to the roster (roster replaces Profile.characters)
- Removal of character storage from the profile system after migration

**Out of scope**:
- Character roster on the kids tier (may be added later as "Favorite Characters")
- Character sharing between tiers
- Character import/export
- Character search or filtering (unnecessary at 20-character scale)
- Character tags or categories
- Character usage history or analytics
- Automatic character detection from story content
- Character art generation (characters are described in text, not generated as standalone images)
