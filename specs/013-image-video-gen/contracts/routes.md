# Route Contracts: Multi-Model Image & Video Generation

**Feature Branch**: `013-image-video-gen`
**Date**: 2026-02-07

## Modified Routes

### GET `/{tier}/` (Home Page)

**Changes**:
- `available_image_models` now returns 5 models (3 OpenAI + Grok Imagine + Gemini) with `provider` grouping
- Template renders models grouped by provider
- New `video_mode_available` context variable (True if XAI_API_KEY is configured)
- Default image model changes from `"dalle"` to `"gpt-image-1"`

### POST `/{tier}/story/start`

**Changes**:
- `image_model` form field now accepts new model keys: `"gpt-image-1"`, `"gpt-image-1-mini"`, `"gpt-image-1.5"`, `"grok-imagine"`, `"gemini"`
- New `video_mode` form field: `str = Form("")` (on/off toggle, same pattern as memory_mode)
- Stores `video_mode` in Story object
- If video_mode is on, after image generation task completes, triggers video generation task

### POST `/{tier}/story/choose/{scene_id}/{choice_id}`

**Changes**:
- Same video generation trigger logic as start_story
- Passes video_mode from story session to video generation pipeline

### GET `/{tier}/story/scene/{scene_id}` (Scene View)

**Changes**:
- Template receives `scene.image.video_url`, `scene.image.video_status`, `scene.image.video_error`
- Template renders `<video>` element when video is available
- Template shows video loading indicator when status is generating/pending
- Template shows video retry button when status is failed

## New Routes

### GET `/{tier}/story/video/{scene_id}` — Video Status

**Purpose**: Check video generation status for polling (same pattern as image status)

**Response**:
```json
{"status": "generating"}
{"status": "complete", "url": "/static/videos/{scene_id}.mp4"}
{"status": "failed"}
{"status": "none"}
```

### POST `/{tier}/story/video/{scene_id}/retry` — Retry Failed Video

**Purpose**: Retry a failed video generation

**Response**:
```json
{"status": "generating"}
{"status": "failed"}
```

## Modified Templates

### home.html

- Image model selector shows models grouped by provider with section headers
- New "Video Mode" toggle checkbox (hidden when xAI key not configured)
- Video mode toggle uses same pattern as memory mode toggle

### scene.html

- Video player element below the image (when video available)
- Video loading spinner (when video generating)
- Video retry button (when video failed)
- Video status polling via JavaScript (same pattern as image status polling)

### gallery.html

- Story cards show a video badge/icon for stories with `video_mode=True`

### reader.html

- Video player inline with scene content (when video_url exists)
- Standard HTML5 `<video>` controls

## External API Contracts

### OpenAI images.generate (expanded)

Models: `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`

```python
response = await openai_client.images.generate(
    model="gpt-image-1.5",  # or any of the three
    prompt="...",
    n=1,
    size="1024x1024",
    quality="auto",
)
```

### OpenAI images.edit (with input_fidelity guard)

```python
params = {
    "model": model_key,
    "image": [image_file],
    "prompt": "...",
    "size": "1024x1024",
}
if model_key != "gpt-image-1-mini":
    params["input_fidelity"] = "high"

response = await openai_client.images.edit(**params)
```

### xAI Grok Imagine — Image Generation

Via OpenAI SDK with custom base_url:
```python
xai_client = AsyncOpenAI(
    base_url="https://api.x.ai/v1",
    api_key=settings.xai_api_key,
)
response = await xai_client.images.generate(
    model="grok-imagine-image",
    prompt="...",
    n=1,
    response_format="b64_json",
)
```

### xAI Grok Imagine — Image Editing (Reference Photos)

Via raw HTTP (OpenAI SDK doesn't work for xAI editing):
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.x.ai/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "grok-imagine-image",
            "prompt": "...",
            "image_url": f"data:image/jpeg;base64,{b64_data}",
        },
    )
```

### xAI Grok Imagine — Video Generation

**Submit**:
```
POST https://api.x.ai/v1/videos/generations
{
    "model": "grok-imagine-video",
    "prompt": "...",
    "image": {"url": "data:image/png;base64,..."},  // image-to-video
    "duration": 8,
    "aspect_ratio": "1:1",
    "resolution": "720p"
}
→ {"request_id": "uuid"}
```

**Poll**:
```
GET https://api.x.ai/v1/videos/{request_id}
→ {"url": "https://temp-url/video.mp4", "duration": 8.0}
```
