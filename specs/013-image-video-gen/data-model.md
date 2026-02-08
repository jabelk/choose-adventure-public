# Data Model: Multi-Model Image & Video Generation

**Feature Branch**: `013-image-video-gen`
**Date**: 2026-02-07

## Entity Changes

### ImageModel (new dataclass in models_registry.py)

Replaces the generic `ModelProvider` for image models with richer metadata.

| Field | Type | Description |
|-------|------|-------------|
| key | str | Unique identifier passed in forms and stored in Story (e.g., "gpt-image-1", "grok-imagine") |
| display_name | str | Human-readable name shown in UI (e.g., "GPT Image 1.5") |
| provider | str | Provider group name for UI grouping (e.g., "OpenAI", "xAI", "Google") |
| api_key_env | str | Environment variable name that must be set for this model to be available |
| supports_input_fidelity | bool | Whether images.edit supports input_fidelity="high" for reference photos |
| supports_references | bool | Whether the model supports reference image input at all |

### Story (extended)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| video_mode | bool | False | Whether video generation is enabled for this story |

**Migration note**: `image_model` field changes from provider keys (e.g., "dalle") to specific model keys (e.g., "gpt-image-1"). Existing saved stories with `image_model="dalle"` should be treated as `gpt-image-1` for display purposes.

### Scene (extended via Image model)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| image.video_url | Optional[str] | None | URL path to the video file (e.g., "/static/videos/{scene_id}.mp4") |
| image.video_status | str | "none" | Video generation status: "none", "pending", "generating", "complete", "failed" |
| image.video_error | Optional[str] | None | Error message if video generation failed |

### SavedScene (extended)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| video_url | Optional[str] | None | URL path to the saved video file |

### SavedStory (extended)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| video_mode | bool | False | Whether this story was generated with video mode |

## Storage Layout

### Video Files

```
static/
├── images/
│   └── {scene_id}.png          # Existing image storage
└── videos/
    └── {scene_id}.mp4          # New video storage
```

Videos are stored as MP4 files alongside images. Scene IDs are UUIDs, so no tier prefix is needed in the filename — tier isolation is enforced at the route/session level.

## State Transitions

### Video Status Flow

```
none → pending → generating → complete
                           → failed (retryable)
```

- `none`: Video mode is off, or no video requested for this scene
- `pending`: Video generation queued (waiting for image to complete first)
- `generating`: xAI API call in progress, polling for result
- `complete`: Video downloaded and saved locally
- `failed`: Generation or download failed; retryable via retry button

### Image-to-Video Pipeline

```
Scene created → Image generating → Image complete → Video pending → Video generating → Video complete
                                 → Image failed    → No video attempt
```

Video generation only starts after the scene's image is successfully generated (image-to-video requires the image as input).
