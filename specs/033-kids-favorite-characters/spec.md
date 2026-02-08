# Feature Specification: Favorite Characters Across Stories (Kids)

**Feature Branch**: `033-kids-favorite-characters`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Favorite Characters Across Stories (Kids) — Let the girls save and reuse characters across stories — their stuffed animals, imaginary friends, or characters they loved from previous stories. Adapt the named character feature (built for NSFW as character roster) for the kids tier with a kid-friendly character creator. Both tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Kids Can Save Favorite Characters (Priority: P1)

A child (or parent helping) navigates to a "My Characters" page on the kids tier, accessible from the home page. They create a new character by entering a name and a short description — such as their favorite stuffed animal ("Mr. Snuggles, a fluffy purple bear who loves cuddles") or an imaginary friend ("Captain Sparkle, a tiny fairy with rainbow wings"). They can optionally upload a photo. The character is saved and appears in their character list, ready to be used in future stories.

**Why this priority**: This is the foundational feature — without saving characters, there's nothing to reuse. The character management page is the entry point for the entire feature.

**Independent Test**: Navigate to the kids tier "My Characters" page, create a character named "Mr. Snuggles" with a description, verify it appears in the list. Close the browser and reopen — the character is still there.

**Acceptance Scenarios**:

1. **Given** a user is on the kids tier home page, **When** they click the "My Characters" link, **Then** they see a character management page with a list of saved characters (or a friendly empty state message if none exist).
2. **Given** a user is on the character page, **When** they enter a name and description and save, **Then** the character appears in their list immediately.
3. **Given** a user is creating a character, **When** they optionally upload a reference photo, **Then** the photo is stored with the character and shown as a thumbnail in the list.
4. **Given** a user has reached the maximum character limit, **When** they try to add another, **Then** a friendly message explains they need to remove one first.

---

### User Story 2 - Pick Favorite Characters When Starting a Story (Priority: P2)

When starting a new story on the kids tier, a character picker appears if the user has saved characters. The user can select one or more characters to include in the story. Selected characters' names and descriptions are woven into the story context so the AI generates scenes featuring those characters. The child can also still type a custom character name/description in the manual fields.

**Why this priority**: This is the main payoff — reusing saved characters. A child doesn't have to describe "Mr. Snuggles" every time they want a story about their favorite bear. Requires characters to exist first (US1).

**Independent Test**: Create a character "Mr. Snuggles" (US1), then start a new kids story. Select Mr. Snuggles from the picker, start the story, and verify the generated content references Mr. Snuggles.

**Acceptance Scenarios**:

1. **Given** a user has saved characters on the kids tier, **When** they view the story start form, **Then** a character picker is visible showing their saved characters.
2. **Given** the user selects one or more characters from the picker, **When** the story starts, **Then** all selected characters appear in the generated story content.
3. **Given** the user has selected characters with reference photos, **When** the story starts, **Then** the photos are used as reference for image generation.
4. **Given** the user has no saved characters, **When** they view the story start form, **Then** the character picker is hidden and the manual fields work as usual.
5. **Given** the user selects roster characters AND types a manual character, **When** the story starts, **Then** all characters (roster + manual) are included.

---

### User Story 3 - Edit and Delete Favorite Characters (Priority: P3)

The user can edit a saved character's name, description, or photo from the "My Characters" page. They can also delete characters they no longer want. Editing opens the character in a form with current values pre-filled. Deleting shows a confirmation to prevent accidental removal.

**Why this priority**: Management operations are important for long-term use but not needed for the initial create-and-reuse flow.

**Independent Test**: Create a character, edit its description, verify the change persists. Delete the character and confirm it's gone from both the list and the story start picker.

**Acceptance Scenarios**:

1. **Given** a character exists, **When** the user taps Edit, **Then** a form appears pre-filled with the character's current name, description, and photo.
2. **Given** the user edits a character's description and saves, **Then** the updated description is persisted and reflected everywhere.
3. **Given** a character exists, **When** the user taps Delete, **Then** a confirmation is shown before deletion proceeds.
4. **Given** the user confirms deletion, **Then** the character is removed from the list and the story start picker.

---

### User Story 4 - NSFW Tier Continues Working Unchanged (Priority: P4)

The existing NSFW character roster continues to function exactly as before. Enabling the character roster on the kids tier does not change NSFW behavior. Each tier's characters are separate — kids characters don't appear on NSFW and vice versa.

**Why this priority**: Regression prevention — must ensure existing NSFW functionality isn't broken.

**Independent Test**: After enabling kids characters, verify the NSFW character roster page, character picker on story start, and template integration all work identically to before.

**Acceptance Scenarios**:

1. **Given** the NSFW tier has existing characters, **When** the kids tier characters feature is enabled, **Then** NSFW characters are unaffected and still function.
2. **Given** characters exist on both tiers, **When** viewing either tier's character list, **Then** only that tier's characters appear — no cross-tier visibility.

---

### Edge Cases

- What happens if a child creates a character with the same name as an existing one? A friendly message says "You already have a character named that! Try a different name or edit the existing one."
- What happens if the character photo file is missing from disk? The character still loads and works; the photo area shows a placeholder image.
- What happens on the kids tier home page if the user has no characters? The "My Characters" link still appears, and the page shows a friendly empty state like "No characters yet! Create your first one."
- What happens with kid-inappropriate character names or descriptions? The same content guidelines that govern story generation apply — the AI ignores or sanitizes inappropriate input when generating stories. No server-side content filtering is needed for character creation itself (this is a private, self-hosted app for a family).
- What happens if the existing NSFW character data directory structure changes? It doesn't — the kids tier uses the same storage pattern (`data/characters/kids/`) that NSFW uses (`data/characters/nsfw/`), so no structural changes are needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The kids tier MUST provide a "My Characters" management page accessible from the home page.
- **FR-002**: Users MUST be able to create a character on the kids tier with a name (required, unique within the kids tier) and a description (required).
- **FR-003**: Users MUST be able to optionally attach a reference photo to a kids tier character, using the same upload mechanism as the story start form.
- **FR-004**: Kids tier character data MUST persist across browser sessions (server-side storage).
- **FR-005**: The kids tier "My Characters" page MUST display all saved characters with name, truncated description, and photo thumbnail.
- **FR-006**: The kids tier story start form MUST include a character picker when the user has saved characters.
- **FR-007**: Selecting characters from the kids tier picker MUST inject their names and descriptions into the story context.
- **FR-008**: Selecting characters with reference photos MUST attach those photos to the story for image generation context.
- **FR-009**: Users MUST be able to use both roster character selections and manual character name/description fields together on the kids tier.
- **FR-010**: Users MUST be able to edit a kids tier character's name, description, and photo.
- **FR-011**: Users MUST be able to delete a kids tier character, with a confirmation step.
- **FR-012**: The system MUST enforce the same maximum character limit per tier (20 characters) on the kids tier.
- **FR-013**: Character names MUST be unique within a tier (case-insensitive).
- **FR-014**: Kids tier characters MUST be completely separate from NSFW tier characters — no cross-tier visibility or access.
- **FR-015**: The existing NSFW character roster MUST continue to function identically after this change.
- **FR-016**: The kids tier character page MUST use kid-friendly language (e.g., "My Characters" instead of "Character Roster", friendly empty states and labels).

### Key Entities

- **Character (Kids Tier)**: A reusable fictional character entry on the kids tier with a unique name, description, and optional reference photo. Stored in the same format and structure as NSFW characters but scoped to the kids tier. Limited to 20 per tier.

### Assumptions

- The existing character roster infrastructure (routes, service, storage, templates) already supports tier-scoped characters. The primary work is removing the NSFW-only gates and adding kid-friendly UI text.
- The character data storage pattern (`data/characters/{tier}/`) already supports multiple tiers — the kids tier directory just needs to be used.
- The character picker on the story start form uses the same client-side JavaScript for both tiers.
- The kids tier character page can reuse the same template as the NSFW tier with adjusted labels and placeholder text.
- No content moderation is needed for character creation — this is a private family app, and the AI's content guidelines handle story generation safety.
- Story templates are NSFW-only at this time, so template integration with kids characters is out of scope.
- Photo upload limits and validation are identical across tiers (same as story start form).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Kids tier users can create and save a character in under 30 seconds (name + description).
- **SC-002**: Selecting a saved character from the kids tier picker pre-fills context instantly (no page reload).
- **SC-003**: 100% of saved kids tier characters appear in both the management page and the story start picker.
- **SC-004**: Kids tier character data persists indefinitely across browser sessions until manually deleted.
- **SC-005**: The NSFW character roster functions identically before and after this change — zero regressions.
- **SC-006**: Kids and NSFW characters are completely isolated — zero cross-tier character visibility.
