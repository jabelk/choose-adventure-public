# Research: Multi-Model AI

## Decision 1: Provider Architecture Pattern

**Decision**: Create a model registry module (`app/models_registry.py`) that defines a list of model provider configs. Each provider has a name, display name, API key env var name, and a `generate_scene()` method. The `StoryService` is refactored to accept a provider name and delegate to the appropriate provider's generation method.

**Rationale**: A simple registry pattern keeps things flat and avoids over-engineering. Each provider is just a function that takes the same inputs (system prompt, messages, max_tokens) and returns text. No abstract base classes or plugin systems needed — just a dict mapping provider names to their generation functions.

**Alternatives considered**:
- Abstract base class with subclasses per provider: Too much ceremony for 4 providers in a personal project.
- Strategy pattern with dependency injection: Over-engineered for this use case.
- Single function with if/elif per provider: Works but gets messy. Registry is barely more complex and much cleaner.

## Decision 2: Gemini SDK Choice

**Decision**: Use the `google-genai` package (official Google Gen AI SDK). Async support via `client.aio.models.generate_content()`. Model ID: `gemini-2.0-flash`.

**Rationale**: This is the official Google SDK for Gemini, actively maintained, and has native async support. The API is different from OpenAI's chat completion pattern but straightforward — pass content and a config with system_instruction.

**Alternatives considered**:
- `google-generativeai` (older SDK): Being deprecated in favor of `google-genai`.
- Vertex AI SDK: Requires GCP project setup, overkill for a personal project with just an API key.

## Decision 3: Grok/xAI SDK Choice

**Decision**: Use the existing `openai` package with a custom `base_url="https://api.x.ai/v1"`. This is the xAI-recommended approach since their API is OpenAI-compatible. Model ID: `grok-beta`.

**Rationale**: Avoids adding a new dependency. The OpenAI SDK is already installed for image generation. Just create a second `AsyncOpenAI` client with the xAI base URL and API key. Same chat completion interface as GPT.

**Alternatives considered**:
- `xai-sdk` package: Less mature async support, adds a new dependency for no benefit since the OpenAI SDK works perfectly.

## Decision 4: OpenAI GPT for Text Generation

**Decision**: Use the existing `openai` package's chat completion API for text generation alongside its image generation usage. Model ID: `gpt-4o`. Separate client instance (or shared) since base_url is default OpenAI.

**Rationale**: The OpenAI SDK is already installed. GPT-4o is the current best general-purpose model. Chat completion API takes system + messages, returns text — same pattern as Claude.

**Alternatives considered**:
- GPT-4-turbo: Older, being superseded by 4o.
- GPT-3.5-turbo: Cheaper but noticeably lower quality for creative writing.

## Decision 5: Where to Store Model Selection

**Decision**: Add a `model` field (string) to the `Story` model and `SavedStory` model. Default value is `"claude"` for backward compatibility. The model name is passed through the form, stored on story creation, and persisted in gallery saves and progress saves.

**Rationale**: Simplest possible approach — one string field. The model name matches the registry key (e.g., "claude", "gpt", "gemini", "grok"). Defaulting to "claude" means all pre-existing stories display correctly without migration.

**Alternatives considered**:
- Per-scene model storage: Overkill since FR-003 says no mid-story switching.
- Separate model metadata file: Unnecessary indirection when the story JSON already exists.

## Decision 6: Model Selector UI Pattern

**Decision**: Add a model selector section to the start form, styled identically to the existing story length selector (radio button cards). Each card shows the model's display name. Only models with configured API keys are rendered.

**Rationale**: Consistent with existing UI patterns. The length selector already works well and users understand the card selection pattern. Radio buttons ensure single selection.

**Alternatives considered**:
- Dropdown: Functional but less visually engaging than cards.
- Toggle buttons: Non-standard, harder to scan.

## Decision 7: Tier Default Model Configuration

**Decision**: Add a `default_model` field to `TierConfig`. Kids defaults to `"claude"` (best safety), adult defaults to `"claude"` as well (can be changed). The home template pre-selects the tier's default model in the radio group.

**Rationale**: Simple field addition. Claude is the safest default for kids. The adult tier can default to whatever the owner prefers. If the default model isn't available (no API key), the template falls back to the first available model.

**Alternatives considered**:
- Per-tier model allow/deny lists: Too complex for a personal project. All models are available in all tiers.

## Decision 8: API Key Configuration

**Decision**: Add `GEMINI_API_KEY` and `XAI_API_KEY` environment variables to the Settings class. The model registry checks each key and only lists providers whose keys are configured. The existing `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are already present.

**Rationale**: Follows the existing pattern in `app/config.py`. Environment variables via dotenv. The validate() method warns about missing keys but doesn't crash — models are simply unavailable.

**Alternatives considered**:
- Config file for model settings: Unnecessary when env vars already work for API keys.
- Runtime API key validation (test call): Slow and wasteful. Presence check is sufficient.

## Decision 9: Response Parsing Across Models

**Decision**: All models receive the same system prompt (the SYSTEM_PROMPT from story.py) and must return JSON in the same format. The story service's `_parse_response()` method works unchanged. Each provider's generation function is responsible only for making the API call and returning the raw text.

**Rationale**: The system prompt already specifies strict JSON output format. All modern LLMs can follow JSON instructions. Keeping the parsing centralized means one place to fix if output format issues arise.

**Alternatives considered**:
- Per-model response parsers: Only needed if models return fundamentally different formats, which they don't with proper prompting.
