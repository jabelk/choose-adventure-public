# Tasks: Multi-Model AI

**Input**: Design documents from `/specs/006-multi-model/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested — manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Dependencies & Configuration)

**Purpose**: Install new dependency and configure API keys for all providers.

- [x] T001 Install `google-genai` package into the virtual environment via `venv/bin/pip install google-genai` and verify import works
- [x] T002 [P] Add `GEMINI_API_KEY` and `XAI_API_KEY` fields to the Settings class in `app/config.py`, loaded from environment variables with empty string defaults
- [x] T003 [P] Update `.env.example` (if it exists) or document new env vars — add `GEMINI_API_KEY` and `XAI_API_KEY` placeholders

**Checkpoint**: New dependency installed, all 4 API key settings available.

---

## Phase 2: Foundational (Model Registry & Data Model)

**Purpose**: Create the model provider registry and add model field to Story models. These are blocking prerequisites for all user stories.

- [x] T004 Add `model` field (str, default `"claude"`) to `Story` model in `app/models.py`
- [x] T005 [P] Add `model` field (str, default `"claude"`) to `SavedStory` model in `app/models.py`
- [x] T006 Create `app/models_registry.py` — define `ModelProvider` dataclass (key, display_name, api_key_env), create `PROVIDERS` list with all 4 providers (claude, gpt, gemini, grok), add `get_available_models()` function that returns providers with configured API keys, add `get_provider(key)` to look up a provider by key
- [x] T007 Add `default_model` field (str, default `"claude"`) to `TierConfig` dataclass in `app/tiers.py` and set it on both kids and nsfw tier configs
- [x] T008 Refactor `StoryService.generate_scene()` in `app/services/story.py` to accept a `model` parameter (str) and dispatch to the correct provider — extract Claude call into `_call_claude()`, add `_call_gpt()`, `_call_gemini()`, `_call_grok()` methods, add `_call_provider(model, system, messages)` dispatcher

**Checkpoint**: Model registry exists, Story models have model field, StoryService can generate with any provider. Foundation ready for user stories.

---

## Phase 3: User Story 1 — Choose a Story Model (Priority: P1) 🎯 MVP

**Goal**: Users can select a model on the start form, story generates with that model, model name shows on scene pages.

**Independent Test**: Start a story with Claude, then with GPT. Verify each generates and shows the correct model name on scene pages.

### Implementation for User Story 1

- [x] T009 [US1] Update `POST /{tier}/story/start` in `app/routes.py` — accept `model` form parameter, validate against available models, fall back to tier default, store on Story object, pass to `generate_scene()`
- [x] T010 [US1] Update `POST /{tier}/story/choose/{scene_id}/{choice_id}` in `app/routes.py` — read model from `story_session.story.model` and pass to `generate_scene()`
- [x] T011 [US1] Update `GET /{tier}/` (tier_home) in `app/routes.py` — pass `available_models` list and `default_model` key to the template context
- [x] T012 [US1] Add model selector radio card section to `templates/home.html` — between length selector and submit button, styled like length options, pre-select default model, show error if no models available
- [x] T013 [US1] Add `.model-selector` and `.model-option` CSS styles in `static/css/style.css` — reuse the length selector card pattern (`.length-option` / `.option-card`)
- [x] T014 [US1] Display model name in scene header in `templates/scene.html` — add model display name next to the chapter info (e.g., "Chapter 2 of ~5 · Claude")
- [x] T015 [US1] Add `get_model_display_name(key)` helper to `app/models_registry.py` — returns display name for a provider key, defaults to key.title() if not found

**Checkpoint**: Model selector on start form, stories generate with selected model, model name visible on scene pages.

---

## Phase 4: User Story 2 — Tier Default Models (Priority: P2)

**Goal**: Each tier pre-selects its configured default model. Fallback to first available if default is unavailable.

**Independent Test**: Visit /kids/ and verify Claude is pre-selected. Remove ANTHROPIC_API_KEY, restart, verify fallback to first available model.

### Implementation for User Story 2

- [x] T016 [US2] Update tier_home route in `app/routes.py` — compute effective default model (tier's default_model if available, else first available model's key), pass as `default_model` to template
- [x] T017 [US2] Update model selector in `templates/home.html` — mark the radio button matching `default_model` as checked, handle case where no models available (disable submit, show message)

**Checkpoint**: Tier defaults pre-selected, fallback works when default model unavailable, error state when no models exist.

---

## Phase 5: User Story 3 — Model Attribution in Gallery (Priority: P2)

**Goal**: Gallery story cards and reader show which model generated each story. Pre-existing stories show "Claude".

**Independent Test**: Complete a story with GPT. View gallery — verify "GPT" appears on the story card. Open in reader — verify model name in header.

### Implementation for User Story 3

- [x] T018 [US3] Display model name on gallery story cards in `templates/gallery.html` — add model display name to the story card info section (e.g., below the date)
- [x] T019 [US3] Display model name in gallery reader header in `templates/reader.html` — add model name next to chapter info, similar to scene.html
- [x] T020 [US3] Ensure `GalleryService.save_story()` in `app/services/gallery.py` includes the model field when saving — verify the existing SavedStory serialization picks up the new field automatically via Pydantic

**Checkpoint**: Gallery cards show model name, reader shows model name, pre-existing stories show "Claude".

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, backward compatibility verification, edge cases.

- [x] T021 Verify backward compatibility — load a pre-existing saved story JSON (without model field) and confirm it deserializes with `model="claude"` without errors
- [x] T022 Verify story resume preserves model — start a story with GPT, navigate away, resume from progress banner, verify story continues with GPT via `app/routes.py` resume flow
- [x] T023 Update Settings.validate() in `app/config.py` — adjust warning to be informational about optional keys (Gemini, Grok) vs required keys (Anthropic, OpenAI)
- [x] T024 Run quickstart.md full validation — test all 13 scenarios manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (needs google-genai installed, API key settings)
- **Phase 3 (US1 - Choose Model)**: Depends on Phase 2 (needs registry, model field, provider dispatch)
- **Phase 4 (US2 - Tier Defaults)**: Depends on Phase 3 (extends model selector behavior)
- **Phase 5 (US3 - Gallery Attribution)**: Depends on Phase 2 (needs model field on SavedStory). Can run parallel with Phase 3/4.
- **Phase 6 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Choose Model)**: Depends on Phase 2. Core feature — must be first.
- **US2 (Tier Defaults)**: Depends on US1 (extends the model selector created in US1).
- **US3 (Gallery Attribution)**: Depends on Phase 2 only. Can proceed in parallel with US1/US2 since it touches different files (gallery.html, reader.html, gallery.py).

### Within Each User Story

- Route changes before template changes (context must be available for templates)
- CSS before template changes (styles must exist for classes)
- Registry helpers before routes (helpers must exist for routes to call)

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T004 and T005 can run in parallel (different model classes in same file, but sequential is safer)
- US3 (Phase 5) can run in parallel with US1/US2 after Phase 2 completes:
  - US3 touches: gallery.html, reader.html, gallery.py
  - US1 touches: routes.py, home.html, scene.html, style.css
  - No file overlap

---

## Parallel Example: Phase 3 + Phase 5

```bash
# After Phase 2 completes, US1 and US3 can start in parallel:

# US1 thread:
Task: "Update POST start route in app/routes.py"
Task: "Add model selector to templates/home.html"
Task: "Display model name in templates/scene.html"

# US3 thread (parallel):
Task: "Display model name in templates/gallery.html"
Task: "Display model name in templates/reader.html"
Task: "Verify gallery save includes model field"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install dependency, add API key settings)
2. Complete Phase 2: Foundational (registry, model fields, provider dispatch)
3. Complete Phase 3: Choose a Story Model
4. **STOP and VALIDATE**: Start stories with Claude and GPT, verify model name on scenes
5. Users can now compare stories from different AI models — core value delivered

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (registry, model fields, 4 providers)
2. Phase 3 (US1) → Model selector works → Test independently (MVP!)
3. Phase 4 (US2) → Tier defaults → Test independently
4. Phase 5 (US3) → Gallery attribution → Test independently
5. Phase 6 → Polish, backward compat verification, full validation

---

## Notes

- One new file: `app/models_registry.py` — flat module, no classes needed beyond dataclass
- One new dependency: `google-genai` — for Gemini API
- Grok uses existing `openai` package with custom base_url — no new dependency
- GPT text generation uses existing `openai` package chat completions — no new dependency
- All providers receive the same system prompt and content guidelines
- `_parse_response()` in story.py works for all models (they all return JSON when prompted)
- Default `model="claude"` on Story/SavedStory handles backward compatibility with zero migration
