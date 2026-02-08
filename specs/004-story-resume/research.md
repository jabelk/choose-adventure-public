# Research: Story Resume

## Decision 1: Persistence Strategy for In-Progress Saves

**Decision**: Write one JSON file per tier to `data/progress/{tier_name}.json`, containing the serialized StorySession.

**Rationale**: Matches the existing gallery pattern (`data/stories/{id}.json`). One file per tier is simpler than one file per story since the spec limits to one in-progress story per tier. The tier name in the filename provides natural tier isolation.

**Alternatives considered**:
- SQLite database: Overkill for 2 files. Violates Principle III (Iterative Simplicity) and Principle IV (human-readable format).
- One file per story ID: Unnecessary since only one in-progress story per tier. Would require a lookup index to find the active story.
- Extend the in-memory session store with disk backing: Would couple the session module to file I/O and complicate the simple dict-based session store.

## Decision 2: Serialization Format for StorySession

**Decision**: Use Pydantic's `model_dump_json()` to serialize the full `StorySession` model directly. On load, use `StorySession.model_validate()` to deserialize.

**Rationale**: StorySession is already a Pydantic BaseModel. This gives us free JSON serialization/deserialization with validation. The existing gallery service uses the same pattern for SavedStory.

**Alternatives considered**:
- Convert to SavedStory format: Lossy — SavedStory strips the Image model to just a URL string, losing pending/generating status. We need the full Image model to resume image polling.
- Custom serialization: Unnecessary work when Pydantic handles it.

## Decision 3: Where to Put Save/Load Logic

**Decision**: Add `save_progress()`, `load_progress()`, and `delete_progress()` methods to the existing `GalleryService` class, since it already handles story persistence.

**Rationale**: GalleryService already owns the `data/` directory and JSON file I/O patterns. Adding progress methods keeps persistence logic consolidated. The service is already instantiated in routes.py.

**Alternatives considered**:
- New `ProgressService` class: Clean separation but unnecessary for 3 simple methods. Violates Principle V (Fun Over Perfection).
- Add to session.py: Session module is currently a thin in-memory dict. Mixing disk I/O would conflate two concerns.

## Decision 4: How Resume Restores the Session

**Decision**: When the home page loads, check if a progress file exists for this tier. If so, pass the story title and a resume URL to the template. When "Continue" is clicked, load the StorySession from disk into the in-memory session store, set the session cookie, and redirect to the current scene.

**Rationale**: This reuses the existing session flow completely. Once the StorySession is loaded back into memory, all existing routes (view_scene, make_choice, go_back, image_status) work without modification.

**Alternatives considered**:
- Load directly from disk on every request: Slower and would bypass the in-memory session store, breaking the existing flow.
- Auto-restore on server startup: Would load all progress files into memory eagerly. Simpler but wastes memory for tiers the user isn't using.

## Decision 5: When to Auto-Save Progress

**Decision**: Save progress to disk after every scene generation (in `start_story` and `make_choice` handlers), after navigation (`go_back`), and on session updates. Delete the progress file when a story completes (is_ending) or is explicitly abandoned.

**Rationale**: Saving after every state change ensures no progress is lost if the server crashes or the user closes the browser. The files are small (a few KB) so disk writes are negligible.

**Alternatives considered**:
- Save only on browser close: Not reliable — there's no guaranteed beforeunload handler that can trigger a server request.
- Save periodically: Adds complexity (background task) and risks losing recent progress.

## Decision 6: How "Start Fresh" / Abandon Works

**Decision**: Add a `POST /{tier}/story/abandon` route. When called, delete the progress file, clear the in-memory session, delete the session cookie, and redirect to the home page.

**Rationale**: POST is appropriate since this is a destructive action (deletes data). A form button on the resume banner submits to this endpoint.

**Alternatives considered**:
- GET with a query parameter: GET should be idempotent and non-destructive. Abandoning a story deletes data, so POST is more appropriate.
- JavaScript confirm dialog: Nice to have but not needed for MVP. The user explicitly clicks "Start Fresh" which is clear enough.

## Decision 7: How Starting a New Story Replaces an Existing Save

**Decision**: In `start_story`, before creating the new session, delete any existing progress file for this tier. The new story's progress will be saved after its first scene is generated.

**Rationale**: Per FR-009, starting a new story replaces any existing in-progress save. This is the simplest approach — just delete the old file before proceeding.

**Alternatives considered**:
- Warn the user before replacing: Adds UI complexity. The resume banner already gives the user the option to continue, so choosing "Start New Adventure" is an explicit decision.

## Decision 8: Progress Directory Structure

**Decision**: Store progress files in `data/progress/` alongside the existing `data/stories/` directory. File naming: `{tier_name}.json` (e.g., `kids.json`, `nsfw.json`).

**Rationale**: Separating progress from completed stories keeps the directories clean and avoids any collision between progress files and gallery story files. The `data/` directory already exists.

**Alternatives considered**:
- Same directory as stories with a prefix: e.g., `data/stories/_progress_kids.json`. Mixing concerns — list_stories would need to filter these out.
- Subdirectory per tier: e.g., `data/progress/kids/current.json`. Overkill for one file per tier.
