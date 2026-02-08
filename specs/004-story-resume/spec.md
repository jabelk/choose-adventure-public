# Feature Specification: Story Resume

**Feature Branch**: `004-story-resume`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Story Resume - Save in-progress stories so users can come back and finish them later. When a user is mid-story and leaves (closes browser, navigates away), their progress should be preserved. When they return to the tier home page, they should see an option to continue their story. In-progress stories should be persisted to disk (not just in-memory sessions) so they survive server restarts. Once a story is completed, it moves to the gallery as before. Users should also be able to explicitly abandon a story to start fresh."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resume an In-Progress Story (Priority: P1)

A user starts a story, plays through a few chapters, then closes their browser or navigates away. When they return to the tier home page later (even after a server restart), they see a prompt offering to continue their story. Clicking "Continue" takes them back to the scene where they left off, with all prior choices and scenes intact.

**Why this priority**: This is the core value of the feature. Without it, users lose all progress when they leave, which discourages playing longer stories.

**Independent Test**: Start a story in `/kids/`, make 2 choices, close the browser tab. Reopen the tier home page — verify a "Continue your story" banner appears with the story title. Click it and verify you're back at the last scene with all previous scenes accessible via "Go Back".

**Acceptance Scenarios**:

1. **Given** a user has an in-progress story with 3 scenes, **When** they close their browser and reopen the tier home page, **Then** they see a banner showing their story title and an option to continue.
2. **Given** a user clicks "Continue" on the resume banner, **When** the page loads, **Then** they see the last scene they were on with all choices and navigation intact.
3. **Given** a user has an in-progress story, **When** the server is restarted and the user revisits the tier home page, **Then** the resume banner still appears and the story is fully intact.

---

### User Story 2 - Abandon a Story and Start Fresh (Priority: P2)

A user has an in-progress story but wants to start over with a new prompt. They can explicitly abandon their current story from the home page. Abandoning removes the in-progress save and returns them to a clean prompt form.

**Why this priority**: Without this, users with a saved story would be stuck — unable to start a new adventure without completing the current one.

**Independent Test**: Start a story, navigate to the home page, verify the resume banner has a "Start Fresh" option. Click it and verify the prompt form is empty and no resume banner appears.

**Acceptance Scenarios**:

1. **Given** a user has an in-progress story, **When** they click "Start Fresh" on the resume banner, **Then** the in-progress save is deleted and the home page shows the normal prompt form with no resume banner.
2. **Given** a user abandons a story, **When** they later visit the home page, **Then** no trace of the abandoned story remains.

---

### User Story 3 - Completed Stories Clear the Save (Priority: P1)

When a user completes a story (reaches an ending), the story is saved to the gallery as before and the in-progress save is automatically removed. The next time the user visits the home page, they see the normal prompt form (no resume banner) and their completed story appears in the gallery.

**Why this priority**: This ensures the existing gallery flow isn't broken and that completing a story cleans up the in-progress save.

**Independent Test**: Resume an in-progress story, play through to the ending. Visit the home page — verify no resume banner. Visit the gallery — verify the completed story appears.

**Acceptance Scenarios**:

1. **Given** a user reaches "The End" of a story, **When** the ending is displayed, **Then** the in-progress save is removed and the story is saved to the gallery.
2. **Given** a user completed their only in-progress story, **When** they visit the tier home page, **Then** no resume banner is shown and the prompt form is ready for a new adventure.

---

### Edge Cases

- What happens if the in-progress save file becomes corrupted? The system gracefully handles it by clearing the save and showing the normal home page with a logged warning.
- What happens if a user starts a new story while one is already in progress? Starting a new story replaces the previous in-progress save (the old one is discarded).
- What happens if multiple browser tabs are open? The most recent action wins — the save file reflects the latest state.
- What if the in-progress story references images that have since been deleted from disk? The scene should show a fallback placeholder, same as the existing image fallback behavior.
- What happens when a user has in-progress stories in multiple tiers? Each tier's save is independent — a kids story doesn't affect the nsfw tier's save.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST persist in-progress story state to disk so it survives browser closure and server restarts.
- **FR-002**: System MUST save the in-progress story automatically after each scene generation (no manual "save" action needed).
- **FR-003**: System MUST display a resume banner on the tier home page when an in-progress story exists for that tier.
- **FR-004**: The resume banner MUST show the story title and provide a "Continue" action.
- **FR-005**: Clicking "Continue" MUST restore the user to their last scene with full navigation history intact.
- **FR-006**: The resume banner MUST provide a "Start Fresh" action to abandon the current story.
- **FR-007**: Abandoning a story MUST delete the in-progress save file and clear the session.
- **FR-008**: When a story reaches its ending, the system MUST remove the in-progress save and save to the gallery (existing behavior preserved).
- **FR-009**: Starting a new story MUST replace any existing in-progress save for that tier.
- **FR-010**: Each tier MUST maintain its own independent in-progress save (tier isolation per Principle I).
- **FR-011**: Corrupted save files MUST be handled gracefully — the system logs a warning and presents the home page as if no save exists.

### Key Entities

- **InProgressSave**: Represents a single in-progress story for a tier. Contains the full story session state (story metadata, all scenes, path history, current scene ID). At most one save per tier exists at any time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can close their browser mid-story and resume from the exact scene they left off, with 100% of prior scenes and choices preserved.
- **SC-002**: In-progress stories survive server restarts with no data loss.
- **SC-003**: Users can abandon a story and start a new one in under 2 clicks from the home page.
- **SC-004**: Completing a story clears the in-progress save and the story appears in the gallery within the same page flow (no manual steps).
- **SC-005**: Tier isolation is maintained — an in-progress story in one tier has no effect on other tiers.

## Assumptions

- Only one in-progress story per tier at a time (users don't need multiple concurrent in-progress stories per tier).
- The in-progress save is tied to the tier, not to a specific browser or user (since this is a personal LAN app with no authentication).
- Auto-save happens server-side after each scene generation — no client-side persistence needed.
- The save format is human-readable (JSON) per Constitution Principle IV.
