# Feature Specification: Image Retry & Polish

**Feature Branch**: `005-image-polish`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Image Retry & Polish - Improve the image generation experience. Add a retry button when image generation fails so users can try again without restarting the story. Show better progress indication during generation (not just a spinner — maybe a pulsing placeholder or progress text). Allow users to regenerate an image they don't like on any scene (a small 'regenerate' button). Images that are still generating when the user navigates away should continue in the background and be available when they return. The image polling should feel smooth and not janky."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retry Failed Images (Priority: P1)

A user is reading a scene and the image generation fails. Instead of seeing a static "Image unavailable" message with no recourse, they see a friendly error state with a "Retry" button. Clicking retry triggers a new image generation attempt. The UI shows the generating state again while the new attempt runs.

**Why this priority**: Failed images are the most frustrating experience — users currently have no way to recover without restarting the entire story. This is the highest-impact fix.

**Independent Test**: Simulate a failed image (e.g., with an invalid API key temporarily). Verify the failed state shows a retry button. Click retry and verify it transitions back to the generating state.

**Acceptance Scenarios**:

1. **Given** image generation has failed for a scene, **When** the user views that scene, **Then** they see an error message with a "Retry" button instead of just "Image unavailable".
2. **Given** a failed image with a retry button, **When** the user clicks "Retry", **Then** the image area transitions to the generating state and a new generation attempt begins.
3. **Given** a retry is in progress, **When** the retry succeeds, **Then** the image fades in smoothly replacing the generating state.
4. **Given** a retry is in progress, **When** the retry also fails, **Then** the error state with the retry button is shown again.

---

### User Story 2 - Improved Generation Progress (Priority: P1)

While an image is being generated, the user sees a polished loading experience instead of a basic spinner. The placeholder area pulses gently with a gradient animation and shows progress text like "Creating your illustration...". The transition from loading to the final image is smooth (fade-in).

**Why this priority**: Image generation takes 10-30 seconds. A polished loading experience makes the wait feel shorter and the app feel more professional.

**Independent Test**: Start a new story and observe the image area while it generates. Verify the pulsing placeholder animation, progress text, and smooth fade-in when the image arrives.

**Acceptance Scenarios**:

1. **Given** a scene is loading and the image is being generated, **When** the user views the scene, **Then** they see an animated pulsing placeholder with progress text.
2. **Given** the image is generating, **When** generation completes, **Then** the image fades in smoothly over ~0.5 seconds.
3. **Given** the image is generating, **When** the user navigates away and returns, **Then** the image is shown immediately if generation completed, or the loading state resumes if still generating.

---

### User Story 3 - Regenerate Any Image (Priority: P2)

A user is viewing a scene with a completed image but doesn't like how it looks. They can click a small "Regenerate" button to request a new image. The old image is replaced with the generating state, and a fresh image is produced from the same prompt. The new image replaces the old one.

**Why this priority**: Nice-to-have that improves satisfaction, but not critical since images are decorative. Users can always continue the story regardless of image quality.

**Independent Test**: View a scene with a completed image. Click "Regenerate". Verify the old image is replaced with the loading state, then a new image appears.

**Acceptance Scenarios**:

1. **Given** a scene with a completed image, **When** the user views it, **Then** a small "Regenerate" button is visible near the image.
2. **Given** a completed image, **When** the user clicks "Regenerate", **Then** the image area transitions to the generating state and a new image is requested.
3. **Given** a regeneration is in progress, **When** it completes, **Then** the new image replaces the old one with a smooth fade-in.

---

### Edge Cases

- What happens if the user clicks retry/regenerate multiple times quickly? Only one generation should be in flight at a time — subsequent clicks are ignored while generating.
- What happens if the user navigates to a different scene while an image is generating? The generation continues in the background. When the user returns, the completed image is shown.
- What happens if the user regenerates an image on a completed gallery story? Regeneration is only available on active story scenes, not in the read-only gallery reader.
- What if the image generation service is completely down? After a retry fails, the error state with the retry button is shown again. Users can keep retrying or continue the story without an image.
- What happens to progress saves when an image is regenerated? The in-progress save is updated with the new image status/URL after regeneration completes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When image generation fails, the scene MUST display an error state with a visible "Retry" button.
- **FR-002**: Clicking "Retry" MUST trigger a new image generation attempt and show the generating state.
- **FR-003**: The image generating state MUST show an animated pulsing placeholder with descriptive progress text (not just a static spinner).
- **FR-004**: When a generated image arrives, it MUST fade in smoothly (approximately 0.5 second transition).
- **FR-005**: Completed images MUST show a "Regenerate" button that triggers a new generation from the same prompt.
- **FR-006**: Only one image generation request per scene MUST be in flight at a time — duplicate requests are prevented.
- **FR-007**: Image generation MUST continue in the background when the user navigates away from the scene.
- **FR-008**: When the user returns to a scene, the image MUST reflect its current state (complete, generating, or failed).
- **FR-009**: The "Regenerate" button MUST only appear on active story scenes, not in the read-only gallery reader.
- **FR-010**: Retry and regenerate MUST work without requiring a page reload.
- **FR-011**: The image polling mechanism MUST not cause visible UI jank (no layout shifts, no flickering).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can recover from a failed image with a single click, without leaving the scene or restarting the story.
- **SC-002**: The image loading experience shows continuous visual feedback (animation) for the full duration of generation.
- **SC-003**: Image transitions (loading to complete, complete to regenerating) are smooth with no layout shifts or flickering.
- **SC-004**: Users can regenerate any image they're unsatisfied with in a single click.
- **SC-005**: Images that finish generating while the user is on a different scene are immediately visible when the user returns.

## Assumptions

- The existing image polling mechanism (2-second interval) is retained but the UI feedback is improved.
- Retry uses the same image prompt as the original generation — no prompt editing.
- Regenerate overwrites the existing image file on disk (same filename, new content).
- The gallery reader remains read-only — no retry or regenerate buttons there.
- Image generation costs (API calls) are acceptable for retries since this is a personal project.
