# Feature Specification: Story Sequel Mode

**Feature Branch**: `027-story-sequel-mode`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Story Continuation / Sequel Mode — Pick a completed gallery story and continue it from the ending. Same characters, same world, new plot thread. Load the last scene as context, carry over character_name/description/kinks, and generate a new opening scene that references the prior story's ending. NSFW tier primarily but could work for kids too."

## User Scenarios & Testing

### User Story 1 - Continue a Completed Story (Priority: P1)

A user finishes a story and wants more. From the gallery reader page of a completed story, they click "Continue Story" to start a sequel. The system loads the original story's ending scene as context, carries over all character details (name, description, kinks, roster characters), and generates a new opening scene that picks up where the last story left off. The sequel becomes its own new active story session.

**Why this priority**: This is the core feature — without the ability to launch a sequel from a completed story, nothing else matters.

**Independent Test**: Open a completed story in the gallery reader, click "Continue Story," verify a new story session begins with the original story's ending referenced in the opening scene and all character fields carried over.

**Acceptance Scenarios**:

1. **Given** a completed story in the gallery, **When** the user clicks "Continue Story" on the reader page, **Then** a new story session starts with an opening scene that references the prior story's ending.
2. **Given** a completed story with a named character (e.g., "Margot Ellis" with physical description), **When** the user starts a sequel, **Then** the character name and description are carried over to the new story.
3. **Given** a completed story with kinks/themes selected, **When** the user starts a sequel, **Then** the same kinks and themes are applied to the sequel.
4. **Given** a completed story with roster characters, **When** the user starts a sequel, **Then** the roster character IDs are preserved and their context is rebuilt in the sequel.
5. **Given** a completed story, **When** the user starts a sequel, **Then** the sequel uses the same AI model and image model as the original story.

---

### User Story 2 - Sequel Customization Before Launch (Priority: P2)

Before the sequel begins generating, the user can optionally adjust settings — change the story length, toggle different kinks, or modify the prompt direction. A brief customization form appears between clicking "Continue Story" and the first scene generating, pre-filled with the original story's settings.

**Why this priority**: Without customization, sequels are locked into the original story's exact settings. Users may want a longer sequel, different themes, or a specific plot direction. However, the feature still works without this — P1 alone delivers a functional sequel with inherited settings.

**Independent Test**: Click "Continue Story" on a gallery story, verify a customization form appears pre-filled with the original story's settings, modify settings, and confirm the sequel uses the updated settings.

**Acceptance Scenarios**:

1. **Given** the user clicks "Continue Story," **When** the customization form appears, **Then** it is pre-filled with the original story's length, kinks, character details, and model selections.
2. **Given** the customization form, **When** the user changes the story length from "short" to "long," **Then** the sequel starts with the updated target depth.
3. **Given** the customization form, **When** the user adds a prompt hint (e.g., "This time they go to Paris"), **Then** the AI incorporates that direction into the sequel's opening scene.
4. **Given** the customization form, **When** the user submits without changes, **Then** the sequel starts with all original settings preserved.

---

### User Story 3 - Sequel Chain Visibility (Priority: P3)

Users can see which stories are sequels and trace the chain. The gallery and reader pages indicate when a story is a sequel, linking back to the original. Sequel chains are visually connected so users can follow a multi-part saga.

**Why this priority**: This is a navigation and discoverability enhancement. Sequels work fine without chain visibility — this just makes the experience more polished.

**Independent Test**: Create a sequel from a story, verify the sequel's gallery entry and reader page show a "Sequel of: [Original Title]" link, and verify the original story shows "Continued in: [Sequel Title]."

**Acceptance Scenarios**:

1. **Given** a sequel story in the gallery, **When** the user views its reader page, **Then** a link to the original story is displayed (e.g., "Sequel of: [Original Title]").
2. **Given** an original story that has been continued, **When** the user views its reader page, **Then** a link to the sequel is displayed (e.g., "Continued in: [Sequel Title]").
3. **Given** a chain of 3+ sequels, **When** the user views any story in the chain, **Then** they can navigate forward and backward through the full chain.

---

### Edge Cases

- What happens when the user tries to continue a story that has been deleted from the gallery? The system shows a friendly error and redirects to the gallery.
- What happens when the original story's ending scene is very long? The system uses only the last scene's content as context, not the entire story history, to avoid exceeding AI context limits.
- What happens when a sequel is started but abandoned? It behaves like any other abandoned story — can be resumed or started fresh from the home page.
- What happens when a user tries to continue a story from a different tier? Sequels MUST stay within the same tier as the original story.
- What happens when the original story used a roster character that has since been deleted? The character name and description (already saved on the story) are still carried over, but the roster character ID is dropped.

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a "Continue Story" button on the gallery reader page for completed stories.
- **FR-002**: System MUST create a new story session when the user initiates a sequel, carrying over: character name, character description, kinks, conflict type, writing style, roster character IDs, art style, AI model, and image model from the original story.
- **FR-003**: System MUST include the original story's final scene content as context when generating the sequel's opening scene, with an instruction to the AI to continue from where the story left off.
- **FR-004**: System MUST store a reference to the original story's ID on the sequel (parent_story_id) so the relationship can be traced.
- **FR-005**: System MUST work on both kids and NSFW tiers — the "Continue Story" button appears on all completed stories regardless of tier.
- **FR-006**: System MUST apply the same tier-specific content guidelines and image style to the sequel as would apply to any new story in that tier.
- **FR-007**: System MUST prevent cross-tier sequels — a kids story can only be continued as a kids story.
- **FR-008**: (P2) System MUST display a pre-filled customization form before generating the sequel, allowing the user to adjust length, kinks, prompt direction, and other settings.
- **FR-009**: (P2) System MUST accept an optional "sequel prompt" — a short text hint describing the direction for the sequel — which is appended to the AI's context alongside the original ending.
- **FR-010**: (P3) System MUST store and display sequel chain relationships — original stories link forward to their sequel(s), and sequels link back to their parent story.
- **FR-011**: (P3) The gallery reader page MUST show sequel chain navigation links when a story is part of a chain.

### Key Entities

- **SavedStory** (existing): Extended with an optional parent_story_id field linking to the original story, and an optional sequel_story_ids list for forward references.
- **Story** (existing, active session): Extended with an optional parent_story_id field and optional sequel_context field (the original story's ending scene content used as AI context).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can launch a sequel from any completed gallery story in under 3 clicks (1 click for P1, 2 clicks for P2 with customization).
- **SC-002**: 100% of character details (name, description, kinks, roster characters) from the original story are preserved in the sequel.
- **SC-003**: The sequel's opening scene references or acknowledges events from the original story's ending at least 90% of the time.
- **SC-004**: Sequel chain navigation (P3) allows users to traverse the full chain from any story in under 2 clicks per hop.

## Assumptions

- Sequels inherit the original story's settings by default but are otherwise independent stories — they have their own story_id, their own scenes, and are saved independently to the gallery.
- The original story is not modified when a sequel is created (except optionally adding a forward reference in P3).
- Only the final scene's content is passed as sequel context to the AI — not the entire story history — to keep context manageable.
- The "Continue Story" button does not appear on stories that are still in progress (only completed/archived stories in the gallery).
- The sequel prompt hint (P2) is optional — if left blank, the AI generates a natural continuation.
- Bedtime mode and video mode settings from the original story are NOT automatically inherited — these are session-level toggles the user should opt into fresh.

## Out of Scope

- Merging or combining multiple stories into one.
- Continuing from a mid-story scene (branch point) — sequels always continue from the ending.
- Collaborative sequel creation (multiple users contributing to a sequel chain).
- Automatic sequel suggestions or AI-generated sequel prompts.
