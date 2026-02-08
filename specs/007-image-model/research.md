# Research: Image Model Selection

## Decision 1: Image Provider Architecture Pattern

**Decision**: Extend the existing `models_registry.py` module with an `IMAGE_PROVIDERS` list and corresponding `get_available_image_models()`, `get_image_provider()`, `get_image_model_display_name()` functions. Reuses the same `ModelProvider` dataclass since image providers have the same shape (key, display_name, api_key_env).

**Rationale**: The text model registry already exists and works well. Adding image providers to the same module avoids creating a separate file for an identical pattern. The functions are prefixed with `image_` to differentiate.

**Alternatives considered**:
- Separate `image_registry.py` module: Unnecessary duplication of the same dataclass and helper pattern.
- Combined registry with a `type` field: Over-engineered — text and image providers have different keys and the lists don't overlap.

## Decision 2: Gemini Image Generation Approach

**Decision**: Use Gemini's native image generation via `client.aio.models.generate_content()` with `response_modalities=["IMAGE"]` and model `gemini-2.0-flash-preview-image-generation`. This uses the same `google-genai` SDK and same API key as text generation.

**Rationale**: Gemini 2.0 Flash supports image generation natively via the same `generate_content` API used for text. The response contains `inline_data` with raw image bytes. No additional SDK or dependency needed — the `google-genai` package from 006-multi-model handles both.

**Alternatives considered**:
- Imagen 3 standalone API: Uses a different endpoint (`generate_images`) and different model IDs. More moving parts for the same result.
- Vertex AI Imagen: Requires GCP project setup, overkill for a personal project.

## Decision 3: Image Response Handling for Gemini

**Decision**: Extract image bytes from `response.candidates[0].content.parts[0].inline_data.data`, write directly to disk as PNG. The response data is raw bytes (not base64-encoded through the SDK accessor), matching the existing pattern of saving `img_bytes` to `static/images/{scene_id}.png`.

**Rationale**: The existing OpenAI flow already handles base64→bytes→disk. The Gemini flow is similar — get bytes from response, write to file. Both paths converge on the same file save and Image model update.

**Alternatives considered**:
- Using PIL to process the image: Adds a dependency for no benefit — we just need to save bytes to disk.

## Decision 4: Image Model Field Storage

**Decision**: Add `image_model` field (str, default `"dalle"`) to `Story` and `SavedStory` models. The default ensures backward compatibility — pre-existing stories display "DALL-E" without migration.

**Rationale**: Mirrors the `model` field pattern from 006-multi-model. String field, provider key as value, Pydantic default handles backward compat.

**Alternatives considered**:
- Storing on the Image model itself: Would allow per-scene image model switching, but FR-005 says it's per-story. Simpler on Story.

## Decision 5: Conditional Image Model Selector Display

**Decision**: The image model selector radio cards only render when `len(available_image_models) > 1`. When only one provider is available, it's used automatically with no UI shown. The hidden input for the single provider ensures the form still submits a value.

**Rationale**: Unlike the text model selector (which always shows even with one model), the spec explicitly requires the image selector to be hidden when there's only one option (FR-003). This avoids cluttering the form for users who only have OpenAI configured.

**Alternatives considered**:
- Always show selector even with one option: Spec explicitly says not to (FR-003).
- No hidden input, default on server: Works but the hidden input is more explicit.

## Decision 6: Image Provider Keys

**Decision**: Use `"dalle"` for OpenAI gpt-image-1 and `"gemini"` for Gemini image generation. Display names: "DALL-E" and "Gemini".

**Rationale**: "dalle" is more descriptive than "openai" for images since OpenAI is already used for text (as "gpt"). "gemini" matches the text model key since it uses the same API key.

**Alternatives considered**:
- "openai" as the image key: Confusing since "gpt" is the text key and both use OPENAI_API_KEY/GEMINI_API_KEY respectively.
- "gpt-image" as key: Too verbose, not user-friendly.

## Decision 7: Tier Default Image Model

**Decision**: Add `default_image_model` field (str, default `"dalle"`) to `TierConfig`. Both tiers default to "dalle" (the existing behavior). The template pre-selects this default when the selector is shown.

**Rationale**: Mirrors `default_model` for text. DALL-E is the safe default since it's the existing provider and all users already have it configured.

**Alternatives considered**:
- No tier default, global default only: Less flexible but the tier config pattern is already established.
