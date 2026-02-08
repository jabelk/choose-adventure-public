# Research: Multi-Model Image & Video Generation

**Feature Branch**: `013-image-video-gen`
**Date**: 2026-02-07

## Decision 1: OpenAI Image Model Variants

**Decision**: Use the same OpenAI Python SDK with `model=` parameter to switch between `gpt-image-1`, `gpt-image-1-mini`, and `gpt-image-1.5`.

**Rationale**: All three models share identical API surface (`images.generate` and `images.edit` endpoints). The only difference is that `gpt-image-1-mini` does not support the `input_fidelity` parameter in `images.edit`. The existing `_generate_dalle` method just needs the model name parameterized instead of hardcoded.

**Alternatives Considered**:
- Separate methods per model: Rejected — unnecessary since the API is identical
- Only supporting gpt-image-1: Rejected — user wants quality/cost choice

**Key Details**:
| Model | images.edit | input_fidelity | Quality options | Cost |
|-------|-----------|---------------|----------------|------|
| gpt-image-1 | Yes | Yes (first 1 image) | low/medium/high | Standard |
| gpt-image-1-mini | Yes | No | low/medium/high | ~55-78% cheaper |
| gpt-image-1.5 | Yes | Yes (first 5 images) | low/medium/high | Premium, 4x faster |

## Decision 2: xAI Grok Imagine Integration Approach

**Decision**: Use the OpenAI Python SDK pointed at `https://api.x.ai/v1` for basic image generation, and raw HTTP requests for image editing (reference photos) and video generation.

**Rationale**: The xAI SDK (`xai-sdk`) is gRPC-based and adds significant dependency weight. The OpenAI SDK can be used for basic `images.generate` by setting `base_url="https://api.x.ai/v1"`, which keeps our dependency footprint minimal. However, `images.edit()` does NOT work via the OpenAI SDK with xAI (multipart/form-data vs JSON mismatch), so we need raw HTTP for editing and video. Using `httpx` (already available via OpenAI SDK dependency) for these calls keeps things simple.

**Alternatives Considered**:
- Native xAI SDK (`pip install xai-sdk`): Rejected — gRPC-based, heavy dependency for what we need
- OpenAI SDK for everything: Rejected — images.edit and video don't work via OpenAI SDK
- Raw HTTP for everything: Considered viable, but OpenAI SDK handles image generation well

**Image Generation via OpenAI SDK**:
```python
from openai import AsyncOpenAI

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

**Image Editing via raw HTTP** (for reference photos):
```python
import httpx

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

## Decision 3: Video Generation Architecture

**Decision**: Use async background tasks with polling for video generation. Video generation is kicked off after image generation completes (image-to-video preferred). Use raw HTTP calls to xAI's video API endpoints.

**Rationale**: Video generation is asynchronous by nature — xAI returns a `request_id` and requires polling. Our existing background task pattern (asyncio.create_task) fits perfectly. Image-to-video is preferred for visual continuity (using the scene's generated image as the starting frame).

**API Endpoints**:
- `POST https://api.x.ai/v1/videos/generations` — submit generation, returns `{request_id}`
- `GET https://api.x.ai/v1/videos/{request_id}` — poll for result, returns `{url, duration}`

**Flow**:
1. Scene text + image generated (existing flow)
2. Once image is complete → kick off video generation task
3. Video task: POST to videos/generations with image URL or base64
4. Poll GET /videos/{request_id} every 5s until url returned (max 5 min)
5. Download video from temporary URL, save as MP4 locally
6. Update scene's video status

**Parameters**:
- Model: `grok-imagine-video`
- Duration: 5-10 seconds (default 8)
- Resolution: 720p
- Aspect ratio: 1:1 (matching image)

## Decision 4: Video Storage Pattern

**Decision**: Store video files in `static/videos/{scene_id}.mp4` alongside existing `static/images/{scene_id}.png`.

**Rationale**: Follows the exact same pattern as image storage. Videos are served as static files. Tier isolation is enforced at the route level (same as images — the scene_id is tied to a story session which is tier-scoped).

**Alternatives Considered**:
- Separate video directory per tier: Rejected — images already use flat scene_id-based storage
- Streaming from temporary URLs: Rejected — URLs expire, local-first principle

## Decision 5: Video Model Data Extensions

**Decision**: Add `video_mode: bool = False` to Story model, add `video_url: Optional[str] = None` and `video_status: str = "pending"` to Scene/Image model, add corresponding fields to SavedScene/SavedStory.

**Rationale**: Minimal model changes. Video status tracking reuses the same pattern as image status. The video_url field on Scene mirrors the image.url pattern.

## Decision 6: Image Model Registry Refactor

**Decision**: Expand IMAGE_PROVIDERS list with individual model entries instead of provider-level entries. Add a `provider_group` field and `supports_input_fidelity` flag to distinguish models.

**Rationale**: The current registry has `dalle` and `gemini` as flat entries. We need to expand to 5 entries with grouping info for the UI. Adding metadata about reference photo support (input_fidelity) allows the routes to pass the right parameters per model.

**New Registry**:
```python
IMAGE_PROVIDERS = [
    ImageModel(key="gpt-image-1", display_name="GPT Image 1", provider="OpenAI", api_key_env="OPENAI_API_KEY", supports_input_fidelity=True),
    ImageModel(key="gpt-image-1-mini", display_name="GPT Image 1 Mini", provider="OpenAI", api_key_env="OPENAI_API_KEY", supports_input_fidelity=False),
    ImageModel(key="gpt-image-1.5", display_name="GPT Image 1.5", provider="OpenAI", api_key_env="OPENAI_API_KEY", supports_input_fidelity=True),
    ImageModel(key="grok-imagine", display_name="Grok Imagine", provider="xAI", api_key_env="XAI_API_KEY", supports_input_fidelity=False),
    ImageModel(key="gemini", display_name="Gemini", provider="Google", api_key_env="GEMINI_API_KEY", supports_input_fidelity=False),
]
```
