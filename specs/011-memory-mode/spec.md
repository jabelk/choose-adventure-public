# Feature Specification: Memory Mode

**Feature Branch**: `011-memory-mode`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Toggleable user profiles per tier that shape story and image generation. Users can create profiles with preferences (themes, art styles, tone, favorite story elements) and character definitions (people who can appear in stories). When memory mode is toggled on at story start, preferences are injected into AI prompts to influence story content, choices, and image style. Profiles are strictly isolated by tier. Characters can reference other profiles within the same tier (e.g., two sisters can appear in each other's stories)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage a Profile (Priority: P1)

A user navigates to a profile management page within their tier. They create a new profile by entering a display name and setting preferences: favorite themes (e.g., "dinosaurs", "space"), preferred art style (e.g., "watercolor", "pixel art"), tone (e.g., "silly and lighthearted"), and favorite story elements (e.g., "talking animals", "treasure hunts"). They can edit or delete the profile at any time. Each tier has its own separate set of profiles — profiles created in the kids tier are never visible from the adult tier and vice versa.

**Why this priority**: Without profiles, there is nothing to toggle on. This is the foundational data layer that all other stories depend on.

**Independent Test**: Navigate to the profile page for a tier, create a profile with preferences, verify it persists across page refreshes, edit it, and confirm changes are saved.

**Acceptance Scenarios**:

1. **Given** a user is on the kids tier home page, **When** they navigate to the profiles page, **Then** they see a list of existing profiles for the kids tier only (no adult profiles visible)
2. **Given** a user is on the profiles page, **When** they create a new profile with a name and preferences, **Then** the profile is saved and appears in the profile list
3. **Given** a profile exists, **When** the user edits preferences (e.g., changes art style from "watercolor" to "cartoon"), **Then** the updated preferences are saved and reflected immediately
4. **Given** a profile exists, **When** the user deletes the profile, **Then** it is removed from the list and no longer available for selection
5. **Given** profiles exist in both tiers, **When** a user views profiles in the kids tier, **Then** they see zero adult-tier profiles

---

### User Story 2 - Toggle Memory Mode at Story Start (Priority: P2)

When starting a new story, a user sees a "Memory Mode" toggle on the home page. When toggled on, a dropdown appears allowing them to select one of their profiles for this tier. The selected profile's preferences are then used to influence the AI's story generation, choice creation, and image style for this story. When toggled off (the default), the story generates without any profile influence, exactly as it does today.

**Why this priority**: This is the core feature — connecting profiles to story generation. Without the toggle, profiles exist but have no effect.

**Independent Test**: Create a profile with strong preferences (e.g., "everything should involve pirates"), start a story with memory mode on, verify the generated story reflects pirate themes. Start another story with memory mode off using the same prompt, verify no pirate influence.

**Acceptance Scenarios**:

1. **Given** a user has at least one profile in this tier, **When** they view the home page, **Then** they see a "Memory Mode" toggle (off by default)
2. **Given** no profiles exist for this tier, **When** a user views the home page, **Then** the Memory Mode toggle is hidden
3. **Given** memory mode is toggled on, **When** the user selects a profile and starts a story, **Then** the story content, choices, and image style are influenced by the profile's preferences
4. **Given** memory mode is toggled off, **When** the user starts a story, **Then** the story generates identically to current behavior (no profile influence)
5. **Given** memory mode is on and a profile is selected, **When** the story continues across multiple scenes, **Then** the profile preferences continue to influence all subsequent scene generation

---

### User Story 3 - Add Characters to a Profile (Priority: P3)

A user adds character definitions to their profile. A character has a name, a brief description (e.g., "Lily, age 5, loves dinosaurs and has a pet cat named Whiskers"), and optionally references another profile in the same tier (e.g., "Lily's sister Rose" links to Rose's profile). When memory mode is active, these characters can appear in generated stories. Characters from profiles in the same tier can reference each other, enabling cross-profile story connections (e.g., two sisters appearing in each other's adventures).

**Why this priority**: Characters add richness and personalization beyond basic preference settings. This builds on top of US1 (profiles) and US2 (toggle), making stories feel truly personal.

**Independent Test**: Add a character "Lily, loves dinosaurs" to a kids profile, start a story with memory mode on, verify the generated story includes or references Lily.

**Acceptance Scenarios**:

1. **Given** a profile exists, **When** the user adds a character with a name and description, **Then** the character appears in the profile's character list
2. **Given** a character exists, **When** the user edits the character's description, **Then** changes are saved
3. **Given** two profiles exist in the kids tier (one for each daughter), **When** a character in Profile A references Profile B, **Then** when Profile A is active, the referenced profile's characters are included in story generation context
4. **Given** a character in a kids profile references another kids profile, **When** the user views this from the adult tier, **Then** the cross-reference is not visible and has no effect
5. **Given** memory mode is active with a profile that has characters, **When** a story is generated, **Then** the characters appear naturally in the story content

---

### Edge Cases

- What happens when a user deletes a profile that is referenced by characters in other profiles? The reference is removed gracefully — the character definition remains but the cross-link is broken with no error shown to the user.
- What happens when memory mode is on but the selected profile has no preferences set (empty)? The story generates normally as if memory mode were off, since there is nothing to inject.
- What happens when preferences conflict with the tier's content guidelines (e.g., a kids profile with a "horror" theme)? The tier's content guidelines always take precedence — preferences influence tone and theme within the bounds of what the tier allows.
- What happens when a profile has many characters (e.g., 10+)? The system includes the most relevant characters in the prompt context, with a reasonable limit to avoid exceeding prompt size constraints. A maximum of 10 characters per profile is enforced.
- What happens when the user switches profiles mid-story? Profile selection is locked at story start. Changing profiles requires starting a new story.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create, edit, and delete profiles within a tier
- **FR-002**: System MUST store profiles persistently on disk so they survive server restarts
- **FR-003**: Profiles MUST be strictly isolated by tier — a profile created in the kids tier MUST NOT be visible, accessible, or referenced from the adult tier
- **FR-004**: Each profile MUST support the following preference fields: display name, themes (list), art style (free text), tone (free text), and favorite story elements (list)
- **FR-005**: System MUST provide a "Memory Mode" toggle on the home page, defaulting to off
- **FR-006**: When memory mode is on, the user MUST be able to select a profile from a dropdown of profiles belonging to the current tier
- **FR-007**: When memory mode is active, the selected profile's preferences MUST be injected into story generation prompts to influence content, choices, and image style
- **FR-008**: When memory mode is off, story generation MUST behave identically to current behavior (no profile influence)
- **FR-009**: The Memory Mode toggle MUST be hidden when no profiles exist for the current tier
- **FR-010**: Users MUST be able to add, edit, and remove characters from a profile
- **FR-011**: Each character MUST have a name (required) and description (required), with an optional cross-reference to another profile in the same tier
- **FR-012**: When a character references another profile, that referenced profile's characters MUST be included in the story generation context when memory mode is active
- **FR-013**: Cross-profile references MUST only work within the same tier — a kids character MUST NOT reference an adult profile
- **FR-014**: Each profile MUST support a maximum of 10 characters
- **FR-015**: Profile preferences MUST NOT override the tier's content guidelines — tier safety rules always take precedence
- **FR-016**: Profile selection MUST be locked at story start and persist for the entire story session
- **FR-017**: The profile management page MUST be accessible via a link from the tier's home page

### Key Entities

- **Profile**: A named collection of preferences and characters belonging to a specific tier. Has a display name, tier association, preference fields (themes, art style, tone, story elements), and a list of characters.
- **Character**: A named person or entity that can appear in stories. Belongs to a profile. Has a name, description, and an optional reference to another profile in the same tier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a complete profile (name, preferences, at least one character) in under 2 minutes
- **SC-002**: Stories generated with memory mode on demonstrably reflect the profile's preferences (themes, tone, art style) compared to stories generated with memory mode off using the same prompt
- **SC-003**: Profile data persists across server restarts with zero data loss
- **SC-004**: Tier isolation is absolute — there is no pathway through the user interface or direct URL access to view profiles from another tier
- **SC-005**: Characters defined in a profile appear naturally in generated stories when memory mode is active

## Assumptions

- This is a single-user (family) app on a LAN — there is no authentication system. Profile management is open to whoever accesses the tier.
- Profiles are stored as files on disk (consistent with the existing gallery persistence pattern), not in an external database.
- The number of profiles per tier is expected to be small (under 20). No pagination is needed.
- Preference fields are free-form text and lists — the system does not enforce a fixed vocabulary of themes or art styles.
- The existing `content_guidelines` and `image_style` fields in the tier configuration continue to serve as the baseline. Profile preferences augment but never contradict them.

## Out of Scope

- Automatic preference learning from user choices (future feature — the system does not analyze past story interactions to infer preferences)
- Photo/image uploads for character portraits (future photo import feature)
- Profile import/export
- Multi-user authentication or profile ownership
