# Research: Image Retry & Polish

## Decision 1: How Retry/Regenerate Triggers New Generation

**Decision**: Add a `POST /{tier}/story/image/{scene_id}/retry` endpoint that resets the Image model's status to PENDING and kicks off a new `asyncio.create_task(image_service.generate_image(...))`. Return JSON status so the client can handle it without a page reload.

**Rationale**: The existing `GET /{tier}/story/image/{scene_id}` endpoint already returns JSON status. Adding a POST endpoint for triggering regeneration keeps the pattern consistent. POST is appropriate since it modifies state (resets image, triggers generation).

**Alternatives considered**:
- Client-side only (just re-poll): Doesn't work — the Image object in memory is marked FAILED, so re-polling would just return "failed" again.
- Full page reload with query param: Works but violates FR-010 (must work without reload) and feels janky.

## Decision 2: Preventing Duplicate Generation Requests

**Decision**: Check `image.status` before starting a new generation. If status is GENERATING, return early with `{"status": "generating"}`. The client disables the retry/regenerate button while in generating state.

**Rationale**: Simple server-side guard plus client-side UI feedback. No need for locks or queues since this is a single-user app.

**Alternatives considered**:
- Client-side only debounce: Fragile — can't prevent duplicate requests from multiple tabs.
- Server-side lock/mutex: Overkill for a personal app with one user.

## Decision 3: Client-Side Architecture for Retry/Regenerate

**Decision**: Extend the existing `pollImageStatus()` function to also handle retry and regenerate flows. Add new functions `retryImage(sceneId)` and `regenerateImage(sceneId)` that POST to the retry endpoint, then call `pollImageStatus()` to track the new generation. The `showFallback()` function is updated to include a retry button.

**Rationale**: Builds on the existing polling infrastructure. The retry endpoint resets the image, and polling picks up the new state naturally.

**Alternatives considered**:
- WebSocket for real-time updates: Overkill for 2-second polling. Adds complexity.
- Server-Sent Events: Better than WebSocket but still unnecessary complexity for a personal project.

## Decision 4: Pulsing Placeholder Animation

**Decision**: Replace the current spinner + "Generating image..." with a CSS-only pulsing gradient animation on the placeholder div. The placeholder maintains the same aspect ratio as the final image (1:1 since images are 1024x1024) to prevent layout shift. Add rotating progress messages for variety.

**Rationale**: CSS animations are smooth, GPU-accelerated, and don't require JavaScript. Fixed aspect ratio prevents the jarring layout shift when the image loads.

**Alternatives considered**:
- Skeleton screen with shimmer: Works but more complex CSS for minimal benefit over a simple pulse.
- Progress bar: Misleading since we can't accurately predict generation time.

## Decision 5: Layout Shift Prevention

**Decision**: Set a fixed aspect ratio on `.scene-image-container` using `aspect-ratio: 1` (matching the 1024x1024 generated images). The container maintains its size through all states (loading, complete, failed) so the text below never jumps.

**Rationale**: The most common source of jank in image loading UIs is layout shift when the image arrives. A fixed container size eliminates this entirely.

**Alternatives considered**:
- `min-height` on container: Works but doesn't adapt to responsive widths as well as `aspect-ratio`.
- Intrinsic size hints on img: Only works when the image is already in the DOM, not during loading.

## Decision 6: Regenerate Button Placement

**Decision**: Place a small "Regenerate" button overlaid on the bottom-right corner of the image container. It appears on hover (desktop) and is always visible on mobile. Use a refresh/reload icon with text.

**Rationale**: Overlay keeps it accessible without taking up vertical space. Hover-reveal on desktop keeps the UI clean while reading.

**Alternatives considered**:
- Below the image: Takes up vertical space and separates it visually from the image.
- Above the image: Competes with the scene header.
- Icon only (no text): Less discoverable for first-time users.

## Decision 7: Regenerate in Gallery Reader

**Decision**: No regenerate button in the gallery reader. The reader template (`reader.html`) doesn't use the `scene-image-container` with interactive controls — it just shows the saved `image_url`. No changes needed to the reader.

**Rationale**: Per FR-009 and the spec assumption, gallery stories are read-only. Regenerating would require a live session which doesn't exist in gallery mode.

## Decision 8: Progress Save Updates After Regeneration

**Decision**: The retry endpoint saves progress to disk after resetting the image status. When the background generation completes and updates the Image object, the next poll or scene view will trigger a progress save with the updated image URL.

**Rationale**: The progress save already happens after every session update. The retry endpoint just needs to save once after resetting status. The actual image URL update happens in-memory (Image object mutation), and the next user action (choice, back, etc.) will persist it. For a more immediate persist, the retry endpoint itself can save progress after kicking off generation.
