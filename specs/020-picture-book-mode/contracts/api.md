# API Contracts: Picture Book Mode

## Modified Endpoints

### GET /{tier}/story/image/{scene_id}

**Current behavior**: Returns status of a single main image.

**Extended response** (backward compatible — new fields added):

```json
{
    "status": "complete",
    "url": "/static/images/abc123.png",
    "extra_images": [
        {
            "index": 0,
            "status": "complete",
            "url": "/static/images/abc123_extra_0.png",
            "type": "close-up"
        },
        {
            "index": 1,
            "status": "generating",
            "url": null,
            "type": "wide-shot"
        }
    ]
}
```

- `extra_images` is an empty list `[]` for non-picture-book scenes (backward compatible).
- Each extra image has its own independent `status` field.
- `type` is informational ("close-up" or "wide-shot").

### POST /{tier}/story/image/{scene_id}/retry

**Current behavior**: Retries the main image.

**Extended behavior**: Unchanged for main image. New endpoint below for extra images.

## New Endpoints

### POST /{tier}/story/image/{scene_id}/retry-extra/{index}

Retries a single extra image by its index (0 or 1).

**Request**: No body required.

**Response**: Redirect to scene page.

**Behavior**:
1. Validates scene exists and has extra images.
2. Resets `extra_images[index]` status to PENDING.
3. Kicks off new async generation task for that extra image.
4. Redirects to scene page.

**Error cases**:
- Scene not found → 404
- Index out of range → 404
- No active session → redirect to home

## Internal Contracts

### ImageService.generate_extra_images()

```python
async def generate_extra_images(
    self,
    extra_images: list[Image],
    scene_id: str,
    main_prompt: str,
    fast_model: str,
    reference_images: list[str] | None = None,
) -> None
```

Generates extra images in parallel. Each image gets a varied prompt derived from `main_prompt`. Uses `fast_model` for generation. Updates each `Image` object's status independently.

### Extra Image Prompt Variations

| Index | Type | Prompt Suffix |
|-------|------|---------------|
| 0 | close-up | "Close-up portrait shot of the main character, showing facial expression and details." |
| 1 | wide-shot | "Wide establishing shot showing the full environment and setting." |
