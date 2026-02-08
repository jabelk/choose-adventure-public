# Implementation Plan: Image Model Selection

**Branch**: `007-image-model` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-image-model/spec.md`

## Summary

Add support for multiple AI image generation providers (DALL-E, Gemini).
Users choose an image model on the start form via radio button cards when
multiple providers are available. The selector is hidden when only one
provider is configured. The selected image model generates all scene
illustrations for that story. Image model name displays alongside text
model name on scene pages, gallery cards, and reader. An image provider
registry extends the existing models_registry module. One new Gemini
image generation method in ImageService. Backward compatibility via
default `"dalle"` on Story/SavedStory models.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai
**Storage**: JSON flat files (stories in `data/stories/`, progress in `data/progress/`)
**Testing**: Manual testing via quickstart guide
**Target Platform**: Linux (Intel NUC) + macOS (development), served via LAN
**Project Type**: Web application (server-rendered)
**Performance Goals**: Image generation latency dominated by AI API calls (~10-60s)
**Constraints**: Single-user, LAN-only, 2 AI image provider APIs
**Scale/Scope**: Personal app, 1 concurrent user, 2 image providers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Image model selector scoped to each tier. Same image_style guidelines applied regardless of provider. Tiers remain fully isolated. |
| II. Local-First | PASS | AI APIs are for generation only (already permitted). Gallery/reading works without any API keys. No new cloud serving dependencies. |
| III. Iterative Simplicity | PASS | Extends existing registry pattern, no new abstractions. One new provider method. Conditional UI avoids cluttering single-provider setups. |
| IV. Archival by Design | PASS | Image model name stored in Story and SavedStory JSON. Gallery shows image model attribution. |
| V. Fun Over Perfection | PASS | Comparing AI image styles is the fun part! Simple conditional radio card UI. |

## Project Structure

### Documentation (this feature)

```text
specs/007-image-model/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: 7 design decisions
├── data-model.md        # Model field additions
├── quickstart.md        # 11-step manual testing guide
├── contracts/
│   └── routes.md        # Modified routes + template changes
├── checklists/
│   └── requirements.md  # Spec quality checklist (all pass)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # Add image_model field to Story and SavedStory
├── models_registry.py   # Add IMAGE_PROVIDERS list + image helper functions
├── tiers.py             # Add default_image_model field to TierConfig
├── routes.py            # Accept image_model param, pass to ImageService, pass to templates
└── services/
    └── image.py         # Refactor to accept image_model param, add Gemini generation method

templates/
├── home.html            # Add conditional image model selector radio cards
├── scene.html           # Display image model name in header
├── gallery.html         # Display image model name on story cards
└── reader.html          # Display image model name in reader header

static/css/
└── style.css            # Image model selector styles (reuse model selector pattern)
```

**Structure Decision**: This feature modifies the existing web application structure.
No new files created. All changes are modifications to existing files following
established patterns from 006-multi-model.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
