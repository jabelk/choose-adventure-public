# Data Model: Story Resume

## Entities

### InProgressSave (on disk)

A JSON file representing the full state of an in-progress story session for a single tier.

**Storage**: `data/progress/{tier_name}.json` (e.g., `data/progress/kids.json`)

**Contents**: The serialized `StorySession` Pydantic model, which includes:

| Field | Type | Description |
|-------|------|-------------|
| story | Story | Story metadata (id, title, prompt, length, tier, created_at, current_scene_id) |
| scenes | dict[str, Scene] | All generated scenes keyed by scene_id |
| path_history | list[str] | Ordered list of scene IDs representing the path taken |
| error_message | str or null | Last error message, if any |

**Constraints**:
- At most one file per tier exists at any time
- File is overwritten on each save (not appended)
- File is deleted when the story completes or is abandoned

### Relationships

```
TierConfig (1) ---> (0..1) InProgressSave file
                          |
                          v
                     StorySession
                          |
                     +---------+
                     |         |
                  Story    Scene (many)
                              |
                        +-----+-----+
                        |           |
                     Image       Choice (many)
```

### State Transitions

```
No Save ──[start_story]──> In Progress
In Progress ──[make_choice]──> In Progress (updated)
In Progress ──[go_back]──> In Progress (updated)
In Progress ──[is_ending=true]──> Completed (save deleted, gallery save created)
In Progress ──[abandon]──> No Save (file deleted)
In Progress ──[start_story]──> In Progress (old file replaced)
```

### Existing Entities (unchanged)

- **StorySession**: Already a Pydantic BaseModel. No changes needed — it serializes/deserializes via `model_dump_json()` / `model_validate()`.
- **Story, Scene, Image, Choice**: Nested models within StorySession. No changes needed.
- **SavedStory**: Gallery model. Unaffected by this feature.
