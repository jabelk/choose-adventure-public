# Feature Specification: Multi-Model AI

**Feature Branch**: `006-multi-model`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Multi-Model AI - Add support for multiple AI providers for story generation. Currently only OpenAI is used for images and Claude for text. Allow users to choose which AI model generates their story text (Claude, OpenAI GPT, Google Gemini, Grok). Show the model name on each scene so users can see which AI wrote it. Add a model selector to the story start form. Each tier can have different default models. The model selection should be stored with the story so gallery stories show which model was used. Start with text generation models only - image model selection can come later."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose a Story Model (Priority: P1)

A user visits the story start page and sees a model selector alongside the existing prompt and length fields. They can pick which AI model will generate their story text — for example, Claude, GPT, Gemini, or Grok. After selecting a model and submitting their prompt, the story is generated using the chosen model. The model name is displayed on each scene so the user knows which AI is telling the story.

**Why this priority**: This is the core feature — without model selection, nothing else matters. It delivers the primary value of letting users compare how different AI models tell stories.

**Independent Test**: Start a story with each available model. Verify the story generates successfully and the model name appears on each scene page.

**Acceptance Scenarios**:

1. **Given** the user is on the story start page, **When** they view the form, **Then** they see a model selector with at least two available models.
2. **Given** the user has selected a model and entered a prompt, **When** they click "Start Adventure", **Then** the story is generated using the selected model.
3. **Given** a story is being viewed, **When** the user reads any scene, **Then** the model name is visible somewhere on the scene page.
4. **Given** a model's API key is not configured, **When** the user views the model selector, **Then** that model does not appear as an option.

---

### User Story 2 - Tier Default Models (Priority: P2)

Each audience tier has a sensible default model pre-selected in the model selector. For example, the kids tier might default to Claude (known for safety), while the adult tier might default to a different model. Users can always override the default.

**Why this priority**: Improves the out-of-the-box experience so users don't have to think about model choice unless they want to. Also allows the project owner to assign the most appropriate model per tier.

**Independent Test**: Visit the kids tier and verify Claude is pre-selected. Visit the adult tier and verify its default is pre-selected. Change the default in configuration and verify it updates.

**Acceptance Scenarios**:

1. **Given** a tier has a configured default model, **When** a user visits that tier's start page, **Then** the default model is pre-selected in the model selector.
2. **Given** a tier's default model, **When** the user wants a different model, **Then** they can override the default by selecting another option.
3. **Given** a tier's configured default model is unavailable (API key missing), **When** the user visits the start page, **Then** the first available model is selected instead.

---

### User Story 3 - Model Attribution in Gallery (Priority: P2)

When viewing completed stories in the gallery, users can see which AI model generated each story. The model name appears on gallery story cards and in the gallery reader. This lets users browse their archive and compare stories from different models.

**Why this priority**: Adds value to the existing gallery by making model comparison browsable after the fact. Without this, users lose track of which model wrote which story.

**Independent Test**: Complete a story with a specific model. View it in the gallery. Verify the model name appears on the story card and in the reader.

**Acceptance Scenarios**:

1. **Given** a completed story in the gallery, **When** the user views the gallery list, **Then** the model name is shown on the story card.
2. **Given** a gallery story being read in the reader, **When** the user views any scene, **Then** the model name is visible.
3. **Given** a story was saved before this feature existed (no model recorded), **When** it appears in the gallery, **Then** it gracefully shows "Claude" as the default (since all pre-existing stories used Claude).

---

### Edge Cases

- What happens if all API keys are missing? The start form should show an error message indicating no models are available, and the submit button should be disabled.
- What happens if a model's API fails mid-story? The error handling should be the same as current behavior (error page with retry link). The user stays on the same model for the entire story.
- Can the user switch models mid-story? No — the model is locked when the story starts and used for all subsequent scenes in that story.
- What happens to in-progress saves (story resume)? The model selection is stored in the session and persisted with progress saves, so resuming a story continues with the same model.
- What if a new model is added later? The model registry should make it easy to add new providers without changing the UI or story flow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The story start form MUST include a model selector that lists all available AI text generation models.
- **FR-002**: Only models with valid, configured API keys MUST appear in the model selector.
- **FR-003**: The selected model MUST be used for all scene generation within a single story (no mid-story switching).
- **FR-004**: Each scene page MUST display the name of the model that generated the story.
- **FR-005**: Each tier MUST have a configurable default model that is pre-selected in the model selector.
- **FR-006**: The model selection MUST be stored with the story data so it persists across sessions and in the gallery.
- **FR-007**: Gallery story cards MUST display which model generated the story.
- **FR-008**: The gallery reader MUST show the model name when reading a stored story.
- **FR-009**: Stories saved before this feature MUST display "Claude" as their model (backward compatibility).
- **FR-010**: The system MUST support at least four text generation providers: Claude (Anthropic), GPT (OpenAI), Gemini (Google), and Grok (xAI).
- **FR-011**: If no models are available (all API keys missing), the start form MUST show a clear error and prevent story submission.

### Key Entities

- **Model Provider**: Represents an AI text generation service — has a name, display name, and availability status based on API key configuration.
- **Story**: Extended with a model identifier that records which provider generated the text.
- **Tier Configuration**: Extended with a default model preference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select from at least 2 different AI models when starting a story.
- **SC-002**: Every scene in a story displays the model name that generated it.
- **SC-003**: Gallery stories show model attribution on both the card listing and the reader view.
- **SC-004**: Stories created before this feature display "Claude" as their model without errors.
- **SC-005**: Adding a new model provider requires only configuration changes, not UI changes.

## Assumptions

- Text generation models only — image model selection is explicitly out of scope for this feature.
- The model selector is a simple radio button group or dropdown, similar to the existing story length selector.
- All models receive the same system prompt and content guidelines — the only difference is which API processes the request.
- API keys are configured via environment variables or the existing settings mechanism.
- The user sees the model's friendly display name (e.g., "Claude", "GPT"), not the technical model ID.
- Grok requires an xAI API key; Gemini requires a Google AI API key. These follow similar patterns to the existing Anthropic and OpenAI keys.
