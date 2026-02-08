# Data Model: Picture Book Mode

## Modified Entities

### Image (existing — no changes)

The existing `Image` model is reused as-is for extra images. Each extra image is its own `Image` instance with independent status tracking.

| Field | Type | Description |
|-------|------|-------------|
| prompt | str | Image generation prompt |
| status | ImageStatus | PENDING / GENERATING / COMPLETE / FAILED |
| url | Optional[str] | Path to generated image file |
| error | Optional[str] | Error message if generation failed |

### Scene (existing — extended)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| extra_images | list[Image] | [] | Additional images for picture book mode (0 for standard, 2 for picture book) |

### SavedScene (existing — extended)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| extra_image_urls | list[str] | [] | URLs of successfully generated extra images |
| extra_image_prompts | list[str] | [] | Prompts used for extra image generation |

### Story (existing — no changes)

The `protagonist_age` field already exists on Story. No model changes needed — the activation logic reads this field to decide whether to generate extra images.

## New Helpers

### is_picture_book_age(protagonist_age: str) -> bool

Returns `True` if `protagonist_age` is `"toddler"` or `"young-child"`. Used by routes to decide whether to kick off extra image generation.

### FAST_IMAGE_MODEL = "gpt-image-1-mini"

Constant for the fast model key used by extra images. Located in image service.

## Image File Naming

| Image Type | File Path |
|------------|-----------|
| Main image | `static/images/{scene_id}.png` |
| Extra image 0 (close-up) | `static/images/{scene_id}_extra_0.png` |
| Extra image 1 (wide shot) | `static/images/{scene_id}_extra_1.png` |

## State Transitions

Each image (main and extra) follows the same state machine independently:

```
PENDING → GENERATING → COMPLETE
                    → FAILED → (retry) → GENERATING → ...
```

No image's state depends on any other image's state.
