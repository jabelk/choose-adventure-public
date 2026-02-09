# Feature Specification: Character Visual Consistency

**Feature Branch**: `043-visual-consistency`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Character Visual Consistency — maintain the same character appearance across all scene images in a story using reference image seeding from roster character photos or first-scene generation, carried through subsequent image generations for visual coherence"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Carry Reference Image Across Scenes (Priority: P1)

When a story is started with a roster character who has photos, the character's reference photos are already passed to the first scene's image generation. However, for scenes 2+, the same reference photos should continue to be passed automatically — and the generated image from the previous scene should ALSO be included as an additional reference to reinforce visual consistency.

For stories without roster character photos, the generated image from scene 1 becomes the reference for scene 2, scene 2's image becomes an additional reference for scene 3, and so on — creating a chain of visual consistency even without an initial photo.

**Why this priority**: This is the core mechanism. Without carrying references forward, every scene generates a character from scratch, producing wildly different appearances. This single change produces the biggest visual quality improvement.

**Independent Test**: Start a story on `/nsfw/` with a roster character who has a photo. Complete 3 scenes. Verify that the character's appearance (face, hair, body type) remains visually consistent across all 3 scene images. Then start a story WITHOUT a roster character photo and verify scene 2+ images maintain visual similarity to scene 1.

**Acceptance Scenarios**:

1. **Given** a story started with a roster character who has photos, **When** scene 2 is generated, **Then** both the roster character's original photos AND the scene 1 generated image are passed as reference images to the image API
2. **Given** a story started without any character photos, **When** scene 1's image completes, **Then** the generated image path is stored on the session as a reference for subsequent scenes
3. **Given** a story at scene 3+, **When** a new image is generated, **Then** the reference images include: roster photos (if any) + the most recently generated scene image (rolling window, not all prior images)
4. **Given** any story in progress, **When** the image generation API receives reference images, **Then** the total reference image count does not exceed 3 (roster photos + generated scene image, prioritizing roster photos)

---

### User Story 2 - Reference Image Display on Story Page (Priority: P2)

Show a small indicator on the story page when reference images are being used for visual consistency. This gives users confidence that the system is maintaining character appearance and helps them understand why images look similar across scenes.

**Why this priority**: Transparency feature. Users should know when reference images are active. Low effort, high UX value.

**Independent Test**: Start a story with a roster character who has a photo. On the story page, verify a small "Reference photo active" badge or indicator appears near the scene image.

**Acceptance Scenarios**:

1. **Given** a story with reference images active, **When** the story page renders, **Then** a subtle indicator shows that visual consistency is being maintained
2. **Given** a story without any reference images, **When** the story page renders, **Then** no reference indicator appears

---

### User Story 3 - Opt-Out / Reset Visual Reference (Priority: P3)

Allow users to clear the accumulated reference images mid-story if they want the character's appearance to change (e.g., a transformation scene, a time skip, or simply wanting a fresh look). A "Reset appearance" button on the story page clears the session's generated reference images while keeping roster photos intact.

**Why this priority**: Edge case but important for transformation-heavy NSFW content where characters are supposed to change appearance mid-story. Without this, the reference system would fight against intentional appearance changes.

**Independent Test**: Start a story, progress 2 scenes, tap "Reset appearance", progress another scene. Verify the new scene's image is not constrained by prior scene references (but roster photos still apply if present).

**Acceptance Scenarios**:

1. **Given** a story at scene 3 with accumulated references, **When** user taps "Reset appearance", **Then** the session's generated reference images are cleared but roster character photos remain
2. **Given** a story after a reset, **When** the next scene generates, **Then** only roster photos (if any) are used as references, and the new generated image becomes the new rolling reference going forward

---

### Edge Cases

- What happens when image generation fails for a scene? The failed scene should not corrupt the reference chain — the last successfully generated image remains the reference.
- What happens when a story has multiple roster characters selected? Photos from all selected characters are included (up to the 3-photo limit, distributed across characters).
- What happens with picture book mode (extra image variations)? Only the primary scene image is used as the rolling reference, not the variations.
- What happens when the user regenerates a scene image? The regenerated image replaces the previous one as the rolling reference.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store the file path of each successfully generated scene image on the story session as a rolling reference
- **FR-002**: System MUST pass accumulated reference images (roster photos + latest generated scene image) to the image generation API for every scene after the first
- **FR-003**: System MUST cap total reference images at 3 per generation call, prioritizing roster character photos over generated scene images
- **FR-004**: System MUST NOT include failed or pending image generations in the reference chain
- **FR-005**: System MUST continue using roster character photos as references for all scenes regardless of the rolling reference state
- **FR-006**: System MUST provide a way to clear generated scene references mid-story without affecting roster character photos
- **FR-007**: System MUST display a visual indicator when reference images are active during story generation
- **FR-008**: System MUST update the rolling reference when a scene image is regenerated (replacing the old reference with the new one)
- **FR-009**: System MUST work across all image generation providers (OpenAI, Gemini, Grok) that support reference images
- **FR-010**: System MUST handle the reference chain gracefully when switching between image models mid-story

### Key Entities

- **Story Session**: Extended with `generated_reference_path` field — the file path of the most recently generated scene image to use as a rolling reference
- **Scene Image**: Existing `Image` model, no changes needed — the generated file at `static/images/{scene_id}.png` serves as the reference source

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Characters in scene 2+ images are visually recognizable as the same character from scene 1 when reference images are provided
- **SC-002**: Reference image passing adds no more than 500ms overhead per scene generation
- **SC-003**: Users can complete a 5-scene story with visual consistency maintained throughout without manual intervention
- **SC-004**: The reference reset feature clears generated references within one user action (single tap/click)
- **SC-005**: No regression in existing image generation — stories without roster characters still generate successfully, with scene 1's image bootstrapping the reference chain
