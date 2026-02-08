# Implementation Plan: Multi-Model AI

**Branch**: `006-multi-model` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-multi-model/spec.md`

## Summary

Add support for multiple AI text generation providers (Claude, GPT, Gemini, Grok).
Users choose a model on the start form via radio button cards. The selected model
generates all scenes for that story. Model name displays on scene pages, gallery
cards, and reader. A model registry module maps provider keys to their generation
functions. One new dependency (`google-genai` for Gemini). Grok uses the existing
OpenAI SDK with a custom base URL. Backward compatibility via default `"claude"`
on the Story model.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai (new)
**Storage**: JSON flat files (stories in `data/stories/`, progress in `data/progress/`)
**Testing**: Manual testing via quickstart guide
**Target Platform**: Linux (Intel NUC) + macOS (development), served via LAN
**Project Type**: Web application (server-rendered)
**Performance Goals**: Scene generation latency dominated by AI API calls (~5-30s)
**Constraints**: Single-user, LAN-only, 4 AI provider APIs
**Scale/Scope**: Personal app, 1 concurrent user, 4 model providers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Model selector scoped to each tier. Same content_guidelines applied regardless of model. Tiers remain fully isolated. |
| II. Local-First | PASS | AI APIs are for generation only (already permitted). Gallery/reading works without any API keys. No new cloud serving dependencies. |
| III. Iterative Simplicity | PASS | Flat registry pattern, no abstract classes. One new dependency (google-genai). Grok reuses existing openai package. |
| IV. Archival by Design | PASS | Model name stored in Story and SavedStory JSON. Gallery shows model attribution. |
| V. Fun Over Perfection | PASS | Comparing AI models is the fun part! Simple radio card UI, no over-engineering. |

## Project Structure

### Documentation (this feature)

```text
specs/006-multi-model/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: 9 design decisions
├── data-model.md        # Model field additions, ModelProvider entity
├── quickstart.md        # 13-step manual testing guide
├── contracts/
│   └── routes.md        # Modified routes + template changes
├── checklists/
│   └── requirements.md  # Spec quality checklist (all pass)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── config.py            # Add GEMINI_API_KEY, XAI_API_KEY settings
├── models.py            # Add model field to Story and SavedStory
├── models_registry.py   # NEW: Model provider registry (providers, availability)
├── tiers.py             # Add default_model field to TierConfig
├── routes.py            # Accept model param, pass to generate_scene, pass to templates
└── services/
    └── story.py         # Refactor to accept model param, dispatch to provider

templates/
├── home.html            # Add model selector radio cards
├── scene.html           # Display model name in header
├── gallery.html         # Display model name on story cards
└── reader.html          # Display model name in reader header

static/css/
└── style.css            # Model selector card styles (reuse length selector pattern)
```

**Structure Decision**: This feature modifies the existing web application structure.
One new file created (`app/models_registry.py`). All other changes are modifications
to existing files following established patterns.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
