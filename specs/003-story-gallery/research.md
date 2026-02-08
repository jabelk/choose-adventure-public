# Research: Story Gallery

## Decision 1: Persistence Format

**Decision**: JSON files, one per story, stored in `data/stories/` directory.

**Rationale**: Constitution Principle IV requires human-readable, portable storage. JSON files are easily inspectable, backed up, and migrated. One file per story avoids write conflicts and makes individual story management trivial. The `data/` directory is separate from `static/` since these are application data, not served assets.

**Alternatives considered**:
- SQLite database — more queryable but violates "human-readable and portable" preference. Overkill for expected volume.
- Single JSON file — write conflicts, grows unwieldy, harder to manage individual stories.
- Markdown files — harder to parse programmatically, less structured.

## Decision 2: What to Persist

**Decision**: Save the full StorySession (all scenes in the branching tree + path_history) rather than just the taken path.

**Rationale**: Constitution Principle IV states "Stories MUST be stored in a format that preserves the full branching structure (all paths, not just the path taken)." The StorySession already contains `scenes` (all generated scenes, including alternate branches) and `path_history` (the specific path taken). Saving both satisfies the constitution and enables future branch visualization.

**Alternatives considered**:
- Save only the taken path — simpler but violates Constitution Principle IV.
- Save scenes separately from story metadata — unnecessary complexity.

## Decision 3: When to Save

**Decision**: Save when a scene with `is_ending=true` is generated and added to the session.

**Rationale**: The spec requires auto-save on completion only. The natural trigger is inside `make_choice` in routes.py, right after the ending scene is added to the session. This keeps the save logic in one place and ensures the full path including the ending is captured.

**Alternatives considered**:
- Save on every scene — creates many partial saves, more disk I/O, would need cleanup for abandoned stories.
- Manual save button — against spec requirement of auto-save.

## Decision 4: Gallery Route Structure

**Decision**: Add gallery routes to the existing tier router factory.

**Rationale**: Gallery is tier-scoped, so it naturally belongs in `create_tier_router()`. New routes:
- `GET /{tier}/gallery` — gallery listing page
- `GET /{tier}/gallery/{story_id}` — story reader (first scene)
- `GET /{tier}/gallery/{story_id}/{scene_index}` — story reader (specific scene by index in path)

Using scene_index (0-based integer) rather than scene_id for the reader URL simplifies Next/Previous navigation — just increment/decrement the index.

**Alternatives considered**:
- Separate gallery router — more isolation but unnecessary duplication of tier context.
- Scene navigation by scene_id with lookup — harder to compute Next/Previous without knowing position in path.

## Decision 5: Storage Service Architecture

**Decision**: Create a new `app/services/gallery.py` with a `GalleryService` class handling save/load operations.

**Rationale**: Keeps persistence logic separate from routing and models. The service handles file I/O, JSON serialization, tier filtering, and error handling for corrupted files. Follows the existing pattern of `StoryService` and `ImageService`.

**Alternatives considered**:
- Inline file I/O in routes — messy, hard to test, violates separation of concerns.
- Extend session.py — session.py is for in-memory ephemeral sessions, not persistent storage.

## Decision 6: Saved Story Data Model

**Decision**: Create a `SavedStory` Pydantic model for the persisted format.

**Rationale**: A dedicated model decouples the persisted format from the in-memory session format. The SavedStory contains: story metadata (from Story), all scenes (from StorySession.scenes), and the path_history (ordered list of scene IDs for the taken path). This is a flat, serializable structure that Pydantic can dump to JSON directly.

**Alternatives considered**:
- Serialize StorySession directly — includes session-specific fields (error_message) that don't belong in the archive.
- Custom dict format — loses type safety and validation.

## Decision 7: Gallery Card Thumbnail

**Decision**: Use the first scene's image URL from the saved story for the gallery card thumbnail.

**Rationale**: The first scene always has an image (or a failed placeholder). No additional image processing or thumbnail generation is needed. The image URL is already a path to a static file on disk.

**Alternatives considered**:
- Generate separate thumbnails — unnecessary complexity, Constitution Principle V (Fun Over Perfection).
- Use last scene's image — first impression is more meaningful for identifying a story.

## Decision 8: Also Save on First Scene Start

**Decision**: No — only save completed stories per spec.

**Rationale**: The spec explicitly states "Stories that are abandoned (not finished) are not saved to the gallery." Saving only on ending keeps the gallery clean and avoids orphan files.
