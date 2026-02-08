# Data Model: Image Model Selection

## Modified Entities

### Story (app/models.py)

| Field       | Type | Change | Description |
|-------------|------|--------|-------------|
| image_model | str  | NEW    | Image provider key (e.g., "dalle", "gemini"). Default: "dalle" |

All other fields remain unchanged.

### SavedStory (app/models.py)

| Field       | Type | Change | Description |
|-------------|------|--------|-------------|
| image_model | str  | NEW    | Image provider key at time of story creation. Default: "dalle" |

Default value ensures backward compatibility — pre-existing saved stories
that lack this field will deserialize with "dalle" as the image model.

### StorySession (app/models.py)

No changes needed. StorySession contains a Story, which now has the image_model field.
The image model persists through session serialization automatically.

### Image (app/models.py)

No changes needed. The Image model stores prompt, status, url, and error.
The image provider is determined by the parent Story's image_model field,
not stored on each Image individually.

## New Entities

### ImageProvider (app/models_registry.py — added to existing module)

Reuses the existing `ModelProvider` dataclass. A separate list `IMAGE_PROVIDERS`
stores image provider configs.

| Field        | Type | Description |
|--------------|------|-------------|
| key          | str  | Unique identifier (e.g., "dalle", "gemini") |
| display_name | str  | User-facing name (e.g., "DALL-E", "Gemini") |
| api_key_env  | str  | Environment variable name for the API key |

Availability is determined dynamically by checking if the API key env var
has a non-empty value (same pattern as text model providers).

## Modified Configuration

### TierConfig (app/tiers.py)

| Field               | Type | Change | Description |
|---------------------|------|--------|-------------|
| default_image_model | str  | NEW    | Provider key for the pre-selected image model. Default: "dalle" |

## Backward Compatibility

- `Story.image_model` defaults to `"dalle"` — new stories get explicit image model, old sessions work.
- `SavedStory.image_model` defaults to `"dalle"` — old gallery JSON files missing this field deserialize correctly.
- No data migration needed. Pydantic's default values handle missing fields on load.
