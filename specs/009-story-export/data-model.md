# Data Model: Story Export

## Existing Entities (No Changes Needed)

### SavedStory (app/models.py)

| Field        | Type                   | Notes |
|--------------|------------------------|-------|
| story_id     | str                    | Unique ID (UUID) |
| title        | str                    | Story title |
| prompt       | str                    | Original user prompt |
| tier         | str                    | Audience tier |
| length       | str                    | Story length setting |
| target_depth | int                    | Target chapter count |
| model        | str                    | AI model used |
| image_model  | str                    | Image model used |
| created_at   | datetime               | Creation timestamp |
| completed_at | datetime               | Completion timestamp |
| scenes       | dict[str, SavedScene]  | All explored scenes from all branches |
| path_history | list[str]              | The path that was active when story was saved |

### SavedScene (app/models.py)

| Field            | Type               | Notes |
|------------------|--------------------|-------|
| scene_id         | str                | Unique ID (UUID) |
| parent_scene_id  | Optional[str]      | Links to parent scene (None for root) |
| choice_taken_id  | Optional[str]      | Which choice led to this scene |
| content          | str                | Scene text content |
| image_url        | Optional[str]      | Relative URL path (e.g., `/static/images/{id}.png`) |
| image_prompt     | str                | Prompt used to generate the image |
| choices          | list[SavedChoice]  | Available choices from this scene |
| is_ending        | bool               | Whether this scene is an ending |
| depth            | int                | Depth in tree (0 = root) |

### SavedChoice (app/models.py)

| Field         | Type           | Notes |
|---------------|----------------|-------|
| choice_id     | str            | Unique ID (UUID) |
| text          | str            | Choice display text |
| next_scene_id | Optional[str]  | Links to generated scene (None = unexplored) |

No model changes needed. The export service reads from existing `SavedStory` data.

## Image Storage

Images are stored on disk at `static/images/{scene_id}.png`. The `SavedScene.image_url` field stores the relative URL path (e.g., `/static/images/abc123.png`). At export time, the service resolves this to a filesystem path and reads the PNG bytes.

**Path resolution**: Strip the leading `/static/` prefix and resolve relative to the project's `static/` directory. The actual file is at `static/images/{scene_id}.png`.

## Export Data Flow

```text
Export Request:
┌──────────────────────┐
│ User clicks Export   │
│ (gallery or reader)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Load SavedStory from JSON        │
│ File: data/stories/{id}.json     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ For each scene:                  │
│ - Read image from disk           │
│ - Encode as base64 (HTML)        │
│ - Or embed as bytes (PDF)        │
│ - Use placeholder if missing     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Build export file:               │
│ HTML: Render Jinja2 template     │
│ PDF: Build with fpdf2            │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Return file as download          │
│ Content-Disposition: attachment  │
└──────────────────────────────────┘
```

## Backward Compatibility

- Pre-branching stories have all scenes in a flat dict with `parent_scene_id` links forming a single linear chain. The export handles them as a single-path tree — no special casing needed.
- Stories with missing images (failed generation) show a placeholder in the export instead of a broken reference.
