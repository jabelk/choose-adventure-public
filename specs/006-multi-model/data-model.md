# Data Model: Multi-Model AI

## Modified Entities

### Story (app/models.py)

| Field | Type | Change | Description |
|-------|------|--------|-------------|
| model | str | NEW | Provider key (e.g., "claude", "gpt", "gemini", "grok"). Default: "claude" |

All other fields remain unchanged.

### SavedStory (app/models.py)

| Field | Type | Change | Description |
|-------|------|--------|-------------|
| model | str | NEW | Provider key at time of story creation. Default: "claude" |

Default value ensures backward compatibility — pre-existing saved stories
that lack this field will deserialize with "claude" as the model.

### StorySession (app/models.py)

No changes needed. StorySession contains a Story, which now has the model field.
The model persists through session serialization automatically.

## New Entities

### ModelProvider (app/models_registry.py)

A lightweight config object for each AI text generation provider.

| Field | Type | Description |
|-------|------|-------------|
| key | str | Unique identifier (e.g., "claude", "gpt", "gemini", "grok") |
| display_name | str | User-facing name (e.g., "Claude", "GPT", "Gemini", "Grok") |
| api_key_env | str | Environment variable name for the API key |

Availability is determined dynamically by checking if the API key env var
has a non-empty value.

## Modified Configuration

### TierConfig (app/tiers.py)

| Field | Type | Change | Description |
|-------|------|--------|-------------|
| default_model | str | NEW | Provider key for the pre-selected model. Default: "claude" |

## Backward Compatibility

- `Story.model` defaults to `"claude"` — new stories get explicit model, old sessions work.
- `SavedStory.model` defaults to `"claude"` — old gallery JSON files missing this field deserialize correctly.
- No data migration needed. Pydantic's default values handle missing fields on load.
