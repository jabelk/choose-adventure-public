# Research: Character Visual Consistency

## R1: Current Image Generation Pipeline

Images are generated via `ImageService.generate_image()` in `app/services/image.py`. The method accepts an optional `reference_images: list[str]` parameter containing absolute file paths. All three providers (OpenAI, Gemini, Grok) support reference images with different mechanisms:

- **OpenAI**: Uses `images.edit()` with file objects + `input_fidelity="high"` for gpt-image-1/1.5
- **Gemini**: Uses `generate_content()` with `inline_data` blobs
- **Grok**: Uses raw httpx POST with base64-encoded `image_url`

Each provider wraps the prompt with context like "Use the person from the reference photo as the main character in this scene."

## R2: Current Reference Image Flow

Reference photos are collected at story start and at each continuation scene:

1. **Story start** (`POST /{tier}/start`): Builds `photo_paths` list from roster character photos (up to 3), passes to first `generate_image()` call
2. **Continuation** (`POST /{tier}/story/continue`): Rebuilds `choice_photo_paths` from roster characters fresh each time — same photos, but never includes previously generated images
3. **Direct uploads**: Override profile photos via `story.reference_photo_paths`

**Gap identified**: Generated scene images are never fed back as references to subsequent scenes. Each scene's image is generated independently, causing visual inconsistency.

## R3: generate_image Call Sites in routes.py

There are approximately 8 `generate_image()` calls:

1. **Story start** (line ~640): First scene — uses `photo_paths`
2. **Continue story** (line ~1171): Choice continuation — uses `choice_photo_paths`
3. **Continue story (agent mode)** (line ~1364): Agent continuation — uses `choice_photo_paths`
4. **Sequel start** (line ~2806): Sequel first scene — uses `choice_photo_paths`
5. **Image status check** (line ~1524): Retry failed image — no references passed currently
6. **Regenerate image** (line ~1568): User-edited prompt — no references passed currently
7. **Regenerate extra image** (line ~1606): Picture book variation — no references

## R4: Story Model Session Lifecycle

`StorySession` lives in an in-memory dict (`sessions`) keyed by session cookie. It contains a `Story` object with `reference_photo_paths` (for direct uploads) and `roster_character_ids`. Adding a field to `Story` persists for the session duration. No disk persistence needed — the reference chain only matters during active story creation.

## R5: Image File Paths

Generated images are saved to `static/images/{scene_id}.png`. The `STATIC_IMAGES_DIR` constant provides the base path. After `generate_image()` completes with status COMPLETE, the file exists at this known path. This is the path to store as the rolling reference.

## R6: Background Task Pattern

`generate_image()` is launched via `asyncio.create_task()` — it runs in the background and modifies the `Image` object in-place. The routes don't await it. To update `story.generated_reference_path` after completion, we need a wrapper coroutine that:
1. Awaits `generate_image()`
2. Checks if `image.status == COMPLETE`
3. If so, sets `story.generated_reference_path`

## R7: Existing Retry/Fallback Behavior

When an image model refuses content, `ImageService` tries fallback models automatically. The retry/fallback is internal to `generate_image()`. The wrapper only needs to check the final status, not handle retries.
