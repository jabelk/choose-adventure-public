# Feature Specification: Multi-Model Image & Video Generation

**Feature Branch**: `013-image-video-gen`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Multi-Model Image & Video Generation - Expand image generation to support multiple OpenAI models (gpt-image-1, gpt-image-1-mini, gpt-image-1.5) and add xAI Grok Imagine as both an image and video generation provider. Users can choose between image models with different quality/cost tradeoffs. Video generation creates short animated scenes for story moments using Grok Imagine's text-to-video and image-to-video capabilities."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expanded Image Model Selection (Priority: P1)

A user starts a new story and sees a richer image model selector on the home page. Instead of just "DALL-E" and "Gemini", they now see individual model variants grouped by provider: OpenAI offers three tiers (a budget-friendly mini option, the standard model, and a premium high-quality model), xAI offers Grok Imagine for images, and Google offers Gemini. The user picks the model that best fits their needs — fast and cheap for casual play, or high quality for a story they plan to save and revisit. The selected model is used for all image generation throughout that story session.

**Why this priority**: This is the foundation for the entire feature. Users need to see and select the new models before any other capability matters. It also unblocks Grok Imagine image generation which is required before video can be added.

**Independent Test**: Start the server with all API keys configured. Navigate to the home page and verify all available image models appear in the selector grouped by provider. Start a story with each model and verify an image is generated successfully.

**Acceptance Scenarios**:

1. **Given** a user with OpenAI and xAI API keys configured, **When** they visit the home page, **Then** they see image model options for GPT Image 1 Mini, GPT Image 1, GPT Image 1.5, and Grok Imagine (plus Gemini if that key is also configured).
2. **Given** a user selects "GPT Image 1 Mini" and starts a story, **When** the first scene generates, **Then** the image is produced using the mini model and the scene view displays "GPT Image 1 Mini" as the image model.
3. **Given** a user selects "Grok Imagine" and starts a story, **When** the first scene generates, **Then** the image is produced via xAI's image generation and displayed normally.
4. **Given** only an OpenAI API key is configured (no xAI, no Gemini), **When** the user visits the home page, **Then** only the three OpenAI image models appear — Grok Imagine and Gemini are hidden.
5. **Given** a story is in progress using a specific image model, **When** the user makes choices and advances through scenes, **Then** all subsequent images in that story use the same model selected at the start.

---

### User Story 2 - Reference Photo Support for New Providers (Priority: P2)

A user who has uploaded reference photos for their characters (feature 012) starts a story using one of the new image models. When memory mode is active, the reference photos are passed to whichever image provider is selected, and the generated images incorporate the likeness of the real people. Each provider handles reference images according to its capabilities — some support direct image editing, others include reference images as context.

**Why this priority**: Reference photos are a key differentiator of this app. Ensuring they work with all new image providers maintains feature parity and prevents a regression in personalization quality.

**Independent Test**: Upload a reference photo for a character, start a story with memory mode on using each new image provider (GPT Image 1 Mini, GPT Image 1.5, Grok Imagine), and verify the generated images visually incorporate the reference photo likeness.

**Acceptance Scenarios**:

1. **Given** a character with a reference photo and memory mode on, **When** a story is started with GPT Image 1.5, **Then** the reference photo is included in the image generation request.
2. **Given** a character with a reference photo and memory mode on, **When** a story is started with GPT Image 1 Mini, **Then** the reference photo is included via the image editing endpoint (without the high-fidelity preservation option, which is not supported on this model).
3. **Given** a character with a reference photo and memory mode on, **When** a story is started with Grok Imagine, **Then** the reference photo is included via Grok's image editing capability.
4. **Given** memory mode is off, **When** a story is started with any model, **Then** no reference photos are included regardless of the provider.

---

### User Story 3 - Video Generation for Story Scenes (Priority: P3)

A user toggles on "Video Mode" on the home page before starting a story. As scenes are generated, each scene receives both a static image and a short animated video clip (up to 10 seconds) that brings the scene to life. The video is generated from either the scene's text prompt (text-to-video) or from the scene's generated image (image-to-video, preferred when available). Videos appear in the scene view below the static image and can be played inline. Videos are also visible when reading saved stories from the gallery.

**Why this priority**: Video generation is the most exciting new capability but depends on Grok Imagine integration (US1) being complete. It's also the most expensive and slowest generation type, so it makes sense as an opt-in enhancement rather than default behavior.

**Independent Test**: Enable video mode on the home page, start a story, and verify that each scene displays a playable video clip alongside the static image. Save the story and reopen it from the gallery to confirm videos persist and play correctly.

**Acceptance Scenarios**:

1. **Given** a user has enabled video mode and starts a story, **When** a scene is generated, **Then** both a static image and a short video clip (up to 10 seconds) are produced for that scene.
2. **Given** a scene has a generated image, **When** video generation is triggered, **Then** the system prefers image-to-video (using the scene's static image as the starting frame) for visual continuity.
3. **Given** video generation is in progress, **When** the user views the scene, **Then** they see the static image immediately and a loading indicator for the video, which appears when ready.
4. **Given** a story with video clips is saved to the gallery, **When** the user opens it in the reader, **Then** all video clips are playable inline alongside their scene text and images.
5. **Given** video mode is enabled but the xAI API key is not configured, **When** the user tries to start a story, **Then** the system shows a clear message that video generation requires the xAI API key and falls back to image-only mode.
6. **Given** video generation fails for a scene, **When** the user views the scene, **Then** the static image is still displayed normally and a non-blocking error message indicates the video could not be generated, with a retry option.

---

### User Story 4 - Video in Gallery and Reader (Priority: P4)

Stories that were generated with video mode enabled display their video clips when browsed in the gallery and read in the story reader. Video thumbnails or play indicators appear on story cards in the gallery so users can distinguish video-enhanced stories from image-only stories. The reader plays videos inline with smooth transitions between scenes.

**Why this priority**: This ensures the full lifecycle of video content — from generation to archival viewing — is complete. Without gallery/reader support, videos would only be visible during active story sessions.

**Independent Test**: Generate a story with video mode on, save it, browse the gallery and verify the story card indicates it has videos, open it in the reader and verify all scene videos play correctly.

**Acceptance Scenarios**:

1. **Given** a saved story that was generated with video mode, **When** the user browses the gallery, **Then** the story card displays an indicator (e.g., a play icon or "Video" badge) showing it contains video content.
2. **Given** a user opens a video-enhanced story in the reader, **When** they navigate between scenes, **Then** each scene's video clip is playable inline with standard play/pause controls.
3. **Given** a saved story that was generated without video mode, **When** the user views it in the reader, **Then** it displays as before with images only — no video placeholders or broken elements.

---

### Edge Cases

- What happens when the xAI API key is valid but the Grok Imagine service is temporarily unavailable? The system retries image generation with backoff (same pattern as existing providers), then marks the image as failed with a retry button. Video generation follows the same pattern independently.
- What happens when video generation takes longer than expected (>60 seconds)? The user sees the static image immediately and video generation continues in the background. A polling mechanism checks for completion and displays the video when ready, up to a maximum wait time of 5 minutes before marking as failed.
- What happens when a user switches from a model that supports reference photos to one that does not mid-feature? Each story locks its image model at creation time — the model cannot be changed during a story. Reference photo support is determined at story start based on the selected model.
- What happens when disk space is low and video files (which are larger than images) cannot be saved? The system catches the write failure, marks the video as failed, and displays the static image normally. No crash or data corruption occurs.
- What happens when a video file becomes corrupted or is manually deleted from disk? The system treats it as if no video exists — shows no video player, does not error, and displays the static image normally (same graceful degradation pattern as photos in feature 012).
- What happens when the user has video mode enabled but selects an image model other than Grok Imagine? Video generation still uses Grok Imagine regardless of the image model selection, since it is the only video provider. If the xAI key is not configured, video mode is unavailable.

## Requirements *(mandatory)*

### Functional Requirements

**Image Model Expansion:**

- **FR-001**: System MUST support the following image generation models: GPT Image 1, GPT Image 1 Mini, GPT Image 1.5 (all via OpenAI), Grok Imagine (via xAI), and Gemini (via Google).
- **FR-002**: System MUST display available image models in the home page selector grouped by provider, showing only models whose API key is configured.
- **FR-003**: System MUST show the specific model name (not just provider) in the scene view, gallery cards, and story reader so users know exactly which model produced each image.
- **FR-004**: System MUST store the selected image model in the story data so it persists across sessions and is used consistently for all scenes in a story.
- **FR-005**: System MUST default to GPT Image 1 when the OpenAI key is configured, or fall back to the first available model.

**Grok Imagine Image Generation:**

- **FR-006**: System MUST generate images via xAI's Grok Imagine API when that model is selected, using the same XAI_API_KEY already used for text generation.
- **FR-007**: System MUST support Grok Imagine's aspect ratio options, defaulting to 1:1 for story illustrations.
- **FR-008**: System MUST handle Grok Imagine's temporary URL response format by downloading and saving the image locally before the URL expires.

**Reference Photo Support:**

- **FR-009**: System MUST pass reference photos to GPT Image 1 and GPT Image 1.5 via the image editing capability when memory mode is active and reference photos are available.
- **FR-010**: System MUST pass reference photos to GPT Image 1 Mini via the image editing endpoint, but without the high-fidelity preservation option (which is not supported on this model).
- **FR-011**: System MUST pass reference photos to Grok Imagine via its image editing capability when memory mode is active.
- **FR-012**: Existing Gemini reference photo support MUST continue to work unchanged.

**Video Generation:**

- **FR-013**: System MUST provide a "Video Mode" toggle on the home page that users can enable before starting a story.
- **FR-014**: System MUST only show the video mode toggle when the xAI API key is configured, since Grok Imagine is the only video provider.
- **FR-015**: When video mode is enabled, the system MUST generate a short video clip (up to 10 seconds) for each story scene in addition to the static image.
- **FR-016**: System MUST prefer image-to-video generation (using the scene's static image as input) over text-to-video for better visual continuity.
- **FR-017**: System MUST generate videos asynchronously — the static image and story text appear immediately, and the video loads when ready.
- **FR-018**: System MUST store video files locally on disk alongside image files, following the same tier-isolated storage pattern.
- **FR-019**: System MUST display videos inline in the scene view with standard play/pause controls.
- **FR-020**: System MUST support video playback in the story reader for saved stories.
- **FR-021**: System MUST indicate on gallery story cards whether a story contains video content.
- **FR-022**: System MUST provide a retry mechanism for failed video generation, independent of image generation retry.
- **FR-023**: System MUST handle video generation failures gracefully — the static image remains visible and the story is fully usable without the video.
- **FR-024**: System MUST store video mode selection and video file references in the story data for persistence.

**Cross-Cutting:**

- **FR-025**: System MUST maintain tier isolation for all new content — video files from one tier are never accessible from another tier's routes.
- **FR-026**: System MUST clean up video files when a story is deleted, following the same pattern as image cleanup.
- **FR-027**: System MUST follow existing retry-with-backoff patterns for all new API integrations.

### Key Entities

- **Image Model (extended)**: The existing concept of an image model expands from a simple provider key (e.g., "dalle") to a specific model variant (e.g., "gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5", "grok-imagine", "gemini"). Each model has a display name, provider grouping, API key dependency, and a flag indicating whether it supports reference image input.
- **Video Clip**: A new media asset associated with a story scene. Key attributes: file path on disk, generation status (pending, generating, complete, failed), duration, associated scene ID, associated story ID, tier. Generated asynchronously after the static image.
- **Story (extended)**: Gains a video mode flag indicating whether video generation is enabled for the story, and scenes gain an optional video reference alongside the existing image reference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select from at least 5 distinct image generation models (3 OpenAI + Grok Imagine + Gemini) when all API keys are configured.
- **SC-002**: Image generation works correctly with each new model — all produce a visible image within 30 seconds for standard scenes.
- **SC-003**: Reference photos are used by all 5 image models that support them, with appropriate fidelity settings per model.
- **SC-004**: Video clips generate and play successfully for at least 90% of scenes when video mode is enabled, with graceful fallback for failures.
- **SC-005**: Video clips appear within 90 seconds of scene generation and play inline without requiring external applications.
- **SC-006**: Saved stories with videos remain fully playable when reopened from the gallery — zero broken video references.
- **SC-007**: Tier isolation is maintained for all video content — videos from one tier are never accessible from another tier's routes.

## Assumptions

- Grok Imagine's image generation API uses its own SDK format (not OpenAI-compatible for images), requiring a dedicated integration method.
- Grok Imagine is the only video generation provider. If additional video providers become available later, the architecture should allow adding them, but only Grok is implemented now.
- Video generation is significantly slower than image generation (10-60 seconds typical), so asynchronous generation with polling is essential for a good user experience.
- Video files are substantially larger than image files (typically 1-10 MB per clip). Disk usage guidance is out of scope but users should be aware video mode increases storage usage.
- GPT Image 1 Mini supports the image editing endpoint but does not support the `input_fidelity` parameter. Reference photos work with all three OpenAI models, with varying fidelity levels.
- The xAI video generation API returns a request ID and requires polling for the result — the system handles this transparently.
- Video format is MP4, which is natively supported by all modern browsers for inline playback.
- Video mode is per-story, not a global setting — each story independently decides whether to include video.

## Scope Boundaries

**In scope**:
- Adding GPT Image 1 Mini, GPT Image 1.5, and Grok Imagine as image providers
- Updating the model registry and UI selector to show all available models
- Integrating xAI's image generation API (Grok Imagine)
- Reference photo support for new providers that support it
- Video generation via Grok Imagine (text-to-video and image-to-video)
- Video playback in scene view, story reader, and gallery
- Async video generation with polling and retry
- Video file storage and cleanup
- Tier isolation for video content

**Out of scope**:
- Video editing or trimming within the application
- Audio/music generation or soundtrack for videos
- User-configurable video duration or resolution
- Video generation from providers other than Grok Imagine
- Streaming video playback (progressive download is sufficient)
- Video thumbnails as animated GIF previews
- Batch video regeneration for existing stories
