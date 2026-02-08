# Feature Specification: Direct Image Upload

**Feature Branch**: `019-direct-image-upload`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Add a Reference Photos upload field to the story start form so users can upload 1-3 images directly without needing a profile. Uploaded photos get passed as reference_images to the image generator for every scene."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Reference Photos at Story Start (Priority: P1)

As a user, I want to upload 1-3 photos directly on the story start form so that the AI image generator incorporates those faces/characters into every scene's generated image — without having to create a profile first.

The user sees a "Reference Photos" section on the story creation form with a file input area. They can select or drag-and-drop up to 3 images (JPEG or PNG). Thumbnails of selected images appear below the input. When they click "Start Adventure," the uploaded photos are saved temporarily and passed to the image generator as reference images for every scene throughout the story.

**Why this priority**: This is the core feature — a direct, zero-friction way to personalize story images. Without this, users must go through the multi-step profile/character workflow just to get their face in the images.

**Independent Test**: Can be tested by uploading a photo on the story start form, generating a story, and verifying the generated images incorporate elements from the uploaded photo.

**Acceptance Scenarios**:

1. **Given** the user is on the story start form, **When** they select 1 photo and start the story, **Then** the generated scene images incorporate the uploaded photo as a reference.
2. **Given** the user is on the story start form, **When** they select 3 photos, **Then** thumbnails of all 3 appear on the form and all are used as references for image generation.
3. **Given** the user selects photos, **When** they start the story without enabling memory mode, **Then** the direct uploads are used (memory mode and direct upload are independent).
4. **Given** the user does NOT upload any photos, **When** they start the story, **Then** image generation works normally without reference images (no regression).

---

### User Story 2 - Thumbnail Preview Before Starting (Priority: P1)

As a user, I want to see thumbnail previews of my selected photos before starting the story, so I can confirm I picked the right images and remove any I don't want.

When photos are selected (via file picker or drag-and-drop), small thumbnail previews appear in the form. Each thumbnail has a remove button (X) to deselect it. The thumbnails update live as files are added or removed.

**Why this priority**: Without previews, users can't verify their selection, leading to wasted story generations with wrong photos. This is essential for the upload UX.

**Independent Test**: Can be tested by selecting files, verifying thumbnails appear, clicking remove on one, and confirming it's removed from the selection.

**Acceptance Scenarios**:

1. **Given** the user selects 2 photos, **When** the files load, **Then** 2 thumbnail previews appear in the form showing the actual images.
2. **Given** 3 thumbnails are shown, **When** the user clicks the remove button on one, **Then** that thumbnail disappears and only 2 photos will be uploaded.
3. **Given** the user has already selected 3 photos, **When** they try to add a 4th, **Then** they see a message that the maximum is 3.

---

### User Story 3 - Cleanup Temporary Files (Priority: P2)

As the system, temporary uploaded photos should be cleaned up when the story session ends or is abandoned, so they don't accumulate on disk.

Uploaded reference photos are saved to a temporary directory tied to the story session. When the story completes (saved to gallery), is abandoned (user starts a new story), or the progress is deleted via admin, the temporary files are removed.

**Why this priority**: Important for disk hygiene but not user-facing. Users don't see this; it just prevents storage bloat over time.

**Independent Test**: Can be tested by uploading photos, completing or abandoning a story, and verifying the temporary files are removed from disk.

**Acceptance Scenarios**:

1. **Given** a story with uploaded photos is completed, **When** it saves to gallery, **Then** the temporary photo files are removed.
2. **Given** a story with uploaded photos is abandoned (user starts fresh), **When** the old session is cleared, **Then** the temporary photo files are removed.
3. **Given** old temporary files exist from previous sessions, **When** the admin runs orphan cleanup, **Then** temporary photo directories with no matching active session are cleaned up.

---

### Edge Cases

- What happens when the user uploads a file that is not an image (e.g., a PDF)? The form should only accept JPEG and PNG files, rejecting other types with a clear message.
- What happens when the uploaded image is very large (e.g., 20MB)? Images should be accepted up to a reasonable size (10MB per file) with an error message for oversized files.
- What happens when both memory mode (with profile photos) and direct upload are used together? Direct uploads take priority — they replace profile photos as the reference images for this story.
- What happens when the user selects photos but the chosen image model doesn't support reference images (e.g., gpt-image-1-mini)? The photos are silently ignored and image generation proceeds normally without references.
- What happens on mobile devices where drag-and-drop isn't available? The file input button works as a tap-to-select fallback, which is the native mobile behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The story start form MUST include a "Reference Photos" upload area that accepts 1-3 image files (JPEG or PNG).
- **FR-002**: The upload area MUST support both click-to-browse and drag-and-drop file selection.
- **FR-003**: Selected photos MUST display as thumbnail previews in the form before submission.
- **FR-004**: Each thumbnail MUST have a remove button that deselects that photo.
- **FR-005**: The system MUST enforce a maximum of 3 photos per story and a maximum of 10MB per file.
- **FR-006**: Uploaded photos MUST be saved to temporary storage and passed as reference images to the image generator for every scene in the story.
- **FR-007**: Direct photo uploads MUST work independently of the profile/memory mode system.
- **FR-008**: When both direct uploads and memory mode profile photos exist, direct uploads MUST take priority.
- **FR-009**: Temporary photo files MUST be cleaned up when the story session ends (completion, abandonment, or admin deletion).
- **FR-010**: The feature MUST NOT change the behavior of stories started without reference photos.
- **FR-011**: The form MUST change its encoding to support file uploads (multipart form data) only when photos are selected, preserving existing form behavior when no photos are chosen.

### Key Entities

- **Reference Photo**: A user-uploaded image file (JPEG/PNG, max 10MB) associated with a story session. Stored temporarily on disk for the duration of the session.
- **Photo Set**: A collection of 1-3 reference photos tied to a single story session. Passed to the image generator for every scene.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload reference photos and start a story in under 30 seconds (no profile creation required).
- **SC-002**: Uploaded photos are reflected in the generated scene images for 100% of scenes in the story.
- **SC-003**: Temporary files are cleaned up within 1 session cycle (story completion or abandonment) — no orphaned uploads persist indefinitely.
- **SC-004**: The feature works on both desktop (drag-and-drop) and mobile (tap-to-select) browsers.
- **SC-005**: Stories started without reference photos behave identically to before this feature was added (zero regression).

## Assumptions

- The existing image generation services already accept `reference_images` parameter — no changes needed to the image generation pipeline itself.
- The form currently uses `application/x-www-form-urlencoded` encoding; it will need to switch to `multipart/form-data` when files are attached.
- Mobile browsers support the file input element natively; no special mobile handling is needed beyond standard HTML file inputs.
- The admin portal's orphan cleanup (feature 018) should also clean up orphaned temporary photo directories.
- Thumbnail previews are generated client-side using the browser's FileReader API — no server-side thumbnail generation needed.

## Scope Boundaries

### In Scope

- File upload UI with drag-and-drop and thumbnail previews on the story start form
- Temporary storage of uploaded photos for the story session duration
- Passing uploaded photos as reference images to the image generator
- Cleanup of temporary files on session end
- Coexistence with (but independence from) the profile/memory mode system

### Out of Scope

- Editing or cropping uploaded photos before use
- Persisting uploaded photos across sessions (they're one-time use per story)
- Using uploaded photos for text/story generation (only for image generation)
- Adding reference photo upload to the mid-story choice flow (only at story start)
