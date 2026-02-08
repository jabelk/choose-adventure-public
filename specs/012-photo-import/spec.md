# Feature Specification: Photo Import

**Feature Branch**: `012-photo-import`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Photo Import - Users can upload photos of real people (e.g., their children) to a profile, and when memory mode is active those photos are used as reference images for AI image generation so the characters in the story visually resemble the real people."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload a Reference Photo for a Character (Priority: P1)

A user navigates to a character within a profile and uploads a photo of the real person that character represents (e.g., their daughter). The photo is stored locally and associated with that character. The user can see a thumbnail preview of the uploaded photo on the character card and can replace or remove it at any time.

**Why this priority**: Without the ability to upload and associate photos with characters, none of the downstream image generation features can work. This is the foundational data entry point.

**Independent Test**: Navigate to a profile's edit page, add or edit a character, upload a JPEG or PNG photo, verify the thumbnail appears on the character card. Refresh the page and confirm the photo persists. Replace the photo with a new one and verify the old one is removed. Delete the photo and confirm the character still works without one.

**Acceptance Scenarios**:

1. **Given** a profile with at least one character, **When** the user uploads a JPEG photo for that character, **Then** the photo is saved and a thumbnail preview appears on the character card.
2. **Given** a character with an existing photo, **When** the user uploads a new photo, **Then** the old photo is replaced and the new thumbnail is displayed.
3. **Given** a character with an existing photo, **When** the user clicks "Remove Photo", **Then** the photo is deleted and the character card shows no image.
4. **Given** a user attempts to upload a file that is not JPEG or PNG, **When** the upload is submitted, **Then** the system rejects it with a clear error message.

---

### User Story 2 - AI Image Generation Uses Reference Photos (Priority: P2)

When memory mode is toggled on and a profile with photo-linked characters is selected, the reference photos are sent along with the image generation request. The AI image generator uses these photos to produce story images where the characters visually resemble the real people in the uploaded photos.

**Why this priority**: This is the core value of the feature — making story images personalized. It depends on US1 (photos must be uploaded first) and the existing memory mode infrastructure.

**Independent Test**: Upload a reference photo for a character, start a story with memory mode on using that profile, verify that generated story images visually incorporate the likeness from the reference photo. Start a story with memory mode off and verify no reference photos are used.

**Acceptance Scenarios**:

1. **Given** a profile with a character that has a reference photo and memory mode is on, **When** a story scene is generated, **Then** the image generation request includes the reference photo so the AI can render a character resembling the real person.
2. **Given** a profile with characters where some have photos and some do not, **When** a story scene is generated, **Then** only characters with photos have their reference images included; characters without photos are described by text only.
3. **Given** memory mode is off, **When** a story scene is generated, **Then** no reference photos are included in the image generation request, regardless of whether the profile has photos.
4. **Given** a character's linked profile has characters with photos, **When** a story scene is generated with cross-profile linking active, **Then** linked characters' reference photos are also included (one level deep, same as existing character linking behavior).

---

### User Story 3 - Photo Management and Housekeeping (Priority: P3)

Photos are cleaned up when characters or profiles are deleted. Users can view all photos associated with a profile from the profile edit page. Storage is managed sensibly with file size limits to prevent disk bloat on the home server.

**Why this priority**: Important for long-term maintainability but not required for the core upload-and-generate flow. Cleanup prevents orphaned files and disk waste.

**Independent Test**: Delete a character that has a reference photo, verify the photo file is removed from disk. Delete an entire profile with photo-linked characters, verify all associated photos are cleaned up. Upload a photo exceeding the size limit and verify it is rejected.

**Acceptance Scenarios**:

1. **Given** a character with a reference photo, **When** the character is deleted, **Then** the associated photo file is removed from disk.
2. **Given** a profile with multiple characters that have photos, **When** the profile is deleted, **Then** all associated photo files are removed from disk.
3. **Given** a user attempts to upload a photo larger than 5 MB, **When** the upload is submitted, **Then** the system rejects it with a clear error message indicating the size limit.

---

### Edge Cases

- What happens when a user uploads a very small image (e.g., 10x10 pixels)? The system accepts it but the AI may produce poor results — no minimum resolution enforced, but a warning is shown for images under 256x256 pixels.
- What happens when the image generation service does not support reference images (e.g., a model that only accepts text prompts)? The system falls back gracefully to text-only character descriptions, and the photo is simply not used for that generation.
- What happens when a photo file becomes corrupted or is manually deleted from disk? The system treats it as if no photo exists — shows no thumbnail, does not include it in generation, and does not error.
- What happens when the same photo is uploaded to multiple characters? Each character gets its own copy of the file — no deduplication, keeping the storage model simple.
- What happens when a character with a photo is part of a cross-profile link and the linked profile is in a different tier? This cannot happen — cross-profile links are enforced to be same-tier only (existing constraint from memory mode feature).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to upload a JPEG or PNG photo for any character within a profile.
- **FR-002**: System MUST store uploaded photos locally on disk, organized by tier and profile, alongside existing profile data.
- **FR-003**: System MUST display a thumbnail preview of the uploaded photo on the character card in the profile edit page.
- **FR-004**: System MUST allow users to replace an existing character photo with a new upload.
- **FR-005**: System MUST allow users to remove a character's photo without deleting the character.
- **FR-006**: System MUST reject uploads that are not JPEG or PNG format, showing a clear error message.
- **FR-007**: System MUST reject uploads larger than 5 MB, showing a clear error message with the size limit.
- **FR-008**: System MUST show a warning (non-blocking) when an uploaded image is smaller than 256x256 pixels.
- **FR-009**: System MUST include character reference photos in image generation requests when memory mode is active and the character has a photo.
- **FR-010**: System MUST NOT include reference photos in image generation when memory mode is off.
- **FR-011**: System MUST include reference photos from cross-profile linked characters (one level deep, same tier only).
- **FR-012**: System MUST delete the associated photo file from disk when a character is deleted.
- **FR-013**: System MUST delete all associated photo files when a profile is deleted.
- **FR-014**: System MUST enforce tier isolation — photos stored under a kids profile are never accessible from the nsfw tier and vice versa.
- **FR-015**: System MUST gracefully handle missing or corrupted photo files by treating them as if no photo exists (no errors, no broken images).
- **FR-016**: System MUST fall back to text-only character descriptions when the image generation model does not support reference images.
- **FR-017**: System MUST serve photo thumbnails from a local route scoped to the tier (not directly from the filesystem).

### Key Entities

- **Character Photo**: A reference image file associated with a specific character within a profile. Stored as a file on disk. Key attributes: file path, original filename, file size, image dimensions, associated character ID, associated profile ID, tier.
- **Character (extended)**: The existing Character entity gains an optional reference to a photo file path.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a photo and see the thumbnail on the character card in under 10 seconds.
- **SC-002**: 100% of generated story images use reference photos when memory mode is active and photos are available, with graceful fallback when the image model does not support references.
- **SC-003**: All photo files are cleaned up within the same operation when a character or profile is deleted — zero orphaned files after deletion.
- **SC-004**: Photos from one tier are never served or accessible from routes belonging to another tier.
- **SC-005**: System handles photo upload failures (wrong format, too large, corrupted) without crashing, showing clear user-facing error messages in all cases.

## Assumptions

- Photos are stored as files on disk (same local-first pattern as profile JSON files and gallery images) — no cloud storage or CDN needed.
- Maximum photo file size of 5 MB is sufficient for reference photos while keeping disk usage manageable on a home server.
- The AI image generation models currently in use (OpenAI gpt-image-1) support reference image input. If a model does not support it, the system falls back to text-only.
- No image processing or resizing is performed on upload — photos are stored as-is. The AI model handles any needed transformations.
- Cross-profile photo sharing follows the same one-level-deep linking rule established in the memory mode feature.
- Photo thumbnails are served via application routes (not static file serving) to enforce tier isolation access control.

## Scope Boundaries

**In scope**:
- Upload, replace, remove photos for characters
- Photo thumbnails on character cards
- Reference photo inclusion in AI image generation
- Photo cleanup on character/profile deletion
- Tier-isolated photo storage and serving

**Out of scope**:
- Photo editing or cropping within the application
- Face detection or automatic character recognition
- Batch photo upload (one photo per character)
- Photo sharing between characters (each gets its own copy)
- Video or animated image support
