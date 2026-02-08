# Feature Specification: Picture Book Mode

**Feature Branch**: `020-picture-book-mode`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "For toddler and young child protagonist ages, automatically generate multiple images per scene (2-3 images instead of 1) for a picture book feel, and default to faster image generation models (gpt-image-1-mini). The extra images should be visual variations of the scene (e.g., character close-up, environment wide shot) generated alongside the main illustration. Images should display in a vertical layout on the scene page. The extra images should use the fast model regardless of what the user picked for the main image. Polling and loading states need to work for all images. Target audience is caucasian upper-middle-class families with young children."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Image Scene Generation (Priority: P1)

A parent selects "Toddler (3-4)" or "Young Child (5-6)" as the protagonist age when starting a new story. When each scene loads, it displays 3 illustrations instead of the usual single image, creating a picture book experience that keeps young children engaged. The extra images are generated automatically without any additional input from the parent.

**Why this priority**: This is the core feature — without multiple images per scene, there is no picture book mode. Young children are visual learners and respond far better to image-rich content.

**Independent Test**: Can be fully tested by starting a story with the "Toddler" or "Young Child" age option selected and verifying that each scene displays multiple images with loading states.

**Acceptance Scenarios**:

1. **Given** a user starts a story with protagonist age set to "Toddler (3-4)", **When** the first scene loads, **Then** the scene displays 3 images: one main illustration, one character close-up, and one environment/setting shot.
2. **Given** a user starts a story with protagonist age set to "Young Child (5-6)", **When** the first scene loads, **Then** the scene displays 3 images in the same layout as the toddler setting.
3. **Given** a user starts a story with protagonist age set to "Older Child (7-9)" or any adult age, **When** the first scene loads, **Then** the scene displays only the standard single image.
4. **Given** a user makes a choice to continue the story, **When** the next scene loads, **Then** it also displays 3 images, maintaining the picture book experience across all scenes.

---

### User Story 2 - Faster Image Generation for Young Ages (Priority: P2)

Extra images automatically use a faster generation model to minimize wait times for young children who have short attention spans. The main illustration uses whatever model the user selected, but the 2 supplementary images use the fastest available model to ensure they appear quickly.

**Why this priority**: Speed is critical for keeping toddlers and young children engaged. A child will lose interest if they have to wait too long for images to appear.

**Independent Test**: Can be tested by starting a picture book mode story and verifying that extra images use the fast model regardless of what primary image model was selected on the form.

**Acceptance Scenarios**:

1. **Given** a user selects a standard image model and starts a story with a young age, **When** images generate, **Then** the main image uses the user's selected model and the extra images use the fast model.
2. **Given** images are generating, **When** extra images complete before the main image, **Then** they appear immediately without waiting for the main image.
3. **Given** the fast model is unavailable, **When** extra images are generated, **Then** the system falls back to the user's selected model gracefully.

---

### User Story 3 - Image Loading Experience (Priority: P3)

All images on a picture book scene show individual loading states and appear independently as they complete. Each image has its own progress indicator and can be retried independently if generation fails.

**Why this priority**: A polished loading experience prevents confusion for parents and keeps visual interest for children even while images are loading.

**Independent Test**: Can be tested by loading a scene and verifying each image placeholder shows progress, and that images appear one by one as they complete.

**Acceptance Scenarios**:

1. **Given** a scene is loading with 3 images, **When** images are still generating, **Then** each image slot shows its own loading placeholder with progress messaging.
2. **Given** the main image completes but extra images are still loading, **When** the main image appears, **Then** the extra image slots continue showing loading state independently.
3. **Given** one extra image fails to generate, **When** the user views the scene, **Then** only the failed image shows a retry button, and the other images display normally.
4. **Given** a completed story is saved to the gallery, **When** the user views it in the reader, **Then** all extra images that completed successfully are preserved and displayed.

---

### Edge Cases

- What happens when the protagonist age is left as "Any" (default)? Standard single-image behavior applies.
- What happens when a user changes from a young age to an older age mid-session? Not applicable — age is set at story start and persists for the duration.
- What happens when the custom choice (open-field) path is taken? Extra images generate for that scene too, same as AI-generated choices.
- What happens if all extra images fail? The scene still displays normally with just the main image.
- What happens on slow connections? Each image loads independently; partial results are better than waiting for all.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate 3 images per scene (1 main + 2 extra) when protagonist age is "Toddler (3-4)" or "Young Child (5-6)".
- **FR-002**: System MUST generate only 1 image per scene (standard behavior) for all other age selections including "Any" (default).
- **FR-003**: Extra images MUST be visual variations of the scene: one character-focused close-up and one environment/setting wide shot.
- **FR-004**: Extra images MUST use the fastest available image model regardless of the user's primary image model selection.
- **FR-005**: The main image MUST continue to use the user's selected image model.
- **FR-006**: Each image MUST have its own independent loading state and progress indicator.
- **FR-007**: Each image MUST be individually retryable if generation fails.
- **FR-008**: Extra images MUST display below the main image in a vertical layout on the scene page.
- **FR-009**: Extra images MUST be preserved when a completed story is saved to the gallery.
- **FR-010**: Extra images MUST appear in the gallery reader when viewing saved stories.
- **FR-011**: Picture book mode MUST only activate for kids tier "Toddler (3-4)" and "Young Child (5-6)" ages. Adult tier ages never trigger picture book mode.

### Key Entities

- **Extra Image**: A supplementary illustration for a scene, generated from a variation of the main image prompt. Has its own generation status (pending, generating, complete, failed) and URL. Two types: "character close-up" and "environment wide shot".
- **Scene (extended)**: An existing scene entity extended with a collection of extra images, in addition to the existing single main image.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Scenes for toddler/young-child ages display 3 images 100% of the time (assuming no generation failures).
- **SC-002**: Extra images appear within 30 seconds of scene load on average, faster than the main image.
- **SC-003**: All 3 images on a scene load and display independently — no image blocks another from appearing.
- **SC-004**: Saved gallery stories preserve and display all extra images that were successfully generated.
- **SC-005**: Standard single-image behavior is completely unaffected for non-young-child age selections.

## Assumptions

- "Fastest available model" means the model with the lowest average generation time among configured models. The current fastest is assumed to be gpt-image-1-mini.
- Extra image prompts are derived from the main scene's image prompt by appending variation instructions (close-up, wide shot), not by generating entirely separate prompts from the AI.
- Picture book mode only activates for kids tier age values "toddler" and "young-child". Adult tier ages never trigger picture book mode.
- The target demographic is caucasian upper-middle-class families. Story content and imagery defaults already reflect age-appropriate content for the kids tier.
- If the fast model is not available (no API key configured), extra images fall back to the user's selected model.

## Scope Boundaries

**In scope**:
- Multi-image generation for young child ages
- Fast model auto-selection for extra images
- Independent polling and loading states
- Gallery persistence of extra images
- Scene page layout for multiple images

**Out of scope**:
- Changing the number of AI-generated story choices based on age
- Modifying text content length based on age (already handled by story flavor options)
- Adding audio narration or text-to-speech for young children
- Different image aspect ratios or sizes for picture book mode
