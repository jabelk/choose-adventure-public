# Feature Specification: Image Gallery View

**Feature Branch**: `030-image-gallery-view`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Image Gallery View — Swipeable full-screen image-only view of a completed story. Just the AI-generated pictures in sequence — no text, no UI chrome. Good for revisiting favorites or showing off the art. Accessible from the gallery reader page. Both tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Story Images Full-Screen (Priority: P1)

A user reading a completed story in the gallery wants to see just the images without any text or interface elements. They click an "Image Gallery" button on the gallery reader page and are taken to a full-screen view showing the story's images in chronological order (following the main path). They can swipe or use arrow keys to navigate between images. They can exit back to the reader at any time.

**Why this priority**: This is the entire feature — without full-screen image viewing, nothing else matters. It delivers the core value of being able to admire and show off the AI-generated art.

**Independent Test**: Navigate to any completed story in the gallery reader, click the "Image Gallery" button, verify images display full-screen in sequence, swipe/arrow between them, and press Escape or a close button to return to the reader.

**Acceptance Scenarios**:

1. **Given** a user viewing a completed story in the gallery reader, **When** they click the "Image Gallery" button, **Then** a full-screen image gallery opens showing the first scene's image.
2. **Given** a user in the image gallery view, **When** they swipe right or press the right arrow key, **Then** the next image in the story sequence appears.
3. **Given** a user in the image gallery view, **When** they swipe left or press the left arrow key, **Then** the previous image in the story sequence appears.
4. **Given** a user in the image gallery view, **When** they press Escape or click a close button, **Then** they return to the gallery reader page.
5. **Given** a story where some scenes have no images, **When** the user enters the image gallery, **Then** only scenes with images are shown (scenes without images are skipped).

---

### User Story 2 - Image Counter and Navigation Indicators (Priority: P2)

While viewing images in the gallery, the user sees a minimal counter (e.g., "3 / 7") showing their position in the image sequence. This helps them know how many images exist and where they are.

**Why this priority**: Enhances the viewing experience with spatial awareness, but the core viewing works without it.

**Independent Test**: Open the image gallery for a multi-scene story, verify the counter shows the correct position and total, navigate through images and confirm the counter updates.

**Acceptance Scenarios**:

1. **Given** a user in the image gallery view showing the first image of a 7-image story, **When** the gallery loads, **Then** a counter displays "1 / 7".
2. **Given** a user navigating to the third image, **When** the image changes, **Then** the counter updates to "3 / 7".
3. **Given** a user on the last image, **When** they try to navigate forward, **Then** nothing happens (no wrap-around) and the counter stays on the last number.

---

### User Story 3 - Works on Both Tiers (Priority: P3)

The image gallery view is accessible from both Kids and NSFW gallery readers with appropriate tier theming.

**Why this priority**: Feature scope requirement — both tiers need it. Lower priority since the implementation is shared via the router factory pattern.

**Independent Test**: Navigate to a Kids tier gallery story and an NSFW tier gallery story, verify the Image Gallery button appears and works identically on both.

**Acceptance Scenarios**:

1. **Given** a Kids tier gallery story with images, **When** the user clicks "Image Gallery", **Then** the full-screen gallery opens with the Kids theme styling.
2. **Given** an NSFW tier gallery story with images, **When** the user clicks "Image Gallery", **Then** the full-screen gallery opens with the NSFW theme styling.

---

### Edge Cases

- What happens when a story has zero images (all scenes have no image_url)? The "Image Gallery" button is hidden entirely.
- What happens when a story has only one image? The gallery shows that single image with no navigation arrows, counter shows "1 / 1".
- What happens when the user reaches the first or last image? Navigation in that direction is disabled (no wrap-around).
- What happens on touch devices? Swipe gestures work for navigation in addition to arrow keys.
- What happens when images are still loading? A loading placeholder is shown until the image loads.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display an "Image Gallery" button on the gallery reader page for stories that have at least one scene with an image.
- **FR-002**: System MUST NOT display the "Image Gallery" button for stories where no scenes have images.
- **FR-003**: The image gallery MUST display images in full-screen mode with a dark/black background and no text content or UI chrome beyond minimal navigation.
- **FR-004**: System MUST display images in the order they appear in the story's main path (path_history), skipping scenes that have no image.
- **FR-005**: System MUST support navigation between images via left/right arrow keys on desktop and swipe gestures on touch devices.
- **FR-006**: System MUST provide a visible close button and support the Escape key to exit the gallery and return to the reader page.
- **FR-007**: System MUST display a position counter (e.g., "3 / 7") showing the current image number and total count.
- **FR-008**: System MUST prevent navigation past the first or last image (no wrap-around behavior).
- **FR-009**: System MUST work on both Kids and NSFW tiers, inheriting the appropriate tier theme.
- **FR-010**: System MUST include extra images from picture book mode scenes (character close-ups, environment shots) in the gallery sequence, inserted after the main scene image.

### Assumptions

- Images are served from existing storage paths — no new image storage is needed.
- The gallery view is client-side only — no new server routes are required beyond what already exists for the gallery reader.
- Touch swipe support uses standard browser touch events without external libraries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open a full-screen image gallery from any completed story that has images, within one click from the reader page.
- **SC-002**: Users can navigate through all story images using keyboard arrows or touch swipes with zero visible latency between transitions.
- **SC-003**: The image gallery correctly shows only images (no text, no story content) in the correct chronological order.
- **SC-004**: The "Image Gallery" button is never shown for stories with zero images.
