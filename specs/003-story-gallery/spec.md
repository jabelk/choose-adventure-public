# Feature Specification: Story Gallery

**Feature Branch**: `003-story-gallery`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Story Gallery - Persistent story archive where all completed adventures are saved and browsable. Each tier gets its own gallery page showing past stories with their title, first image, prompt, and date. Users can click into a past story to read through it scene by scene (read-only, no choices needed since the path is already taken). Stories should be persisted to disk (JSON files) so they survive server restarts. Gallery should be accessible from the tier home page."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Past Stories (Priority: P1) 🎯 MVP

A user visits the gallery page for their tier and sees a list of all previously completed stories. Each story is shown as a card with its title, the first scene's image (or a placeholder if unavailable), the original prompt, and the date it was created. Stories are listed most-recent first. The gallery is accessible via a link on the tier home page.

**Why this priority**: Without browsing, there's no gallery. This is the core feature — seeing what stories exist.

**Independent Test**: Complete a story in the kids tier. Navigate to the gallery from the home page. Verify the completed story appears with its title, image thumbnail, prompt text, and creation date. Restart the server and verify the story still appears.

**Acceptance Scenarios**:

1. **Given** a user has completed one or more stories, **When** they visit the gallery page, **Then** they see all their completed stories displayed as cards with title, first image, prompt, and date, ordered newest first.
2. **Given** the server has been restarted, **When** a user visits the gallery, **Then** all previously saved stories are still visible (persisted to disk).
3. **Given** no stories have been completed yet, **When** a user visits the gallery, **Then** they see a friendly empty state message encouraging them to start an adventure.
4. **Given** a user is in the kids tier, **When** they visit the gallery, **Then** they only see stories from the kids tier (not adult stories).

---

### User Story 2 - Read a Past Story (Priority: P2)

A user clicks on a story card in the gallery and enters a read-only view where they can read through the story scene by scene, following the path that was originally taken. Each scene shows its narrative text and image. Navigation is linear — "Next" and "Previous" buttons step through the scenes in the order they were experienced. No choices are presented since the path is already determined.

**Why this priority**: Browsing titles is useful, but the real value is being able to re-read and relive past adventures.

**Independent Test**: Complete a story with multiple scenes. Open it from the gallery. Verify each scene displays its text and image. Navigate forward and backward through scenes. Verify the reading order matches the original path taken.

**Acceptance Scenarios**:

1. **Given** a user clicks on a story in the gallery, **When** the story reader opens, **Then** the first scene is displayed with its narrative text, image, and a "Next" button.
2. **Given** a user is reading a multi-scene story, **When** they click "Next", **Then** the next scene in the original path is displayed.
3. **Given** a user is on a scene beyond the first, **When** they click "Previous", **Then** the prior scene is displayed.
4. **Given** a user reaches the final scene, **When** they view it, **Then** there is no "Next" button, and a "Back to Gallery" link is shown.

---

### User Story 3 - Auto-Save Completed Stories (Priority: P1)

When a story reaches its ending scene (is_ending=true), the system automatically saves the complete story — including all scenes in the taken path, images, metadata, and the tier — to persistent storage. No manual action is needed from the user. Stories that are abandoned (not finished) are not saved to the gallery.

**Why this priority**: Without auto-save, there's nothing to show in the gallery. This is a prerequisite for US1.

**Independent Test**: Start a story, play through to the ending. Verify a file is created on disk containing the full story data. Start another story and abandon it (close the tab). Verify no file is created for the abandoned story.

**Acceptance Scenarios**:

1. **Given** a user reaches an ending scene, **When** the ending is displayed, **Then** the complete story is automatically saved to persistent storage.
2. **Given** a story is saved, **When** the save file is inspected, **Then** it contains: story metadata (title, prompt, tier, date), all scenes in the path taken (text, image URLs, depth), and the order of scenes.
3. **Given** a user starts a story but navigates away before finishing, **When** the gallery is checked, **Then** the incomplete story does not appear.

---

### Edge Cases

- What happens when a story's image failed to generate? The gallery card shows a placeholder, and the reader shows the fallback "Image unavailable" state.
- What happens when the story data file is corrupted or unreadable? The system skips it and logs a warning, showing only valid stories in the gallery.
- What happens when many stories accumulate (50+)? The gallery paginates or lazy-loads to keep the page responsive.
- What happens if two stories finish saving at the same time? Each story saves to its own file (named by unique ID), so no conflicts occur.
- What happens when the images directory is cleared but story data remains? Stories still appear in the gallery; images show the fallback state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically save a completed story to disk when the user reaches an ending scene.
- **FR-002**: System MUST persist stories as individual files on disk, each containing all story metadata and scene data for the path taken.
- **FR-003**: System MUST load all saved stories for a given tier when the gallery page is requested.
- **FR-004**: System MUST display gallery stories in reverse chronological order (newest first).
- **FR-005**: System MUST scope the gallery by tier — kids gallery shows only kids stories, adult gallery shows only adult stories.
- **FR-006**: System MUST provide a read-only story reader that displays scenes sequentially in the order originally taken.
- **FR-007**: System MUST show a gallery link on each tier's home page.
- **FR-008**: System MUST show a friendly empty state when no stories exist in a tier's gallery.
- **FR-009**: System MUST gracefully handle corrupted or unreadable story files by skipping them.
- **FR-010**: System MUST only save stories that have reached an ending (is_ending=true); incomplete/abandoned stories are not saved.

### Key Entities

- **Saved Story**: A completed adventure persisted to disk. Contains: unique ID, title, original prompt, tier name, creation date, and an ordered list of scenes from the path taken.
- **Saved Scene**: A scene within a saved story. Contains: narrative text, image URL (if available), image prompt, depth/chapter number. No choices are stored since the path is determined.
- **Gallery**: A per-tier collection of all saved stories, loaded from disk on request.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Completed stories appear in the gallery within 2 seconds of reaching the ending scene.
- **SC-002**: Gallery page loads and displays all saved stories within 2 seconds for up to 100 stories.
- **SC-003**: All saved stories survive server restarts with zero data loss.
- **SC-004**: Story reader allows users to navigate through all scenes of a past story in the correct original order.
- **SC-005**: Gallery is fully tier-isolated — no cross-tier story leakage.

## Assumptions

- Stories are saved only when they reach an ending; there is no manual "save" button.
- Each story is saved as its own file, named by the story's unique ID, to avoid write conflicts.
- The gallery loads stories by reading files from disk on each request (no caching layer needed for a personal/family app).
- Image files already exist on disk in `static/images/` from the original generation; saved stories reference these paths.
- No authentication is needed — this is a personal LAN-only app.
- No delete or edit functionality for saved stories in this version (can be added later).
- Pagination is deferred; a simple scrollable list is sufficient for the expected volume (family use).
