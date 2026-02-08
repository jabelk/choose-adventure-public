# Data Model: Story Branching Explorer

## Existing Entities (No Changes Needed)

### Scene (app/models.py)

The Scene model already supports tree structure:

| Field            | Type           | Notes |
|------------------|----------------|-------|
| scene_id         | str            | Unique ID (UUID) |
| parent_scene_id  | Optional[str]  | Links to parent scene (None for root) |
| choice_taken_id  | Optional[str]  | Which choice led to this scene |
| choices          | list[Choice]   | Available choices from this scene |
| depth            | int            | Depth in tree (0 = root) |

No changes needed. Parent-child relationships already form a tree.

### Choice (app/models.py)

| Field         | Type           | Notes |
|---------------|----------------|-------|
| choice_id     | str            | Unique ID (UUID) |
| text          | str            | Choice display text |
| next_scene_id | Optional[str]  | Links to generated scene (None = unexplored) |

`next_scene_id` being non-None indicates an explored choice. No changes needed.

### StorySession (app/models.py)

| Field        | Type              | Notes |
|--------------|-------------------|-------|
| story        | Story             | Story metadata |
| scenes       | dict[str, Scene]  | All explored scenes (flat dict) |
| path_history | list[str]         | Current reading position path (root → current) |

`scenes` holds ALL explored scenes including branches. `path_history` only tracks the current branch being read. When switching branches, `path_history` is rebuilt from root to the target scene.

**Behavioral change**: `path_history` is now mutable when navigating the tree map (not just linear forward/backward). A new method `navigate_to(scene_id)` rebuilds `path_history` from root to the given scene.

### SavedStory (app/models.py)

| Field        | Type                   | Notes |
|--------------|------------------------|-------|
| scenes       | dict[str, SavedScene]  | All explored scenes from all branches |
| path_history | list[str]              | The path that was active when story was saved |

`scenes` already saves ALL scenes (not just the active path) because `GalleryService.save_story()` iterates `story_session.scenes.items()`. No changes needed for saving branches.

## New Computed Data (Server-Side)

### Tree Data (for template rendering)

A helper function builds a nested tree structure from the flat scenes dict for D3.js:

| Field       | Type         | Description |
|-------------|--------------|-------------|
| id          | str          | Scene ID |
| label       | str          | Chapter label (e.g., "Ch. 1") |
| is_ending   | bool         | Whether this scene is an ending |
| is_current  | bool         | Whether this is the user's current scene |
| on_path     | bool         | Whether this scene is on the current path |
| choice_text | str          | The choice text that led to this scene (empty for root) |
| children    | list[Tree]   | Child nodes (scenes generated from this scene's choices) |

This is a transient computed structure, not persisted.

## Route Changes

### Gallery Reader Route

**Current**: `GET /{tier}/gallery/{story_id}/{scene_index}` (index-based, linear)

**New**: `GET /{tier}/gallery/{story_id}/{scene_id}` (scene-ID-based, supports any branch)

The old index-based route is replaced because index ordering assumes a single linear path. With branches, any scene is directly addressable by ID.

### New Route: Navigate to Scene

**New**: `POST /{tier}/story/navigate/{scene_id}` — Jump to any explored scene in the active story tree. Rebuilds `path_history` from root to the target scene.

## Backward Compatibility

- Pre-existing saved stories have all scenes in a flat dict with `parent_scene_id` links. They naturally form a single-path tree. The tree map renders them as a straight line. No migration needed.
- `SavedStory.path_history` continues to work for linear stories. For branched stories, it records whichever path was active at save time.
- The gallery reader route change from `{scene_index}` to `{scene_id}` is a breaking URL change for bookmarked gallery URLs, but this is acceptable for a personal project with no external users.
