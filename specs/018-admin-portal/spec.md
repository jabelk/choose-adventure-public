# Feature Specification: Admin Portal

**Feature Branch**: `018-admin-portal`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Admin Portal - Add an /admin page for managing the app. Features: (1) List all stories across all tiers with delete buttons, (2) Bulk cleanup of orphaned images/videos, (3) Storage usage summary."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Storage Dashboard (Priority: P1)

As the app owner, I want to see an overview of storage usage so I can understand how much disk space my stories, images, and videos are consuming.

The admin visits `/admin` and sees a dashboard showing:
- Total number of saved stories (completed), grouped by tier
- Total number of in-progress stories
- Total number of image files on disk
- Total number of video files on disk
- Total disk usage for each storage directory (data/, static/images/, static/videos/)

**Why this priority**: Provides immediate visibility into the system's state. Read-only, zero risk, and the foundation that every other admin action builds on.

**Independent Test**: Can be fully tested by navigating to `/admin` and verifying the counts and sizes match the files on disk.

**Acceptance Scenarios**:

1. **Given** the app has 5 saved stories, 3 in-progress saves, 10 images, and 2 videos, **When** the admin visits `/admin`, **Then** they see counts of 5 stories, 3 in-progress, 10 images, 2 videos with accurate disk sizes.
2. **Given** the storage directories are empty, **When** the admin visits `/admin`, **Then** they see all counts as 0 and all sizes as 0 bytes.

---

### User Story 2 - Story Management (Priority: P1)

As the app owner, I want to see all stories across all tiers in a single list and be able to delete individual stories, including their associated images and videos.

The admin sees a table of all saved stories showing: title, tier, model used, creation date, and number of scenes. Each row has a delete button. Clicking delete shows a confirmation dialog. Confirming deletes the story JSON file and all image and video files associated with that story's scenes.

**Why this priority**: Core admin functionality — without the ability to delete stories, there is no way to reclaim storage or remove unwanted content from the GUI.

**Independent Test**: Can be tested by creating a test story, visiting the admin page, verifying it appears in the list, deleting it, and confirming the story JSON and associated image/video files are removed from disk.

**Acceptance Scenarios**:

1. **Given** stories exist across multiple tiers, **When** the admin visits the admin page, **Then** all stories from all tiers appear in a single unified list.
2. **Given** a story with 3 scenes that each have an image, **When** the admin deletes that story, **Then** the story JSON file is deleted and all 3 associated image files are deleted.
3. **Given** a story with video files, **When** the admin deletes that story, **Then** the associated video files are also deleted.
4. **Given** the admin clicks delete, **When** the confirmation dialog appears, **Then** the admin can cancel without any data being deleted.

---

### User Story 3 - Orphan Cleanup (Priority: P2)

As the app owner, I want to find and remove orphaned files — images or videos on disk that are not referenced by any saved story — so I can reclaim wasted storage.

The admin page shows a count of orphaned image files and orphaned video files. An "orphan" is a file in `static/images/` or `static/videos/` whose filename (without extension) does not match any scene ID in any saved story. A "Clean Up Orphans" button deletes all orphaned files after confirmation.

**Why this priority**: Orphaned files accumulate from deleted stories, failed generations, or in-progress stories that were abandoned. This is important but less urgent than basic story management.

**Independent Test**: Can be tested by placing a random-named .png in the images directory, visiting admin, verifying it shows as orphaned, running cleanup, and confirming the file is removed while legitimate story images remain.

**Acceptance Scenarios**:

1. **Given** 2 image files exist that do not match any story scene, **When** the admin views the admin page, **Then** it shows "2 orphaned images" with the total size.
2. **Given** orphaned files are identified, **When** the admin clicks "Clean Up Orphans" and confirms, **Then** all orphaned files are deleted and the page refreshes showing 0 orphans.
3. **Given** no orphaned files exist, **When** the admin views the admin page, **Then** the orphan section shows "No orphaned files" and the cleanup button is disabled or hidden.
4. **Given** an in-progress story has images on disk, **When** calculating orphans, **Then** those images are NOT counted as orphans (in-progress scene IDs are included in the valid set).

---

### User Story 4 - In-Progress Story Management (Priority: P2)

As the app owner, I want to see and delete in-progress story saves so I can clear stale sessions.

The admin page shows a list of in-progress saves (one per tier) with the story prompt, tier name, number of scenes generated so far, and a delete button.

**Why this priority**: Complementary to story management but lower priority since in-progress files are small and self-replacing (each tier only has one at a time).

**Independent Test**: Can be tested by starting a story without completing it, visiting admin, verifying the in-progress entry appears, deleting it, and confirming the progress file is removed.

**Acceptance Scenarios**:

1. **Given** an in-progress story exists for the "kids" tier, **When** the admin views the admin page, **Then** it appears in the in-progress section with tier name, prompt excerpt, and scene count.
2. **Given** the admin deletes an in-progress save, **When** confirming the action, **Then** the progress file is removed from disk.

---

### Edge Cases

- What happens when a story JSON file is corrupted or unparseable? It should be listed with an "error" indicator and still be deletable.
- What happens when an image file referenced by a story doesn't exist on disk? The story should still display normally; the missing file is simply not counted in storage.
- What happens when the admin tries to delete a story while a background image/video generation is in progress for it? The delete should proceed; the background task will fail gracefully when it tries to write to a now-deleted path.
- What happens when the data directories don't exist yet? The admin page should handle this gracefully, showing 0 for all counts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST serve an admin page at the `/admin` URL path, independent of any tier.
- **FR-002**: System MUST display a storage summary showing file counts and total disk usage for stories, images, and videos.
- **FR-003**: System MUST list all saved stories from all tiers in a single unified table, showing title, tier, model, creation date, and scene count.
- **FR-004**: System MUST provide a delete action for each story that removes the story JSON and all associated image and video files from disk.
- **FR-005**: System MUST display a confirmation dialog before executing any delete or cleanup action.
- **FR-006**: System MUST identify orphaned files (images/videos not referenced by any saved or in-progress story) and display their count and total size.
- **FR-007**: System MUST provide a bulk cleanup action that deletes all orphaned files.
- **FR-008**: System MUST list in-progress story saves with tier name, prompt excerpt, and scene count, with individual delete actions.
- **FR-009**: System MUST NOT require any authentication to access the admin page (LAN-only personal app).
- **FR-010**: System MUST handle corrupted story files gracefully — display them as errored entries that can still be deleted.
- **FR-011**: System MUST treat images/videos referenced by in-progress stories as non-orphaned during orphan detection.

### Key Entities

- **Storage Summary**: Aggregate counts and sizes for each storage category (stories, images, videos, in-progress saves).
- **Story Entry**: A saved story with metadata (title, tier, model, dates, scene count) and references to associated media files.
- **In-Progress Entry**: A tier's current in-progress save with prompt excerpt and scene count.
- **Orphaned File**: An image or video file on disk whose scene ID does not appear in any saved or in-progress story.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin can view the full storage dashboard within 3 seconds of navigating to `/admin`, even with 100+ stories on disk.
- **SC-002**: Admin can delete a story and all its associated files in a single action (one click + one confirmation).
- **SC-003**: Orphan detection correctly identifies 100% of files not referenced by any story or in-progress save.
- **SC-004**: After cleanup, the orphaned file count drops to zero.
- **SC-005**: All destructive actions require explicit confirmation — no data is deleted without the admin confirming first.

## Assumptions

- No authentication is needed; the app runs on a private LAN and only the owner accesses it.
- The admin page uses the same visual styling as the rest of the app (base template, CSS custom properties).
- Story files follow the existing naming convention: `{story_id}.json` in `data/stories/`.
- Image files follow the existing naming convention: `{scene_id}.png` in `static/images/`.
- Video files follow the existing naming convention: `{scene_id}.mp4` in `static/videos/`.
- In-progress saves follow the existing naming convention: `{tier_name}.json` in `data/progress/`.

## Scope Boundaries

### In Scope

- Storage dashboard with counts and sizes
- Story listing and deletion (including associated media)
- Orphan detection and bulk cleanup
- In-progress save listing and deletion
- Confirmation dialogs for all destructive actions

### Out of Scope

- User authentication or access control
- Story editing or modification
- Image/video regeneration
- Log viewing
- Configuration management (API keys, settings)
- Backup or export functionality
