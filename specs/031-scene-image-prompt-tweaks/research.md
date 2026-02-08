# Research: Scene Image Prompt Tweaks

## Existing Image Regeneration Pattern

**Decision**: Reuse the existing `retry_image` pattern but with a new route that accepts a custom prompt.

**Rationale**: The codebase already has `/story/image/{scene_id}/retry` which regenerates with the original prompt. The new `/story/image/{scene_id}/regenerate` route follows the same pattern but updates `scene.image.prompt` first. This avoids duplicating retry logic while adding prompt editing capability.

**Alternatives considered**:
- Modifying the existing retry route to accept an optional prompt parameter — rejected because it changes existing behavior and complicates the simple retry flow.
- Client-side-only approach — rejected because image generation requires server-side API calls.

## Gallery Story Updates

**Decision**: Add an `update_story()` method to GalleryService that writes a modified SavedStory back to disk.

**Rationale**: The gallery service currently only has `save_story()` (from StorySession) and `get_story()` (read). Prompt tweaks on saved stories need a write-back path. A simple JSON re-serialization to the same file path is sufficient.

**Alternatives considered**:
- Direct file manipulation in the route handler — rejected because it bypasses the gallery service abstraction.
- Creating a separate "gallery edit service" — rejected as over-engineering for a single update operation.

## Image Overwrite vs. New File

**Decision**: Overwrite the existing image file at the same path, append cache-busting `?t=timestamp` query param.

**Rationale**: Scene IDs are unique, and each scene has exactly one main image. Keeping old versions would bloat storage with no user-facing benefit (spec says "no undo or image history"). Cache-busting ensures the browser loads the new image.

**Alternatives considered**:
- Generating a new filename with a suffix — rejected because it would require updating all references and complicates cleanup.
- Keeping image history — rejected per spec assumption: "The regenerated image replaces the original permanently."
