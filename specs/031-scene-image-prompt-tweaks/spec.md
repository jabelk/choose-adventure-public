# Feature Specification: Scene Image Prompt Tweaks

**Feature Branch**: `031-scene-image-prompt-tweaks`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Scene Image Prompt Tweaks — After an image generates, let the user edit the image prompt and regenerate. 'Make her hair blonde,' 'add a sunset,' 'make it more dramatic.' Small edit icon on the generated image that opens the prompt in an editable field with a regenerate button. Both tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edit and Regenerate Scene Image (Priority: P1)

A user playing through a story sees an image that doesn't match their vision. They click a small edit icon on the generated image, which reveals the current image prompt in an editable text field. The user modifies the prompt text (e.g., changing "a dark forest" to "a dark forest with glowing mushrooms") and clicks a "Regenerate" button. The system generates a new image using the updated prompt and replaces the old image. The updated prompt is saved on the scene.

**Why this priority**: This is the entire feature — without the ability to edit and regenerate, nothing else matters. It delivers the core value of giving users creative control over their story's visual presentation.

**Independent Test**: Start a story, wait for the first scene image to generate, click the edit icon, modify the prompt text, click Regenerate, and verify a new image replaces the old one using the updated prompt.

**Acceptance Scenarios**:

1. **Given** a user viewing a scene with a generated image, **When** they click the edit icon on the image, **Then** the current image prompt is displayed in an editable text field with a "Regenerate" and "Cancel" button.
2. **Given** a user has edited the image prompt, **When** they click "Regenerate", **Then** a new image is generated using the updated prompt and replaces the old image on the page.
3. **Given** a user has regenerated an image, **When** they continue the story and return to that scene, **Then** the regenerated image and updated prompt persist.
4. **Given** a user is editing a prompt, **When** they click "Cancel" or click outside the edit area, **Then** the edit field closes without changes and the original image remains.

---

### User Story 2 - Works on Both Tiers (Priority: P2)

The image prompt edit feature is accessible from both Kids and NSFW tier story pages, using the same edit icon and regenerate flow. The tier's configured image model is used for regeneration.

**Why this priority**: Feature scope requirement — both tiers need it. Lower priority since the implementation is shared via the router factory pattern.

**Independent Test**: Start a Kids tier story and an NSFW tier story, verify the edit icon appears on scene images and regeneration works identically on both.

**Acceptance Scenarios**:

1. **Given** a Kids tier story with a scene image, **When** the user clicks the edit icon, **Then** the prompt editing UI appears and regeneration uses the story's configured image model.
2. **Given** an NSFW tier story with a scene image, **When** the user clicks the edit icon, **Then** the prompt editing UI appears and regeneration uses the story's configured image model.

---

### User Story 3 - Gallery Reader Prompt Tweaks (Priority: P3)

When viewing a completed story in the gallery reader, the user can also edit image prompts and regenerate images. The updated images are saved back to the story's archive.

**Why this priority**: Extends the feature to saved stories, which is valuable for polishing past stories but not essential for the core experience during active play.

**Independent Test**: Open a saved story in the gallery reader, click the edit icon on a scene image, modify the prompt, regenerate, and verify the new image persists in the saved story.

**Acceptance Scenarios**:

1. **Given** a user viewing a saved story scene in the gallery reader, **When** they click the edit icon and modify the prompt, **Then** a regenerated image replaces the original.
2. **Given** a user has regenerated an image in the gallery reader, **When** they close and reopen the same story, **Then** the regenerated image and updated prompt are preserved.

---

### Edge Cases

- What happens when image generation fails during regeneration? The original image is preserved, and an error message is displayed to the user. The edit field remains open so they can try again.
- What happens when a scene has no image (image generation was skipped or failed originally)? The edit icon is not shown — you can only edit an existing image's prompt.
- What happens when the user clears the prompt field and clicks Regenerate? The system prevents regeneration and displays a validation message requiring non-empty prompt text.
- What happens if the user navigates away while regeneration is in progress? The regeneration continues in the background; if the user returns, they see the new image (or the original if it failed).
- What happens with extra images (picture book mode close-ups and environment shots)? Only the main scene image prompt is editable. Extra images are not individually editable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a small edit icon overlaid on each scene image that has an associated image prompt.
- **FR-002**: System MUST NOT display the edit icon on scenes without an image or without an image prompt.
- **FR-003**: Clicking the edit icon MUST reveal the current image prompt in an editable text field, along with "Regenerate" and "Cancel" buttons.
- **FR-004**: Clicking "Regenerate" MUST send the updated prompt to the image generation service and replace the scene image with the newly generated image.
- **FR-005**: System MUST show a loading indicator during image regeneration and disable the Regenerate button to prevent duplicate requests.
- **FR-006**: System MUST preserve the original image if regeneration fails, and display an error message to the user.
- **FR-007**: System MUST save the updated image prompt on the scene after successful regeneration.
- **FR-008**: System MUST validate that the prompt field is not empty before allowing regeneration.
- **FR-009**: System MUST work on both Kids and NSFW tiers, using the story's configured image model for regeneration.
- **FR-010**: System MUST support prompt editing and image regeneration in the gallery reader for saved/completed stories, persisting changes to the story archive.

### Assumptions

- Image regeneration uses the same image model that was used for the original story (stored on the story/session).
- Only the main scene image prompt is editable — extra images from picture book mode are not individually editable in this feature.
- The regenerated image replaces the original permanently; there is no undo or image history.
- Image regeneration requires the same API credentials as normal story image generation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can edit an image prompt and see a regenerated image within one interaction (click edit, modify text, click Regenerate).
- **SC-002**: The edit icon is visible on every scene image that has an associated prompt, and hidden on scenes without images.
- **SC-003**: Regenerated images persist across page navigation — returning to the scene shows the updated image and prompt.
- **SC-004**: The feature works identically on both Kids and NSFW tiers with zero tier-specific code paths for the user interface.
